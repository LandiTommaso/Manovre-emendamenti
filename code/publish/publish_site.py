"""Copia le due dashboard nel sito personale (landitommaso.github.io/projects/...) con <head> completo:
titolo, descrizione, URL canonico e anteprima per X/LinkedIn (Open Graph). Un solo comando per aggiornare."""
import shutil, glob, os, html
SITE = '/home/claude/landitommaso.github.io/projects/'
BASE = 'https://landitommaso.github.io/projects/'
P = {
 'manovra-2027': dict(src='/home/claude/emend/site/', title='Amendments to Italy’s 2027 budget law',
   desc='All 6,558 amendments tabled in the Chamber’s Budget Committee: who signs them, which are inadmissible, how much they ask for and where the money would go. Interactive maps and search, in IT/EN/ES/FR.'),
 'manovre-2023-2027': dict(src='/home/claude/multi/site2/', title='Italian budget laws 2023–2027, amendment by amendment',
   desc='Every proposal to the five budget laws of the legislature, Chamber and Senate (24,977): outcomes, MP rankings, a map of local spending requests and a comparison with the 2022 vote. In IT/EN/ES/FR.'),
}
for slug, c in P.items():
    out = SITE + slug + '/'; os.makedirs(out, exist_ok=True)
    for f in glob.glob(out + '*.json'): os.remove(f)
    for f in glob.glob(c['src'] + '*.json'): shutil.copy(f, out)
    url = BASE + slug + '/'; t = html.escape(c['title']); d = html.escape(c['desc'])
    head = f'''<!doctype html><html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="description" content="{d}"><link rel="canonical" href="{url}"><meta name="author" content="Tommaso Landi">
<meta property="og:type" content="website"><meta property="og:site_name" content="Tommaso Landi"><meta property="og:title" content="{t}"><meta property="og:description" content="{d}">
<meta property="og:url" content="{url}"><meta property="og:image" content="{url}preview.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{t}"><meta name="twitter:description" content="{d}"><meta name="twitter:image" content="{url}preview.png">
<style>[hidden]{{display:none!important}}</style></head><body>'''
    body = open(c['src'] + 'index.html', encoding='utf-8').read()
    open(out + 'index.html', 'w', encoding='utf-8').write(head + body + '</body></html>')
    print('ok', slug)
