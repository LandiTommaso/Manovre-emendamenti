"""Esporta i dati del replication package in CSV semplici (separatore virgola, UTF-8)."""
import json, csv, collections, gzip
B = '/home/claude/multi/'; E = '/home/claude/emend/'; O = '/home/claude/repo_manovre/data/'
R = json.load(open(B + 'out/multi_rows.json'))
topo = json.load(open(E + 'site/province.topo.json'))
REG = {g['properties']['prov_name']: g['properties']['reg_name'] for g in topo['objects']['provinces']['geometries']}
ATTO = {(2023,'Camera'):'C.643-bis',(2023,'Senato'):'S.442',(2024,'Senato'):'S.926',(2024,'Camera'):'C.1627',(2025,'Camera'):'C.2112-bis',(2025,'Senato'):'S.1330',(2026,'Senato'):'S.1689',(2026,'Camera'):'C.2750',(2027,'Camera'):'C.3174-bis'}
cols = ['manovra','ramo','atto','lettura','emendamento','articolo','primo_firmatario','id_firmatario','gruppo','schieramento','n_firmatari','firmatari',
        'esito','motivo_inammissibilita','portata','province','regioni','luoghi','tema','euro_annuo','euro_triennio','grande_opera','copertura','oggetto','link_ufficiale']
GN = {'Governo / relatori': 'Governo / relatori'}
with open(O + 'emendamenti_2023_2027.csv', 'w', newline='', encoding='utf-8') as f, gzip.open(O + 'testi_emendamenti_2023_2027.csv.gz', 'wt', newline='', encoding='utf-8') as ft:
    w = csv.writer(f); w.writerow(cols); wt = csv.writer(ft); wt.writerow(['manovra','ramo','emendamento','testo'])
    def _nk(i):
        out = []
        for x in str(i).replace('Tab.', '9999.').split('.'):
            out.append((0, int(x), len(x)) if x.isdigit() else (1, 0, x))
        return out
    # ordine cronologico: manovra, poi prima lettura e seconda lettura, poi numero dell'emendamento
    for r in sorted(R, key=lambda r: (r['anno'], r['lett'], _nk(r['id']))):
        pm = sorted(set(r['pm']))
        w.writerow([r['anno'], r['ramo'], ATTO[(r['anno'], r['ramo'])], r['lett'], r['id'], r.get('art') or '', r['p'], r.get('pid') or '', r['g'], r['coal'], r['nf'],
                    '; '.join(f"{a} ({b})" for a, b in (r.get('f') or [])), r['es'], r.get('mot') or '', r['po'], '; '.join(pm), '; '.join(sorted(set(REG[p] for p in pm if p in REG))),
                    '; '.join(r['l']), '; '.join(r['th'] or []), r['e'] or '', r['e3'] or '', int(bool(r['big'])), r.get('cv') or '', (r.get('tt') or '').replace('\n', ' '), r.get('link') or ''])
        wt.writerow([r['anno'], r['ramo'], r['id'], r.get('tx') or ''])
V = json.load(open(E + 'data/voti2022.json')); POP = json.load(open(E + 'site/popolazione.json'))
with open(O + 'voti_camera_2022_province.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['provincia', 'regione', 'popolazione_2025'] + ['voti_' + k for k in V['K']])
    for p, v in sorted(V['prov'].items()):
        if p in POP: w.writerow([p, REG[p], POP[p]] + v)
PC = json.load(open(E + 'data/prov_collegi2022.json'))['prov']
with open(O + 'elettori_provincia_collegio_2022.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['provincia', 'collegio_plurinominale', 'elettori'])
    for p, d in sorted(PC.items()):
        for c, n in d.items(): w.writerow([p, c, n])
with open(O + 'deputati_collegi.csv', 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['cognome', 'nome', 'gruppo', 'collegio_plurinominale', 'collegio_uninominale'])
    for line in open(E + 'data/deputati.txt', encoding='utf-8'):
        x = line.rstrip('\n').split('|')
        if len(x) >= 5: w.writerow(x[:5])
print('ok', len(R))
