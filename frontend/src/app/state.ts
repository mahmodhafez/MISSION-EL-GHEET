import { createContext, useContext } from 'react';
import type { Bi, Locale } from '../i18n/format';
import type { IntakeSnapshot, Permission, PlanResponse, PlannerClient, SeasonEntry } from '../services/plannerClient';
import { slotsFrom, todayIso, type SeasonSlot } from '../domain/seasons';

export type Route =
  | 'start' | 'intent' | 'practice'
  | 'intake' | 'protect' | 'permit' | 'scope'
  | 'checking' | 'result' | 'why' | 'failed'
  | 'options' | 'inspect' | 'try'
  | 'replay' | 'forecast' | 'summary';

export type Field = 'crop' | 'purpose' | 'month' | 'day' | 'sownMonth' | 'sownDay' | 'done';

export interface State {
  locale: Locale;
  route: Route;
  history: Route[];
  audioUnlocked: boolean;
  journey: 'check' | 'explore';
  today: string;
  slots: SeasonSlot[];
  cropIds: string[];
  lockedCropIds: string[];
  cropsPending: boolean;
  dataRelease: string | null;
  seasons: SeasonEntry[];
  cursor: { season: number; field: Field; ym?: { y: number; m: number } };
  clarify: boolean;
  msg: Bi | null;
  heard: { chips: Bi[]; undo: SeasonEntry[] } | null;
  locks: Record<string, boolean>;
  permissions: Permission[];
  confirmed: boolean;
  stale: boolean;
  plan: PlanResponse | null;
  pick: number;
  practiced: boolean;
}

/** First winter slot: the winter season running now or next (Nov 2026 → winter 2026/27). */
export function firstWinter(today: string) {
  const [y, m] = today.split('-').map(Number);
  return m >= 6 ? y : y - 1;
}

export function initialState(now = new Date()): State {
  const today = todayIso(now);
  const slots = slotsFrom(firstWinter(today));
  return {
    locale: 'ar', route: 'start', history: [], audioUnlocked: false, journey: 'explore', today, slots,
    cropIds: [], lockedCropIds: [], cropsPending: false, dataRelease: null,
    seasons: slots.map((s) => ({ season_id: s.id, crop_id: null, purpose: null, sowing_date: null, last_cut_date: null })),
    cursor: { season: 0, field: 'crop' }, clarify: false, msg: null, heard: null,
    locks: {}, permissions: [], confirmed: false, stale: false, plan: null, pick: 0, practiced: false,
  };
}

export type Action =
  | { type: 'set'; patch: Partial<State> }
  | { type: 'go'; route: Route }
  | { type: 'back' }
  | { type: 'season'; index: number; patch: Partial<SeasonEntry>; cursor?: State['cursor'] };

export function reducer(s: State, a: Action): State {
  switch (a.type) {
    case 'set': return { ...s, ...a.patch };
    case 'go': return a.route === s.route ? s : { ...s, route: a.route, history: [...s.history, s.route], msg: null, heard: null, clarify: false };
    case 'back': {
      const h = [...s.history]; const prev = h.pop();
      return prev ? { ...s, route: prev, history: h, msg: null, heard: null, clarify: false } : s;
    }
    case 'season': {
      const seasons = s.seasons.map((x, i) => (i === a.index ? { ...x, ...a.patch } : x));
      // Editing a confirmed fact makes the last check not current (design §3).
      return { ...s, seasons, cursor: a.cursor ?? s.cursor, stale: s.confirmed ? true : s.stale };
    }
  }
}

export function snapshotOf(s: State): IntakeSnapshot {
  return { journey: s.journey, seasons: s.seasons, locks: s.locks, permissions: s.journey === 'explore' ? s.permissions : [] };
}

export interface AppCtx {
  state: State;
  dispatch: (a: Action) => void;
  client: PlannerClient;
  t: (b: Bi) => string;
}
export const AppContext = createContext<AppCtx | null>(null);
export function useApp() {
  const c = useContext(AppContext);
  if (!c) throw new Error('AppContext missing');
  return c;
}
