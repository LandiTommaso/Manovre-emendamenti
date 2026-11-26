"""Analisi empirica: voti 2022, deputati eletti e richieste di spesa locale.

Unità: provincia i × partito p (8 partiti, 109 province; esclusa la Valle d'Aosta).
Stima OLS con effetti fissi di partito (e di regione), errori standard
robusti a cluster per provincia (CR1). Output: site/analisi.json
"""
import json, math, re, unicodedata
import numpy as np

B = '/home/claude/emend/'
R = json.load(open(B + 'site/emendamenti.json'))['rows']
POP = json.load(open(B + 'site/popolazione.json'))
V = json.load(open(B + 'data/voti2022.json')); K = V['K']; VP = V['prov']
PC = json.load(open(B + 'data/prov_collegi2022.json'))['prov']
topo = json.load(open(B + 'site/province.topo.json'))
REG = {g['properties']['prov_name']: g['properties']['reg_name'] for g in topo['objects']['provinces']['geometries']}
PALIAS = {'Sud Sardegna': 'Sulcis Iglesiente'}

PARTIES = [('FdI', 'FdI', ['FdI'], ['FDI']), ('Lega', 'Lega', ['Lega'], ['LEGA']), ('FI', 'FI', ['FI'], ['FI-PPE']),
           ('NM', 'Noi Moderati', ['Noi Moderati'], ['NM(N-C-U-I)M-CP']), ('PD', 'PD', ['PD'], ['PD-IDP']),
           ('M5S', 'M5S', ['M5S'], ['M5S']), ('AVS', 'AVS', ['AVS'], ['AVS']), ('AzIV', 'Azione + IV', ['Azione', 'IV'], ['AZ-PER-RE', 'IV-CR'])]

def norm(s):
    return re.sub(r'[^A-Z0-9]', '', unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode().upper())

# deputati in carica per collegio plurinominale
dep = {}
for line in open(B + 'data/deputati.txt', encoding='utf-8'):
    f = line.rstrip('\n').split('|')
    if len(f) < 6 or f[5].strip() != '1': continue
    for k, lab, gs, codes in PARTIES:
        if f[2] in codes:
            dep.setdefault(k, set()).add(norm(f[3]))
provs = [p for p in VP if p in POP]
ALL_REG = sorted(set(REG[p] for p in provs))

def home_share(k, p):
    cols = PC[p]; tot = sum(cols.values())
    return sum(v for c, v in cols.items() if norm(c) in dep.get(k, set())) / tot

def money(gs, admissible=False):
    E, N = {}, {}
    for r in R:
        if r['g'] not in gs or not r['pm']: continue
        if admissible and r['s'] != 'Ammissibile': continue
        amt = r['e3'] or r['e'] or 0
        for p0 in r['pm']:
            p = PALIAS.get(p0, p0)
            E[p] = E.get(p, 0) + amt / len(r['pm']); N[p] = N.get(p, 0) + 1
    return E, N

# closeness: distacco CDX - CSX (punti percentuali)
ix = K.index
def margin(p):
    v = VP[p]; cdx = v[ix('FdI')] + v[ix('Lega')] + v[ix('FI')] + v[ix('NM')]; csx = v[ix('PD')] + v[ix('AVS')] + v[ix('PiuE')]
    return abs(cdx - csx) / v[0] * 100

rows = []
for k, lab, gs, _ in PARTIES:
    E, N = money(gs); Ea, Na = money(gs, True)
    for p in provs:
        pc = E.get(p, 0) / POP[p]; pca = Ea.get(p, 0) / POP[p]
        rows.append(dict(prov=p, reg=REG[p], party=k, lab=lab, share=VP[p][ix(k)] / VP[p][0] * 100,
                         any=1 if N.get(p) else 0, eur=E.get(p, 0), pc=pc, ihs=math.asinh(pc),
                         any_a=1 if Na.get(p) else 0, ihs_a=math.asinh(pca), n=N.get(p, 0),
                         home=home_share(k, p), close=-margin(p) / 10, pop=POP[p]))

def ols(y, X, cl):
    X = np.asarray(X, float); y = np.asarray(y, float)
    XtX = np.linalg.pinv(X.T @ X); b = XtX @ X.T @ y; e = y - X @ b
    n, kx = X.shape; G = sorted(set(cl)); g = len(G); idx = {c: i for i, c in enumerate(G)}
    S = np.zeros((g, kx))
    for i in range(n): S[idx[cl[i]]] += X[i] * e[i]
    meat = S.T @ S; V = XtX @ meat @ XtX * (g / (g - 1)) * ((n - 1) / (n - kx))
    r2 = 1 - (e @ e) / ((y - y.mean()) @ (y - y.mean()))
    return b, np.sqrt(np.diag(V)), r2, n, g

def design(sub, regs, region_fe=True):
    names = list(regs); X = []
    pl = [k for k, *_ in PARTIES]; rl = ALL_REG
    for r in sub:
        row = [r[v] for v in regs] + [1.0] + [1.0 if r['party'] == q else 0.0 for q in pl[1:]]
        if region_fe: row += [1.0 if r['reg'] == q else 0.0 for q in rl[1:]]
        X.append(row)
    return X, names

def model(yv, regs, region_fe=True, filt=None, label='', pr_fe=False):
    sub = [r for r in rows if (filt is None or filt(r))]
    X, names = design(sub, regs, region_fe and not pr_fe)
    if pr_fe:
        cells = sorted(set((r['party'], r['reg']) for r in sub))[1:]
        X = [[r[v] for v in regs] + [1.0] + [1.0 if (r['party'], r['reg']) == c else 0.0 for c in cells] for r in sub]
    b, se, r2, n, g = ols([r[yv] for r in sub], X, [r['prov'] for r in sub])
    coefs = {nm: dict(b=float(b[i]), se=float(se[i])) for i, nm in enumerate(names)}
    return dict(label=label, y=yv, coefs=coefs, r2=float(r2), n=n, clusters=g, mean=float(np.mean([r[yv] for r in sub])),
                pfe=True, rfe=region_fe, prfe=pr_fe)

# scala: share in unità da 10 punti
for r in rows: r['share10'] = r['share'] / 10
OUT = '(Taranto|Siracusa)'
models = [
    model('any', ['share10'], False, label='(1)'),
    model('any', ['share10'], True, label='(2)'),
    model('any', ['share10', 'home'], True, label='(3)'),
    model('any', ['share10', 'close'], True, label='(4)'),
    model('ihs', ['share10', 'home'], True, label='(5)'),
    model('ihs', ['share10', 'home'], True, filt=lambda r: not re.match(OUT, r['prov']), label='(6)'),
    model('ihs_a', ['share10', 'home'], True, label='(7)'),
    model('any', ['share10', 'home'], True, label='(8)', pr_fe=True),
]
# eterogeneità: pendenza per partito (any ~ share10 per partito + FE regione), cluster provincia
het = []
for k, lab, *_ in PARTIES:
    sub = [r for r in rows if r['party'] == k]
    X = [[r['share10'], 1.0] + [1.0 if r['reg'] == q else 0.0 for q in ALL_REG[1:]] for r in sub]
    b, se, r2, n, g = ols([r['any'] for r in sub], X, [r['prov'] for r in sub])
    X0 = [[r['share10'], 1.0] for r in sub]
    b0, se0, *_ = ols([r['any'] for r in sub], X0, [r['prov'] for r in sub])
    het.append(dict(k=k, lab=lab, b=float(b[0]), se=float(se[0]), b0=float(b0[0]), se0=float(se0[0]), n=n, nany=sum(r['any'] for r in sub)))

# binscatter (FWL: residui su FE partito + regione, 20 bin per quantili, media riaggiunta)
def resid(v):
    X, _ = design(rows, [], True); X = np.asarray(X); y = np.array([r[v] for r in rows])
    b = np.linalg.pinv(X.T @ X) @ X.T @ y; return y - X @ b + y.mean()
rx, ry = resid('share10'), resid('any')
order = np.argsort(rx); nb = 20; bins = []
for chunk in np.array_split(order, nb):
    bins.append(dict(x=float(rx[chunk].mean() * 10), y=float(ry[chunk].mean())))
slope = models[1]['coefs']['share10']['b']
line = dict(b=slope / 10, a=float(ry.mean() - slope / 10 * rx.mean() * 10))
# descrittive
desc = dict(n=len(rows), provs=len(provs), parties=len(PARTIES), any_mean=float(np.mean([r['any'] for r in rows])),
            share_mean=float(np.mean([r['share'] for r in rows])), home_mean=float(np.mean([r['home'] for r in rows])),
            pc_mean_pos=float(np.mean([r['pc'] for r in rows if r['any']])),
            collegi_con_deputati=sum(len(v) for v in dep.values()))
panel = [[r['prov'], r['reg'], r['lab'], round(r['share'], 3), r['any'], round(r['eur']), round(r['pc'], 3), round(r['home'], 4), round(-r['close'] * 10, 3), r['n'], r['pop']] for r in rows]
json.dump(dict(models=models, het=het, bins=bins, line=line, desc=desc, panel=panel,
               panel_cols=['provincia', 'regione', 'partito', 'voti_2022_pct', 'richiesta_0_1', 'euro_2027_29', 'euro_per_abitante', 'quota_elettori_in_collegi_con_deputato', 'distacco_cdx_csx_punti', 'n_emendamenti', 'popolazione_2025']),
          open(B + 'site/analisi.json', 'w'), ensure_ascii=False)
for m in models:
    print(m['label'], m['y'], {k: (round(v['b'], 4), round(v['se'], 4)) for k, v in m['coefs'].items()}, 'R2', round(m['r2'], 3), 'N', m['n'], 'G', m['clusters'], 'mean', round(m['mean'], 3))
for h in het: print(h)
print(desc)

# ---- robustezza (statsmodels): logit con effetti marginali e test di permutazione ----
try:
    import pandas as pd, statsmodels.formula.api as smf, warnings
    warnings.filterwarnings('ignore')
    df = pd.DataFrame([dict(p=r['prov'], party=r['party'], reg=r['reg'], y=r['any'], s=r['share10']) for r in rows])
    g = pd.factorize(df.p)[0]
    lg = smf.logit('y ~ s + C(party) + C(reg)', df).fit(disp=0, cov_type='cluster', cov_kwds={'groups': g})
    ame = float(lg.get_margeff().summary_frame().loc['s', 'dy/dx'])
    rng = np.random.default_rng(20261126); NP = 500
    b_obs = models[1]['coefs']['share10']['b']; b8 = models[7]['coefs']['share10']['b']
    perm1 = []; perm2 = []
    for _ in range(NP):
        x = df.copy(); x['s'] = x.groupby('party').s.transform(lambda v: rng.permutation(v.values))
        perm1.append(smf.ols('y ~ s + C(party) + C(reg)', x).fit().params['s'])
        x = df.copy(); x['s'] = x.groupby(['party', 'reg']).s.transform(lambda v: rng.permutation(v.values))
        perm2.append(smf.ols('y ~ s + C(party):C(reg)', x).fit().params['s'])
    rob = dict(logit_ame=ame, logit_b=float(lg.params['s']), logit_se=float(lg.bse['s']), nperm=NP,
               p_perm_pooled=float(np.mean(np.abs(perm1) >= abs(b_obs))), p_perm_within=float(np.mean(np.abs(perm2) >= abs(b8))),
               perm_pooled_p95=float(np.percentile(np.abs(perm1), 95)))
except Exception as ex:
    rob = dict(error=str(ex))
J = json.load(open(B + 'site/analisi.json')); J['rob'] = rob; json.dump(J, open(B + 'site/analisi.json', 'w'), ensure_ascii=False)
print('ROB', rob)
