import re,json
t=open('/home/claude/emend/fonti/b68n.txt').read()
i=t.find('C. 3174-bis Governo.\n'); seg=t[i:]
seg=re.sub(r'(?<=[a-zàèéìòù])-\n(?=[a-zàèéìòù])','',seg).replace('\n',' ')
seg=re.sub(r'Lunedì 23 novembre 2026\s+— \d+\s*','',seg); seg=re.sub(r'—\s+Commissione V','',seg)
a=seg.find('risultano inammissibili, in ragione'); m=seg.find('considerate inammissibili per carenza o'); end=seg.find('nunce di inammissibilità',m)
def norm(x):
    p=x.split('.')
    if len(p)==3 and p[1]=='0': return p[0]+'.0'+p[2]
    return x
rx=r'(?<![\d.])((?:Tab\.\s?\d+\.)?0?\d{1,3}\.\d+(?:\.\d+)?)(?![\d])'
MATtxt=seg[a:m]; COVtxt=seg[m:end]
MAT=[norm(x) for x in re.findall(rx,MATtxt)]
COV=[norm(x) for x in re.findall(rx,COVtxt)]
# partial markers in matter list
PARZ={}
for s in re.split(r';\s',MATtxt):
    ids=[norm(x) for x in re.findall(rx,s)]
    if 'limitatamente' in s:
        for x in ids: PARZ[x]=s[:200]
json.dump(dict(MAT=MAT,COV=COV,PARZ=PARZ,MATtxt=MATtxt,COVtxt=COVtxt),open('/home/claude/emend/fonti/b68_lists.json','w'),ensure_ascii=False)
