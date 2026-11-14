import { useEffect, type ReactNode } from 'react';
import { useApp } from '../app/state';
import { useVoiceCtx } from '../app/voiceContext';
import { Icon } from './Icon';
import { UI, VOICE_STATE } from '../i18n/strings';
import type { Bi } from '../i18n/format';

interface Props {
  prompt?: Bi | null;
  top?: ReactNode;
  children: ReactNode;
  back?: boolean;
  dock?: boolean;
  quiet?: boolean;
  onTranscript?: (t: string) => void;
}

/** One screen = header + (optional top strip) + main + voice dock. Speaks the prompt when it changes. */
export function Shell({ prompt = null, top, children, back = true, dock = true, quiet = false, onTranscript }: Props) {
  const { state, dispatch, t } = useApp();
  const voice = useVoiceCtx();
  const L = state.locale;
  const key = prompt ? prompt[L] : '';
  useEffect(() => {
    // New screen or language: old audio stops; the new prompt is spoken (design §2 rule 8).
    if (state.audioUnlocked && !quiet && prompt) voice.speak(prompt); else voice.stop();
    // speak only when the words change
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, state.audioUnlocked]);

  const v = voice.state;
  const [line1, line2] = VOICE_STATE[v] ?? VOICE_STATE.idle;
  const micCls = v === 'denied' || v === 'unsupported' ? 'off' : v === 'listening' || v === 'asking' ? 'listening' : v === 'processing' ? 'processing' : v === 'speaking' ? 'speaking' : '';
  const micLabel = v === 'listening' ? t(UI.doneTalking) : v === 'denied' || v === 'unsupported' ? t(line1) : t(UI.talk);

  return (
    <section className={`stage ${v === 'fallback' || v === 'denied' || v === 'unsupported' ? 'fallback' : ''}`} lang={L} dir={L === 'ar' ? 'rtl' : 'ltr'}
      // Tapping anything except a mic (a picture, a disabled date, empty space) closes an open or pending mic.
      onPointerDownCapture={(e) => { if ((v === 'listening' || v === 'asking') && !(e.target as Element).closest('[data-mic]')) voice.cancel(); }}>
      <div className="app-head">
        {back && state.history.length > 0 && (
          <button className="chip-btn" onClick={() => { voice.stop(); dispatch({ type: 'back' }); }}><Icon name="back" /><span>{t(UI.back)}</span></button>
        )}
        <span className="spacer" />
        <button className="chip-btn" lang={L === 'ar' ? 'en' : 'ar'} onClick={() => { voice.stop(); dispatch({ type: 'set', patch: { locale: L === 'ar' ? 'en' : 'ar' } }); }}>
          <Icon name="globe" /><span>{t(UI.langSwitch)}</span>
        </button>
        <button className="chip-btn" onClick={() => voice.speak({ ar: 'تقدر تتكلّم أو تختار صورة. دوس "تاني" علشان تسمع السؤال من الأول.', en: 'You can talk or tap a picture. Press Repeat to hear the question again.' })}>
          <Icon name="help" /><span>{t(UI.help)}</span>
        </button>
      </div>
      {top}
      <main className="app-main">
        {state.heard && (
          <div className="implicit" role="status">
            <Icon name="mic" />
            <span><span className="who">{t(UI.heard)}</span> {state.heard.chips.map((c, i) => <b key={i}>{i ? ' · ' : ''}{t(c)}</b>)}</span>
            <button className="chip-btn" onClick={() => dispatch({ type: 'set', patch: { seasons: state.heard!.undo, heard: null } })}><Icon name="edit" />{t(UI.change)}</button>
          </div>
        )}
        {children}
      </main>
      {dock && (
        <div className="dock" role="region" aria-label={L === 'ar' ? 'الصوت' : 'Voice'}>
          <div className="dock-state" role="status" aria-live="polite">
            {t(line1)}<small>{t(line2)}{voice.deviceVoice && v === 'speaking' ? ` · ${t(UI.deviceVoice)}` : ''}</small>
          </div>
          <div className="side">
            <div className="ctl">
              <button className="round" aria-label={t(v === 'speaking' ? UI.stop : UI.repeat)} onClick={() => (v === 'speaking' ? voice.stop() : voice.speak(prompt))}>
                <Icon name={v === 'speaking' ? 'stop' : 'repeat'} />
              </button>
              <span className="round-label">{t(v === 'speaking' ? UI.stop : UI.repeat)}</span>
            </div>
          </div>
          <div className="ctl">
            <button type="button" data-mic className={`mic ${micCls}`} aria-label={micLabel} aria-pressed={v === 'listening'} disabled={!onTranscript}
              onClick={() => onTranscript && voice.micTap(onTranscript)}>
              <Icon name={micCls === 'off' ? 'micoff' : 'mic'} /><span className="ring" />
            </button>
            <span className="round-label">{micLabel}</span>
          </div>
          <div className="side end" />
        </div>
      )}
    </section>
  );
}
