import json,collections,copy
R=json.load(open('/home/claude/emend/data/rows.json'))
off={}
for tok in open('/home/claude/emend/data/inamm_ufficiali.txt').read().strip().split(','):
    i,c=tok.rsplit(':',1); off[i]=c
LBL={'C':'Inammissibile per carenza di compensazione','E':'Inammissibile per estraneità di materia','I':'Inammissibile per inidoneità della compensazione','CI':'Inammissibile per carenza di compensazione e per inidoneità della compensazione'}
def code(m):
    if not m: return 'A'
    return 'E' if 'estraneit' in m else ('CI' if 'carenza' in m and 'inidon' in m else ('I' if 'inidon' in m else 'C'))
ids={r['id'] for r in R}
# add 85.11 (identico a 85.10) and 85.0100 (Governo)
b=[r for r in R if r['id']=='85.10'][0]
r11=copy.deepcopy(b); r11['id']='85.11'; r11['firm']=["Dell'Olio","Carmina","Donno","Torto"]
r11['firmInfo']=[dict(n=n,g='M5S',c=x['c'],u=x.get('u','')) for n,x in zip(r11['firm'],b['firmInfo'][:1]*4)]
r11['primo']="Dell'Olio"; r11['circ']='Puglia'; r11['circFull']='PUGLIA - P02'; r11['uni']=''
gov=dict(id='85.0100',ident='',art='Art. agg. dopo art. 85',firm=['Governo'],firmInfo=[dict(n='Governo',g='Governo',c='')],primo='Governo',gruppo='Governo',coal='Governo',gruppi=['Governo'],circ='',circFull='',uni='',stato='Ammissibile',motivo='',importo=None,importo3=None,luoghi=[],regioni=[],temi=['Imprese/agricoltura','Mezzogiorno/aree interne'],titolo='Disposizioni in materia di zone economiche speciali per la promozione e lo sviluppo delle attività economiche e imprenditoriali',titoloAuto=None,testo="Emendamento del Governo, non presente nel fascicolo HTML: testo completo sul sito della Camera (proposta emendativa 85.0100). Estende le semplificazioni della ZES unica (artt. 14-15 DL 124/2023) ai territori fuori dalla ZES per i settori indicati in un documento di programmazione strategica triennale.",nIdent=1,estraneo=False,province=[],regTerr=[],localistico=False,portata='Nazionale')
R.append(r11); R.append(gov)
mism=collections.Counter(); ex=[]
for r in R:
    mine=code(r['motivo']) if r['stato']=='Inammissibile' else 'A'
    o=off.get(r['id'],'A')
    if mine!=o:
        mism[(mine,o)]+=1; ex.append((r['id'],mine,o))
        if o=='A':
            r['stato']='Ammissibile'
            r['motivo']=('Parzialmente: '+r['motivo']) if 'limitatamente' in r['motivo'] else ''
        else: r['stato']='Inammissibile'; r['motivo']=LBL[o]
    r['estraneo']='estraneità' in r['motivo']
print('mismatch',sum(mism.values()),mism.most_common(),ex[:15])
print('missing official ids in mine',[i for i in off if i not in {r['id'] for r in R}])
json.dump(R,open('/home/claude/emend/data/rows.json','w'),ensure_ascii=False)
print(len(R), collections.Counter(code(r['motivo']) for r in R))
