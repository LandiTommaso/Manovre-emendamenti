import re, html, json, unicodedata, collections
D = '/home/claude/emend/data/'
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
YRS = (2027, 2028, 2029)
def set_years(y0):
    global YRS
    YRS = (y0, y0+1, y0+2)

def _val(m):
    v = tonum(m.group(1))
    if v is None: return None
    if v < 100000: v *= MULT.get((m.group(2) or '').lower(), 1)
    return v

def _years_after(tail):
    """anni a cui si riferisce una cifra, letti nelle parole che la seguono"""
    t = tail
    mm = re.match(r"\s*(?:annui\s+)?(?:per\s+)?ciascun[oa]?\s+(?:degli\s+anni|anno)\s+(?:del\s+triennio\s+|dal\s+)?(\d{4})\s*(?:[-–]|al|e)\s*(\d{4})(?!\s*,)", t)
    if mm and ' e ' not in mm.group(0):
        return list(range(int(mm.group(1)), int(mm.group(2)) + 1))
    mm = re.match(r"\s*(?:annui\s+)?(?:per\s+)?ciascun[oa]?\s+degli\s+anni\s+(?:dal\s+)?((?:\d{4}(?:,\s*|\s+e\s+|\s+al\s+)?)+)", t)
    if mm:
        ys = [int(y) for y in re.findall(r'\d{4}', mm.group(1))]
        if ' al ' in mm.group(1) and len(ys) == 2: ys = list(range(ys[0], ys[1] + 1))
        return ys
    mm = re.match(r"\s*(?:complessiv[ie]\s+)?(?:nel|per\s+il)\s+(?:biennio|triennio)\s+(\d{4})\s*[-–]\s*(\d{4})", t)
    if mm:
        ys = list(range(int(mm.group(1)), int(mm.group(2)) + 1)); return [('tot', y, len(ys)) for y in ys]
    mm = re.match(r"\s*(?:annui\s+)?per\s+gli\s+anni\s+(\d{4})\s*[-–]\s*(\d{4})", t)
    if mm: return list(range(int(mm.group(1)), int(mm.group(2)) + 1))
    mm = re.match(r"\s*(?:annui\s+)?per\s+gli\s+anni\s+((?:\d{4}(?:,\s*|\s+e\s+)?)+)", t)
    if mm: return [int(y) for y in re.findall(r'\d{4}', mm.group(1))]
    mm = re.match(r"\s*(?:annui\s+)?(?:per\s+l.anno|nell.anno|per\s+il|nel)\s+(\d{4})", t)
    if mm: return [int(mm.group(1))]
    mm = re.match(r"\s*(?:annui\s+|(?:al)?l.anno\s+|in\s+ragione\s+(?:d.)?annua\s+|ogni\s+anno\s+)?(?:,\s*)?a\s+(?:decorrere|partire)\s+dal(?:l.anno)?\s+(\d{4})", t)
    if mm: return list(range(int(mm.group(1)), YRS[-1] + 1))
    if re.match(r"\s*annui", t): return list(YRS)
    return []

def year_profile(text, need_spend=True):
    """cifra per ciascun anno della manovra (anno, anno+1, anno+2) dalle clausole di spesa"""
    prof = {}
    for sent in re.split(r'(?<=[.;])\s+', text):
        if need_spend and not SPEND.search(sent): continue
        for m in AMT.finditer(sent):
            v = _val(m)
            if not v or v < 1000 or v > 5e10: continue
            if BADCTX.search(sent[max(0, m.start() - 70):m.start()]): continue
            for y in _years_after(sent[m.end():m.end() + 160]):
                w = v
                if isinstance(y, tuple): w = v / y[2]; y = y[1]
                if y in YRS: prof[y] = max(prof.get(y, 0), w)
    return prof

REPL = [re.compile(r"sostitui(?:re|te|ta|to) (?:le parole|la parola)?:?\s*«?([^»]{0,200}?)»?\s+con (?:le|la) seguent[ei]:?\s*«?([^»]{0,200}?)(?:»|\.\s|;|\.?\s*$)"),
        re.compile(r"«([^»]{0,200})»\s*,?\s+(?:sono\s+sostituit[ei]|è\s+sostituit[ao])\s+dall[ae]\s+seguent[ei]:?\s*«([^»]{0,200})»")]
def replacement_deltas(text):
    """modifiche di cifre già in legge: conta la differenza (nuova cifra meno vecchia), anno per anno se il testo lo dice"""
    out = []
    for rx in REPL:
        for m in rx.finditer(text):
            if any(a <= m.start() < b for a, b, _, _ in out): continue
            a = [_val(x) for x in AMT.finditer(m.group(1))]
            b = [_val(x) for x in AMT.finditer(m.group(2))]
            a = [x for x in a if x]; b = [x for x in b if x]
            if a and b:
                # la cifra vecchia non è una richiesta: il tratto si toglie sempre dal testo; conta solo l'aumento
                pa, pb = year_profile(m.group(1), False), year_profile(m.group(2), False)
                dp = {y: pb.get(y, 0) - pa.get(y, 0) for y in set(pa) | set(pb)} if (pa and pb) else {}
                dp = {y: v for y, v in dp.items() if v > 0}
                d = max([y - x for x, y in zip(a, b)] + [0]) if len(a) == len(b) else max(sum(dp.values()), 0)
                out.append((m.start(), m.end(), d, dp))
    out.sort()
    return out

def amounts(text, is_tab):
    """returns (max annual, total 2027-29)"""
    text = re.sub(r"\beuro\s+(\d{1,3}(?:\.\d{3})+(?:,\d+)?|\d+(?:,\d+)?)", r"\1 euro", text)
    yv = {}
    if is_tab or re.search(r"\bCP:\s*[+-]?\s*\d", text):
        for blk in re.finditer(r"(20\d\d):\s*CP:\s*([+-]?)\s*([\d.]+)", text):
            y, sign, v = int(blk.group(1)), blk.group(2), tonum(blk.group(3))
            if v and sign != '-':
                yv[y] = yv.get(y, 0) + v
        if yv and is_tab:
            tot = sum(v for y, v in yv.items() if y in YRS)
            return max(yv.values()), tot or None, {y:v for y,v in yv.items() if y in YRS}
    deltas = replacement_deltas(text)
    t2 = text
    for a, b, _, _ in reversed(deltas):
        t2 = t2[:a] + ' ' + t2[b:]
    pref, allv = [d for _, _, d, _ in deltas if d > 0], []
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
    dprof = {}
    for _, _, _, dp in deltas:
        for y, v in dp.items(): dprof[y] = dprof.get(y, 0) + v
    if deltas:
        for y, v in dprof.items(): prof[y] = prof.get(y, 0) + v
    cpv = {y: v for y, v in yv.items() if y in YRS}
    if not prof and cpv and not any(d > 0 for _, _, d, _ in deltas):   # variazioni di tabella (CP: +…) come unica spesa con anni
        prof = cpv; mx = max(cpv.values())
    pos = any(d > 0 for _, _, d, _ in deltas)
    if prof and not pos: mx = max(prof.values())
    tot = sum(prof.values()) if prof else None
    if mx and tot and tot < mx and not pos: tot = None
    return mx, tot, (prof if prof else {})


_CUTRE = re.compile(r"(?:\n|\.\s+|;\s+)(?:Conseguentemente|Agli oneri|Ai relativi oneri|Ai maggiori oneri|All.onere|Alla copertura|Ai fini della copertura|Per la copertura)")
ONERI = re.compile(r"(?:[Aa]gli|[Aa]i|[Aa]ll.)\s*(?:maggiori\s+|relativi\s+|nuovi\s+)?oner[ei][^.;]{0,220}?(?:pari\s+a|valutat[ie]\s+in|quantificat[ie]\s+in|nel\s+limite\s+(?:massimo\s+)?di|ammontano\s+a)([^;:]{0,400}?)(?:,?\s*(?:si\s+provvede|si\s+fa\s+fronte|mediante|a\s+valere|all.articolo|alla\s+[Tt]abella|sostituire|[Cc]onseguentemente)|\.\s|:|$)")
def oneri_profile(text):
    """costo dichiarato dal proponente nella clausola di copertura («Agli oneri ..., pari a X per l'anno ...»)"""
    prof = {}; seen = []
    for m in ONERI.finditer(text):
        seg = re.sub(r"\bmln\b\.?", "milioni", m.group(1)); seg = re.sub(r"\bmld\b\.?", "miliardi", seg)
        seg = re.sub(r"(\d[\d.,]*\s*(?:milioni|miliardi|milione|miliardo|mila))(?!\s*(?:di\s+)?euro)", r"\1 di euro", seg)
        if any(int(y) < YRS[0] for y in re.findall(r'\b(20\d\d)\b', seg)): continue   # cita gli oneri di una legge già in vigore (anni passati)
        p = year_profile('oneri ' + seg, False)
        if not p or p in seen: continue   # la stessa cifra ripetuta (dichiarazione e copertura) si conta una volta
        seen.append(p)
        for y, v in p.items(): prof[y] = prof.get(y, 0) + v
    return prof

def amounts_body(text, is_tab):
    """come amounts(), ma se la clausola di copertura gonfia le cifre usa solo la parte dispositiva
    (prima di «Conseguentemente», «Agli oneri», ecc.), purché lì ci sia un profilo annuo di spesa."""
    r = amounts(text, is_tab)
    if is_tab: return r
    op = oneri_profile(text)
    if op: return max(op.values()), sum(op.values()), op
    body = _CUTRE.split(text)[0]
    if len(body) < len(text) - 20:
        n = amounts(body, False)
        if n[0] and n[0] >= 1e5 and (n[2] or any(d > 0 for _, _, d, _ in replacement_deltas(body))) and (n[1] or n[0]) < (r[1] or r[0] or 0): return n
    return r

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

