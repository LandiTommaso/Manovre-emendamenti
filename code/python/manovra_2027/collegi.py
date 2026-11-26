import json,re,collections
R=json.load(open('/home/claude/emend/data/rows.json'))
com=json.load(open('/home/claude/emend/data/comuni.json'))
REG={1:'PIEMONTE',2:"VALLE D'AOSTA",3:'LOMBARDIA',4:'TRENTINO-ALTO ADIGE',5:'VENETO',6:'FRIULI-VENEZIA GIULIA',7:'LIGURIA',8:'EMILIA-ROMAGNA',9:'TOSCANA',10:'UMBRIA',11:'MARCHE',12:'LAZIO',13:'ABRUZZO',14:'MOLISE',15:'CAMPANIA',16:'PUGLIA',17:'BASILICATA',18:'CALABRIA',19:'SICILIA',20:'SARDEGNA'}
def label(code,t):
    code=int(code); n=code%100; sub=(code//100)%100; reg=code//10000
    return REG[reg]+(' %d'%sub if sub else '')+' - %s%02d'%(t,n)
def norm(s):
    s=(s or '').upper().replace('/SÜDTIROL','').replace("/VALLÉE D'AOSTE",'')
    return re.sub(r'\s+',' ',s).strip()
C2U=collections.defaultdict(set);C2P=collections.defaultdict(set)
for line in open('/home/claude/emend/data/collegi.txt'):
    t,body=line.strip().split('|',1)
    for part in body.split(';'):
        k,v=part.split(':')
        for c in v.split(','):
            (C2U if t=='U' else C2P)[int(c)].add(label(k,t))
by={}
for c in com: by.setdefault(c['nome'],[]).append(c)
for k in by: by[k].sort(key=lambda c:-(c.get('popolazione') or 0))
alias={'Roma Capitale':'Roma','Massa-Carrara':'Massa','Reggio Calabria':'Reggio di Calabria',"Reggio Emilia":"Reggio nell'Emilia",'Bolzano':'Bolzano/Bozen','Bozen':'Bolzano/Bozen','Forlì-Cesena':'Forlì','Pesaro e Urbino':'Pesaro','Barletta-Andria-Trani':'Barletta','Monza e della Brianza':'Monza','Verbano-Cusio-Ossola':'Verbania','Verbano':'Verbania','Sud Sardegna':'Carbonia'}
cnt=collections.Counter()
for r in R:
    r['nelCollegio']=''; r['collegiLuoghi']=[]
    if not r['luoghi'] or r['gruppo']=='Governo': continue
    us=set();ps=set()
    for p in r['luoghi']:
        n=alias.get(p['nome'],p['nome'])
        if n in by:
            code=int(by[n][0]['codice']); us|=C2U[code]; ps|=C2P[code]
    r['collegiLuoghi']=sorted(us)
    fu=norm(r.get('uni')); fp=norm(r.get('circFull'))
    if fu and fu in {norm(x) for x in us}: r['nelCollegio']='U'
    elif fp and fp in {norm(x) for x in ps}: r['nelCollegio']='P'
    cnt[r['nelCollegio']]+=1
json.dump(R,open('/home/claude/emend/data/rows.json','w'),ensure_ascii=False)
print(cnt)
L=[r for r in R if r['nelCollegio']=='U']
for r in L[:40]: print(r['id'],r['primo'],r['gruppo'],r['uni'],[p['nome'] for p in r['luoghi']][:3],r['stato'][:5],(r['titolo'] or '')[:60])
