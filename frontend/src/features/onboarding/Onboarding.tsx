import logoUrl from '../../../../media/brand/mission-el-gheet-logo.svg';
import { useApp } from '../../app/state';
import { useVoiceCtx } from '../../app/voiceContext';
import { Shell } from '../../components/Shell';
import { Icon, CropArt } from '../../components/Icon';
import { Hero } from '../../components/parts';
import { UI } from '../../i18n/strings';
import type { PlantArt } from '../../domain/catalogue';

export function Start() {
  const { state, dispatch, t } = useApp();
  const start = (locale: 'ar' | 'en') => dispatch({ type: 'set', patch: { locale, audioUnlocked: true, route: 'intent', history: ['start'] } });
  return (
    <Shell dock={false} back={false} quiet>
      <div className="start">
        <img className="logo" src={logoUrl} alt="MISSION EL GHEET" />
        <h2 className="question" style={{ maxWidth: 'none' }}>{state.locale === 'ar' ? 'سكة المواسم' : 'Season Path'}</h2>
        <p className="sub">{t({ ar: 'خطّط أرضك لـ ٤ مواسم', en: 'Plan your field for 4 seasons' })}</p>
        {/* Start is also the audio unlock: the first tap browsers need before playing sound. */}
        <div className="actions">
          {/* The current language's Start is the filled (primary) button */}
          <button className={state.locale === 'ar' ? 'primary' : 'secondary'} lang="ar" onClick={() => start('ar')}><Icon name="play" /><span>ابدأ</span></button>
          <button className={state.locale === 'en' ? 'primary' : 'secondary'} lang="en" onClick={() => start('en')}><Icon name="play" /><span>Start</span></button>
        </div>
        <span className="badge sim">{t(UI.practice)}</span>
      </div>
    </Shell>
  );
}

function IntentArt({ filled }: { filled: boolean }) {
  const plants: PlantArt[] = ['berseem', 'maize', 'wheat', 'sorghum'];
  return (
    <span className={`intent-art ${filled ? '' : 'empty'}`}>
      {plants.map((p) => <span key={p} className="mini">{filled && <CropArt plant={p} />}</span>)}
      <span className="badge-ic"><Icon name={filled ? 'search' : 'plus'} /></span>
    </span>
  );
}

export function Intent() {
  const { dispatch, t } = useApp();
  const voice = useVoiceCtx();
  const choose = (journey: 'check' | 'explore') => { dispatch({ type: 'set', patch: { journey } }); dispatch({ type: 'go', route: 'practice' }); };
  const opts = [
    { j: 'check' as const, label: t({ ar: 'شيّك على خطتي', en: 'Check my plan' }), filled: true },
    { j: 'explore' as const, label: t({ ar: 'دوّر معايا على بدايل', en: 'Look for options with me' }), filled: false },
  ];
  return (
    <Shell back={false} prompt={{ ar: 'أهلاً بيك. عندك خطة نشيّك عليها، ولا ندوّر سوا على بدايل؟', en: 'Welcome. Do you have a plan to check, or shall we look for options together?' }}>
      <h2 className="question">{t({ ar: 'عايز تعمل إيه؟', en: 'What would you like to do?' })}</h2>
      <div className="tiles two">
        {opts.map((o) => (
          <div className="tile-wrap" key={o.j}>
            <button className="tile" onClick={() => choose(o.j)}><span className="art" style={{ width: 'auto', background: 'none' }}><IntentArt filled={o.filled} /></span>{o.label}</button>
            <button className="hear" aria-label={`${t(UI.listen)}: ${o.label}`} onClick={() => voice.speak({ ar: o.label, en: o.label })}><Icon name="speaker" /></button>
          </div>
        ))}
      </div>
    </Shell>
  );
}

/** Practice turn: the big mic picture IS the button. Uses the real browser recogniser. */
export function Practice() {
  const { state, dispatch, t } = useApp();
  const voice = useVoiceCtx();
  const v = voice.state;
  const heard = state.practiced;
  const onTranscript = (text: string) => { dispatch({ type: 'set', patch: { practiced: true, heard: { chips: [{ ar: text, en: text }], undo: state.seasons } } }); voice.settle(); voice.speak({ ar: 'برافو، سمعتك. اللي سمعته مكتوب فوق.', en: 'Good, I heard you. What I heard is written above.' }); };
  const cls = heard ? 'ok' : v === 'listening' || v === 'asking' ? 'listening' : v === 'processing' ? 'processing' : '';
  const hint = heard ? t({ ar: 'سمعتك', en: 'I heard you' })
    : v === 'listening' ? t({ ar: 'سامعك… دوس لما تخلّص', en: 'Listening… tap when done' })
    : v === 'asking' ? t({ ar: 'اسمح بالميكروفون', en: 'Allow the microphone' })
    : v === 'denied' || v === 'unsupported' ? t({ ar: 'الميكروفون مش متاح · تقدر تكمّل بالصور', en: 'Mic not available · you can use the pictures' })
    : t({ ar: 'دوس على الميكروفون واتكلّم', en: 'Tap the mic and talk' });
  return (
    <Shell prompt={{ ar: 'جرّب: دوس الميكروفون وقول اسم محصول.', en: 'Try it: tap the mic and say a crop.' }} onTranscript={onTranscript}>
      <Hero icon="mic" title={t({ ar: 'جرّب الميكروفون', en: 'Try the mic' })}>
        <button type="button" data-mic className={`mic-big ${cls}`} aria-label={hint} onClick={() => voice.micTap(onTranscript)}><Icon name={heard ? 'check' : 'mic'} /><span className="ring" /></button>
      </Hero>
      <p className="mic-hint" role="status" style={{ textAlign: 'center' }}>{hint}</p>
      {heard
        ? <button className="primary wide-btn push-end" onClick={() => dispatch({ type: 'go', route: 'intake' })}><Icon name="check" />{t({ ar: 'يلا نبدأ', en: "Let's start" })}</button>
        : <button className="secondary wide-btn push-end" onClick={() => dispatch({ type: 'go', route: 'intake' })}>{t({ ar: 'اتخطّى', en: 'Skip' })}</button>}
    </Shell>
  );
}
