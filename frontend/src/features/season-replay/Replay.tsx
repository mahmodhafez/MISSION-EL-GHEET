import { useEffect, useState } from 'react';
import { useApp, snapshotOf } from '../../app/state';
import { Shell } from '../../components/Shell';
import { Icon } from '../../components/Icon';
import { DateText, Hero } from '../../components/parts';
import { num } from '../../i18n/format';
import type { ReplayResponse } from '../../services/plannerClient';

/* Past weather (Season Replay): equal 14-day windows per sowing date in NASA POWER history (2001–2025) plus
 * typical conditions. It shows heat and air water demand only; it never changes a plan's status. */
const STATUS: Record<string, { cls: string; icon: string; ar: string; en: string }> = {
  rejected: { cls: 'rejected', icon: 'reject', ar: 'تعارض', en: 'Conflict' },
  needs_review: { cls: 'review', icon: 'review', ar: 'محتاج مراجعة', en: 'Needs review' },
  feasible: { cls: 'feasible', icon: 'feasible', ar: 'ماشية', en: 'Feasible' },
};
const toArDigits = (s: string) => s.replace(/(\d)\.(\d)/g, '$1٫$2').replace(/[0-9]/g, (d) => '٠١٢٣٤٥٦٧٨٩'[+d]);

export function Replay() {
  const { state, dispatch, client, t } = useApp();
  const [r, setR] = useState<ReplayResponse | null>(null);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { client.replay(snapshotOf(state)).then(setR); }, [client]);
  const L = state.locale;
  const cont = <button className="primary wide-btn push-end" onClick={() => dispatch({ type: 'back' })}><Icon name="check" />{t({ ar: 'كمّل', en: 'Continue' })}</button>;
  if (!r) return <Shell prompt={null}><Hero icon="sun" title={t({ ar: 'بجيب الجو اللي فات…', en: 'Loading past weather…' })} /></Shell>;
  if (r.status !== 'ok') {
    return (
      <Shell prompt={{ ar: 'مقارنة الجو اللي فات مش متاحة دلوقتي.', en: 'The past-weather comparison is not available right now.' }}>
        <Hero icon="sun" sub="unknown" unknown title={t({ ar: 'الجو اللي فات: مش متاح دلوقتي', en: 'Past weather: not available now' })} />
        <div className="chips-row"><span className="ichip no"><Icon name="reject" />{t({ ar: 'مش كمية الري', en: 'Not irrigation' })}</span></div>
        {cont}
      </Shell>);
  }
  const rep = r.replay;
  const fmt = (s: string) => { const c = s.replace(/\s?degC/g, '°C'); return L === 'ar' ? toArDigits(c) : c; };
  const mean = (w: string, m: string) => rep.layer_a_historical.windows[w]?.across_years[m]?.mean ?? null;
  const summary = rep.farmer_summary.filter((x) => x.kind === 'historical_comparison').slice(0, 1);
  return (
    <Shell prompt={{ ar: rep.farmer_summary[0]?.ar ?? rep.label.ar, en: rep.farmer_summary[0]?.en ?? rep.label.en }}>
      <h2 className="question" style={{ fontSize: 22 }}>{t({ ar: 'الجو في السنين اللي فاتت', en: 'Weather in past years' })}</h2>
      <div className="chips-row" style={{ justifyContent: 'flex-start' }}>
        <span className="ichip src"><Icon name="archive" />{t({ ar: 'ناسا', en: 'NASA' })} · {num(rep.layer_a_historical.years_used.length, L)} {t({ ar: 'سنة', en: 'years' })}</span>
        <span className="ichip no"><Icon name="reject" />{t({ ar: 'مش كمية الري', en: 'Not irrigation' })}</span>
      </div>
      <div className="replay-cards">
        {rep.windows.map((w) => {
          const st = STATUS[w.planner_status];
          const tmax = mean(w.window_id, 'tmax_mean_c'); const et0 = mean(w.window_id, 'et0_total_mm');
          return (
            <div className="replay-card" key={w.window_id}>
              <span className="big-date"><Icon name="sow" /><DateText value={w.sow_date} noYear short /></span>
              {st && <span className={`badge ${st.cls}`}><Icon name={st.icon} />{t(st)}</span>}
              <span className="m"><Icon name="thermo" />{tmax == null ? '—' : fmt(`${tmax.toFixed(1)}°`)}</span>
              <span className="m"><Icon name="drop" />{et0 == null ? '—' : `${num(Math.round(et0), L)} ${t({ ar: 'مم', en: 'mm' })}`}</span>
            </div>);
        })}
      </div>
      <ul className="replay-sum">{summary.map((s, k) => <li key={k}>{fmt(L === 'ar' ? s.ar : s.en)}</li>)}</ul>
      <p className="meta" style={{ margin: 0 }}>{fmt(L === 'ar' ? rep.label.ar : rep.label.en)}</p>
      {cont}
    </Shell>
  );
}
