const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const dir=__dirname,js=fs.readFileSync(dir+'/preview.js','utf8'),html=fs.readFileSync(dir+'/index.html','utf8'),css=fs.readFileSync(dir+'/design.css','utf8'),tokens=JSON.parse(fs.readFileSync(dir+'/tokens.proposal.json','utf8'));
new vm.Script(js);
function luminance(hex){return hex.slice(1).match(/../g).map(n=>parseInt(n,16)/255).map(n=>n<=.04045?n/12.92:((n+.055)/1.055)**2.4).reduce((sum,n,i)=>sum+n*[.2126,.7152,.0722][i],0);}
const contrast=(a,b)=>{const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
const rows=[];function pair(name,a,b,min){const value=contrast(a,b);rows.push({pair:name,foreground:a,background:b,ratio:Number(value.toFixed(2)),minimum:min});assert.ok(value>=min,`${name}: ${value} < ${min}`);}
for(const [name,p] of Object.entries(tokens.themes)){
 for(const bg of ['canvas','surface','wash']){for(const ink of ['ink','muted','secondary'])pair(`${name}.${ink}/${bg}`,p[ink],p[bg],4.5);}
 pair(name+'.action','#FFFFFF',p.action,4.5);pair(name+'.actionHover','#FFFFFF',p.actionHover,4.5);pair(name+'.border',p.border,p.surface,3);pair(name+'.focus',p.focus,p.canvas,3);pair(name+'.onAccent',p.ink,p.accent,4.5);
 for(const value of Object.values(p)){if(typeof value==='string')assert.ok(css.includes(value),'Missing CSS token '+value);}
}
for(const [name,p] of Object.entries(tokens.semantic)){pair(name,p.ink,p.surface,4.5);if(p.border)pair(name+'.border',p.border,p.surface,3);}
pair('earth.heroMuted','#64564B','#EEE3CF',4.5);
fs.writeFileSync(dir+'/contrast-report.json',JSON.stringify({scope:'Calculated opaque sRGB token pairs; not rendered, sunlight or full WCAG validation',pairs:rows},null,2)+'\n');
const gallery={innerHTML:'',className:'',querySelector(){return {focus(){}};}},select={value:''},events={};
const document={documentElement:{},getElementById:id=>id==='gallery'?gallery:select,querySelectorAll:()=>[],addEventListener:(key,fn)=>events[key]=fn};
const context={document};vm.runInNewContext(js,context);
const click=dataset=>events.click({target:{closest:()=>({dataset})}}),screen=value=>events.change({target:{id:'screen',value}});
let renders=0;
for(const locale of ['ar','en']){click({locale});for(const mode of ['compare','earth','light','ledger']){click({mode});for(const p of ['welcome','intake','planner','conflict','compare','history','outlook','evidence']){
 screen(p);assert.doesNotMatch(gallery.innerHTML,/undefined|NaN/);
 for(const cls of ['product ','listen','speak'])assert.equal((gallery.innerHTML.match(new RegExp('class="'+cls,'g'))||[]).length,mode==='compare'?3:1);
 // The language switch deliberately names Arabic in Arabic in the English UI.
 if(locale==='en')assert.doesNotMatch(gallery.innerHTML.replace(/<button class="locale"[^>]*>العربية<\/button>/g,''),/[\u0600-\u06ff]/);
 if(p==='outlook')assert.match(gallery.innerHTML,/Chronos-2/);renders++;
}}}
click({mode:'ledger'});click({locale:'en'});screen('welcome');click({a:'explore'});assert.match(gallery.innerHTML,/What do you need from your field/);click({a:'planner'});assert.match(gallery.innerHTML,/No planting schedule has been generated/);assert.doesNotMatch(gallery.innerHTML,/28 May/);screen('welcome');click({a:'check'});click({a:'planner'});assert.match(gallery.innerHTML,/28 May/);assert.match(gallery.innerHTML,/1 June/);assert.match(gallery.innerHTML,/Original plan rejected/);
for(const src of html.matchAll(/(?:src|href)="([^"#]+)"/g))assert.ok(fs.existsSync(path.resolve(dir,src[1])),src[1]);
for(const family of ['readexpro','notonaskharabic','notosansarabic']){const buffer=fs.readFileSync(`${dir}/fonts/${family}.ttf`);assert.equal(buffer.readUInt32BE(0),0x00010000);assert.match(fs.readFileSync(`${dir}/fonts/${family}-OFL.txt`,'utf8'),/SIL OPEN FONT LICENSE/);}
assert.doesNotMatch(js,/\b(fetch\s*\(|XMLHttpRequest|getUserMedia|localStorage|sessionStorage)/);assert.doesNotMatch(css,/@import/);assert.match(css,/prefers-reduced-motion/);assert.match(css,/:focus-visible/);
console.log(`PASS: syntax; ${renders} rendered-template states; two intention paths; one speaker/mic per view; full English templates; fixture invariants; ${rows.length} contrast pairs; local links; font headers/licenses; no live services.`);
console.log('Token contrasts, templates and DOM-stub navigation only. Not browser layout, screen-reader or farmer-usability validation.');
console.log(rows.filter(x=>/\.action$/.test(x.pair)).map(x=>`${x.pair}: ${x.ratio}:1`).join('\n'));
