import json
R=json.load(open('/home/claude/multi/out/multi_rows.json'))
G=['FdI','Lega','FI','Noi Moderati','PD','M5S','AVS','Azione / IV','Autonomie','Misto','Governo / relatori']
names=[];ni={}
def nid(x):
    if x not in ni: ni[x]=len(names); names.append(x)
    return ni[x]
ES={'Approvato':'A','Inammissibile':'I','Ritirato':'R','Non approvato':'N'}
PO={'Locale':'L','Più territori':'P','Nazionale':'N'}
rows=[]
for r in R:
    e=r['e3'] or 0
    rows.append([r['anno'],0 if r['ramo']=='Camera' else 1,r['lett'],r['id'],nid(r['p']),G.index(r['g']),ES[r['es']],PO[r['po']],r['pm'],round(e) if e and not r['big'] else 0,r['big'],(r['th'] or ['Altro'])[0],r['l'][:4]])
json.dump(dict(groups=G,names=names,rows=rows),open('/home/claude/multi/site/dati.json','w'),ensure_ascii=False,separators=(',',':'))
import os;print(os.path.getsize('/home/claude/multi/site/dati.json')/1e6,len(rows))
