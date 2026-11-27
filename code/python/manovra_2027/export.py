import json,re
BIGRE=r"collegamento stabile tra la Sicilia|[Pp]onte sullo [Ss]tretto|[Ss]ociet[àa] Stretto di Messina|[Rr]imodula"  # stessa regola in multi/src/build.py
R=json.load(open('/home/claude/emend/data/rows.json'))
out=[];texts=[];idx={}
COVP=[('FISPE (DL 282/2004)',r"10,? comma 5,? del decreto-legge 29 novembre 2004"),
 ('Fondo esigenze indifferibili (L. 190/2014)',r"comma 200,? della legge 23 dicembre 2014"),
 ('Fondo art. 137 del ddl',r"articolo 137,? comma [12]"),
 ('Fondi speciali (Tab. A/B)',r"fondo speciale|[Tt]abella [AB]\b"),
 ('Tagli a stati di previsione',r"\bCP:\s*-"),
 ('Nuove entrate',r"maggiori entrate|aliquota|accisa|prelievo|contributo di solidariet|imposta (?:sostitutiva|straordinaria)"),
 ('Riduzione di altre spese/fondi',r"riduzione (?:delle dotazioni|lineare|dello stanziamento|del [Ff]ondo|dell.autorizzazione)|è ridott[oa]|sono ridott"),
 ('Risorse già stanziate / rimodulazione',r"a valere (?:sulle|sulla|sul|nell)|nell.ambito delle risorse|nei limiti delle risorse|Conseguentemente, all.articolo \d+[^.]{0,80}(?:sostituire|ridurre|le parole)|risorse (?:già )?(?:disponibili|previste|stanziate)"),
 ('Senza oneri dichiarati',r"nuovi o maggiori oneri|invarianza finanziaria")]
def cov(t):
    for k,(n,p) in enumerate(COVP):
        if re.search(p,t if k<5 else t[-2500:]): return n
    return 'Non indicata'
FIRSTK={}
for r in R:
    _k=(r['art'],re.sub(r'\s+',' ',r['testo'] or '').strip())
    if _k not in FIRSTK: FIRSTK[_k]=r['id']
    dup='' if FIRSTK[_k]==r['id'] else FIRSTK[_k]
    loc=r['localistico']; est=r['estraneo']; t=r['testo']
    lim=4000 if (loc or est or r['portata']!='Nazionale') else 900
    tt=t if len(t)<=lim else t[:lim].rsplit(' ',1)[0]+' […]'
    if tt not in idx: idx[tt]=len(texts); texts.append(tt)
    mot=r['motivo'].replace('Inammissibile per ','').replace('Parzialmente: ','parzialmente inammissibile: ')
    cat='Ammissibile'
    if r['stato']=='Inammissibile':
        cat='Estraneità di materia' if mot.startswith('estraneità') else 'Compensazione'
    out.append(dict(i=r['id'],a=r['art'],p=r['primo'],g=r['gruppo'],c=r['coal'],
        f=[[x['n'],x['g']] for x in r['firmInfo']],ce=r['circ'],cf=r['circFull'],u=r['uni'] or '',
        s=cat,pz=1 if ('limitatamente' in mot and '(e per estraneità' not in mot) else 0,m=mot,e=r['importo'],ey=r.get('importoAnno',''),e3=r['importo3'],
        l=[x['nome'] for x in r['luoghi']],pr=r['province'],rg=r['regTerr'],
        loc=1 if loc else 0,po=r['portata'],th=r['temi'],t=r['titolo'] or r['titoloAuto'],ta=0 if r['titolo'] else 1,
        x=idx[tt],d=dup,id_=r['ident'],cv=cov(t),co=r.get('nelCollegio',''),
        rx=('R' if 'resta' in r.get('riammesso','') else ('S' if r.get('riammesso') else '')),ns=1 if r.get('nota_esito') else 0,big=1 if (re.search(BIGRE,t) or (r['importo3'] or r['importo'] or 0)>1e9) else 0,pm=(sorted(set(p['provincia'] for p in r.get('luoghiMappa',[]))) if (r.get('luoghiMappa') and r['localistico'] and not (len(r['luoghiMappa'])>=6 and len(set(p['regione'] for p in r['luoghiMappa']))>=3)) else [])))
s=json.dumps({'texts':texts,'rows':out},ensure_ascii=False,separators=(',',':'))
open('/home/claude/emend/site/emendamenti.json','w').write(s); print(len(s)/1e6)
