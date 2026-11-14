import exportDoc from './uh001.json';
import type { IntakeSnapshot, PlannerClient, Extraction, InterpretResponse } from '../plannerClient';
import type { PlanningResult } from '../types';

/* DEVELOPMENT ADAPTER, clearly labelled in the UI.
 * - Promise Test: returns the REAL planner output exported from meg_core for UH-001, but only when the
 *   farmer-entered plan matches that fixture exactly. Any other plan → `planner_not_connected`.
 *   No scenario-ID branching and no invented results (frontend handoff).
 * - Replay, forecast and saving are not connected → `unavailable` with a reason.
 * - Speech: a tiny keyword extractor that returns the Gemini schema shape, standing in for the backend. */

type Signature = typeof exportDoc.signature;

export function signatureOf(s: IntakeSnapshot): Signature {
  const commitments: Signature['commitments'] = [];
  for (const season of s.seasons) {
    if (!s.locks[season.season_id] || !season.crop_id) continue;
    if (season.last_cut_date) commitments.push({ season_id: season.season_id, kind: 'harvest_or_cut_date', value: season.last_cut_date });
    else {
      commitments.push({ season_id: season.season_id, kind: 'crop', value: season.crop_id });
      if (season.purpose) commitments.push({ season_id: season.season_id, kind: 'purpose', value: season.purpose });
    }
  }
  commitments.sort((a, b) => (a.season_id + a.kind).localeCompare(b.season_id + b.kind));
  return {
    seasons: s.seasons.map((x) => ({
      crop_id: x.crop_id,
      purpose: x.purpose,
      sowing_date: x.sowing_date === 'unknown' ? null : x.sowing_date,
      last_cut_date: x.last_cut_date,
    })) as Signature['seasons'],
    commitments,
    choices: s.journey === 'explore' ? s.permissions.map((p) => ({ season_id: p.season_id, field: p.field, allowed_values: [...p.allowed_values].sort() })) : [],
  };
}

const same = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);

export function createDevClient(): PlannerClient {
  return {
    kind: 'dev',
    async catalogue() {
      // Same picture as the server (14 Nov 2026): these catalogue crops have no reviewed KB evidence yet.
      return { data_release: exportDoc.data_release, crop_ids: exportDoc.result.scope.available_crop_ids, locked_ids: ['rice', 'faba_bean', 'sugar_beet', 'egyptian_cotton'] };
    },
    async promiseTest(snapshot) {
      await new Promise((r) => setTimeout(r, 900)); // let "checking" be seen
      if (!same(signatureOf(snapshot), exportDoc.signature)) return { status: 'unavailable', reason: 'planner_not_connected' };
      return { status: 'ok', source: 'dev-export', data_release: exportDoc.data_release, result: exportDoc.result as unknown as PlanningResult };
    },
    async replay(): Promise<{ status: 'unavailable'; reason: string }> {
      return { status: 'unavailable', reason: 'replay_not_connected' };
    },
    async forecast() {
      // UH-001 decisions are months away; the outlook covers 7 days (reference scenario §5).
      return { status: 'not_applicable', reason: 'outside_forecast_window' };
    },
    async saveEvidence() {
      return { status: 'unavailable', reason: 'server_not_connected' };
    },
    async interpret(req): Promise<InterpretResponse> {
      return devExtract(req.transcript, req.season_order);
    },
  };
}

/* ---------- dev stand-in for Gemini extraction (NOT the real interpreter) ---------- */
const AR_DIGITS = '٠١٢٣٤٥٦٧٨٩';
const MONTHS: [RegExp, number][] = [
  [/يناير|january/, 1], [/فبراير|february/, 2], [/مارس|march/, 3], [/ابريل|أبريل|april/, 4], [/مايو|may/, 5], [/يونيو|june/, 6],
  [/يوليو|july/, 7], [/اغسطس|أغسطس|august/, 8], [/سبتمبر|september/, 9], [/اكتوبر|أكتوبر|october/, 10], [/نوفمبر|november/, 11], [/ديسمبر|december/, 12],
];
function norm(t: string) {
  return t.toLowerCase().replace(/[٠-٩]/g, (d) => String(AR_DIGITS.indexOf(d))).replace(/[ًٌٍَُِّْـ]/g, '').replace(/[إأآ]/g, 'ا').replace(/ى/g, 'ي');
}
export function devExtract(transcript: string, seasonOrder: number): InterpretResponse {
  const t = norm(transcript);
  const ex: Extraction = { seasons: [], area: null, answer: { yes_no: null, confirm: null, dont_know: null }, ambiguous: [], off_topic: false };
  const season = { order: seasonOrder, crop: null as string | null, crop_said: null as string | null, purpose: null as string | null, sowing_date: null as Extraction['seasons'][0]['sowing_date'], last_cut_date: null as Extraction['seasons'][0]['last_cut_date'], must_stay: null as boolean | null };
  if (/برسيم|berseem|clover/.test(t)) season.crop = 'berseem';
  else if (/شاميه|شامية|maize/.test(t)) season.crop = 'grain_maize';
  else if (/رفيعه|رفيعة|sorghum/.test(t)) season.crop = 'grain_sorghum';
  else if (/قمح|wheat/.test(t)) season.crop = 'wheat';
  else if (/ذره|ذرة|درة|corn/.test(t)) ex.ambiguous.push({ path: `seasons[${seasonOrder - 1}].crop`, said: 'ذرة', options: ['grain_maize', 'grain_sorghum'] });
  const day = t.match(/(\d{1,2})/);
  const month = MONTHS.find(([re]) => re.test(t));
  const year = t.match(/(20\d\d)/);
  if (month) season.sowing_date = { day: day && !year?.[0].startsWith(day[1]) ? +day[1] : null, month: month[1], year: year ? +year[1] : null };
  if (/مش عارف|مش فاكر|معرفش|don.?t know|not sure/.test(t)) ex.answer.dont_know = true;
  if (/^(ايوه|اه|ايوا|تمام|صح|yes|yeah|right)\b/.test(t)) ex.answer.yes_no = 'yes';
  if (/^(لا|لأ|no)\b/.test(t)) ex.answer.yes_no = 'no';
  if (/اكد|دور|confirm|search/.test(t)) ex.answer.confirm = true;
  if (/ازرع ايه|انهي احسن|what should i|which is best/.test(t)) ex.off_topic = true;
  if (season.crop || season.sowing_date) ex.seasons.push(season);
  const found = ex.seasons.length || ex.ambiguous.length || ex.off_topic || ex.answer.yes_no || ex.answer.confirm || ex.answer.dont_know;
  return found ? { status: 'ok', extraction: ex } : { status: 'no_match' };
}
