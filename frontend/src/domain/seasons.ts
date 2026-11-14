/* Four consecutive season slots and the date limits used for touch input.
 * PLACEHOLDER windows (docs/design/voice-first.md §3, open question 6): winter October→May,
 * summer April→October. The planner spec says crop profiles set the supported dates; these windows
 * only stop impossible picks and need the planner owner's sign-off. */

export interface YearMonth { y: number; m: number }
export interface SeasonSlot { id: string; order: number; kind: 'winter' | 'summer'; startYear: number; label: string }

/** Four slots from a winter that starts in `firstWinterYear` (UH-001: winter 2026/27). */
export function slotsFrom(firstWinterYear: number): SeasonSlot[] {
  return [0, 1, 2, 3].map((i) => {
    const winter = i % 2 === 0;
    const startYear = firstWinterYear + Math.floor((i + 1) / 2);
    return { id: `s${i + 1}`, order: i + 1, kind: winter ? 'winter' : 'summer', startYear, label: `${winter ? 'winter' : 'summer'}-${startYear}` };
  });
}

export function monthsOf(slot: SeasonSlot): YearMonth[] {
  if (slot.kind === 'winter') return [10, 11, 12, 1, 2, 3, 4, 5].map((m) => ({ m, y: m >= 10 ? slot.startYear : slot.startYear + 1 }));
  return [4, 5, 6, 7, 8, 9, 10].map((m) => ({ m, y: slot.startYear }));
}

export const iso = (y: number, m: number, d: number) => `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
export const daysIn = (y: number, m: number) => new Date(y, m, 0).getDate();
export const todayIso = (now = new Date()) => iso(now.getFullYear(), now.getMonth() + 1, now.getDate());
export const isPast = (isoDate: string, today: string) => isoDate < today;
export const monthIsPast = (ym: YearMonth, today: string) => iso(ym.y, ym.m, daysIn(ym.y, ym.m)) < today;
