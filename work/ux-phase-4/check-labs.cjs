// Static check for the UX Phase 4 voice-first labs. Node only, no dependencies.
// Covers: script syntax, local links, lab list matches files, no live services, accessibility basics,
// no un-isolated Arabic-digit ranges, and minimum touch-target tokens.
// It does NOT render pages, test speech, devices, screen readers or farmers.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=__dirname;
const read=f=>fs.readFileSync(path.join(root,f),'utf8');
const js=read('lab.js'),css=read('lab.css');
new vm.Script(js,{filename:'lab.js'});
const labs=fs.readdirSync(root).filter(f=>/^lab-\d\d-.*\.html$/.test(f)).sort();
assert.equal(labs.length,9,'expected 9 labs (00–08)');
const listed=[...js.matchAll(/\['(lab-\d\d-[a-z-]+\.html)'/g)].map(m=>m[1]).sort();
assert.deepEqual(listed,labs,'LABS list in lab.js must match the lab files');
let states=0;
for(const f of [...labs,'index.html']){
  const html=read(f);
  for(const m of html.matchAll(/(?:src|href)="([^"#:]+)"/g))assert.ok(fs.existsSync(path.resolve(root,m[1])),`${f}: missing ${m[1]}`);
  for(const m of html.matchAll(/<script>([\s\S]*?)<\/script>/g))new vm.Script(m[1],{filename:f});
  if(f!=='index.html'){
    assert.match(html,/Lab\.page\(def\)/,`${f}: does not register a page`);
    assert.match(html,/notes:\[/,`${f}: needs review notes`);
    const s=(html.match(/\{id:'[a-z0-9-]+',name:/g)||[]).length;assert.ok(s>=2||f==='lab-00-voice.html',`${f}: needs at least 2 states`);states+=s;
  }
  assert.doesNotMatch(html,/\b(fetch\s*\(|XMLHttpRequest|getUserMedia|localStorage|sessionStorage|https?:\/\/(?!www\.w3))/,`${f}: live service or network use`);
  // Arabic-Indic ranges: each number in its own isolate so digits stay intact and the earlier year reads on the right (RTL)
  for(const m of html.matchAll(/[٠-٩]+[\/–][٠-٩]+/g))assert.fail(`${f}: un-isolated Arabic range ${m[0]}; write <bdi>A</bdi>/<bdi>B</bdi>`);
}
for(const m of js.matchAll(/[٠-٩]+[\/–][٠-٩]+/g))assert.fail(`lab.js: un-isolated Arabic range ${m[0]}; write <bdi>A</bdi>/<bdi>B</bdi>`);
assert.doesNotMatch(js,/\b(fetch\s*\(|XMLHttpRequest|getUserMedia|localStorage|sessionStorage)/,'lab.js: live service use');
assert.match(css,/prefers-reduced-motion/);assert.match(css,/:focus-visible/);assert.doesNotMatch(css,/@import/);
assert.match(css,/\.chip-btn\{min-height:48px;min-width:48px/,'header controls must stay ≥48px');
assert.match(css,/\.primary\{min-height:60px/,'primary actions must stay ≥60px');
assert.match(css,/\.phone \.stage\{height:760px\}/,'phone review frame must stay 390x760 (one step = one screen)');
console.log(`PASS: ${labs.length} labs, ${states} named states; syntax, local links, lab list, no live services, per-number isolated Arabic ranges, focus/reduced-motion, 48/60px targets.`);
console.log('Static checks only. Not browser layout, speech, device, screen-reader or farmer-usability validation.');
