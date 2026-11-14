import { describe, expect, it } from 'vitest';
import INDEX from '../../voice/voice-index.json';
import { planSpeech } from './clips';
import { dateText, num } from '../../i18n/format';
import { PLANT, SEASON_KIND } from '../../i18n/strings';

type Loc = 'ar' | 'en';
const idx = INDEX as unknown as { lines: Record<Loc, { id: string; parts: ({ t: string; key?: string } | { slot: string })[] }[]>; vocab: Record<Loc, Record<string, { show: string; key: string }[]>> };
const allKeys = (l: Loc) => new Set([...idx.lines[l].flatMap((x) => x.parts.flatMap((p) => ('key' in p && p.key ? [p.key] : []))), ...Object.values(idx.vocab[l]).flat().map((w) => w.key)]);
const sample: Record<Loc, Record<string, string>> = {
  ar: { date: '١٥ مايو', num: '٢', days: 'سبع أيام', crop: 'الذرة الشامية', purpose: 'حبوب', season: 'شتوي' },
  en: { date: '15 May', num: '2', days: '7 days', crop: 'maize', purpose: 'grain', season: 'Winter' },
};

describe('recorded voice: every catalogue line can be spoken from clips', () => {
  for (const loc of ['ar', 'en'] as Loc[]) {
    it(`${loc}: each line, filled with sample words, resolves to recorded pieces and words`, () => {
      const keys = allKeys(loc);
      for (const line of idx.lines[loc]) {
        const text = line.parts.map((p) => ('slot' in p ? sample[loc][p.slot] : p.t)).join('');
        const plan = planSpeech(text, loc);
        expect(plan, `${line.id}: ${text}`).not.toBeNull();
        expect(plan!.keys.length).toBeGreaterThan(0);
        for (const k of plan!.keys) expect(keys.has(k), `${line.id} key ${k}`).toBe(true);
      }
    });
  }
});

describe('recorded voice: real sentences the app produces', () => {
  it('backend UH-001 speech (spoken numbers, both languages)', () => {
    expect(planSpeech('زراعة الذرة الشامية يوم خمستاشر مايو قبل حشة البرسيم اللي ثبّتها يوم عشرين مايو. الحشة هتفضل.', 'ar')?.id).toBe('api.sowing_before_protected_cut');
    expect(planSpeech('الأرض تفضى يوم واحد وعشرين مايو. بعد سبع أيام تجهيز، أقرب ميعاد تمانية وعشرين مايو. ده عدّ أيام بس، ومحتاج مراجعة زراعية.', 'ar')?.id).toBe('api.preparation_shortfall');
    expect(planSpeech('لو الذرة الشامية تمانية وعشرين مايو: اللي عليه قفل بيفضل. ميعاد الحصاد يبقى مش معروف، فمحتاج مراجعة زراعية.', 'ar')?.id).toBe('api.investigation');
    expect(planSpeech('الذرة الشامية في الموسم أربعة: ماتشيّكش، مفيش بيانات كفاية.', 'ar')?.id).toBe('api.profile_binding_unavailable');
    expect(planSpeech('Sowing the maize on May fifteen comes before the berseem cut you kept on May twenty. The cut stays.', 'en')?.id).toBe('api.sowing_before_protected_cut');
    expect(planSpeech('The field is free on May twenty-one. After seven days of preparation, the earliest date is May twenty-eight. That is only day counting and needs agricultural review.', 'en')?.id).toBe('api.preparation_shortfall');
  });

  it('a date is played as day + month (+ year) words', () => {
    const p = planSpeech(`آخر حشة ${dateText('2027-05-20', 'ar')}`, 'ar')!;
    const say = (k: string) => Object.values(idx.vocab.ar).flat().find((w) => w.key === k);
    expect(p.id).toBe('intake.heard_cut');
    expect(p.keys.slice(1).map((k) => (say(k) as { say?: string } | undefined)?.say)).toEqual(['عشرين', 'مايو', 'ألفين سبعة وعشرين']);
  });

  it('screen prompts built the way the screens build them', () => {
    expect(planSpeech(`الموسم ${num(3, 'ar')}، ${SEASON_KIND.winter.ar}. هتزرع إيه؟`, 'ar')?.id).toBe('intake.crop_q');
    expect(planSpeech(`When will you sow the ${PLANT.cotton.en.toLowerCase()}?`, 'en')?.id).toBe('intake.sow_q');
    const dates = ['2027-05-28', '2027-06-01'].map((d) => dateText(d, 'ar', { noYear: true })).join(' و ');
    expect(planSpeech(`مفيش بديل أكيد لسه. فيه ${num(2, 'ar')} ميعاد نراجعهم: ${dates}.`, 'ar')?.id).toBe('options.none_two_dates');
    expect(planSpeech(`${PLANT.wheat.ar}: ثابت.`, 'ar')?.id).toBe('protect.kept');
  });

  it('anything not in the catalogue falls back (null), including unknown words in a slot', () => {
    expect(planSpeech('Some sentence nobody recorded.', 'en')).toBeNull();
    expect(planSpeech('هتزرع الموز إمتى؟', 'ar')).toBeNull();
  });
});
