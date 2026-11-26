import json,re,html,collections
B=json.load(open('/home/claude/multi/raw/camera_liste_e_fascicoli_2.json'))
META={'C643bis':(2023,1,'Commissione'),'C643bisA':(2023,1,'Commissione (rinvio)'),'C643bisAula':(2023,1,'Aula'),
'C1627':(2024,2,'Commissione'),'C1627Aula':(2024,2,'Aula'),'C2112bis':(2025,1,'Commissione'),'C2750':(2026,2,'Commissione'),'C2750Aula':(2026,2,'Aula'),'C3174bis':(2027,1,'Commissione')}
rows=[]
def parse(key,t):
    art=None
    for m in re.finditer(r'<tr class="(rigaArticolo\w*|normale)"[^>]*>(.*?)</tr>',t,re.S):
        cls,body=m.groups()
        if cls.startswith('rigaArticolo'):
            a=re.search(r'>([^<]+)</a>\s*</acronym>',body); art=html.unescape(a.group(1)).strip() if a else None; continue
        idm=re.search(r'idPropostaEmendativa=([^&"]+)&amp;position=(\d+)"[^>]*>([^<]+)</a>',body)
        if not idm: continue
        tds=re.findall(r'<td[^>]*?(?:/>|>(.*?)</td>)',body,re.S)
        firm=tds[2] if len(tds)>2 else ''
        fm=re.search(r'idPersona=(\d+)[^>]*>([^<]+)</a>',firm)
        txt=re.sub(r'<[^>]+>','',firm); txt=html.unescape(re.sub(r'\s+',' ',txt)).strip()
        es=re.search(r'class="esito\w+">([^<]*)<',body)
        rows.append(dict(src=key,id=idm.group(3).strip(),pos=idm.group(2),art=art,idp=fm.group(1) if fm else None,
            primo=html.unescape(fm.group(2)).strip() if fm else txt,altri=' e altri' in txt,esito=es.group(1) if es else ''))
for k,t in B.items():
    if k.startswith('lista_') and len(t)>5000: parse(k[6:],t)
    if k.startswith('seduta_C2112bis'): parse('C2112bis',t)
# dedup (id,pos) within src
seen=set();R=[]
for r in rows:
    key=(r['src'],r['id'],r['pos'])
    if key in seen: continue
    seen.add(key);r['anno'],r['lettura'],r['sede']=META[r['src']];R.append(r)
json.dump(R,open('/home/claude/multi/out/camera_liste.json','w'),ensure_ascii=False)
c=collections.Counter((r['src'],r['esito']) for r in R)
for s in META: print(s, sum(v for (a,b),v in c.items() if a==s), {b:v for (a,b),v in c.items() if a==s})
print(collections.Counter(r['primo'] for r in R if not r['idp']).most_common(8))
