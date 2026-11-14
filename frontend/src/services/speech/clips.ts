/* Recorded voice: every sentence was recorded once with pauses where the changing words go, cut at the pauses,
 * and every changing word was recorded on its own (backend/scripts/voice_build). To speak a sentence we find
 * the catalogue line it comes from, then play its pieces and words in order. Anything that doesn't match, or
 * whose clips aren't recorded yet, returns null and the caller falls back to the device voice. */
import INDEX from '../../voice/voice-index.json';

type Part = { t: string; say?: string; key?: string } | { slot: string };
type Word = { show: string; say: string; key: string };
interface Index { lines: Record<string, { id: string; parts: Part[] }[]>; vocab: Record<string, Record<string, Word[]>> }
const idx = INDEX as unknown as Index;

const esc = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const norm = (s: string) => s.replace(/[\s ]+/g, ' ').trim();
const alt = (ws: Word[]) => ws.map((w) => esc(w.show)).join('|');

interface Compiled { id: string; re: RegExp; parts: Part[] }
const cache: Record<string, Compiled[]> = {};

function compile(loc: string): Compiled[] {
  if (cache[loc]) return cache[loc];
  const v = idx.vocab[loc];
  const day = alt(v.num), mon = alt(v.month), yr = alt(v.year);
  // Dates appear as "15 May", "١٥ مايو ٢٠٢٧", "خمستاشر مايو" or "May fifteen" (backend English speech).
  const date = `(?:(?:${day}) (?:${mon})|(?:${mon}) (?:${day}))(?: (?:${yr}))?`;
  const slotRe = (s: string) => (s === 'date' ? date : alt(v[s] ?? []));
  cache[loc] = idx.lines[loc].map((l) => ({
    id: l.id,
    parts: l.parts,
    re: new RegExp('^' + l.parts.map((p) => ('slot' in p ? `(${slotRe(p.slot)})` : esc(norm(p.t) === '' ? ' ' : p.t).replace(/ /g, ' ?'))).join('') + '$'),
  }));
  return cache[loc];
}

/** Longest-first tokens of a slot value (a date is day + month + year words). */
function tokens(loc: string, slot: string, value: string): Word[] | null {
  const v = idx.vocab[loc];
  const pool = slot === 'date' ? [...v.num, ...v.month, ...v.year].sort((a, b) => b.show.length - a.show.length) : v[slot] ?? [];
  const whole = pool.find((w) => w.show === value);
  if (whole) return [whole];
  if (slot !== 'date') return null;
  const out: Word[] = []; let rest = value;
  while (rest) {
    const w = pool.find((x) => rest.startsWith(x.show) && (rest.length === x.show.length || rest[x.show.length] === ' '));
    if (!w) return null;
    out.push(w); rest = rest.slice(w.show.length).trimStart();
  }
  return out;
}

/** Sentence → clip keys in play order, with the matching line id; null when it isn't in the catalogue. */
export function planSpeech(text: string, locale: 'ar' | 'en'): { id: string; keys: string[] } | null {
  const s = norm(text);
  for (const c of compile(locale)) {
    const m = c.re.exec(s);
    if (!m) continue;
    const keys: string[] = []; let g = 1; let ok = true;
    for (const p of c.parts) {
      if ('slot' in p) {
        const ws = tokens(locale, p.slot, norm(m[g++]));
        if (!ws) { ok = false; break; }
        keys.push(...ws.map((w) => w.key));
      } else if (p.key) keys.push(p.key);
    }
    if (ok) return { id: c.id, keys };
  }
  return null;
}

/* ---- playback ---- */
let available: Record<string, Set<string>> | null = null;
let loading: Promise<void> | null = null;
const base = `${import.meta.env.BASE_URL ?? '/'}audio`;

/** Load the list of recorded clips once. No manifest (nothing recorded yet) → every sentence uses the device voice. */
export function loadClips(fetcher: typeof fetch = fetch): Promise<void> {
  loading ??= fetcher(`${base}/manifest.json`).then((r) => (r.ok ? r.json() : null)).then((m) => {
    if (m?.keys) available = Object.fromEntries(Object.entries(m.keys as Record<string, string[]>).map(([l, ks]) => [l, new Set(ks)]));
  }).catch(() => undefined);
  return loading;
}

export const hasClips = () => !!available && Object.values(available).some((k) => k.size > 0);

/** Clip keys for this sentence if every piece and word is recorded, else null. */
export function recorded(text: string, locale: 'ar' | 'en'): string[] | null {
  const have = available?.[locale];
  if (!have) return null;
  const p = planSpeech(text, locale);
  return p && p.keys.length && p.keys.every((k) => have.has(k)) ? p.keys : null;
}

/** Plays clips back to back. stop() cancels; done() fires once at the end, failed() if a clip can't play. */
export function createClipPlayer() {
  let token = 0; let current: HTMLAudioElement | null = null;
  return {
    play(locale: string, keys: string[], done: () => void, failed: () => void) {
      const my = ++token;
      const els = keys.map((k) => { const a = new Audio(`${base}/${locale}/${k}.mp3`); a.preload = 'auto'; return a; });
      const next = (i: number) => {
        if (my !== token) return;
        if (i >= els.length) { current = null; done(); return; }
        current = els[i];
        current.onended = () => next(i + 1);
        current.onerror = () => { if (my === token) { current = null; failed(); } };
        current.play().catch(() => { if (my === token) { current = null; failed(); } });
      };
      next(0);
    },
    stop() { token++; if (current) { current.pause(); current = null; } },
  };
}
