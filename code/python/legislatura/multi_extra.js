// token di periodo tradotti (usati da Lc)
function trTok(v){if(typeof LANG==='undefined'||LANG==='it')return v;const m=String(v).match(/^(?:(\d{4})–(\d{4}), intera legislatura|manovre (\d{4})–(\d{4})|manovra (\d{4}))(?: · (Camera|Senato))?$/);if(!m)return v;
  const W={en:{leg:'{0}–{1}, whole legislature',many:'{0}–{1} budgets',one:'{0} budget',Camera:'Chamber',Senato:'Senate'},es:{leg:'{0}–{1}, toda la legislatura',many:'presupuestos {0}–{1}',one:'presupuesto {0}',Camera:'Cámara',Senato:'Senado'},fr:{leg:'{0}–{1}, toute la législature',many:'budgets {0}–{1}',one:'budget {0}',Camera:'Chambre',Senato:'Sénat'}}[LANG];if(!W)return v;
  const f=(t,a,b)=>t.replace('{0}',a).replace('{1}',b);let o=m[1]?f(W.leg,m[1],m[2]):m[3]?f(W.many,m[3],m[4]):f(W.one,m[5]);if(m[6])o+=' · '+W[m[6]];return o}
// ---------- legislatura: quadro, studio, fonti ----------
const cssv=n=>getComputedStyle(document.body).getPropertyValue(n).trim();
const SELY=()=>YEARS.filter(y=>y>=PA&&y<=PB);
const pf=(x,d=1)=>Number(x).toLocaleString(LOC(),{minimumFractionDigits:d,maximumFractionDigits:d}).replace(/^-/,'−');
const LETT={'2023|Camera':1,'2023|Senato':2,'2024|Senato':1,'2024|Camera':2,'2025|Camera':1,'2025|Senato':2,'2026|Senato':1,'2026|Camera':2,'2027|Camera':1};
function svgEl(svg,tag,at,txt){const e=document.createElementNS('http://www.w3.org/2000/svg',tag);for(const k in at)e.setAttribute(k,at[k]);if(txt!=null)e.textContent=txt;svg.appendChild(e);return e}
function renderQuadro(){
  if(!D||$('#view-quadro').hidden&&renderQuadro._done===PA+'-'+PB+PRA)return;renderQuadro._done=PA+'-'+PB+PRA;
  const tot=D.length,ap=D.filter(r=>r.o==='A').length,inam=D.filter(r=>r.o==='I').length;
  const voted=D.filter(r=>r.le===1&&r.y<2027);const rate=s=>{const x=voted.filter(r=>s(r.c));return x.length?x.filter(r=>r.o==='A').length/x.length*100:NaN};
  const rm=rate(c=>c==='Maggioranza'),ro=rate(c=>c==='Opposizione');
  $('#qtiles').innerHTML=`<div class="tile acc"><b>${nf(tot)}</b><span>proposte di modifica · ${esc(perLab())}</span></div>`+
   `<div class="tile"><b style="color:var(--ok)">${nf(ap)}</b><span>approvate (${pc(ap,tot)})</span></div>`+
   `<div class="tile bad"><b>${nf(inam)}</b><span>dichiarate inammissibili (${pc(inam,tot)})</span></div>`+
   `<div class="tile"><b>${isNaN(rm)?'—':pf(rm)+'% · '+pf(ro)+'%'}</b><span>${isNaN(rm)?'nessuna prima lettura già votata nel periodo':'approvate in prima lettura: maggioranza · opposizione'}</span></div>`;
  // barre per manovra × ramo
  const keys=[];SELY().forEach(y=>['Camera','Senato'].forEach(ra=>{if(LETT[y+'|'+ra]&&(!PRA||PRA===ra))keys.push([y,ra])}));
  const svg=$('#qbars');svg.innerHTML='';const W=900,lw=190,rh=30,top=8,H=top+keys.length*rh+28;svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const cnt=keys.map(([y,ra])=>{const x=D.filter(r=>r.y===y&&r.ra===ra);return {y,ra,n:x.length,A:x.filter(r=>r.o==='A').length,I:x.filter(r=>r.o==='I').length,R:x.filter(r=>r.o==='R').length,N:x.filter(r=>r.o==='N').length}});
  const mx=Math.max(1,...cnt.map(c=>c.n)),sx=v=>v/mx*(W-lw-80);
  const COL={A:'var(--ok)',I:'var(--bad)',R:'var(--warn)',N:'var(--line)'};
  cnt.forEach((c,i)=>{const yy=top+i*rh;svgEl(svg,'text',{x:0,y:yy+18,class:'lab'},`${c.y} · ${c.ra} · ${LETT[c.y+'|'+c.ra]===1?'1ª':'2ª'} lett.`);let x0=lw;
    ['A','I','R','N'].forEach(k=>{const w=sx(c[k]);if(w<=0)return;const r=svgEl(svg,'rect',{x:x0,y:yy+5,width:Math.max(w-1,1),height:rh-10,rx:2});r.style.fill=COL[k];svgEl(r,'title',{},`${c.y} ${c.ra}: ${nf(c[k])} ${{A:'approvate',I:'inammissibili',R:'ritirate',N:'respinte o non votate'}[k]}`);x0+=w});
    svgEl(svg,'text',{x:x0+6,y:yy+18},nf(c.n)+(c.A?' · '+nf(c.A)+' appr.':''))});
  $('#qtab').innerHTML='<thead><tr><th>Manovra</th><th>Ramo</th><th>Lettura</th><th style="text-align:right">Proposte</th><th style="text-align:right">Inammissibili</th><th style="text-align:right">Ritirate</th><th style="text-align:right">Approvate</th></tr></thead><tbody>'+
    cnt.map(c=>`<tr><td>${c.y}</td><td>${c.ra}</td><td>${LETT[c.y+'|'+c.ra]===1?'prima':'seconda'}</td><td class="n">${nf(c.n)}</td><td class="n">${nf(c.I)} <span class="meta">${pc(c.I,c.n)}</span></td><td class="n">${nf(c.R)}</td><td class="n"><b>${nf(c.A)}</b> <span class="meta">${pc(c.A,c.n)}</span></td></tr>`).join('')+'</tbody>';
  // schieramenti
  const CO=['Maggioranza','Opposizione','Governo','Misto'];const hb=(sel,data,fmt)=>{const s=$(sel);s.innerHTML='';const lw2=130,rh2=40,W2=520;const m=Math.max(1e-9,...data.map(d=>d[1]||0));
    data.forEach(([k,v],i)=>{const y=8+i*rh2;svgEl(s,'text',{x:0,y:y+20,class:'lab'},k);const r=svgEl(s,'rect',{x:lw2,y:y+6,width:Math.max(1,(v||0)/m*(W2-lw2-90)),height:rh2-16,rx:3});r.style.fill=k==='Maggioranza'?'#257de0':k==='Opposizione'?'#ec4647':'var(--muted)';svgEl(s,'text',{x:lw2+(v||0)/m*(W2-lw2-90)+6,y:y+20},isNaN(v)?'—':fmt(v))})};
  const apr=D.filter(r=>r.o==='A');hb('#qcoal',CO.map(c=>[c,apr.filter(r=>r.c===c).length]),v=>nf(v));
  hb('#qrate',['Maggioranza','Opposizione'].map(c=>[c,rate(x=>x===c)]),v=>pf(v)+'%');
  // partiti
  renderQParty();renderMoney();
}
const COAL=[['Centrodestra',['FdI','Lega','FI','Noi Moderati']],['Campo largo',['PD','M5S','AVS','IV']],['Azione',['Azione']],['Altri gruppi',['Autonomie','Misto']],['Governo e relatori',['Governo']]];
function renderMoney(){if(!D||!$('#qmtab'))return;
  if(!renderMoney._b){renderMoney._b=1;['qme','qmd'].forEach(id=>$('#'+id).onchange=renderMoney)}
  const es=$('#qme').value,dd=$('#qmd').value==='1';
  let X=D.filter(r=>es===''||(es==='A'&&r.o==='A')||(es==='M'&&r.s==='Ammissibile')||(es==='I'&&r.s!=='Ammissibile'));
  const nAll=X.length;let dup=0;
  if(dd){const seen=new Set();X=X.slice().sort((a,b)=>a._k<b._k?-1:1).filter(r=>{if(!r.h)return true;const k=r.y+'|'+r.ra+'|'+r.h;if(seen.has(k)){dup++;return false}seen.add(k);return true})}
  const st=a=>{const w=a.filter(r=>AMT(r)>0);return {n:a.length,nw:w.length,eur:a.reduce((s,r)=>s+AMT(r),0),loc:a.filter(r=>r.pm.length).reduce((s,r)=>s+AMT(r),0),ap:a.filter(r=>r.o==='A').reduce((s,r)=>s+AMT(r),0)}};
  const tot=st(X);const mx=Math.max(1,...COAL.flatMap(([c,ps])=>ps.map(p=>st(X.filter(r=>r.pa===p)).eur)));
  const bar=(v,c)=>`<span class="qmbar"><i style="width:${(v/mx*100).toFixed(1)}%;background:${c}"></i></span>`;
  const row=(lab,S,cls,col)=>`<tr class="${cls}"><td>${col?`<i class="qdot" style="background:${col}"></i>`:''}${esc(lab)}</td><td class="n">${nf(S.n)}</td><td class="n">${nf(S.nw)}</td><td class="n"><b>${fmtE(S.eur)}</b>${cls==='pa'?bar(S.eur,col||'var(--muted)'):''}</td><td class="n">${tot.eur?pf(S.eur/tot.eur*100)+'%':'—'}</td><td class="n">${fmtE(S.loc)}</td><td class="n">${fmtE(S.ap)}</td></tr>`;
  let h='<thead><tr><th>Partito o coalizione</th><th style="text-align:right">Proposte</th><th style="text-align:right">Con una cifra</th><th style="text-align:right">Euro chiesti nel triennio</th><th style="text-align:right">Quota del totale</th><th style="text-align:right">Di cui per luoghi precisi</th><th style="text-align:right">Di cui approvati</th></tr></thead><tbody>';
  let sumP=0,sumN=0;
  COAL.forEach(([c,ps])=>{const Y=X.filter(r=>ps.includes(r.pa));if(!Y.length)return;h+=row(c+(ps.length>1?' ('+ps.join(', ')+')':''),st(Y),'co');if(ps.length>1)ps.forEach(p=>{const Z=X.filter(r=>r.pa===p);if(!Z.length)return;const S=st(Z);sumP+=S.eur;sumN+=S.n;h+=row(p,S,'pa',(p==='IV'?'#16a394':p==='Azione'?PCOL['Azione / IV']:PCOL[p])||'var(--muted)')});else{const S=st(Y);sumP+=S.eur;sumN+=S.n}});
  h+=row('Totale',tot,'tot');h+='</tbody>';$('#qmtab').innerHTML=h;
  const ok=Math.abs(sumP-tot.eur)<1&&sumN===tot.n;
  $('#qmchk').textContent=Lf('Controllo: la somma dei partiti fa {0} su {1} proposte, uguale al totale.',fmtE(sumP),nf(sumN))+(ok?'':' ⚠')+(dd?' '+Lf('Le proposte con lo stesso testo nella stessa manovra e nello stesso ramo sono contate una volta: {0} doppioni tolti su {1}.',nf(dup),nf(nAll)):'');
  const top=X.filter(r=>AMT(r)>0).sort((a,b)=>AMT(b)-AMT(a)).slice(0,10);
  $('#qmtop').innerHTML=top.map(r=>`<li><b>${fmtE(AMT(r))}</b> · ${esc(r.t)} <span class="meta">— ${esc(r.p)} (${esc(r.pa)}), ${r.y} · ${esc(r.ra)} ${esc(r.i)} · ${r.s==='Ammissibile'?esc(OLAB[r.o]):'inammissibile'}</span> <button class="btn sm" type="button" data-qmk="${esc(r.y+'|'+r.ra+'|'+r.i)}">${L('Apri')}</button></li>`).join('');
  document.querySelectorAll('[data-qmk]').forEach(b=>b.onclick=()=>{const [y,ra,i]=b.dataset.qmk.split('|');const r=D.find(x=>x.y==y&&x.ra===ra&&x.i===i);setOnly({q:i+' '+r.p.split(' ')[0].toLowerCase(),fy:y});})}
let QPS='n',QPD=-1;
function renderQParty(){if(!D)return;
  if(!renderQParty._b){renderQParty._b=1;$('#qps').onchange=()=>{QPS=$('#qps').value;QPD=QPS==='g'?1:-1;renderQParty()};$('#qpy').onchange=()=>renderQParty()}
  const ys=SELY().filter(y=>D.some(r=>r.y===y));const GS=ORDER.filter(g=>D.some(r=>r.g===g));const yv=$('#qpy').value;
  const st=a=>{const n=a.length,ap=a.filter(r=>r.o==='A').length,ia=a.filter(r=>r.s!=='Ammissibile').length,lo=a.filter(r=>r.loc);return {n,ap,ia,pap:n?ap/n*100:NaN,pia:n?ia/n*100:NaN,pam:n?(n-ia)/n*100:NaN,lo:lo.length,plo:n?lo.length/n*100:NaN,eur:lo.reduce((x,r)=>x+AMT(r),0)}};
  const T=GS.map(g=>{const x=D.filter(r=>r.g===g);return {g,S:st(x),Y:ys.map(y=>st(x.filter(r=>r.y===y)))}});
  const key=o=>o.S[QPS];T.sort((a,b)=>QPS==='g'?(ORDER.indexOf(a.g)-ORDER.indexOf(b.g))*-QPD:((isNaN(key(b))?-1:key(b))-(isNaN(key(a))?-1:key(a)))*-QPD||b.S.n-a.S.n);
  const p1=v=>isNaN(v)?'—':pf(v)+'%';
  const ycell=Y=>yv==='none'?'':yv==='pap'?`<td class="n">${Y.n?p1(Y.pap):'—'}</td>`:yv==='pia'?`<td class="n">${Y.n?p1(Y.pia):'—'}</td>`:`<td class="n">${nf(Y.n)} · <b>${nf(Y.ap)}</b></td>`;
  const th=(k,lab,al)=>`<th data-qs="${k}" class="qs${QPS===k?' on':''}" style="text-align:${al||'right'};cursor:pointer" aria-sort="${QPS===k?(QPD<0?'descending':'ascending'):'none'}">${lab}</th>`;
  $('#qparty').innerHTML='<thead><tr>'+th('g','Partito','left')+(yv==='none'?'':ys.map(y=>`<th style="text-align:right">${y}</th>`).join(''))+th('n','Proposte')+th('pap','Approvate')+th('pia','Inammissibili')+th('plo','Per un solo territorio')+th('eur','Euro chiesti per territori')+'</tr></thead><tbody>'+
    T.map(({g,S,Y})=>`<tr><td style="white-space:nowrap"><i class="qdot" style="background:${PCOL[g]||'var(--muted)'}"></i><button class="who" type="button" data-qg="${esc(g)}">${esc(g)}</button></td>${Y.map(ycell).join('')}<td class="n"><b>${nf(S.n)}</b></td><td class="n">${nf(S.ap)} <span class="meta">${p1(S.pap)}</span></td><td class="n">${nf(S.ia)} <span class="meta">${p1(S.pia)}</span></td><td class="n">${nf(S.lo)} <span class="meta">${p1(S.plo)}</span></td><td class="n">${fmtE(S.eur)}</td></tr>`).join('')+'</tbody>';
  document.querySelectorAll('[data-qg]').forEach(b=>b.onclick=()=>setOnly({fg:b.dataset.qg,fo:'A'}));
  document.querySelectorAll('#qparty th[data-qs]').forEach(h=>h.onclick=()=>{const k=h.dataset.qs;if(QPS===k)QPD=-QPD;else{QPS=k;QPD=k==='g'?1:-1}$('#qps').value=QPS;renderQParty()});
}

function coefPlot(svg,items,lab){svg.innerHTML='';const W=640,ml=150,mr=20,mt=12,mb=34,rh=34,NR=items.reduce((m,d,i)=>Math.max(m,(d.row??i)+1),0),H=mt+mb+rh*NR;svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const lo=Math.min(-5,...items.map(d=>d.b-1.96*d.se)),hi=Math.max(5,...items.map(d=>d.b+1.96*d.se));const X=v=>ml+(v-lo)/(hi-lo)*(W-ml-mr);
  const step=(hi-lo)>60?20:(hi-lo)>25?10:5;for(let t=Math.ceil(lo/step)*step;t<=hi;t+=step){const l=svgEl(svg,'line',{x1:X(t),x2:X(t),y1:mt,y2:H-mb,class:t===0?'ax':'gr'});if(t===0)l.style.stroke='var(--fg)';svgEl(svg,'text',{x:X(t),y:H-mb+15,'text-anchor':'middle'},pf(t,0))}
  svgEl(svg,'text',{x:(ml+W-mr)/2,y:H-4,'text-anchor':'middle'},lab);
  items.forEach((d,i)=>{const yy=mt+(d.row??i)*rh+rh/2+(d.dy||0);const c=d.col||'var(--accent)';const l=svgEl(svg,'line',{x1:X(d.b-1.96*d.se),x2:X(d.b+1.96*d.se),y1:yy,y2:yy,'stroke-width':2});l.style.stroke=c;
    const ci=svgEl(svg,'circle',{cx:X(d.b),cy:yy,r:5,'stroke-width':2});ci.style.stroke=c;ci.style.fill=d.hollow?'var(--surface)':c;svgEl(ci,'title',{},`${d.t}: ${pf(d.b)} (e.s. ${pf(d.se)})`);
    if(d.lab)svgEl(svg,'text',{x:0,y:yy+4,class:'lab'},d.lab)})}
let PANEL=null,panLoading=false;
const MAJ_P=['FdI','Lega','FI','Noi Moderati'];
function quintStats(){const ys=SELY();const by={};PANEL.rows.forEach(r=>{(by[r[2]]=by[r[2]]||{})[r[0]]=r[4]});
  const qOf={};for(const g in by){const ps=Object.keys(by[g]).sort((a,b)=>by[g][a]-by[g][b]);ps.forEach((p,i)=>{qOf[g+'|'+p]=Math.min(4,Math.floor(i*5/ps.length))})}
  const A={maj:[0,0,0,0,0].map(()=>[0,0]),opp:[0,0,0,0,0].map(()=>[0,0]),all:[0,0,0,0,0].map(()=>[0,0])};let n=0;
  PANEL.rows.forEach(r=>{if(!ys.includes(r[3]))return;const q=qOf[r[2]+'|'+r[0]];const k=MAJ_P.includes(r[2])?'maj':'opp';[k,'all'].forEach(z=>{A[z][q][0]+=r[5];A[z][q][1]++});n++});
  const pc=x=>x[1]?x[0]/x[1]*100:NaN;return {maj:A.maj.map(pc),opp:A.opp.map(pc),all:A.all.map(pc),n}}
function descPlot(Q){const s=$('#adesc');s.innerHTML='';const W=640,H=300,ml=46,mr=12,mt=26,mb=40;const mx=Math.max(5,...Q.maj,...Q.opp)*1.15;const Y=v=>mt+(1-v/mx)*(H-mt-mb);const gw=(W-ml-mr)/5,bw=gw*0.32;
  const step=mx>40?10:5;for(let t=0;t<=mx;t+=step){svgEl(s,'line',{x1:ml,x2:W-mr,y1:Y(t),y2:Y(t),class:t===0?'ax':'gr'});svgEl(s,'text',{x:ml-6,y:Y(t)+4,'text-anchor':'end'},pf(t,0)+'%')}
  const labs=['quinto più debole','2°','3°','4°','quinto più forte'];
  [['maj','#2b5d9c','Partiti di maggioranza'],['opp','#c0392b','Partiti di opposizione']].forEach(([k,c,lab],j)=>{Q[k].forEach((v,q)=>{if(isNaN(v))return;const x=ml+q*gw+gw/2+(j?2:-2-bw);const r=svgEl(s,'rect',{x,y:Y(v),width:bw,height:Math.max(1,Y(0)-Y(v)),rx:3});r.style.fill=c;svgEl(r,'title',{},lab+': '+pf(v)+'%');svgEl(s,'text',{x:x+bw/2,y:Y(v)-4,'text-anchor':'middle',class:'vlab'},pf(v,0)+'%')})});
  labs.forEach((l,q)=>svgEl(s,'text',{x:ml+q*gw+gw/2,y:H-mb+16,'text-anchor':'middle'},(q===0||q===4)?L(l):l));
  svgEl(s,'text',{x:(ml+W-mr)/2,y:H-mb+34,'text-anchor':'middle'},L('quinto di province secondo i voti 2022 del partito'));
  const lg=[['#2b5d9c','Partiti di maggioranza'],['#c0392b','Partiti di opposizione']];lg.forEach(([c,t],k)=>{const x=ml+8+k*210;const r=svgEl(s,'rect',{x,y:2,width:11,height:11,rx:2});r.style.fill=c;svgEl(s,'text',{x:x+16,y:12},L(t))})}
function renderAnalisi(){
  if(!AN||!PANEL){if(anLoading)return;anLoading=true;Promise.all([AN?AN:fetch('analisi_multi.json').then(r=>r.json()),PANEL?PANEL:fetch('panel_multi.json').then(r=>r.json())]).then(([a,p])=>{AN=a;PANEL=p;anLoading=false;renderAnalisi()}).catch(()=>{anLoading=false;$('#abrief').textContent='Non riesco a caricare i risultati.'});return}
  const K=PA+'-'+PB,Q=AN.ranges[K];if(!Q)return;const P=Q.pooled,Wn=Q.within,A=Q.approval;
  const sig=m=>Math.abs(m.b/m.se)>1.96;const PL=perLab();$('#aper').textContent=PL;$('#aper2').textContent=PL;
  const D5=quintStats();$('#anobs').textContent=Lf('{0} (109 province × 8 partiti × {1})',nf(D5.n),SELY().length===1?L('1 manovra'):Lf('{0} manovre',SELY().length));
  descPlot(D5);
  const a=D5.all;$('#adescp').textContent=Lf('In media, nel quinto di province dove il partito è più forte c’è una richiesta nel {0}% dei casi, nel quinto dove è più debole nel {1}%. La differenza è più marcata per l’opposizione ({2}% contro {3}%) che per la maggioranza ({4}% contro {5}%).',pf(a[4]),pf(a[0]),pf(D5.opp[4]),pf(D5.opp[0]),pf(D5.maj[4]),pf(D5.maj[0]));
  let h='<ol>'+'<li>'+Lf('<b>Dove un partito è più forte, chiede più spesso soldi per quella provincia:</b> {0}% dei casi nel quinto di province più favorevole, {1}% in quello meno favorevole.',pf(a[4]),pf(a[0]))+'</li>';
  h+='<li>'+(sig(Wn)?Lf('<b>Il legame resta confrontando province della stessa regione</b> per lo stesso partito, ma è più piccolo: {0} punti per 10 punti di voto, contro {1} nel confronto tra tutte le province.',pf(Wn.b),pf(P.b)):Lf('<b>Confrontando solo province della stessa regione il legame si riduce e non è più distinguibile dal caso</b> ({0} punti, errore standard {1}): buona parte del legame è una differenza tra regioni.',pf(Wn.b),pf(Wn.se)))+'</li>';
  if(A)h+='<li>'+Lf('<b>Per far approvare una proposta conta soprattutto chi la firma.</b> Una proposta dell’opposizione passa nel {0}% dei casi; una della maggioranza ha {1} punti in più.',pf(A.base),pf(A.mag.b))+'</li>';
  h+='</ol>';$('#abrief').innerHTML=h;
  const cell=m=>m?`<td>${pf(m.b,2)}${stars(m.b,m.se)}</td>`:'<td>—</td>',cse=m=>m?`<td>(${pf(m.se,2)})</td>`:'<td></td>';
  $('#atab').innerHTML=`<thead><tr><th></th><th>(1)</th><th>(2)</th><th>(3)</th></tr><tr><th>Confronto</th><th>${L('Tutte le province')}</th><th>${L('Province della stessa regione')}</th><th>${L('Stessa regione, stesso partito')}</th></tr></thead><tbody>
  <tr><td>${L('Voti 2022 (+10 punti)')}</td>${cell(Q.nofe)}${cell(P)}${cell(Wn)}</tr><tr class="se"><td></td>${cse(Q.nofe)}${cse(P)}${cse(Wn)}</tr>
  <tr class="sep"><td>${L('Effetti fissi')}</td><td>${L('partito × manovra')}</td><td>${L('+ regione')}</td><td>${L('+ partito × regione')}</td></tr>
  <tr><td>${L('Media delle richieste (%)')}</td><td>${pf(Q.nofe.mean)}</td><td>${pf(P.mean)}</td><td>${pf(Wn.mean)}</td></tr>
  <tr><td>${L('Osservazioni · province')}</td><td>${nf(Q.nofe.n)} · ${Q.nofe.g}</td><td>${nf(P.n)} · ${P.g}</td><td>${nf(Wn.n)} · ${Wn.g}</td></tr></tbody>`;
  $('#anote').textContent=L('* p<0,05; ** p<0,01; *** p<0,001. La colonna 3 è la più prudente: confronta solo province della stessa regione per lo stesso partito.');
  $('#aptab').innerHTML=A?`<thead><tr><th></th><th>${L('Punti percentuali')}</th><th>${L('Errore standard')}</th></tr></thead><tbody>
  <tr><td>${L('Tasso di approvazione dell’opposizione')}</td><td>${pf(A.base,1)}%</td><td></td></tr>
  <tr><td>${L('Primo firmatario in maggioranza')}</td><td>+${pf(A.mag.b,1)}${stars(A.mag.b,A.mag.se)}</td><td>${pf(A.mag.se,1)}</td></tr>
  <tr><td>${L('Proposta per un solo territorio')}</td><td>${A.loc.b>=0?'+':''}${pf(A.loc.b,1)}${stars(A.loc.b,A.loc.se)}</td><td>${pf(A.loc.se,1)}</td></tr>
  <tr><td>${L('Proposte · primi firmatari')}</td><td>${nf(A.n)} · ${nf(A.g)}</td><td></td></tr></tbody>`:'<tbody><tr><td>'+L('Nessuna prima lettura già votata nel periodo scelto (la manovra 2027 non è ancora stata votata).')+'</td></tr></tbody>';
  if(AN.het){const hs=ORDER.filter(g=>AN.het[g]).map(g=>({t:g,lab:g,b:AN.het[g].b,se:AN.het[g].se,col:PCOL[g]}));coefPlot($('#ahet'),hs,L('punti percentuali per +10 punti di voto (intera legislatura)'));
    $('#ahetp').textContent=L(AN.het_txt||'');$('#ahetf').hidden=false}else $('#ahetf').hidden=true;
  if(AN.spec&&AN.spec.length){const S=AN.spec;const pos=S.filter(d=>d.b>0).length,sg=S.filter(d=>d.b/d.se>1.96).length;$('#arob').textContent=Lf('Rifacendo il conto in {0} modi diversi (campione, definizione di richiesta, confronto, misura del voto), {1} stime su {0} sono positive e {2} significative.',nf(S.length),nf(pos),nf(sg))}
  renderFonti();
}
$('#pcsv').onclick=async()=>{const m=$('#pcsvm');try{const P=await (await fetch('panel_multi.json')).json();const cell=v=>typeof v==='number'?String(v).replace('.',','):'"'+String(v).replace(/"/g,'""')+'"';const csv='﻿'+[P.cols.map(cell).join(';')].concat(P.rows.map(r=>r.map(cell).join(';'))).join('\r\n');
  await dlReady;if(DLNS){await DLNS.save({filename:'replica-manovre-2023-2027.csv',data:csv});m.textContent='Scaricato.'}else{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='replica-manovre-2023-2027.csv';a.click();m.textContent='Scaricato.'}}catch(e){m.textContent='Download non disponibile qui.'}};
function renderFonti(){if(!ALL)return;const S=[
 [2023,'Camera','C. 643-bis','prima','Elenco delle proposte con esito; testi delle proposte segnalate','https://documenti.camera.it/apps/emendamenti/getProposteEmendative.aspx?contenitorePortante=leg.19.eme.ac.643-bis&tipoSeduta=1&sedeEsame=referente&urnTestoRiferimento=urn:leg:19:643:bis:null:com:05:referente&tipoListaEmendamenti=1'],
 [2023,'Senato','S. 442','seconda','Fascicolo completo degli emendamenti in 5ª Commissione','https://www.senato.it/show-doc?leg=19&tipodoc=ListEmendc&id=56372&idoggetto=1368104'],
 [2024,'Senato','S. 926','prima','Fascicolo completo con esiti','https://www.senato.it/show-doc?leg=19&tipodoc=ListEmendc&id=57654&idoggetto=1395344'],
 [2024,'Camera','C. 1627','seconda','Fascicolo delle proposte presentate ed elenco esiti','https://documenti.camera.it/_dati/leg19/lavori/bollet/202312/emendamenti/html/05/1627/1627.htm'],
 [2025,'Camera','C. 2112-bis','prima','Fascicolo, elenchi per seduta con esiti, testi approvati','https://documenti.camera.it/_dati/leg19/lavori/bollet/202411/emendamenti/html/05/2112-bis/2112-bis.htm'],
 [2025,'Senato','S. 1330','seconda','Fascicolo completo degli emendamenti','https://www.senato.it/show-doc?leg=19&tipodoc=ListEmendc&id=58757&idoggetto=1441141'],
 [2026,'Senato','S. 1689','prima','Fascicolo completo con esiti','https://www.senato.it/show-doc?leg=19&tipodoc=ListEmendc&id=59654&idoggetto=1477272'],
 [2026,'Camera','C. 2750','seconda','Elenco delle proposte con esito; testi singoli','https://documenti.camera.it/apps/emendamenti/getProposteEmendative.aspx?contenitorePortante=leg.19.eme.ac.2750&tipoSeduta=1&sedeEsame=referente&urnTestoRiferimento=urn:leg:19:2750:null:null:com:05:referente&tipoListaEmendamenti=1'],
 [2027,'Camera','C. 3174-bis','prima','Fascicolo del 23 novembre 2026 ed elenco delle inammissibilità','https://documenti.camera.it/_dati/leg19/lavori/bollet/202611/emendamenti/html/05/3174-bis/3174-bis.htm']];
 $('#ftab').innerHTML='<thead><tr><th>Manovra</th><th>Ramo</th><th>Atto</th><th>Lettura</th><th>Documento</th><th style="text-align:right">Proposte</th></tr></thead><tbody>'+S.map(s=>`<tr><td>${s[0]}</td><td>${s[1]}</td><td>${s[2]}</td><td>${s[3]}</td><td><a href="${s[5]}" target="_blank" rel="noopener">${s[4]} ↗</a></td><td class="n">${nf(ALL.filter(r=>r.y===s[0]&&r.ra===s[1]).length)}</td></tr>`).join('')+'</tbody>'}
