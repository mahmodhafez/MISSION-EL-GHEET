import { useEffect, useState } from 'react';
import { useApp, snapshotOf } from '../../app/state';
import { Shell } from '../../components/Shell';
import { Icon } from '../../components/Icon';
import { Hero } from '../../components/parts';

/* Past weather (NASA history). The replay service is not connected yet: the screen says so in one line.
 * Never a fake chart or a placeholder value that looks like a result. */
export function Replay() {
  const { state, dispatch, client, t } = useApp();
  const [reason, setReason] = useState<string | null>(null);
  useEffect(() => { client.replay(snapshotOf(state)).then((r) => setReason(r.reason)); }, [client, state]);
  return (
    <Shell prompt={{ ar: 'مقارنة الجو اللي فات مش متاحة دلوقتي.', en: 'The past-weather comparison is not available right now.' }}>
      <Hero icon="sun" sub="unknown" unknown title={t({ ar: 'الجو اللي فات: مش متاح دلوقتي', en: 'Past weather: not available now' })}
        text={reason ? t({ ar: 'الخدمة لسه بتتجهّز', en: 'This service is still being prepared' }) : '…'} />
      <div className="chips-row"><span className="ichip src"><Icon name="archive" />{t({ ar: 'ناسا · سنين فاتت', en: 'NASA · past years' })}</span><span className="ichip no"><Icon name="reject" />{t({ ar: 'مش كمية الري', en: 'Not irrigation' })}</span></div>
      <button className="primary wide-btn" onClick={() => dispatch({ type: 'back' })}><Icon name="check" />{t({ ar: 'كمّل', en: 'Continue' })}</button>
    </Shell>
  );
}
