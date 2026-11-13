/* Push-to-talk speech recognition behind a small interface (backend design §8.2: SpeechRecognizer).
 * Uses the browser Web Speech API (ar-EG / en-US). Chrome sends audio to Google; the first mic tap
 * explains this before the permission prompt. A server-side recogniser can replace this later. */

export type RecognizerError = 'denied' | 'nospeech' | 'unsupported' | 'network' | 'aborted';
export interface Recognizer {
  readonly supported: boolean;
  start(lang: 'ar-EG' | 'en-US', on: { result: (t: string) => void; error: (e: RecognizerError) => void; end: () => void }): void;
  stop(): void;
  abort(): void;
}

type SR = { lang: string; interimResults: boolean; maxAlternatives: number; continuous: boolean; start(): void; stop(): void; abort(): void;
  onresult: ((e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void) | null; onerror: ((e: { error: string }) => void) | null; onend: (() => void) | null };

export function createRecognizer(): Recognizer {
  const w = window as unknown as { SpeechRecognition?: new () => SR; webkitSpeechRecognition?: new () => SR };
  const Ctor = w.SpeechRecognition ?? w.webkitSpeechRecognition;
  let current: SR | null = null;
  return {
    supported: !!Ctor,
    start(lang, on) {
      if (!Ctor) return on.error('unsupported');
      const r = new Ctor();
      r.lang = lang; r.interimResults = false; r.maxAlternatives = 1; r.continuous = false;
      let got = false;
      r.onresult = (e) => { const t = e.results[0]?.[0]?.transcript?.trim(); if (t) { got = true; on.result(t); } };
      r.onerror = (e) => on.error(e.error === 'not-allowed' || e.error === 'service-not-allowed' ? 'denied' : e.error === 'no-speech' ? 'nospeech' : e.error === 'network' ? 'network' : 'aborted');
      r.onend = () => { if (!got) on.end(); current = null; };
      current = r;
      r.start();
    },
    stop() { current?.stop(); },
    abort() { current?.abort(); current = null; },
  };
}
