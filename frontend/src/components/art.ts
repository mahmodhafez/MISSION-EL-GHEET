/* Outline icons (36 grid) and coloured crop pictures, copied from work/ux-phase-4/lab.js.
 * Crop pictures are placeholders: real photos + a farmer recognition test are required (design §2). */
/* eslint-disable */
export const ICON: Record<string, string> = {
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
  play:'<path d="M10 6v24l20-12z"/>',
  calendar:'<rect x="4" y="7" width="28" height="25" rx="3"/><path d="M4 14h28M11 3v7M25 3v7M10 20h4M16 20h4M22 20h4M10 26h4M16 26h4"/>',
  sun:'<circle cx="18" cy="18" r="6"/><path d="M18 3v4M18 29v4M3 18h4M29 18h4M7 7l3 3M26 26l3 3M29 7l-3 3M10 26l-3 3"/>',
  winter:'<path d="M8 21h19a5 5 0 0 0 0-10 9 9 0 0 0-17-2 6 6 0 0 0-2 12M12 26l-1 5M18 26l-1 5M24 26l-1 5"/>',
  thermo:'<path d="M15 6a3 3 0 0 1 6 0v15a6 6 0 1 1-6 0z"/><path d="M18 13v12"/>',
  drop:'<path d="M18 4q10 12 10 19a10 10 0 0 1-20 0q0-7 10-19z"/>',
  search:'<circle cx="15" cy="15" r="10"/><path d="m22 22 10 10"/>',
  plus:'<path d="M18 6v24M6 18h24"/>',
  cow:'<path d="M5 9q4 3 9 2M31 9q-4 3-9 2"/><path d="M12 11q6-3 12 0l1 12q0 8-7 8t-7-8z"/><circle cx="15" cy="17" r="1"/><circle cx="21" cy="17" r="1"/><path d="M14 26q4 2 8 0"/>',
  sack:'<path d="M13 5h10l-2 6q9 5 9 14a7 7 0 0 1-7 7H13a7 7 0 0 1-7-7q0-9 9-14z"/><path d="M14 11h8M15 22l3 3 3-3"/>',
  field:'<path d="M3 29 11 8h14l8 21z"/><path d="M7 19h22M18 8v21"/>',
  soil:'<path d="M3 11h30M3 19h30M3 27h30"/><circle cx="10" cy="15" r="1"/><circle cx="24" cy="23" r="1"/><circle cx="17" cy="31" r="1"/>',
  salt:'<path d="M12 9h12l2 22H10z"/><path d="M13 4h10v5H13zM15 16h1M20 18h1M16 23h1"/>',
  cut:'<circle cx="9" cy="27" r="4"/><circle cx="27" cy="27" r="4"/><path d="M12 24 26 5M24 24 10 5"/>',
  sow:'<path d="M18 32V16M18 18q-10 0-12-10q10 0 12 10M18 14q2-9 12-9q-1 9-12 9"/>',
  arrow:'<path d="M6 18h22M20 10l8 8-8 8"/>'
};

function tre(x: number, y: number, r: number){ // berseem leaf: three long leaflets
  return [-38,0,38].map(a=>`<ellipse cx="${x}" cy="${y-r}" rx="${r*0.42}" ry="${r}" transform="rotate(${a} ${x} ${y})" fill="#5E9E3E" stroke="#2F6A2A" stroke-width="1.5"/>`).join('');}
function grains(x: number, y0: number, n: number, dx: number, fill: string, edge: string, rx: number, ry: number, tilt: number){let o='';for(let i=0;i<n;i++){const y=y0+i*ry*1.45;
  o+=`<ellipse cx="${x-dx}" cy="${y}" rx="${rx}" ry="${ry}" transform="rotate(${-tilt} ${x-dx} ${y})" fill="${fill}" stroke="${edge}" stroke-width="1.3"/><ellipse cx="${x+dx}" cy="${y}" rx="${rx}" ry="${ry}" transform="rotate(${tilt} ${x+dx} ${y})" fill="${fill}" stroke="${edge}" stroke-width="1.3"/>`;}return o;}
function kernels(){let o='';for(let r=0;r<7;r++)for(let c=0;c<3;c++)o+=`<circle cx="${61+c*5}" cy="${52+r*5.2}" r="2.1" fill="#F7D458" stroke="#C99A10" stroke-width=".8"/>`;return o;}
export const CROP_ART: Record<string, string> = {
  berseem:`<g stroke="#3C7A2E" stroke-width="2.6" fill="none" stroke-linecap="round"><path d="M55 116V58M55 96Q38 86 30 64M55 88Q72 80 80 58M55 106Q36 104 22 92M55 108Q76 104 90 92"/></g>
    ${tre(30,66,13)}${tre(80,60,13)}${tre(22,94,10)}${tre(90,94,10)}
    <ellipse cx="55" cy="40" rx="11" ry="17" fill="#F5EDCB" stroke="#B5A160" stroke-width="1.6"/><path d="M47 34h16M46 41h18M47 48h16" stroke="#D9CC95" stroke-width="1.4"/>
    <ellipse cx="36" cy="44" rx="7" ry="11" fill="#F5EDCB" stroke="#B5A160" stroke-width="1.4"/><path d="M36 54v10" stroke="#3C7A2E" stroke-width="2"/>`,
  maize:`<path d="M46 118V14" stroke="#4E8A32" stroke-width="4.5" stroke-linecap="round"/>
    <path d="M46 74Q18 70 6 96Q24 80 46 82Z" fill="#6DAA45" stroke="#3E7A2A" stroke-width="1.4"/>
    <path d="M46 42Q20 34 10 50Q26 42 46 50Z" fill="#6DAA45" stroke="#3E7A2A" stroke-width="1.4"/>
    <path d="M46 100Q70 98 84 116Q66 106 46 108Z" fill="#6DAA45" stroke="#3E7A2A" stroke-width="1.4"/>
    <path d="M50 92Q52 70 60 46" stroke="#4E8A32" stroke-width="3" fill="none"/>
    <ellipse cx="66" cy="68" rx="11" ry="22" fill="#F2C230" stroke="#B88A0C" stroke-width="1.6"/>${kernels()}
    <path d="M56 90Q50 66 62 44Q58 70 68 92Z" fill="#8CC65C" stroke="#3E7A2A" stroke-width="1.3"/><path d="M78 90Q84 66 72 46Q78 70 66 92Z" fill="#8CC65C" stroke="#3E7A2A" stroke-width="1.3"/>
    <path d="M66 46q2-8 6-10M64 46q-1-8 2-12" stroke="#B5762A" stroke-width="1.5" fill="none"/>
    <path d="M46 14l-9-10M46 14l9-10M46 14V2M46 14l-4-12M46 14l4-12" stroke="#C9A24A" stroke-width="2" stroke-linecap="round"/>`,
  wheat:`<path d="M55 118V40M40 118Q42 80 32 52M70 118Q68 80 78 52" stroke="#B88C2E" stroke-width="2.8" fill="none" stroke-linecap="round"/>
    <path d="M55 112Q34 100 26 78Q44 92 55 96Z" fill="#9DBA55" stroke="#6E8A2E" stroke-width="1.3"/>
    ${grains(55,22,6,5,'#E6BC4E','#A9821F',4.2,6.4,22)}${grains(31,40,4,4,'#E6BC4E','#A9821F',3.4,5.4,22)}${grains(79,40,4,4,'#E6BC4E','#A9821F',3.4,5.4,22)}
    <path d="M55 16V2M49 22L41 8M61 22l8-14M27 36l-6-12M35 36l2-13M75 36l-2-13M83 36l6-12" stroke="#C9A24A" stroke-width="1.6" stroke-linecap="round"/>`,
  sorghum:`<path d="M55 118V40" stroke="#4E8A32" stroke-width="4.5" stroke-linecap="round"/>
    <path d="M55 88Q24 82 10 104Q30 90 55 96Z" fill="#6DAA45" stroke="#3E7A2A" stroke-width="1.4"/>
    <path d="M55 64Q86 56 100 76Q80 66 55 72Z" fill="#6DAA45" stroke="#3E7A2A" stroke-width="1.4"/>
    <path d="M55 108Q82 104 94 118Q76 110 55 114Z" fill="#6DAA45" stroke="#3E7A2A" stroke-width="1.4"/>
    ${[[55,10],[47,15],[63,15],[42,22],[52,21],[60,22],[68,22],[45,29],[55,28],[65,29],[49,36],[60,36],[55,42]].map(([x,y]: number[])=>`<circle cx="${x}" cy="${y+2}" r="5.2" fill="#A8492A" stroke="#6E2A14" stroke-width="1.2"/>`).join('')}`,
  fallow:'<g fill="none" stroke="#7A5C3A" stroke-width="2.6" stroke-linecap="round"><path d="M10 100h90M20 92h70M30 84h50"/></g>',
  unknown:'<g fill="none" stroke="#6B7B73" stroke-width="2.6" stroke-linecap="round"><circle cx="55" cy="60" r="34" stroke-dasharray="6 5"/><path d="M45 50a10 10 0 1 1 15 8c-3 2-5 4-5 8M55 76v2"/></g>'
};
