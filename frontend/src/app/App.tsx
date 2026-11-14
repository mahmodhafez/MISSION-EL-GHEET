import { useEffect, useMemo, useReducer } from 'react';
import { AppContext, initialState, reducer, type Route } from './state';
import { VoiceContext } from './voiceContext';
import { useVoice } from './useVoice';
import type { PlannerClient } from '../services/plannerClient';
import type { Bi } from '../i18n/format';
import { Start, Intent, Practice } from '../features/onboarding/Onboarding';
import { Intake } from '../features/farmer-intake/Intake';
import { Protect, Permit, ScopeReadback } from '../features/farmer-intake/Scope';
import { Checking, Failed, Result, Why } from '../features/promise-test/Result';
import { Options, Inspect, TryAgain } from '../features/promise-test/Options';
import { Summary } from '../features/evidence-card/Summary';
import { Replay } from '../features/season-replay/Replay';
import { Forecast } from '../features/forecast/Forecast';

const SCREENS: Record<Route, () => React.ReactElement | null> = {
  start: Start, intent: Intent, practice: Practice, intake: Intake, protect: Protect, permit: Permit, scope: ScopeReadback,
  checking: Checking, result: Result, why: Why, failed: Failed, options: Options, inspect: Inspect, try: TryAgain,
  replay: Replay, forecast: Forecast, summary: Summary,
};

export function App({ client }: { client: PlannerClient }) {
  const [state, dispatch] = useReducer(reducer, undefined, () => initialState());
  const voice = useVoice(state.locale);
  useEffect(() => { client.catalogue().then((c) => dispatch({ type: 'set', patch: { cropIds: c.crop_ids, lockedCropIds: c.locked_ids ?? [], cropsPending: !!c.pending, dataRelease: c.data_release } })); }, [client]);
  // Language switch: re-render the stored server result in the new language (planner not re-run).
  useEffect(() => {
    const p = state.plan;
    if (p?.status !== 'ok' || !p.result_id || !client.relocalise || p.rendered?.locale === (state.locale === 'ar' ? 'ar-EG' : 'en')) return;
    client.relocalise(p.result_id, state.locale).then((rendered) => { if (rendered) dispatch({ type: 'set', patch: { plan: { ...p, rendered } } }); });
  }, [state.locale, state.plan, client]);
  useEffect(() => { document.documentElement.lang = state.locale; document.documentElement.dir = state.locale === 'ar' ? 'rtl' : 'ltr'; }, [state.locale]);
  const ctx = useMemo(() => ({ state, dispatch, client, t: (b: Bi) => b[state.locale] }), [state, client]);
  const Screen = SCREENS[state.route];
  return (
    <AppContext.Provider value={ctx}>
      <VoiceContext.Provider value={voice}>
        <Screen />
      </VoiceContext.Provider>
    </AppContext.Provider>
  );
}
