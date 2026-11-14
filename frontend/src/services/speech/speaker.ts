/* Voice output. Real app audio is pre-generated with ElevenLabs and served by /speech/tts (D7, offline only).
 * Until those files exist, the device voice is used and the UI says so ("Device voice"). Some Android phones
 * silently fall back to English when the Arabic pack is missing; that is a known limitation. */

export interface Speaker {
  readonly available: boolean;
  speak(text: string, lang: 'ar-EG' | 'en-GB', done: () => void, failed: () => void): void;
  stop(): void;
}

export function createSpeaker(): Speaker {
  const synth = typeof window !== 'undefined' ? window.speechSynthesis : undefined;
  return {
    available: !!synth && typeof SpeechSynthesisUtterance !== 'undefined',
    speak(text, lang, done, failed) {
      if (!synth) return failed();
      synth.cancel();
      const u = new SpeechSynthesisUtterance(text);
      u.lang = lang; u.rate = lang === 'ar-EG' ? 0.92 : 0.95;
      u.onend = done; u.onerror = (e) => (e.error === 'interrupted' || e.error === 'canceled' ? done() : failed());
      synth.speak(u);
    },
    stop() { synth?.cancel(); },
  };
}
