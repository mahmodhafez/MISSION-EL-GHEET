import { useApp } from '../../app/state';
import { Shell } from '../../components/Shell';
import { Icon, CropArt } from '../../components/Icon';
import { Banner, DateText, SeasonStrip, plantOf, type StripItem } from '../../components/parts';
import { PLANT } from '../../i18n/strings';
import { dateText, num } from '../../i18n/format';
import type { Candidate } from '../../services/types';
import { blockedChoices, directChanges, reviewReasons } from './explain';

/* Feasible alternatives (≤2 shown), review investigations and what the search could not try.
 * No "best", no ranking score, nothing preselected. ML never proposes or ranks these. */

function label(c: Candidate, seasons: { season_id: string; crop_id: string | null }[]) {
  const ch = directChanges(c)[0];
  const s = seasons.find((x) => x.season_id === ch?.season_id);
  return { ch, plant: ch?.field === 'crop_id' ? plantOf(ch.value) : plantOf(s?.crop_id ?? null) };
}

export function Options() {
  const { state, dispatch, t } = useApp();
  if (state.plan?.status !== 'ok') return null;
  const r = state.plan.result;
  const feasible = r.feasible_alternatives.slice(0, 2);
  const review = r.review_investigations;
  const blocked = blockedChoices(r);
  const open = (list: 'f' | 'r', k: number) => { dispatch({ type: 'set', patch: { pick: list === 'f' ? k : 100 + k } }); dispatch({ type: 'go', route: 'inspect' }); };
  const dates = review.map((c) => directChanges(c)[0]?.value).filter(Boolean) as string[];
  const prompt = feasible.length
    ? { ar: `لقينا ${num(feasible.length, 'ar')} بديل ماشي بالشروط دي.`, en: `We found ${feasible.length} alternative${feasible.length > 1 ? 's' : ''} that hold under these conditions.` }
    : { ar: `مفيش بديل أكيد لسه.${dates.length ? ` فيه ${num(dates.length, 'ar')} ميعاد نراجعهم: ${dates.map((d) => dateText(d, 'ar', { noYear: true })).join(' و')}.` : ''}`, en: `No sure alternative yet.${dates.length ? ` There ${dates.length > 1 ? 'are' : 'is'} ${dates.length} date${dates.length > 1 ? 's' : ''} to check: ${dates.map((d) => dateText(d, 'en', { noYear: true })).join(' and ')}.` : ''}` };
  const coverage = state.plan.rendered?.coverage ?? [];
  const card = (c: Candidate, k: number, kind: 'f' | 'r') => {
    const { ch, plant } = label(c, state.seasons);
    return (
      <div className="date-card" key={c.candidate_id} style={kind === 'f' ? { borderColor: 'var(--feasible)' } : undefined}>
        <span className="s-art"><CropArt plant={plant} /></span>
        {ch?.field === 'sowing_date' && ch.value
          ? <><span className="big-date"><Icon name="sow" /><DateText value={ch.value} noYear /></span><span className="yr"><bdi>{num(ch.value.slice(0, 4), state.locale)}</bdi></span></>
          : <span className="big-date">{t(PLANT[plant])}</span>}
        {kind === 'f'
          ? <span className="badge feasible"><Icon name="feasible" />{t({ ar: 'ماشي بالشروط دي', en: 'Feasible under conditions' })}</span>
          : <span className="badge review"><Icon name="review" />{t({ ar: 'محتاج مراجعة', en: 'Needs review' })}</span>}
        <button className="secondary" onClick={() => open(kind, k)}><Icon name="search" />{t({ ar: 'شوف', en: 'Look' })}</button>
      </div>);
  };
  return (
    <Shell prompt={prompt}>
      {!feasible.length && <Banner kind="unknown" icon="unknown">{t({ ar: 'مفيش بديل أكيد', en: 'No sure alternative' })}<small>{t({ ar: 'ده رد صحيح · خطتك محفوظة', en: 'That is a real answer · your plan is kept' })}</small></Banner>}
      {feasible.length > 0 && <div className="date-cards">{feasible.map((c, k) => card(c, k, 'f'))}</div>}
      {review.length > 0 && <><h2 className="question" style={{ fontSize: 22 }}>{t({ ar: 'مواعيد نراجعها', en: 'Dates to check' })}</h2><div className="date-cards">{review.map((c, k) => card(c, k, 'r'))}</div></>}
      {coverage.length > 0 && (
        <ul className="scope-list">{(() => {
          const main = coverage.filter((c) => c.code !== 'search_incomplete');
          const note = coverage.find((c) => c.code === 'search_incomplete');
          return (main.length ? main : coverage.slice(0, 1)).map((c, k) => <li key={k} className="unk"><Icon name="unknown" /><span>{c.text}{note && main.length > 0 && k === 0 && <small>{note.text}</small>}</span></li>);
        })()}</ul>)}
      {coverage.length === 0 && (blocked.length > 0 || r.search.status === 'incomplete') && (
        <ul className="scope-list">
          {blocked.map((b) => {
            const sid = b.season_ids[0]; const perm = state.permissions.find((p) => p.season_id === sid && b.choice_ids.length);
            const what = perm?.field === 'crop_id' ? perm.allowed_values.map((c) => t(PLANT[plantOf(c)])).join('، ') : t({ ar: 'اختيار', en: 'A choice' });
            const i = state.seasons.findIndex((s) => s.season_id === sid);
            return <li key={b.code + sid} className="unk"><Icon name="unknown" /><span>{what} {t({ ar: 'في الموسم', en: 'in season' })} {num(i + 1, state.locale)}: {t({ ar: 'ماتشيّكش', en: 'not checked' })}<small>{t({ ar: 'مفيش بيانات كفاية · البحث مش كامل', en: 'not enough data · search incomplete' })}</small></span></li>;
          })}
        </ul>)}
      <button className="secondary wide-btn" onClick={() => dispatch({ type: 'go', route: 'summary' })}><Icon name="save" />{t({ ar: 'سيب خطتي واحفظها', en: 'Keep my plan and save it' })}</button>
    </Shell>
  );
}

function stripFor(seasons: { season_id: string; crop_id: string | null; sowing_date: string | null; last_cut_date: string | null }[], locks: Record<string, boolean>, changed?: Map<string, { field: string; value: string | null }>, conflict?: Set<string>): StripItem[] {
  return seasons.map((s) => {
    const ch = changed?.get(s.season_id);
    const cropId = ch?.field === 'crop_id' ? ch.value : s.crop_id;
    const date = ch?.field === 'sowing_date' ? ch.value : s.last_cut_date ?? (s.sowing_date !== 'unknown' ? s.sowing_date : null);
    if (ch) return { cropId, date, kind: 'start', mark: 'change', cls: 'change' };
    if (conflict?.has(s.season_id)) return { cropId, date, kind: 'start', mark: 'reject', cls: 'reject' };
    return { cropId, date, kind: s.last_cut_date ? 'end' : 'start', mark: locks[s.season_id] ? 'lock' : undefined, cls: locks[s.season_id] ? 'lock' : '' };
  });
}

function picked(state: ReturnType<typeof useApp>['state']): Candidate | null {
  if (state.plan?.status !== 'ok') return null;
  const r = state.plan.result;
  return state.pick >= 100 ? r.review_investigations[state.pick - 100] ?? null : r.feasible_alternatives[state.pick] ?? null;
}

export function Inspect() {
  const { state, dispatch, t } = useApp();
  const c = picked(state);
  if (!c || state.plan?.status !== 'ok') return null;
  const changes = new Map(directChanges(c).map((x) => [x.season_id, x]));
  const conflict = new Set(state.plan.result.current.checks.filter((x) => x.outcome === 'fail').map((x) => String(x.explanation.params.season_id ?? '')));
  const reasons = reviewReasons(c.evaluation);
  const first = directChanges(c)[0];
  const whatChanged = first?.field === 'sowing_date' && first.value ? <DateText value={first.value} noYear /> : first?.value ? t(PLANT[plantOf(first.value)]) : '';
  const firstSeason = state.seasons.find((s) => s.season_id === first?.season_id);
  const p = PLANT[plantOf(firstSeason?.crop_id ?? null)];
  return (
    <Shell prompt={{ ar: `لو ${p.def} ${first?.value && first.field === 'sowing_date' ? dateText(first.value, 'ar', { noYear: true }) : ''}: اللي عليه قفل بيفضل زي ما هو. ${reasons.length ? 'وفيه حاجات لسه مش معروفة، فمحتاج مراجعة.' : ''}`, en: `If the ${p.en.toLowerCase()} is on ${first?.value && first.field === 'sowing_date' ? dateText(first.value, 'en', { noYear: true }) : 'the new value'}: everything locked stays as it is. ${reasons.length ? 'Some things are still unknown, so it needs review.' : ''}` }}>
      <p className="strip-label">{t({ ar: 'خطتك', en: 'Your plan' })}</p>
      <SeasonStrip inline compact items={stripFor(state.seasons, state.locks, undefined, conflict)} />
      <p className="strip-label"><Icon name="search" />{t({ ar: 'بالتغيير ده:', en: 'With this change:' })} {whatChanged}</p>
      <SeasonStrip inline compact items={stripFor(state.seasons, state.locks, changes)} />
      {reasons.length > 0 && <><p className="strip-label"><Icon name="review" />{t({ ar: 'ليه محتاج مراجعة؟', en: 'Why it needs review' })}</p>
        <div className="facts" style={{ gridTemplateColumns: `repeat(${reasons.length}, minmax(0, 1fr))` }}>{reasons.map((r, k) => <span key={k} className="fact unk"><Icon name={r.icon} />{state.locale === 'ar' ? '؟' : '?'}<small>{t(r.label)}</small></span>)}</div></>}
      <div className="two-btns">
        <button className="primary" onClick={() => dispatch({ type: 'go', route: 'try' })}><Icon name="check" />{t({ ar: 'جرّبه', en: 'Try it' })}</button>
        <button className="secondary" onClick={() => dispatch({ type: 'back' })}><Icon name="back" />{t({ ar: 'رجوع', en: 'Back' })}</button>
      </div>
    </Shell>
  );
}

/** "Check again with this change?" The original plan is kept until a new one is saved. */
export function TryAgain() {
  const { state, dispatch, t } = useApp();
  const c = picked(state);
  if (!c) return null;
  const changes = new Map(directChanges(c).map((x) => [x.season_id, x]));
  const apply = () => {
    const seasons = state.seasons.map((s) => {
      const ch = changes.get(s.season_id);
      if (!ch) return s;
      return ch.field === 'sowing_date' ? { ...s, sowing_date: ch.value } : { ...s, crop_id: ch.value, sowing_date: null };
    });
    // A changed plan is a new proposal: it must be confirmed and checked again. Permissions are used up.
    dispatch({ type: 'set', patch: { seasons, journey: 'check', permissions: [], confirmed: false, stale: false, plan: null } });
    dispatch({ type: 'go', route: 'scope' });
  };
  return (
    <Shell prompt={{ ar: 'نشيّك على الخطة تاني بالتغيير ده؟ خطتك الأصلية محفوظة.', en: 'Check the plan again with this change? Your original plan is kept.' }}>
      <h2 className="question">{t({ ar: 'نشيّك تاني بالتغيير ده؟', en: 'Check again with this change?' })}</h2>
      <SeasonStrip inline compact items={stripFor(state.seasons, state.locks, changes)} />
      <p className="keepnote"><Icon name="lock" />{t({ ar: 'خطتك الأصلية محفوظة لحد ما تحفظ الجديدة', en: 'Your original plan is kept until you save a new one' })}</p>
      <button className="primary wide-btn push-end" onClick={apply}><Icon name="repeat" />{t({ ar: 'شيّك على الخطة تاني', en: 'Check the plan again' })}</button>
      <button className="secondary wide-btn" onClick={() => dispatch({ type: 'go', route: 'options' })}><Icon name="back" />{t({ ar: 'لأ، رجّع خطتي', en: 'No, back to my plan' })}</button>
    </Shell>
  );
}
