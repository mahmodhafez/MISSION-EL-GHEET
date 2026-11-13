import { createContext, useContext } from 'react';
import type { Voice } from './useVoice';
export const VoiceContext = createContext<Voice | null>(null);
export function useVoiceCtx() {
  const v = useContext(VoiceContext);
  if (!v) throw new Error('VoiceContext missing');
  return v;
}
