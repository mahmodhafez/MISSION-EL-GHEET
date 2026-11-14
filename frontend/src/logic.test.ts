import { describe, expect, it } from 'vitest';
import exportDoc from './services/dev/uh001.json';
import { createDevClient, devExtract, signatureOf } from './services/dev/devAdapter';
import type { IntakeSnapshot } from './services/plannerClient';
import type { PlanningResult } from './services/types';
import { blockedChoices, conflictPair, directChanges, prepSteps, reviewReasons } from './features/promise-test/explain';
import { monthIsPast, monthsOf, slotsFrom } from './domain/seasons';
import { plantsFrom } from './domain/catalogue';
import { firstWinter } from './app/state';

const result = exportDoc.result as unknown as PlanningResult;

/** UH-001 as a farmer would enter it in the app (reference-scenario.md). */
const uh001: IntakeSnapshot = {
  journey: 'explore',
  seasons: [
    { season_id: 's1', crop_id: 'berseem', purpose: 'forage', sowing_date: 'unknown', last_cut_date: '2027-05-20' },
    { season_id: 's2', crop_id: 'grain_maize', purpose: 'grain', sowing_date: '2027-05-15', last_cut_date: null },
    { season_id: 's3', crop_id: 'wheat', purpose: 'grain', sowing_date: '2027-11-20', last_cut_date: null },
    { season_id: 's4', crop_id: 'grain_sorghum', purpose: 'grain', sowing_date: '2028-06-01', last_cut_date: null },
  ],
  locks: { s1: true, s2: true, s3: true },
  permissions: [
    { season_id: 's2', field: 'sowing_date', allowed_values: ['2027-06-01', '2027-05-28'] },
    { season_id: 's4', field: 'crop_id', allowed_values: ['grain_maize'] },
  ],
};

describe('dev adapter', () => {
  it('signature of the UI-entered UH-001 equals the planner fixture signature', () => {
    expect(signatureOf(uh001)).toEqual(exportDoc.signature);
  });
  it('returns the real planner export for UH-001', async () => {
    const r = await createDevClient().promiseTest(uh001, { locale: 'en', firstWinterYear: 2026 });
    expect(r.status).toBe('ok');
    if (r.status === 'ok') {
      expect(r.source).toBe('dev-export');
      expect(r.result.current.status).toBe('rejected');
      expect(r.result.feasible_alternatives).toHaveLength(0);
      expect(r.result.review_investigations).toHaveLength(2);
    }
  });
  it('never invents a result for any other plan', async () => {
    const other = { ...uh001, seasons: uh001.seasons.map((s, i) => (i === 1 ? { ...s, sowing_date: '2027-05-16' } : s)) };
    expect(await createDevClient().promiseTest(other, { locale: 'en', firstWinterYear: 2026 })).toEqual({ status: 'unavailable', reason: 'planner_not_connected' });
  });
  it('save, replay are honest about not being connected', async () => {
    const c = createDevClient();
    expect((await c.saveEvidence(uh001)).status).toBe('unavailable');
    expect((await c.replay(uh001)).status).toBe('unavailable');
  });
});

describe('dev extraction (Gemini schema stand-in)', () => {
  it('ambiguous ذرة is not guessed', () => {
    const r = devExtract('ذرة', 2);
    expect(r.status).toBe('ok');
    if (r.status === 'ok') { expect(r.extraction.seasons).toHaveLength(0); expect(r.extraction.ambiguous[0].options).toEqual(['grain_maize', 'grain_sorghum']); }
  });
  it('a date without a year keeps year null', () => {
    const r = devExtract('٢٠ مايو', 1);
    if (r.status !== 'ok') throw new Error('expected ok');
    expect(r.extraction.seasons[0].sowing_date).toEqual({ day: 20, month: 5, year: null });
  });
  it('nothing recognisable → no_match', () => expect(devExtract('السلام عليكم', 1).status).toBe('no_match'));
});

describe('planner output → screens', () => {
  it('conflict pair and preparation steps come from the codes and params', () => {
    expect(conflictPair(result.current)).toEqual({ sowSeason: 's2', sowDate: '2027-05-15', cutSeason: 's1', cutDate: '2027-05-20' });
    expect(prepSteps(result.current)).toEqual({ cutDate: '2027-05-20', releaseDate: '2027-05-21', days: 7, earliest: '2027-05-28' });
  });
  it('investigations, review reasons and blocked choices', () => {
    expect(result.review_investigations.map((c) => directChanges(c)[0].value)).toEqual(['2027-05-28', '2027-06-01']);
    expect(reviewReasons(result.review_investigations[0].evaluation).map((r) => r.label.en)).toEqual(['Harvest date', 'Water', 'Soil', 'Variety']);
    expect(blockedChoices(result)).toHaveLength(1);
    expect(result.search.status).toBe('incomplete');
  });
});

describe('seasons and catalogue', () => {
  it('four slots from winter 2026/27', () => {
    expect(firstWinter('2026-11-14')).toBe(2026);
    expect(slotsFrom(2026).map((s) => s.label)).toEqual(['winter-2026', 'summer-2027', 'winter-2027', 'summer-2028']);
  });
  it('winter months carry their year; past months are past', () => {
    const w = monthsOf(slotsFrom(2026)[0]);
    expect(w[0]).toEqual({ m: 10, y: 2026 });
    expect(w.at(-1)).toEqual({ m: 5, y: 2027 });
    expect(monthIsPast({ m: 10, y: 2026 }, '2026-11-14')).toBe(true);
    expect(monthIsPast({ m: 11, y: 2026 }, '2026-11-14')).toBe(false);
  });
  it('one picture per plant from the catalogue; purposes only when several', () => {
    const p = plantsFrom(result.scope.available_crop_ids);
    expect(p.map((x) => x.plant)).toEqual(['berseem', 'maize', 'wheat', 'sorghum']);
    expect(p.every((x) => x.options.length === 1)).toBe(true);
  });
});
