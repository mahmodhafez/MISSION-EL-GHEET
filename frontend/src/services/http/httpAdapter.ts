import type { ForecastResponse, InterpretResponse, IntakeSnapshot, PlannerClient, PlanResponse, RenderedResult, ReplayResponse, SaveResponse, Unavailable } from '../plannerClient';
import type { PlanningResult } from '../types';
import type { Locale } from '../../i18n/format';
import { devExtract } from '../dev/devAdapter';

/* HTTP adapter for /api/v1 (backend milestone 1). Same PlannerClient interface as the dev adapter,
 * so screens do not change. App answers go to POST /scenarios/from-answers, where the backend builds the
 * planner snapshot (unknowns explicit). TEMPORARY handwritten types until OpenAPI → TS generation. */

const apiLocale = (l: Locale) => (l === 'ar' ? 'ar-EG' : 'en');

export function createHttpClient(base = '/api/v1'): PlannerClient {
  let last: { scenarioId: string; resultId: string; result: PlanningResult; snapshot: IntakeSnapshot } | null = null;

  async function call<T>(path: string, init?: RequestInit): Promise<T> {
    const r = await fetch(base + path, { ...init, headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) } });
    const body = await r.json().catch(() => ({}));
    if (!r.ok) throw Object.assign(new Error(body?.error?.code ?? `http_${r.status}`), { code: body?.error?.code ?? `http_${r.status}` });
    return body as T;
  }
  const fail = (e: unknown): Unavailable => ({ status: 'unavailable', reason: (e as { code?: string })?.code ?? 'server_unreachable' });

  return {
    kind: 'http',
    async catalogue() {
      const c = await call<{ data_release: string; crop_ids: string[]; crops?: { approval: string }[] }>('/catalogue');
      return { data_release: c.data_release, crop_ids: c.crop_ids, pending: (c.crops ?? []).some((x) => x.approval !== 'approved') };
    },
    async promiseTest(s: IntakeSnapshot, ctx): Promise<PlanResponse> {
      try {
        const answers = {
          first_winter_year: ctx.firstWinterYear, journey: s.journey, seasons: s.seasons, locks: s.locks,
          permissions: s.journey === 'explore' ? s.permissions : [], confirm_exploration: s.journey === 'explore' && s.permissions.length > 0,
        };
        const sc = await call<{ id: string }>('/scenarios/from-answers', { method: 'POST', body: JSON.stringify(answers) });
        const out = await call<Record<string, unknown>>(
          `/scenarios/${sc.id}/promise-test?locale=${apiLocale(ctx.locale)}`, { method: 'POST' });
        last = { scenarioId: sc.id, resultId: out.result_id as string, result: out.result as PlanningResult, snapshot: s };
        return { status: 'ok', source: 'server', data_release: out.data_release as string, result: out.result as never, rendered: out.rendered as RenderedResult, result_id: out.result_id as string };
      } catch (e) { return fail(e); }
    },
    async relocalise(resultId, locale) {
      try { return (await call<{ rendered: RenderedResult | null }>(`/results/${resultId}?locale=${apiLocale(locale)}`)).rendered; } catch { return null; }
    },
    async replay(): Promise<ReplayResponse> {
      if (!last) return { status: 'unavailable', reason: 'no_scenario' };
      // Compare the season the options change (its current date first) with the option dates; else the planned sowings.
      const changed = [...last.result.review_investigations, ...last.result.feasible_alternatives]
        .map((c) => c.changes.find((x) => x.direct && x.field === 'sowing_date')).filter((x) => x?.after.value);
      const season = changed[0] ? last.snapshot.seasons.find((x) => x.season_id === changed[0]!.season_id) : undefined;
      const base = season?.sowing_date && season.sowing_date !== 'unknown' ? [season.sowing_date] : [];
      const dates = changed.length
        ? [...base, ...changed.map((c) => String(c!.after.value))]
        : last.snapshot.seasons.map((x) => x.sowing_date).filter((d): d is string => !!d && d !== 'unknown');
      if (!dates.length) return { status: 'unavailable', reason: 'no_sowing_dates' };
      try {
        return await call<ReplayResponse>(`/scenarios/${last.scenarioId}/replay`, { method: 'POST', body: JSON.stringify({ sow_dates: [...new Set(dates)].slice(0, 4), result_id: last.resultId }) });
      } catch (e) { return fail(e); }
    },
    async forecast(s): Promise<ForecastResponse> {
      const dates = s.seasons.map((x) => x.sowing_date).filter((d): d is string => !!d && d !== 'unknown');
      try { return await call<ForecastResponse>(`/forecast?${dates.map((d) => `action_dates=${d}`).join('&')}`); } catch (e) { return fail(e); }
    },
    async saveEvidence(): Promise<SaveResponse> {
      if (!last) return { status: 'unavailable', reason: 'no_result' };
      try {
        const c = await call<{ card_id: string }>(`/scenarios/${last.scenarioId}/evidence-cards`, { method: 'POST', body: JSON.stringify({ result_id: last.resultId }) });
        return { status: 'saved', card_id: c.card_id };
      } catch (e) { return fail(e); }
    },
    async interpret(req): Promise<InterpretResponse> {
      try {
        const r = await call<{ status: string; extraction?: InterpretResponse extends { extraction: infer X } ? X : never }>('/speech/interpret', {
          method: 'POST', body: JSON.stringify({ question_id: req.question_id, locale: apiLocale(req.locale), transcript: req.transcript, season_order: req.season_order }) });
        if (r.status === 'ok' && r.extraction) return { status: 'ok', extraction: r.extraction };
        // No Gemini key on this server: the labelled dev keyword extractor keeps voice usable in development.
        if (r.status === 'unavailable') return devExtract(req.transcript, req.season_order);
        return { status: 'no_match' };
      } catch { return devExtract(req.transcript, req.season_order); }
    },
  };
}
