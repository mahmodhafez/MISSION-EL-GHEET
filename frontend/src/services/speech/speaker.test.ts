import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import INDEX from '../../voice/voice-index.json';
import MANIFEST from '../../../public/audio/manifest.json';

type Part = { t: string; key?: string } | { slot: string };
const lines = (INDEX as unknown as { lines: Record<'ar' | 'en', { id: string; parts: Part[] }[]> }).lines;
const shipped = new Set((MANIFEST as { keys: Record<string, string[]> }).keys.ar ?? []);
// A sentence with no changing words whose clips all ship: it must play recorded.
const line = lines.ar.find((l) => l.parts.every((p) => 'key' in p && p.key && shipped.has(p.key)))!;
const text = line.parts.map((p) => ('t' in p ? p.t : '')).join('');

class FakeAudio {
  static fail = false;
  static played: string[] = [];
  onended: (() => void) | null = null;
  onerror: (() => void) | null = null;
  preload = '';
  constructor(public src: string) {}
  play() {
    FakeAudio.played.push(this.src);
    if (FakeAudio.fail) return Promise.reject(new Error('404'));
    queueMicrotask(() => this.onended?.());
    return Promise.resolve();
  }
  pause() {}
}

const spoken: string[] = [];
beforeEach(() => {
  vi.resetModules();
  FakeAudio.fail = false; FakeAudio.played = []; spoken.length = 0;
  vi.stubGlobal('Audio', FakeAudio);
  vi.stubGlobal('fetch', () => Promise.resolve({ ok: true, json: () => Promise.resolve(MANIFEST) }));
  vi.stubGlobal('SpeechSynthesisUtterance', class { lang = ''; rate = 1; onend: (() => void) | null = null; onerror = null; constructor(public text: string) {} });
  Object.defineProperty(window, 'speechSynthesis', {
    configurable: true,
    value: { cancel() {}, speak(u: { text: string; onend: () => void }) { spoken.push(u.text); queueMicrotask(u.onend); } },
  });
});
afterEach(() => vi.unstubAllGlobals());

async function speaker() {
  const clips = await import('./clips');
  await clips.loadClips();
  return (await import('./speaker')).createSpeaker();
}

describe('speaker: recorded Arabic clips', () => {
  it('the shipped manifest has Arabic clips and at least one whole sentence', () => {
    expect(shipped.size).toBeGreaterThan(0);
    expect(line, 'a fully recorded sentence').toBeTruthy();
  });

  it('plays the clips of a fully recorded sentence', async () => {
    const s = await speaker();
    const done = vi.fn(); const failed = vi.fn(); const onSource = vi.fn();
    expect(s.speak(text, 'ar-EG', done, failed, onSource)).toBe('recorded');
    await vi.waitFor(() => expect(done).toHaveBeenCalledOnce());
    expect(FakeAudio.played[0]).toMatch(/\/audio\/ar\/[0-9a-f]{16}\.mp3$/);
    expect(spoken).toEqual([]); expect(failed).not.toHaveBeenCalled(); expect(onSource).not.toHaveBeenCalled();
  });

  it('a clip that fails to play falls back to the device voice and says so', async () => {
    FakeAudio.fail = true;
    const s = await speaker();
    const done = vi.fn(); const failed = vi.fn(); const onSource = vi.fn();
    expect(s.speak(text, 'ar-EG', done, failed, onSource)).toBe('recorded');
    await vi.waitFor(() => expect(done).toHaveBeenCalledOnce());
    expect(spoken).toEqual([text]); expect(onSource).toHaveBeenCalledWith('device'); expect(failed).not.toHaveBeenCalled();
  });

  it('English has no clips yet: device voice', async () => {
    const s = await speaker();
    const en = lines.en.find((l) => l.id === line.id)!.parts.map((p) => ('t' in p ? p.t : '')).join('');
    expect(s.speak(en, 'en-GB', vi.fn(), vi.fn())).toBe('device');
  });
});
