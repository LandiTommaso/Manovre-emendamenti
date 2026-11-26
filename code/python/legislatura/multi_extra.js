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
  const ys=SELY().filter(y=>D.some(r=>r.y===y));const GS=ORDER.filter(g=>D.some(r=>r.g===g));
  $('#qparty').innerHTML='<thead><tr><th>Partito</th>'+ys.map(y=>`<th style="text-align:right">${y}</th>`).join('')+'<th style="text-align:right">Totale</th></tr></thead><tbody>'+
    GS.map(g=>{const x=D.filter(r=>r.g===g);const cell=a=>`<td class="n">${nf(a.length)} · <b>${nf(a.filter(r=>r.o==='A').length)}</b></td>`;return `<tr><td><button class="who" type="button" data-qg="${esc(g)}">${esc(g)}</button></td>${ys.map(y=>cell(x.filter(r=>r.y===y))).join('')}${cell(x)}</tr>`}).join('')+'</tbody>';
  document.querySelectorAll('[data-qg]').forEach(b=>b.onclick=()=>setOnly({fg:b.dataset.qg,fo:'A'}));
}
function coefPlot(svg,items,lab){svg.innerHTML='';const W=640,ml=150,mr=20,mt=12,mb=34,rh=34,NR=items.reduce((m,d,i)=>Math.max(m,(d.row??i)+1),0),H=mt+mb+rh*NR;svg.setAttribute('viewBox',`0 0 ${W} ${H}`);
  const lo=Math.min(-5,...items.map(d=>d.b-1.96*d.se)),hi=Math.max(5,...items.map(d=>d.b+1.96*d.se));const X=v=>ml+(v-lo)/(hi-lo)*(W-ml-mr);
  const step=(hi-lo)>60?20:(hi-lo)>25?10:5;for(let t=Math.ceil(lo/step)*step;t<=hi;t+=step){const l=svgEl(svg,'line',{x1:X(t),x2:X(t),y1:mt,y2:H-mb,class:t===0?'ax':'gr'});if(t===0)l.style.stroke='var(--fg)';svgEl(svg,'text',{x:X(t),y:H-mb+15,'text-anchor':'middle'},pf(t,0))}
  svgEl(svg,'text',{x:(ml+W-mr)/2,y:H-4,'text-anchor':'middle'},lab);
  items.forEach((d,i)=>{const yy=mt+(d.row??i)*rh+rh/2+(d.dy||0);const c=d.col||'var(--accent)';const l=svgEl(svg,'line',{x1:X(d.b-1.96*d.se),x2:X(d.b+1.96*d.se),y1:yy,y2:yy,'stroke-width':2});l.style.stroke=c;
    const ci=svgEl(svg,'circle',{cx:X(d.b),cy:yy,r:5,'stroke-width':2});ci.style.stroke=c;ci.style.fill=d.hollow?'var(--surface)':c;svgEl(ci,'title',{},`${d.t}: ${pf(d.b)} (e.s. ${pf(d.se)})`);
    if(d.lab)svgEl(svg,'text',{x:0,y:yy+4,class:'lab'},d.lab)})}
function renderAnalisi(){
  if(!AN){if(anLoading)return;anLoading=true;fetch('analisi_multi.json').then(r=>r.json()).then(j=>{AN=j;anLoading=false;renderAnalisi()}).catch(()=>{anLoading=false;$('#abrief').textContent='Non riesco a caricare i risultati.'});return}
  const K=PA+'-'+PB,Q=AN.ranges[K];if(!Q)return;const P=Q.pooled,Wn=Q.within,Ap=Q.approved,A=Q.approval;
  const sig=m=>Math.abs(m.b/m.se)>1.96;const many=PA!==PB;const PL=perLab();
  $('#aper').textContent=PL;
  $('#ah2').textContent=(PL[0].toUpperCase()+PL.slice(1))+(sig(Wn)?': il voto del 2022 conta anche dentro la stessa regione':': i partiti chiedono dove sono forti, ma tra regioni');
  let h=`<ol><li><b>Dove un partito ha preso più voti nel 2022, chiede più spesso soldi per quella provincia.</b> Con 10 punti di voto in più la probabilità sale di ${pf(P.b)} punti percentuali (errore standard ${pf(P.se)}), su una media del ${pf(P.mean)}%.</li>`;
  h+=sig(Wn)?`<li><b>Il legame regge confrontando solo province della stessa regione</b> per lo stesso partito: ${pf(Wn.b)} punti (e.s. ${pf(Wn.se)}). Non è solo una questione di Nord e Sud.</li>`:`<li><b>Confrontando solo province della stessa regione la stima non è distinguibile da zero</b>: ${pf(Wn.b)} punti (e.s. ${pf(Wn.se)}). ${many?'In questo periodo':'In questa manovra'} il legame si vede con sicurezza solo tra regioni.</li>`;
  h+=Ap?`<li><b>Le richieste approvate seguono la stessa geografia</b>${sig(Ap)?'':', ma la stima è incerta'}: ${pf(Ap.b,2)} punti (e.s. ${pf(Ap.se,2)}) su una media dell’${pf(Ap.mean)}%.</li>`:`<li><b>Nessuna stima sulle approvate</b>: ${PA===2027?'la manovra 2027 non è ancora stata votata.':'troppo poche richieste locali approvate nel periodo.'}</li>`;
  if(A)h+=`<li><b>Essere in maggioranza conta più del territorio.</b> Una proposta dell’opposizione passa nel ${pf(A.base)}% dei casi; la maggioranza ha ${pf(A.mag.b)} punti in più (e.s. ${pf(A.mag.se)}).</li>`;
  h+='</ol>';if(PA<=2023&&PB>=2027&&AN.ranges['2027-2027'])h+=`<p class="meta">Con la sola manovra 2027 il confronto dentro la regione dà ${pf(AN.ranges['2027-2027'].within.b)} punti (e.s. ${pf(AN.ranges['2027-2027'].within.se)}): scegli «2027» nel periodo per vederlo.</p>`;
  $('#abrief').innerHTML=h;
  const M=AN.models,it=[];SELY().forEach((y,i)=>{it.push({row:i,t:y+' tutta Italia',b:M.by_year[y].b,se:M.by_year[y].se,dy:-7,lab:'Manovra '+y},{row:i,t:y+' stessa regione',b:M.by_year_within[y].b,se:M.by_year_within[y].se,dy:7,hollow:1})});
  coefPlot($('#afig'),it,'punti percentuali per +10 punti di voto');
  const cell=m=>m?`<td>${pf(m.b,2)}${stars(m.b,m.se)}</td>`:'<td>—</td>',cse=m=>m?`<td>(${pf(m.se,2)})</td>`:'<td></td>';
  const yl=PA===PB?String(PA):PA+'–'+String(PB).slice(2);const apy=Ap?(PA===Math.min(PB,2026)?String(PA):PA+'–'+String(Math.min(PB,2026)).slice(2)):'—';
  $('#atab').innerHTML=`<thead><tr><th></th><th>(1)</th><th>(2)</th><th>(3)</th><th>(4)</th></tr><tr><th>Variabile dipendente</th><th>Richiesta 0/1</th><th>Richiesta 0/1</th><th>Richiesta 0/1</th><th>Approvata 0/1</th></tr></thead><tbody>
  <tr><td>Voti 2022 (+10 punti)</td>${cell(Q.nofe)}${cell(P)}${cell(Wn)}${cell(Ap)}</tr><tr class="se"><td></td>${cse(Q.nofe)}${cse(P)}${cse(Wn)}${cse(Ap)}</tr>
  <tr class="sep"><td>Effetti fissi partito × manovra</td><td>Sì</td><td>Sì</td><td>Sì</td><td>Sì</td></tr>
  <tr><td>Effetti fissi regione</td><td>No</td><td>Sì</td><td>—</td><td>Sì</td></tr>
  <tr><td>Effetti fissi partito × regione</td><td>No</td><td>No</td><td>Sì</td><td>No</td></tr>
  <tr><td>Manovre</td><td>${yl}</td><td>${yl}</td><td>${yl}</td><td>${apy}</td></tr>
  <tr class="sep"><td>Media var. dipendente (%)</td><td>${pf(Q.nofe.mean)}</td><td>${pf(P.mean)}</td><td>${pf(Wn.mean)}</td><td>${Ap?pf(Ap.mean):'—'}</td></tr>
  <tr><td>Osservazioni · cluster</td><td>${nf(Q.nofe.n)} · ${Q.nofe.g}</td><td>${nf(P.n)} · ${P.g}</td><td>${nf(Wn.n)} · ${Wn.g}</td><td>${Ap?nf(Ap.n)+' · '+Ap.g:'—'}</td></tr></tbody>`;
  $('#anote').textContent=`Modello lineare di probabilità. Unità: provincia × partito × manovra; ${AN.nprov} province (esclusa la Valle d’Aosta) × 8 partiti × ${SELY().length} ${SELY().length>1?'manovre':'manovra'}${PRA?' (le stime usano sempre entrambi i rami)':''}. Richiesta = almeno una proposta del partito (primo firmatario) che nomina la provincia. Colonna (4): richiesta approvata, solo prime letture già votate. Errori standard a cluster per provincia. *** p<0,01; ** p<0,05; * p<0,1.`;
  $('#aptab').innerHTML=A?`<thead><tr><th>Variabile</th><th>Coefficiente (punti %)</th><th>Errore standard</th></tr></thead><tbody>
  <tr><td>Primo firmatario in maggioranza</td><td>${pf(A.mag.b,2)}${stars(A.mag.b,A.mag.se)}</td><td>${pf(A.mag.se,2)}</td></tr>
  <tr><td>Proposta per un solo territorio</td><td>${pf(A.loc.b,2)}${stars(A.loc.b,A.loc.se)}</td><td>${pf(A.loc.se,2)}</td></tr>
  <tr><td>Maggioranza × territorio</td><td>${pf(A.magloc.b,2)}${stars(A.magloc.b,A.magloc.se)}</td><td>${pf(A.magloc.se,2)}</td></tr>
  <tr class="sep"><td>Tasso di base (opposizione, proposta non locale)</td><td>${pf(A.base,2)}%</td><td></td></tr>
  <tr><td>Proposte · primi firmatari (cluster)</td><td>${nf(A.n)} · ${nf(A.g)}</td><td></td></tr></tbody>`:'<tbody><tr><td>Nessuna prima lettura già votata nel periodo scelto (la manovra 2027 non è ancora stata votata).</td></tr></tbody>';
  // eterogeneità per partito
  if(AN.het){const hs=ORDER.filter(g=>AN.het[g]).map(g=>({t:g,lab:g,b:AN.het[g].b,se:AN.het[g].se,col:PCOL[g]}));coefPlot($('#ahet'),hs,'punti percentuali per +10 punti di voto (intera legislatura)');
    $('#ahetp').innerHTML=''+(AN.het_txt||'');$('#ahetf').hidden=false}else $('#ahetf').hidden=true;
  // curva delle specificazioni
  if(AN.spec&&AN.spec.length){const S=AN.spec.slice().sort((a,b)=>a.b-b.b);$('#aspn').textContent=nf(S.length);const s=$('#aspec');s.innerHTML='';const W=640,H=260,ml=40,mr=10,mt=10,mb=30;
    const lo=Math.min(0,...S.map(d=>d.b-1.96*d.se)),hi=Math.max(...S.map(d=>d.b+1.96*d.se));const Y=v=>mt+(hi-v)/(hi-lo)*(H-mt-mb),X=i=>ml+(i+.5)/S.length*(W-ml-mr);
    for(let t=Math.ceil(lo/5)*5;t<=hi;t+=5){const l=svgEl(s,'line',{x1:ml,x2:W-mr,y1:Y(t),y2:Y(t),class:t===0?'ax':'gr'});if(t===0)l.style.stroke='var(--fg)';svgEl(s,'text',{x:ml-6,y:Y(t)+4,'text-anchor':'end'},pf(t,0))}
    S.forEach((d,i)=>{const sg=Math.abs(d.b/d.se)>1.96;const l=svgEl(s,'line',{x1:X(i),x2:X(i),y1:Y(d.b-1.96*d.se),y2:Y(d.b+1.96*d.se)});l.style.stroke='var(--line)';const c=svgEl(s,'circle',{cx:X(i),cy:Y(d.b),r:2.6});c.style.fill=sg?'var(--accent)':'var(--surface)';c.style.stroke='var(--accent)';svgEl(c,'title',{},d.lab+': '+pf(d.b)+' (e.s. '+pf(d.se)+')')});
    svgEl(s,'text',{x:(ml+W-mr)/2,y:H-6,'text-anchor':'middle'},'specificazioni, dalla stima più bassa alla più alta');
    const pos=S.filter(d=>d.b>0).length,sgp=S.filter(d=>d.b/d.se>1.96).length;$('#aspecp').innerHTML=`Su ${nf(S.length)} modi ragionevoli di fare il conto, ${nf(pos)} danno un legame positivo e ${nf(sgp)} positivo e significativo. La mediana è ${pf(S[Math.floor(S.length/2)].b)} punti. ${AN.spec_txt||''}`;$('#aspecf').hidden=false}
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
