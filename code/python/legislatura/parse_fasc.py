import re, html, json, unicodedata, collections, sys

D = '/home/claude/emend/data/'
import sys
FASC, OUTP, Y0 = sys.argv[1], sys.argv[2], int(sys.argv[3])
raw = open(FASC, encoding='utf-8').read().replace('<br />','<br>').replace('\r\n','\n')
body = raw[raw.find('<p align="center">ART.'):]

def norm(s):
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r"[^A-Z]", '', s.upper())

def strip(h):
    h = re.sub(r'<br\s*/?>', '\n', h)
    h = re.sub(r'</p>', '\n', h)
    h = re.sub(r'<[^>]+>', '', h)
    h = html.unescape(h).replace(' ', ' ').replace(' ', ' ')
    h = re.sub(r'[ \t]+', ' ', h)
    h = re.sub(r'\n\s*', '\n', h)
    return h.strip()

# ---------- deputies ----------
deps = []
for l in open(D + 'deputati.txt', encoding='utf-8'):
    c = l.rstrip('\n').split('|')
    if len(c) < 6: continue
    deps.append(dict(cog=c[0], nome=c[1], gruppo=c[2], circ=c[3], uni=c[4], attivo=c[5] == '1'))
by_sur = collections.defaultdict(list)
for d in deps:
    by_sur[norm(d['cog'])].append(d)

GRP_LABEL = {'FDI': 'FdI', 'LEGA': 'Lega', 'FI-PPE': 'FI', 'NM(N-C-U-I)M-CP': 'Noi Moderati',
             'PD-IDP': 'PD', 'M5S': 'M5S', 'AVS': 'AVS', 'AZ-PER-RE': 'Azione', 'IV-CR': 'IV', 'MISTO': 'Misto'}
MAGG = {'FdI', 'Lega', 'FI', 'Noi Moderati'}

def lookup(sig):
    words = sig.split()
    cands = []
    for k in range(len(words)):
        sur = norm(' '.join(words[k:]))
        first = ' '.join(words[:k]).upper()
        if sur not in by_sur and k==0 and norm(words[0]) in by_sur and len(words)>1:
            sur=norm(words[0]); first=''
        if sur in by_sur:
            c = by_sur[sur]
            if first:
                c2 = [d for d in c if norm(d['nome']).startswith(norm(first))]
                c = c2 or c
            cands = c
            break
    if len(cands) > 1:
        act = [d for d in cands if d['attivo']]
        cands = act or cands
    return cands

def circ_region(c):
    c = c or ''
    r = re.sub(r'\s*\d?\s*-\s*[PU]\d+$', '', c).strip()
    r = re.sub(r'\s+\d$', '', r)
    return r.title().replace("D'Aosta", "d'Aosta").replace('/Südtirol', '').replace('/SüDtirol', '')

# ---------- comuni ----------
com = json.load(open(D + 'comuni.json', encoding='utf-8'))
prov_reg = {}
cname = collections.defaultdict(list)
for c in com:
    prov_reg[c['provincia']['nome']] = c['regione']['nome']
    cname[c['nome']].append(c)
for k in cname:
    cname[k].sort(key=lambda c: -(c.get('popolazione') or 0))
provs = set(prov_reg)
regions = sorted(set(prov_reg.values()), key=len, reverse=True)
# capoluoghi with risky words removed unless in explicit context
RISKY = {'Fermo', 'Massa', 'Prato', 'Bene', 'Latina', 'Monza', 'Sud Sardegna', 'Asti', 'Como', 'Lodi',
         'Terni', 'Imperia', 'Matera', 'Lecco', 'Rimini'}
RISKY = {'Fermo', 'Massa', 'Prato', 'Latina', 'Como', 'Lodi', 'Imperia', 'Sud Sardegna'}
PROVNAMES = {}
for p in provs:
    for alias in re.split(r'[-/]', p) + [p]:
        alias = alias.strip()
        if alias and alias not in RISKY:
            PROVNAMES[alias] = p
for k in ['Bolzano', 'Bozen', 'Trento', 'Reggio Calabria', "Reggio Emilia", "Reggio nell'Emilia", 'Pesaro', 'Urbino',
          'Barletta', 'Andria', 'Trani', 'Carbonia', 'Iglesias', 'Forlì', 'Cesena', 'Massa Carrara', 'Carrara',
          'Monza', 'Verbania', 'Aosta']:
    for c in cname.get(k, [])[:1]:
        PROVNAMES[k] = c['provincia']['nome']
PROVNAMES['Reggio Calabria'] = 'Reggio Calabria'
PROVNAMES['Roma Capitale'] = 'Roma'
for _k in [k for k in PROVNAMES if 'Aost' in k or 'Vallée' in k]: PROVNAMES.pop(_k)
# names that are also common words or recurring non-territorial uses
EXCL_ANY = {'Italia', 'Stato', 'Europa', 'Valle', 'San', 'Santa', 'Monte', 'Porto', 'Villa', 'Lago', 'Pace',
            'Bene', 'Ponte', 'Paese', 'Campo', 'Castello', 'Croce', 'Fondo', 'Gioia', 'Lei', 'Montagna', 'Piano',
            'Sale', 'Scala', 'Torre', 'Vita', 'Verità', 'Calendario', 'Cassano', 'Codice', 'Comune', 'Isola',
            'Mezzana', 'Moneta', 'Fondi', 'Paese', 'Patti', 'Campagna', 'Medicina', 'Parti', 'Premio', 'Ricadi', 'Riva', 'Sì', 'Settimo', 'Vaglio', 'Credito',
            'Stazione', 'Basso', 'Alto', 'Fiume', 'Marina', 'Musei', 'Badia', 'Serra', 'Corte', 'Casa', 'Tributi'}
REG_ALIASES = {r: r for r in regions}
REG_ALIASES.update({'Trentino-Alto Adige': 'Trentino-Alto Adige/Südtirol', 'Valle d\'Aosta': "Valle d'Aosta/Vallée d'Aoste",
                    'Friuli Venezia Giulia': 'Friuli-Venezia Giulia', 'Emilia Romagna': 'Emilia-Romagna'})
for r in list(REG_ALIASES):
    if '/' in r:
        REG_ALIASES[r.split('/')[0]] = r

BIGSKIP = EXCL_ANY | {'Fondi', 'Paese', 'Patti', 'Campagna', 'Medicina', 'Augusta', 'Fermo', 'Massa', 'Vita', 'Sorso', 'Assemini', 'Gioia', 'Corato'}
BIGN = set(c['nome'] for c in com if (c.get('popolazione') or 0) >= 10000) | set(PROVNAMES)
BIGN = sorted((n for n in BIGN if n not in BIGSKIP), key=len, reverse=True)
BIGRX = re.compile(r"(?<![\w'’])(" + '|'.join(re.escape(n) for n in BIGN) + r")(?![\w])")
CTX = re.compile(r"\b(?:[Cc]omun[ei]|[Ii]sol[ae]|[Cc]ittà|[Pp]rovincia|[Cc]ittà metropolitana|[Ff]razione|[Ll]ocalità|[Aa]bitato|[Mm]unicipio|territorio|[Aa]eroporto|[Pp]orto|[Ss]tazione|[Oo]spedale|[Pp]olo|[Ss]tadio|[Cc]omunale)\s+(?:di|del|della|dei|delle|d'|in)\s*((?:[A-ZÀ-Ý][\w'’àèéìòù-]*(?:\s+(?:di|del|della|dei|de|d'|sul|sull'|al|in|e|la|le|lo|il|San|Santa|Santo)?\s*[A-ZÀ-Ý][\w'’àèéìòù-]*)*)(?:\s*(?:,|e)\s*[A-ZÀ-Ý][\w'’àèéìòù-]*(?:\s+[A-ZÀ-Ý][\w'’àèéìòù-]*)*)*)")

def find_places(text):
    found = {}
    def add(name, prov, reg, kind):
        key = (name, prov)
        if key not in found:
            found[key] = dict(nome=name, provincia=prov, regione=reg, tipo=kind)
    # explicit context
    for m in CTX.finditer(text):
        for part in re.split(r'\s*(?:,|\be\b)\s*', m.group(1)):
            part = part.strip().rstrip("'’")
            cand = part
            while cand:
                if cand in cname and cand not in EXCL_ANY:
                    c = cname[cand][0]
                    add(cand, c['provincia']['nome'], c['regione']['nome'], 'comune')
                    break
                if cand in PROVNAMES:
                    p = PROVNAMES[cand]; add(cand, p, prov_reg.get(p, ''), 'comune'); break
                ws = cand.split()
                if len(ws) <= 1: break
                cand = ' '.join(ws[:-1])
    # standalone: capoluoghi + comuni >= 10k abitanti
    t2 = re.sub(r"[Pp]rovince autonome di Trento e (?:di )?Bolzano|[Pp]rovince autonome di Bolzano e (?:di )?Trento|Trento e (?:di )?Bolzano|Bolzano e (?:di )?Trento|[Pp]rovincia autonoma di (?:Trento|Bolzano)", " ", text)
    for m in BIGRX.finditer(t2):
        nm = m.group(1)
        if nm in PROVNAMES:
            p = PROVNAMES[nm]; add(nm, p, prov_reg.get(p, ''), 'comune')
        elif nm in cname:
            c = cname[nm][0]; add(nm, c['provincia']['nome'], c['regione']['nome'], 'comune')
    regs = set()
    for alias, r in REG_ALIASES.items():
        if re.search(r"(?<![\w])" + re.escape(alias) + r"(?![\w])", text):
            regs.add(r.split('/')[0])
    return list(found.values()), sorted(regs)

# ---------- amounts ----------
NUM = r"(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)"
AMT = re.compile(NUM + r"\s*(miliardi|miliardo|milioni|milione|mila)?\s*(?:di\s+)?euro", re.I)
MULT = {'miliardi': 1e9, 'miliardo': 1e9, 'milioni': 1e6, 'milione': 1e6, 'mila': 1e3}

def tonum(s):
    s = s.replace('.', '').replace(',', '.')
    try: return float(s)
    except: return None

KEYCTX = re.compile(r"(oner|spesa|dotazione|incrementat|rifinanziat|ridott|riduzione|limite|stanziament|contributo|pari a|valutat|autorizzat|assegnat|destinat|fondo)", re.I)
BADCTX = re.compile(r"(attivo|fatturato|ricavi|volume d.affari|patrimonio netto|soglia|reddito|ISEE|per progetto|per beneficiario|per ciascun[oa]? (?:beneficiari|soggett|impres|comun|lavorat|dipendent|famigli|student|nucle)|pari o inferiore|pari o superiore|non superiore a|non inferiore a|superiore a|inferiore a|importo massimo|fino a|lire)", re.I)
SPEND = re.compile(r"(oneri|autorizzata la spesa|dotazione|incrementat|rifinanziat|è destinat|stanziat|contributo)", re.I)
YRS = (Y0, Y0+1, Y0+2)

def _val(m):
    v = tonum(m.group(1))
    if v is None: return None
    if v < 100000: v *= MULT.get((m.group(2) or '').lower(), 1)
    return v

def year_profile(text):
    """amount per year 2027-29 from spending clauses"""
    prof = {}
    for sent in re.split(r'(?<=[.;])\s+', text):
        if not SPEND.search(sent): continue
        for m in AMT.finditer(sent):
            v = _val(m)
            if not v or v < 1000 or v > 5e10: continue
            if BADCTX.search(sent[max(0, m.start() - 70):m.start()]): continue
            tail = sent[m.end():m.end() + 140]
            yrs = []
            mm = re.match(r"\s*(?:annui\s+)?per\s+ciascuno\s+degli\s+anni\s+(?:dal\s+)?((?:\d{4}(?:,\s*|\s+e\s+|\s+al\s+)?)+)", tail)
            if mm:
                ys = [int(y) for y in re.findall(r'\d{4}', mm.group(1))]
                if ' al ' in mm.group(1) and len(ys) == 2: ys = list(range(ys[0], ys[1] + 1))
                yrs = ys
            else:
                mm = re.match(r"\s*(?:annui\s+)?(?:per\s+l.anno|nell.anno|per\s+il)\s+(\d{4})", tail)
                if mm: yrs = [int(mm.group(1))]
                else:
                    mm = re.match(r"\s*(?:annui\s+)?(?:,\s*)?a\s+decorrere\s+dal(?:l.anno)?\s+(\d{4})", tail)
                    if mm: yrs = list(range(int(mm.group(1)), YRS[-1]+1))
                    elif re.match(r"\s*annui", tail): yrs = list(YRS)
            for y in yrs:
                if y in YRS: prof[y] = max(prof.get(y, 0), v)
    return prof

def replacement_deltas(text):
    out = []
    for m in re.finditer(r"sostitui(?:re|te|ta|to) (?:le parole|la parola)?:?\s*«?([^»]{0,160}?)»?\s+con le seguenti:?\s*«?([^»]{0,160}?)(?:»|\.\s|;)", text):
        a = [_val(x) for x in AMT.finditer(m.group(1))]
        b = [_val(x) for x in AMT.finditer(m.group(2))]
        a = [x for x in a if x]; b = [x for x in b if x]
        if a and b and len(a) == len(b):
            out.append((m.start(), m.end(), max(abs(y - x) for x, y in zip(a, b))))
    return out

def amounts(text, is_tab):
    """returns (max annual, total 2027-29)"""
    text = re.sub(r"\beuro\s+(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)", r"\1 euro", text)
    if is_tab or re.search(r"\bCP:\s*[+-]?\s*\d", text):
        yv = {}
        for blk in re.finditer(r"(20\d\d):\s*CP:\s*([+-]?)\s*([\d.]+)", text):
            y, sign, v = int(blk.group(1)), blk.group(2), tonum(blk.group(3))
            if v and sign != '-':
                yv[y] = yv.get(y, 0) + v
        if yv and is_tab:
            tot = sum(v for y, v in yv.items() if y in YRS)
            return max(yv.values()), tot or None, {y:v for y,v in yv.items() if y in YRS}
    deltas = replacement_deltas(text)
    t2 = text
    for a, b, _ in reversed(deltas):
        t2 = t2[:a] + ' ' + t2[b:]
    pref, allv = [d for _, _, d in deltas], []
    for m in AMT.finditer(t2):
        v = _val(m)
        if v is None or v < 1000 or v > 5e10: continue
        pre = t2[max(0, m.start() - 70):m.start()]
        if BADCTX.search(pre): continue
        allv.append(v)
        if KEYCTX.search(pre[-90:]): pref.append(v)
    vals = pref or allv
    mx = max(vals) if vals else None
    prof = year_profile(t2)
    if prof and not deltas: mx = max(prof.values())
    tot = sum(prof.values()) if prof else None
    if mx and tot and tot < mx: tot = None
    return mx, tot, (prof if (prof and not deltas) else {})

# ---------- themes ----------
THEMES = [
    ('Sanità', r'\bsanitar|\bospedal|\bmedic[oi]\b|\bmedici\b|infermier|\bSSN\b|\bfarmac|\bsalute\b|\bASL\b|pazient|malatti|vaccin|psicolog|oncolog|\bsangue\b|plasma|disabilità|epiless'),
    ('Fisco', r'\bIRPEF\b|\bIVA\b|\bIva\b|\bimpost[ae]\b|aliquot|detrazion|deduzion|\btribut|fiscal|credito d.imposta|\baccis|\bIRES\b|\bIRAP\b|cedolare|\bIMU\b'),
    ('Previdenza/pensioni', r'pension|previdenz|\bINPS\b|APE sociale|Opzione donna|\bQuota \d'),
    ('Lavoro', r'lavorat|occupazion|salari|retribuz|assunzion|ammortizzator|cassa integrazione|NASpI|sicurezza sul lavoro|\bcontratt[oi] collettiv'),
    ('Scuola/università/ricerca', r'\bscuol|scolastic|universit|\bdocent|studenti|istruzione|\bricerca\b|\bAFAM\b|borse di studio|\bITS\b|dottorand|alunni'),
    ('Famiglia/sociale', r'famigli|\bfigli|disabil|non autosufficien|povertà|assegno unico|\bsocial[ei]\b|anzian|caregiver|\bminori\b|terzo settore|inclusione|vittim'),
    ('Casa', r'abitativ|\baffitt|locazion|\bmutu[oi]\b|prima casa|edilizia residenziale|\balloggi'),
    ('Infrastrutture/trasporti', r'infrastruttur|\bstrad[ae]\b|stradal|ferrovi|autostrad|\btrasport|viabilit|\bponte\b|\bporto\b|aeroport|metropolitan[ae] \b(?:linea|M\d)|ciclabil|\bTPL\b|\bviario'),
    ('Enti locali', r'\bcomuni\b|enti locali|\bprovince\b|città metropolitan|fondo di solidarietà comunale|\bsindac'),
    ('Cultura/turismo', r'cultur|\bturis|\bmuse[oi]|teatr|cinema|patrimonio (?:storico|artistico|culturale)|spettacolo|bibliotec|festival|UNESCO|Francigena|\bcammin|lirico|sinfonic|centenario|anniversari'),
    ('Sport', r'\bsport|\bstadi[oi]?\b|impianti sportivi|palestr|olimpi|\bcalcio\b'),
    ('Ambiente/energia', r'ambient|\benergi|rinnovabil|\bclima|emission|dissesto|idrogeolog|rifiut|bonific|\bacqua\b|\bidric|efficientamento|fotovoltaic'),
    ('Imprese/agricoltura', r'\bimpres[ae]\b|\bPMI\b|agricol|agroaliment|\bpesca\b|artigian|\bcommerci|industri|zootecn|filiera|start-?up'),
    ('Sicurezza/difesa/giustizia', r'polizia|carabinier|vigili del fuoco|forze armate|\bdifesa\b|sicurezza (?:pubblica|urbana)|giustizia|magistrat|carcer|penitenziar|militar'),
    ('Pubblica amministrazione', r'pubblic[ao] impieg|dipendenti pubblici|amministrazioni pubbliche|\bconcors|precariato|stabilizzazione del personale'),
    ('Mezzogiorno/aree interne', r'Mezzogiorno|aree interne|\bZES\b|coesione|\bSud\b|\bmontan|isole minori'),
]
THEMES = [(n, re.compile(p)) for n, p in THEMES]

def theme(title, text):
    s = (title or '') + ' ' + text[:2500]
    sc = []
    for n, rx in THEMES:
        k = len(rx.findall(s)) + (3 * len(rx.findall(title or '')))
        if k: sc.append((k, n))
    sc.sort(reverse=True)
    if sc and len(sc) > 1 and sc[1][0] < sc[0][0] / 3: sc = sc[:1]
    return [n for _, n in sc[:2]] or ['Altro']

# ---------- main parse ----------
MARK = re.compile(r"<b>(\*{0,3})((?:Tab\.[A-Z]\.\d+)|(?:Tab\.)?\d+(?:\.\d+)+)\.</b>\s*(.*?)(?=\n<br>|</p>)", re.S)
NOTE = re.compile(r"\(\s*(Inammissibil.*?)\)\s*(?=</i>|<)", re.S)
ART = re.compile(r'<p align="center">ART\.\s*(\d+[^<]*?)\.?\s*</p>')

events = []
for m in MARK.finditer(body):
    events.append(('M', m.start(), m.end(), m))
arts = [(m.start(), m.group(1).strip()) for m in ART.finditer(body)]

rows = []
prev_end = 0
i = 0
unmatched = collections.Counter()
N = len(events)
while i < N:
    # group consecutive markers (identical amendments)
    grp = [events[i]]
    j = i + 1
    while j < N:
        gap = body[grp[-1][2]:events[j][1]]
        gs = re.sub(r'<br>|<b>|</b>|<i>|</i>|\s', '', gap)
        gs = re.sub(r'\(Inammissibil.*?\)', '', strip(gap).replace('\n', ' '))
        if re.sub(r'[\s()]', '', gs) == '':
            grp.append(events[j]); j += 1
        else:
            break
    start = grp[0][1]
    text_html = body[prev_end:start]
    # text html may begin with leftover note from previous group; drop leading notes / closing tags
    text = strip(text_html)
    text = re.sub(r'^\s*\(\s*Inammissibil.*?\)\s*', '', text, flags=re.S)
    text = re.sub(r'^ART\.\s*\d+[^\n]*\n', '', text)
    # rubric for articoli aggiuntivi
    rub = None
    mr = re.search(r'Art\.\s*\d+-[a-z]+\.?\s*\n\s*\(([^)]{5,400})\)', text)
    # la rubrica vale come oggetto solo se l'articolo aggiuntivo apre l'emendamento:
    # più avanti di solito è l'articolo della copertura (es. «Tassazione rendite finanziarie»)
    if mr and mr.start() > 250: mr = None
    if not mr: mr = re.match(r'\s*Sostituirlo con il seguente:\s*Art\.\s*\d+(?:-[a-z]+)?\.?\s*\(([^)]{5,400})\)', text)
    if mr: rub = re.sub(r'\s+', ' ', mr.group(1)).strip()
    if not rub:
        tt = re.sub(r'\s+', ' ', text)
        tt = re.sub(r"^(?:Dopo l.articolo \d+[^:]*:\s*)?(?:Art\.\s*\d+(?:-[a-z]+)?\.\s*)?", '', tt)
        m1 = re.match(r"(.{0,90}?:)\s*(.*)", tt)
        if m1 and len(m1.group(2)) > 10:
            body_ = re.sub(r"^\d+(?:-[a-z]+)?\.\s*", '', m1.group(2))
            rub_auto = m1.group(1).rstrip(':') + ' → ' + body_[:120]
        else:
            rub_auto = re.sub(r"^\d+(?:-[a-z]+)?\.\s*", '', tt)[:150]
        rub_auto = rub_auto.strip()
    else:
        rub_auto = None
    art = None
    for p, a in arts:
        if p < start: art = a
    is_tab = grp[0][3].group(2).startswith('Tab')
    amt, amt3, prof_ = amounts(text, is_tab)
    if prof_ and amt:
        ys = sorted(y for y, v in prof_.items() if abs(v - amt) < 1)
        allyrs = sorted(prof_)
        if len(set(round(v) for v in prof_.values())) == 1 and len(allyrs) == 3: amt_y = 'ogni anno'
        elif len(set(round(v) for v in prof_.values())) == 1 and len(allyrs) > 1: amt_y = ', '.join(map(str, allyrs))
        else: amt_y = ', '.join(map(str, ys)) if ys else ''
    else:
        amt_y = ''
    if amt and not amt_y and re.search(r"annui\s+a\s+decorrere|a\s+decorrere\s+dal", text): amt_y = 'a regime'
    places, regs = find_places(text)
    tplace = re.split(r"(?:\n|\. )(?:Conseguentemente|Agli oneri|Ai relativi oneri|Ai maggiori oneri|All.onere)", text)[0]
    tplace = re.sub(r"[Ss]tretto di Messina|Ponte sullo Stretto|Domodossola-confine svizzero|ferrovia circumetnea", " ", tplace)
    tplace = re.sub(r"navigazione laghi Maggiore, di Garda e di Como|[Cc]ircumetnea|(?:[Pp]iazza|[Pp]iazzale|[Vv]ia|[Vv]iale|[Cc]orso|[Ll]argo) [A-Z][\w'’]+|sede (?:legale |operativa )?(?:in|a) [A-Z][\w'’]+", " ", tplace)
    places_map, _ = find_places(tplace)
    if re.search(r"\bnazional[ei]\b", (rub or '') + ' ' + tplace[:300]) and len(places_map) <= 2 and not re.search(r"(?:comune|città|provincia) di [A-Z]", (rub or '') + ' ' + tplace[:900]):
        places_map = []
    def _real(nm):
        if re.search(r"(?:[Cc]omun[ei]|[Cc]ittà|[Pp]rovincia|[Pp]rovince) (?:di|del|della) (?:[^.;]{0,60}?)" + re.escape(nm), tplace): return True
        return bool(re.search(r"(?<![-\w'’])" + re.escape(nm) + r"(?![\w-])(?!\s+[A-Z][a-zà-ù]{2,})", tplace))
    _STOP = {'Nave','Arco','Ala','Lana','Cento','Vasto','Mira','Calcio','Corte','Sale','Grado','Albino','Marino','Lavello','Bella','Ponte','Pace','Cassano','Monte','Riva'}
    places_map = [p for p in places_map if (_real(p['nome']) or p['nome'] not in tplace) and not (p['nome'] in _STOP and not re.search(r"(?:[Cc]omun[ei]|[Cc]ittà) di " + re.escape(p['nome']), tplace))]
    th = theme(rub, text)
    end_of_group = grp[-1][2]
    grp_rows_start = len(rows)
    for k, (_, s, e, m) in enumerate(grp):
        nxt = grp[k + 1][1] if k + 1 < len(grp) else None
        tail = body[e: (nxt if nxt else e + 600)]
        status = 'Ammissibile'
        reason = ''
        nm = re.match(r"\s*\n<br>\s*<b>\s*<i>\s*\(\s*(Inammissibil.*?)\)\s*</i>", tail, re.S)
        if not nm:
            nm = re.match(r"\s*\n?<br>\s*(?:<[bi]>\s*)+\(\s*(Inammissibil.*?)\)", tail, re.S)
        if nm:
            reason = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', nm.group(1))).strip()
            reason = re.sub(r'\s+\)', ')', reason).split(')')[0]
            status = 'Inammissibile'
            end_of_group = max(end_of_group, e + nm.end())
        sigs = [x.strip() for x in re.split(r',\s*', html.unescape(re.sub(r'<[^>]+>', '', m.group(3))).strip().rstrip('.')) if x.strip()]
        info = []
        for sname in sigs:
            c = lookup(sname)
            if not c:
                unmatched[sname] += 1
                info.append(dict(n=sname, g='?', c=''))
            else:
                d = c[0]
                info.append(dict(n=sname, g=GRP_LABEL.get(d['gruppo'], d['gruppo']), c=d['circ'], u=d['uni']))
        first = info[0] if info else dict(n='', g='?', c='')
        groups = sorted(set(x['g'] for x in info))
        num = m.group(2)
        if num.startswith('Tab'):
            artlbl = 'Tabelle'
        elif re.match(r'\d+\.0\d*', num):
            artlbl = 'Art. agg. dopo art. ' + num.split('.')[0]
        else:
            artlbl = 'Art. ' + num.split('.')[0]
        rows.append(dict(
            id=num, ident=m.group(1), art=artlbl, firm=sigs, firmInfo=info,
            primo=first['n'], gruppo=first['g'],
            coal=('Maggioranza' if first['g'] in MAGG else ('Misto' if first['g'] == 'Misto' else ('?' if first['g'] == '?' else 'Opposizione'))),
            gruppi=groups,
            circ=circ_region(first.get('c', '')), circFull=first.get('c', ''), uni=first.get('u', ''),
            stato=status, motivo=reason,
            luoghiMappa=places_map, importo=amt, importo3=amt3, importoAnno=amt_y, luoghi=places, regioni=regs, temi=th, titolo=rub, titoloAuto=rub_auto, testo=text,
            nIdent=len(grp)))
    gr = rows[grp_rows_start:]
    if len(gr) > 1 and gr[-1]['stato'] == 'Inammissibile' and all(x['stato'] == 'Ammissibile' for x in gr[:-1]):
        for x in gr[:-1]:
            x['stato'] = 'Inammissibile'; x['motivo'] = gr[-1]['motivo']
    prev_end = end_of_group
    i = j

# fix: estraneità flag
for r in rows:
    r['estraneo'] = 'estraneità' in r['motivo']
    provs_ = sorted(set(p['provincia'] for p in r['luoghi']))
    r['province'] = provs_
    regs_ = sorted(set([p['regione'] for p in r['luoghi'] if p['regione']] + r['regioni']))
    r['regTerr'] = [x.split('/')[0] for x in regs_]
    nreg = len(set(p['regione'] for p in r['luoghi']))
    if not r['luoghi']: r['portata'] = 'Nazionale'
    elif len(r['luoghi']) >= 6 and nreg >= 3: r['portata'] = 'Più territori'
    else: r['portata'] = 'Locale'
    r['localistico'] = r['portata'] == 'Locale'

json.dump(rows, open(OUTP, 'w', encoding='utf-8'), ensure_ascii=False)
print('rows', len(rows))
print('unmatched', unmatched.most_common(30))
c = collections.Counter(r['stato'] for r in rows); print(c)
print(collections.Counter(r['motivo'] for r in rows).most_common(15))
print(collections.Counter(r['gruppo'] for r in rows).most_common())
print('local', sum(r['localistico'] for r in rows))
print('with amt', sum(1 for r in rows if r['importo']))
