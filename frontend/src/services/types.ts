/* Planner wire types, mirrored from the meg_core planner JSON output (planner/candidate-generation,
 * `planner_cli.py plan --json`). TEMPORARY: replace with types generated from the backend OpenAPI
 * once the FastAPI adapter exists (frontend handoff: no handwritten wire schema long term). */

export type PlanStatus = 'feasible' | 'rejected' | 'needs_review';
export type EvidenceStatus = 'verified' | 'proposed' | 'open';

export interface SourceRef { source_id: string; locator: string }

export interface Fact<T = string | number | null> {
  value: T | null;
  unknown_reason: string | null;
  origin: string;
  evidence_status: EvidenceStatus;
  confirmation_status: string;
  unit: string | null;
  source_refs: SourceRef[];
  method: string | null;
}

export interface Explanation { code: string; params: Record<string, string | number | boolean | null>; source_refs: SourceRef[] }

export interface Check {
  rule_id: string;
  rule_version: string;
  effect: 'hard' | 'review' | string;
  required_for: string;
  outcome: 'pass' | 'fail' | 'unknown' | 'not_applicable';
  season_ids: string[];
  commitment_ids: string[];
  explanation: Explanation;
  missing_input_paths: string[];
}

export interface PlanEvaluation {
  status: PlanStatus;
  checks: Check[];
  preserved_commitment_ids: string[];
  assumptions: Explanation[];
}

export interface SeasonPlan {
  season_id: string;
  order: number;
  season_label: string;
  crop_id: Fact<string>;
  purpose: Fact<string>;
  profile_id: Fact<string>;
  sowing_date: Fact<string>;
  harvest_or_cut_date: Fact<string>;
  crop_end_exclusive: Fact<string>;
  release_date: Fact<string>;
  preparation_days_after_release: Fact<number>;
}

export interface Change { season_id: string; field: string; before: Fact; after: Fact; direct: boolean }

export interface Candidate {
  candidate_id: string;
  kind: string;
  plan: SeasonPlan[];
  changes: Change[];
  evaluation: PlanEvaluation;
  choice_ids: string[];
  direct_season_ids: string[];
  source_refs: SourceRef[];
  tradeoffs: Explanation[];
}

export interface SearchSummary {
  status: 'complete' | 'incomplete';
  raw_count: number;
  evaluated_count: number;
  feasible_count: number;
  needs_review_count: number;
  rejected_count: number;
  blocked_count: number;
  uninstantiated_choice_ids: string[];
  limit_reason: string | null;
  policy_version: string;
  policy_approval: string;
}

export interface Exclusion { code: string; kind: 'blocked' | 'excluded'; choice_ids: string[]; season_ids: string[]; missing_input_paths: string[] }

export interface PlanningResult {
  current: PlanEvaluation;
  feasible_alternatives: Candidate[];
  review_investigations: Candidate[];
  rejected_candidates: Candidate[];
  search: SearchSummary;
  exclusions: Exclusion[];
  scope: { data_release: string; scope_hash: string | null; available_crop_ids: string[] };
}
