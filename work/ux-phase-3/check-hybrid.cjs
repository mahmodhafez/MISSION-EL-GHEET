const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=__dirname,js=fs.readFileSync(root+'/fieldlight-hybrid.js','utf8'),html=fs.readFileSync(root+'/fieldlight-hybrid.html','utf8');
new vm.Script(js);const tokens=JSON.parse(fs.readFileSync(root+'/tokens.fieldlight-hybrid.proposal.json','utf8'));
for(const m of html.matchAll(/(?:src|href)="([^"#]+)"/g))assert.ok(fs.existsSync(path.resolve(root,m[1])),m[1]);
const gallery={innerHTML:'',className:'',querySelector:()=>({focus(){}})},selector={},events={};
vm.runInNewContext(js,{document:{documentElement:{},getElementById:id=>id==='gallery'?gallery:selector,querySelectorAll:()=>[],addEventListener:(k,v)=>events[k]=v}});
const click=dataset=>events.click({target:{closest:()=>({dataset})}}),screen=value=>events.change({target:{id:'screen',value}});
for(const locale of ['ar','en']){click({locale});for(const view of ['planner','conflict','history']){screen(view);assert.doesNotMatch(gallery.innerHTML,/undefined|NaN/);assert.equal((gallery.innerHTML.match(/class="listen"/g)||[]).length,1);assert.equal((gallery.innerHTML.match(/class="speak"/g)||[]).length,1);if(view==='planner')assert.equal((gallery.innerHTML.match(/class="botanical-window"/g)||[]).length,4);}}
screen('welcome');click({a:'explore'});click({a:'planner'});assert.match(gallery.innerHTML,/No planting schedule has been generated/);assert.doesNotMatch(gallery.innerHTML,/28 May/);screen('welcome');click({a:'check'});click({a:'planner'});assert.match(gallery.innerHTML,/Original plan rejected/);assert.match(gallery.innerHTML,/28 May/);assert.match(gallery.innerHTML,/1 June/);click({width:'phone'});assert.match(gallery.className,/phone-mode/);
const luminance=h=>h.slice(1).match(/../g).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
const pairs=[[tokens.themes.light.ink,tokens.themes.light.canvas],[tokens.themes.light.muted,tokens.themes.light.surface],['#FFFFFF',tokens.themes.light.action],...Object.values(tokens.semantic).map(p=>[p.ink,p.surface])];
for(const [a,b] of pairs){const l=[luminance(a),luminance(b)].sort((x,y)=>y-x);assert.ok((l[0]+.05)/(l[1]+.05)>=4.5,a+' / '+b);}
assert.doesNotMatch(js,/\b(fetch\s*\(|getUserMedia|localStorage)/);
console.log('PASS: syntax, local dependencies, six bilingual core templates, both intentions, phone mode, '+pairs.length+' text contrast pairs. No browser-layout or usability validation.');
