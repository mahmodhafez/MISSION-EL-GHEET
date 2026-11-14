import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';
import { useVoice } from './useVoice';

/* Fake Web Speech recogniser: records instances so tests can fire events on them. */
type Fake = { started: boolean; aborted: boolean; onresult: ((e: unknown) => void) | null; onerror: ((e: unknown) => void) | null; onend: (() => void) | null };
let made: Fake[] = [];
class FakeSR {
  lang = ''; interimResults = false; maxAlternatives = 1; continuous = false;
  started = false; aborted = false;
  onresult: ((e: unknown) => void) | null = null; onerror: ((e: unknown) => void) | null = null; onend: (() => void) | null = null;
  constructor() { made.push(this as unknown as Fake); }
  start() { this.started = true; }
  stop() { this.onend?.(); }
  abort() { this.aborted = true; }
}

beforeEach(() => {
  made = [];
  vi.useFakeTimers();
  (window as unknown as { SpeechRecognition: unknown }).SpeechRecognition = FakeSR;
});
afterEach(() => { vi.useRealTimers(); delete (window as unknown as { SpeechRecognition?: unknown }).SpeechRecognition; });

const firstTap = (r: { current: ReturnType<typeof useVoice> }, fn = vi.fn()) => { act(() => r.current.micTap(fn)); return fn; };

describe('useVoice mic', () => {
  it('a pending first-tap start is cancelled by tapping elsewhere: the mic never opens', () => {
    const { result } = renderHook(() => useVoice('en'));
    firstTap(result);
    expect(result.current.state).toBe('asking');
    act(() => result.current.cancel());
    act(() => { vi.advanceTimersByTime(2000); });
    expect(made.length).toBe(0);
    expect(result.current.state).toBe('idle');
  });

  it('navigation (stop) closes an open mic and late events from it are ignored', () => {
    const { result } = renderHook(() => useVoice('en'));
    const onT = firstTap(result);
    act(() => { vi.advanceTimersByTime(1400); });
    expect(result.current.state).toBe('listening');
    const sr = made[0];
    act(() => result.current.stop());
    expect(sr.aborted).toBe(true);
    expect(result.current.state).toBe('idle');
    act(() => { sr.onresult?.({ results: [[{ transcript: 'rice' }]] }); sr.onend?.(); });
    expect(onT).not.toHaveBeenCalled();
    expect(result.current.misses).toBe(0);
  });

  it('a failed listen counts one miss, not two (error then end)', () => {
    const { result } = renderHook(() => useVoice('en'));
    firstTap(result);
    act(() => { vi.advanceTimersByTime(1400); });
    const sr = made[0];
    act(() => { sr.onerror?.({ error: 'no-speech' }); sr.onend?.(); });
    expect(result.current.misses).toBe(1);
    expect(result.current.state).toBe('nospeech');
  });

  it('speaking cancels a pending start', () => {
    const { result } = renderHook(() => useVoice('en'));
    firstTap(result);
    act(() => result.current.speak({ ar: 'x', en: 'x' }));
    act(() => { vi.advanceTimersByTime(2000); });
    expect(made.length).toBe(0);
  });
});
