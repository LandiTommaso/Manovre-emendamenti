import json,re,html,collections
S=json.load(open('/home/claude/multi/raw/senato_fascicoli_commissione.json'))
META={'S442':(2023,2,'2022-12-27'),'S926':(2024,1,'2023-11-15'),'S1330':(2025,2,'2024-12-23'),'S1689':(2026,1,'2025-11-15')}
BLK=re.compile(r'<p style="text-align:justify" ?><b>([^<]+)</b></p>')
def strip(h):
    h=re.sub(r'<br\s*/?>|</p>|</li>','\n',h); h=re.sub(r'<[^>]+>','',h)
    h=html.unescape(h).replace('\xa0',' '); h=re.sub(r'[ \t]+',' ',h); h=re.sub(r'\n\s*','\n',h); return h.strip()
out=[]
for k,t in S.items():
    a=t.find('main-content'); t=t[a:]
    ms=list(BLK.finditer(t))
    for i,m in enumerate(ms):
        idr=re.sub(r'\s*\[id\..*$','',html.unescape(m.group(1))).strip()
        if idr.startswith('G') or idr.startswith('x'): continue
        seg=t[m.end(): ms[i+1].start() if i+1<len(ms) else len(t)]
        fm=re.match(r'\s*<p class="firm"[^>]*>(.*?)</p>',seg,re.S)
        firm=[];rest=seg
        if fm:
            firm=[(html.unescape(n).strip(),pid) for pid,n in re.findall(r'SANASEN&amp;id=(\d+)">([^<]+)</A>',fm.group(1),re.I)]
            if not firm: firm=[(x.strip(),None) for x in strip(fm.group(1)).split(',') if x.strip()]
            rest=seg[fm.end():]
        em=re.match(r'\s*<p>(?:<b>)+([^<]+)(?:</b>)+</p>',rest)
        esito=html.unescape(em.group(1)).strip() if em else ''
        if em: rest=rest[em.end():]
        txt=strip(rest)
        tm=re.match(r'(.+?)\s*\((testo[^)]*)\)$',idr)
        base=tm.group(1) if tm else idr
        out.append(dict(src=k,anno=META[k][0],lettura=META[k][1],data=META[k][2],idr=idr,id=base,ver=tm.group(2) if tm else '',firm=firm,esito=esito,testo=txt))
json.dump(out,open('/home/claude/multi/out/senato_raw.json','w'),ensure_ascii=False)
for k in META:
    R=[r for r in out if r['src']==k]; ids=set(r['id'] for r in R)
    print(k,len(R),len(ids),collections.Counter(r['esito'] for r in R).most_common(6), sum(1 for r in R if not r['firm']))
#print([ (r['idr'],r['firm'][:2],r['esito'],r['testo'][:120]) for r in out if r['src']=='S1689'][:3])
