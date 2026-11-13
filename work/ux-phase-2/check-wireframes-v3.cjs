// Offline structural/state checks; these do not validate browser rendering or agronomy.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(__dirname+'/season-path-wireframes-v3.html','utf8');
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
function setup(){
 const nodes=new Map(),events={};
 function node(){const attrs={},classes=new Set();return {innerHTML:'',textContent:'',hidden:false,dataset:{},attrs,setAttribute(k,v){attrs[k]=v;},querySelector(){return null;},querySelectorAll(){return [];},classList:{toggle(k,on){on?classes.add(k):classes.delete(k);},contains:k=>classes.has(k)}};}
 const root={querySelector(k){if(!nodes.has(k))nodes.set(k,node());return nodes.get(k);},querySelectorAll(){return [];},addEventListener(k,v){events[k]=v;}};
 const document={getElementById:()=>root,documentElement:node()};
 const context={document,Intl,Date};
 // Test-only state observation: no changes to the executable design artifact.
 vm.runInNewContext(script.replace('render();\n})();','globalThis.state=()=>JSON.parse(JSON.stringify({plan,page,season,step,locale,voice,playing,candidate,editor,pending}));\nrender();\n})();'),context);
 const click=dataset=>events.click({target:{closest:()=>({dataset})}}),action=a=>click({action:a});
 const change=(dataset,value,id)=>events.change({target:{dataset,value,id}});
 return {root,document,click,action,change,state:()=>JSON.parse(JSON.stringify(context.state())),body:()=>root.querySelector('.app-body').innerHTML,notice:()=>root.querySelector('.notice').textContent};
}
let checks=0;
function test(name,fn){fn();checks++;console.log('PASS '+name);}
function checkMarkup(markup){
 const stack=[],voids=new Set(['input','br','hr','img','meta','link','source','wbr']);
 for(const token of markup.matchAll(/<\/?([a-z][a-z0-9-]*)\b[^>]*>/gi)){
  const name=token[1].toLowerCase();if(voids.has(name)||token[0].endsWith('/>'))continue;
  if(token[0].startsWith('</'))assert.equal(stack.pop(),name,'Mismatched tag '+token[0]);else stack.push(name);
 }
 assert.deepEqual(stack,[],'Unclosed generated tags');
}
function reference(h){h.action('fixture');for(let i=0;i<4;i++){h.click({crop:String(i)});h.action('cropnext');h.action('seasonnext');}assert.equal(h.state().page,'context');h.action('confirm');h.action('confirmed');assert.equal(h.state().plan.result,'rejected');}
test('1. Hussein: four seasons, confirmed fixture, rejected P0, zero alternatives, simulated save',()=>{
 const h=setup();assert.equal(h.state().locale,'ar');reference(h);assert.match(h.body(),/صفر بدائل/);assert.equal(h.state().plan.seasons[0].end,'2027-05-20');assert.ok(h.state().plan.seasons[0].dateLock);assert.ok(h.state().plan.seasons[1].cropLock);assert.ok(h.state().plan.seasons[2].cropLock);h.action('card');h.action('save');assert.ok(h.state().plan.saved);assert.equal(h.state().plan.result,'rejected');h.action('listen');assert.match(h.body(),/معاينة حفظ ناجح/);
});
test('2. Other catalogue crops, unknown dates, no forced commitment, no inherited fixture result',()=>{
 const h=setup();h.action('start');for(const crop of [2,3,0,1]){h.click({crop:String(crop)});h.action('cropnext');h.action('seasonnext');}h.action('confirm');h.action('confirmed');assert.equal(h.state().plan.result,'needs_review');assert.equal(h.state().plan.evaluated,false);assert.deepEqual(h.state().plan.seasons.map(s=>s.crop),[2,3,0,1]);assert.ok(h.state().plan.seasons.every(s=>s.sow===null&&!s.cropLock&&!s.dateLock));h.action('card');h.action('save');assert.ok(h.state().plan.saved);
});
test('3. Protected date correction: old value retained until separate explicit acknowledgment',()=>{
 const h=setup();reference(h);h.action('card');h.action('save');h.click({season:'0'});h.action('cropnext');h.action('enddate');h.change({typeddate:''},'2027-05-22');h.action('applydate');assert.equal(h.state().plan.seasons[0].end,'2027-05-20');assert.ok(h.state().pending);h.action('cancelprotected');assert.equal(h.state().plan.seasons[0].end,'2027-05-20');h.action('enddate');h.change({typeddate:''},'2027-05-22');h.action('applydate');h.action('applyprotected');assert.equal(h.state().plan.seasons[0].end,'2027-05-22');assert.ok(h.state().plan.seasons[0].dateLock);assert.equal(h.state().plan.result,null);assert.equal(h.state().plan.saved,false);assert.equal(h.state().plan.confirmed,false);h.action('confirm');h.action('confirmed');h.action('card');h.action('save');assert.ok(h.state().plan.saved);
});
test('4. Inspect versus adopt; preserve locks; invalidate harvest/release and downstream result',()=>{
 const h=setup();reference(h);const before=h.state().plan.version;h.action('inspect');h.click({candidate:'2027-06-01'});assert.equal(h.state().plan.seasons[1].sow,'2027-05-15');assert.equal(h.state().plan.version,before);h.action('back');assert.equal(h.state().page,'result');h.action('inspect');h.click({candidate:'2027-06-01'});h.action('adopt');assert.equal(h.state().plan.seasons[1].sow,'2027-06-01');assert.equal(h.state().plan.seasons[1].end,null);assert.equal(h.state().plan.seasons[1].release,null);assert.equal(h.state().plan.result,null);assert.ok(h.state().plan.seasons[0].dateLock);assert.ok(h.state().plan.seasons[1].cropLock);assert.ok(h.state().plan.seasons[2].cropLock);h.action('confirmed');h.action('card');h.action('save');assert.ok(h.state().plan.saved);assert.equal(h.state().plan.evaluated,false);
});
test('5. Entirely incomplete draft, explicit confirmation, failed save and retry',()=>{
 const h=setup();h.action('start');for(let i=0;i<4;i++){h.action('unknowncrop');h.action('seasonnext');}h.action('card');h.action('save');assert.equal(h.state().page,'confirm');h.action('confirmed');h.action('card');h.action('savefail');assert.equal(h.state().plan.saved,false);assert.ok(h.state().plan.saveFailed);h.action('save');assert.ok(h.state().plan.saved);assert.equal(h.state().plan.result,'needs_review');assert.ok(h.state().plan.seasons.every(s=>s.crop===null));
});
test('6. NASA exploration returns to exact inspected candidate and preserves plan',()=>{
 const h=setup();reference(h);h.action('inspect');h.click({candidate:'2027-06-01'});const before=JSON.stringify(h.state().plan);h.action('replay');for(const metric of ['temperature','heat','demand','variation']){h.click({metric});assert.match(h.body(),/القيم غير موصلة/);}assert.match(h.body(),/2001-01-01/);assert.match(h.body(),/ASCE daily cloudiness bound/);h.action('back');assert.equal(h.state().page,'inspect');assert.equal(h.state().candidate,'2027-06-01');assert.equal(JSON.stringify(h.state().plan),before);
});
test('7. Seven dated illustrative slots, unavailable/stale outlook, no numeric predictions',()=>{
 const h=setup();reference(h);h.action('outlook');assert.equal((h.body().match(/<li><b>/g)||[]).length,7);assert.match(h.body(),/٣١ أكتوبر/);assert.match(h.body(),/لم تتفوق/);h.action('stale');assert.match(h.body(),/التوقع قديم/);h.action('forecastunavailable');assert.match(h.body(),/مفيش توقع حالي/);h.action('back');assert.equal(h.state().page,'result');assert.equal(h.state().plan.result,'rejected');
});
test('8. Complete English screens, RTL/LTR, language switch preserves data and cancels audio',()=>{
 const h=setup();reference(h);h.action('listen');const before=JSON.stringify(h.state().plan);h.click({locale:'en'});assert.equal(h.state().playing,false);assert.equal(h.document.documentElement.attrs.dir,'ltr');assert.equal(JSON.stringify(h.state().plan),before);for(const p of ['welcome','plan','context','confirm','result','inspect','replay','outlook','card','states','failure']){h.click({reviewpage:p});assert.doesNotMatch(h.body(),/[\u0600-\u06ff]/,p+' has untranslated farmer content');assert.equal((h.body().match(/data-action="listen"/g)||[]).length,1,p+' speaker count');assert.doesNotMatch(h.body(),/undefined|NaN/);}h.click({locale:'ar'});assert.equal(h.document.documentElement.attrs.dir,'rtl');assert.equal(JSON.stringify(h.state().plan),before);
});
test('9. Engineer details, precise edits, unknowns, validation and generic review save',()=>{
 const h=setup();reference(h);h.action('context');h.change({context:'area'},'-1');assert.equal(h.state().plan.area,1);h.change({context:'area'},'2');h.change({context:'prep'},'');assert.equal(h.state().plan.area,2);assert.equal(h.state().plan.prep,null);h.action('confirm');h.action('confirmed');assert.equal(h.state().plan.result,'needs_review');h.action('card');assert.match(h.body(),/المصادر/);assert.match(h.body(),/NASA/);h.action('save');assert.ok(h.state().plan.saved);
});
test('10. Speech simulations/failures/interruption never confirm; audio section and correction',()=>{
 const h=setup();h.action('start');h.action('speak');assert.equal(h.state().voice,'listening');h.action('recognized');assert.equal(h.state().plan.seasons[0].crop,null);h.action('proposal');assert.equal(h.state().plan.seasons[0].crop,0);assert.equal(h.state().plan.confirmed,false);for(const state of ['unclear','denied','unavailable','audiofailed']){h.change({},state,'voice-simulation');assert.equal(h.state().plan.confirmed,false);assert.match(h.body(),/إجاباتك لسه موجودة/);}h.action('speak');h.action('stopvoice');assert.equal(h.state().voice,'ready');h.action('cropnext');h.action('recognized');h.action('dateproposal');h.change({typeddate:''},'2027-02-30');h.action('applydate');assert.match(h.notice(),/صحيحين/);assert.equal(h.state().plan.seasons[0].end,null);h.change({typeddate:''},'2027-05-20');h.action('applydate');assert.equal(h.state().plan.seasons[0].end,'2027-05-20');assert.equal(h.state().plan.confirmed,false);
});
test('Additional: protected crop correction retains independent date, empty selection and network recovery',()=>{
 const h=setup();reference(h);h.click({season:'0'});h.click({crop:'2'});assert.ok(h.state().pending);assert.equal(h.state().plan.seasons[0].crop,0);h.action('applyprotected');assert.ok(h.state().plan.seasons[0].dateLock);assert.equal(h.state().plan.seasons[0].end,'2027-05-20');assert.equal(h.state().plan.result,null);h.action('loadfail');assert.equal(h.state().page,'failure');h.action('card');h.action('confirm');h.action('confirmed');h.action('card');h.action('save');assert.ok(h.state().plan.saved);const empty=setup();empty.action('start');empty.action('cropnext');assert.equal(empty.state().step,'crop');assert.match(empty.notice(),/اختار/);
});
test('Structure: standalone parity, no network/mic/storage, reduced motion, V2 link, layout switch',()=>{
 assert.equal(fs.readFileSync(__dirname+'/preview-v3.html','utf8'),html);assert.ok(!/\b(fetch\s*\(|XMLHttpRequest|WebSocket|getUserMedia|localStorage|sessionStorage)/.test(script));assert.ok(html.includes('prefers-reduced-motion'));assert.ok(html.includes('min-height:48px'));assert.ok(html.includes('season-path-wireframes.html'));assert.doesNotMatch(html,/اسمع السؤال/);const h=setup();h.click({layout:'desktop'});assert.ok(h.root.querySelector('.stage').classList.contains('desktop'));
});
test('Generated markup: all views, both languages, date editor and pending commitment',()=>{
 const h=setup();reference(h);for(const locale of ['ar','en']){h.click({locale});for(const page of ['welcome','plan','context','confirm','result','inspect','replay','outlook','card','states','failure']){h.click({reviewpage:page});checkMarkup(h.body());checkMarkup(h.root.querySelector('.mini-path').innerHTML);}}
 h.click({season:'0'});h.action('cropnext');h.action('enddate');checkMarkup(h.body());h.change({typeddate:''},'2027-05-22');h.action('applydate');checkMarkup(h.body());h.click({locale:'ar'});h.click({locale:'en'});assert.doesNotMatch(h.body(),/[\u0600-\u06ff]/);h.action('listen');assert.doesNotMatch(h.body(),/[\u0600-\u06ff]/);assert.equal(h.state().plan.seasons[0].end,'2027-05-20');
});
test('One speaker throughout speech failure/retry, matched English transcripts, focus/reduced-motion rules',()=>{
 const h=setup();h.action('start');h.click({locale:'en'});for(const state of ['ready','listening','recognized','unclear','denied','unavailable','audiofailed']){h.change({},state,'voice-simulation');assert.equal((h.body().match(/data-action="listen"/g)||[]).length,1);assert.doesNotMatch(h.body(),/[\u0600-\u06ff]/);checkMarkup(h.body());}h.action('listen');assert.doesNotMatch(h.body(),/[\u0600-\u06ff]/);assert.ok(html.includes(':focus-visible'));assert.ok(html.includes('.mini-path{position:sticky'));assert.ok(html.includes('h?.focus({preventScroll:true})'));
});
console.log(`${checks} groups passed. Minimal-DOM checks only; rendering, screen readers, speech and farmer usability require separate verification.`);
