import { useEffect, useState } from 'react';
import { useApp, snapshotOf } from '../../app/state';
import { Shell } from '../../components/Shell';
import { Icon } from '../../components/Icon';
import { Hero } from '../../components/parts';
import type { ForecastResponse } from '../../services/plannerClient';

/* Experimental 7-day outlook, a side note only. Statuses follow the ML ↔ backend contract §6.
 * It never changes whether a plan holds. */
export function Forecast() {
  const { state, dispatch, client, t } = useApp();
  const [f, setF] = useState<ForecastResponse | null>(null);
  useEffect(() => { client.forecast(snapshotOf(state)).then(setF); }, [client, state]);
  const view = !f ? null
    : f.status === 'not_applicable' ? { sub: 'calendar', title: { ar: 'مش لخطتك دي', en: 'Not for this plan' }, text: { ar: 'التوقع لـ ٧ أيام بس', en: 'The outlook covers 7 days only' } }
    : f.status === 'stale' ? { sub: 'review', title: { ar: 'التوقع قديم', en: 'Outlook too old' }, text: { ar: 'مش هنعرضه', en: 'We will not show it' } }
    : f.status === 'unavailable' ? { sub: 'reject', title: { ar: 'التوقع مش متاح', en: 'Outlook not available' }, text: { ar: 'خطتك مش متأثرة', en: 'Your plan is not affected' } }
    : { sub: 'check', title: { ar: 'التوقع متاح', en: 'Outlook available' }, text: { ar: 'العرض لسه بيتعمل', en: 'Display still being built' } };
  return (
    <Shell prompt={view ? { ar: `${view.title.ar}. ${view.text.ar}.`, en: `${view.title.en}. ${view.text.en}.` } : null}>
      {view && <Hero icon="future" sub={view.sub} unknown title={t(view.title)} text={t(view.text)} />}
      <span className="badge sim" style={{ alignSelf: 'center' }}><Icon name="future" />{t({ ar: 'تجريبي', en: 'Experimental' })}</span>
      <button className="primary wide-btn push-end" onClick={() => dispatch({ type: 'back' })}><Icon name="check" />{t({ ar: 'كمّل', en: 'Continue' })}</button>
    </Shell>
  );
}
