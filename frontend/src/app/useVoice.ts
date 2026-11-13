import { useCallback, useEffect, useRef, useState } from 'react';
import { createRecognizer } from '../services/speech/recognizer';
import { createSpeaker } from '../services/speech/speaker';
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
  const denied = useRef(false);
  const asked = useRef(false);
  const rest = useCallback((): VoiceState => (denied.current ? 'denied' : rec.current.supported ? 'idle' : 'unsupported'), []);

  const stop = useCallback(() => { spk.current.stop(); setState((v) => (v === 'speaking' ? rest() : v)); }, [rest]);

  const speak = useCallback((b: Bi | null) => {
    if (!b) return;
    rec.current.abort();
    if (!spk.current.available) { setState('audiooff'); return; }
    setState('speaking');
    spk.current.speak(b[locale], locale === 'ar' ? 'ar-EG' : 'en-GB', () => setState((v) => (v === 'speaking' ? rest() : v)), () => setState('audiooff'));
  }, [locale, rest]);

  const miss = useCallback((kind: 'nospeech' | 'notunderstood') => {
    setMisses((m) => { const n = m + 1; setState(n >= 2 ? 'fallback' : kind); return n; });
  }, []);

  const micTap = useCallback((onTranscript: (t: string) => void) => {
    if (denied.current) { setState('denied'); return; }
    if (!rec.current.supported) { setState('unsupported'); return; }
    if (state === 'listening' || state === 'asking') { rec.current.stop(); setState('processing'); return; }
    spk.current.stop();
    const begin = () => {
      setState('listening');
      rec.current.start(locale === 'ar' ? 'ar-EG' : 'en-US', {
        result: (t) => { setState('processing'); setMisses(0); onTranscript(t); },
        error: (e) => { if (e === 'denied') { denied.current = true; setState('denied'); } else if (e === 'nospeech') miss('nospeech'); else setState(rest()); },
        end: () => miss('nospeech'),
      });
    };
    if (!asked.current) { asked.current = true; setState('asking'); setTimeout(begin, 1400); return; }
    begin();
  }, [state, locale, miss, rest]);

  useEffect(() => () => { rec.current.abort(); spk.current.stop(); }, []);

  return { state, setState, misses, speak, stop, micTap, notUnderstood: () => miss('notunderstood'), settle: () => setState(rest()), deviceVoice: spk.current.available };
}
export type Voice = ReturnType<typeof useVoice>;
