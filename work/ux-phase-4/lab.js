/* UX Phase 4 voice-first labs: shared engine.
 * Each lab page calls Lab.page({...}). Everything here is a simulation for design review:
 * no live recognition, planning, forecasting or saving. Real browser TTS is opt-in and labelled. */
(function(){
'use strict';

const LABS=[
  ['lab-00-voice.html','00','Voice controller & states'],
  ['lab-01-welcome.html','01','Welcome & first use'],
  ['lab-02-seasons.html','02','Choose crops per season'],
  ['lab-03-confirm.html','03','Readback & protect'],
  ['lab-04-check.html','04','Promise Test result'],
  ['lab-05-options.html','05','Alternatives & investigations'],
  ['lab-06-replay.html','06','Past weather (Season Replay)'],
  ['lab-07-outlook.html','07','Next 7 days (outlook)'],
  ['lab-08-card.html','08','Save & takeaway (Evidence Card)']
];

/* ---------- text helpers ---------- */
const AR_DIGITS='٠١٢٣٤٥٦٧٨٩';
const MONTHS={ar:['يناير','فبراير','مارس','أبريل','مايو','يونيو','يوليو','أغسطس','سبتمبر','أكتوبر','نوفمبر','ديسمبر'],
  en:['January','February','March','April','May','June','July','August','September','October','November','December']};
function num(n,loc){const s=String(n);return loc==='ar'?s.replace(/[0-9]/g,d=>AR_DIGITS[d]):s;}
function date(iso,loc,opts){
  if(!iso)return loc==='ar'?'مش معروف':'unknown';
  const [y,m,d]=iso.split('-').map(Number);const mo=MONTHS[loc][m-1];
  const txt=opts&&opts.noYear?`${num(d,loc)} ${mo}`:`${num(d,loc)} ${mo} ${num(y,loc)}`;
  return `<bdi>${txt}</bdi>`;
}
function plain(html){return String(html).replace(/<[^>]+>/g,'');}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}

/* ---------- icons (outline, 36 grid; first nine reused from ux-phase-3) ---------- */
const ICON={
  speaker:'<path d="M4 13h6l9-7v24l-9-7H4zM24 11q9 7 0 14M28 6q13 12 0 24"/>',
  mic:'<rect x="13" y="3" width="10" height="20" rx="5"/><path d="M8 17v3a10 10 0 0 0 20 0v-3M18 30v5M12 35h12"/>',
  micoff:'<rect x="13" y="3" width="10" height="20" rx="5"/><path d="M8 17v3a10 10 0 0 0 20 0v-3M18 30v5M12 35h12M4 4l28 28"/>',
  lock:'<rect x="7" y="15" width="22" height="18" rx="3"/><path d="M12 15V9a6 6 0 0 1 12 0v6M18 23v4"/>',
  review:'<path d="M18 4 34 32H2zM18 13v9M18 27v1"/>',
  reject:'<circle cx="18" cy="18" r="15"/><path d="m12 12 12 12M24 12 12 24"/>',
  archive:'<path d="M4 8h28v7H4zM7 15v17h22V15M13 22h10M10 3h16"/>',
  future:'<path d="M5 26h24a5 5 0 0 0 0-10 10 10 0 0 0-19-3 7 7 0 0 0-5 13M10 32h1m6 0h1m6 0h1"/>',
  plan:'<path d="M8 4h22v29H8zM3 10h10M3 19h10M3 28h10M18 12h6M18 21h6"/>',
  check:'<path d="m6 18 8 8L31 8"/>',
  stop:'<rect x="9" y="9" width="18" height="18" rx="2"/>',
  repeat:'<path d="M28 14a11 11 0 1 0 1 9M29 5v9h-9"/>',
  back:'<path d="M22 6 10 18l12 12"/>',
  help:'<circle cx="18" cy="18" r="15"/><path d="M14 14a4 4 0 1 1 6 3.5c-1.5.8-2 1.8-2 3.5M18 26v1"/>',
  edit:'<path d="M6 30l2-8L24 6l6 6-16 16zM21 9l6 6"/>',
  unknown:'<circle cx="18" cy="18" r="15" stroke-dasharray="4 3"/><path d="M14 14a4 4 0 1 1 6 3.5c-1.5.8-2 1.8-2 3.5M18 26v1"/>',
  save:'<path d="M6 4h20l5 5v23H6zM11 4v9h13V4M11 32V21h14v11"/>',
  globe:'<circle cx="18" cy="18" r="15"/><path d="M3 18h30M18 3c-6 8-6 22 0 30M18 3c6 8 6 22 0 30"/>',
  feasible:'<circle cx="18" cy="18" r="15"/><path d="m11 18 5 5 9-10"/>',
  play:'<path d="M10 6v24l20-12z"/>'
};
function icon(name,cls){return `<svg class="${cls||''}" viewBox="0 0 36 36" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">${ICON[name]||ICON.plan}</svg>`;}

/* ---------- crop drawings: original placeholders, NOT recognition-tested ---------- */
const CROP_ART={
  berseem:'<path d="M55 112V58M55 78q-18-6-22-24M55 70q16-4 20-22"/><circle cx="33" cy="44" r="9"/><circle cx="25" cy="54" r="8"/><circle cx="41" cy="55" r="8"/><circle cx="75" cy="40" r="9"/><circle cx="67" cy="50" r="8"/><circle cx="83" cy="51" r="8"/><path d="M55 58q-6-14 0-26q6 12 0 26"/><circle cx="55" cy="26" r="6"/>',
  maize:'<path d="M55 114V12M55 40q-30-6-36 22M55 66q30-6 38 18M55 88q-24-2-30 18"/><path d="M62 52q12-6 12-22t-8-16q-10 4-10 22"/><path d="M60 26h12M59 34h14M60 42h12M55 12l-6-8M55 12l6-8"/>',
  wheat:'<path d="M55 114V20M55 90q-20-10-28-34M55 96q20-10 26-30"/><path d="M55 20q-8 4-8 10t8 6q8 0 8-6t-8-10M55 36q-9 3-9 9t9 6q9 0 9-6t-9-9M55 52q-9 3-9 9t9 6q9 0 9-6t-9-9"/><path d="M55 20V6M47 26l-6-10M63 26l6-10"/>',
  sorghum:'<path d="M55 114V34M55 70q-26-6-32 18M55 84q26-4 32 20M55 52q20-6 26 10"/><path d="M55 34q-14-4-16-18q10-6 16 4q6-10 16-4q-2 14-16 18"/><circle cx="46" cy="18" r="3"/><circle cx="55" cy="12" r="3"/><circle cx="64" cy="18" r="3"/><circle cx="50" cy="26" r="3"/><circle cx="60" cy="26" r="3"/>',
  fallow:'<path d="M10 100h90M20 92h70M30 84h50"/><path d="M40 84q4-8 8 0M62 84q4-8 8 0"/>',
  unknown:'<circle cx="55" cy="60" r="34" stroke-dasharray="6 5"/><path d="M45 50a10 10 0 1 1 15 8c-3 2-5 4-5 8M55 76v2"/>'
};
function crop(name){return `<svg viewBox="0 0 110 120" aria-hidden="true" fill="none" stroke="#476344" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round">${CROP_ART[name]||CROP_ART.unknown}</svg>`;}

const CROPS={
  berseem:{ar:'برسيم',en:'Berseem'},
  maize:{ar:'ذرة',en:'Maize'},
  wheat:{ar:'قمح',en:'Wheat'},
  sorghum:{ar:'ذرة رفيعة',en:'Sorghum'},
  fallow:{ar:'الأرض فاضية',en:'Leave empty'},
  unknown:{ar:'لسه مش عارف',en:"I don't know yet"}
};
const PURPOSE={forage:{ar:'علف للمواشي',en:'animal feed'},grain:{ar:'حبوب',en:'grain'}};
// Year ranges are isolated LTR so Arabic-Indic digits around "/" are never visually reversed (design §5).
const SEASONS=[
  {ar:'شتوي <bdi dir="ltr">٢٠٢٦/٢٠٢٧</bdi>',en:'Winter 2026/27'},{ar:'صيفي <bdi>٢٠٢٧</bdi>',en:'Summer 2027'},
  {ar:'شتوي <bdi dir="ltr">٢٠٢٧/٢٠٢٨</bdi>',en:'Winter 2027/28'},{ar:'صيفي <bdi>٢٠٢٨</bdi>',en:'Summer 2028'}
];

/* ---------- voice dock wording (Arabic is a draft for native review) ---------- */
const VOICE_TEXT={
  idle:{ar:['دوس على الميكروفون واتكلّم','أو اختار من الصور'],en:['Tap the mic and talk','or tap a picture']},
  speaking:{ar:['بتكلّم دلوقتي…','دوس الميكروفون لو عايز ترد على طول'],en:['Speaking…','Tap the mic to answer now']},
  listening:{ar:['سامعك… اتكلّم','دوس تاني لما تخلّص'],en:['Listening… go ahead','Tap again when you finish']},
  processing:{ar:['بفهم كلامك…',''],en:['Working out what you said…','']},
  nospeech:{ar:['ماسمعتش حاجة','دوس الميكروفون تاني، أو اختار صورة'],en:["I didn't hear anything",'Tap the mic again, or tap a picture']},
  notunderstood:{ar:['مافهمتش كويس','قولها تاني بطريقة تانية، أو اختار صورة'],en:["I didn't catch that",'Say it another way, or tap a picture']},
  denied:{ar:['الميكروفون مقفول','تقدر تختار بالصور، وأنا هفضل أقرا بصوت عالي'],en:['Microphone is off','You can tap the pictures; I will keep reading aloud']},
  asking:{ar:['الموبايل هيسألك تسمح بالميكروفون','الصوت بيتبعت علشان يتفهم'],en:['Your phone will ask to use the microphone','Your voice is sent to be understood']},
  audiooff:{ar:['الصوت مش شغال','الصور والكلام المكتوب لسه موجودين'],en:['Sound is not working','Pictures and text are still here']},
  fallback:{ar:['خلّينا نختار بالصور','الميكروفون لسه موجود لو حبيت تجرّب تاني'],en:["Let's use the pictures",'The mic is still here if you want to try again']}
};
const UI={
  back:{ar:'رجوع',en:'Back'},help:{ar:'مساعدة',en:'Help'},repeat:{ar:'تاني',en:'Repeat'},stop:{ar:'وقّف',en:'Stop'},
  lang:{ar:'English',en:'العربية'},listen:{ar:'اسمع',en:'Listen'},
  says:{ar:'التطبيق بيقول',en:'The app says'},
  heardQ:{ar:'أنا فهمت كده — صح؟',en:'This is what I understood. Is it right?'},
  yes:{ar:'أيوه، صح',en:'Yes, that is right'},change:{ar:'غيّر',en:'Change'},
  sim:{ar:'مثال تجريبي — مش بيانات حقيقية',en:'Practice example, not real data'}
};

/* ---------- engine ---------- */
function page(def){
  const ctx={locale:'ar',state:def.states[0].id,voice:'idle',heard:null,data:JSON.parse(JSON.stringify(def.data||{})),
    audioStarted:false,micDenied:false,audioOff:false,realTTS:false,autoPlay:true,phone:false,log:[]};
  ctx.t=o=>o==null?'':(typeof o==='string'?o:(o[ctx.locale]??o.en));
  ctx.date=(iso,o)=>date(iso,ctx.locale,o);ctx.num=n=>num(n,ctx.locale);
  ctx.misses=0;ctx.lastHeard=null;
  ctx.go=id=>{stopAudio();ctx.state=id;ctx.heard=null;ctx.lastHeard=null;ctx.misses=0;ctx.voice=ctx.micDenied?'denied':'idle';
    if(def.onShow)def.onShow(ctx);render();if(!def.quiet||!def.quiet(ctx))autoSpeak();};
  /* Implicit confirmation: apply a single heard answer as a proposal, say it back, keep an undo. */
  ctx.implicit=(said,chips,apply)=>{const snap=JSON.stringify(ctx.data);apply(ctx);ctx.lastHeard={said,chips,snap};
    return{ar:chips.map(c=>plain(c.ar)).join('، ')+'.',en:chips.map(c=>plain(c.en)).join(', ')+'.'};};
  /* Two misses in a row: stop asking to speak, point at the pictures (research: escalate, then fall back). */
  function miss(kind){ctx.misses++;ctx.voice=ctx.misses>=2?'fallback':kind;log(kind+' (miss '+ctx.misses+')'+(ctx.misses>=2?': switching emphasis to pictures':''));render();}
  ctx.rerender=()=>render();
  ctx.say=text=>speak(text);
  ctx.setVoice=v=>{ctx.voice=v;render();};
  let timer=null;

  document.body.innerHTML=`
  <header class="lab-bar">
    <div><span class="tag">MISSION EL GHEET · UX Phase 4 · voice-first lab ${esc(def.num)}</span><h1>${esc(def.title)}</h1></div>
    <label>Lab <select id="lab-nav">${LABS.map(([f,n,tt])=>`<option value="${f}"${n===def.num?' selected':''}>${n} · ${tt}</option>`).join('')}</select></label>
    <label>State <select id="lab-state">${def.states.map(s=>`<option value="${s.id}">${esc(s.name)}</option>`).join('')}</select></label>
    <div class="group"><button data-lab="loc-ar" aria-pressed="true">العربية</button><button data-lab="loc-en" aria-pressed="false">English</button></div>
    <div class="group"><button data-lab="phone" aria-pressed="false">Phone width</button><button data-lab="tts" aria-pressed="false" title="Uses this browser's built-in speech synthesis; quality varies by device">Real browser voice</button><button data-lab="auto" aria-pressed="true" title="Speak each prompt when a screen opens (after the first tap)">Auto-speak</button></div>
    <a href="index.html">All labs</a>
  </header>
  <div class="lab-layout" id="layout">
    <section class="stage" id="stage" aria-label="App preview"></section>
    <aside class="lab-side">
      <div class="lab-card"><h2>Simulate the farmer</h2><p id="sim-hint"></p><div class="utterances" id="utter"></div></div>
      <div class="lab-card"><h2>Inject a problem</h2><div class="utterances">
        <button data-lab="silence">Silence <span>Mic opened, nobody spoke</span></button>
        <button data-lab="garble">Not understood <span>Recognition returns nothing useful</span></button>
        <button data-lab="deny" aria-pressed="false">Microphone denied <span>Permission refused; touch must still finish the task</span></button>
        <button data-lab="audiooff" aria-pressed="false">Sound unavailable <span>Playback failed; text and pictures remain</span></button>
      </div></div>
      <div class="lab-card"><h2>What this lab tests</h2><div id="notes"></div></div>
      <div class="lab-card"><h2>Event log</h2><pre class="log" id="log"></pre></div>
    </aside>
  </div>`;

  const $=id=>document.getElementById(id);
  const stage=$('stage');

  function log(msg){ctx.log.unshift(new Date().toLocaleTimeString()+'  '+msg);$('log').textContent=ctx.log.slice(0,40).join('\n');}
  ctx.logEvent=log;

  /* ---- audio ---- */
  function stopAudio(){
    clearTimeout(timer);
    if(window.speechSynthesis)window.speechSynthesis.cancel();
    if(ctx.voice==='speaking')ctx.voice=ctx.micDenied?'denied':'idle';
  }
  function speak(text){
    stopAudio();
    const txt=plain(ctx.t(text));
    if(!txt)return;
    if(ctx.audioOff){ctx.voice='audiooff';log('playback failed (simulated): '+txt.slice(0,50));render();return;}
    ctx.audioStarted=true;ctx.voice='speaking';ctx.speakingText=txt;log('speak ['+ctx.locale+']: '+txt.slice(0,70));render();
    const done=()=>{if(ctx.voice==='speaking'){ctx.voice=ctx.micDenied?'denied':'idle';render();}};
    if(ctx.realTTS&&window.speechSynthesis&&window.SpeechSynthesisUtterance){
      const u=new SpeechSynthesisUtterance(txt);u.lang=ctx.locale==='ar'?'ar-EG':'en-GB';u.rate=ctx.locale==='ar'?.92:.95;
      u.onend=done;u.onerror=()=>{log('browser voice error');done();};window.speechSynthesis.speak(u);
    }else{timer=setTimeout(done,Math.min(9000,900+txt.length*55));}
  }
  function autoSpeak(){if(ctx.autoPlay&&ctx.audioStarted&&def.prompt){const p=def.prompt(ctx);if(p)speak(p);}}

  /* ---- mic ---- */
  function micTap(){
    if(ctx.micDenied){ctx.voice='denied';log('mic tap ignored: permission denied, no re-prompt');render();return;}
    if(ctx.voice==='listening'){ctx.voice='processing';render();timer=setTimeout(()=>miss('nospeech'),700);return;}
    stopAudio();
    if(!ctx.micAsked){ctx.micAsked=true;ctx.voice='asking';log('first mic tap: explain, then browser permission prompt');render();timer=setTimeout(()=>{ctx.voice='listening';render();},1600);return;}
    ctx.voice='listening';ctx.heard=null;log('listening (push-to-talk)');render();
  }
  function utter(u){
    if(ctx.micDenied){log('ignored: mic denied');return;}
    stopAudio();ctx.micAsked=true;ctx.audioStarted=true;
    ctx.voice='listening';render();
    timer=setTimeout(()=>{ctx.voice='processing';render();
      timer=setTimeout(()=>{log('heard ['+ctx.locale+']: '+ctx.t(u.say));ctx.voice='idle';ctx.misses=0;ctx.lastHeard=null;
        const next=u.effect?u.effect(ctx):null;render();
        if(next)speak(next);else autoSpeak();},650);},500);
  }

  /* ---- render ---- */
  function render(){
    const L=ctx.locale;
    stage.lang=L;stage.dir=L==='ar'?'rtl':'ltr';stage.classList.toggle('fallback',ctx.voice==='fallback'||ctx.micDenied);
    const prog=def.progress?def.progress(ctx):null;
    const vt=VOICE_TEXT[ctx.voice]||VOICE_TEXT.idle;
    const micCls=ctx.micDenied?'off':ctx.voice==='listening'||ctx.voice==='asking'?'listening':ctx.voice==='processing'?'processing':ctx.voice==='speaking'?'speaking':'';
    const micLabel=ctx.micDenied?VOICE_TEXT.denied[L][0]:ctx.voice==='listening'?(L==='ar'?'خلّصت':'Done talking'):(L==='ar'?'اتكلّم':'Talk');
    const prompt=def.prompt?def.prompt(ctx):null;
    const showBack=def.back!==false;
    const mainHTML=def.render(ctx);
    // Caption only when the spoken words are not already the visible headline.
    const showCaption=prompt&&def.caption!==false&&!plain(mainHTML).replace(/\s+/g,' ').includes(plain(ctx.t(prompt)).replace(/\s+/g,' ').trim());
    stage.innerHTML=`
      <div class="app-head">
        ${showBack?`<button class="chip-btn" data-act="back">${icon('back')}<span>${ctx.t(UI.back)}</span></button>`:''}
        <span class="spacer"></span>
        <button class="chip-btn" data-act="lang" lang="${L==='ar'?'en':'ar'}">${icon('globe')}<span>${ctx.t(UI.lang)}</span></button>
        <button class="chip-btn" data-act="help">${icon('help')}<span>${ctx.t(UI.help)}</span></button>
      </div>
      ${prog?progressHTML(prog):''}
      <main class="app-main" id="app-main">
        ${showCaption?`<div class="caption ${ctx.voice==='speaking'?'speaking':''}" aria-live="polite">${icon('speaker')}<div><span class="who">${ctx.t(UI.says)}</span>${ctx.t(prompt)}</div></div>`:''}
        ${ctx.heard?heardHTML():''}
        ${ctx.lastHeard?`<div class="implicit" role="status">${icon('mic')}<span><span class="who">${ctx.locale==='ar'?'سمعت':'I heard'}</span> ${ctx.lastHeard.chips.map(c=>`<b>${ctx.t(c)}</b>`).join(' · ')}</span><button class="chip-btn" data-act="undo-heard">${icon('edit')}${ctx.t(UI.change)}</button></div>`:''}
        ${mainHTML}
      </main>
      ${(typeof def.dock==='function'?!def.dock(ctx):def.dock===false)?'':`<div class="dock" role="region" aria-label="${L==='ar'?'الصوت':'Voice'}">
        <div class="dock-state" role="status" aria-live="polite">${vt[L][0]}<small>${vt[L][1]||''}</small></div>
        <div class="side"><div class="ctl"><button class="round" data-act="${ctx.voice==='speaking'?'stop':'repeat'}" aria-label="${ctx.t(ctx.voice==='speaking'?UI.stop:UI.repeat)}">${icon(ctx.voice==='speaking'?'stop':'repeat')}</button><span class="round-label">${ctx.t(ctx.voice==='speaking'?UI.stop:UI.repeat)}</span></div></div>
        <div class="ctl"><button class="mic ${micCls}" data-act="mic" aria-label="${micLabel}" aria-pressed="${ctx.voice==='listening'}">${icon(ctx.micDenied?'micoff':'mic')}<span class="ring"></span></button><span class="round-label">${micLabel}</span></div>
        <div class="side end">${def.dockEnd?def.dockEnd(ctx):''}</div>
      </div>`}`;
    // simulator panel
    const us=def.utterances?def.utterances(ctx):[];
    $('sim-hint').textContent=us.length?'Tap a line to simulate the farmer saying it (as if they had pressed the mic). Arabic lines are draft phrasing for native review.':'Nothing to say on this state; use the screen controls.';
    $('utter').innerHTML=us.map((u,i)=>`<button data-utter="${i}" ${ctx.micDenied?'disabled':''}><bdi lang="${L}">${esc(ctx.t(u.say))}</bdi><span>${esc(u.label||'')}</span></button>`).join('');
    $('utter').onclick=e=>{const b=e.target.closest('[data-utter]');if(b)utter(us[+b.dataset.utter]);};
    const s=def.states.find(x=>x.id===ctx.state);
    $('notes').innerHTML=(s&&s.note?`<p><strong>${esc(s.name)}:</strong> ${esc(s.note)}</p>`:'')+'<ul>'+(def.notes||[]).map(n=>`<li>${n}</li>`).join('')+'</ul>';
    $('lab-state').value=ctx.state;
    document.querySelector('[data-lab="loc-ar"]').setAttribute('aria-pressed',L==='ar');
    document.querySelector('[data-lab="loc-en"]').setAttribute('aria-pressed',L==='en');
  }
  function progressHTML(p){
    const L=ctx.locale;
    return `<nav class="progress" aria-label="${L==='ar'?'المواسم الأربعة':'Four seasons'}"><ol>${[0,1,2,3].map(i=>{
      const c=p.crops&&p.crops[i];const done=c&&c!=='unknown';
      return `<li class="${p.now===i?'now':''} ${done?'done':''}" ${p.now===i?'aria-current="step"':''}><span class="n">${done?'✓':num(i+1,L)}</span><span class="lbl">${c?ctx.t(CROPS[c]):ctx.t(SEASONS[i])}</span></li>`;}).join('')}</ol>
      ${p.step?`<span class="step">${ctx.t(p.step)}</span>`:''}</nav>`;
  }
  function heardHTML(){
    const h=ctx.heard;
    return `<div class="heard" aria-live="polite"><div class="q">${ctx.t(UI.heardQ)}</div><div class="said">“${esc(ctx.t(h.said))}”</div>
      <div class="chips">${h.chips.map(c=>`<span class="chip ${c.missing?'missing':''}">${c.missing?icon('unknown'):''}${ctx.t(c.text)}</span>`).join('')}</div>
      <div class="actions"><button class="primary" data-act="heard-yes">${icon('check')}${ctx.t(h.yes||UI.yes)}</button><button class="secondary" data-act="heard-change">${icon('edit')}${ctx.t(UI.change)}</button></div></div>`;
  }

  /* ---- events ---- */
  stage.addEventListener('click',e=>{
    const b=e.target.closest('[data-act]');if(!b)return;const a=b.dataset.act;
    if(a==='mic')return micTap();
    if(a==='repeat'){const p=def.prompt&&def.prompt(ctx);if(p)speak(p);return;}
    if(a==='stop'){stopAudio();log('audio stopped by farmer');render();return;}
    if(a==='lang'){stopAudio();ctx.locale=ctx.locale==='ar'?'en':'ar';log('language switched to '+ctx.locale+'; facts kept');render();autoSpeak();return;}
    if(a==='help'){speak(def.help?def.help(ctx):{ar:'تقدر تتكلّم أو تختار صورة. دوس "تاني" علشان تسمع السؤال من الأول.',en:'You can talk or tap a picture. Press Repeat to hear the question again.'});return;}
    if(a==='heard-yes'&&ctx.heard){const h=ctx.heard;ctx.heard=null;log('farmer accepted proposal (still unconfirmed until final readback)');const n=h.onYes&&h.onYes(ctx);render();if(n)speak(n);else autoSpeak();return;}
    if(a==='hear'){const el=b.closest('.tile-wrap,.rb,.path li,.status,.option')||b;speak({ar:el.innerText,en:el.innerText});return;}
    if(a==='undo-heard'&&ctx.lastHeard){ctx.data=JSON.parse(ctx.lastHeard.snap);ctx.lastHeard=null;log('farmer undid the heard answer');render();speak({ar:'ماشي. قولها تاني أو اختار من الصور.',en:'OK. Say it again or choose from the pictures.'});return;}
    if(a==='heard-change'&&ctx.heard){ctx.heard=null;log('farmer rejected proposal');render();speak({ar:'ماشي. قولها تاني أو اختار من الصور.',en:'OK. Say it again or choose from the pictures.'});return;}
    if(def.action){stopAudio();const n=def.action(a,b,ctx);render();if(n)speak(n);}
  });
  document.querySelector('.lab-bar').addEventListener('click',e=>{
    const b=e.target.closest('[data-lab]');if(!b)return;const k=b.dataset.lab;
    if(k==='loc-ar'||k==='loc-en'){stopAudio();ctx.locale=k.slice(4);render();return;}
    if(k==='phone'){ctx.phone=!ctx.phone;b.setAttribute('aria-pressed',ctx.phone);$('layout').classList.toggle('phone',ctx.phone);return;}
    if(k==='tts'){ctx.realTTS=!ctx.realTTS;b.setAttribute('aria-pressed',ctx.realTTS);if(ctx.realTTS&&!window.speechSynthesis)log('this browser has no speechSynthesis; staying simulated');return;}
    if(k==='auto'){ctx.autoPlay=!ctx.autoPlay;b.setAttribute('aria-pressed',ctx.autoPlay);return;}
  });
  document.querySelector('.lab-side').addEventListener('click',e=>{
    const b=e.target.closest('[data-lab]');if(!b)return;const k=b.dataset.lab;
    if(k==='silence'){stopAudio();ctx.voice='listening';render();timer=setTimeout(()=>miss('nospeech'),1400);}
    if(k==='garble'){stopAudio();ctx.voice='processing';render();timer=setTimeout(()=>miss('notunderstood'),700);}
    if(k==='deny'){ctx.micDenied=!ctx.micDenied;b.setAttribute('aria-pressed',ctx.micDenied);ctx.voice=ctx.micDenied?'denied':'idle';log(ctx.micDenied?'mic denied: touch route only':'mic re-enabled');render();}
    if(k==='audiooff'){ctx.audioOff=!ctx.audioOff;b.setAttribute('aria-pressed',ctx.audioOff);stopAudio();ctx.voice=ctx.audioOff?'audiooff':'idle';log(ctx.audioOff?'audio unavailable':'audio restored');render();}
  });
  $('lab-state').onchange=e=>{ctx.data=JSON.parse(JSON.stringify(def.data||{}));if(def.enter)def.enter(e.target.value,ctx);ctx.go(e.target.value);};
  $('lab-nav').onchange=e=>{location.href=e.target.value;};
  if(def.enter)def.enter(ctx.state,ctx);
  if(def.onShow)def.onShow(ctx);
  render();
  return ctx;
}

window.Lab={page,icon,crop,date,num,esc,plain,CROPS,PURPOSE,SEASONS,UI,LABS};
})();
