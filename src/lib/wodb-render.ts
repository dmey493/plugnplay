// @ts-nocheck
/* eslint-disable */
// GENERATED from toolbelt/wodb/*.html — faithful copy of the SVG render
// helpers, kept per-grade because a few (dotplot/prism/boxplot/spinner/
// mapping/transform) have grade-specific variants. Do not hand-edit; edit
// the source routine and re-run scratchpad/extract_render.js.
// Each box in the data is a spec { t: "<fn>", args: [...] }; nested specs
// (e.g. text containing a fraction) resolve recursively.

export type WodbBox = { t: string; args: unknown[] };

const TABLES = (() => {
  function build6() {
    const C = {ns:'#0d9488', rp:'#ea580c', af:'#7c3aed', gm:'#16a34a', ds:'#2563eb'};
    let clipN = 0;
    function frac(n,d){return `<span class="frac"><span class="n">${n}</span><span class="d">${d}</span></span>`;}
function txt(main,sub){return `<div class="q-text">${main}${sub?`<div class="q-sub">${sub}</div>`:''}</div>`;}
function dots(filled, empty){
  const total=filled+empty, per=5, r=13, gapX=33, gapY=36;
  const rows=Math.ceil(total/per);
  const startY=70-((rows-1)*gapY)/2;
  let s=`<svg viewBox="0 0 200 140" class="q-svg">`;
  let idx=0;
  for(let row=0; row<rows; row++){
    const inRow=Math.min(per, total-row*per);
    const startX=100-((inRow-1)*gapX)/2;
    for(let c=0;c<inRow;c++){
      const cx=startX+c*gapX, cy=startY+row*gapY;
      const isFilled= idx<filled;
      s+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="${isFilled?C.rp:'#fff'}" stroke="${C.rp}" stroke-width="3"/>`;
      idx++;
    }
  }
  return s+`</svg>`;
}
function ineq(boundary,right,closed,min,max){
  const X=v=>18+(v-min)/(max-min)*184;
  let s=`<svg viewBox="0 0 220 86" class="q-svg">`;
  s+=`<line x1="${X(min)}" y1="42" x2="${X(max)}" y2="42" stroke="#334" stroke-width="2"/>`;
  for(let v=min;v<=max;v++){
    s+=`<line x1="${X(v)}" y1="37" x2="${X(v)}" y2="47" stroke="#334" stroke-width="1.4"/>`;
    s+=`<text x="${X(v)}" y="66" text-anchor="middle" font-size="11" fill="#556" font-family="system-ui">${v}</text>`;
  }
  const end= right? X(max) : X(min);
  s+=`<line x1="${X(boundary)}" y1="42" x2="${end}" y2="42" stroke="${C.af}" stroke-width="5" stroke-linecap="round"/>`;
  const dir= right?1:-1;
  s+=`<path d="M${end} 42 l${-8*dir} -6 v12 z" fill="${C.af}"/>`;
  s+=`<circle cx="${X(boundary)}" cy="42" r="7.5" fill="${closed?C.af:'#fff'}" stroke="${C.af}" stroke-width="3.2"/>`;
  return s+`</svg>`;
}
function point(px,py){
  const min=-5,max=5, X=v=>100+v*15.5, Y=v=>100-v*15.5;
  let s=`<svg viewBox="0 0 200 200" class="q-svg" style="max-height:170px">`;
  for(let v=min;v<=max;v++){
    s+=`<line x1="${X(min)}" y1="${Y(v)}" x2="${X(max)}" y2="${Y(v)}" stroke="#eef1f6" stroke-width="1"/>`;
    s+=`<line x1="${X(v)}" y1="${Y(min)}" x2="${X(v)}" y2="${Y(max)}" stroke="#eef1f6" stroke-width="1"/>`;
  }
  s+=`<line x1="${X(min)}" y1="${Y(0)}" x2="${X(max)}" y2="${Y(0)}" stroke="#334" stroke-width="1.6"/>`;
  s+=`<line x1="${X(0)}" y1="${Y(min)}" x2="${X(0)}" y2="${Y(max)}" stroke="#334" stroke-width="1.6"/>`;
  s+=`<circle cx="${X(px)}" cy="${Y(py)}" r="6.5" fill="${C.af}"/>`;
  const lx=X(px)+(px<0?-7:7), ly=Y(py)+(py>0?-11:19);
  s+=`<text x="${lx}" y="${ly}" text-anchor="${px<0?'end':'start'}" font-size="15" font-weight="800" fill="${C.af}" font-family="system-ui">(${px}, ${py})</text>`;
  return s+`</svg>`;
}
function dotplot(values,min,max){
  const X=v=>18+(v-min)/(max-min)*184;
  const counts={}; values.forEach(v=>counts[v]=(counts[v]||0)+1);
  let s=`<svg viewBox="0 0 220 120" class="q-svg">`;
  s+=`<line x1="12" y1="98" x2="208" y2="98" stroke="#334" stroke-width="2"/>`;
  for(let v=min;v<=max;v++){
    s+=`<line x1="${X(v)}" y1="95" x2="${X(v)}" y2="101" stroke="#334" stroke-width="1.2"/>`;
    s+=`<text x="${X(v)}" y="115" text-anchor="middle" font-size="10.5" fill="#556" font-family="system-ui">${v}</text>`;
  }
  Object.keys(counts).forEach(v=>{
    for(let i=0;i<counts[v];i++)
      s+=`<circle cx="${X(+v)}" cy="${88-i*14}" r="5.4" fill="${C.ds}"/>`;
  });
  return s+`</svg>`;
}
function shaded(n){
  let s=`<svg viewBox="0 0 120 120" class="q-svg" style="max-height:130px">`;
  const cell=10, ox=10, oy=10;
  for(let i=0;i<100;i++){
    const r=Math.floor(i/10), c=i%10;
    s+=`<rect x="${ox+c*cell}" y="${oy+r*cell}" width="${cell}" height="${cell}" fill="${i<n?C.ns:'#eef7f5'}" stroke="#cfe3df" stroke-width="0.7"/>`;
  }
  return s+`</svg>`;
}
function rect(w,h){
  const u=Math.min(120/w,90/h,22), pw=w*u, ph=h*u, ox=100-pw/2, oy=70-ph/2;
  let s=`<svg viewBox="0 0 200 140" class="q-svg">`;
  s+=`<rect x="${ox}" y="${oy}" width="${pw}" height="${ph}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2.2"/>`;
  s+=`<text x="100" y="${oy+ph+17}" text-anchor="middle" font-size="13" fill="#334" font-family="system-ui">${w}</text>`;
  s+=`<text x="${ox-7}" y="${oy+ph/2+4}" text-anchor="end" font-size="13" fill="#334" font-family="system-ui">${h}</text>`;
  return s+`</svg>`;
}
function triangle(b,h){
  const u=Math.min(120/b,80/h,22), pb=b*u, ph=h*u, ox=100-pb/2, baseY=70+ph/2, apexY=70-ph/2;
  let s=`<svg viewBox="0 0 200 140" class="q-svg">`;
  s+=`<polygon points="${ox},${baseY} ${ox+pb},${baseY} ${ox+pb*0.32},${apexY}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2.2"/>`;
  s+=`<line x1="${ox+pb*0.32}" y1="${apexY}" x2="${ox+pb*0.32}" y2="${baseY}" stroke="${C.gm}" stroke-width="1" stroke-dasharray="3 3"/>`;
  s+=`<text x="100" y="${baseY+17}" text-anchor="middle" font-size="13" fill="#334" font-family="system-ui">${b}</text>`;
  s+=`<text x="${ox+pb*0.32+6}" y="${(apexY+baseY)/2}" font-size="13" fill="#334" font-family="system-ui">${h}</text>`;
  return s+`</svg>`;
}
function parallelo(b,h){
  const u=Math.min(110/b,80/h,22), pb=b*u, ph=h*u, sk=ph*0.5, ox=100-(pb+sk)/2, topY=70-ph/2, botY=70+ph/2;
  let s=`<svg viewBox="0 0 200 140" class="q-svg">`;
  s+=`<polygon points="${ox+sk},${topY} ${ox+sk+pb},${topY} ${ox+pb},${botY} ${ox},${botY}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2.2"/>`;
  s+=`<line x1="${ox}" y1="${botY}" x2="${ox}" y2="${topY}" stroke="${C.gm}" stroke-width="1" stroke-dasharray="3 3"/>`;
  s+=`<text x="${ox+sk+pb/2}" y="${botY+17}" text-anchor="middle" font-size="13" fill="#334" font-family="system-ui">${b}</text>`;
  s+=`<text x="${ox-7}" y="${70+4}" text-anchor="end" font-size="13" fill="#334" font-family="system-ui">${h}</text>`;
  return s+`</svg>`;
}
function prism(w,h,d){
  const u=15, pw=w*u, ph=h*u, dx=d*8, dy=d*8;
  const ox=60, oyB=118;            // front bottom-left
  const oyT=oyB-ph;                // front top-left
  let s=`<svg viewBox="0 0 200 150" class="q-svg">`;
  // top face
  s+=`<polygon points="${ox},${oyT} ${ox+pw},${oyT} ${ox+pw+dx},${oyT-dy} ${ox+dx},${oyT-dy}" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/>`;
  // right face
  s+=`<polygon points="${ox+pw},${oyT} ${ox+pw+dx},${oyT-dy} ${ox+pw+dx},${oyB-dy} ${ox+pw},${oyB}" fill="#86efac" stroke="${C.gm}" stroke-width="2"/>`;
  // front face
  s+=`<rect x="${ox}" y="${oyT}" width="${pw}" height="${ph}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/>`;
  // labels: w bottom, h left, d along top-right
  s+=`<text x="${ox+pw/2}" y="${oyB+16}" text-anchor="middle" font-size="12.5" fill="#334" font-family="system-ui">${w}</text>`;
  s+=`<text x="${ox-7}" y="${oyT+ph/2+4}" text-anchor="end" font-size="12.5" fill="#334" font-family="system-ui">${h}</text>`;
  s+=`<text x="${ox+pw+dx/2+5}" y="${oyT-dy/2-2}" font-size="12.5" fill="#334" font-family="system-ui">${d}</text>`;
  return s+`</svg>`;
}
function words(s){return `<div class="q-text sm">${s}</div>`;}
function tableH(headers,rows){let s=`<table class="mini-table"><thead><tr>`+headers.map(h=>`<th>${h}</th>`).join('')+`</tr></thead><tbody>`;rows.forEach(r=>s+=`<tr>`+r.map(c=>`<td>${c}</td>`).join('')+`</tr>`);return s+`</tbody></table>`;}
function boxplot(mn,q1,med,q3,mx,sMin,sMax){const X=v=>18+(v-sMin)/(sMax-sMin)*184,y=52,bh=30,c=C.ds;let s=`<svg viewBox="0 0 220 108" class="q-svg"><line x1="12" y1="92" x2="208" y2="92" stroke="#334" stroke-width="1.5"/>`;for(let v=sMin;v<=sMax;v+=2){s+=`<line x1="${X(v)}" y1="89" x2="${X(v)}" y2="95" stroke="#334" stroke-width="1"/><text x="${X(v)}" y="105" text-anchor="middle" font-size="9.5" fill="#556" font-family="system-ui">${v}</text>`;}s+=`<line x1="${X(mn)}" y1="${y}" x2="${X(q1)}" y2="${y}" stroke="${c}" stroke-width="1.8"/><line x1="${X(q3)}" y1="${y}" x2="${X(mx)}" y2="${y}" stroke="${c}" stroke-width="1.8"/><line x1="${X(mn)}" y1="${y-8}" x2="${X(mn)}" y2="${y+8}" stroke="${c}" stroke-width="1.8"/><line x1="${X(mx)}" y1="${y-8}" x2="${X(mx)}" y2="${y+8}" stroke="${c}" stroke-width="1.8"/><rect x="${X(q1)}" y="${y-bh/2}" width="${X(q3)-X(q1)}" height="${bh}" fill="#dbeafe" stroke="${c}" stroke-width="1.8"/><line x1="${X(med)}" y1="${y-bh/2}" x2="${X(med)}" y2="${y+bh/2}" stroke="${c}" stroke-width="2.6"/></svg>`;return s;}
function histogram(bins){const n=bins.length,mx=Math.max(...bins),baseY=96,top=14,ox=24,bw=176/n,sY=(baseY-top)/mx;let s=`<svg viewBox="0 0 210 116" class="q-svg"><line x1="24" y1="12" x2="24" y2="${baseY}" stroke="#334" stroke-width="1.4"/><line x1="24" y1="${baseY}" x2="200" y2="${baseY}" stroke="#334" stroke-width="1.4"/>`;bins.forEach((h,i)=>{const x=ox+i*bw;s+=`<rect x="${x}" y="${baseY-h*sY}" width="${bw}" height="${h*sY}" fill="#dbeafe" stroke="${C.ds}" stroke-width="1.4"/>`;});return s+`</svg>`;}
function barchart(vals){const n=vals.length,mx=Math.max(...vals),baseY=96,top=14,ox=24,slot=176/n,bw=slot*0.62,sY=(baseY-top)/mx,cols=['#f59e0b','#10b981','#ef4444','#6366f1','#ec4899'];let s=`<svg viewBox="0 0 210 116" class="q-svg"><line x1="24" y1="12" x2="24" y2="${baseY}" stroke="#334" stroke-width="1.4"/><line x1="24" y1="${baseY}" x2="200" y2="${baseY}" stroke="#334" stroke-width="1.4"/>`;vals.forEach((h,i)=>{const x=ox+i*slot+(slot-bw)/2;s+=`<rect x="${x}" y="${baseY-h*sY}" width="${bw}" height="${h*sY}" fill="${cols[i%cols.length]}" opacity="0.85"/><text x="${x+bw/2}" y="${baseY+13}" text-anchor="middle" font-size="10" fill="#556" font-family="system-ui">${'ABCDE'[i]}</text>`;});return s+`</svg>`;}
function tapeDiagram(a,b){const u=Math.min(150/Math.max(a,b),24),h=20,ox=44,y1=32,y2=64;let s=`<svg viewBox="0 0 200 104" class="q-svg">`;for(let i=0;i<a;i++)s+=`<rect x="${ox+i*u}" y="${y1}" width="${u}" height="${h}" fill="#93c5fd" stroke="#2563eb" stroke-width="1.5"/>`;for(let i=0;i<b;i++)s+=`<rect x="${ox+i*u}" y="${y2}" width="${u}" height="${h}" fill="#fca5a5" stroke="#dc2626" stroke-width="1.5"/>`;s+=`<text x="${ox-5}" y="${y1+14}" text-anchor="end" font-size="11" fill="#2563eb" font-weight="700" font-family="system-ui">blue</text><text x="${ox-5}" y="${y2+14}" text-anchor="end" font-size="11" fill="#dc2626" font-weight="700" font-family="system-ui">red</text></svg>`;return s;}
function doubleNumberLine(top,bot){const n=top.length,ox=30,ex=196,gap=(ex-ox)/(n-1);let s=`<svg viewBox="0 0 210 104" class="q-svg">`;s+=`<line x1="${ox}" y1="40" x2="${ex+6}" y2="40" stroke="#2563eb" stroke-width="2"/><path d="M${ex+6} 40 l-7 -4 v8 z" fill="#2563eb"/><line x1="${ox}" y1="74" x2="${ex+6}" y2="74" stroke="#dc2626" stroke-width="2"/><path d="M${ex+6} 74 l-7 -4 v8 z" fill="#dc2626"/>`;top.forEach((v,i)=>{const x=ox+i*gap;s+=`<line x1="${x}" y1="35" x2="${x}" y2="45" stroke="#2563eb" stroke-width="1.5"/><text x="${x}" y="26" text-anchor="middle" font-size="11" fill="#2563eb" font-weight="700" font-family="system-ui">${v}</text>`;});bot.forEach((v,i)=>{const x=ox+i*gap;s+=`<line x1="${x}" y1="69" x2="${x}" y2="79" stroke="#dc2626" stroke-width="1.5"/><text x="${x}" y="94" text-anchor="middle" font-size="11" fill="#dc2626" font-weight="700" font-family="system-ui">${v}</text>`;});return s+`</svg>`;}
    return { frac, txt, dots, ineq, point, dotplot, shaded, rect, triangle, parallelo, prism, words, tableH, boxplot, histogram, barchart, tapeDiagram, doubleNumberLine, __setClip: (n) => { clipN = n; } };
  }
  function build7() {
    const C = {ns:'#0d9488',rp:'#ea580c',af:'#7c3aed',gm:'#16a34a',ds:'#2563eb'};
    let clipN = 0;
    function frac(n,d){return `<span class="frac"><span class="n">${n}</span><span class="d">${d}</span></span>`;}
function txt(main,sub){return `<div class="q-text">${main}${sub?`<div class="q-sub">${sub}</div>`:''}</div>`;}
function words(s){return `<div class="q-text sm">${s}</div>`;}
function tableH(headers,rows){
  let s=`<table class="mini-table"><thead><tr>`+headers.map(h=>`<th>${h}</th>`).join('')+`</tr></thead><tbody>`;
  rows.forEach(r=> s+=`<tr>`+r.map(c=>`<td>${c}</td>`).join('')+`</tr>`);
  return s+`</tbody></table>`;
}
function dots(filled,empty){
  const total=filled+empty,per=5,r=13,gapX=33,gapY=36,rows=Math.ceil(total/per),startY=70-((rows-1)*gapY)/2;
  let s=`<svg viewBox="0 0 200 140" class="q-svg">`,idx=0;
  for(let row=0;row<rows;row++){const inRow=Math.min(per,total-row*per),startX=100-((inRow-1)*gapX)/2;
    for(let c=0;c<inRow;c++){const cx=startX+c*gapX,cy=startY+row*gapY;
      s+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="${idx<filled?C.rp:'#fff'}" stroke="${C.rp}" stroke-width="3"/>`;idx++;}}
  return s+`</svg>`;
}
function ineq(boundary,right,closed,min,max){
  const X=v=>18+(v-min)/(max-min)*184;let s=`<svg viewBox="0 0 220 86" class="q-svg">`;
  s+=`<line x1="${X(min)}" y1="42" x2="${X(max)}" y2="42" stroke="#334" stroke-width="2"/>`;
  for(let v=min;v<=max;v++){s+=`<line x1="${X(v)}" y1="37" x2="${X(v)}" y2="47" stroke="#334" stroke-width="1.4"/><text x="${X(v)}" y="66" text-anchor="middle" font-size="11" fill="#556" font-family="system-ui">${v}</text>`;}
  const end=right?X(max):X(min),dir=right?1:-1;
  s+=`<line x1="${X(boundary)}" y1="42" x2="${end}" y2="42" stroke="${C.af}" stroke-width="5" stroke-linecap="round"/>`;
  s+=`<path d="M${end} 42 l${-8*dir} -6 v12 z" fill="${C.af}"/>`;
  s+=`<circle cx="${X(boundary)}" cy="42" r="7.5" fill="${closed?C.af:'#fff'}" stroke="${C.af}" stroke-width="3.2"/>`;
  return s+`</svg>`;
}
function point(px,py,color){
  color=color||C.af;const min=-5,max=5,X=v=>100+v*15.5,Y=v=>100-v*15.5;
  let s=`<svg viewBox="0 0 200 200" class="q-svg" style="max-height:170px">`;
  for(let v=min;v<=max;v++){s+=`<line x1="${X(min)}" y1="${Y(v)}" x2="${X(max)}" y2="${Y(v)}" stroke="#eef1f6" stroke-width="1"/><line x1="${X(v)}" y1="${Y(min)}" x2="${X(v)}" y2="${Y(max)}" stroke="#eef1f6" stroke-width="1"/>`;}
  s+=`<line x1="${X(min)}" y1="${Y(0)}" x2="${X(max)}" y2="${Y(0)}" stroke="#334" stroke-width="1.6"/><line x1="${X(0)}" y1="${Y(min)}" x2="${X(0)}" y2="${Y(max)}" stroke="#334" stroke-width="1.6"/>`;
  s+=`<circle cx="${X(px)}" cy="${Y(py)}" r="6.5" fill="${color}"/>`;
  const lx=X(px)+(px<0?-7:7),ly=Y(py)+(py>0?-11:19);
  s+=`<text x="${lx}" y="${ly}" text-anchor="${px<0?'end':'start'}" font-size="15" font-weight="800" fill="${color}" font-family="system-ui">(${px}, ${py})</text>`;
  return s+`</svg>`;
}
function linegraph(spec){
  const min=-6,max=6,X=v=>100+v*14.5,Y=v=>100-v*14.5,id='cl'+(clipN++);
  let s=`<svg viewBox="0 0 200 200" class="q-svg" style="max-height:172px">`;
  s+=`<defs><clipPath id="${id}"><rect x="${X(min)}" y="${Y(max)}" width="${X(max)-X(min)}" height="${Y(min)-Y(max)}"/></clipPath></defs>`;
  for(let v=min;v<=max;v++){s+=`<line x1="${X(min)}" y1="${Y(v)}" x2="${X(max)}" y2="${Y(v)}" stroke="#eef1f6" stroke-width="1"/><line x1="${X(v)}" y1="${Y(min)}" x2="${X(v)}" y2="${Y(max)}" stroke="#eef1f6" stroke-width="1"/>`;}
  s+=`<line x1="${X(min)}" y1="${Y(0)}" x2="${X(max)}" y2="${Y(0)}" stroke="#334" stroke-width="1.5"/><line x1="${X(0)}" y1="${Y(min)}" x2="${X(0)}" y2="${Y(max)}" stroke="#334" stroke-width="1.5"/>`;
  s+=`<g clip-path="url(#${id})">`;
  (spec.lines||[]).forEach(l=>{const col=l.color||C.af;
    if(l.vertical!==undefined){s+=`<line x1="${X(l.vertical)}" y1="${Y(min)}" x2="${X(l.vertical)}" y2="${Y(max)}" stroke="${col}" stroke-width="3"/>`;}
    else{const y1=l.m*min+l.b,y2=l.m*max+l.b;s+=`<line x1="${X(min)}" y1="${Y(y1)}" x2="${X(max)}" y2="${Y(y2)}" stroke="${col}" stroke-width="3" ${l.dashed?'stroke-dasharray="5 4"':''}/>`;}});
  (spec.curves||[]).forEach(c=>{const col=c.color||C.af;let pts='';for(let x=min;x<=max;x+=0.4){pts+=`${X(x)},${Y(c.a*x*x+(c.b||0))} `;}s+=`<polyline points="${pts}" fill="none" stroke="${col}" stroke-width="3"/>`;});
  (spec.points||[]).forEach(p=> s+=`<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="4.5" fill="${p.color||C.ds}"/>`);
  return s+`</g></svg>`;
}
function numline2(a,b,min,max,color){
  color=color||C.ns;const X=v=>18+(v-min)/(max-min)*184;let s=`<svg viewBox="0 0 220 100" class="q-svg">`;
  s+=`<line x1="${X(min)}" y1="60" x2="${X(max)}" y2="60" stroke="#334" stroke-width="2"/>`;
  for(let v=min;v<=max;v++){s+=`<line x1="${X(v)}" y1="55" x2="${X(v)}" y2="65" stroke="#334" stroke-width="1.2"/><text x="${X(v)}" y="82" text-anchor="middle" font-size="10.5" fill="#556" font-family="system-ui">${v}</text>`;}
  const x1=Math.min(X(a),X(b)),x2=Math.max(X(a),X(b));
  s+=`<line x1="${x1}" y1="34" x2="${x2}" y2="34" stroke="${color}" stroke-width="2"/><line x1="${x1}" y1="34" x2="${x1}" y2="55" stroke="${color}" stroke-width="1.4"/><line x1="${x2}" y1="34" x2="${x2}" y2="55" stroke="${color}" stroke-width="1.4"/>`;
  s+=`<text x="${(x1+x2)/2}" y="26" text-anchor="middle" font-size="13" font-weight="800" fill="${color}" font-family="system-ui">${Math.abs(a-b)}</text>`;
  s+=`<circle cx="${X(a)}" cy="60" r="6" fill="${color}"/><circle cx="${X(b)}" cy="60" r="6" fill="${color}"/>`;
  return s+`</svg>`;
}
function shaded(n){
  let s=`<svg viewBox="0 0 120 120" class="q-svg" style="max-height:130px">`;const cell=10,ox=10,oy=10;
  for(let i=0;i<100;i++){const r=Math.floor(i/10),c=i%10;s+=`<rect x="${ox+c*cell}" y="${oy+r*cell}" width="${cell}" height="${cell}" fill="${i<n?C.ns:'#eef7f5'}" stroke="#cfe3df" stroke-width="0.7"/>`;}
  return s+`</svg>`;
}
function rect(w,h){const u=Math.min(120/w,90/h,22),pw=w*u,ph=h*u,ox=100-pw/2,oy=70-ph/2;
  return `<svg viewBox="0 0 200 140" class="q-svg"><rect x="${ox}" y="${oy}" width="${pw}" height="${ph}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2.2"/><text x="100" y="${oy+ph+17}" text-anchor="middle" font-size="13" fill="#334" font-family="system-ui">${w}</text><text x="${ox-7}" y="${oy+ph/2+4}" text-anchor="end" font-size="13" fill="#334" font-family="system-ui">${h}</text></svg>`;}
function triangle(b,h){const u=Math.min(120/b,80/h,22),pb=b*u,ph=h*u,ox=100-pb/2,baseY=70+ph/2,apexY=70-ph/2;
  return `<svg viewBox="0 0 200 140" class="q-svg"><polygon points="${ox},${baseY} ${ox+pb},${baseY} ${ox+pb*0.32},${apexY}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2.2"/><line x1="${ox+pb*0.32}" y1="${apexY}" x2="${ox+pb*0.32}" y2="${baseY}" stroke="${C.gm}" stroke-width="1" stroke-dasharray="3 3"/><text x="100" y="${baseY+17}" text-anchor="middle" font-size="13" fill="#334" font-family="system-ui">${b}</text><text x="${ox+pb*0.32+6}" y="${(apexY+baseY)/2}" font-size="13" fill="#334" font-family="system-ui">${h}</text></svg>`;}
function parallelo(b,h){const u=Math.min(110/b,80/h,22),pb=b*u,ph=h*u,sk=ph*0.5,ox=100-(pb+sk)/2,topY=70-ph/2,botY=70+ph/2;
  return `<svg viewBox="0 0 200 140" class="q-svg"><polygon points="${ox+sk},${topY} ${ox+sk+pb},${topY} ${ox+pb},${botY} ${ox},${botY}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2.2"/><line x1="${ox}" y1="${botY}" x2="${ox}" y2="${topY}" stroke="${C.gm}" stroke-width="1" stroke-dasharray="3 3"/><text x="${ox+sk+pb/2}" y="${botY+17}" text-anchor="middle" font-size="13" fill="#334" font-family="system-ui">${b}</text><text x="${ox-7}" y="74" text-anchor="end" font-size="13" fill="#334" font-family="system-ui">${h}</text></svg>`;}
function prism(w,h,d){const u=15,pw=w*u,ph=h*u,dx=d*8,dy=d*8,ox=60,oyB=118,oyT=oyB-ph;
  let s=`<svg viewBox="0 0 200 150" class="q-svg">`;
  s+=`<polygon points="${ox},${oyT} ${ox+pw},${oyT} ${ox+pw+dx},${oyT-dy} ${ox+dx},${oyT-dy}" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/>`;
  s+=`<polygon points="${ox+pw},${oyT} ${ox+pw+dx},${oyT-dy} ${ox+pw+dx},${oyB-dy} ${ox+pw},${oyB}" fill="#86efac" stroke="${C.gm}" stroke-width="2"/>`;
  s+=`<rect x="${ox}" y="${oyT}" width="${pw}" height="${ph}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/>`;
  s+=`<text x="${ox+pw/2}" y="${oyB+16}" text-anchor="middle" font-size="12.5" fill="#334" font-family="system-ui">${w}</text><text x="${ox-7}" y="${oyT+ph/2+4}" text-anchor="end" font-size="12.5" fill="#334" font-family="system-ui">${h}</text><text x="${ox+pw+dx/2+5}" y="${oyT-dy/2-2}" font-size="12.5" fill="#334" font-family="system-ui">${d}</text>`;
  return s+`</svg>`;}
function dotplot(values,min,max){const X=v=>18+(v-min)/(max-min)*184,counts={};values.forEach(v=>counts[v]=(counts[v]||0)+1);
  let s=`<svg viewBox="0 0 220 120" class="q-svg"><line x1="12" y1="98" x2="208" y2="98" stroke="#334" stroke-width="2"/>`;
  for(let v=min;v<=max;v++){s+=`<line x1="${X(v)}" y1="95" x2="${X(v)}" y2="101" stroke="#334" stroke-width="1.2"/><text x="${X(v)}" y="115" text-anchor="middle" font-size="10.5" fill="#556" font-family="system-ui">${v}</text>`;}
  Object.keys(counts).forEach(v=>{for(let i=0;i<counts[v];i++)s+=`<circle cx="${X(+v)}" cy="${88-i*14}" r="5.4" fill="${C.ds}"/>`;});
  return s+`</svg>`;}
function boxplot(mn,q1,med,q3,mx,sMin,sMax){const X=v=>18+(v-sMin)/(sMax-sMin)*184,y=52,bh=30,c=C.ds;
  let s=`<svg viewBox="0 0 220 108" class="q-svg"><line x1="12" y1="92" x2="208" y2="92" stroke="#334" stroke-width="1.5"/>`;
  for(let v=sMin;v<=sMax;v+=2){s+=`<line x1="${X(v)}" y1="89" x2="${X(v)}" y2="95" stroke="#334" stroke-width="1"/><text x="${X(v)}" y="105" text-anchor="middle" font-size="9.5" fill="#556" font-family="system-ui">${v}</text>`;}
  s+=`<line x1="${X(mn)}" y1="${y}" x2="${X(q1)}" y2="${y}" stroke="${c}" stroke-width="1.8"/><line x1="${X(q3)}" y1="${y}" x2="${X(mx)}" y2="${y}" stroke="${c}" stroke-width="1.8"/>`;
  s+=`<line x1="${X(mn)}" y1="${y-8}" x2="${X(mn)}" y2="${y+8}" stroke="${c}" stroke-width="1.8"/><line x1="${X(mx)}" y1="${y-8}" x2="${X(mx)}" y2="${y+8}" stroke="${c}" stroke-width="1.8"/>`;
  s+=`<rect x="${X(q1)}" y="${y-bh/2}" width="${X(q3)-X(q1)}" height="${bh}" fill="#dbeafe" stroke="${c}" stroke-width="1.8"/><line x1="${X(med)}" y1="${y-bh/2}" x2="${X(med)}" y2="${y+bh/2}" stroke="${c}" stroke-width="2.6"/>`;
  return s+`</svg>`;}
function scatter(kind){
  const data={pos:[[1,1.5],[2,2],[3,3.2],[4,3.4],[5,4.8],[6,5.4],[7,7],[8,7.6]],
    neg:[[1,7.6],[2,7],[3,5.5],[4,5],[5,3.8],[6,3],[7,2.2],[8,1.4]],
    none:[[1,5],[2,2],[3,7],[4,3.2],[5,6],[6,2.4],[7,7.5],[8,4]],
    nonlinear:[[1,7],[2,4.4],[3,2.4],[4,1.5],[5,1.6],[6,2.7],[7,4.7],[8,7.2]]}[kind];
  const X=v=>26+v/9*168,Y=v=>96-v/9*84;
  let s=`<svg viewBox="0 0 210 120" class="q-svg"><line x1="24" y1="12" x2="24" y2="98" stroke="#334" stroke-width="1.4"/><line x1="24" y1="98" x2="202" y2="98" stroke="#334" stroke-width="1.4"/>`;
  data.forEach(([x,y])=>s+=`<circle cx="${X(x)}" cy="${Y(y)}" r="3.6" fill="${C.ds}"/>`);
  return s+`</svg>`;}
function spinner(fr){const cx=100,cy=70,r=44,ang=fr*2*Math.PI,large=fr>0.5?1:0,ex=cx+r*Math.sin(ang),ey=cy-r*Math.cos(ang);
  let s=`<svg viewBox="0 0 200 150" class="q-svg">`;
  s+= fr>=1 ? `<circle cx="${cx}" cy="${cy}" r="${r}" fill="#c7d2fe"/>` : `<path d="M${cx} ${cy} L${cx} ${cy-r} A${r} ${r} 0 ${large} 1 ${ex} ${ey} Z" fill="#c7d2fe"/>`;
  s+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${C.ds}" stroke-width="2.4"/>`;
  s+=`<line x1="${cx}" y1="${cy}" x2="${cx+r*0.7}" y2="${cy-r*0.55}" stroke="#1f2430" stroke-width="2.4"/><circle cx="${cx}" cy="${cy}" r="3.5" fill="#1f2430"/>`;
  return s+`</svg>`;}
function circleShape(r,type){const pr=Math.min(r*8,52),color=C.gm;
  let s=`<svg viewBox="0 0 200 150" class="q-svg"><circle cx="100" cy="64" r="${pr}" fill="#eafaf0" stroke="${color}" stroke-width="2.4"/><circle cx="100" cy="64" r="2.6" fill="${color}"/>`;
  if(type==='d'){s+=`<line x1="${100-pr}" y1="64" x2="${100+pr}" y2="64" stroke="${color}" stroke-width="1.8"/><text x="100" y="${64+pr+20}" text-anchor="middle" font-size="14" font-weight="700" fill="#334" font-family="system-ui">d = ${r*2}</text>`;}
  else{s+=`<line x1="100" y1="64" x2="${100+pr}" y2="64" stroke="${color}" stroke-width="1.8"/><text x="100" y="${64+pr+20}" text-anchor="middle" font-size="14" font-weight="700" fill="#334" font-family="system-ui">r = ${r}</text>`;}
  return s+`</svg>`;}
function cylinder(){const cx=100,rx=34,ry=11,top=38,bot=112;
  return `<svg viewBox="0 0 200 150" class="q-svg"><rect x="${cx-rx}" y="${top}" width="${rx*2}" height="${bot-top}" fill="#dcfce7"/><line x1="${cx-rx}" y1="${top}" x2="${cx-rx}" y2="${bot}" stroke="${C.gm}" stroke-width="2"/><line x1="${cx+rx}" y1="${top}" x2="${cx+rx}" y2="${bot}" stroke="${C.gm}" stroke-width="2"/><ellipse cx="${cx}" cy="${bot}" rx="${rx}" ry="${ry}" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/><ellipse cx="${cx}" cy="${top}" rx="${rx}" ry="${ry}" fill="#eafaf0" stroke="${C.gm}" stroke-width="2"/></svg>`;}
function cone(){const cx=100,rx=34,ry=11,bot=112,apex=34;
  return `<svg viewBox="0 0 200 150" class="q-svg"><path d="M${cx-rx} ${bot} L${cx} ${apex} L${cx+rx} ${bot} Z" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/><path d="M${cx-rx} ${bot} A${rx} ${ry} 0 0 0 ${cx+rx} ${bot}" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/><ellipse cx="${cx}" cy="${bot}" rx="${rx}" ry="${ry}" fill="none" stroke="${C.gm}" stroke-width="1.4" stroke-dasharray="3 3"/></svg>`;}
function sphere(){
  return `<svg viewBox="0 0 200 150" class="q-svg"><circle cx="100" cy="74" r="42" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/><ellipse cx="100" cy="74" rx="42" ry="13" fill="none" stroke="${C.gm}" stroke-width="1.4" stroke-dasharray="3 3"/></svg>`;}
function pyramid(){
  return `<svg viewBox="0 0 200 150" class="q-svg"><polygon points="100,96 60,112 100,128 140,112" fill="#eafaf0" stroke="${C.gm}" stroke-width="1.6"/><polygon points="100,30 60,112 100,128" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/><polygon points="100,30 100,128 140,112" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/><line x1="100" y1="30" x2="100" y2="96" stroke="${C.gm}" stroke-width="1.2" stroke-dasharray="3 3"/></svg>`;}
function rightTri(a,b){const u=Math.min(115/a,78/b,15),pw=a*u,ph=b*u,ox=52,oy=118;
  return `<svg viewBox="0 0 200 150" class="q-svg"><polygon points="${ox},${oy} ${ox+pw},${oy} ${ox},${oy-ph}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2.2"/><rect x="${ox}" y="${oy-10}" width="10" height="10" fill="none" stroke="${C.gm}" stroke-width="1.2"/><text x="${ox+pw/2}" y="${oy+16}" text-anchor="middle" font-size="13" fill="#334" font-family="system-ui">${a}</text><text x="${ox-8}" y="${oy-ph/2}" text-anchor="end" font-size="13" fill="#334" font-family="system-ui">${b}</text><text x="${ox+pw/2+6}" y="${oy-ph/2-3}" font-size="14" font-weight="800" fill="${C.gm}" font-family="system-ui">?</text></svg>`;}
function mapping(pairs){
  const ins=[...new Set(pairs.map(p=>p[0]))],outs=[...new Set(pairs.map(p=>p[1]))],posIn={},posOut={},lx=66,rx=134;
  ins.forEach((v,i)=>posIn[v]=36+i*(90/Math.max(ins.length-1,1)));
  outs.forEach((v,i)=>posOut[v]=36+i*(90/Math.max(outs.length-1,1)));
  let s=`<svg viewBox="0 0 200 150" class="q-svg" style="max-height:160px"><defs><marker id="arw${clipN++}" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6.5 3 L0 6 z" fill="${C.af}"/></marker></defs>`;
  const mk='arw'+(clipN-1);
  s+=`<text x="${lx}" y="18" text-anchor="middle" font-size="11" fill="#556" font-family="system-ui">input</text><text x="${rx}" y="18" text-anchor="middle" font-size="11" fill="#556" font-family="system-ui">output</text>`;
  pairs.forEach(([a,b])=>s+=`<line x1="${lx+14}" y1="${posIn[a]}" x2="${rx-14}" y2="${posOut[b]}" stroke="${C.af}" stroke-width="1.7" marker-end="url(#${mk})"/>`);
  ins.forEach(v=>s+=`<circle cx="${lx}" cy="${posIn[v]}" r="13" fill="#ede9fe" stroke="${C.af}" stroke-width="1.8"/><text x="${lx}" y="${posIn[v]+4}" text-anchor="middle" font-size="12" font-weight="700" fill="${C.af}" font-family="system-ui">${v}</text>`);
  outs.forEach(v=>s+=`<circle cx="${rx}" cy="${posOut[v]}" r="13" fill="#f5f3ff" stroke="${C.af}" stroke-width="1.8"/><text x="${rx}" y="${posOut[v]+4}" text-anchor="middle" font-size="12" font-weight="700" fill="${C.af}" font-family="system-ui">${v}</text>`);
  return s+`</svg>`;}
function transform(kind){const X=v=>100+v*13.5,Y=v=>100-v*13.5,pre=[[1,1],[3,1],[1,4]];
  let img = kind==='translate'?pre.map(([x,y])=>[x+3,y]) : kind==='reflect'?pre.map(([x,y])=>[-x,y]) : kind==='rotate'?pre.map(([x,y])=>[-x,-y]) : pre.map(([x,y])=>[x*1.5,y*1.5]);
  const poly=(pts,fill,stroke,dash)=>`<polygon points="${pts.map(([x,y])=>X(x)+','+Y(y)).join(' ')}" fill="${fill}" stroke="${stroke}" stroke-width="2" ${dash?'stroke-dasharray="4 3"':''}/>`;
  let s=`<svg viewBox="0 0 200 200" class="q-svg" style="max-height:168px">`;
  s+=`<line x1="${X(-6)}" y1="${Y(0)}" x2="${X(6)}" y2="${Y(0)}" stroke="#cbd3df" stroke-width="1.2"/><line x1="${X(0)}" y1="${Y(-6)}" x2="${X(0)}" y2="${Y(6)}" stroke="#cbd3df" stroke-width="1.2"/>`;
  s+=poly(pre,'rgba(150,160,175,.16)','#9aa4b2',true)+poly(img,'#dcfce7',C.gm,false);
  return s+`</svg>`;}
    return { frac, txt, words, tableH, dots, ineq, point, linegraph, numline2, shaded, rect, triangle, parallelo, prism, dotplot, boxplot, scatter, spinner, circleShape, cylinder, cone, sphere, pyramid, rightTri, mapping, transform, __setClip: (n) => { clipN = n; } };
  }
  function build8() {
    const C = {ns:'#0d9488',rp:'#ea580c',af:'#7c3aed',gm:'#16a34a',ds:'#2563eb'};
    let clipN = 0;
    function frac(n,d){return `<span class="frac"><span class="n">${n}</span><span class="d">${d}</span></span>`;}
function txt(main,sub){return `<div class="q-text">${main}${sub?`<div class="q-sub">${sub}</div>`:''}</div>`;}
function words(s){return `<div class="q-text sm">${s}</div>`;}
function tableH(headers,rows){let s=`<table class="mini-table"><thead><tr>`+headers.map(h=>`<th>${h}</th>`).join('')+`</tr></thead><tbody>`;rows.forEach(r=>s+=`<tr>`+r.map(c=>`<td>${c}</td>`).join('')+`</tr>`);return s+`</tbody></table>`;}
function point(px,py,color){color=color||C.af;const min=-5,max=5,X=v=>100+v*15.5,Y=v=>100-v*15.5;let s=`<svg viewBox="0 0 200 200" class="q-svg" style="max-height:170px">`;for(let v=min;v<=max;v++){s+=`<line x1="${X(min)}" y1="${Y(v)}" x2="${X(max)}" y2="${Y(v)}" stroke="#eef1f6" stroke-width="1"/><line x1="${X(v)}" y1="${Y(min)}" x2="${X(v)}" y2="${Y(max)}" stroke="#eef1f6" stroke-width="1"/>`;}s+=`<line x1="${X(min)}" y1="${Y(0)}" x2="${X(max)}" y2="${Y(0)}" stroke="#334" stroke-width="1.6"/><line x1="${X(0)}" y1="${Y(min)}" x2="${X(0)}" y2="${Y(max)}" stroke="#334" stroke-width="1.6"/>`;s+=`<circle cx="${X(px)}" cy="${Y(py)}" r="6.5" fill="${color}"/>`;const lx=X(px)+(px<0?-7:7),ly=Y(py)+(py>0?-11:19);s+=`<text x="${lx}" y="${ly}" text-anchor="${px<0?'end':'start'}" font-size="15" font-weight="800" fill="${color}" font-family="system-ui">(${px}, ${py})</text>`;return s+`</svg>`;}
function linegraph(spec){const min=-6,max=6,X=v=>100+v*14.5,Y=v=>100-v*14.5,id='cl'+(clipN++);let s=`<svg viewBox="0 0 200 200" class="q-svg" style="max-height:172px">`;s+=`<defs><clipPath id="${id}"><rect x="${X(min)}" y="${Y(max)}" width="${X(max)-X(min)}" height="${Y(min)-Y(max)}"/></clipPath></defs>`;for(let v=min;v<=max;v++){s+=`<line x1="${X(min)}" y1="${Y(v)}" x2="${X(max)}" y2="${Y(v)}" stroke="#eef1f6" stroke-width="1"/><line x1="${X(v)}" y1="${Y(min)}" x2="${X(v)}" y2="${Y(max)}" stroke="#eef1f6" stroke-width="1"/>`;}s+=`<line x1="${X(min)}" y1="${Y(0)}" x2="${X(max)}" y2="${Y(0)}" stroke="#334" stroke-width="1.5"/><line x1="${X(0)}" y1="${Y(min)}" x2="${X(0)}" y2="${Y(max)}" stroke="#334" stroke-width="1.5"/>`;s+=`<g clip-path="url(#${id})">`;(spec.lines||[]).forEach(l=>{const col=l.color||C.af;if(l.vertical!==undefined){s+=`<line x1="${X(l.vertical)}" y1="${Y(min)}" x2="${X(l.vertical)}" y2="${Y(max)}" stroke="${col}" stroke-width="3"/>`;}else{const y1=l.m*min+l.b,y2=l.m*max+l.b;s+=`<line x1="${X(min)}" y1="${Y(y1)}" x2="${X(max)}" y2="${Y(y2)}" stroke="${col}" stroke-width="3" ${l.dashed?'stroke-dasharray="5 4"':''}/>`;}});(spec.curves||[]).forEach(c=>{const col=c.color||C.af;let pts='';for(let x=min;x<=max;x+=0.4){pts+=`${X(x)},${Y(c.a*x*x+(c.b||0))} `;}s+=`<polyline points="${pts}" fill="none" stroke="${col}" stroke-width="3"/>`;});(spec.points||[]).forEach(p=>s+=`<circle cx="${X(p.x)}" cy="${Y(p.y)}" r="4.5" fill="${p.color||C.ds}"/>`);return s+`</g></svg>`;}
function numline2(a,b,min,max,color){color=color||C.ns;const X=v=>18+(v-min)/(max-min)*184;let s=`<svg viewBox="0 0 220 100" class="q-svg"><line x1="${X(min)}" y1="60" x2="${X(max)}" y2="60" stroke="#334" stroke-width="2"/>`;for(let v=min;v<=max;v++){s+=`<line x1="${X(v)}" y1="55" x2="${X(v)}" y2="65" stroke="#334" stroke-width="1.2"/><text x="${X(v)}" y="82" text-anchor="middle" font-size="10.5" fill="#556" font-family="system-ui">${v}</text>`;}const x1=Math.min(X(a),X(b)),x2=Math.max(X(a),X(b));s+=`<line x1="${x1}" y1="34" x2="${x2}" y2="34" stroke="${color}" stroke-width="2"/><line x1="${x1}" y1="34" x2="${x1}" y2="55" stroke="${color}" stroke-width="1.4"/><line x1="${x2}" y1="34" x2="${x2}" y2="55" stroke="${color}" stroke-width="1.4"/><text x="${(x1+x2)/2}" y="26" text-anchor="middle" font-size="13" font-weight="800" fill="${color}" font-family="system-ui">${Math.abs(a-b)}</text><circle cx="${X(a)}" cy="60" r="6" fill="${color}"/><circle cx="${X(b)}" cy="60" r="6" fill="${color}"/></svg>`;return s;}
function prism(w,h,d){const u=15,pw=w*u,ph=h*u,dx=d*8,dy=d*8,ox=60,oyB=118,oyT=oyB-ph;let s=`<svg viewBox="0 0 200 150" class="q-svg"><polygon points="${ox},${oyT} ${ox+pw},${oyT} ${ox+pw+dx},${oyT-dy} ${ox+dx},${oyT-dy}" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/><polygon points="${ox+pw},${oyT} ${ox+pw+dx},${oyT-dy} ${ox+pw+dx},${oyB-dy} ${ox+pw},${oyB}" fill="#86efac" stroke="${C.gm}" stroke-width="2"/><rect x="${ox}" y="${oyT}" width="${pw}" height="${ph}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/><text x="${ox+pw/2}" y="${oyB+16}" text-anchor="middle" font-size="12.5" fill="#334" font-family="system-ui">${w}</text><text x="${ox-7}" y="${oyT+ph/2+4}" text-anchor="end" font-size="12.5" fill="#334" font-family="system-ui">${h}</text><text x="${ox+pw+dx/2+5}" y="${oyT-dy/2-2}" font-size="12.5" fill="#334" font-family="system-ui">${d}</text></svg>`;return s;}
function scatter(kind){const data={pos:[[1,1.5],[2,2],[3,3.2],[4,3.4],[5,4.8],[6,5.4],[7,7],[8,7.6]],neg:[[1,7.6],[2,7],[3,5.5],[4,5],[5,3.8],[6,3],[7,2.2],[8,1.4]],none:[[1,5],[2,2],[3,7],[4,3.2],[5,6],[6,2.4],[7,7.5],[8,4]],nonlinear:[[1,7],[2,4.4],[3,2.4],[4,1.5],[5,1.6],[6,2.7],[7,4.7],[8,7.2]]}[kind];const X=v=>26+v/9*168,Y=v=>96-v/9*84;let s=`<svg viewBox="0 0 210 120" class="q-svg"><line x1="24" y1="12" x2="24" y2="98" stroke="#334" stroke-width="1.4"/><line x1="24" y1="98" x2="202" y2="98" stroke="#334" stroke-width="1.4"/>`;data.forEach(([x,y])=>s+=`<circle cx="${X(x)}" cy="${Y(y)}" r="3.6" fill="${C.ds}"/>`);return s+`</svg>`;}
function spinner(fr){const cx=100,cy=70,r=44,ang=fr*2*Math.PI,large=fr>0.5?1:0,ex=cx+r*Math.sin(ang),ey=cy-r*Math.cos(ang);let s=`<svg viewBox="0 0 200 150" class="q-svg">`;s+= fr>=1?`<circle cx="${cx}" cy="${cy}" r="${r}" fill="#c7d2fe"/>`:`<path d="M${cx} ${cy} L${cx} ${cy-r} A${r} ${r} 0 ${large} 1 ${ex} ${ey} Z" fill="#c7d2fe"/>`;s+=`<circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${C.ds}" stroke-width="2.4"/><line x1="${cx}" y1="${cy}" x2="${cx+r*0.7}" y2="${cy-r*0.55}" stroke="#1f2430" stroke-width="2.4"/><circle cx="${cx}" cy="${cy}" r="3.5" fill="#1f2430"/></svg>`;return s;}
function cylinder(){const cx=100,rx=34,ry=11,top=38,bot=112;return `<svg viewBox="0 0 200 150" class="q-svg"><rect x="${cx-rx}" y="${top}" width="${rx*2}" height="${bot-top}" fill="#dcfce7"/><line x1="${cx-rx}" y1="${top}" x2="${cx-rx}" y2="${bot}" stroke="${C.gm}" stroke-width="2"/><line x1="${cx+rx}" y1="${top}" x2="${cx+rx}" y2="${bot}" stroke="${C.gm}" stroke-width="2"/><ellipse cx="${cx}" cy="${bot}" rx="${rx}" ry="${ry}" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/><ellipse cx="${cx}" cy="${top}" rx="${rx}" ry="${ry}" fill="#eafaf0" stroke="${C.gm}" stroke-width="2"/></svg>`;}
function cone(){const cx=100,rx=34,ry=11,bot=112,apex=34;return `<svg viewBox="0 0 200 150" class="q-svg"><path d="M${cx-rx} ${bot} L${cx} ${apex} L${cx+rx} ${bot} Z" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/><path d="M${cx-rx} ${bot} A${rx} ${ry} 0 0 0 ${cx+rx} ${bot}" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/><ellipse cx="${cx}" cy="${bot}" rx="${rx}" ry="${ry}" fill="none" stroke="${C.gm}" stroke-width="1.4" stroke-dasharray="3 3"/></svg>`;}
function sphere(){return `<svg viewBox="0 0 200 150" class="q-svg"><circle cx="100" cy="74" r="42" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/><ellipse cx="100" cy="74" rx="42" ry="13" fill="none" stroke="${C.gm}" stroke-width="1.4" stroke-dasharray="3 3"/></svg>`;}
function pyramid(){return `<svg viewBox="0 0 200 150" class="q-svg"><polygon points="100,96 60,112 100,128 140,112" fill="#eafaf0" stroke="${C.gm}" stroke-width="1.6"/><polygon points="100,30 60,112 100,128" fill="#dcfce7" stroke="${C.gm}" stroke-width="2"/><polygon points="100,30 100,128 140,112" fill="#bbf7d0" stroke="${C.gm}" stroke-width="2"/><line x1="100" y1="30" x2="100" y2="96" stroke="${C.gm}" stroke-width="1.2" stroke-dasharray="3 3"/></svg>`;}
function rightTri(a,b){const u=Math.min(115/a,78/b,15),pw=a*u,ph=b*u,ox=52,oy=118;return `<svg viewBox="0 0 200 150" class="q-svg"><polygon points="${ox},${oy} ${ox+pw},${oy} ${ox},${oy-ph}" fill="#dcfce7" stroke="${C.gm}" stroke-width="2.2"/><rect x="${ox}" y="${oy-10}" width="10" height="10" fill="none" stroke="${C.gm}" stroke-width="1.2"/><text x="${ox+pw/2}" y="${oy+16}" text-anchor="middle" font-size="13" fill="#334" font-family="system-ui">${a}</text><text x="${ox-8}" y="${oy-ph/2}" text-anchor="end" font-size="13" fill="#334" font-family="system-ui">${b}</text><text x="${ox+pw/2+6}" y="${oy-ph/2-3}" font-size="14" font-weight="800" fill="${C.gm}" font-family="system-ui">?</text></svg>`;}
function mapping(pairs){const ins=[...new Set(pairs.map(p=>p[0]))],outs=[...new Set(pairs.map(p=>p[1]))],posIn={},posOut={},lx=66,rx=134;ins.forEach((v,i)=>posIn[v]=36+i*(90/Math.max(ins.length-1,1)));outs.forEach((v,i)=>posOut[v]=36+i*(90/Math.max(outs.length-1,1)));const mk='arw'+(clipN++);let s=`<svg viewBox="0 0 200 150" class="q-svg" style="max-height:160px"><defs><marker id="${mk}" markerWidth="8" markerHeight="8" refX="6.5" refY="3" orient="auto"><path d="M0 0 L6.5 3 L0 6 z" fill="${C.af}"/></marker></defs>`;s+=`<text x="${lx}" y="18" text-anchor="middle" font-size="11" fill="#556" font-family="system-ui">input</text><text x="${rx}" y="18" text-anchor="middle" font-size="11" fill="#556" font-family="system-ui">output</text>`;pairs.forEach(([a,b])=>s+=`<line x1="${lx+14}" y1="${posIn[a]}" x2="${rx-14}" y2="${posOut[b]}" stroke="${C.af}" stroke-width="1.7" marker-end="url(#${mk})"/>`);ins.forEach(v=>s+=`<circle cx="${lx}" cy="${posIn[v]}" r="13" fill="#ede9fe" stroke="${C.af}" stroke-width="1.8"/><text x="${lx}" y="${posIn[v]+4}" text-anchor="middle" font-size="12" font-weight="700" fill="${C.af}" font-family="system-ui">${v}</text>`);outs.forEach(v=>s+=`<circle cx="${rx}" cy="${posOut[v]}" r="13" fill="#f5f3ff" stroke="${C.af}" stroke-width="1.8"/><text x="${rx}" y="${posOut[v]+4}" text-anchor="middle" font-size="12" font-weight="700" fill="${C.af}" font-family="system-ui">${v}</text>`);return s+`</svg>`;}
function transform(kind){const X=v=>100+v*13.5,Y=v=>100-v*13.5,pre=[[1,1],[3,1],[1,4]];let img=kind==='translate'?pre.map(([x,y])=>[x+3,y]):kind==='reflect'?pre.map(([x,y])=>[-x,y]):kind==='rotate'?pre.map(([x,y])=>[-x,-y]):pre.map(([x,y])=>[x*1.5,y*1.5]);const poly=(pts,fill,stroke,dash)=>`<polygon points="${pts.map(([x,y])=>X(x)+','+Y(y)).join(' ')}" fill="${fill}" stroke="${stroke}" stroke-width="2" ${dash?'stroke-dasharray="4 3"':''}/>`;let s=`<svg viewBox="0 0 200 200" class="q-svg" style="max-height:168px"><line x1="${X(-6)}" y1="${Y(0)}" x2="${X(6)}" y2="${Y(0)}" stroke="#cbd3df" stroke-width="1.2"/><line x1="${X(0)}" y1="${Y(-6)}" x2="${X(0)}" y2="${Y(6)}" stroke="#cbd3df" stroke-width="1.2"/>`;s+=poly(pre,'rgba(150,160,175,.16)','#9aa4b2',true)+poly(img,'#dcfce7',C.gm,false);return s+`</svg>`;}
    return { frac, txt, words, tableH, point, linegraph, numline2, prism, scatter, spinner, cylinder, cone, sphere, pyramid, rightTri, mapping, transform, __setClip: (n) => { clipN = n; } };
  }
  return { 6: build6(), 7: build7(), 8: build8() };
})();

function _render(funcs, spec) {
  const args = (spec && spec.args ? spec.args : []).map((a) =>
    a && typeof a === "object" && a.t ? _render(funcs, a) : a
  );
  const fn = funcs[spec.t];
  if (!fn) throw new Error("wodb: no renderer '" + spec.t + "'");
  return fn(...args);
}

// seed makes any generated SVG ids (clip-paths/markers) deterministic per
// box AND collision-free across boxes, so SSR and client hydration match.
function renderBox(grade, spec, seed) {
  const funcs = TABLES[grade] || TABLES[6];
  if (typeof seed === "number" && funcs.__setClip) funcs.__setClip(seed);
  return _render(funcs, spec);
}

export { renderBox };
