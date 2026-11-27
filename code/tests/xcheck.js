// Controlli incrociati: dashboard legislatura (e 2027) contro un "oracolo" calcolato in modo indipendente da emendamenti.json
const {chromium}=require('playwright');const fs=require('fs');
const BASE=process.argv[2]||'http://localhost:8790/_test.html';
const DIR=process.argv[3]||'/home/claude/multi/site2';
const J=JSON.parse(fs.readFileSync(DIR+'/emendamenti.json'));const ALL=J.rows.map(a=>{const o={};if(J.cols)J.cols.forEach((k,i)=>o[k]=a[i]);else Object.assign(o,a);if(o.o==null)o.o=o.s==='Ammissibile'?'N':'I';if(o.y==null)o.y=2027;if(!o.ra)o.ra='Camera';return o});
const VOTI=JSON.parse(fs.readFileSync(DIR+'/voti2022.json')),POP=JSON.parse(fs.readFileSync(DIR+'/popolazione.json'));
const PALIAS={'Sud Sardegna':'Sulcis Iglesiente'};
const AMT=r=>r.big?0:(r.e3||0);
const nf=n=>n.toLocaleString('it-IT');const pc=(a,b)=>b?(a/b*100).toLocaleString('it-IT',{maximumFractionDigits:1})+'%':'—';const pc1=(a,b)=>b?(a/b*100).toLocaleString('it-IT',{maximumFractionDigits:1,minimumFractionDigits:1})+'%':'—';
const fmtE=v=>(v==null||v===0)?'—':(v>=1e9?(v/1e9).toLocaleString('it-IT',{maximumFractionDigits:v>=1e11?0:v>=1e10?1:2,useGrouping:'always'})+' mld':(v>=1e6?(v/1e6).toLocaleString('it-IT',{maximumFractionDigits:2})+' mln':Math.round(v/1e3).toLocaleString('it-IT')+' mila'));
let seed=20261127;const rnd=()=>{seed=(seed*1103515245+12345)%2147483648;return seed/2147483648};const pick=a=>a[Math.floor(rnd()*a.length)];
const res=[];const ok=(c,lab,got,exp)=>{res.push({c:!!c,lab,got,exp});if(!c)console.log('FAIL',lab,'| got:',JSON.stringify(got),'| exp:',JSON.stringify(exp))};
const norm=s=>String(s).replace(/\s+/g,' ').trim();
const per=(a,b,ra)=>ALL.filter(r=>r.y>=a&&r.y<=b&&(!ra||r.ra===ra));
(async()=>{const br=await chromium.launch();const ctx=await br.newContext({acceptDownloads:true,viewport:{width:1400,height:1000}});const p=await ctx.newPage();
await p.route('**/d3.min.js',r=>r.fulfill({path:'/tmp/claude-0/libs/node_modules/d3/dist/d3.min.js',contentType:'application/javascript'}));
await p.route('**/topojson.min.js',r=>r.fulfill({path:'/tmp/claude-0/libs/node_modules/topojson/dist/topojson.min.js',contentType:'application/javascript'}));
const errs=[];p.on('pageerror',e=>errs.push(e.message));
await p.goto(BASE);await p.evaluate(()=>{try{localStorage.clear()}catch(e){}});await p.goto(BASE);await p.waitForSelector('#tb tr.r',{timeout:30000});
const MULTI=await p.$('#pya')!==null;
async function setPer(a,b,ra){if(!MULTI)return;await p.selectOption('#pya',String(2023));await p.selectOption('#pyb',String(b));await p.selectOption('#pya',String(a));await p.selectOption('#pra',ra||'');await p.waitForTimeout(150);const v=await p.evaluate(()=>[document.querySelector('#pya').value,document.querySelector('#pyb').value,document.querySelector('#pra').value]);if(v.join()!==[a,b,ra||''].join())throw new Error('periodo non impostato '+v)}
async function view(v){await p.click(`[data-view="${v}"]`);await p.waitForTimeout(250)}
async function resetEl(){await p.click('#reset');await p.waitForTimeout(100)}
const csvOf=async(btn)=>{const [d]=await Promise.all([p.waitForEvent('download'),p.click(btn)]);const t=fs.readFileSync(await d.path(),'utf8').replace(/^﻿/,'');return t.trim().split(/\r?\n/).map(l=>{const out=[];let cur='',q=false;for(const ch of l){if(q){if(ch==='"')q=false;else cur+=ch}else if(ch==='"')q=true;else if(ch===';'){out.push(cur);cur=''}else cur+=ch}out.push(cur);return out})};
const num=s=>s===''?0:parseFloat(String(s).replace(/\./g,'').replace(',','.'));

// ---------- A. emendamento per emendamento: ricerca, riga, dettaglio, link ----------
await view('elenco');
const strata={};ALL.forEach(r=>{const k=r.y+r.ra;(strata[k]=strata[k]||[]).push(r)});
const sample=[];Object.values(strata).forEach(a=>{for(let i=0;i<8;i++)sample.push(pick(a))});
// aggiungo casi difficili: riammessi, parziali, grandi opere, multi-provincia
ALL.filter(r=>r.y===2027&&(r.pz||r.big)).slice(0,6).forEach(r=>sample.push(r));
const URN={2023:['643-bis','urn:leg:19:643:bis:null:com:05:referente'],2024:['1627','urn:leg:19:1627:null:null:com:05:referente'],2025:['2112-bis','urn:leg:19:2112:bis:null:com:05:referente'],2026:['2750','urn:leg:19:2750:null:null:com:05:referente'],2027:['3174-bis','urn:leg:19:3174:bis:null:com:05:referente']},SOBJ={2023:'1368104',2024:'1395344',2025:'1441141',2026:'1477272'};
const OLAB={A:'Approvato',N:'Respinto o non votato',R:'Ritirato',I:'Inammissibile'};
for(const r of sample){
  await setPer(r.y,r.y,r.ra);await resetEl();
  const sur=r.p.split(' ')[0].toLowerCase();await p.fill('#q',r.i+' '+sur);await p.waitForTimeout(200);
  const key=MULTI?r.y+'|'+r.ra+'|'+r.i:r.i+'|'+r.p;
  let row=await p.$(`#tb tr.r[data-k="${key}"]`);
  ok(row,`A ricerca trova ${r.y} ${r.ra} ${r.i}`,!!row,true);if(!row)continue;
  const SS=x=>(MULTI?(x.i+' '+x.t+' '+x.f.map(f=>f[0]).join(' ')+' '+x.l.join(' ')+' '+x.y+' '+x.ra):(x.i+' '+x.t+' '+J.texts[x.x]+' '+x.f.map(f=>f[0]).join(' ')+' '+x.l.join(' '))).toLowerCase();const exp=ALL.filter(x=>x.y===r.y&&x.ra===r.ra).filter(x=>SS(x).includes(r.i.toLowerCase())&&SS(x).includes(sur)).length;
  const cnt=norm(await p.$eval('#cnt',e=>e.innerText)).split(' ')[0];ok(num(cnt)===exp,`A conteggio ricerca ${r.i}`,cnt,exp);
  await row.click();await p.waitForTimeout(150);
  const det=await p.$eval('#tb tr.det',e=>{const o={};const dts=[...e.querySelectorAll('dt')];dts.forEach(dt=>o[dt.innerText.trim()]=dt.nextElementSibling);return {es:o['Esito']?.innerText.trim(),man:o['Manovra']?.innerText.trim(),src:o['Fonte']?.querySelector('a')?.href||'',nf:o['Firmatari']?.querySelectorAll('.chip').length,terr:o['Territorio']?.innerText.trim()}});
  const esExp=!MULTI?(r.s==='Ammissibile'?(r.pz?'Ammissibile, '+r.m:'Ammissibile'):'Inammissibile per '+r.m):r.s==='Ammissibile'?((r.o==='A'?'Approvato':OLAB[r.o])+(r.pz?' · '+r.m:'')):(r.s==='Altro motivo'?'Inammissibile ('+r.m+')':'Inammissibile per '+r.m);
  ok(norm(det.es)===norm(esExp),`A esito ${r.y} ${r.ra} ${r.i}`,det.es,esExp);
  if(MULTI){const le=r.le===2?'seconda':'prima';ok(norm(det.man)===`${r.y} · ${r.ra} · ${le} lettura`,`A manovra ${r.i}`,det.man,`${r.y} · ${r.ra} · ${le} lettura`)}
  ok(det.nf===r.f.length,`A firmatari ${r.i}`,det.nf,r.f.length);
  if(MULTI&&r.lk){let L;if(r.lk.startsWith('S:'))L='https://www.senato.it/show-doc?leg=19&tipodoc=EMENDC&id='+r.lk.slice(2)+'&idoggetto='+SOBJ[r.y];else{const [id,pos]=r.lk.split('|');const [c,u]=URN[r.y];L='https://documenti.camera.it/apps/emendamenti/getPropostaEmendativa.aspx?contenitorePortante=leg.19.eme.ac.'+c+'&tipoSeduta=1&sedeEsame=referente&urnTestoRiferimento='+u+'&dataSeduta=null&idPropostaEmendativa='+encodeURIComponent(id)+'&position='+pos}
    ok(det.src===L,`A link ufficiale ${r.y} ${r.ra} ${r.i}`,det.src,L);
    const idInLink=r.lk.startsWith('S:')?true:decodeURIComponent(r.lk.split('|')[0]).replace(/\.$/,'')===r.i;ok(idInLink,`A il link punta al numero giusto ${r.i}`,r.lk,r.i)}
  ok(det.terr.includes(r.l.length?r.l[0]:'—'),`A territorio ${r.i}`,det.terr,r.l[0]||'—');
}
// ---------- B. riquadri dell'elenco sotto combinazioni di filtri ----------
const PER=MULTI?[[2023,2027,''],[2023,2023,''],[2024,2024,'Senato'],[2025,2025,'Camera'],[2026,2026,''],[2027,2027,''],[2025,2027,'Senato']]:[[2027,2027,'']];
let GR=['','FdI','PD','M5S','Lega','FI','AVS','Azione / IV'];{const av=await p.$$eval('#fg option',o=>o.map(x=>x.value));GR=GR.filter(g=>av.includes(g));}
for(const [a,b,ra] of PER)for(let k=0;k<4;k++){
  await setPer(a,b,ra);await resetEl();const g=k?pick(GR):'';const fo=MULTI?pick(['','A','N','I','']):'';const loc=k===3;
  if(g)await p.selectOption('#fg',g);if(fo)await p.selectOption('#fo',fo);if(loc)await p.check('#floc');await p.waitForTimeout(150);
  const Dp=per(a,b,ra);const F=Dp.filter(r=>(!g||r.g===g)&&(!fo||r.o===fo)&&(!loc||r.loc));
  const tiles=await p.$$eval('#tiles .tile b',a=>a.map(x=>x.innerText.trim()));const tl=`B ${a}-${b}${ra} g=${g} fo=${fo} loc=${loc}`;
  if(!MULTI){const iE=F.filter(r=>r.s==='Estraneità di materia').length,iC=F.filter(r=>r.s==='Compensazione').length,L_=F.filter(r=>r.loc);
    const ex=[nf(F.length),pc(iE+iC,F.length),nf(iE),nf(iC),nf(L_.length),fmtE(L_.reduce((s,r)=>s+AMT(r),0))];ex.forEach((e,j)=>ok(tiles[j]===e,tl+' riquadro '+j,tiles[j],e));continue}
  ok(tiles[0]===nf(F.length),tl+' totale',tiles[0],nf(F.length));
  ok(tiles[1]===nf(F.filter(r=>r.o==='A').length),tl+' approvate',tiles[1],nf(F.filter(r=>r.o==='A').length));
  ok(tiles[2]===pc(F.filter(r=>r.s!=='Ammissibile').length,F.length),tl+' % inammissibili',tiles[2],pc(F.filter(r=>r.s!=='Ammissibile').length,F.length));
  ok(tiles[3]===nf(F.filter(r=>r.loc).length),tl+' per un territorio',tiles[3],nf(F.filter(r=>r.loc).length));
  ok(tiles[4]===fmtE(F.filter(r=>r.loc).reduce((s,r)=>s+AMT(r),0)),tl+' euro per territori',tiles[4],fmtE(F.filter(r=>r.loc).reduce((s,r)=>s+AMT(r),0)));
}
// ---------- C. classifica parlamentari vs elenco vs mappa ----------
const firsts={};ALL.forEach(r=>{if(r.g!=='Governo e relatori')(firsts[r.p]=firsts[r.p]||[]).push(r)});
const names=Object.keys(firsts).filter(n=>firsts[n].length>=3);const deps=[];for(let i=0;i<30;i++)deps.push(pick(names));
['Furfaro Marco','Furfaro'].forEach(n=>{if(firsts[n])deps.push(n)});
for(const name of deps){
  const rows=firsts[name];const ras=[...new Set(rows.map(r=>r.ra))];
  await setPer(MULTI?2023:2027,2027,'');
  // elenco
  await view('elenco');await resetEl();await p.fill('#fw',name);await p.dispatchEvent('#fw','input');await p.waitForTimeout(200);
  const cnt=norm(await p.$eval('#cnt',e=>e.innerText)).split(' ')[0];const allRows=ALL.filter(r=>r.p===name);
  ok(num(cnt)===allRows.length,`C elenco conteggio ${name}`,cnt,allRows.length);
  // classifica
  await view('classifica');await p.fill('#rmin','1');await p.dispatchEvent('#rmin','input');if(MULTI){await p.fill('#rq',name);await p.dispatchEvent('#rq','input')}else{const tx=await p.$eval('#rall',e=>e.textContent);if(/tutti/i.test(tx))await p.click('#rall')}await p.waitForTimeout(150);
  const rk=await p.$$eval('#rankb tr',(trs,name)=>trs.map(tr=>{const b=tr.querySelector('button.who');return b&&b.innerText.trim()===name?[...tr.children].map(td=>td.innerText.replace(/\s+/g,' ').trim()).concat([tr.querySelector('.meta:not(.n .meta)')?.innerText||'']):null}).filter(Boolean),name);
  for(const ra of ras){const R=rows.filter(r=>r.ra===ra);const t=rk.find(x=>MULTI?x[1].endsWith(ra):true);
    ok(t,`C classifica riga ${name} ${ra}`,!!t,true);if(!t)continue;
    if(!MULTI){const e2=[nf(R.length),pc(R.filter(r=>r.s!=='Ammissibile').length,R.length),pc(R.filter(r=>r.s==='Estraneità di materia').length,R.length),nf(R.filter(r=>r.loc).length)];e2.forEach((e,j)=>ok(t[2+j].startsWith(e)||t[2+j].endsWith(e),`C classifica col${j} ${name}`,t[2+j],e));continue}
    const exp=[nf(R.length),nf(R.filter(r=>r.o==='A').length)+' '+pc(R.filter(r=>r.o==='A').length,R.length),pc(R.filter(r=>r.s!=='Ammissibile').length,R.length),nf(R.filter(r=>r.loc).length),fmtE(R.filter(r=>r.loc).reduce((s,r)=>s+AMT(r),0))];
    ['proposte','approvate','% inamm.','per un territorio','euro territori'].forEach((lab,j)=>ok(t[2+j]===exp[j],`C classifica ${lab} ${name} ${ra}`,t[2+j],exp[j]));}
  // mappa per deputato (primo firmatario, tutti gli esiti)
  await view('mappa');await p.waitForSelector('#mapsvg path.pv',{timeout:20000});await p.click('#mreset');await p.fill('#mdep',name);await p.dispatchEvent('#mdep','input');await p.dispatchEvent('#mdep','change');await p.waitForTimeout(250);
  const csv=await csvOf('#csvmp');const h=csv[0];const iN=h.indexOf('Emendamenti che la nominano'),iE=h.findIndex(x=>x.startsWith('Euro chiesti nel periodo')||x.startsWith('Euro chiesti 2027'));
  const P={};rows.filter(r=>r.pm.length).forEach(r=>{const v=AMT(r)/r.pm.length;r.pm.forEach(p0=>{const q=PALIAS[p0]||p0;const o=P[q]||(P[q]={n:0,e:0});o.n++;o.e+=v})});
  let bad=0,tot=0;csv.slice(1).forEach(c=>{const o=P[c[1]]||{n:0,e:0};tot++;if(num(c[iN])!==o.n||Math.abs(num(c[iE])-Math.round(o.e))>1)bad++});
  ok(bad===0&&tot===110,`C mappa ${name}: 110 province coerenti`,{bad,tot},{bad:0,tot:110});
}
// ---------- D. mappa per periodo × esito × gruppo: tutte le province ----------
await view('mappa');
const MES=MULTI?['','AP','A','I','E']:['','A','I','E'];
for(const [a,b,ra] of PER)for(let k=0;k<3;k++){
  await setPer(a,b,ra);await p.click('#mreset');const es=pick(MES),g=k?pick(GR):'',po=k===2?pick(['1','m']):'';
  if(es)await p.selectOption('#mes',es);if(g)await p.selectOption('#mg',g);if(po)await p.selectOption('#mpo',po);await p.waitForTimeout(200);
  const Dp=per(a,b,ra).filter(r=>r.g!=='Governo e relatori'&&(!g||r.g===g)&&(!po||(po==='1'?r.pm.length===1:r.pm.length>1)))
    .filter(r=>es===''||(es==='AP'&&r.o==='A')||(es==='A'&&r.s==='Ammissibile')||(es==='I'&&r.s!=='Ammissibile')||(es==='E'&&r.s==='Estraneità di materia'));
  const P={};Dp.filter(r=>r.pm.length).forEach(r=>{const v=AMT(r)/r.pm.length;r.pm.forEach(p0=>{const q=PALIAS[p0]||p0;const o=P[q]||(P[q]={n:0,e:0,G:{}});o.n++;o.e+=v;o.G[r.g]=(o.G[r.g]||0)+v})});
  const csv=await csvOf('#csvmp');const h=csv[0];const iN=h.indexOf('Emendamenti che la nominano'),iE=h.findIndex(x=>x.startsWith('Euro chiesti nel periodo')||x.startsWith('Euro chiesti 2027')),iPC=h.indexOf('Euro per abitante'),iPop=h.findIndex(x=>x.startsWith('Popolazione'));
  const tl=`D mappa ${a}-${b}${ra} es=${es} g=${g} po=${po}`;
  csv.slice(1).forEach(c=>{const o=P[c[1]]||{n:0,e:0};ok(num(c[iN])===o.n&&Math.abs(num(c[iE])-Math.round(o.e))<=1,`${tl} ${c[1]}`,[c[iN],c[iE]],[o.n,Math.round(o.e)]);
    if(+c[iPop]&&o.e)ok(Math.abs(num(c[iPC])-o.e/POP[c[1]])<0.01,`${tl} ${c[1]} € per abitante`,c[iPC],o.e/POP[c[1]])});
  // somma frase in testa alla mappa = somma province
  const sumTxt=norm(await p.$eval('#mapsum',e=>e.innerText));const tot=Object.values(P).reduce((s,o)=>s+o.e,0);
  ok(Object.keys(P).length===0?/Nessun/.test(sumTxt):sumTxt.includes(fmtMap(tot)),`${tl} frase riassuntiva`,sumTxt.slice(0,160),fmtMap(tot));
}
function fmtMap(v){return !v?'0 €':v>=1e9?(v/1e9).toLocaleString('it-IT',{maximumFractionDigits:v>=1e10?1:2})+' mld':v>=1e6?(v/1e6).toLocaleString('it-IT',{maximumFractionDigits:v>=1e8?0:1})+' mln':v>=1e3?Math.round(v/1e3).toLocaleString('it-IT')+' mila €':Math.round(v)+' €'}
// ---------- E. quadro ----------
if(MULTI){await setPer(2023,2027,'');await view('quadro');
  const q=await p.$$eval('#qtab tbody tr',trs=>trs.map(tr=>[...tr.children].map(td=>td.innerText.replace(/\s+/g,' ').trim())));
  for(const t of q){const y=+t[0],ra=t[1];const X=ALL.filter(r=>r.y===y&&r.ra===ra);const exp=[nf(X.length),nf(X.filter(r=>r.o==='I').length)+' '+pc(X.filter(r=>r.o==='I').length,X.length),nf(X.filter(r=>r.o==='R').length),nf(X.filter(r=>r.o==='A').length)+' '+pc(X.filter(r=>r.o==='A').length,X.length)];
    [3,4,5,6].forEach((j,k)=>ok(t[j]===exp[k],`E quadro ${y} ${ra} col${j}`,t[j],exp[k]))}
  const qp=await p.$$eval('#qparty tbody tr',trs=>trs.map(tr=>[...tr.children].map(td=>td.innerText.replace(/\s+/g,' ').trim())));
  const ys=[2023,2024,2025,2026,2027];
  for(const t of qp){const g=t[0];const X=ALL.filter(r=>r.g===g);ys.forEach((y,j)=>{const Y=X.filter(r=>r.y===y);const e=nf(Y.length)+' · '+nf(Y.filter(r=>r.o==='A').length);ok(t[1+j]===e,`E partiti ${g} ${y}`,t[1+j],e)});
    ok(t[6]===nf(X.length),`E partiti ${g} totale`,t[6],nf(X.length));const na=X.filter(r=>r.o==='A').length,ni=X.filter(r=>r.s!=='Ammissibile').length;ok(t[7]===nf(na)+' '+pc1(na,X.length),`E partiti ${g} approvate`,t[7],nf(na)+' '+pc1(na,X.length));ok(t[8]===nf(ni)+' '+pc1(ni,X.length),`E partiti ${g} inammissibili`,t[8],nf(ni)+' '+pc1(ni,X.length));const L_=X.filter(r=>r.loc);ok(t[10]===fmtE(L_.reduce((s,r)=>s+AMT(r),0)),`E partiti ${g} euro`,t[10],fmtE(L_.reduce((s,r)=>s+AMT(r),0)))}
  // ordinamento per % approvate
  await p.selectOption('#qps','pap');await p.waitForTimeout(200);const pa=await p.$$eval('#qparty tbody tr td:nth-child(8) .meta',a=>a.map(x=>parseFloat(x.innerText.replace(',','.'))));ok(pa.every((v,i)=>i===0||pa[i-1]>=v),'E ordinamento % approvate',pa,'decrescente');await p.selectOption('#qps','n');
  const qt=await p.$$eval('#qtiles .tile b',a=>a.map(x=>x.innerText.trim()));ok(qt[0]===nf(ALL.length),'E quadro totale',qt[0],nf(ALL.length));ok(qt[2]===nf(ALL.filter(r=>r.o==='I').length),'E quadro inammissibili',qt[2],nf(ALL.filter(r=>r.o==='I').length));
}
// ---------- F. soldi e voti ----------
const VG=[['FdI',['FdI']],['Lega',['Lega']],['FI',['FI']],['NM',['Noi Moderati']],['PD',['PD']],['M5S',['M5S']],['AVS',['AVS']],['AzIV',MULTI?['Azione / IV']:['Azione','IV']]];
const rankArr=x=>{const s=x.map((v,i)=>[v,i]).sort((a,b)=>a[0]-b[0]);const r=new Array(x.length);let i=0;while(i<s.length){let j=i;while(j+1<s.length&&s[j+1][0]===s[i][0])j++;for(let k=i;k<=j;k++)r[s[k][1]]=(i+j)/2;i=j+1}return r};
const pear=(a,b)=>{if(new Set(a).size<2||new Set(b).size<2)return NaN;const n=a.length,ma=a.reduce((x,y)=>x+y,0)/n,mb=b.reduce((x,y)=>x+y,0)/n;let sxy=0,sx=0,sy=0;for(let i=0;i<n;i++){sxy+=(a[i]-ma)*(b[i]-mb);sx+=(a[i]-ma)**2;sy+=(b[i]-mb)**2}return sxy/Math.sqrt(sx*sy)};
for(const [a,b,ra] of PER.slice(0,MULTI?4:1))for(const amm of [false,true]){
  await setPer(a,b,ra);await view('voti');await p.waitForSelector('#vtab tbody tr',{timeout:20000});await p.selectOption('#vsort','');if(amm!==await p.isChecked('#vamm'))await p.click('#vamm');await p.waitForTimeout(250);
  const tab=await p.$$eval('#vtab tbody tr',trs=>trs.map(tr=>({k:tr.dataset.k,c:[...tr.children].map(td=>td.innerText.replace(/\s+/g,' ').trim())})));
  for(const [k,gs] of VG){const ki=VOTI.K.indexOf(k);const E={},Nn={};per(a,b,ra).forEach(r=>{if(!gs.includes(r.g)||!r.pm.length)return;if(amm&&r.s!=='Ammissibile')return;r.pm.forEach(p0=>{const q=PALIAS[p0]||p0;E[q]=(E[q]||0)+AMT(r)/r.pm.length;Nn[q]=(Nn[q]||0)+1})});
    const rows=Object.keys(VOTI.prov).filter(q=>POP[q]).map(q=>({q,sh:VOTI.prov[q][ki]/VOTI.prov[q][0]*100,e:E[q]||0,n:Nn[q]||0,pop:POP[q]}));const rho=pear(rankArr(rows.map(r=>r.sh)),rankArr(rows.map(r=>r.e/r.pop)));
    const s=rows.slice().sort((x,y)=>x.sh-y.sh);const t=Math.floor(s.length/3);const lo=s.slice(0,t),hi=s.slice(-t);const pcg=A=>A.reduce((x,r)=>x+r.e,0)/A.reduce((x,r)=>x+r.pop,0);
    const row=tab.find(x=>x.k===k);const tl=`F voti ${a}-${b}${ra} amm=${amm} ${k}`;ok(row,tl+' riga',!!row,true);if(!row)continue;
    const rhoTxt=isNaN(rho)?'—':(rho>=0?'+':'−')+Math.abs(rho).toLocaleString('it-IT',{maximumFractionDigits:2,minimumFractionDigits:2});ok(row.c[1].startsWith(rhoTxt),tl+' correlazione',row.c[1],rhoTxt);
    const nW=rows.filter(r=>r.n>0).length;ok(row.c[2]===`${nW} su ${rows.length}`,tl+' province con richieste',row.c[2],`${nW} su ${rows.length}`);
    const pcF=v=>v>=100?Math.round(v).toLocaleString('it-IT')+' €':v>=10?v.toLocaleString('it-IT',{maximumFractionDigits:0})+' €':v.toLocaleString('it-IT',{maximumFractionDigits:1})+' €';
    ok(row.c[4]===pcF(pcg(hi)),tl+' € roccaforti',row.c[4],pcF(pcg(hi)));ok(row.c[6]===pcF(pcg(lo)),tl+' € deboli',row.c[6],pcF(pcg(lo)));}
  // ordinamento per correlazione
  await p.selectOption('#vsort','rho');await p.waitForTimeout(150);const ord=await p.$$eval('#vtab tbody tr td:nth-child(2)',a=>a.map(x=>parseFloat(x.innerText.replace('−','-').replace(',','.'))));
  const o1=ord.filter(v=>!isNaN(v));ok(o1.every((v,i)=>i===0||o1[i-1]>=v)&&ord.slice(o1.length).every(isNaN),`F ordinamento per correlazione ${a}-${b}${ra} amm=${amm}`,ord,'decrescente');
  await p.selectOption('#vsort','rhoa');await p.waitForTimeout(150);const ord2=await p.$$eval('#vtab tbody tr td:nth-child(2)',a=>a.map(x=>parseFloat(x.innerText.replace('−','-').replace(',','.'))));
  const o2=ord2.filter(v=>!isNaN(v));ok(o2.every((v,i)=>i===0||o2[i-1]<=v)&&ord2.slice(o2.length).every(isNaN),`F ordinamento crescente ${a}-${b}${ra} amm=${amm}`,ord2,'crescente');
  if(amm)await p.click('#vamm');
}
const nOk=res.filter(r=>r.c).length;console.log(`\n${nOk}/${res.length} controlli superati; errori JS: ${errs.length}`,errs.slice(0,3));
const byS={};res.forEach(r=>{const s=r.lab.split(' ')[0];byS[s]=byS[s]||[0,0];byS[s][0]++;if(r.c)byS[s][1]++});console.log(byS);
fs.writeFileSync('/tmp/claude-0/xcheck_'+(MULTI?'multi':'2027')+'.json',JSON.stringify(res));
await br.close()})();
