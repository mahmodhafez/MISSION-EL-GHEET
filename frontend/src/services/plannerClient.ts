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
}
export type PlanResponse =
  | { status: 'ok'; source: 'dev-export' | 'server'; data_release: string; result: PlanningResult; rendered?: RenderedResult; result_id?: string }
  | Unavailable;
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
export type InterpretResponse = { status: 'ok'; extraction: Extraction } | { status: 'no_match' };

export interface PlannerClient {
  readonly kind: 'dev' | 'http';
  catalogue(): Promise<{ data_release: string; crop_ids: string[] }>;
  promiseTest(snapshot: IntakeSnapshot, ctx: { locale: Locale; firstWinterYear: number }): Promise<PlanResponse>;
  /** Re-render a stored result in another language without re-running the planner (server only). */
  relocalise?(resultId: string, locale: Locale): Promise<RenderedResult | null>;
  replay(snapshot: IntakeSnapshot): Promise<Unavailable>;
  forecast(snapshot: IntakeSnapshot): Promise<ForecastResponse>;
  saveEvidence(snapshot: IntakeSnapshot): Promise<SaveResponse>;
  interpret(req: { question_id: string; locale: Locale; transcript: string; season_order: number }): Promise<InterpretResponse>;
}
