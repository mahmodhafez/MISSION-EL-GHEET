import { useCallback, useEffect, useRef, useState } from 'react';
import { createRecognizer } from '../services/speech/recognizer';
import { createSpeaker, type VoiceSource } from '../services/speech/speaker';
import type { Bi, Locale } from '../i18n/format';

export type VoiceState = 'idle' | 'speaking' | 'listening' | 'processing' | 'nospeech' | 'notunderstood' | 'denied' | 'unsupported' | 'asking' | 'audiooff' | 'fallback';

/* Voice rules (docs/design/voice-first.md §2): push-to-talk; mic tap stops speech first (barge-in);
 * permission asked on first mic tap after one line of why; never re-asked after refusal;
 * two misses → pictures become the main route. */
export function useVoice(locale: Locale) {
  const rec = useRef(createRecognizer());
  const spk = useRef(createSpeaker());
  const [state, setState] = useState<VoiceState>(rec.current.supported ? 'idle' : 'unsupported');
  const [misses, setMisses] = useState(0);
  const [source, setSource] = useState<VoiceSource | null>(null);
  const denied = useRef(false);
  const asked = useRef(false);
  const rest = useCallback((): VoiceState => (denied.current ? 'denied' : rec.current.supported ? 'idle' : 'unsupported'), []);

  /* Every listen gets a session id; callbacks from an older (aborted) session are ignored, and the
   * delayed start after the permission notice is cancelled by anything else the farmer does. */
  const session = useRef(0);
  const pending = useRef<ReturnType<typeof setTimeout> | null>(null);
  const cancelListen = useCallback(() => {
    session.current += 1;
    if (pending.current) { clearTimeout(pending.current); pending.current = null; }
    rec.current.abort();
  }, []);

  /** Stop the mic (if open or about to open) without counting a miss. */
  const cancel = useCallback(() => {
    cancelListen();
    setState((v) => (v === 'listening' || v === 'asking' || v === 'processing' ? rest() : v));
  }, [cancelListen, rest]);

  /** Stop everything: speech and mic. Used on navigation, language switch and screen changes. */
  const stop = useCallback(() => {
    cancelListen();
    spk.current.stop();
    setState((v) => (v === 'speaking' || v === 'listening' || v === 'asking' || v === 'processing' ? rest() : v));
  }, [cancelListen, rest]);

  const speak = useCallback((b: Bi | null) => {
    if (!b) return;
    cancelListen();
    if (!spk.current.available) { setState('audiooff'); return; }
    setState('speaking');
    setSource(spk.current.speak(b[locale], locale === 'ar' ? 'ar-EG' : 'en-GB', () => setState((v) => (v === 'speaking' ? rest() : v)), () => setState('audiooff')));
  }, [locale, rest]);

  const miss = useCallback((kind: 'nospeech' | 'notunderstood') => {
    setMisses((m) => { const n = m + 1; setState(n >= 2 ? 'fallback' : kind); return n; });
  }, []);

  const micTap = useCallback((onTranscript: (t: string) => void) => {
    if (denied.current) { setState('denied'); return; }
    if (!rec.current.supported) { setState('unsupported'); return; }
    if (state === 'asking') { cancel(); return; }
    if (state === 'listening') { rec.current.stop(); setState('processing'); return; }
    cancelListen();
    spk.current.stop();
    const id = session.current;
    const live = () => id === session.current;
    const begin = () => {
      pending.current = null;
      if (!live()) return;
      setState('listening');
      let done = false; // one outcome per session: error and end both fire on failure
      const finish = (f: () => void) => { if (!live() || done) return; done = true; f(); };
      rec.current.start(locale === 'ar' ? 'ar-EG' : 'en-US', {
        result: (t) => finish(() => { setState('processing'); setMisses(0); onTranscript(t); }),
        error: (e) => finish(() => { if (e === 'denied') { denied.current = true; setState('denied'); } else if (e === 'nospeech') miss('nospeech'); else setState(rest()); }),
        end: () => finish(() => miss('nospeech')),
      });
    };
    if (!asked.current) { asked.current = true; setState('asking'); pending.current = setTimeout(begin, 1400); return; }
    begin();
  }, [state, locale, miss, rest, cancel, cancelListen]);

  useEffect(() => () => { cancelListen(); spk.current.stop(); }, [cancelListen]);

  return { state, setState, misses, speak, stop, cancel, micTap, notUnderstood: () => miss('notunderstood'), settle: () => setState(rest()), deviceVoice: source === 'device' };
}
export type Voice = ReturnType<typeof useVoice>;
