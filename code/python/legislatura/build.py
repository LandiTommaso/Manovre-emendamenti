"""Unifica gli emendamenti alle leggi di bilancio 2023-2027 (Camera e Senato) in un unico dataset.
Una riga = una proposta emendativa (numero base; le riformulazioni sono fuse nella stessa riga)."""
import json, re, html, collections, sys
sys.path.insert(0, '/home/claude/multi/src')
import textan as T
BIGRE = r"collegamento stabile tra la Sicilia|[Pp]onte sullo [Ss]tretto|[Ss]ociet[àa] Stretto di Messina|[Rr]imodula"

B = '/home/claude/multi/'
LIST = json.load(open(B + 'out/camera_liste.json'))
SEN = json.load(open(B + 'out/senato_raw.json'))
X = json.load(open(B + 'raw/camera_testi_deputati.json'))
TXT, DEP = X['T'], X['DEP']
SJ = json.load(open(B + 'raw/senato_senatori_gruppi.json'))

# ---------------- gruppi ----------------
FAM = ['FdI', 'Lega', 'FI', 'Noi Moderati', 'PD', 'M5S', 'AVS', 'Azione / IV', 'Autonomie', 'Misto', 'Governo / relatori']
MAGG = {'FdI', 'Lega', 'FI', 'Noi Moderati'}
OPP = {'PD', 'M5S', 'AVS', 'Azione / IV'}
def coal(f):
    return 'Maggioranza' if f in MAGG else 'Opposizione' if f in OPP else 'Governo / relatori' if f == 'Governo / relatori' else 'Altri'

def fam_camera(sig):
    s = sig.upper()
    if s.startswith('FDI'): return 'FdI'
    if s.startswith('LEGA'): return 'Lega'
    if s.startswith('FI'): return 'FI'
    if s.startswith('NM'): return 'Noi Moderati'
    if s.startswith('PD'): return 'PD'
    if s.startswith('M5S'): return 'M5S'
    if s.startswith('AVS'): return 'AVS'
    if s.startswith(('AZ', 'A-IV', 'IV')): return 'Azione / IV'
    return 'Misto'

# deputati: idPersona -> [(inizio, fine, famiglia, cognome nome)]
DEPG = collections.defaultdict(list)
for d in DEP:
    pid = re.search(r'/d(\d+)_19', d['d']).group(1)
    DEPG[pid].append((d['ini'], d.get('fin', '99999999'), fam_camera(d['sigla']), (d['cog'] + ' ' + d['nome']).title()))
def dep_group(pid, date):
    c = DEPG.get(pid)
    if not c: return None, None
    for a, b, f, n in sorted(c):
        if a <= date <= b: return f, n
    return sorted(c)[-1][2], sorted(c)[-1][3]

# senatori: id -> [(inizio, fine, gid)] ; componenti del Misto note
SGID = {'85': 'FdI', '56': 'FI', '49': 'PD', '33': 'Lega', '71': 'M5S', '91': 'Azione / IV', '92': 'Noi Moderati', '69': 'Autonomie', '9': 'Misto'}
MISTO_COMP = {'Magni': 'AVS', 'De Cristofaro': 'AVS', 'Cucchi': 'AVS', 'Floridia': 'AVS', 'Calenda': 'Azione / IV', 'Lombardo': 'Azione / IV'}
SENG = collections.defaultdict(list); SNAME = {}; SREG = {}; SCOG = {}
for a in SJ['A']:
    sid = a['s'].split('/')[-1]
    SENG[sid].append((a['inizio'], a.get('fine', '9999-99-99'), SGID.get(a['g'].split('/')[-1], 'Misto')))
    SNAME[sid] = a['cog'] + ' ' + a['nome']; SREG[sid] = a.get('reg', ''); SCOG[sid] = a['cog']
def sen_group(sid, date):
    c = SENG.get(sid)
    if not c: return None
    f = None
    for a, b, g in sorted(c):
        if a <= date <= b: f = g
    if f is None: f = sorted(c)[-1][2]
    if f == 'Misto':
        cog = SCOG.get(sid, '')
        f = MISTO_COMP.get(cog, 'Misto')
    return f

def norm_esito(e):
    e = (e or '').lower()
    if e.startswith(('approvat', 'accolt')): return 'Approvato'
    if 'inammissibil' in e: return 'Inammissibile'
    if e.startswith('ritirat'): return 'Ritirato'
    return 'Non approvato'

# ---------------- analisi del testo ----------------
COVP = [('FISPE (DL 282/2004)', r"10,? comma 5,? del decreto-legge 29 novembre 2004"),
 ('Fondo esigenze indifferibili (L. 190/2014)', r"comma 200,? della legge 23 dicembre 2014"),
 ('Fondi speciali (Tab. A/B)', r"fondo speciale|[Tt]abella [AB]\b"),
 ('Tagli a stati di previsione', r"\bCP:\s*-"),
 ('Nuove entrate', r"maggiori entrate|aliquota|accisa|prelievo|contributo di solidariet|imposta (?:sostitutiva|straordinaria)"),
 ('Riduzione di altre spese/fondi', r"riduzione (?:delle dotazioni|lineare|dello stanziamento|del [Ff]ondo|dell.autorizzazione)|è ridott[oa]|sono ridott"),
 ('Risorse già stanziate / rimodulazione', r"a valere (?:sulle|sulla|sul|nell)|nell.ambito delle risorse|nei limiti delle risorse|risorse (?:già )?(?:disponibili|previste|stanziate)"),
 ('Senza oneri dichiarati', r"nuovi o maggiori oneri|invarianza finanziaria")]
def cov(t):
    for k, (n_, p_) in enumerate(COVP):
        if re.search(p_, t if k < 4 else t[-2500:]): return n_
    return 'Non indicata'
def analyze(text, y0):
    T.set_years(y0)
    amt, amt3, prof = T.amounts_body(text, False)
    tplace = re.split(r"(?:\n|\. )(?:Conseguentemente|Agli oneri|Ai relativi oneri|Ai maggiori oneri|All.onere|Alla copertura)", text)[0]
    tplace = re.sub(r"[Ss]tretto di Messina|Ponte sullo Stretto|[Cc]ircumetnea|(?:[Pp]iazza|[Pp]iazzale|[Vv]ia|[Vv]iale|[Cc]orso|[Ll]argo) [A-Z][\w'’]+|sede (?:legale |operativa )?(?:in|a) [A-Z][\w'’]+", " ", tplace)
    pl, _ = T.find_places(tplace)
    if re.search(r"\bnazional[ei]\b", tplace[:300]) and len(pl) <= 2 and not re.search(r"(?:comune|città|provincia) di [A-Z]", tplace[:900]):
        pl = []
    nreg = len(set(p['regione'] for p in pl))
    portata = 'Nazionale' if not pl else ('Più territori' if len(pl) >= 6 and nreg >= 3 else 'Locale')
    pm = sorted(set(p['provincia'] for p in pl)) if portata == 'Locale' else []
    big = bool(re.search(BIGRE, text)) or (amt3 or amt or 0) > 1e9  # stessa regola in emend/src/export.py
    ey = ''
    if prof:
        ys_ = sorted(prof); vs_ = [prof[y] for y in ys_]
        ey = 'ogni anno' if len(set(vs_)) == 1 and len(ys_) >= 3 else str(max(prof, key=prof.get))
    return dict(e=amt, e3=amt3, ey=ey, l=[p['nome'] for p in pl][:8], pm=pm, po=portata, th=T.theme(None, text), big=1 if big else 0, cv=cov(text), tx=text)

URN = {'C643bis': ('643-bis', 'urn:leg:19:643:bis:null:com:05:referente'), 'C1627': ('1627', 'urn:leg:19:1627:null:null:com:05:referente'),
       'C2112bis': ('2112-bis', 'urn:leg:19:2112:bis:null:com:05:referente'), 'C2750': ('2750', 'urn:leg:19:2750:null:null:com:05:referente'),
       'C3174bis': ('3174-bis', 'urn:leg:19:3174:bis:null:com:05:referente')}
SLINK = json.load(open(B + 'raw/senato_link_emendamenti.json')); SLM = {}
SOBJ = {'S442': '1368104', 'S926': '1395344', 'S1330': '1441141', 'S1689': '1477272'}
for k_, L_ in SLINK.items():
    for lab, eid in L_:
        lab = re.sub(r'\s+', ' ', lab).strip()
        SLM.setdefault((k_, lab), eid)
        SLM.setdefault((k_, re.sub(r'\s*\((?:testo|nuovo testo)[^)]*\)$', '', lab).strip()), eid)
def link(ramo, src, i):
    if ramo == 'Camera':
        c, urn = URN[src]; raw, pos = L_POS.get((src, i), (i + '.', None))
        if pos is None: return ''
        return f'https://documenti.camera.it/apps/emendamenti/getPropostaEmendativa.aspx?contenitorePortante=leg.19.eme.ac.{c}&tipoSeduta=1&sedeEsame=referente&urnTestoRiferimento={urn}&dataSeduta=null&idPropostaEmendativa={raw}&position={pos}'
    eid = SLM.get((src, i))
    return f'https://www.senato.it/show-doc?leg=19&tipodoc=EMENDC&id={eid}&idoggetto={SOBJ[src]}' if eid else ''
rows = []
def add(**k):
    k['link'] = link(k['ramo'], k['atto'], k['id']); k.setdefault('cv', 'Non indicata'); k.setdefault('tx', ''); k.setdefault('ey', '')
    if not k.get('art'):
        m_ = re.match(r'(?:Tab\.?[A-Z]?\.?)?(\d+)', k['id'], re.I); k['art'] = ('Art. ' + m_.group(1)) if m_ else ''
    k['p'] = re.sub(r'\s+', ' ', (k.get('p') or '').replace('\xa0', ' ')).strip(); k['coal'] = coal(k['g']); rows.append(k)

# ---------------- Camera ----------------
CAM_DATE = {'C643bis': '20221214', 'C643bisA': '20221220', 'C1627': '20231227', 'C2112bis': '20241115', 'C2750': '20251229', 'C3174bis': '20261123'}
# esiti dalle liste ufficiali (per numero base; approvato se una qualsiasi formulazione è approvata)
def base_id(i): return re.sub(r'\.$', '', i.strip()).replace('(Nuova formulazione)', '').strip().rstrip('.')
L_ES = collections.defaultdict(set); L_PID = {}; L_ART = {}; L_POS = {}
for r in LIST:
    if r['sede'] == 'Aula': continue
    src = 'C643bis' if r['src'].startswith('C643bis') else r['src']
    k = (src, base_id(r['id']))
    L_ES[k].add(r['esito']); L_ART[k] = r['art']
    if k not in L_POS: L_POS[k] = (r['id'].strip(), r['pos'])
    if r['idp'] and k not in L_PID: L_PID[k] = (r['idp'], r['primo'])
    elif not r['idp'] and k not in L_PID: L_PID[k] = (None, r['primo'])

def cam_esito(src, i):
    es = L_ES.get((src, i), set())
    return 'Approvato' if 'approvato' in es else 'Inammissibile' if 'inammissibile' in es else 'Ritirato' if 'ritirato' in es else 'Non approvato'

def gov_fam(name):
    n = (name or '').lower()
    if n.startswith(('il governo', 'i relatori', 'il relatore', 'la relatrice', 'le relatrici', 'governo', 'relator')): return 'Governo / relatori'
    if re.match(r'la [ivxl]+ commissione', n): return 'Governo / relatori'  # pareri/emendamenti delle commissioni
    return None

META_C = {'C643bis': (2023, 1), 'C1627': (2024, 2), 'C2112bis': (2025, 1), 'C2750': (2026, 2), 'C3174bis': (2027, 1)}
# 2024, 2025, 2027: fascicolo completo
import os
def _strip(h):
    h = re.sub(r'<br\s*/?>|</p>|</li>', '\n', h); h = re.sub(r'<[^>]+>', '', h)
    h = html.unescape(h).replace('\xa0', ' '); h = re.sub(r'[ \t]+', ' ', h); return re.sub(r'\n\s*', '\n', h).strip()
APPROVED_TXT = {}
if os.path.exists(B + 'raw/camera_approvati_2025.json'):
    for k, v in sorted(json.load(open(B + 'raw/camera_approvati_2025.json')).items(), key=lambda kv: kv[0].split('|')[2]):
        s_, i_, pos_ = k.split('|')
        m_ = re.search(r'<div class="testo">(.*?)</div>\s*<div class="proponenti', v, re.S)
        if m_: APPROVED_TXT[(s_, base_id(i_))] = _strip(m_.group(1))
FAS = {'C1627': B + 'out/rows_C1627.json', 'C2112bis': B + 'out/rows_C2112bis.json', 'C3174bis': '/home/claude/emend/data/rows.json'}
seen = set()
for src, path in FAS.items():
    anno, lett = META_C[src]
    for r in json.load(open(path)):
        i = r['id']
        if (src, i) in seen: continue
        seen.add((src, i))
        pid, primo = L_PID.get((src, i), (None, r['primo']))
        g = gov_fam(primo)
        if not g:
            g, nm = dep_group(pid, CAM_DATE[src]) if pid else (None, None)
            if not g: g = {'Azione': 'Azione / IV', 'IV': 'Azione / IV'}.get(r['gruppo'], r['gruppo'] if r['gruppo'] in FAM else 'Misto')
        es = cam_esito(src, i)
        if es == 'Non approvato' and r['stato'] == 'Inammissibile': es = 'Inammissibile'
        if src == 'C3174bis' and es == 'Inammissibile' and r['stato'] != 'Inammissibile': es = 'Non approvato'  # riesame 24/11 e Bollettino n. 768 (emend/src/riesame.py)
        txt_ = r['testo']
        if es == 'Approvato' and (src, i) in APPROVED_TXT: txt_ = APPROVED_TXT[(src, i)]
        a = analyze(txt_, anno)
        add(anno=anno, ramo='Camera', lett=lett, atto=src, id=i, art=r.get('art', ''), p=primo, pid=pid, g=g, nf=len(r['firm']), es=es,
            mot=html.unescape(r['motivo']), ce=r.get('circ', ''), cf=r.get('circFull', ''), u=r.get('uni') or '',
            f=[[x['n'], {'Azione': 'Azione / IV', 'IV': 'Azione / IV'}.get(x['g'], x['g'])] for x in r.get('firmInfo', [])],
            tt=r.get('titolo') or '', **a)
# 2023 e 2026: testi singoli dal sito della Camera
def strip(h):
    h = re.sub(r'<br\s*/?>|</p>|</li>', '\n', h); h = re.sub(r'<[^>]+>', '', h)
    h = html.unescape(h).replace('\xa0', ' '); h = re.sub(r'[ \t]+', ' ', h); return re.sub(r'\n\s*', '\n', h).strip()
by_key = collections.defaultdict(list)
for k, v in TXT.items():
    s, i, pos = k.split('|'); s = 'C643bis' if s.startswith('C643bis') else s
    by_key[(s, base_id(i))].append((pos, v))
for (src, i), vs in by_key.items():
    anno, lett = META_C[src]
    if (src, i) in seen: continue
    seen.add((src, i))
    vs.sort()
    es = cam_esito(src, i)
    v = vs[-1][1] if es == 'Approvato' else vs[0][1]
    m = re.search(r'<div class="testo">(.*?)</div>\s*<div class="proponenti', v, re.S) or re.search(r'<div class="testo">(.*?)</div>', v, re.S)
    text = strip(m.group(1)) if m else strip(v)
    fm = re.search(r'<div class="proponenti">(.*?)</div>', v, re.S)
    nf = len([x for x in strip(fm.group(1)).split(',') if x.strip()]) if fm else 1
    fl = []
    if fm:
        for pid_, nm_ in re.findall(r'idPersona=(\d+)[^>]*>([^<]+)</a>', fm.group(1)):
            fl.append([html.unescape(nm_).strip(), (dep_group(pid_, CAM_DATE[src])[0] or 'Misto')])
    pid, primo = L_PID.get((src, i), (None, ''))
    g = gov_fam(primo) or (dep_group(pid, CAM_DATE[src])[0] if pid else None) or 'Misto'
    a = analyze(text, anno)
    add(anno=anno, ramo='Camera', lett=lett, atto=src, id=i, art=L_ART.get((src, i)) or '', p=primo, pid=pid, g=g, nf=nf, es=es, mot='', ce='', f=fl, **a)
# righe di lista senza testo (es. riformulazioni non scaricate)
for (src, i), es_ in L_ES.items():
    if (src, i) in seen or src not in META_C: continue
    seen.add((src, i)); anno, lett = META_C[src]
    pid, primo = L_PID.get((src, i), (None, ''))
    g = gov_fam(primo) or (dep_group(pid, CAM_DATE[src])[0] if pid else None) or 'Misto'
    if (src, i) in APPROVED_TXT:
        add(anno=anno, ramo='Camera', lett=lett, atto=src, id=i, p=primo, pid=pid, g=g, nf=1, es=cam_esito(src, i), mot='', ce='', **analyze(APPROVED_TXT[(src, i)], anno))
    else:
        add(anno=anno, ramo='Camera', lett=lett, atto=src, id=i, p=primo, pid=pid, g=g, nf=1, es=cam_esito(src, i), mot='', ce='',
            e=None, e3=None, l=[], pm=[], po='Nazionale', th=['Altro'], notext=1, big=0)

# ---------------- Senato ----------------
grp = collections.defaultdict(list)
for r in SEN: grp[(r['src'], r['id'])].append(r)
for (src, i), vs in grp.items():
    r0 = vs[-1]  # versione originale (l'ordine del fascicolo è testo N ... testo 1)
    anno, lett, date = r0['anno'], r0['lettura'], r0['data']
    ess = [norm_esito(v['esito']) for v in vs]
    es = 'Approvato' if 'Approvato' in ess else 'Inammissibile' if 'Inammissibile' in ess else 'Ritirato' if 'Ritirato' in ess else 'Non approvato'
    v = next((v for v in vs if norm_esito(v['esito']) == 'Approvato'), r0) if es == 'Approvato' else r0
    primo, sid = (v['firm'][0] if v['firm'] else ('', None))
    g = gov_fam(primo) or (sen_group(sid, date) if sid else None) or 'Misto'
    a = analyze(v['testo'], anno)
    add(anno=anno, ramo='Senato', lett=lett, atto=src, id=i, p=SNAME.get(sid, primo),
        pid=sid, g=g, nf=len(v['firm']), es=es, mot=v['esito'] if es == 'Inammissibile' else '', ce=SREG.get(sid, '') if sid else '',
        f=[[SNAME.get(x[1], x[0]) if x[1] else x[0], (sen_group(x[1], date) if x[1] else 'Misto')] for x in v['firm']], **a)

json.dump(rows, open(B + 'out/multi_rows.json', 'w'), ensure_ascii=False)
c = collections.Counter((r['anno'], r['ramo'], r['lett']) for r in rows)
for k in sorted(c):
    sub = [r for r in rows if (r['anno'], r['ramo'], r['lett']) == k]
    print(k, c[k], dict(collections.Counter(r['es'] for r in sub)), 'loc', sum(r['po'] == 'Locale' for r in sub), 'notext', sum(r.get('notext', 0) for r in sub))
print(collections.Counter(r['g'] for r in rows).most_common())
