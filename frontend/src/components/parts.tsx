import type { ReactNode } from 'react';
import { Icon, CropArt } from './Icon';
import { useApp } from '../app/state';
import { useVoiceCtx } from '../app/voiceContext';
import { cropView, type PlantArt } from '../domain/catalogue';
import { PLANT, SEASON_KIND, UI } from '../i18n/strings';
import { MONTHS, num, parseIso, type Bi, type Locale } from '../i18n/format';
import { daysIn, iso, monthIsPast, monthsOf, type SeasonSlot } from '../domain/seasons';

/** Arabic year ranges read right-to-left: each year is its own isolate, earlier year on the right. */
export function SeasonYears({ slot, short, locale }: { slot: SeasonSlot; short?: boolean; locale: Locale }) {
  const y = (n: number) => num(short ? String(n).slice(2) : n, locale);
  if (slot.kind === 'summer') return <bdi>{y(slot.startYear)}</bdi>;
  if (locale === 'en') return <bdi>{`${slot.startYear}/${String(slot.startYear + 1).slice(2)}`}</bdi>;
  return <span className="yr-range"><bdi>{y(slot.startYear)}</bdi>/<bdi>{y(slot.startYear + 1)}</bdi></span>;
}

export function SeasonName({ slot }: { slot: SeasonSlot }) {
  const { state, t } = useApp();
  return <>{t(SEASON_KIND[slot.kind])} <SeasonYears slot={slot} locale={state.locale} /></>;
}

export function DateText({ value, noYear, short }: { value: string; noYear?: boolean; short?: boolean }) {
  const { state } = useApp();
  const { y, m, d } = parseIso(value);
  const L = state.locale;
  const mo = short && L === 'en' ? MONTHS.en[m - 1].slice(0, 3) : MONTHS[L][m - 1];
  return <bdi>{noYear ? `${num(d, L)} ${mo}` : `${num(d, L)} ${mo} ${num(y, L)}`}</bdi>;
}

export const plantOf = (cropId: string | null): PlantArt => (cropId && cropId !== 'unknown' ? cropView(cropId).plant : 'unknown');

export interface StripItem { cropId: string | null; date?: string | null; kind?: 'end' | 'start'; mark?: 'lock' | 'reject' | 'review' | 'done' | 'change'; cls?: string; current?: boolean; note?: string }
const MARK_ICON = { lock: 'lock', reject: 'reject', review: 'review', done: 'check', change: 'edit' } as const;

/** The four seasons as arched mini cards. With onPick, each card is a button. */
export function SeasonStrip({ items, onPick, inline, compact }: { items: StripItem[]; onPick?: (i: number) => void; inline?: boolean; compact?: boolean }) {
  const { state, t } = useApp();
  const L = state.locale;
  return (
    <ol className={`strip ${inline ? 'in' : ''} ${compact ? 'compact' : ''}`} aria-label={L === 'ar' ? 'المواسم الأربعة' : 'The four seasons'}>
      {items.map((it, i) => {
        const slot = state.slots[i];
        const plant = plantOf(it.cropId);
        const name = it.cropId && it.cropId !== 'unknown' ? t(PLANT[plant]) : t({ ar: 'لسه', en: 'Not yet' });
        const inner = (
          <>
            <span className="s-season"><Icon name={slot.kind === 'summer' ? 'sun' : 'winter'} /><span>{t(SEASON_KIND[slot.kind])}</span><span className="s-sy"><SeasonYears slot={slot} short locale={L} /></span></span>
            <span className="s-art"><CropArt plant={plant} />{it.mark && <span className={`s-mark ${it.mark}`}><Icon name={MARK_ICON[it.mark]} /></span>}</span>
            <span className="s-name">{name}</span>
            {it.date ? (
              <span className="s-when"><Icon name={it.kind === 'end' ? 'cut' : 'sow'} /><span className="s-date"><DateText value={it.date} noYear short /></span></span>
            ) : <span className="s-when muted">{it.note ?? '\u00a0'}</span>}
          </>
        );
        return (
          <li key={slot.id} className={`${it.cropId && it.cropId !== 'unknown' ? '' : 'empty'} ${it.cls ?? ''}`}>
            {onPick ? (
              <button className="s-card" aria-current={it.current ? 'step' : undefined} onClick={() => onPick(i)}>{inner}</button>
            ) : <div className="s-card">{inner}</div>}
          </li>
        );
      })}
    </ol>
  );
}

export function Banner({ kind, icon, children }: { kind: 'rejected' | 'review' | 'unknown' | 'protected' | 'feasible' | 'saved'; icon: string; children: ReactNode }) {
  return <div className={`banner ${kind}`}><Icon name={icon} /><span>{children}</span></div>;
}

export function Hero({ icon, sub, unknown, title, text, children }: { icon: string; sub?: string; unknown?: boolean; title: string; text?: string; children?: ReactNode }) {
  return (
    <div className={`hero ${unknown ? 'unknown' : ''}`}>
      {children ?? <span className="hero-ic"><Icon name={icon} />{sub && <span className="sub-ic"><Icon name={sub} /></span>}</span>}
      <h2>{title}</h2>{text && <p>{text}</p>}
    </div>
  );
}

/** Picture tile with its own listen button (never nested in the answer button). */
export function Tile({ label, art, pressed, badge, onClick }: { label: string; art: ReactNode; pressed?: boolean; badge?: string; onClick: () => void }) {
  const voice = useVoiceCtx();
  const { t } = useApp();
  return (
    <div className="tile-wrap">
      <button className="tile" aria-pressed={!!pressed} onClick={onClick}><span className="art">{art}</span>{label}{badge && <span className="badge review tile-badge">{badge}</span>}</button>
      <button className="hear" aria-label={`${t(UI.listen)}: ${label}`} onClick={() => voice.speak({ ar: label, en: label })}><Icon name="speaker" /></button>
    </div>
  );
}

/** Month grid limited to the season (each month carries its year), then a day grid. Past dates disabled unless allowPast. */
export function DatePicker({ slot, today, allowPast, until, ym, onMonth, onDay }: {
  slot: SeasonSlot; today: string; allowPast?: boolean; until?: string; ym?: { y: number; m: number };
  onMonth: (ym: { y: number; m: number }) => void; onDay: (isoDate: string) => void;
}) {
  const { state } = useApp();
  const L = state.locale;
  if (!ym) {
    const months = monthsOf(slot).filter((w) => !until || iso(w.y, w.m, 1) <= until);
    return (
      <div className="dense-grid months win">
        {months.map((w) => (
          <button key={`${w.y}-${w.m}`} disabled={!allowPast && monthIsPast(w, today)} onClick={() => onMonth(w)}>
            {MONTHS[L][w.m - 1]}<small>{num(w.y, L)}</small>
          </button>
        ))}
      </div>
    );
  }
  return (
    <div className="dense-grid days">
      {Array.from({ length: daysIn(ym.y, ym.m) }, (_, k) => {
        const d = iso(ym.y, ym.m, k + 1);
        return <button key={d} disabled={(!allowPast && d < today) || (!!until && d > until)} onClick={() => onDay(d)}>{num(k + 1, L)}</button>;
      })}
    </div>
  );
}

export function useT() {
  const { t } = useApp();
  return (b: Bi) => t(b);
}
