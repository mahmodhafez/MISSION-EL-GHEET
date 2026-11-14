import { Icon, CropArt } from '../../components/Icon';
import { plantOf } from '../../components/parts';
import { PLANT } from '../../i18n/strings';
import { dateText, type Bi, type Locale } from '../../i18n/format';
import type { ResearchBlock, ResearchNote, ResearchSource } from '../../services/plannerClient';
import { noteIcon, noteTone, timelineLayout } from './research';

/* "What research says": sourced KB findings rendered by the backend (D4). Advisory only:
   it never uses rejected styling and never changes the plan's status. */

const short = (s: string, n = 60) => (s.length > n ? `${s.slice(0, n - 1).trimEnd()}…` : s);
const D = ({ v, L }: { v: string; L: Locale }) => <bdi>{dateText(v, L, { noYear: true })}</bdi>;

function SourceLine({ where, source }: { where: string; source: ResearchSource }) {
  const label = `${short(source.title)}${source.locator ? ` · ${source.locator}` : ''}`;
  return (
    <p className="rs-src">
      <bdi>{where}</bdi>{' · '}
      {source.url ? <a href={source.url} target="_blank" rel="noopener noreferrer" lang="en" dir="ltr">{label}</a> : <bdi lang="en">{label}</bdi>}
    </p>
  );
}

function Timeline({ n, L, t }: { n: ResearchNote; L: Locale; t: (b: Bi) => string }) {
  if (!n.window) return null;
  const g = timelineLayout(n.window, n.farmer_date);
  return (
    <div className="rs-line" aria-hidden="true">
      <div className="rs-track">
        <span className="rs-band" style={{ insetInlineStart: `${g.bandStart}%`, width: `${g.bandWidth}%` }} />
        {g.marker !== null && <span className="rs-mark" style={{ insetInlineStart: `${g.marker}%` }} />}
      </div>
      <div className="rs-ends">
        <span><D v={n.window.start} L={L} /> – <D v={n.window.end} L={L} /></span>
        {n.farmer_date && <span className="rs-you"><span className="rs-dot" />{t({ ar: 'ميعادك', en: 'your date' })} <D v={n.farmer_date} L={L} /></span>}
      </div>
    </div>
  );
}

function Note({ n, L, t }: { n: ResearchNote; L: Locale; t: (b: Bi) => string }) {
  const tone = noteTone(n);
  return (
    <li className={`rs-note ${tone}`} data-placement={n.placement ?? undefined}>
      <span className="ic"><Icon name={noteIcon(n.kind)} /></span>
      <div className="rs-body">
        <b>{n.title}</b>
        <p>{n.text}</p>
        {n.window && <Timeline n={n} L={L} t={t} />}
        {n.kind === 'trial_dates' && n.dates.length > 0 && (
          <div className="rs-chips">
            {n.dates.map((d) => <span key={d} className="chip"><D v={d} L={L} /></span>)}
            {n.farmer_date && <span className="chip you"><span className="rs-dot" />{t({ ar: 'ميعادك', en: 'your date' })} <D v={n.farmer_date} L={L} /></span>}
          </div>
        )}
        <SourceLine where={n.where} source={n.source} />
      </div>
    </li>
  );
}

export function Research({ block, locale: L, t, onAddCrops }: { block: ResearchBlock; locale: Locale; t: (b: Bi) => string; onAddCrops?: () => void }) {
  const seasons = block.seasons.filter((s) => s.notes.length || s.other.length);
  if (!seasons.length && !block.empty_hint) return null;
  return (
    <section className="research" aria-labelledby="rs-h">
      <h3 id="rs-h">{t({ ar: 'اللي الأبحاث بتقوله', en: 'What research says' })}</h3>
      <p className="rs-caveat"><Icon name="archive" />{block.caveat.text}</p>
      {seasons.map((s) => {
        const plant = plantOf(s.crop_id);
        return (
          <div key={s.season_id} className="rs-season">
            <div className="rs-crop"><span className="portrait-sm"><CropArt plant={plant} /></span><b>{plant !== 'unknown' ? t(PLANT[plant]) : s.crop}</b></div>
            {s.notes.length > 0 && <ul className="rs-notes">{s.notes.map((n) => <Note key={n.rule_id} n={n} L={L} t={t} />)}</ul>}
            {s.other.length > 0 && (
              <details className="rs-more">
                <summary>{t({ ar: 'حاجات تانية من المصادر (بالإنجليزي)', en: 'More from the sources (English)' })}</summary>
                <ul>{s.other.map((o) => (
                  <li key={o.rule_id} lang="en" dir="ltr"><b>{o.label}</b><p>{o.source_text}</p><SourceLine where={o.where} source={o.source} /></li>
                ))}</ul>
              </details>
            )}
          </div>
        );
      })}
      {block.empty_hint && (
        <div className="rs-empty">
          <p>{block.empty_hint.text}</p>
          {onAddCrops && <button className="secondary" onClick={onAddCrops}><Icon name="plus" /><span>{t({ ar: 'زوّد المحاصيل', en: 'Add crops' })}</span></button>}
        </div>
      )}
    </section>
  );
}
