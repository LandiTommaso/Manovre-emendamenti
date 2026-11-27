# Revisione manuale delle proposte 2027 'Locale' senza province per la mappa (vedi data/luoghi_revisione.json).
import json
R=json.load(open('/home/claude/emend/data/rows.json'))
NAZ=json.load(open('/home/claude/emend/data/luoghi_revisione.json'))['nazionale']
a=b=0
for r in R:
    if r['id'] in NAZ and (r['localistico'] or r.get('luoghiMappa')):
        r['localistico']=False; r['portata']='Nazionale'; r['luoghiMappa']=[]; a+=1
    elif r['localistico'] and not r.get('luoghiMappa'):
        r['luoghiMappa']=r['luoghi']; b+=1
assert not [k for k in NAZ if k not in {r['id'] for r in R}]
json.dump(R,open('/home/claude/emend/data/rows.json','w'),ensure_ascii=False)
print('passate a Nazionale',a,'; luoghi in mappa',b)
