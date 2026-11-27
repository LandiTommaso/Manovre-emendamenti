"""Allinea le righe della manovra 2027 (Camera) alla classificazione del sito sulla manovra 2027,
così sito 2027, sito della legislatura e paper usano gli stessi luoghi, importi e temi."""
import json
B = '/home/claude/multi/'
R = json.load(open(B + 'out/multi_rows_prealign.json'))
S27 = {r['i']: r for r in json.load(open('/home/claude/emend/site/emendamenti.json'))['rows']}
n = 0
for r in R:
    if r['anno'] == 2027 and r['ramo'] == 'Camera' and r['id'] in S27:
        a = S27[r['id']]; n += 1
        r['pm'] = a['pm']; r['big'] = a.get('big', 0); r['po'] = a['po']; r['l'] = a['l']; r['e'] = a['e']; r['e3'] = a['e3']; r['ey'] = a.get('ey') or ''
        r['th'] = a['th']; r['cv'] = a['cv']
json.dump(R, open(B + 'out/multi_rows.json', 'w'), ensure_ascii=False)
print('allineate', n)
