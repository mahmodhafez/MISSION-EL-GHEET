import type { ResearchNote } from '../../services/plannerClient';

const day = (isoDate: string) => {
  const [y, m, d] = isoDate.split('-').map(Number);
  return Date.UTC(y, m - 1, d) / 86400000;
};

export interface TimelineLayout { bandStart: number; bandWidth: number; marker: number | null }

/**
 * Placement of a research window and the farmer's date on one line, in percent of the line
 * (logical inline-start = earlier, so it flips in RTL via inset-inline-start). Pure geometry:
 * the window and the placement come from the backend; nothing here judges the date.
 */
export function timelineLayout(window: { start: string; end: string }, farmerDate: string | null): TimelineLayout {
  const s = day(window.start), e = Math.max(day(window.end), s);
  const f = farmerDate ? day(farmerDate) : null;
  const pad = Math.max(7, Math.round((e - s) * 0.25));
  const lo = Math.min(s, f ?? s) - pad, hi = Math.max(e, f ?? e) + pad;
  const pct = (x: number) => Math.round(((x - lo) / (hi - lo)) * 1000) / 10;
  return { bandStart: pct(s), bandWidth: Math.round((pct(e) - pct(s)) * 10) / 10, marker: f === null ? null : pct(f) };
}

export const noteIcon = (kind: ResearchNote['kind']) =>
  kind === 'sowing_window' ? 'sow' : kind === 'trial_dates' ? 'calendar' : kind === 'maturity_days' ? 'calendar' : 'cut';

/** Advisory tone only: never "rejected". */
export const noteTone = (n: ResearchNote): 'inside' | 'review' | 'plain' =>
  n.placement === 'inside' ? 'inside' : n.placement === 'before' || n.placement === 'after' ? 'review' : 'plain';
