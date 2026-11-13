// Structural/state checks only: no browser rendering, speech or agronomy validation.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(__dirname + '/season-path-wireframes.html', 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
new vm.Script(script);
function element() {
  const classes = new Set();
  return { innerHTML: '', textContent: '', hidden: false, dataset: {}, setAttribute() {},
    classList: { contains: c => classes.has(c), toggle(c, on) { if (on) classes.add(c); else classes.delete(c); } }
  };
}
const nodes = new Map(), events = {};
const root = { querySelector(key) { if (!nodes.has(key)) nodes.set(key, element()); return nodes.get(key); },
  querySelectorAll() { return []; }, addEventListener(type, fn) { events[type] = fn; } };
vm.runInNewContext(script, { document: { getElementById: () => root }, window: { addEventListener() {} } });
const body = () => root.querySelector('.app-body').innerHTML;
const notice = () => root.querySelector('.notice').textContent;
const invoke = dataset => events.click({ target: { closest: () => ({ dataset }) } });
const action = name => invoke({ action: name });
const screen = n => invoke({ screen: String(n) });
const field = (name,value) => events.change({ target: { dataset: {field:name}, value } });
const voice = value => events.change({ target: { id:'voice-simulation', value } });
const speakerCount = () => (body().match(/data-action="listen"/g)||[]).length;
for (let i=0;i<7;i++) { screen(i); assert.ok(body().length>100); assert.ok(!body().includes('undefined')); assert.equal(speakerCount(),1); }
screen(0); assert.equal(root.querySelector('.app-foot').hidden,true);
assert.doesNotMatch(html,/اسمع السؤال|data-action="repeat"/);
action('crops'); assert.match(body(),/إيه أول محصول/); assert.match(body(),/data-action="speak"/);
action('choosecrop'); assert.match(notice(),/اختار محصول/);
invoke({crop:'برسيم'}); action('choosecrop'); assert.match(body(),/آخر حشة برسيم/);
action('back'); assert.match(body(),/إيه أول محصول/);
action('choosecrop'); action('protectyes');
for (const crop of ['ذرة حبوب','قمح','ذرة رفيعة حبوب']) { invoke({crop}); action('choosecrop'); }
assert.match(body(),/الأرض/); action('review');
assert.match(body(),/دي اختياراتك/); assert.equal((body().match(/data-action="confirmed"/g)||[]).length,1);
assert.match(body(),/data-action="speak"/);
action('speak'); assert.match(body(),/بسمعك/); action('stopvoice'); assert.match(notice(),/مفيش إجابة اتأكدت/);
for (const state of ['recognized','unclear','denied','unavailable','audiofailed']) { voice(state); assert.equal(speakerCount(),1); assert.match(body(),/voice-panel/); }
voice('recognized'); assert.match(body(),/لسه مش متأكد/); action('useproposal');
action('confirmed'); assert.match(body(),/× الخطة فيها تعارض/); assert.match(body(),/صفر بدائل/);
action('listen'); assert.match(body(),/خمستاشر مايو/); assert.equal(speakerCount(),1); action('stopaudio');
action('inspect'); invoke({date:'١ يونيو ٢٠٢٧'}); assert.match(body(),/بتشوف بس/);
action('replay'); assert.match(body(),/NASA/); action('replayback'); assert.match(body(),/بتشوف بس/);
assert.match(body(),/aria-pressed="true">١ يونيو/); action('closeinspect'); assert.match(body(),/× الخطة فيها تعارض/);
action('path'); assert.match(body(),/أربع مواسم/); action('pathback'); assert.match(body(),/× الخطة فيها تعارض/);
action('inspect'); action('adopt'); assert.match(body(),/تغيير في المسودة فقط/);
action('confirmed'); assert.match(body(),/مفيش نتيجة جديدة/); assert.doesNotMatch(body(),/× الخطة فيها تعارض/);
action('card'); assert.doesNotMatch(body(),/data-action="save"/);
action('listen'); assert.match(body(),/مفيش نتيجة محسوبة للخطة دي/); assert.doesNotMatch(body(),/ميعاد الذرة خمستاشر/);
action('original'); assert.match(body(),/دي اختياراتك/); action('confirmed'); action('card');
action('save'); assert.match(body(),/معاينة: مسودة محفوظة/); assert.match(body(),/× الخطة فيها تعارض/); assert.equal(speakerCount(),1);
action('savefail'); assert.match(body(),/لسه مش محفوظة/); assert.match(notice(),/الحفظ ما اكتملش/);
action('edit'); field('typedDate','2027-05-22'); assert.match(body(),/٢٢ مايو ٢٠٢٧/);
action('review'); action('confirmed'); assert.match(body(),/مفيش نتيجة جديدة/);
action('original'); action('edit'); field('cutDay','31'); field('cutMonth','4'); action('protectyes'); assert.match(notice(),/اليوم مش موجود/);
action('original'); action('contextedit'); field('area','-1'); assert.match(notice(),/راجع القيمة/);
field('area','2'); field('prep','9'); action('review'); assert.match(body(),/٢ هكتار/); assert.match(body(),/٩ أيام/);
action('confirmed'); assert.match(body(),/مفيش نتيجة جديدة/);
action('original'); action('edit'); action('protectlater'); action('review'); assert.match(body(),/مفيش التزامات ثابتة/);
action('confirmed'); assert.match(body(),/مفيش نتيجة جديدة/);
invoke({view:'states'}); assert.equal((root.querySelector('.state-board').innerHTML.match(/class="state-tile"/g)||[]).length,12);
invoke({layout:'desktop'}); assert.equal(root.querySelector('.stage').classList.contains('desktop'),true);
assert.ok(!/\b(fetch\s*\(|XMLHttpRequest|WebSocket|getUserMedia|localStorage|sessionStorage)/.test(script));
assert.ok(html.includes('prefers-reduced-motion'));
assert.equal(fs.readFileSync(__dirname+'/preview.html','utf8'),html);
console.log('PASS: JavaScript syntax; 7 views; single speaker; touch journey; substep Back; one confirmation; voice states/proposals; inspect/adopt separation; replay return; stale-result guards; manual edits; invalid date/value; optional protection; save/failure separation; 12 state examples; desktop switch; matching standalone preview; no network/mic/storage.');
console.log('Minimal-DOM state checks only. Browser layout, actual audio, screen readers and farmer usability remain unverified.');
