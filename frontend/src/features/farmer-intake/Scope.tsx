import { useState } from 'react';
import { useApp } from '../../app/state';
import { useVoiceCtx } from '../../app/voiceContext';
import { Shell } from '../../components/Shell';
import { Icon, CropArt } from '../../components/Icon';
import { DatePicker, DateText, SeasonName, SeasonStrip, plantOf } from '../../components/parts';
import { asksLastCut, plantsFrom } from '../../domain/catalogue';
import { PLANT, PURPOSE } from '../../i18n/strings';
import { MONTHS, num } from '../../i18n/format';
import type { Permission } from '../../services/plannerClient';

const known = (c: string | null) => !!c && c !== 'unknown';

/** What must stay? On berseem the lock keeps the last cut; on other crops it keeps crop + purpose. */
export function Protect() {
  const { state, dispatch, t } = useApp();
  const voice = useVoiceCtx();
  const L = state.locale;
  const n = Object.values(state.locks).filter(Boolean).length;
  const toggle = (sid: string, name: string) => {
    const on = !state.locks[sid];
    dispatch({ type: 'set', patch: { locks: { ...state.locks, [sid]: on }, stale: state.confirmed || state.stale } });
    voice.speak(on ? { ar: `${name}: ثابت.`, en: `${name}: kept.` } : { ar: `${name}: ممكن يتغيّر.`, en: `${name}: can change.` });
  };
  const next = () => dispatch({ type: 'go', route: state.journey === 'explore' ? 'permit' : 'scope' });
  return (
    <Shell prompt={{ ar: 'إيه اللي لازم يفضل زي ما هو مهما حصل؟ دوس على القفل.', en: 'What must stay exactly as it is, whatever happens? Tap the lock.' }}>
      <h2 className="question">{t({ ar: 'إيه اللي لازم يفضل؟', en: 'What must stay?' })}</h2>
      <ol className="path wide short">
        {state.seasons.map((s, i) => {
          if (!known(s.crop_id)) return (
            <li key={s.season_id} className="empty"><span className="portrait"><CropArt plant="unknown" /></span><div className="txt"><h3>{t(PLANT.unknown)}</h3><div className="meta"><SeasonName slot={state.slots[i]} /></div></div><div className="end" /></li>);
          const p = PLANT[plantOf(s.crop_id)]; const on = !!state.locks[s.season_id];
          const date = s.last_cut_date ?? (s.sowing_date !== 'unknown' ? s.sowing_date : null);
          return (
            <li key={s.season_id} className={on ? 'locked' : ''}>
              <span className="portrait"><CropArt plant={plantOf(s.crop_id)} /></span>
              <div className="txt">
                <h3>{t(p)} {s.purpose && <span className="meta"><span className="sep">· </span>{t(PURPOSE[s.purpose as 'grain'])}</span>}</h3>
                {date && <div className="when"><Icon name={s.last_cut_date ? 'cut' : 'sow'} /><DateText value={date} /></div>}
                <div className="meta"><SeasonName slot={state.slots[i]} /></div>
              </div>
              <div className="end"><button className="lock-btn" aria-pressed={on} aria-label={`${t({ ar: 'لازم يفضل', en: 'Must stay' })}: ${t(p)}`} onClick={() => toggle(s.season_id, t(p))}><Icon name="lock" /><span>{t({ ar: 'ثابت', en: 'Keep' })}</span></button></div>
            </li>);
        })}
      </ol>
      <button className="primary wide-btn" onClick={next}>
        <Icon name="check" />{state.journey === 'explore' ? t({ ar: 'التالي: إيه اللي ممكن يتغيّر؟', en: 'Next: what may change?' }) : t({ ar: 'التالي', en: 'Next' })}
        {n > 0 && <span className="badge protected" style={{ background: '#fff' }}><Icon name="lock" />{num(n, L)}</span>}
      </button>
    </Shell>
  );
}

/** What may change? The planner only searches explicit permissions (dates, crops). Nothing pre-ticked. */
export function Permit() {
  const { state, dispatch, t } = useApp();
  const L = state.locale;
  const [adding, setAdding] = useState<{ season: number; ym?: { y: number; m: number } } | null>(null);
  const [cropFor, setCropFor] = useState<number | null>(null);
  const [page, setPage] = useState(0);
  const perms = state.permissions;
  const get = (sid: string, field: Permission['field']) => perms.find((p) => p.season_id === sid && p.field === field)?.allowed_values ?? [];
  const setVals = (sid: string, field: Permission['field'], values: string[]) => {
    const rest = perms.filter((p) => !(p.season_id === sid && p.field === field));
    dispatch({ type: 'set', patch: { permissions: values.length ? [...rest, { season_id: sid, field, allowed_values: values }] : rest } });
  };
  const toggle = (sid: string, field: Permission['field'], v: string) => {
    const cur = get(sid, field);
    setVals(sid, field, cur.includes(v) ? cur.filter((x) => x !== v) : [...cur, v]);
  };

  if (adding) {
    const slot = state.slots[adding.season]; const s = state.seasons[adding.season];
    return (
      <Shell prompt={{ ar: 'اختار الميعاد اللي ممكن نجرّبه.', en: 'Choose a date we may try.' }}>
        <h2 className="question q-small">{t({ ar: `ميعاد تاني لـ${PLANT[plantOf(s.crop_id)].def}`, en: `Another date for ${PLANT[plantOf(s.crop_id)].en.toLowerCase()}` })} · <SeasonName slot={slot} /></h2>
        {adding.ym && <p className="sub">{MONTHS[L][adding.ym.m - 1]} {num(adding.ym.y, L)}</p>}
        <DatePicker slot={slot} today={state.today} ym={adding.ym} onMonth={(ym) => setAdding({ ...adding, ym })}
          onDay={(d) => { const cur = get(s.season_id, 'sowing_date'); if (d !== s.sowing_date && !cur.includes(d)) setVals(s.season_id, 'sowing_date', [...cur, d].sort()); setAdding(null); }} />
        <button className="secondary wide-btn" onClick={() => setAdding(null)}><Icon name="back" />{t({ ar: 'رجوع', en: 'Back' })}</button>
      </Shell>);
  }

  const plants = plantsFrom(state.cropIds);
  if (cropFor !== null) {
    const s = state.seasons[cropFor]; const others = plants.filter((pl) => pl.plant !== plantOf(s.crop_id));
    const pages = Math.max(1, Math.ceil(others.length / 4)); const shown = others.slice((page % pages) * 4, (page % pages) * 4 + 4);
    const chosen = get(s.season_id, 'crop_id');
    return (
      <Shell prompt={{ ar: 'أنهي محصول ممكن نجرّبه بداله؟', en: 'Which crop may we try instead?' }}>
        <h2 className="question q-small">{t({ ar: `بدل ${PLANT[plantOf(s.crop_id)].def}`, en: `Instead of ${PLANT[plantOf(s.crop_id)].en.toLowerCase()}` })} · <SeasonName slot={state.slots[cropFor]} /></h2>
        <div className="tiles four">{shown.map((pl) => { const id = pl.options[0].crop_id; return (
          <div className="tile-wrap" key={id}><button className="tile" aria-pressed={chosen.includes(id)} onClick={() => toggle(s.season_id, 'crop_id', id)}><span className="art"><CropArt plant={pl.plant} /></span>{t(PLANT[pl.plant])}</button></div>); })}</div>
        <div className={pages > 1 ? 'two-btns' : ''}>
          {pages > 1 && <button className="secondary" onClick={() => setPage(page + 1)}><Icon name="plus" />{t({ ar: 'محاصيل تانية', en: 'More crops' })} {num((page % pages) + 1, L)}/{num(pages, L)}</button>}
          <button className={`primary ${pages > 1 ? '' : 'wide-btn'}`} onClick={() => { setCropFor(null); setPage(0); }}><Icon name="check" />{t({ ar: 'تمام', en: 'Done' })}</button>
        </div>
      </Shell>);
  }
  return (
    <Shell prompt={{ ar: 'إيه اللي ممكن يتغيّر علشان ندوّر على بدايل؟', en: 'What may change so we can look for alternatives?' }}>
      <h2 className="question">{t({ ar: 'إيه اللي ممكن يتغيّر؟', en: 'What may change?' })}</h2>
      {state.seasons.map((s, i) => {
        if (!known(s.crop_id)) return null;
        const cutLocked = state.locks[s.season_id] && asksLastCut(s.crop_id);
        if (cutLocked) return null; // a protected cut never moves
        const cropLocked = !!state.locks[s.season_id];
        const dates = get(s.season_id, 'sowing_date'); const crops = get(s.season_id, 'crop_id');
        const p = PLANT[plantOf(s.crop_id)];
        return (
          <div className="perm" key={s.season_id}>
            <span className="s-art"><CropArt plant={plantOf(s.crop_id)} /></span>
            <div>
              <b>{t(p)} · <SeasonName slot={state.slots[i]} /></b>
              {s.sowing_date && s.sowing_date !== 'unknown' && <span className="was">{t({ ar: 'الزراعة دلوقتي', en: 'sowing now' })} <DateText value={s.sowing_date} noYear /></span>}
              <div className="pchips">
                {dates.map((d) => <button key={d} className="pchip" aria-pressed onClick={() => toggle(s.season_id, 'sowing_date', d)}><Icon name="check" /><DateText value={d} noYear /></button>)}
                {!asksLastCut(s.crop_id) && <button className="pchip" aria-pressed={false} onClick={() => setAdding({ season: i })}><Icon name="calendar" />{t({ ar: 'ميعاد تاني', en: 'Another date' })}</button>}
                {crops.map((id) => <button key={id} className="pchip" aria-pressed onClick={() => toggle(s.season_id, 'crop_id', id)}><Icon name="check" />{t(PLANT[plantOf(id)])}</button>)}
                {!cropLocked && <button className="pchip" aria-pressed={false} onClick={() => setCropFor(i)}><Icon name="plus" />{t({ ar: 'محصول تاني', en: 'Another crop' })}</button>}
              </div>
            </div>
          </div>);
      })}
      <div className="two-btns">
        <button className="primary" onClick={() => dispatch({ type: 'go', route: 'scope' })}><Icon name="check" />{t({ ar: 'التالي', en: 'Next' })}</button>
        <button className="secondary" onClick={() => { dispatch({ type: 'set', patch: { journey: 'check', permissions: [] } }); dispatch({ type: 'go', route: 'scope' }); }}>{t({ ar: 'مفيش حاجة تتغيّر', en: 'Nothing may change' })}</button>
      </div>
    </Shell>
  );
}

/** Readback of what will be checked, then ONE explicit confirm (exploration_confirmed). Silence/"yeah" never confirm. */
export function ScopeReadback() {
  const { state, dispatch, client, t } = useApp();
  const voice = useVoiceCtx();
  const L = state.locale;
  const explore = state.journey === 'explore' && state.permissions.length > 0;
  const confirm = () => { voice.stop(); dispatch({ type: 'set', patch: { confirmed: true, stale: false, plan: null } }); dispatch({ type: 'go', route: 'checking' }); };
  const onTranscript = async (text: string) => {
    const r = await client.interpret({ question_id: 'confirm_scope', locale: L, transcript: text, season_order: 1 });
    voice.settle();
    if (r.status === 'ok' && r.extraction.answer.confirm) return confirm();
    if (r.status === 'ok' && r.extraction.answer.yes_no === 'yes') return voice.speak({ ar: 'علشان أتأكد: قول "أكّد" أو دوس الزرار.', en: 'To be sure: say “confirm” or press the button.' });
    voice.notUnderstood();
  };
  const items = state.seasons.map((s) => ({
    cropId: s.crop_id, date: s.last_cut_date ?? (s.sowing_date !== 'unknown' ? s.sowing_date : null), kind: (s.last_cut_date ? 'end' : 'start') as 'end' | 'start',
    mark: state.locks[s.season_id] ? ('lock' as const) : state.permissions.some((p) => p.season_id === s.season_id) && explore ? ('change' as const) : undefined,
    cls: state.locks[s.season_id] ? 'lock' : '',
  }));
  const unknowns = state.seasons.flatMap((s, i) => [
    ...(s.crop_id === 'unknown' ? [{ ar: `محصول الموسم ${num(i + 1, 'ar')}: مش معروف`, en: `Season ${i + 1} crop: unknown` }] : []),
    ...(s.sowing_date === 'unknown' ? [{ ar: `ميعاد زراعة ${PLANT[plantOf(s.crop_id)].def}: مش معروف`, en: `${PLANT[plantOf(s.crop_id)].en} sowing date: unknown` }] : []),
  ]);
  return (
    <Shell onTranscript={onTranscript} prompt={explore ? { ar: 'ده اللي هنشيّك عليه وندوّر فيه. لو تمام، قول "أكّد".', en: 'This is what we will check and search. If that is right, say “confirm”.' } : { ar: 'هنشيّك على خطتك زي ما هي. لو تمام، قول "أكّد".', en: 'We will check your plan as it is. If that is right, say “confirm”.' }}>
      {state.stale && <div className="banner unknown"><Icon name="review" /><span>{t({ ar: 'غيّرت حاجة: أكّد تاني', en: 'Something changed: confirm again' })}</span></div>}
      <h2 className="question">{explore ? t({ ar: 'هنشيّك وندوّر في كده', en: 'This is what we will check' }) : t({ ar: 'هنشيّك على خطتك', en: 'We will check your plan' })}</h2>
      <SeasonStrip items={items} inline compact />
      <ul className="scope-list">
        {explore && state.permissions.map((p) => {
          const s = state.seasons.find((x) => x.season_id === p.season_id)!;
          return (
            <li key={p.season_id + p.field} className="ok"><Icon name="search" />
              <span>{p.field === 'sowing_date'
                ? <>{t(PLANT[plantOf(s.crop_id)])}: {p.allowed_values.map((d, k) => <span key={d}>{k ? t({ ar: ' أو ', en: ' or ' }) : ''}<DateText value={d} noYear /></span>)}</>
                : <>{t({ ar: 'بدل', en: 'Instead of' })} {t(PLANT[plantOf(s.crop_id)])}: {p.allowed_values.map((c) => t(PLANT[plantOf(c)])).join(t({ ar: ' أو ', en: ' or ' }))}</>}
              </span></li>);
        })}
        {unknowns.map((u, k) => <li key={k} className="unk"><Icon name="unknown" /><span>{t(u)}</span></li>)}
      </ul>
      <button className="primary wide-btn" onClick={confirm}><Icon name={explore ? 'search' : 'check'} />{explore ? t({ ar: 'أكّد ودوّر', en: 'Confirm and search' }) : t({ ar: 'أكّد وشيّك', en: 'Confirm and check' })}</button>
    </Shell>
  );
}
