"""Genera il sito 2023-2027 partendo dal codice del sito sulla manovra 2027 (stesse funzioni, mappa, filtri),
aggiungendo periodo, ramo, esito finale, il quadro per manovra e lo studio sulla legislatura."""
import re
SRC = '/home/claude/emend/site/index.html'
OUT = '/home/claude/multi/site2/index.html'
s = open(SRC).read()
def R(a, b, c=1):
    global s
    n = s.count(a)
    assert n == c, (a[:90], n)
    s = s.replace(a, b)
def RX(pat, rep, c=1):
    global s
    s2, n = re.subn(pat, rep, s, flags=re.S)
    assert n == c, (pat[:80], n)
    s = s2

# ---------- testa ----------
R('<title>Emendamenti Legge di Bilancio 2027</title>', '<title>Manovre della legislatura</title>')
R('<div class="eyebrow">Camera dei deputati · V Commissione Bilancio · C. 3174-bis · fascicolo del 23 novembre 2026</div>',
  '<div class="eyebrow">XIX legislatura · leggi di bilancio 2023–2027 · Camera e Senato · commissioni Bilancio</div>')
R('<h1>Emendamenti alla legge di bilancio 2027</h1>', '<h1>Le manovre della legislatura, emendamento per emendamento</h1>')
RX(r'<p>Tutte le proposte emendative del fascicolo,.*?</p>\n  </header>',
   '<p>Tutte le proposte di modifica alle cinque leggi di bilancio dal 2023 al 2027, alla Camera e al Senato: chi le firma, quante sono inammissibili, quante passano, quanto chiedono e per quali territori. Scegli il periodo qui sotto: vale per tutte le sezioni.</p>\n  </header>\n'
   '  <div class="period" id="period"><span class="seglab">Periodo</span>'
   '<span class="seg sm" role="group" aria-label="Periodo rapido"><button type="button" data-pr="2023-2027">Intera legislatura</button><button type="button" data-pr="2023-2023">2023</button><button type="button" data-pr="2024-2024">2024</button><button type="button" data-pr="2025-2025">2025</button><button type="button" data-pr="2026-2026">2026</button><button type="button" data-pr="2027-2027">2027</button></span>'
   '<span class="pf"><label for="pya">da</label><select id="pya"><option>2023</option><option>2024</option><option>2025</option><option>2026</option><option>2027</option></select><label for="pyb">a</label><select id="pyb"><option>2023</option><option>2024</option><option>2025</option><option>2026</option><option selected>2027</option></select></span>'
   '<span class="pf"><label for="pra">Ramo</label><select id="pra"><option value="">Camera e Senato</option><option>Camera</option><option>Senato</option></select></span>'
   '<span class="pnote" id="pnote"></span></div>')
R('.loading{padding:40px;text-align:center;color:var(--muted)}',
  '.loading{padding:40px;text-align:center;color:var(--muted)}\n'
  '.period{display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:10px 14px;margin:10px 0 4px}\n'
  '.period .pf{display:inline-flex;gap:6px;align-items:center;font-size:13px;color:var(--muted)}.period select{padding:4px 6px}\n'
  '.pnote{font-size:12.5px;color:var(--muted)}\n'
  '.qgrid{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px}@media (max-width:860px){.qgrid{grid-template-columns:minmax(0,1fr)}}\n'
  '.qdot{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:7px;vertical-align:middle}.qpctl{display:flex;gap:12px;flex-wrap:wrap;margin:8px 0 10px}#qparty th.qs:hover{color:var(--accent)}#qparty th.on{color:var(--accent)}\n'
  '.qbars text{fill:var(--muted);font-size:11px}.qbars .lab{fill:var(--fg);font-size:12px}\n'
  '.chip.st-ap{background:var(--ok);color:var(--bg)}\n'
  '.find p{margin:0 0 8px;max-width:90ch}\n#view-analisi .paper{max-width:1040px}#view-analisi .rtab th{font-size:11.5px}')

# ---------- schede ----------
RX(r'<nav class="tabs" role="tablist" aria-label="Vista">.*?</nav>',
   '<nav class="tabs" role="tablist" aria-label="Vista"><button class="tab" role="tab" type="button" data-view="quadro" aria-selected="false">Il quadro: cinque manovre</button><button class="tab" role="tab" type="button" data-view="elenco" aria-selected="true">Cerca un emendamento o un parlamentare</button><button class="tab" role="tab" type="button" data-view="classifica" aria-selected="false">Classifica dei parlamentari</button><button class="tab" role="tab" type="button" data-view="mappa" aria-selected="false">Mappa: dove vanno i soldi</button><button class="tab" role="tab" type="button" data-view="voti" aria-selected="false">Soldi e voti 2022</button><button class="tab" role="tab" type="button" data-view="analisi" aria-selected="false">Studio statistico</button><a class="tab tabout" href="https://claude.ai/artifact/D5WQFUaW1R2Z67CGSseZGe" target="_blank" rel="noopener">Manovra 2027 nel dettaglio ↗</a></nav>\n'
   '<div id="view-quadro" class="view" hidden>\n'
   '  <section class="tiles" id="qtiles" aria-label="Riepilogo"></section>\n'
   '  <section class="panel"><h2>Quante proposte, e che fine hanno fatto</h2><p class="sub">Proposte presentate nella commissione Bilancio di ciascuna Camera, per esito. La prima lettura è quella in cui la manovra si cambia davvero; in seconda lettura il testo arriva «blindato» e non passa nessuna modifica (²).</p>'
   '<div class="legend"><span><i class="sw" style="background:var(--ok)"></i>Approvata</span><span><i class="sw c-bad"></i>Inammissibile</span><span><i class="sw c-warn"></i>Ritirata</span><span><i class="sw" style="background:var(--line)"></i>Respinta, decaduta o non votata</span></div>'
   '<div class="tablewrap"><svg id="qbars" class="qbars" viewBox="0 0 900 330" style="width:100%;min-width:620px;height:auto" role="img" aria-label="Proposte per manovra, ramo ed esito"></svg></div>'
   '<div class="tablewrap"><table class="rank" id="qtab"></table></div>'
   '<p class="sub">Il 2023 alla Camera conta solo le proposte <b>segnalate</b> dai gruppi (1.043): nel dicembre 2022 la Camera non ha pubblicato i testi di tutte le circa 3.000 presentate. La manovra 2027 non è ancora stata votata in commissione.</p></section>\n'
   '  <section class="qgrid"><div class="panel"><h2>Chi firma le proposte approvate</h2><p class="sub">Proposte approvate, per schieramento del primo firmatario.</p><svg id="qcoal" class="qbars" viewBox="0 0 520 210" style="width:100%;height:auto"></svg></div>'
   '<div class="panel"><h2>Quanto conviene essere in maggioranza</h2><p class="sub">Quota di proposte approvate sul totale presentato dallo schieramento, prime letture già votate.</p><svg id="qrate" class="qbars" viewBox="0 0 520 210" style="width:100%;height:auto"></svg></div></section>\n'
   '  <section class="panel"><h2>Partito per partito</h2><p class="sub">Primo firmatario, gruppo alla data della manovra. Le percentuali sono sul totale delle proposte del partito nel periodo; la manovra 2027 non è ancora stata votata, quindi non ha approvate. Clicca un titolo di colonna per ordinare, un partito per vedere le sue proposte approvate nell’elenco.</p><div class="qpctl"><div class="f"><label for="qps">Ordina per</label><select id="qps"><option value="n">Proposte presentate</option><option value="pap">% approvate</option><option value="pia">% inammissibili</option><option value="pam">% ammissibili</option><option value="plo">% per un solo territorio</option><option value="eur">Euro chiesti per territori</option><option value="g">Ordine dei partiti</option></select></div><div class="f"><label for="qpy">Colonne per anno</label><select id="qpy"><option value="np">Presentate · approvate</option><option value="pap">% approvate</option><option value="pia">% inammissibili</option><option value="none">Nascondi</option></select></div></div><div class="tablewrap"><table class="rank" id="qparty"></table></div></section>\n'
   '</div>')

# ---------- filtri elenco ----------
R('<div class="f"><label for="fw">Deputato</label>', '<div class="f"><label for="fw">Parlamentare</label>')
R('<div class="f"><label for="fwm">Ruolo del deputato</label>', '<div class="f"><label for="fwm">Ruolo</label>')
R('<div class="f"><label for="fs">Esito</label><select id="fs"><option value="">Tutti</option><option>Ammissibile</option><option value="INAMM">Inammissibile (tutti i motivi)</option><option>Estraneità di materia</option><option>Compensazione</option></select></div>',
  '<div class="f"><label for="fo">Esito finale</label><select id="fo"><option value="">Tutti</option><option value="A">Approvato</option><option value="N">Respinto o non votato</option><option value="R">Ritirato</option><option value="I">Inammissibile</option></select></div>'
  '<div class="f"><label for="fs">Ammissibilità</label><select id="fs"><option value="">Tutte</option><option>Ammissibile</option><option value="INAMM">Inammissibile (tutti i motivi)</option><option>Estraneità di materia</option><option>Compensazione</option><option>Altro motivo</option></select></div>'
  '<div class="f"><label for="fy">Manovra</label><select id="fy"><option value="">Tutte nel periodo</option><option>2023</option><option>2024</option><option>2025</option><option>2026</option><option>2027</option></select></div>'
  '<div class="f"><label for="fl">Lettura</label><select id="fl"><option value="">Tutte</option><option value="1">Prima lettura</option><option value="2">Seconda lettura</option></select></div>')
R('<div class="f"><label for="fe">Eletto in (1° firmatario)</label>', '<div class="f"><label for="fe">Regione di elezione</label>')
R('<option value="e3">Costo 2027–29</option>', '<option value="e3">Costo nel triennio</option>')
RX(r'<div class="presets" aria-label="Viste rapide">.*?</div>\n',
   '<div class="presets" aria-label="Viste rapide"><span class="eyebrow">Viste rapide</span>\n'
   '    <button class="btn sm" type="button" data-pre="loc-ap">Soldi a un comune: approvati</button>\n'
   '    <button class="btn sm" type="button" data-pre="loc-est">Soldi a un comune: bocciati come fuori tema</button>\n'
   '    <button class="btn sm" type="button" data-pre="ap">Tutte le approvate</button>\n'
   '    <button class="btn sm" type="button" data-pre="big">Le richieste più costose</button>\n'
   '  </div>\n')
R('<th data-k="ce" scope="col">Eletto in</th>', '<th data-k="y" scope="col">Manovra</th>')
R('title="Somma della spesa chiesta per il 2027, 2028 e 2029, come scritta nell\'emendamento">Costo 2027–29</th>',
  'title="Somma della spesa chiesta per i tre anni della manovra, come scritta nell\'emendamento">Costo triennio</th>')
R('<tr><td colspan="8" class="loading">Caricamento dei 6.558 emendamenti…</td></tr>', '<tr><td colspan="8" class="loading">Caricamento delle proposte di cinque manovre…</td></tr>')

# ---------- classifica ----------
R('<section class="panel" id="rankp" aria-label="Classifica deputati">', '<section class="panel" id="rankp" aria-label="Classifica dei parlamentari">')
R('<h2>Classifica dei deputati per inammissibilità</h2><p class="sub">Su tutti gli emendamenti, contando il deputato come primo firmatario. Non dipende dai filtri della tabella. Clic sul nome per vedere i suoi emendamenti.</p>',
  '<h2>Classifica di deputati e senatori</h2><p class="sub">Sulle proposte del periodo scelto, contando il parlamentare come primo firmatario. Clic sul nome per vedere tutte le sue proposte nell’elenco, con testo, costo, copertura e link alla scheda ufficiale.</p>')
R('<select id="rk"><option value="pi">% inammissibili</option><option value="pe">% estraneità di materia</option><option value="loc">emendamenti per un solo territorio</option><option value="n">numero di emendamenti</option></select>',
  '<select id="rk"><option value="n">proposte presentate</option><option value="ap">proposte approvate</option><option value="pa">% approvate</option><option value="loc">proposte per un solo territorio</option><option value="soldi">euro chiesti per singoli territori</option><option value="pi">% inammissibili</option><option value="pe">% estraneità di materia</option></select>')
R('<div class="f"><label for="rmin">Almeno N emendamenti</label><input id="rmin" type="number" min="1" step="1" value="10"></div>',
  '<div class="f"><label for="rra">Ramo</label><select id="rra"><option value="">Entrambi</option><option>Camera</option><option>Senato</option></select></div><div class="f"><label for="rq">Nome</label><input id="rq" type="search" placeholder="Es. Furfaro"></div><div class="f"><label for="rmin">Almeno N proposte</label><input id="rmin" type="number" min="1" step="1" value="5"></div>')
R('<th>Deputato</th><th style="text-align:right">Emendamenti</th><th style="text-align:right">Inammissibili</th><th style="text-align:right">di cui estraneità</th><th style="text-align:right">Per un solo territorio</th>',
  '<th>Parlamentare</th><th style="text-align:right">Proposte</th><th style="text-align:right">Approvate</th><th style="text-align:right">Inammissibili</th><th style="text-align:right">Per un solo territorio</th><th style="text-align:right">Euro chiesti per territori</th>')

# ---------- mappa ----------
R('<h2 id="maptitle">Dove sarebbero finiti i soldi</h2>', '<h2 id="maptitle">Dove vanno i soldi</h2>')
R('<div class="f"><label for="mdep">Deputato (primo firmatario)</label>', '<div class="f"><label for="mdep">Parlamentare (primo firmatario)</label>')
R('<select id="mes"><option value="">Tutti</option><option value="A">Ammissibili</option><option value="I">Inammissibili (tutti)</option><option value="E">Inammissibili per estraneità</option></select>',
  '<select id="mes"><option value="">Tutti</option><option value="AP">Approvati</option><option value="A">Ammissibili</option><option value="I">Inammissibili (tutti)</option><option value="E">Inammissibili per estraneità</option></select>')
R('<p class="sub">Somme chieste per il 2027–29, inammissibili compresi; un emendamento su più province è diviso in parti uguali; contano tutte le cifre chieste, grandi opere comprese. Popolazione ISTAT al 1° gennaio 2025. <a href="#metodo">Fonti e metodo</a>.</p>',
  '<p class="sub">Somme chieste per i tre anni di ciascuna manovra, inammissibili compresi; sommando più manovre gli importi si accumulano. Un emendamento su più province è diviso in parti uguali; contano tutte le cifre chieste, grandi opere comprese. Popolazione ISTAT al 1° gennaio 2025. <a href="#metodo">Fonti e metodo</a>.</p>')

# ---------- voti ----------
R("{k:'AzIV',lab:'Azione + IV',gs:['Azione','IV']}", "{k:'AzIV',lab:'Azione + IV',gs:['Azione / IV']}")
R('in verticale gli euro per abitante che i suoi deputati chiedono per quella provincia con gli emendamenti alla manovra.</p>',
  'in verticale gli euro per abitante che i suoi parlamentari (Camera e Senato) chiedono per quella provincia con gli emendamenti alle manovre del periodo scelto.</p>')

# ---------- studio statistico + fonti ----------
a = s.index('<div id="view-analisi" class="view" hidden>'); b = s.index('<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/')
s = s[:a] + open('/home/claude/multi/src/multi_analisi.html').read() + '\n</div>\n\n' + s[b:]

# ---------- JS: dati, periodo, testi ----------
R("const CAM='https://documenti.camera.it/apps/emendamenti/getPropostaEmendativa.aspx?contenitorePortante=leg.19.eme.ac.3174-bis&tipoSeduta=1&sedeEsame=referente&urnTestoRiferimento=urn:leg:19:3174:bis:null:com:05:referente&dataSeduta=20261123&idPropostaEmendativa=';",
  "const URN={2023:['643-bis','urn:leg:19:643:bis:null:com:05:referente'],2024:['1627','urn:leg:19:1627:null:null:com:05:referente'],2025:['2112-bis','urn:leg:19:2112:bis:null:com:05:referente'],2026:['2750','urn:leg:19:2750:null:null:com:05:referente'],2027:['3174-bis','urn:leg:19:3174:bis:null:com:05:referente']};\n"
  "const SOBJ={2023:'1368104',2024:'1395344',2025:'1441141',2026:'1477272'};\n"
  "const LINK=r=>{if(!r.lk)return '';if(r.lk.startsWith('S:'))return 'https://www.senato.it/show-doc?leg=19&tipodoc=EMENDC&id='+r.lk.slice(2)+'&idoggetto='+SOBJ[r.y];const [id,pos]=r.lk.split('|');const [c,u]=URN[r.y];return 'https://documenti.camera.it/apps/emendamenti/getPropostaEmendativa.aspx?contenitorePortante=leg.19.eme.ac.'+c+'&tipoSeduta=1&sedeEsame=referente&urnTestoRiferimento='+u+'&dataSeduta=null&idPropostaEmendativa='+encodeURIComponent(id)+'&position='+pos};\n"
  "const TX={},TXL={};function txt(r){if(TX[r.y])return TX[r.y][r.x];if(!TXL[r.y])TXL[r.y]=fetch('testi_'+r.y+'.json').then(x=>x.json()).then(a=>{TX[r.y]=a;renderTable()}).catch(()=>{TX[r.y]=[]});return null}\n"
  "let ALL=null,PA=2023,PB=2027,PRA='';const YEARS=[2023,2024,2025,2026,2027];\n"
  "const perLab=()=>(PA===PB?'manovra '+PA:(PA===2023&&PB===2027?'2023–2027, intera legislatura':'manovre '+PA+'–'+PB))+(PRA?' · '+PRA:'');")
R("const ORDER=['FdI','Lega','FI','Noi Moderati','PD','M5S','AVS','Azione','IV','Misto','Governo'];",
  "const ORDER=['FdI','Lega','FI','Noi Moderati','PD','M5S','AVS','Azione / IV','Autonomie','Misto','Governo'];")
R("const scls=s=>s==='Ammissibile'?'st-ok':(s==='Compensazione'?'st-warn':'st-bad');",
  "const scls=s=>s==='Ammissibile'?'st-ok':(s==='Compensazione'?'st-warn':'st-bad');\nconst OLAB={A:'Approvato',N:'Respinto o non votato',R:'Ritirato',I:'Inammissibile'};\nconst ochip=r=>r.s!=='Ammissibile'?`<span class=\"chip ${scls(r.s)}\">${slbl(r.s,r.pz)}</span>`:(r.o==='A'?'<span class=\"chip st-ap\">Approvato</span>':r.o==='R'?'<span class=\"chip st-warn\">Ritirato</span>':(r.y===2027?'<span class=\"chip\">In esame</span>':'<span class=\"chip\">'+(r.le===2?'Seconda lettura, non approvato':'Non approvato')+'</span>'));")
R("const slbl=(s,pz)=>s==='Ammissibile'?(pz?'Ammissibile (in parte inamm.)':'Ammissibile'):(s==='Compensazione'?'Inamm. compensazione':'Inamm. estraneità')+(pz?' (parz.)':'');",
  "const slbl=(s,pz)=>s==='Ammissibile'?(pz?'Ammissibile (in parte inamm.)':'Ammissibile'):(s==='Compensazione'?'Inamm. compensazione':s==='Altro motivo'?'Inammissibile':'Inamm. estraneità')+(pz?' (parz.)':'');")
R("box.innerHTML='<div class=\"cbh\">'+(q?nf(items.length)+' deputati trovati':nf(items.length)+' deputati · scorri o scrivi')",
  "box.innerHTML='<div class=\"cbh\">'+(q?nf(items.length)+' parlamentari trovati':nf(items.length)+' deputati e senatori · scorri o scrivi')")
R("'<div class=\"cbh\" style=\"position:static;border:0\">Nessun deputato con questo nome</div>'", "'<div class=\"cbh\" style=\"position:static;border:0\">Nessun parlamentare con questo nome</div>'")
R("""fetch('emendamenti.json').then(r=>r.json()).then(j=>{
  T=j.texts; D=j.rows;
  D.forEach(r=>{r._k=numKey(r.i);r._s=(r.i+' '+r.t+' '+T[r.x]+' '+r.f.map(x=>x[0]).join(' ')+' '+r.l.join(' ')).toLowerCase()});""",
"""fetch('emendamenti.json').then(r=>r.json()).then(j=>{
  const C=j.cols;ALL=j.rows.map(a=>{const o={};C.forEach((k,i)=>o[k]=a[i]);o.pr=o.pm;o.d='';o.id_='';o.co='';if(o.f.length&&o.f[0][0]!==o.p&&o.p.startsWith(o.f[0][0]))o.f[0][0]=o.p;return o});D=ALL;
  D.forEach(r=>{r._k=String(r.y)+(r.ra==='Senato'?'S':'C')+numKey(r.i);r._s=(r.i+' '+r.t+' '+r.f.map(x=>x[0]).join(' ')+' '+r.l.join(' ')+' '+r.y+' '+r.ra).toLowerCase()});""")
R("""  try{const s=JSON.parse(localStorage.getItem('emb27-f')||'null');if(s){for(const k in s){const el=$('#'+k);if(!el)continue;if(el.type==='checkbox')el.checked=s[k];else el.value=s[k]}}}catch(e){}
  apply();renderRank();""",
"""  try{const s=JSON.parse(localStorage.getItem('mdl-f')||'null');if(s){for(const k in s){const el=$('#'+k);if(!el)continue;if(el.type==='checkbox')el.checked=s[k];else el.value=s[k]}}}catch(e){}
  let pr='2023-2027|';try{pr=localStorage.getItem('mdl-per')||pr}catch(e){}const [ab,rr]=pr.split('|');const [a0,b0]=ab.split('-').map(Number);setPeriod(a0,b0,rr||'',true);
  apply();renderRank();renderQuadro();""")
R("const IDS=['q','fw','fwm','fg','fc','fs','ft','fr','fp','fe','fa','fcost','fcb','fm','fmx','fpo','fcv','floc','fco'];",
  "const IDS=['q','fw','fwm','fg','fc','fo','fs','fy','fl','ft','fr','fp','fe','fa','fcost','fcb','fm','fmx','fpo','fcv','floc','fco'];\n"
  "function setPeriod(a,b,ra,init){if(a>b)[a,b]=[b,a];PA=a;PB=b;PRA=ra||'';$('#pya').value=a;$('#pyb').value=b;$('#pra').value=PRA;document.querySelectorAll('[data-pr]').forEach(x=>x.setAttribute('aria-pressed',String(x.dataset.pr===a+'-'+b)));\n"
  "  if(!ALL)return;D=ALL.filter(r=>r.y>=a&&r.y<=b&&(!PRA||r.ra===PRA));$('#pnote').textContent=nf(D.length)+' proposte · '+perLab();try{localStorage.setItem('mdl-per',a+'-'+b+'|'+PRA)}catch(e){}\n"
  "  if(init)return;shown=100;openId=null;apply();renderRank();renderQuadro();const v=location.hash.slice(1);if(v==='mappa')renderMap();if(v==='voti')renderVoti();if(v==='analisi')renderAnalisi(); }\n"
  "document.querySelectorAll('[data-pr]').forEach(b=>b.onclick=()=>{const [a,c]=b.dataset.pr.split('-').map(Number);setPeriod(a,c,PRA)});\n"
  "['pya','pyb','pra'].forEach(id=>$('#'+id).onchange=()=>setPeriod(+$('#pya').value,+$('#pyb').value,$('#pra').value));")
R("  try{const o={};IDS.forEach(id=>o[id]=val(id));localStorage.setItem('emb27-f',JSON.stringify(o))}catch(err){}",
  "  try{const o={};IDS.forEach(id=>o[id]=val(id));localStorage.setItem('mdl-f',JSON.stringify(o))}catch(err){}\n  const fo=val('fo'),fy=val('fy'),fl=val('fl');")
R("    if(c&&r.c!==c)return false;", "    if(c&&r.c!==c)return false;\n    if(fo&&r.o!==fo)return false;if(fy&&r.y!=fy)return false;if(fl&&r.le!=fl)return false;")
R("if(key==='i'){A=x._k;B=y._k}", "if(key==='i'){A=x._k;B=y._k}else if(key==='y'){A=x.y;B=y.y}")
# tiles
RX(r"  \$\('#tiles'\)\.innerHTML=\n.*?;\n  // group bars",
   """  const AP=F.filter(r=>r.o==='A').length,LA=L.filter(r=>r.o==='A').length;
  $('#tiles').innerHTML=
   `<div class="tile acc"><b>${nf(n)}</b><span>proposte${n!==D.length?' (filtrate su '+nf(D.length)+')':''} · ${esc(perLab())}</span></div>`+
   `<div class="tile"><b style="color:var(--ok)">${nf(AP)}</b><span>approvate · ${pc(AP,n)}</span></div>`+
   `<div class="tile bad"><b>${pc(inE+inC+F.filter(r=>r.s==='Altro motivo').length,n)}</b><span>inammissibili (${nf(n-F.filter(r=>r.s==='Ammissibile').length)})</span></div>`+
   `<div class="tile"><b>${nf(L.length)}</b><span>per un solo comune o territorio, di cui approvate ${nf(LA)}</span></div>`+
   `<div class="tile"><b>${fmtE(sumL)}</b><span>chiesti per singoli territori (stima, dove calcolabile)</span></div>`;
  // group bars""")
R("F.forEach(r=>{const o=cnt[r.g];if(!o)return;o.t++;if(r.s==='Ammissibile')o.ok++;else if(r.s==='Compensazione')o.c++;else o.e++});",
  "F.forEach(r=>{const o=cnt[r.g];if(!o)return;o.t++;if(r.s==='Ammissibile')o.ok++;else if(r.s==='Compensazione')o.c++;else o.e++});")
R("const sumAll=F.reduce((s,r)=>s+AMT(r),0);\n  $('#cnt').innerHTML=`${nf(n)} emendamenti <small>· totale 2027–29 stimato: ${fmtE(sumAll)} (somma indicativa: gli emendamenti identici si ripetono)</small>`;",
  "const sumAll=F.reduce((s,r)=>s+(r.big?0:(r.e3||r.e||0)),0);\n  $('#cnt').innerHTML=`${nf(n)} proposte <small>· somma dei costi triennali stimati: ${fmtE(sumAll)} (indicativa: proposte identiche si ripetono)</small>`;")
# righe e dettaglio
R("<div class=\"meta\">${esc(r.a)} · ${esc(r.th.join(', '))} · cop.: ${esc(r.cv)}${r.po==='Più territori'?' · più territori':''}</div></td>",
  "<div class=\"meta\">${esc(r.ra)} · ${esc(r.a)} · ${esc(r.th.join(', '))} · cop.: ${esc(r.cv)}${r.po==='Più territori'?' · più territori':''}</div></td>")
R("   <td class=\"loc\">${esc(r.ce)}${r.u?'<div class=\"meta\">'+esc(r.u.replace(/^.* - /,''))+'</div>':''}</td>",
  "   <td class=\"loc\">${r.y}<div class=\"meta\">${r.le===2?'2ª lettura':'1ª lettura'}</div></td>")
R("   <td><span class=\"chip ${scls(r.s)}\">${slbl(r.s,r.pz)}</span></td></tr>`;", "   <td>${ochip(r)}</td></tr>`;")
R("<dt>Esito</dt><dd>${r.s==='Ammissibile'?(r.pz?esc('Ammissibile, '+r.m):'Ammissibile'):esc('Inammissibile per '+r.m)}</dd>",
  "<dt>Manovra</dt><dd>${r.y} · ${esc(r.ra)} · ${r.le===2?'seconda':'prima'} lettura</dd>\n   <dt>Esito</dt><dd>${r.s==='Ammissibile'?(r.o==='A'?'<b>Approvato</b>':esc(OLAB[r.o]))+(r.pz?' · '+esc(r.m):''):esc(r.s==='Altro motivo'?'Inammissibile ('+r.m+')':'Inammissibile per '+r.m)}</dd>")
R("<dt>Fonte</dt><dd><a href=\"${CAM+encodeURIComponent(r.i)+'.&position=20261123'}\" target=\"_blank\" rel=\"noopener\">Scheda ufficiale sul sito della Camera ↗</a></dd>",
  "<dt>Fonte</dt><dd>${LINK(r)?'<a href=\"'+esc(LINK(r))+'\" target=\"_blank\" rel=\"noopener\">Scheda ufficiale sul sito '+(r.ra==='Senato'?'del Senato':'della Camera')+' ↗</a>':'—'}</dd>")
R("<dt>Eletto in</dt><dd>${esc(r.cf||'—')}${r.u?' · uninominale '+esc(r.u):''}</dd>", "<dt>Eletto in</dt><dd>${esc(r.cf||r.ce||'—')}${r.u?' · uninominale '+esc(r.u):''}</dd>")
R("costo 2027–29 ${fmtE(r.e3)}", "costo nel triennio ${fmtE(r.e3)}")
R("<pre class=\"notr\">${hl(esc(T[r.x]))}</pre>", "<pre class=\"notr\">${(()=>{const t=txt(r);return t==null?'Carico il testo…':(t?hl(esc(t)):'Testo non disponibile: apri la scheda ufficiale.')})()}</pre>")
R("const id=(r.id_||'')+r.i;\n  return `<tr class=\"r${openId===r.i+'|'+r.p?' open':''}\" data-k=\"${esc(r.i+'|'+r.p)}\" tabindex=\"0\">",
  "const id=(r.id_||'')+r.i;const ok_=r.y+'|'+r.ra+'|'+r.i;\n  return `<tr class=\"r${openId===ok_?' open':''}\" data-k=\"${esc(ok_)}\" tabindex=\"0\">")
R("rows.map(r=>rowHTML(r)+((openId===r.i+'|'+r.p)?detHTML(r):''))", "rows.map(r=>rowHTML(r)+((openId===r.y+'|'+r.ra+'|'+r.i)?detHTML(r):''))")
# preset
RX(r"document\.querySelectorAll\('\[data-pre\]'\)\.forEach\(b=>b\.onclick=\(\)=>\{const k=b\.dataset\.pre;.*?\n(?=function showView)",
   "document.querySelectorAll('[data-pre]').forEach(b=>b.onclick=()=>{const k=b.dataset.pre;\n"
   "  if(k==='loc-ap')setOnly({floc:true,fo:'A'});else if(k==='loc-est')setOnly({floc:true,fs:'Estraneità di materia'});else if(k==='ap')setOnly({fo:'A'});else if(k==='big'){sortK='e3';sortDir=-1;setOnly({})}});\n")
R("function showView(v){if(!['classifica','mappa','voti','analisi'].includes(v))v='elenco';",
  "function showView(v){if(!['quadro','classifica','mappa','voti','analisi'].includes(v))v='elenco';")
R("if(v==='mappa')renderMap();if(v==='voti')renderVoti();if(v==='analisi')renderAnalisi();}",
  "if(v==='mappa')renderMap();if(v==='voti')renderVoti();if(v==='analisi')renderAnalisi();if(v==='quadro')renderQuadro();}")
# colori
R("const PCOL_L={'FdI':'#257de0','Lega':'#008a17','FI':'#38b6e8','Noi Moderati':'#6a4ce2','PD':'#ec4647','M5S':'#f2a600','AVS':'#ee7fac','Azione':'#1b64be','IV':'#f47230','Misto':'#8a8f98'};",
  "const PCOL_L={'FdI':'#257de0','Lega':'#008a17','FI':'#38b6e8','Noi Moderati':'#6a4ce2','PD':'#ec4647','M5S':'#f2a600','AVS':'#ee7fac','Azione / IV':'#1b64be','Autonomie':'#4f8a8b','Misto':'#8a8f98'};")
R("const PCOL_D={'FdI':'#338ced','Lega':'#0aac23','FI':'#1fa5c9','Noi Moderati':'#7d6cf0','PD':'#ec4647','M5S':'#d28e05','AVS':'#e86f9e','Azione':'#6f86c9','IV':'#e76624','Misto':'#8b93a3'};",
  "const PCOL_D={'FdI':'#338ced','Lega':'#0aac23','FI':'#1fa5c9','Noi Moderati':'#7d6cf0','PD':'#ec4647','M5S':'#d28e05','AVS':'#e86f9e','Azione / IV':'#6f86c9','Autonomie':'#6fa3a3','Misto':'#8b93a3'};")
# soglie mappa scalate col numero di manovre
R("function rampIdx(v){const m=$('#mmis').value,th=m==='n'?TH_N:(m==='pc'?TH_PC:TH_SOLDI);",
  "const NY=()=>D?new Set(D.map(r=>r.y)).size||1:1;const SC=a=>a.map(x=>x*NY());\nfunction rampIdx(v){const m=$('#mmis').value,th=SC(m==='n'?TH_N:(m==='pc'?TH_PC:TH_SOLDI));")
R("if(es==='A'&&r.s!=='Ammissibile')return;if(es==='I'&&r.s==='Ammissibile')return;if(es==='E'&&r.s!=='Estraneità di materia')return;",
  "if(es==='AP'&&r.o!=='A')return;if(es==='A'&&r.s!=='Ammissibile')return;if(es==='I'&&r.s==='Ammissibile')return;if(es==='E'&&r.s!=='Estraneità di materia')return;")
R("const esT={A:'ammessi al voto',I:'dichiarati inammissibili',E:'dichiarati fuori tema'}[es]||'';", "const esT={AP:'approvati',A:'ammessi al voto',I:'dichiarati inammissibili',E:'dichiarati fuori tema'}[es]||'';")
R("((mm==='n'?{A:' (solo ammessi)',I:' (solo inammissibili)',E:' (solo fuori tema)'}:{A:' con emendamenti ammessi',I:' con emendamenti inammissibili',E:' con emendamenti fuori tema'})[es]||'')",
  "((mm==='n'?{AP:' (solo approvati)',A:' (solo ammessi)',I:' (solo inammissibili)',E:' (solo fuori tema)'}:{AP:' con emendamenti approvati',A:' con emendamenti ammessi',I:' con emendamenti inammissibili',E:' con emendamenti fuori tema'})[es]||'')+' · '+perLab()")
R("${fmtM(eurZ)}</b> nel 2027–29, in", "${fmtM(eurZ)}</b> (${esc(perLab())}), in")
R("'Euro chiesti per abitante, 2027–29':'Euro chiesti 2027–29'", "'Euro chiesti per abitante · '+perLab():'Euro chiesti · '+perLab()")
R("const lab=mm_==='n'?['1','2','3','4–5','6–8','9–15',Lf('oltre {0}','15')]:(mm_==='pc'?[Lf('fino a {0}','10 €'),'10–50 €','50–100 €','100–250 €','250–500 €','500–'+k1+' €',Lf('oltre {0}',k1+' €')]:[Lf('fino a {0}','5'+mU),'5–20'+mU,'20–50'+mU,'50–100'+mU,'100–250'+mU,'250'+mU+'–1'+bU,Lf('oltre {0}','1'+bU)]);",
  "const thS=SC(mm_==='n'?TH_N:(mm_==='pc'?TH_PC:TH_SOLDI));const fv=v=>mm_==='n'?nf(v):(mm_==='pc'?nf(v)+' €':fmtM(v));const lab=[(mm_==='n'?'1–':'fino a ')+fv(thS[0])].concat(thS.slice(1).map((t,i)=>fv(thS[i])+'–'+fv(t))).concat(['oltre '+fv(thS[thS.length-1])]);")
R("o.rows.slice().sort((a,b)=>(b.e3||b.e||0)-(a.e3||a.e||0))", "o.rows.slice().sort((a,b)=>(b.o==='A')-(a.o==='A')||(b.e3||b.e||0)-(a.e3||a.e||0))")
R("${fmtE(r.e3||r.e)} · ${r.s==='Ammissibile'?'ammissibile':'inammissibile'}</div></div>", "${r.y} · ${esc(r.ra)} · ${fmtE(r.e3||r.e)}${r.big?' (esclusa dalle somme)':''} · ${r.s!=='Ammissibile'?'inammissibile':r.o==='A'?'<b>approvato</b>':'non approvato'}</div></div>")
R("if(es==='A')o2.fs='Ammissibile';if(es==='I')o2.fs='INAMM';if(es==='E')o2.fs='Estraneità di materia';setOnly(o2)};",
  "if(es==='AP')o2.fo='A';if(es==='A')o2.fs='Ammissibile';if(es==='I')o2.fs='INAMM';if(es==='E')o2.fs='Estraneità di materia';setOnly(o2)};")
# classifica
RX(r"function renderRank\(\)\{\n.*?\n\}\n\$\('#rk'\)\.addEventListener\('change',renderRank\);\$\('#rg2'\)\.addEventListener\('change',renderRank\);\$\('#rmin'\)\.addEventListener\('input',renderRank\);",
   """function renderRank(){
  if(!D)return;const by={};const gsel=$('#rg2').value,rra=$('#rra').value,rq=fold($('#rq').value.trim());
  D.forEach(r=>{if(r.g==='Governo'||(gsel&&r.g!==gsel)||(rra&&r.ra!==rra))return;if(rq&&!fold(r.p).includes(rq))return;const k=r.p+'|'+r.ra;const o=by[k]||(by[k]={p:r.p,ra:r.ra,g:r.g,gs:new Set(),n:0,i:0,e:0,loc:0,soldi:0,ap:0});o.n++;o.gs.add(r.g);o.g=r.g;if(r.s!=='Ammissibile')o.i++;if(r.s==='Estraneità di materia')o.e++;if(r.o==='A')o.ap++;if(r.loc){o.loc++;o.soldi+=AMT(r)}});
  const min=Math.max(1,parseInt($('#rmin').value)||1),k=$('#rk').value;
  let L=Object.values(by).filter(o=>o.n>=min);
  const key=o=>k==='pi'?o.i/o.n:k==='pe'?o.e/o.n:k==='pa'?o.ap/o.n:(o[k]||0);
  L.sort((a,b)=>key(b)-key(a)||b.n-a.n);
  const tot=L.length;const rows=rankAll?L:L.slice(0,30);
  $('#rankb').innerHTML=rows.length?rows.map((o,ix)=>`<tr><td class="pos">${ix+1}</td><td><button class="who" type="button" data-who="${esc(o.p)}">${esc(o.p)}</button> ${[...o.gs].map(g=>'<span class="chip '+gcls(g)+'">'+esc(g)+'</span>').join(' ')} <span class="meta">${esc(o.ra)}</span></td><td class="n">${nf(o.n)}</td><td class="n">${nf(o.ap)} <span class="meta">${pc(o.ap,o.n)}</span></td><td class="n"><span class="minibar" style="width:${Math.round(o.i/o.n*60)}px"></span>${pc(o.i,o.n)}</td><td class="n">${nf(o.loc)}</td><td class="n">${fmtE(o.soldi)}</td></tr>`).join(''):'<tr><td colspan="7" class="meta">Nessun parlamentare con questi criteri. Abbassa la soglia o cambia nome.</td></tr>';
  $('#rall').textContent=rankAll?'Mostra i primi 30':'Mostra tutti ('+tot+')';
  document.querySelectorAll('#rankb .who').forEach(b=>b.onclick=()=>setOnly({fw:b.dataset.who}));
}
['rk','rg2','rra'].forEach(id=>$('#'+id).addEventListener('change',renderRank));['rmin','rq'].forEach(id=>$('#'+id).addEventListener('input',renderRank));""")
# CSV
R("const ESITO=r=>r.s==='Ammissibile'?(r.pz?'Ammissibile, in parte inammissibile':'Ammissibile'):(r.s==='Compensazione'?'Inammissibile per compensazione':'Inammissibile per estraneità di materia')+(r.pz?' (solo una parte)':'');",
  "const ESITO=r=>r.s==='Ammissibile'?(r.pz?'Ammissibile, in parte inammissibile':'Ammissibile'):(r.s==='Compensazione'?'Inammissibile per compensazione':r.s==='Altro motivo'?'Inammissibile':'Inammissibile per estraneità di materia')+(r.pz?' (solo una parte)':'');")
RX(r"const EM_HEAD=\[.*?\];\nconst emRow=r=>\[.*?\];",
   "const EM_HEAD=['Manovra','Ramo','Lettura','Emendamento','Articolo del ddl','Oggetto','Primo firmatario','Gruppo del primo firmatario','Schieramento','Numero di firmatari','Firmatari (gruppo)','Regione di elezione del primo firmatario','Ammissibilità','Esito finale','Motivo di inammissibilità','Portata','Comuni o luoghi citati','Province citate','Regioni citate','Tema','Costo annuo (euro)','Anno a cui si riferisce il costo annuo','Costo nel triennio (euro)','Esclusa dalle somme (non chiede soldi nuovi)','Copertura indicata','Scheda ufficiale'];\n"
   "const emRow=r=>[r.y,r.ra,r.le===2?'seconda':'prima',r.i,r.a,r.t,r.p,r.g,r.c,r.f.length,r.f.map(x=>x[0]+' ('+x[1]+')').join(', '),r.cf||r.ce||'',ESITO(r),OLAB[r.o],r.m||'',r.po,r.l.join(', '),r.pr.join(', '),r.rg.join(', '),r.th.join(', '),r.e||null,r.e?(r.ey||'non individuato nel testo'):'',r.e3||null,r.big?'sì':'no',r.cv,LINK(r)];")
R("'emendamenti-manovra-2027-filtrati-'+n+'.csv'", "'emendamenti-manovre-'+PA+'-'+PB+'-filtrati-'+n+'.csv'")
R("saveCSV($('#csva'),'emendamenti-manovra-2027-tutti.csv'", "saveCSV($('#csva'),'emendamenti-manovre-'+PA+'-'+PB+'-tutti.csv'")
R("'deputati-inammissibilita-manovra-2027.csv',csvBuild(['Deputato (primo firmatario)',", "'parlamentari-manovre-'+PA+'-'+PB+'.csv',csvBuild(['Parlamentare (primo firmatario)',")
R("'Euro chiesti 2027-2029 (quota attribuita)'", "'Euro chiesti nel periodo (quota attribuita)'")
R("'Euro chiesti da '+g.lab+' 2027-2029'", "'Euro chiesti da '+g.lab+' ('+perLab()+')'")
R("'Euro chiesti per singoli territori 2027-2029'", "'Euro chiesti per singoli territori nel periodo'")
# immagine e fonti
R("x.fillText(L('EMENDAMENTI ALLA MANOVRA 2027 · ELABORAZIONE SU DATI CAMERA DEI DEPUTATI E ISTAT'),P,y+12)",
  "x.fillText(('EMENDAMENTI ALLE MANOVRE · '+perLab()+' · DATI CAMERA, SENATO E ISTAT').toUpperCase(),P,y+12)")
RX(r"function srcText\(es\)\{return Lf\(.*?\)\}\n",
   "function srcText(es){return 'Fonti: Camera dei deputati e Senato della Repubblica, fascicoli ed elenchi delle proposte emendative alle leggi di bilancio 2023–2027 (commissioni Bilancio); ISTAT, popolazione al 1° gennaio 2025. Cifre chieste dai proponenti per il triennio di ciascuna manovra'+(es?'':', inammissibili comprese')+'; '+perLab()+'. Solo proposte che citano un luogo preciso; se ne citano più d’uno, i soldi sono divisi in parti uguali. Esclusi i fondi nazionali; grandi opere comprese.'}\n")
RX(r"function renderAnalisi\(\)\{if\(!AN\).*?\n(?=var I18=null)", '')

# ---------- i18n: periodi come token tradotti, nuovi gruppi ----------
R("const set=new Set(['Azione + IV','Noi Moderati',", "const set=new Set(['Azione / IV','Autonomie','Azione + IV','Noi Moderati',")
R("const re=new RegExp(\"(?<![\\\\p{L}\\\\d'’])(?:\"+names+\")",
  "const re=new RegExp(\"(?<![\\\\p{L}\\\\d])(?:\\\\d{4}–\\\\d{4}, intera legislatura|manovre \\\\d{4}–\\\\d{4}|manovra \\\\d{4})(?: · (?:Camera|Senato))?|(?<![\\\\p{L}\\\\d'’])(?:\"+names+\")")
R("return t!=null?t.replace(/\\{(\\d+)\\}/g,(_,i)=>vals[+i]):null}", "return t!=null?t.replace(/\\{(\\d+)\\}/g,(_,i)=>trTok(vals[+i])):null}")

R('<a class="sb-x" href="https://claude.ai/artifact/PAuWEiKeqcTfEX1DMy16PH">Tutte le manovre 2023–2027 →</a>', '<a class="sb-x" href="https://claude.ai/artifact/D5WQFUaW1R2Z67CGSseZGe">Manovra 2027 nel dettaglio →</a>')
# i18n spento
R("function loadI18(){if(I18)return Promise.resolve(I18);", "function loadI18(){if(LANG==='it')return Promise.resolve(null);if(I18)return Promise.resolve(I18);")
# nuove funzioni (quadro e studio) prima della chiusura
i = s.rindex('})();')
s = s[:i] + open('/home/claude/multi/src/multi_extra.js').read() + '\n' + s[i:]
open(OUT, 'w').write(s)
print('ok', len(s))
