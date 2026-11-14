import { useApp, type State, type Field } from '../../app/state';
import { useVoiceCtx } from '../../app/voiceContext';
import { Shell } from '../../components/Shell';
import { Icon, CropArt } from '../../components/Icon';
import { DatePicker, Hero, SeasonName, SeasonStrip, Tile, plantOf } from '../../components/parts';
import { asksLastCut, cropView, plantsFrom } from '../../domain/catalogue';
import { iso, monthsOf } from '../../domain/seasons';
import { PLANT, PURPOSE, SEASON_KIND, UI } from '../../i18n/strings';
import { MONTHS, dateText, num, type Bi } from '../../i18n/format';
import type { SeasonEntry, Extraction } from '../../services/plannerClient';

/** Next cursor after the current field is answered (one question per screen). */
export function nextCursor(s: State, seasons: SeasonEntry[], season: number, field: Field): State['cursor'] {
  const e = seasons[season];
  const plant = e.crop_id && e.crop_id !== 'unknown' ? cropView(e.crop_id).plant : null;
  const options = plant ? plantsFrom(s.cropIds).find((p) => p.plant === plant)?.options ?? [] : [];
  const step = (f: Field): Field | 'next' => {
    switch (f) {
      case 'crop': return e.crop_id === 'unknown' ? 'next' : options.length > 1 && !e.purpose ? 'purpose' : 'month';
      case 'purpose': return 'month';
      case 'month': return 'day';
      case 'day': return asksLastCut(e.crop_id) && !e.sowing_date ? 'sownMonth' : 'next';
      case 'sownMonth': return e.sowing_date === 'unknown' ? 'next' : 'sownDay';
      default: return 'next';
    }
  };
  const f = step(field);
  if (f !== 'next') return { season, field: f };
  for (let i = season + 1; i < 4; i++) if (!seasons[i].crop_id) return { season: i, field: 'crop' };
  return { season: 4, field: 'done' };
}

export function Intake() {
  const { state, dispatch, client, t } = useApp();
  const voice = useVoiceCtx();
  const L = state.locale;
  const { season: i, field, ym } = state.cursor;
  const slot = state.slots[Math.min(i, 3)];
  const entry = state.seasons[Math.min(i, 3)];
  const plants = plantsFrom(state.cropIds);
  // More than 4 crops: show them all at once (row tiles on phone, 4×2 on desktop) instead of paging.
  const many = plants.length > 4;
  const endDate = asksLastCut(entry.crop_id);

  const answer = (patch: Partial<SeasonEntry>, after: Field, heardChips?: Bi[]) => {
    const seasons = state.seasons.map((x, k) => (k === i ? { ...x, ...patch } : x));
    dispatch({ type: 'season', index: i, patch, cursor: nextCursor(state, seasons, i, after) });
    dispatch({ type: 'set', patch: { clarify: false, msg: null, heard: heardChips ? { chips: heardChips, undo: state.seasons } : null } });
  };
  const pickCrop = (cropId: string, chips?: Bi[]) => {
    const v = cropView(cropId);
    const opts = plants.find((p) => p.plant === v.plant)?.options ?? [];
    answer({ crop_id: cropId, purpose: opts.length === 1 ? opts[0].purpose : null, sowing_date: null, last_cut_date: null }, 'crop', chips);
  };
  const pickPlant = (plant: string) => {
    const opts = plants.find((p) => p.plant === plant)?.options ?? [];
    if (opts.length) pickCrop(opts[0].crop_id);
  };

  /* Voice: Gemini-shaped extraction → proposals. Year comes from the season; always read back with year. */
  const onTranscript = async (text: string) => {
    const r = await client.interpret({ question_id: `s${i + 1}_${field}`, locale: L, transcript: text, season_order: i + 1 });
    voice.settle();
    if (r.status !== 'ok') return voice.notUnderstood();
    const ex: Extraction = r.extraction;
    if (ex.off_topic) return voice.speak({ ar: 'مقدرش أنصح بمحصول من عندي. قولّي إنت هتزرع إيه.', en: 'I cannot recommend a crop myself. Tell me what you will grow.' });
    if (ex.ambiguous.length && field === 'crop') return dispatch({ type: 'set', patch: { clarify: true } });
    const said = ex.seasons.find((s) => s.order === i + 1) ?? ex.seasons[0];
    if (field === 'crop') {
      if (ex.answer.dont_know) return answer({ crop_id: 'unknown' }, 'crop', [PLANT.unknown]);
      if (said?.crop && state.cropIds.includes(said.crop)) { const p = PLANT[cropView(said.crop).plant]; voice.speak(p); return pickCrop(said.crop, [p]); }
      return voice.notUnderstood();
    }
    if ((field === 'sownMonth' || field === 'sownDay') && ex.answer.dont_know) return answer({ sowing_date: 'unknown' }, 'sownMonth', [{ ar: 'مش فاكر', en: "Don't remember" }]);
    const dp = said?.sowing_date ?? said?.last_cut_date;
    if (dp?.month && dp.day) {
      const w = monthsOf(slot).find((x) => x.m === dp.month && (dp.year == null || x.y === dp.year));
      const mo = { ar: MONTHS.ar[dp.month - 1], en: MONTHS.en[dp.month - 1] };
      if (!w) return dispatch({ type: 'set', patch: { msg: { ar: `${mo.ar} مش في الموسم ده. اختار شهر من دول.`, en: `${mo.en} is not in this season. Choose one of these months.` } } });
      const d = iso(w.y, w.m, dp.day);
      const sown = field === 'sownMonth' || field === 'sownDay';
      if (!sown && d < state.today) return dispatch({ type: 'set', patch: { msg: { ar: `${dateText(d, 'ar')} عدّى خلاص. اختار ميعاد جاي.`, en: `${dateText(d, 'en')} has already passed. Choose a date ahead.` } } });
      const chip = { ar: `${endDate && !sown ? 'آخر حشة' : 'زراعة'} ${dateText(d, 'ar')}`, en: `${endDate && !sown ? 'Last cut' : 'Sowing'} ${dateText(d, 'en')}` };
      voice.speak(chip);
      return sown ? answer({ sowing_date: d }, 'sownDay', [chip]) : answer(endDate ? { last_cut_date: d } : { sowing_date: d }, 'day', [chip]);
    }
    voice.notUnderstood();
  };

  const strip = (
    <SeasonStrip
      onPick={(k) => dispatch({ type: 'set', patch: { cursor: { season: k, field: 'crop' }, msg: null, clarify: false } })}
      items={state.seasons.map((x, k) => {
        const date = x.last_cut_date ?? (x.sowing_date && x.sowing_date !== 'unknown' ? x.sowing_date : null);
        return { cropId: x.crop_id, date, kind: x.last_cut_date ? 'end' : 'start', current: field !== 'done' && k === i, mark: x.crop_id && x.crop_id !== 'unknown' && date ? 'done' : undefined, note: x.crop_id === 'unknown' ? t(PLANT.unknown) : undefined };
      })}
    />
  );

  const seasonHero = (
    <div className={`season-hero ${slot.kind === 'winter' ? 'w' : 's'}`}>
      <span className="sh-ic"><Icon name={slot.kind === 'winter' ? 'winter' : 'sun'} /></span>
      <div><span className="sh-n">{t({ ar: 'الموسم', en: 'Season' })} {num(i + 1, L)} {t({ ar: 'من', en: 'of' })} {num(4, L)}</span><strong><SeasonName slot={slot} /></strong></div>
      {entry.crop_id && entry.crop_id !== 'unknown' && field !== 'crop' && <span className="sh-crop"><CropArt plant={plantOf(entry.crop_id)} /></span>}
    </div>
  );
  const q = (b: Bi, note?: React.ReactNode) => (<>{seasonHero}<h2 className="question q-small q-row">{t(b)}{note}</h2>{state.msg && <div className="msg" role="status"><Icon name="calendar" />{t(state.msg)}</div>}</>);
  const plantName = entry.crop_id ? PLANT[plantOf(entry.crop_id)] : PLANT.unknown;
  const dateQ: Bi = endDate ? { ar: 'آخر حشة إمتى؟', en: 'When is the last cut?' } : { ar: `هتزرع ${plantName.def} إمتى؟`, en: `When will you sow the ${plantName.en.toLowerCase()}?` };

  let body: React.ReactNode; let prompt: Bi | null = null;
  if (field === 'done') {
    prompt = { ar: 'تمام، المواسم الأربعة اتملت. اللي بعده: إيه اللي لازم يفضل؟', en: 'Good, all four seasons are filled. Next: what must stay?' };
    body = (<><Hero icon="check" title={t({ ar: 'المواسم الأربعة جاهزة', en: 'All four seasons filled' })} text={t({ ar: 'دوس على أي موسم فوق علشان تغيّره', en: 'Tap any season above to change it' })} />
      <button className="primary wide-btn" onClick={() => dispatch({ type: 'go', route: 'protect' })}><Icon name="lock" />{t({ ar: 'التالي: إيه اللي لازم يفضل؟', en: 'Next: what must stay?' })}</button></>);
  } else if (state.clarify) {
    prompt = { ar: 'تقصد ذرة شامية ولا ذرة رفيعة؟', en: 'Do you mean maize or sorghum?' };
    body = (<>{q({ ar: 'أنهي ذرة؟', en: 'Which one?' })}<div className="tiles two">
      {plants.filter((p) => p.plant === 'maize' || p.plant === 'sorghum').map((p) => <Tile key={p.plant} label={t(PLANT[p.plant])} art={<CropArt plant={p.plant} />} onClick={() => pickPlant(p.plant)} />)}</div></>);
  } else if (field === 'crop') {
    prompt = { ar: `الموسم ${num(i + 1, 'ar')}، ${SEASON_KIND[slot.kind].ar}. هتزرع إيه؟`, en: `Season ${i + 1}, ${SEASON_KIND[slot.kind].en}. What will you grow?` };
    body = (<>{q({ ar: 'هتزرع إيه؟', en: 'What will you grow?' }, state.cropsPending && <span className="badge review q-note" title={t({ ar: 'كل المحاصيل لسه محتاجة مراجعة زراعية', en: 'Every crop still needs agricultural review' })}><Icon name="review" />{t(UI.needsReview)}</span>)}
      <div className={`tiles four ${many ? 'compact' : ''}`}>{plants.map((p) => <Tile key={p.plant} label={t(PLANT[p.plant])} art={<CropArt plant={p.plant} />} pressed={plantOf(entry.crop_id) === p.plant} onClick={() => pickPlant(p.plant)} />)}</div>
      <button className="secondary wide-btn" onClick={() => answer({ crop_id: 'unknown', purpose: null, sowing_date: null, last_cut_date: null }, 'crop')}><Icon name="unknown" />{t(PLANT.unknown)}</button></>);
  } else if (field === 'purpose') {
    const opts = plants.find((p) => p.plant === plantOf(entry.crop_id))?.options ?? [];
    prompt = { ar: `${plantName.def} علشان إيه؟`, en: `What is the ${plantName.en.toLowerCase()} for?` };
    body = (<>{q(prompt)}<div className="tiles two">{opts.map((o) => <Tile key={o.crop_id} label={o.purpose ? t(PURPOSE[o.purpose]) : o.crop_id} art={<Icon name={o.purpose === 'forage' ? 'cow' : 'sack'} />} onClick={() => answer({ crop_id: o.crop_id, purpose: o.purpose }, 'purpose')} />)}</div></>);
  } else if (field === 'month' || field === 'day') {
    prompt = field === 'month' ? dateQ : { ar: 'يوم كام؟', en: 'Which day?' };
    body = (<>{q(field === 'month' ? dateQ : { ar: `يوم كام في ${MONTHS.ar[ym!.m - 1]} ${num(ym!.y, 'ar')}؟`, en: `Which day in ${MONTHS.en[ym!.m - 1]} ${ym!.y}?` })}
      <DatePicker slot={slot} today={state.today} ym={field === 'day' ? ym : undefined}
        onMonth={(w) => dispatch({ type: 'set', patch: { cursor: { season: i, field: 'day', ym: w }, msg: null } })}
        onDay={(d) => answer(endDate ? { last_cut_date: d } : { sowing_date: d }, 'day')} /></>);
  } else {
    // Berseem sowing: the crop is already growing, so past dates are allowed; "don't remember" stays unknown.
    prompt = { ar: 'زرعت البرسيم إمتى؟ لو مش فاكر، قول مش فاكر.', en: 'When did you sow the berseem? If you do not remember, say so.' };
    body = (<>{q({ ar: 'زرعت البرسيم إمتى؟', en: 'When did you sow the berseem?' })}
      <DatePicker slot={slot} today={state.today} allowPast until={entry.last_cut_date ?? undefined} ym={field === 'sownDay' ? ym : undefined}
        onMonth={(w) => dispatch({ type: 'set', patch: { cursor: { season: i, field: 'sownDay', ym: w } } })}
        onDay={(d) => answer({ sowing_date: d }, 'sownDay')} />
      {field === 'sownMonth' && <button className="secondary wide-btn" onClick={() => answer({ sowing_date: 'unknown' }, 'sownMonth')}><Icon name="unknown" />{t({ ar: 'مش فاكر', en: "I don't remember" })}</button>}</>);
  }

  return <Shell top={strip} prompt={prompt} onTranscript={field === 'done' ? undefined : onTranscript}>{body}</Shell>;
}
