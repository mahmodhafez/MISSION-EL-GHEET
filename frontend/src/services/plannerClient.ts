import type { PlanningResult } from './types';
import type { Locale } from '../i18n/format';

/* The one interface screens use (frontend handoff: PlannerClient). The dev adapter implements it now;
 * the HTTP adapter will implement it against /api/v1 with no screen changes. */

/** What the farmer entered and confirmed, before it becomes a backend ScenarioSnapshot. */
export interface SeasonEntry {
  season_id: string;
  crop_id: string | null; // null = not answered; 'unknown' = farmer said "I don't know"
  purpose: string | null;
  sowing_date: string | null | 'unknown';
  last_cut_date: string | null;
}
export interface Permission { season_id: string; field: 'sowing_date' | 'crop_id'; allowed_values: string[] }
export interface IntakeSnapshot {
  journey: 'check' | 'explore';
  seasons: SeasonEntry[];
  locks: Record<string, boolean>;
  permissions: Permission[];
}

export type Unavailable = { status: 'unavailable'; reason: string };
/** Backend-rendered wording for one locale (design D4): `text` for the screen, `speech` for audio. */
export interface Rendered { code: string; version: number; text: string; speech: string }
export interface RenderedResult {
  locale: 'ar-EG' | 'en';
  headline: Rendered | null; conflicts: Rendered[]; why: Rendered | null;
  options: (Rendered & { candidate_id: string })[]; coverage: Rendered[]; review_reasons: Rendered[]; takeaway: Rendered | null;
  /** Sourced findings from the reviewed KB (advisory; never changes status). Absent with the dev adapter / older servers. */
  research?: ResearchBlock;
}
export interface ResearchSource { source_id: string; title: string; url: string | null; version: string | null; locator: string | null }
export type ResearchKind = 'sowing_window' | 'maturity_window' | 'harvest_window' | 'trial_dates' | 'maturity_days' | 'first_cut';
export interface ResearchNote {
  rule_id: string; kind: ResearchKind; title: string; text: string; speech: string;
  window: { start: string; end: string } | null; farmer_date: string | null;
  placement: 'before' | 'inside' | 'after' | null; days_outside: number | null;
  dates: string[]; where: string; source: ResearchSource;
}
export interface ResearchOther { rule_id: string; label: string; source_text: string; where: string; source: ResearchSource }
export interface ResearchSeason { season_id: string; crop_id: string; crop: string; notes: ResearchNote[]; other: ResearchOther[] }
export interface ResearchBlock { caveat: Rendered; seasons: ResearchSeason[]; empty_seasons: string[]; empty_hint: Rendered | null }
export type PlanResponse =
  | { status: 'ok'; source: 'dev-export' | 'server'; data_release: string; result: PlanningResult; rendered?: RenderedResult; result_id?: string }
  | Unavailable;
/** Season Replay (backend /replay): equal 14-day windows per sowing date; statuses echoed from the Promise Test. */
export interface ReplayWindow { window_id: string; sow_date: string; planner_status: string }
export interface Replay {
  status: string; label: { ar: string; en: string }; windows: ReplayWindow[];
  layer_a_historical: { years_used: number[]; windows: Record<string, { across_years: Record<string, { mean: number | null } | undefined> }> };
  farmer_summary: { kind: string; ar: string; en: string }[];
}
export type ReplayResponse = { status: 'ok'; replay: Replay } | Unavailable;
export type ForecastResponse = { status: 'available' | 'stale' | 'not_applicable' | 'unavailable'; reason?: string };
export type SaveResponse = { status: 'saved'; card_id: string } | Unavailable;

/** Gemini strict extraction (docs/backend/backend-design.md §8.3). Every field null unless said. */
export interface DateParts { day: number | null; month: number | null; year: number | null }
export interface Extraction {
  seasons: { order: number; crop: string | null; crop_said: string | null; purpose: string | null; sowing_date: DateParts | null; last_cut_date: DateParts | null; must_stay: boolean | null }[];
  area: { value: number | null; unit: string | null } | null;
  answer: { yes_no: 'yes' | 'no' | null; confirm: boolean | null; dont_know: boolean | null };
  ambiguous: { path: string; said: string; options: string[] }[];
  off_topic: boolean;
}
/** `busy`: the server's abuse limits said wait (429); the screen switches to pictures, it never retries by itself. */
export type InterpretResponse = { status: 'ok'; extraction: Extraction } | { status: 'no_match' } | { status: 'busy' };

export interface PlannerClient {
  readonly kind: 'dev' | 'http';
  /** `pending`: no crop in this release has agronomic sign-off, so tiles show a "needs review" badge. */
  /** `locked_ids`: crops shown greyed out and not selectable (no reviewed evidence in the KB yet). */
  catalogue(): Promise<{ data_release: string; crop_ids: string[]; pending?: boolean; locked_ids?: string[] }>;
  promiseTest(snapshot: IntakeSnapshot, ctx: { locale: Locale; firstWinterYear: number }): Promise<PlanResponse>;
  /** Re-render a stored result in another language without re-running the planner (server only). */
  relocalise?(resultId: string, locale: Locale): Promise<RenderedResult | null>;
  replay(snapshot: IntakeSnapshot): Promise<ReplayResponse>;
  forecast(snapshot: IntakeSnapshot): Promise<ForecastResponse>;
  saveEvidence(snapshot: IntakeSnapshot): Promise<SaveResponse>;
  interpret(req: { question_id: string; locale: Locale; transcript: string; season_order: number }): Promise<InterpretResponse>;
}
