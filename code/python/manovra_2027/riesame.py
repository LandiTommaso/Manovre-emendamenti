# Applica le pronunce ufficiali di inammissibilità riportate nei Bollettini della V Commissione:
#  - n. 768 del 23/11/2026 (pronuncia iniziale: elenco per materia + elenco per copertura)
#  - n. 769 del 24/11/2026 (riesame: riammissioni per materia e per copertura; testo integrato con l'errata corrige del n. 770)
# Il Bollettino è il resoconto ufficiale della pronuncia; la colonna "esito" del sito della Camera
# ne è una trascrizione e in alcuni casi diverge (vedi CORREZIONI_SITO). Gli elenchi sono estratti
# dai PDF in /home/claude/emend/fonti con b68parse.py e riamm.py.
import json, re, collections
R = json.load(open('/home/claude/emend/data/rows.json'))
B68 = json.load(open('/home/claude/emend/fonti/b68_lists.json'))
B69 = json.load(open('/home/claude/emend/fonti/riamm_0769.json'))
by = {r['id']: r for r in R}

def norm(x):
    p = x.split('.')
    return p[0] + '.0' + p[2] if len(p) == 3 and p[1] == '0' else x

JUNK = {'3.000', '5.000', '3.3'}          # numeri nel testo descrittivo / Tab.3.3 letto a metà
MAT = {x for x in B68['MAT'] if x not in JUNK}
COV = {x for x in B68['COV'] if x not in JUNK} | {'Tab.3.3', 'Tab.A.46'}
# inammissibilità parziali: trascrizione del sito (36 casi), verificata contro il Bollettino n. 768
# (tutti nell'elenco per materia con «limitatamente»; «e per carenza di compensazione» = presenti anche nell'elenco per copertura)
PARZ = {l.split('|')[0]: l.split('|')[1].strip() for l in open('/home/claude/emend/fonti/parz_sito.txt') if '|' in l}
assert all(x in MAT for x in PARZ) and all(('carenza' in v) == (x in COV) for x, v in PARZ.items())
def lim(s):
    return 'limitatamente ' + s.split('limitatamente ', 1)[1].replace(' e per carenza di compensazione', '')

log = collections.Counter(); notes = []
def setr(i, stato, motivo, why):
    r = by[i]
    if (r['stato'], r['motivo']) != (stato, motivo):
        notes.append((i, r['stato'], r['motivo'], '->', stato, motivo, why)); log[why] += 1
    r['stato'] = stato; r['motivo'] = motivo

# 1) pronuncia del 23/11 secondo il Bollettino
for i, r in by.items():
    inM, inC = i in MAT, i in COV
    if not (inM or inC):
        continue
    if inM and i in PARZ:
        if inC:   # inammissibile per copertura (tutto) e per materia in parte
            setr(i, 'Inammissibile', 'Inammissibile per carenza o inidoneità della compensazione (e per estraneità di materia ' + lim(PARZ[i]) + ')', 'parziale+copertura')
        else:     # solo una parte è inammissibile: l'emendamento resta votabile
            setr(i, 'Ammissibile', 'Parzialmente: Inammissibile per estraneità di materia ' + lim(PARZ[i]), 'solo parziale')
    elif inM:
        if r['stato'] != 'Inammissibile' or 'estraneit' not in r['motivo']:
            setr(i, 'Inammissibile', 'Inammissibile per estraneità di materia', 'materia (bollettino)')
    else:
        if r['stato'] != 'Inammissibile' or 'compensazion' not in r['motivo']:
            if r['stato'] == 'Inammissibile' and 'estraneit' in r['motivo']:
                continue
            setr(i, 'Inammissibile', 'Inammissibile per carenza o inidoneità della compensazione', 'copertura (bollettino)')
# inammissibili sul sito ma assenti da entrambi gli elenchi del Bollettino
SOLO_SITO = sorted(i for i, r in by.items() if r['stato'] == 'Inammissibile' and i not in MAT and i not in COV)
# 108.27: refuso del sito per 108.027 (il Bollettino: «Manzi 108.29 e Torto 108.027», identici)
if '108.27' in SOLO_SITO:
    setr('108.27', 'Ammissibile', '', 'refuso sito 108.27/108.027'); SOLO_SITO.remove('108.27')
for i in SOLO_SITO:
    by[i]['nota_esito'] = 'inammissibile sul sito della Camera, assente dagli elenchi del Bollettino n. 768'
n23 = sum(r['stato'] == 'Inammissibile' for r in R)

# 2) riesame del 24/11
RM = set(B69['materia'])
RC = {norm(x) for x in B69['copertura']}
info = {norm(k): v for k, v in B69['info'].items()}
for i in sorted(RM | RC):
    r = by[i]; inf = info.get(i, {})
    stillM = (i in MAT) and (i not in RM)
    stillC = (i in COV) and (i not in RC)
    r['riammesso'] = '24/11/2026: ' + ' e '.join(x for x, y in (('materia', i in RM), ('copertura', i in RC)) if y)
    if inf.get('resta') and i in PARZ:          # 77.077: resta fuori solo la parte estranea
        setr(i, 'Ammissibile', 'Parzialmente: Inammissibile per estraneità di materia ' + lim(PARZ[i]), 'riesame: resta parziale')
    elif stillM or inf.get('resta'):
        setr(i, 'Inammissibile', 'Inammissibile per estraneità di materia', 'riesame: resta per materia')
        r['riammesso'] = '24/11/2026: riesame sulla copertura accolto, resta inammissibile per estraneità di materia'
    elif stillC:
        setr(i, 'Inammissibile', 'Inammissibile per carenza o inidoneità della compensazione', 'riesame: resta per copertura')
    elif inf.get('parz'):
        m = re.search(r'limitatamente (.*?)(?:,\s+(?:nel presupposto|che|in considerazione|alla luce)|$)', inf.get('firm', ''))
        setr(i, 'Ammissibile', 'Parzialmente: Inammissibile per carenza o inidoneità della compensazione, salvo la parte riammessa il 24/11 (limitatamente ' + (m.group(1) if m else 'ad alcune parti') + ')', 'riesame: riammesso in parte')
    else:
        setr(i, 'Ammissibile', '', 'riesame: riammesso')
for r in R:
    r['estraneo'] = r['stato'] == 'Inammissibile' and r['motivo'].startswith('Inammissibile per estraneità')
n24 = sum(r['stato'] == 'Inammissibile' for r in R)
json.dump(R, open('/home/claude/emend/data/rows.json', 'w'), ensure_ascii=False)
json.dump(dict(log=log, notes=notes, solo_sito=SOLO_SITO, n23=n23, n24=n24),
          open('/home/claude/emend/fonti/riesame_log.json', 'w'), ensure_ascii=False, indent=0)
print('inammissibili 23/11 (Bollettino):', n23, ' dopo riesame 24/11:', n24)
print(dict(log)); print('solo sito:', SOLO_SITO)
