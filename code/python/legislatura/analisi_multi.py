"""Analisi pluriennale 2023-2027: voti 2022 e richieste locali; probabilità di approvazione.
OLS con effetti fissi, errori standard cluster (CR1)."""
import json, math, collections
import numpy as np

B = '/home/claude/multi/'; E = '/home/claude/emend/'
R = json.load(open(B + 'out/multi_rows.json'))
POP = json.load(open(E + 'site/popolazione.json'))
V = json.load(open(E + 'data/voti2022.json')); K = V['K']; VP = V['prov']
topo = json.load(open(E + 'site/province.topo.json'))
REG = {g['properties']['prov_name']: g['properties']['reg_name'] for g in topo['objects']['provinces']['geometries']}
PARTIES = ['FdI', 'Lega', 'FI', 'Noi Moderati', 'PD', 'M5S', 'AVS', 'Azione / IV']
KMAP = {'FdI': 'FdI', 'Lega': 'Lega', 'FI': 'FI', 'Noi Moderati': 'NM', 'PD': 'PD', 'M5S': 'M5S', 'AVS': 'AVS', 'Azione / IV': 'AzIV'}
YEARS = [2023, 2024, 2025, 2026, 2027]
provs = [p for p in VP if p in POP]

def ols(y, X, cl):
    X = np.asarray(X, float); y = np.asarray(y, float)
    XtX = np.linalg.pinv(X.T @ X); b = XtX @ X.T @ y; e = y - X @ b
    n, kx = X.shape; G = sorted(set(cl)); g = len(G); idx = {c: i for i, c in enumerate(G)}
    S = np.zeros((g, kx))
    for i in range(n): S[idx[cl[i]]] += X[i] * e[i]
    rank = np.linalg.matrix_rank(X)
    Vc = XtX @ (S.T @ S) @ XtX * (g / (g - 1)) * ((n - 1) / (n - rank))
    return b, np.sqrt(np.abs(np.diag(Vc))), n, g

def dummies(vals):
    lv = sorted(set(vals))[1:]
    return [[1.0 if v == l else 0.0 for l in lv] for v in vals]

# ---------- panel provincia × partito × manovra ----------
cnt = collections.Counter(); cntA = collections.Counter(); eur = collections.Counter()
for r in R:
    if r['g'] not in PARTIES or not r['pm']: continue
    for p in set(r['pm']):
        cnt[(p, r['g'], r['anno'])] += 1
        if r['es'] == 'Approvato': cntA[(p, r['g'], r['anno'])] += 1
        if not r['big']: eur[(p, r['g'], r['anno'])] += (r['e3'] or r['e'] or 0) / len(set(r['pm']))
panel = []
for y in YEARS:
    for g in PARTIES:
        for p in provs:
            sh = VP[p][K.index(KMAP[g])] / VP[p][0] * 100
            panel.append(dict(p=p, reg=REG[p], g=g, y=y, share10=sh / 10, any=1 if cnt[(p, g, y)] else 0, anyA=1 if cntA[(p, g, y)] else 0,
                              n=cnt[(p, g, y)], eur=eur[(p, g, y)]))

def model(sub, yv, fe):
    cols = [[r['share10'], 1.0] for r in sub]
    for f in fe:
        D = dummies([f(r) for r in sub])
        cols = [c + d for c, d in zip(cols, D)]
    b, se, n, g = ols([r[yv] for r in sub], cols, [r['p'] for r in sub])
    return dict(b=float(b[0]) * 100, se=float(se[0]) * 100, n=n, g=g, mean=float(np.mean([r[yv] for r in sub])) * 100)

gy = lambda r: r['g'] + str(r['y'])
M = {}
M['pooled_regFE'] = model(panel, 'any', [gy, lambda r: r['reg']])
M['within_partyXreg'] = model(panel, 'any', [gy, lambda r: r['g'] + r['reg']])
M['pooled_noRegFE'] = model(panel, 'any', [gy])
M['approved_regFE'] = model([r for r in panel if r['y'] < 2027], 'anyA', [gy, lambda r: r['reg']])
M['by_year'] = {y: model([r for r in panel if r['y'] == y], 'any', [lambda r: r['g'], lambda r: r['reg']]) for y in YEARS}
M['by_year_within'] = {y: model([r for r in panel if r['y'] == y], 'any', [lambda r: r['g'] + r['reg']]) for y in YEARS}

# ---------- probabilità di approvazione (emendamento) ----------
sub = [r for r in R if r['lett'] == 1 and r['anno'] < 2027 and r['coal'] in ('Maggioranza', 'Opposizione')]
X = []; y = []; cl = []
fe = dummies([r['ramo'] + str(r['anno']) for r in sub])
for r, d in zip(sub, fe):
    mag = 1.0 if r['coal'] == 'Maggioranza' else 0.0; loc = 1.0 if r['po'] == 'Locale' else 0.0
    X.append([mag, loc, mag * loc, 1.0] + d); y.append(1.0 if r['es'] == 'Approvato' else 0.0); cl.append(r['pid'] or r['p'])
b, se, n, g = ols(y, X, cl)
APP = dict(mag=dict(b=b[0] * 100, se=se[0] * 100), loc=dict(b=b[1] * 100, se=se[1] * 100), magloc=dict(b=b[2] * 100, se=se[2] * 100), n=n, g=g,
           base=float(np.mean([v for v, x in zip(y, X) if x[0] == 0 and x[1] == 0])) * 100)
# tasso di approvazione per gruppi (solo prime letture già votate)
rate = {}
for c in ['Maggioranza', 'Opposizione']:
    for lo in ['Locale', 'Altro']:
        s = [r for r in sub if r['coal'] == c and ((r['po'] == 'Locale') == (lo == 'Locale'))]
        rate[c + '|' + lo] = [len(s), sum(r['es'] == 'Approvato' for r in s)]
# per anno e ramo
ap_y = {}
for r in sub:
    k = r['ramo'] + ' ' + str(r['anno'])
    a = ap_y.setdefault(k, {'Maggioranza': [0, 0], 'Opposizione': [0, 0]})
    a[r['coal']][0] += 1; a[r['coal']][1] += r['es'] == 'Approvato'

# ---------- tutte le combinazioni di anni (da a) ----------
def approval_model(ys):
    sub = [r for r in R if r['lett'] == 1 and r['anno'] in ys and r['anno'] < 2027 and r['coal'] in ('Maggioranza', 'Opposizione')]
    if len(sub) < 200: return None
    fev = [r['ramo'] + str(r['anno']) for r in sub]
    fe = dummies(fev) if len(set(fev)) > 1 else [[] for _ in sub]
    X = []; y = []; cl = []
    for r, d in zip(sub, fe):
        mag = 1.0 if r['coal'] == 'Maggioranza' else 0.0; loc = 1.0 if r['po'] == 'Locale' else 0.0
        X.append([mag, loc, mag * loc, 1.0] + d); y.append(1.0 if r['es'] == 'Approvato' else 0.0); cl.append(r['pid'] or r['p'])
    b, se, n, g = ols(y, X, cl)
    return dict(mag=dict(b=b[0] * 100, se=se[0] * 100), loc=dict(b=b[1] * 100, se=se[1] * 100), magloc=dict(b=b[2] * 100, se=se[2] * 100), n=n, g=g,
                base=float(np.mean([v for v, x in zip(y, X) if x[0] == 0 and x[1] == 0])) * 100)
RANGES = {}
for a in YEARS:
    for b_ in YEARS:
        if b_ < a: continue
        ys = set(range(a, b_ + 1)); sp = [r for r in panel if r['y'] in ys]
        d = dict(pooled=model(sp, 'any', [gy, lambda r: r['reg']]), within=model(sp, 'any', [gy, lambda r: r['g'] + r['reg']]),
                 nofe=model(sp, 'any', [gy]))
        spa = [r for r in sp if r['y'] < 2027]
        d['approved'] = model(spa, 'anyA', [gy, lambda r: r['reg']]) if spa and sum(r['anyA'] for r in spa) >= 10 else None
        d['approval'] = approval_model(ys)
        RANGES[f'{a}-{b_}'] = d
out = dict(ranges=RANGES, models=M, approval=APP, rate=rate, ap_y=ap_y,
           npanel=len(panel), nprov=len(provs))
json.dump(out, open(B + 'site/analisi_multi.json', 'w'), ensure_ascii=False, default=float)
for k, v in M.items(): print(k, v)
print('APP', APP); print(rate); print(ap_y)
# pannello per replica
cols = ['provincia', 'regione', 'partito', 'manovra', 'voti_2022_pct', 'richiesta_locale_0_1', 'richiesta_approvata_0_1', 'n_emendamenti_locali', 'euro_stimati']
json.dump(dict(cols=cols, rows=[[r['p'], r['reg'], r['g'], r['y'], round(r['share10'] * 10, 3), r['any'], r['anyA'], r['n'], round(r['eur'])] for r in panel]),
          open(B + 'site/panel_multi.json', 'w'), ensure_ascii=False, separators=(',', ':'))
