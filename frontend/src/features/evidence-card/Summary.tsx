import { useState } from 'react';
import { useApp, snapshotOf } from '../../app/state';
import { useVoiceCtx } from '../../app/voiceContext';
import { Shell } from '../../components/Shell';
import { Icon } from '../../components/Icon';
import { Banner, SeasonStrip, plantOf } from '../../components/parts';
import { PLANT } from '../../i18n/strings';
import { dateText, type Bi } from '../../i18n/format';
import { conflictPair, conflictSeasons } from '../promise-test/explain';
import type { SaveResponse } from '../../services/plannerClient';

/* Calm summary: the four crops, the one problem, one Save. Plan status and save status stay separate:
 * a saved plan keeps its problem. "Saved" only after the server confirms (handoff). */
export function Summary() {
  const { state, dispatch, client, t } = useApp();
  const voice = useVoiceCtx();
  const [save, setSave] = useState<'idle' | 'saving' | SaveResponse>('idle');
  const cur = state.plan?.status === 'ok' ? state.plan.result.current : null;
  const bad = cur ? conflictSeasons(cur) : new Set<string>();
  const pair = cur ? conflictPair(cur) : null;
  const sow = pair ? state.seasons.find((s) => s.season_id === pair.sowSeason) : null;
  const problem: Bi | null = cur?.status === 'rejected'
    ? sow ? { ar: `مشكلة واحدة: ميعاد ${PLANT[plantOf(sow.crop_id)].def}`, en: `One problem: the ${PLANT[plantOf(sow.crop_id)].en.toLowerCase()} date` } : { ar: 'الخطة فيها تعارض', en: 'The plan has a conflict' }
    : cur?.status === 'needs_review' ? { ar: 'محتاج مراجعة زراعية', en: 'Needs agricultural review' } : null;
  const takeaway: Bi = pair && sow
    ? { ar: `حشة يوم ${dateText(pair.cutDate, 'ar', { noYear: true })} ثابتة في الخطة. ميعاد ${PLANT[plantOf(sow.crop_id)].def} الحالي متعارض معاها. مفيش بديل أكيد لسه. هنحفظ خطتك والنقط اللي محتاجة مراجعة.`,
        en: `The cut on ${dateText(pair.cutDate, 'en', { noYear: true })} is kept in the plan. The current ${PLANT[plantOf(sow.crop_id)].en.toLowerCase()} date conflicts with it. There is no sure alternative yet. We will save your plan and the points that need review.` }
    : { ar: 'ده ملخص خطتك.', en: 'This is your plan summary.' };
  const serverTakeaway = state.plan?.status === 'ok' ? state.plan.rendered?.takeaway : null;
  const spokenTakeaway: Bi = serverTakeaway ? { ar: serverTakeaway.speech, en: serverTakeaway.speech } : takeaway;
  const doSave = async () => { voice.stop(); setSave('saving'); setSave(await client.saveEvidence(snapshotOf(state))); };
  const items = state.seasons.map((s) => ({ cropId: s.crop_id, date: s.last_cut_date ?? (s.sowing_date !== 'unknown' ? s.sowing_date : null), kind: (s.last_cut_date ? 'end' : 'start') as 'end' | 'start', mark: bad.has(s.season_id) ? ('reject' as const) : undefined, cls: bad.has(s.season_id) ? 'reject' : '' }));
  return (
    <Shell prompt={{ ar: `ده ملخص خطتك. تحب نحفظها للمراجعة؟ الحفظ مش معناه موافقة.`, en: 'This is your plan summary. Save it for review? Saving does not mean approval.' }}>
      <div className="calm">
        <div className="alt-head"><h2 className="question" style={{ fontSize: 24 }}>{t({ ar: 'ملخص خطتك', en: 'Your plan' })}</h2>
          <button className="hear" aria-label={t({ ar: 'اسمع الملخص', en: 'Hear the summary' })} onClick={() => voice.speak(spokenTakeaway)}><Icon name="speaker" /></button></div>
        <SeasonStrip inline compact items={items} />
        {problem && <Banner kind={cur?.status === 'rejected' ? 'rejected' : 'review'} icon={cur?.status === 'rejected' ? 'reject' : 'review'}>{t(problem)}</Banner>}
        <div className="calm-end">
          <div className="two-btns">
            <button className="secondary" onClick={() => dispatch({ type: 'go', route: 'replay' })}><Icon name="sun" />{t({ ar: 'الجو اللي فات', en: 'Past weather' })}</button>
            <button className="secondary" onClick={() => dispatch({ type: 'go', route: 'forecast' })}><Icon name="future" />{t({ ar: 'الأسبوع الجاي', en: 'Next week' })}</button>
          </div>
          {save === 'idle' && <button className="primary wide-btn" onClick={doSave}><Icon name="save" />{t({ ar: 'احفظ للمراجعة', en: 'Save for review' })}</button>}
          {save === 'saving' && <button className="primary wide-btn" disabled><Icon name="save" />{t({ ar: 'بيتحفظ…', en: 'Saving…' })}</button>}
          {typeof save === 'object' && save.status === 'saved' && <Banner kind="saved" icon="check">{t({ ar: 'اتحفظت للمراجعة', en: 'Saved for review' })}</Banner>}
          {typeof save === 'object' && save.status === 'unavailable' && (<>
            <Banner kind="unknown" icon="reject">{t({ ar: 'ماتحفظتش', en: 'Not saved' })}<small>{save.reason === 'server_not_connected' ? t({ ar: 'الحفظ محتاج السيرفر · إجاباتك لسه هنا', en: 'Saving needs the server · your answers are still here' }) : save.reason}</small></Banner>
            <button className="primary wide-btn" onClick={doSave}><Icon name="repeat" />{t({ ar: 'جرّب تاني', en: 'Try again' })}</button></>)}
        </div>
      </div>
    </Shell>
  );
}
