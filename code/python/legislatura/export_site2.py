"""Esporta i dati 2023-2027 nello schema del sito 2027 (emendamenti.json) + testi per manovra (testi_ANNO.json)."""
import json, re, collections
B = '/home/claude/multi/'
R = json.load(open(B + 'out/multi_rows.json'))
topo = json.load(open('/home/claude/emend/site/province.topo.json'))
REG = {g['properties']['prov_name']: g['properties']['reg_name'] for g in topo['objects']['provinces']['geometries']}
GMAP = {'Governo / relatori': 'Governo'}
CMAP = {'Maggioranza': 'Maggioranza', 'Opposizione': 'Opposizione'}
def scat(r):
    if r['es'] != 'Inammissibile':
        mo = r.get('mot') or ''
        return 'Ammissibile', (mo.replace('Parzialmente: Inammissibile per ', 'parzialmente inammissibile: ') if mo.startswith('Parzialmente') else '')
    m = (r.get('mot') or '').lower()
    if 'estrane' in m and '(e per estraneit' not in m: return 'Estraneità di materia', r['mot'].replace('Inammissibile per ', '')
    if 'compensaz' in m or 'copertura' in m: return 'Compensazione', r['mot'].replace('Inammissibile per ', '')
    return 'Altro motivo', (r.get('mot') or 'motivo non indicato nel fascicolo')
def title(r):
    if r.get('tt'): return r['tt'], 0
    t = r.get('tx') or ''
    m = re.search(r"Art\.\s*\d+[-\w]*\.?\s*\n?\s*\(([^)]{5,160})\)", t[:400])
    if m: return m.group(1).strip(), 0
    t2 = re.sub(r'^\s*(?:Al|All[ao]?|Alla|Dopo|Sopprimere|Sostituire|Aggiungere)[^:]{0,160}:\s*', '', t.replace('\n', ' ')).strip()
    t2 = re.sub(r'\s+', ' ', t2)
    return (t2[:110].rsplit(' ', 1)[0] + '…') if len(t2) > 110 else (t2 or '(testo non disponibile)'), 1
OUT = {'A': 'Approvato', 'I': 'Inammissibile', 'R': 'Ritirato', 'N': 'Respinto o non votato'}
ESC = {'Approvato': 'A', 'Inammissibile': 'I', 'Ritirato': 'R', 'Non approvato': 'N'}
rows = []; texts = collections.defaultdict(list); tidx = collections.defaultdict(dict)
for r in R:
    s, m = scat(r)
    t, ta = title(r)
    tx = r.get('tx') or ''
    loc = r['po'] == 'Locale'
    lim = 4000 if (loc or r['po'] != 'Nazionale' or r['es'] == 'Approvato') else 1500
    tt = tx if len(tx) <= lim else tx[:lim].rsplit(' ', 1)[0] + ' […]'
    y = r['anno']
    if tt not in tidx[y]: tidx[y][tt] = len(texts[y]); texts[y].append(tt)
    pm = r['pm']
    rows.append(dict(i=r['id'], a=r.get('art') or '', p=r['p'], g=GMAP.get(r['g'], r['g']), c=CMAP.get(r['coal'], 'Misto') if r['g'] != 'Governo / relatori' else 'Governo',
                     f=r.get('f') or [[r['p'], GMAP.get(r['g'], r['g'])]], ce=r.get('ce') or '', cf=r.get('cf') or '', u=r.get('u') or '',
                     s=s, pz=1 if ('limitatamente' in (m or '') and '(e per estraneit' not in (m or '')) else 0, m=m, e=r['e'], ey=r.get('ey') or '', e3=r['e3'],
                     l=r['l'], pr=pm, rg=sorted(set(REG[p] for p in pm if p in REG)), loc=1 if loc else 0, po=r['po'], th=r['th'] or ['Altro'],
                     t=t, ta=ta, x=tidx[y][tt], d='', id_='', cv=r.get('cv') or 'Non indicata', co='', pm=pm,
                     y=y, ra=r['ramo'], le=r['lett'], o=ESC[r['es']], lk=r.get('link') or '', big=r['big'], nt=r.get('notext', 0)))
# manovra 2027: stessi campi del sito sulla manovra 2027 (stessi numeri nelle due dashboard)
S27 = {r['i']: r for r in json.load(open('/home/claude/emend/site/emendamenti.json'))['rows']}
n27 = 0
for r in rows:
    if r['y'] == 2027 and r['ra'] == 'Camera' and r['i'] in S27:
        a = S27[r['i']]; n27 += 1
        for k in ('e', 'e3', 'ey', 'l', 'pm', 'po', 'loc', 'th', 'cv', 'rg'):
            r[k] = a[k]
        r['pr'] = a['pm']
        if a.get('e3') and a['e3'] >= 5e9: r['big'] = 1
print('2027 allineate al sito 2027:', n27)
COLS = ['i','a','p','g','c','f','ce','cf','u','s','pz','m','e','ey','e3','l','rg','loc','po','th','t','ta','x','cv','pm','y','ra','le','o','lk','big','nt']
def comp(v):
    if isinstance(v, float) and v.is_integer(): return int(v)
    return v
LK = []; lki = {}
def lkc(u):
    # link compresso: 'idPropostaEmendativa|position' (Camera) o 'S:id' (Senato); il sito ricostruisce l'URL
    m = re.search(r'idPropostaEmendativa=([^&]+)&position=(\d+)', u)
    if m: return m.group(1) + '|' + m.group(2)
    m = re.search(r'tipodoc=EMENDC&id=(\d+)', u)
    return ('S:' + m.group(1)) if m else ''
for r in rows: r['lk'] = lkc(r['lk'])
js = json.dumps({'cols': COLS, 'rows': [[comp(r[k]) for k in COLS] for r in rows]}, ensure_ascii=False, separators=(',', ':'))
open(B + 'site2/emendamenti.json', 'w').write(js)
for y, tl in texts.items():
    open(B + f'site2/testi_{y}.json', 'w').write(json.dumps(tl, ensure_ascii=False, separators=(',', ':')))
import os
print(len(rows), round(len(js) / 1e6, 1), 'MB rows;', {y: round(os.path.getsize(B + f'site2/testi_{y}.json') / 1e6, 1) for y in texts})
print(collections.Counter(r['s'] for r in rows), collections.Counter(r['ta'] for r in rows))
