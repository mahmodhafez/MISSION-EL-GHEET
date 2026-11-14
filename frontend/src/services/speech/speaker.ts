import { createClipPlayer, hasClips, loadClips, planSpeech, recorded } from './clips';
/* Voice output. Recorded clips first (frontend/public/audio, built by backend/scripts/voice_build); any sentence
 * without clips uses the device voice and the UI says so ("Device voice"). Some Android phones
 * silently fall back to English when the Arabic pack is missing; that is a known limitation. */

export type VoiceSource = 'recorded' | 'device';
export interface Speaker {
  /** True if anything can speak: recorded clips or the device voice. */
  readonly available: boolean;
  /** Plays the recorded clips for this sentence if they all exist, else the device voice. Returns which, or null.
   * If a clip fails to load or play, the sentence is spoken again by the device voice and onSource('device') fires. */
  speak(text: string, lang: 'ar-EG' | 'en-GB', done: () => void, failed: () => void, onSource?: (s: VoiceSource) => void): VoiceSource | null;
  stop(): void;
}

export function createSpeaker(): Speaker {
  const synth = typeof window !== 'undefined' ? window.speechSynthesis : undefined;
  const device = !!synth && typeof SpeechSynthesisUtterance !== 'undefined';
  const clips = createClipPlayer();
  void loadClips();
  return {
    get available() { return device || hasClips(); },
    speak(text, lang, done, failed, onSource) {
      const locale = lang === 'ar-EG' ? 'ar' : 'en';
      synth?.cancel(); clips.stop();
      const viaDevice = (): VoiceSource | null => {
        if (!device || !synth) { failed(); return null; }
        const u = new SpeechSynthesisUtterance(text);
        u.lang = lang; u.rate = lang === 'ar-EG' ? 0.92 : 0.95;
        u.onend = done; u.onerror = (e) => (e.error === 'interrupted' || e.error === 'canceled' ? done() : failed());
        synth.speak(u);
        return 'device';
      };
      const keys = recorded(text, locale);
      if (keys) {
        // A missing or broken clip (404, decode error) shouldn't silence the app: say it with the device voice.
        clips.play(locale, keys, done, () => { if (viaDevice()) onSource?.('device'); });
        return 'recorded';
      }
      if (import.meta.env.DEV && !planSpeech(text, locale)) console.info('[voice] not in catalogue:', text);
      return viaDevice();
    },
    stop() { synth?.cancel(); clips.stop(); },
  };
}
