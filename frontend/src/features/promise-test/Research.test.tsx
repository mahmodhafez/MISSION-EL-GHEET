import { afterEach, describe, expect, it, vi } from 'vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { Research } from './Research';
import { timelineLayout } from './research';
import type { ResearchBlock, ResearchSource } from '../../services/plannerClient';
import type { Bi, Locale } from '../../i18n/format';

afterEach(cleanup);

const src: ResearchSource = { source_id: 'SRC_8bbfb83d46a7befb', title: 'Crop calendar for the Nile Delta', url: 'https://example.org/calendar', version: '1', locator: 'Table 1, Nile Delta, Wheat' };
const rd = (code: string, text: string) => ({ code, version: 1, text, speech: text });

/* The contract example: wheat sown 12 Dec in s1, s2–s4 empty. ar-EG uses the same structure with Arabic text. */
function block(ar: boolean): ResearchBlock {
  return {
    caveat: rd('research.caveat', ar ? 'من أبحاث منشورة. لسه ماتراجعتش لسخا. مش بتغيّر حالة خطتك.' : "From published research. Not yet reviewed for Sakha. It does not change your plan's status."),
    seasons: [{
      season_id: 's1', crop_id: 'wheat', crop: ar ? 'القمح' : 'the wheat',
      notes: [
        { rule_id: 'C01', kind: 'sowing_window', title: ar ? 'ميعاد الزراعة' : 'Sowing date',
          text: ar ? 'تقويم الدلتا: القمح يتزرع من ١٠ لـ ٣٠ نوفمبر.' : 'Nile Delta calendar: sow wheat 10–30 November. Your date, 12 December, is 12 days after it.', speech: '',
          window: { start: '2026-11-10', end: '2026-11-30' }, farmer_date: '2026-12-12', placement: 'after', days_outside: 12, dates: [], where: ar ? 'الدلتا' : 'Nile Delta', source: src },
        { rule_id: 'C03', kind: 'trial_dates', title: ar ? 'اتجرّب في سخا' : 'Tested at Sakha', text: 'A trial at Sakha sowed wheat on 5 November, 5 December and 5 January.', speech: '',
          window: null, farmer_date: '2026-12-12', placement: null, days_outside: null, dates: ['2026-11-05', '2026-12-05', '2027-01-05'], where: 'Sakha', source: src },
        { rule_id: 'C02', kind: 'maturity_window', title: ar ? 'الحصاد' : 'Harvest', text: 'Nile Delta calendar: wheat matures 15 April – 10 May.', speech: '',
          window: { start: '2027-04-15', end: '2027-05-10' }, farmer_date: null, placement: null, days_outside: null, dates: [], where: 'Nile Delta', source: src },
      ],
      other: [{ rule_id: 'C05', label: 'Local crop-coefficient evidence', source_text: 'Initial 0.43–0.68', where: 'Sakha Research Station', source: src }],
    }],
    empty_seasons: ['s2', 's3', 's4'],
    empty_hint: rd('research.empty_seasons', ar ? 'زوّد محاصيل المواسم الجاية.' : 'Add the crops for your next seasons so we can check how they fit together.'),
  };
}
const tOf = (L: Locale) => (b: Bi) => b[L];

describe('Research', () => {
  it('en: titles, texts, source link, after-placement in review tone (never rejected)', () => {
    const add = vi.fn();
    const { container } = render(<Research block={block(false)} locale="en" t={tOf('en')} onAddCrops={add} />);
    expect(screen.getByText('What research says')).toBeTruthy();
    expect(screen.getByText(/Not yet reviewed for Sakha/)).toBeTruthy();
    expect(screen.getByText('Sowing date')).toBeTruthy();
    expect(screen.getByText(/is 12 days after it/)).toBeTruthy();
    const sow = container.querySelector('[data-placement="after"]')!;
    expect(sow.className).toContain('review');
    expect(container.querySelector('.reject, .rejected')).toBeNull();
    expect(sow.querySelector('.rs-mark')).toBeTruthy();
    const a = sow.querySelector('a')!;
    expect(a.getAttribute('href')).toBe('https://example.org/calendar');
    expect(a.getAttribute('target')).toBe('_blank');
    expect(a.textContent).toContain('Table 1, Nile Delta, Wheat');
    expect(container.querySelectorAll('.rs-chips .chip').length).toBe(4); // 3 trial dates + farmer's date
    expect((container.querySelector('details.rs-more') as HTMLDetailsElement).open).toBe(false);
    fireEvent.click(screen.getByText('Add crops'));
    expect(add).toHaveBeenCalled();
  });

  it('ar-EG: Arabic headings and backend text, Arabic digits in dates', () => {
    render(<Research block={block(true)} locale="ar" t={tOf('ar')} />);
    expect(screen.getByText('اللي الأبحاث بتقوله')).toBeTruthy();
    expect(screen.getByText('ميعاد الزراعة')).toBeTruthy();
    expect(screen.getByText('قمح')).toBeTruthy();
    expect(screen.getAllByText('١٢ ديسمبر').length).toBeGreaterThan(0);
  });
});

describe('timelineLayout', () => {
  it('puts a date after the window to the inline-end of the band', () => {
    const g = timelineLayout({ start: '2026-11-10', end: '2026-11-30' }, '2026-12-12');
    expect(g.bandStart).toBeGreaterThan(0);
    expect(g.marker!).toBeGreaterThan(g.bandStart + g.bandWidth);
    expect(g.marker!).toBeLessThan(100);
  });
  it('keeps an inside date within the band, and no marker without a date', () => {
    const g = timelineLayout({ start: '2026-11-10', end: '2026-11-30' }, '2026-11-20');
    expect(g.marker!).toBeGreaterThanOrEqual(g.bandStart);
    expect(g.marker!).toBeLessThanOrEqual(g.bandStart + g.bandWidth);
    expect(timelineLayout({ start: '2027-04-15', end: '2027-05-10' }, null).marker).toBeNull();
  });
});
