import { useEffect } from 'react';
import { useApp, snapshotOf } from '../../app/state';
import { useVoiceCtx } from '../../app/voiceContext';
import { Shell } from '../../components/Shell';
import { Icon, CropArt } from '../../components/Icon';
import { Banner, DateText, Hero, SeasonStrip, plantOf } from '../../components/parts';
import { PLANT, UI } from '../../i18n/strings';
import { dateText, num, type Bi } from '../../i18n/format';
import { conflictPair, conflictSeasons, prepSteps, reviewReasons } from './explain';

export function Checking() {
  const { state, dispatch, client, t } = useApp();
  useEffect(() => {
    let live = true;
    client.promiseTest(snapshotOf(state)).then((plan) => {
      if (!live) return; // stale response guard: a newer request or navigation wins
      dispatch({ type: 'set', patch: { plan, pick: 0 } });
      dispatch({ type: 'go', route: plan.status === 'ok' ? 'result' : 'failed' });
    });
    return () => { live = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return (
    <Shell prompt={{ ar: 'بشيّك على المواسم الأربعة…', en: 'Checking your four seasons…' }}>
      <div style={{ display: 'grid', gap: 16, alignContent: 'center', justifyItems: 'center', textAlign: 'center', flex: 1 }}>
        <div className="seq" aria-hidden="true">{state.seasons.map((s, i) => <span key={i} className="portrait-sm"><CropArt plant={plantOf(s.crop_id)} /></span>)}</div>
        <h2 className="question" role="status" style={{ maxWidth: 'none' }}>{t({ ar: 'بشيّك على المواسم الأربعة…', en: 'Checking your four seasons…' })}</h2>
      </div>
    </Shell>
  );
}

export function Failed() {
  const { state, dispatch, t } = useApp();
  const reason = state.plan?.status === 'unavailable' ? state.plan.reason : 'unknown';
  const notConnected = reason === 'planner_not_connected';
  return (
    <Shell prompt={notConnected ? { ar: 'الفحص لسه مش متوصّل للخطة دي. إجاباتك محفوظة.', en: 'Checking is not connected for this plan yet. Your answers are kept.' } : { ar: 'الفحص ماكملش. إجاباتك محفوظة. جرّب تاني.', en: 'The check did not finish. Your answers are kept. Try again.' }}>
      <Hero icon="review" unknown title={notConnected ? t({ ar: 'الفحص مش متوصّل لسه', en: 'Checking not connected yet' }) : t({ ar: 'الفحص ماكملش', en: 'The check did not finish' })} text={t({ ar: 'إجاباتك محفوظة', en: 'Your answers are kept' })} />
      {notConnected && <div className="notice">{t({ ar: 'نسخة التطوير فيها نتيجة المخطِّط الحقيقية لمثال عم حسين (UH-001) بس. أي خطة تانية محتاجة السيرفر.', en: 'This development build only has the real planner result for the UH-001 example. Any other plan needs the server.' })}</div>}
      <div className="two-btns">
        <button className="primary" onClick={() => dispatch({ type: 'go', route: 'checking' })}><Icon name="repeat" />{t({ ar: 'جرّب تاني', en: 'Try again' })}</button>
        <button className="secondary" onClick={() => dispatch({ type: 'go', route: 'intake' })}><Icon name="edit" />{t({ ar: 'غيّر الخطة', en: 'Change the plan' })}</button>
      </div>
    </Shell>
  );
}

function DevBadge() {
  const { state, t } = useApp();
  return state.plan?.status === 'ok' && state.plan.source === 'dev-export' ? <span className="badge sim" style={{ justifySelf: 'start' }}>{t(UI.devData)}</span> : null;
}

export function Result() {
  const { state, dispatch, t } = useApp();
  const voice = useVoiceCtx();
  if (state.plan?.status !== 'ok') return null;
  const cur = state.plan.result.current;
  const pair = conflictPair(cur);
  const idx = (sid: string | null) => state.seasons.findIndex((s) => s.season_id === sid);
  const sow = pair ? state.seasons[idx(pair.sowSeason)] : null;
  const cut = pair ? state.seasons[idx(pair.cutSeason)] : null;
  let prompt: Bi; let body: React.ReactNode;
  if (cur.status === 'rejected' && pair && sow && cut) {
    const sp = PLANT[plantOf(sow.crop_id)], cp = PLANT[plantOf(cut.crop_id)];
    prompt = { ar: `زراعة ${sp.def} يوم ${dateText(pair.sowDate, 'ar', { noYear: true })} قبل حشة ${cp.def} اللي ثبّتها يوم ${dateText(pair.cutDate, 'ar', { noYear: true })}. الحشة هتفضل.`,
      en: `Sowing ${sp.en.toLowerCase()} on ${dateText(pair.sowDate, 'en', { noYear: true })} comes before the ${cp.en.toLowerCase()} cut you kept on ${dateText(pair.cutDate, 'en', { noYear: true })}. The cut stays.` };
    body = (
      <div className="clash" role="img" aria-label={t(prompt)}>
        <div className="c-card reject"><span className="s-art"><CropArt plant={plantOf(sow.crop_id)} /><span className="s-mark reject"><Icon name="reject" /></span></span><span className="c-name">{t(sp)}</span><span className="c-when"><Icon name="sow" /><DateText value={pair.sowDate} noYear /></span><span className="c-what">{t({ ar: 'زراعة', en: 'sowing' })}</span></div>
        <div className="vs"><Icon name="arrow" /><span>{t({ ar: 'قبل', en: 'before' })}</span></div>
        <div className="c-card lock"><span className="s-art"><CropArt plant={plantOf(cut.crop_id)} /><span className="s-mark lock"><Icon name="lock" /></span></span><span className="c-name">{t(cp)}</span><span className="c-when"><Icon name="cut" /><DateText value={pair.cutDate} noYear /></span><span className="c-what">{t({ ar: 'آخر حشة · ثابت', en: 'last cut · kept' })}</span></div>
      </div>);
  } else if (cur.status === 'rejected') {
    const bad = conflictSeasons(cur);
    prompt = { ar: 'الخطة فيها تعارض. شوف المواسم اللي عليها علامة حمرا.', en: 'The plan has a conflict. Look at the seasons marked red.' };
    body = <SeasonStrip inline items={state.seasons.map((s) => ({ cropId: s.crop_id, date: s.last_cut_date ?? (s.sowing_date !== 'unknown' ? s.sowing_date : null), mark: bad.has(s.season_id) ? 'reject' : undefined, cls: bad.has(s.season_id) ? 'reject' : '' }))} />;
  } else if (cur.status === 'needs_review') {
    const rs = reviewReasons(cur);
    prompt = { ar: 'مفيش تعارض واضح، بس الخطة محتاجة مراجعة زراعية.', en: 'No clear conflict, but the plan needs agricultural review.' };
    body = <div className="facts four">{rs.map((r, k) => <span key={k} className="fact unk"><Icon name={r.icon} />؟<small>{t(r.label)}</small></span>)}</div>;
  } else {
    prompt = { ar: 'الخطة ماشية بالشروط اللي اتقالت. ده مش وعد بمحصول.', en: 'The plan holds under the stated conditions. That is not a promise of a harvest.' };
    body = <Hero icon="feasible" title={t({ ar: 'الخطة ماشية بالشروط دي', en: 'The plan holds under these conditions' })} />;
  }
  const banner = cur.status === 'rejected' ? <Banner kind="rejected" icon="reject">{t({ ar: 'الخطة فيها تعارض', en: 'The plan has a conflict' })}</Banner>
    : cur.status === 'needs_review' ? <Banner kind="review" icon="review">{t({ ar: 'محتاج مراجعة زراعية', en: 'Needs agricultural review' })}</Banner>
    : <Banner kind="feasible" icon="feasible">{t({ ar: 'ماشية بالشروط الموضّحة', en: 'Feasible under stated conditions' })}</Banner>;
  const hasOptions = state.journey === 'explore';
  return (
    <Shell prompt={prompt} onTranscript={undefined}>
      <div className="calm">
        {banner}<DevBadge />{body}
        <div className="calm-end"><div className="three-btns">
          {prepSteps(cur) ? <button className="secondary" onClick={() => dispatch({ type: 'go', route: 'why' })}><Icon name="help" /><span>{t({ ar: 'ليه؟', en: 'Why?' })}</span></button> : <span />}
          {hasOptions ? <button className="primary" onClick={() => dispatch({ type: 'go', route: 'options' })}><Icon name="calendar" /><span>{t({ ar: 'مواعيد تانية', en: 'Other dates' })}</span></button> : <span />}
          <button className="secondary" onClick={() => { voice.stop(); dispatch({ type: 'go', route: 'summary' }); }}><Icon name="save" /><span>{t({ ar: 'احفظ', en: 'Save' })}</span></button>
        </div></div>
      </div>
    </Shell>
  );
}

export function Why() {
  const { state, dispatch, t } = useApp();
  if (state.plan?.status !== 'ok') return null;
  const st = prepSteps(state.plan.result.current);
  if (!st) return null;
  const L = state.locale;
  const prompt = { ar: `${st.cutDate ? `آخر حشة ${dateText(st.cutDate, 'ar', { noYear: true })}. ` : ''}الأرض تفضى ${dateText(st.releaseDate, 'ar', { noYear: true })}. بعد ${num(st.days, 'ar')} أيام تجهيز، أقرب ميعاد ${dateText(st.earliest, 'ar')}. ده عدّ أيام بس، ومحتاج مراجعة زراعية.`,
    en: `${st.cutDate ? `Last cut ${dateText(st.cutDate, 'en', { noYear: true })}. ` : ''}The field is free on ${dateText(st.releaseDate, 'en', { noYear: true })}. After ${st.days} preparation days, the earliest date is ${dateText(st.earliest, 'en')}. That is only day counting and needs agricultural review.` };
  return (
    <Shell prompt={prompt}>
      <Banner kind="rejected" icon="reject">{t({ ar: 'الخطة فيها تعارض', en: 'The plan has a conflict' })}</Banner>
      <h2 className="question" style={{ fontSize: 24 }}>{t({ ar: 'أقرب ميعاد للزراعة', en: 'Earliest sowing date' })}</h2>
      <ol className="steps">
        {st.cutDate && <li className="lock"><span className="ic"><Icon name="cut" /></span><b><DateText value={st.cutDate} noYear /></b><span>{t({ ar: 'آخر حشة', en: 'last cut' })}</span></li>}
        <li><span className="ic"><Icon name="field" /></span><b><DateText value={st.releaseDate} noYear /></b><span>{t({ ar: 'الأرض فاضية', en: 'field free' })}</span></li>
        <li><span className="ic"><Icon name="calendar" /></span><b>{num(st.days, L)} {t({ ar: 'أيام', en: 'days' })}</b><span>{t({ ar: 'تجهيز (افتراض)', en: 'prep (assumed)' })}</span></li>
        <li className="review"><span className="ic"><Icon name="sow" /></span><b><DateText value={st.earliest} noYear /></b><span>{t({ ar: 'محتاج مراجعة', en: 'needs review' })}</span></li>
      </ol>
      {state.journey === 'explore' && <button className="primary wide-btn" onClick={() => dispatch({ type: 'go', route: 'options' })}><Icon name="calendar" />{t({ ar: 'شوف المواعيد اللي ممكن نراجعها', en: 'See dates we could check' })}</button>}
    </Shell>
  );
}
