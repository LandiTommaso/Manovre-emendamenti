"""Stime e figure per il working paper. Output: paper/tables/*.tex, paper/fig/*.pdf, paper/stats.json"""
import json, math, collections, os, re
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')

B = '/home/claude/multi/'; E = '/home/claude/emend/'; P = B + 'paper/'
os.makedirs(P + 'tables', exist_ok=True); os.makedirs(P + 'fig', exist_ok=True)
R = json.load(open(B + 'out/multi_rows.json'))
POP = json.load(open(E + 'site/popolazione.json'))
V = json.load(open(E + 'data/voti2022.json')); K = V['K']; VP = V['prov']
topo = json.load(open(E + 'site/province.topo.json'))
REG = {g['properties']['prov_name']: g['properties']['reg_name'] for g in topo['objects']['provinces']['geometries']}
PARTIES = ['FdI', 'Lega', 'FI', 'Noi Moderati', 'PD', 'M5S', 'AVS', 'Azione / IV']
KMAP = {'FdI': 'FdI', 'Lega': 'Lega', 'FI': 'FI', 'Noi Moderati': 'NM', 'PD': 'PD', 'M5S': 'M5S', 'AVS': 'AVS', 'Azione / IV': 'AzIV'}
YEARS = [2023, 2024, 2025, 2026, 2027]
provs = [p for p in VP if p in POP]
S = {}

def build_panel(filt=lambda r: True):
    cnt = collections.Counter(); cntA = collections.Counter()
    for r in R:
        if r['g'] not in PARTIES or not r['pm'] or not filt(r): continue
        for p in set(r['pm']):
            cnt[(p, r['g'], r['anno'])] += 1
            if r['es'] == 'Approvato': cntA[(p, r['g'], r['anno'])] += 1
    rows = []
    for y in YEARS:
        for g in PARTIES:
            for p in provs:
                sh = VP[p][K.index(KMAP[g])] / VP[p][0] * 100
                n = cnt[(p, g, y)]
                rows.append(dict(p=p, reg=REG[p], g=g, y=y, s=sh / 10, share=sh, any=int(n > 0), anyA=int(cntA[(p, g, y)] > 0), n=n,
                                 ihs=math.asinh(n / POP[p] * 1e5), gy=g + str(y), gr=g + REG[p], pop=POP[p]))
    return pd.DataFrame(rows)

D = build_panel()
D.to_csv(P + 'panel.csv', index=False)
import patsy
class _Fit:
    pass
def fit(f, d, cl='p'):
    """OLS con SE cluster CR1 (stessa formula del sito); robusto a molti effetti fissi."""
    y, X = patsy.dmatrices(f, d, return_type='dataframe')
    Xv = X.values; yv = y.values[:, 0]
    XtX = np.linalg.pinv(Xv.T @ Xv); b = XtX @ Xv.T @ yv; e = yv - Xv @ b
    g = pd.factorize(d.loc[X.index, cl])[0]; G = g.max() + 1
    Sm = np.zeros((G, Xv.shape[1])); np.add.at(Sm, g, Xv * e[:, None])
    n = len(yv); k = np.linalg.matrix_rank(Xv)
    Vc = XtX @ (Sm.T @ Sm) @ XtX * (G / (G - 1)) * ((n - 1) / (n - k))
    m = _Fit(); m.params = pd.Series(b, X.columns); m.bse = pd.Series(np.sqrt(np.abs(np.diag(Vc))), X.columns)
    m.nobs = n; m.rsquared = 1 - (e @ e) / ((yv - yv.mean()) @ (yv - yv.mean())); m.fittedvalues = pd.Series(Xv @ b, X.index)
    return m
def co(m, v='s'): return dict(b=float(m.params[v]) * 100, se=float(m.bse[v]) * 100, n=int(m.nobs), r2=float(m.rsquared))

# Tabella 2: principali
T2 = {}
T2['c1'] = co(fit('any ~ s + C(gy)', D))
T2['c2'] = co(fit('any ~ s + C(gy) + C(reg)', D))
T2['c3'] = co(fit('any ~ s + C(gy) + C(gr)', D))
T2['c4'] = co(fit('ihs ~ s + C(gy) + C(reg)', D)); T2['c4']['b'] /= 100; T2['c4']['se'] /= 100
T2['c5'] = co(fit('ihs ~ s + C(gy) + C(gr)', D)); T2['c5']['b'] /= 100; T2['c5']['se'] /= 100
DA = D[D.y < 2027]
T2['c6'] = co(fit('anyA ~ s + C(gy) + C(reg)', DA))
T2['c7'] = co(fit('anyA ~ s + C(gy) + C(gr)', DA))
for k in T2: T2[k]['mean'] = float((D if k in ('c1', 'c2', 'c3') else DA if k in ('c6', 'c7') else D)[('any' if k in ('c1', 'c2', 'c3') else 'anyA' if k in ('c6', 'c7') else 'ihs')].mean()) * (100 if k not in ('c4', 'c5') else 1)
S['T2'] = T2
S['nprov'] = len(provs); S['nobs'] = len(D)

# per anno
BY = {}
for y in YEARS:
    d = D[D.y == y]
    BY[y] = dict(pooled=co(fit('any ~ s + C(g) + C(reg)', d)), within=co(fit('any ~ s + C(gr)', d)), mean=float(d['any'].mean()) * 100)
S['BY'] = BY

# robustezza (within, party×region FE)
ROB = {}
def within(d, y='any'): return co(fit(f'{y} ~ s + C(gy) + C(gr)', d))
def pooledr(d, y='any'): return co(fit(f'{y} ~ s + C(gy) + C(reg)', d))
for name, f in [('camera', lambda r: r['ramo'] == 'Camera'), ('senato', lambda r: r['ramo'] == 'Senato'), ('first', lambda r: r['lett'] == 1),
                ('nogov', lambda r: True)]:
    d = build_panel(f); ROB[name] = dict(pooled=pooledr(d), within=within(d))
d = D[D.y != 2023]; ROB['no2023'] = dict(pooled=pooledr(d), within=within(d))
d = D[D.y != 2027]; ROB['no2027'] = dict(pooled=pooledr(d), within=within(d))
d = D[~D.p.isin(['Roma', 'Milano', 'Napoli', 'Torino'])]; ROB['nometro'] = dict(pooled=pooledr(d), within=within(d))
# logit AME
lg = smf.logit('any ~ s + C(gy) + C(reg)', D).fit(disp=0, cov_type='cluster', cov_kwds={'groups': pd.factorize(D.p)[0]})
ROB['logit_ame'] = float(lg.get_margeff().summary_frame().loc['s', 'dy/dx']) * 100
ROB['logit_ame_se'] = float(lg.get_margeff().summary_frame().loc['s', 'Std. Err.']) * 100
# permutazione dentro partito×regione×anno
rng = np.random.default_rng(20261126); NP = 300; perm = []
bw = T2['c3']['b'] / 100
Dp = D.copy()
_, Xf = patsy.dmatrices('any ~ C(gy) + C(gr)', D, return_type='dataframe'); Xf = Xf.values; Pf = np.linalg.pinv(Xf.T @ Xf) @ Xf.T
yres = D['any'].values - Xf @ (Pf @ D['any'].values)
grp = D.groupby(['g', 'reg', 'y']).indices
for _ in range(NP):
    sp = D['s'].values.copy()
    for idx in grp.values(): sp[idx] = sp[rng.permutation(idx)]
    sr = sp - Xf @ (Pf @ sp); perm.append((sr @ yres) / (sr @ sr))
ROB['perm_p'] = float(np.mean(np.abs(perm) >= abs(bw))); ROB['nperm'] = NP
S['ROB'] = ROB

# eterogeneità per partito (within regione, pooled years)
HET = {}
for g in PARTIES:
    d = D[D.g == g]
    HET[g] = dict(pooled=co(fit('any ~ s + C(y) + C(reg)', d)), within=co(fit('any ~ s + C(y) + C(gr)', d)), n_any=int(d['any'].sum()))
S['HET'] = HET

# approvazione (livello emendamento)
A = pd.DataFrame([dict(y=r['anno'], ramo=r['ramo'], ap=int(r['es'] == 'Approvato'), mag=int(r['coal'] == 'Maggioranza'), loc=int(r['po'] == 'Locale'),
                       ina=int(r['es'] == 'Inammissibile'), pid=str(r['pid'] or r['p']), g=r['g'], th=(r['th'] or ['Altro'])[0], nf=r['nf'],
                       big=int((r['e3'] or r['e'] or 0) >= 1e8)) for r in R if r['lett'] == 1 and r['anno'] < 2027 and r['coal'] in ('Maggioranza', 'Opposizione')])
A['ry'] = A.ramo + A.y.astype(str)
AP = {}
for k, f in [('a1', 'ap ~ mag + C(ry)'), ('a2', 'ap ~ mag + loc + mag:loc + C(ry)'), ('a3', 'ap ~ mag + loc + mag:loc + np.log1p(nf) + big + C(ry) + C(th)'),
             ('a4', 'ap ~ loc + np.log1p(nf) + big + C(ry) + C(th) + C(pid)')]:
    m = fit(f, A, 'pid')
    AP[k] = {v: dict(b=float(m.params[v]) * 100, se=float(m.bse[v]) * 100) for v in ['mag', 'loc', 'mag:loc', 'np.log1p(nf)', 'big'] if v in m.params}
    AP[k]['n'] = int(m.nobs); AP[k]['g'] = int(A.pid.nunique())
AP['base'] = float(A[(A.mag == 0)].ap.mean()) * 100; AP['basemag'] = float(A[(A.mag == 1)].ap.mean()) * 100
AP['ina_opp'] = float(A[A.mag == 0].ina.mean()) * 100; AP['ina_mag'] = float(A[A.mag == 1].ina.mean()) * 100
S['AP'] = AP

# descrittive per anno/ramo
DESC = []
for y in YEARS:
    for ramo in ['Camera', 'Senato']:
        s = [r for r in R if r['anno'] == y and r['ramo'] == ramo]
        if not s: continue
        DESC.append(dict(y=y, ramo=ramo, lett=s[0]['lett'], n=len(s), ap=sum(r['es'] == 'Approvato' for r in s), ina=sum(r['es'] == 'Inammissibile' for r in s),
                         rit=sum(r['es'] == 'Ritirato' for r in s), loc=sum(r['po'] == 'Locale' for r in s),
                         maj=sum(r['coal'] == 'Maggioranza' for r in s), opp=sum(r['coal'] == 'Opposizione' for r in s)))
S['DESC'] = DESC
S['N'] = len(R); S['NAP'] = sum(r['es'] == 'Approvato' for r in R); S['NINA'] = sum(r['es'] == 'Inammissibile' for r in R); S['NLOC'] = sum(r['po'] == 'Locale' for r in R)
S['NSIGN'] = len(set((r['ramo'], r['pid'] or r['p']) for r in R if r['coal'] != 'Governo / relatori'))
S['pd_share'] = {g: sum(r['g'] == g for r in R) for g in set(r['g'] for r in R)}
json.dump(S, open(P + 'stats.json', 'w'), indent=1, default=float)

# ---------------- figure ----------------
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
# Fig 1: proposte per manovra e ramo, per esito
fig, ax = plt.subplots(figsize=(6.3, 3.0))
lab = []; x = 0; xs = []
cols = {'ap': '#2b7bb9', 'ina': '#b8322a', 'rit': '#d99a1e', 'oth': '#c9ced8'}
for d in DESC:
    oth = d['n'] - d['ap'] - d['ina'] - d['rit']; b0 = 0
    for k, v in [('ap', d['ap']), ('ina', d['ina']), ('rit', d['rit']), ('oth', oth)]:
        ax.bar(x, v, bottom=b0, color=cols[k], width=0.8, edgecolor='white', linewidth=0.4); b0 += v
    ax.text(x, d['n'] + 80, f"{d['n']:,}".replace(',', '.'), ha='center', fontsize=7)
    xs.append(x); lab.append(f"{d['y']}\n{'C' if d['ramo']=='Camera' else 'S'}{'' if d['lett']==1 else '*'}"); x += 1 if d['ramo'] == 'Camera' and d['y'] < 2027 and False else 1
ax.set_xticks(xs); ax.set_xticklabels(lab, fontsize=7.5); ax.set_ylabel('Amendments')
from matplotlib.patches import Patch
ax.legend(handles=[Patch(color=cols['ap'], label='Approved'), Patch(color=cols['ina'], label='Inadmissible'), Patch(color=cols['rit'], label='Withdrawn'), Patch(color=cols['oth'], label='Rejected / lapsed / not voted')],
          fontsize=7, frameon=False, ncol=2, loc='upper left')
fig.tight_layout(); fig.savefig(P + 'fig/fig1_counts.pdf'); plt.close(fig)

# Fig 2: binscatter (FWL su FE partito×anno e regione)
def resid(v, fe):
    m = fit(f'{v} ~ ' + ' + '.join(fe), D); return D[v] - m.fittedvalues + D[v].mean()
rx, ry = resid('share', ['C(gy)', 'C(reg)']), resid('any', ['C(gy)', 'C(reg)'])
rx2, ry2 = resid('share', ['C(gy)', 'C(gr)']), resid('any', ['C(gy)', 'C(gr)'])
fig, axs = plt.subplots(1, 2, figsize=(6.3, 2.7), sharey=True)
for ax, (a, b_, ttl, kk) in zip(axs, [(rx, ry, 'Party×year and region FE', 'c2'), (rx2, ry2, 'Party×year and party×region FE', 'c3')]):
    q = pd.qcut(a, 20, labels=False, duplicates='drop'); g = pd.DataFrame(dict(x=a, y=b_, q=q)).groupby('q').mean()
    ax.scatter(g.x, g.y * 100, s=14, color='#1757ac')
    xx = np.linspace(a.quantile(.02), a.quantile(.98), 10); sl = T2[kk]['b'] / 10
    ax.plot(xx, b_.mean() * 100 + sl * (xx - a.mean()), color='black', lw=1, ls='--')
    ax.set_title(ttl, fontsize=8.5); ax.set_xlabel('Party vote share 2022 (residualised, %)')
axs[0].set_ylabel('Pr(local request), %')
fig.tight_layout(); fig.savefig(P + 'fig/fig2_binscatter.pdf'); plt.close(fig)

# Fig 3: coefficienti per anno
fig, ax = plt.subplots(figsize=(6.3, 2.6))
for k, (key, mk, off) in enumerate([('pooled', 'o', -0.12), ('within', 's', 0.12)]):
    for i, y in enumerate(YEARS):
        c = BY[y][key]; ax.errorbar(i + off, c['b'], yerr=1.96 * c['se'], fmt=mk, color='#1757ac', mfc='#1757ac' if key == 'pooled' else 'white', ms=5, capsize=2, lw=1,
                                    label=('Across Italy (region FE)' if key == 'pooled' else 'Within region (party×region FE)') if i == 0 else None)
ax.axhline(0, color='black', lw=.6); ax.set_xticks(range(5)); ax.set_xticklabels([f'{y} budget' for y in YEARS])
ax.set_ylabel('pp per +10 vote points'); ax.legend(fontsize=7, frameon=False, loc='upper left')
fig.tight_layout(); fig.savefig(P + 'fig/fig3_byyear.pdf'); plt.close(fig)

# Fig 4: mappa (decodifica topojson)
tr = topo.get('transform'); arcs = []
for a in topo['arcs']:
    x = y = 0; pts = []
    for dx, dy in a:
        x += dx; y += dy; pts.append((x * tr['scale'][0] + tr['translate'][0], y * tr['scale'][1] + tr['translate'][1]) if tr else (dx, dy))
    arcs.append(pts)
def ring(ix):
    out = []
    for i in ix:
        seg = arcs[i] if i >= 0 else arcs[~i][::-1]
        out += seg if not out else seg[1:]
    return out
cntp = collections.Counter(); cnta = collections.Counter()
for r in R:
    if r['g'] in ('Governo / relatori',) or not r['pm']: continue
    for p in set(r['pm']):
        cntp[p] += 1; cnta[p] += r['es'] == 'Approvato'
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
fig, axs = plt.subplots(1, 2, figsize=(6.3, 4.1))
ramp = ['#cce3fd', '#9dc8f7', '#6aabf1', '#338ced', '#2370cd', '#1757ac', '#0e3d7e']
for ax, (vals, ttl, th) in zip(axs, [({p: cntp[p] / POP[p] * 1e5 for p in POP}, 'Local requests per 100,000 residents', [1, 1.5, 2, 3, 4, 6]),
                                     ({p: cnta[p] for p in POP}, 'Approved local requests (count)', [2, 3, 4, 6, 9, 13])]):
    patches = []; colors = []
    for g in topo['objects']['provinces']['geometries']:
        p = g['properties']['prov_name']; v = vals.get(p, 0)
        c = '#f1f3f6' if v <= 0 else ramp[sum(v >= t for t in th)]
        polys = g['arcs'] if g['type'] == 'Polygon' else [pp for pp in g['arcs']] if False else g['arcs']
        polys = [g['arcs']] if g['type'] == 'Polygon' else g['arcs']
        for poly in polys:
            patches.append(Polygon(ring(poly[0]), closed=True)); colors.append(c)
    pc = PatchCollection(patches, facecolor=colors, edgecolor='#8b93a5', linewidth=0.15); ax.add_collection(pc)
    ax.autoscale_view(); ax.set_aspect(1.3); ax.axis('off'); ax.set_title(ttl, fontsize=8.5)
    hs = [Patch(facecolor='#f1f3f6', edgecolor='#8b93a5', label='none')] + [Patch(color=ramp[i], label=(f'< {th[0]}' if i == 0 else f'≥ {th[i-1]}')) for i in range(len(th) + 1)]
    ax.legend(handles=hs, fontsize=6, frameon=False, loc='lower left')
fig.tight_layout(); fig.savefig(P + 'fig/fig4_map.pdf'); plt.close(fig)

# Fig 5: tasso di approvazione per schieramento e manovra
fig, ax = plt.subplots(figsize=(6.3, 2.5)); i = 0; labs = []
for y, ramo in [(2023, 'Camera'), (2024, 'Senato'), (2025, 'Camera'), (2026, 'Senato')]:
    s = A[(A.y == y) & (A.ramo == ramo)]
    for k, (m, c) in enumerate([(1, '#2b5d9c'), (0, '#a04a86')]):
        v = s[s.mag == m].ap.mean() * 100; ax.bar(i + (k - .5) * .38, v, width=.36, color=c, label=('Majority' if m else 'Opposition') if i == 0 else None)
        ax.text(i + (k - .5) * .38, v + .6, f'{v:.1f}', ha='center', fontsize=7)
    labs.append(f'{y} ({ramo})'); i += 1
ax.set_xticks(range(4)); ax.set_xticklabels(labs); ax.set_ylabel('% approved'); ax.legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(P + 'fig/fig5_approval.pdf'); plt.close(fig)
print(json.dumps({k: S[k] for k in ['T2', 'ROB', 'AP']}, indent=0, default=float)[:3000])
