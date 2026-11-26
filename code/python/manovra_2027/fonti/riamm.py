import json,re
t=open('/home/claude/emend/fonti/bol.txt').read()
i=t.find('missibili per materia le seguenti proposte'); j=t.find('Comunica, altresì, che, a seguito del'); k=t.find('Conferma, infine, i giudizi di inammis')
def clean(s):
    s=re.sub(r'\(\d\) Testo modificato.*?2026\.','',s,flags=re.S)
    return re.sub(r'-\n','',s).replace('\n',' ')
A=clean(t[i:j]); B=clean(t[j:k])
MAT=re.findall(r'\b(\d{1,3}\.\d+)\b',A)
COP=re.findall(r'\b(0?\d{1,3}\.\d+(?:\.\d+)?)\b',B)
# segments of coverage list with text, to catch 'resta inammissibile' and 'limitatamente'
segs=re.split(r';\s',B)
info={}
for s in segs:
    for x in re.findall(r'\b(0?\d{1,3}\.\d+(?:\.\d+)?)\b',s):
        info[x]=dict(resta='resta inam' in s, parz=('limitatamente' in s), firm=s.strip()[:500])
json.dump(dict(materia=MAT,copertura=COP,info=info),open('/home/claude/emend/fonti/riamm_0769.json','w'),ensure_ascii=False,indent=0)
