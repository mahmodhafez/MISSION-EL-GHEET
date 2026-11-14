import type { Candidate, Check, PlanEvaluation, PlanningResult } from '../../services/types';
import type { Bi } from '../../i18n/format';

/* Turns planner codes + params into what screens show. Codes not listed here fall back to a generic
 * line; the real wording will come from backend templates (D4). */

export const failing = (e: PlanEvaluation) => e.checks.filter((c) => c.outcome === 'fail');

export interface ConflictPair { sowSeason: string; sowDate: string; cutSeason: string | null; cutDate: string }
export function conflictPair(e: PlanEvaluation): ConflictPair | null {
  const c = failing(e).find((x) => x.explanation.code === 'sowing_before_protected_cut');
  if (!c) return null;
  const p = c.explanation.params as Record<string, string>;
  return { sowSeason: p.season_id, sowDate: p.sowing_date, cutSeason: c.season_ids.find((s) => s !== p.season_id) ?? null, cutDate: p.protected_cut_date };
}

export interface PrepSteps { cutDate: string | null; releaseDate: string; days: number; earliest: string }
export function prepSteps(e: PlanEvaluation): PrepSteps | null {
  const c = failing(e).find((x) => x.explanation.code === 'preparation_shortfall');
  if (!c) return null;
  const p = c.explanation.params as Record<string, string | number>;
  return { cutDate: conflictPair(e)?.cutDate ?? null, releaseDate: String(p.release_date), days: Number(p.preparation_days), earliest: String(p.earliest_sowing_date) };
}

/** Seasons involved in a failing hard check (for red marks). */
export const conflictSeasons = (e: PlanEvaluation) => new Set(failing(e).flatMap((c) => c.explanation.params.season_id ? [String(c.explanation.params.season_id)] : c.season_ids.slice(-1)));

/** Top reasons a plan needs review, from its unknown checks (farmer words + what is missing). */
const NOT_KNOWN: Bi = { ar: 'لسه مش معروف', en: 'not known yet' };
const REASONS: [string, string, Bi, Bi][] = [
  ['endpoint_mapping_missing', 'cut', { ar: 'ميعاد الحصاد', en: 'Harvest date' }, NOT_KNOWN],
  ['irrigation_availability_unknown', 'drop', { ar: 'المية', en: 'Water' }, NOT_KNOWN],
  ['soil_suitability_unknown', 'soil', { ar: 'التربة', en: 'Soil' }, NOT_KNOWN],
  ['cultivar_availability_unknown', 'sow', { ar: 'الصنف', en: 'Variety' }, NOT_KNOWN],
  ['forage_quantity_unknown', 'cow', { ar: 'كمية العلف', en: 'Feed amount' }, NOT_KNOWN],
  ['sowing_support_unverified', 'calendar', { ar: 'ميعاد الزراعة', en: 'Sowing date' }, { ar: 'الأبحاث لسه ماأكّدتهوش', en: 'not yet confirmed by research' }],
];
export function reviewReasons(e: PlanEvaluation, max = 4) {
  const codes = new Set(e.checks.filter((c) => c.outcome === 'unknown').map((c) => c.explanation.code));
  return REASONS.filter(([code]) => codes.has(code)).slice(0, max).map(([, icon, label, note]) => ({ icon, label, note }));
}

export interface DirectChange { season_id: string; field: string; value: string | null }
export function directChanges(c: Candidate): DirectChange[] {
  return c.changes.filter((x) => x.direct).map((x) => ({ season_id: x.season_id, field: x.field, value: x.after.value == null ? null : String(x.after.value) }));
}
export const unknownAfter = (c: Candidate) => c.changes.filter((x) => !x.direct && x.after.value == null).map((x) => ({ season_id: x.season_id, field: x.field }));

/** Choices the search could not try (e.g. no profile for that crop in the KB). */
export function blockedChoices(r: PlanningResult) {
  const seen = new Set<string>();
  return r.exclusions.filter((x) => x.kind === 'blocked').filter((x) => { const k = x.code + x.choice_ids.join(); if (seen.has(k)) return false; seen.add(k); return true; });
}

export const isHard = (c: Check) => c.effect === 'hard';
