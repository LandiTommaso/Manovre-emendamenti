"""Analisi aggiuntive per il working paper v2:
 1. curva delle specificazioni (144 specificazioni)
 2. confronto dentro la provincia (effetti fissi provincia x manovra)
 3. deputati del partito eletti nella provincia (geografia degli eletti vs strategia di partito)
 4. conteggi con PPML
 5. approvazione per fasi (ammissibilita', poi voto)
 6. provincia contesa e manovra pre-elettorale 2027
Output: paper/extra.json, paper/fig/fig6_spec.pdf, fig7_het.pdf, fig8_stages.pdf; aggiorna site*/analisi_multi.json (het, spec)."""
import json, math, collections, itertools, os
import numpy as np, pandas as pd, patsy
import statsmodels.api as sm
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
import warnings; warnings.filterwarnings('ignore')

B = '/home/claude/multi/'; E = '/home/claude/emend/'; P = B + 'paper/'
R = json.load(open(B + 'out/multi_rows.json'))
POP = json.load(open(E + 'site/popolazione.json'))
V = json.load(open(E + 'data/voti2022.json')); K = V['K']; VP = V['prov']
topo = json.load(open(E + 'site/province.topo.json'))
REG = {g['properties']['prov_name']: g['properties']['reg_name'] for g in topo['objects']['provinces']['geometries']}
PARTIES = ['FdI', 'Lega', 'FI', 'Noi Moderati', 'PD', 'M5S', 'AVS', 'Azione / IV']
KMAP = {'FdI': 'FdI', 'Lega': 'Lega', 'FI': 'FI', 'Noi Moderati': 'NM', 'PD': 'PD', 'M5S': 'M5S', 'AVS': 'AVS', 'Azione / IV': 'AzIV'}
YEARS = [2023, 2024, 2025, 2026, 2027]
provs = [p for p in VP if p in POP]
MAJ = {'FdI', 'Lega', 'FI', 'Noi Moderati'}

# --- deputati del partito eletti nei collegi plurinominali che coprono la provincia (Camera, elezioni 2022) ---
PC = json.load(open(E + 'data/prov_collegi2022.json'))['prov']
coll_el = collections.Counter()
for p, d in PC.items():
    for c, n in d.items(): coll_el[c] += n
DGRP = {'FDI': 'FdI', 'LEGA': 'Lega', 'FI-PPE': 'FI', 'NM(N-C-U-I)M-CP': 'Noi Moderati', 'PD-IDP': 'PD', 'M5S': 'M5S', 'AVS': 'AVS', 'AZ-PER-RE': 'Azione / IV', 'IV-CR': 'Azione / IV'}
dep_c = collections.Counter()
for line in open(E + 'data/deputati.txt', encoding='utf-8'):
    f = line.rstrip('\n').split('|')
    if len(f) < 4 or f[2] not in DGRP or not f[3]: continue
    dep_c[(DGRP[f[2]], f[3])] += 1
def mp(p, g):  # deputati "attribuiti" alla provincia: quota di elettori della provincia nel collegio
    return sum(dep_c[(g, c)] * n / coll_el[c] for c, n in PC.get(p, {}).items())

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
                v = VP[p]; sh = v[K.index(KMAP[g])] / v[0] * 100
                cdx = sum(v[K.index(k)] for k in ['FdI', 'Lega', 'FI', 'NM']) / v[0] * 100
                csx = sum(v[K.index(k)] for k in ['PD', 'AVS', 'PiuE']) / v[0] * 100
                top2 = sorted([cdx, csx, v[K.index('M5S')] / v[0] * 100], reverse=True)  # prime due forze
                n = cnt[(p, g, y)]
                rows.append(dict(p=p, reg=REG[p], g=g, y=y, s=sh / 10, share=sh, any=int(n > 0), anyA=int(cntA[(p, g, y)] > 0), n=n,
                                 ihs=math.asinh(n / POP[p] * 1e5), gy=g + str(y), gr=g + REG[p], py=p + str(y), pop=POP[p], lpop=math.log(POP[p]),
                                 mp=mp(p, g), maj=int(g in MAJ), marg=top2[0] - top2[1], metro=int(p in ('Roma', 'Milano', 'Napoli', 'Torino'))))
    return pd.DataFrame(rows)

class F: pass
def fit(f, d, cl='p'):
    y, X = patsy.dmatrices(f, d, return_type='dataframe')
    Xv = X.values; yv = y.values[:, 0]
    XtX = np.linalg.pinv(Xv.T @ Xv); b = XtX @ Xv.T @ yv; e = yv - Xv @ b
    g = pd.factorize(d.loc[X.index, cl])[0]; G = g.max() + 1
    Sm = np.zeros((G, Xv.shape[1])); np.add.at(Sm, g, Xv * e[:, None])
    n = len(yv); k = np.linalg.matrix_rank(Xv)
    Vc = XtX @ (Sm.T @ Sm) @ XtX * (G / (G - 1)) * ((n - 1) / (n - k))
    m = F(); m.params = pd.Series(b, X.columns); m.bse = pd.Series(np.sqrt(np.abs(np.diag(Vc))), X.columns); m.nobs = n; m.G = G
    return m
def co(m, v='s', sc=100): return dict(b=float(m.params[v]) * sc, se=float(m.bse[v]) * sc, n=int(m.nobs), g=int(m.G))

X = {}
D = build_panel()
X['mean_any'] = float(D['any'].mean() * 100)

# 2. dentro la provincia: stessa provincia, stessa manovra, partiti diversi
X['within_prov'] = co(fit('any ~ s + C(gy) + C(py)', D))
X['within_prov_gr'] = co(fit('any ~ s + C(gy) + C(gr) + C(py)', D))

# 3. deputati eletti nella provincia
X['mp_mean'] = float(D.mp.mean()); X['mp_sd'] = float(D.mp.std())
m = fit('any ~ s + mp + C(gy) + C(reg) + lpop', D); X['mp_pooled'] = dict(s=co(m), mp=co(m, 'mp'))
m = fit('any ~ s + mp + C(gy) + C(py)', D); X['mp_prov'] = dict(s=co(m), mp=co(m, 'mp'))
m = fit('any ~ mp + C(gy) + C(py)', D); X['mp_only_prov'] = co(m, 'mp')
m = fit('any ~ s + mp + C(gy) + C(gr)', D); X['mp_within'] = dict(s=co(m), mp=co(m, 'mp'))
X['corr_s_mp'] = float(np.corrcoef(D.s, D.mp)[0, 1])

# 4. PPML sul numero di richieste
def ppml(f, d):
    y, Xm = patsy.dmatrices(f, d, return_type='dataframe')
    r = sm.GLM(y, Xm, family=sm.families.Poisson()).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(d.loc[Xm.index, 'p'])[0]})
    return dict(b=float(r.params['s']), se=float(r.bse['s']), irr=float(math.exp(r.params['s'])))
X['ppml_reg'] = ppml('n ~ s + C(gy) + C(reg) + lpop', D)
Dp = D[(D.groupby('py').n.transform('sum') > 0) & (D.groupby('gy').n.transform('sum') > 0)]
try: X['ppml_prov'] = ppml('n ~ s + C(gy) + C(py)', Dp)
except Exception as e: X['ppml_prov'] = None; print('ppml_prov fallito', e)

# 6. provincia contesa e 2027
D['close'] = (D.marg < D.marg.median()).astype(int); D['y27'] = (D.y == 2027).astype(int)
m = fit('any ~ s + s:close + s:y27 + s:close:y27 + C(gy) + C(gr)', D)
X['close27'] = {k: co(m, k) for k in ['s', 's:close', 's:y27', 's:close:y27']}
# eterogeneità maggioranza/opposizione x anno
m = fit('any ~ s + s:maj + C(gy) + C(gr)', D); X['majhet'] = dict(s=co(m), smaj=co(m, 's:maj'))

# eterogeneità per partito (come nel paper)
HET = {}
for g in PARTIES:
    d = D[D.g == g]; HET[g] = dict(pooled=co(fit('any ~ s + C(y) + C(reg)', d)), within=co(fit('any ~ s + C(y) + C(gr)', d)), n_any=int(d['any'].sum()))
X['het'] = HET

# 1. curva delle specificazioni
PANELS = {}
OUTC = {'Any request': lambda r: True, 'Local only': lambda r: r['po'] == 'Locale', 'Admissible only': lambda r: r['es'] != 'Inammissibile'}
SAMP = {'Both chambers': lambda r: True, 'Chamber only': lambda r: r['ramo'] == 'Camera', 'Senate only': lambda r: r['ramo'] == 'Senato', 'First readings': lambda r: r['lett'] == 1}
YS = {'All budgets': YEARS, 'Excl. 2023': [2024, 2025, 2026, 2027], 'Excl. 2027': [2023, 2024, 2025, 2026]}
FES = {'Region': 'C(gy) + C(reg)', 'Party×region': 'C(gy) + C(gr)', 'Province×year': 'C(gy) + C(py)', 'Party×region + province×year': 'C(gy) + C(gr) + C(py)'}
SPEC = []
for (on, of), (sn, sf) in itertools.product(OUTC.items(), SAMP.items()):
    d0 = build_panel(lambda r, of=of, sf=sf: of(r) and sf(r))
    for (yn, ys), (fn, fe), met in itertools.product(YS.items(), FES.items(), [0, 1]):
        d = d0[d0.y.isin(ys)]
        if met: d = d[d.metro == 0]
        if len(ys) < 5 and sn != 'Both chambers': continue  # tiene la griglia leggibile
        m = fit(f'any ~ s + {fe}', d)
        SPEC.append(dict(out=on, samp=sn, years=yn, fe=fn, metro='Excl. 4 metro' if met else 'All provinces', **co(m)))
print('spec', len(SPEC))
X['spec'] = SPEC
sp = pd.DataFrame(SPEC)
X['spec_sum'] = dict(n=len(sp), pos=int((sp.b > 0).sum()), sig=int((sp.b / sp.se > 1.96).sum()), neg_sig=int((sp.b / sp.se < -1.96).sum()), med=float(sp.b.median()),
                     by_fe={k: float(v) for k, v in sp.groupby('fe').b.median().items()})

# 5. approvazione per fasi
A = pd.DataFrame([dict(y=r['anno'], ramo=r['ramo'], ap=int(r['es'] == 'Approvato'), adm=int(r['es'] != 'Inammissibile'), mag=int(r['coal'] == 'Maggioranza'),
                       loc=int(r['po'] == 'Locale'), pid=str(r['pid'] or r['p']), th=(r['th'] or ['Altro'])[0], nf=r['nf'])
                  for r in R if r['lett'] == 1 and r['anno'] < 2027 and r['coal'] in ('Maggioranza', 'Opposizione')])
A['ry'] = A.ramo + A.y.astype(str)
ST = {}
m = fit('adm ~ mag + loc + C(ry) + C(th)', A, 'pid'); ST['adm'] = dict(mag=co(m, 'mag'), loc=co(m, 'loc'), mean=float(A.adm.mean() * 100))
Aa = A[A.adm == 1]
m = fit('ap ~ mag + loc + C(ry) + C(th)', Aa, 'pid'); ST['ap_given_adm'] = dict(mag=co(m, 'mag'), loc=co(m, 'loc'), mean=float(Aa.ap.mean() * 100))
for c in (0, 1):
    s = A[A.mag == c]; ST['raw_' + ('mag' if c else 'opp')] = dict(adm=float(s.adm.mean() * 100), ap_adm=float(s[s.adm == 1].ap.mean() * 100), ap=float(s.ap.mean() * 100), n=int(len(s)))
X['stages'] = ST
# quota delle approvate locali per partito di maggioranza vs quota dei seggi (Gamson)
apL = collections.Counter(r['g'] for r in R if r['es'] == 'Approvato' and r['po'] == 'Locale' and r['g'] in MAJ)
apA = collections.Counter(r['g'] for r in R if r['es'] == 'Approvato' and r['g'] in MAJ)
seats = {'FdI': 119, 'Lega': 60, 'FI': 52, 'Noi Moderati': 8}  # deputati attuali (dati.camera.it), solo descrittivo
X['gamson'] = {g: dict(ap_local=apL[g], ap_all=apA[g], seats=seats[g]) for g in seats}

json.dump(X, open(P + 'extra.json', 'w'), indent=1, default=float)

# ---- figure ----
plt.rcParams.update({'font.family': 'serif', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False})
s2 = sp.sort_values('b').reset_index(drop=True)
fig, (ax, ax2) = plt.subplots(2, 1, figsize=(6.3, 5.2), gridspec_kw=dict(height_ratios=[1.3, 1.6]), sharex=True)
sig = s2.b / s2.se > 1.96
ax.vlines(s2.index, s2.b - 1.96 * s2.se, s2.b + 1.96 * s2.se, color='#c9ced8', lw=.8)
ax.scatter(s2.index[sig], s2.b[sig], s=7, color='#1757ac', zorder=3, label='Significant at 5%')
ax.scatter(s2.index[~sig], s2.b[~sig], s=7, facecolor='white', edgecolor='#1757ac', zorder=3, label='Not significant')
ax.axhline(0, color='black', lw=.6); ax.set_ylabel('pp per +10 vote points'); ax.legend(frameon=False, fontsize=7, loc='upper left')
rows = []
for dim, vals in [('out', list(OUTC)), ('samp', list(SAMP)), ('years', list(YS)), ('fe', list(FES)), ('metro', ['All provinces', 'Excl. 4 metro'])]:
    rows += [(dim, v) for v in vals]
for j, (dim, v) in enumerate(rows):
    idx = s2.index[s2[dim] == v]; ax2.scatter(idx, [j] * len(idx), s=3, marker='s', color='#2b2f3a')
ax2.set_yticks(range(len(rows))); ax2.set_yticklabels([v for _, v in rows], fontsize=6.5); ax2.invert_yaxis(); ax2.set_xlabel('Specification (sorted by estimate)')
fig.tight_layout(); fig.savefig(P + 'fig/fig6_spec.pdf'); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.3, 2.8))
for i, g in enumerate(PARTIES):
    for k, (key, mk, off) in enumerate([('pooled', 'o', -.13), ('within', 's', .13)]):
        c = HET[g][key]; ax.errorbar(i + off, c['b'], yerr=1.96 * c['se'], fmt=mk, color='#2b5d9c' if g in MAJ else '#a04a86', mfc='white' if key == 'within' else None, ms=4.5, capsize=2, lw=1)
ax.axhline(0, color='black', lw=.6); ax.set_xticks(range(len(PARTIES))); ax.set_xticklabels(PARTIES, fontsize=7.5); ax.set_ylabel('pp per +10 vote points')
ax.text(.01, .97, 'filled: region FE; hollow: party×region FE. Blue: majority; purple: opposition', transform=ax.transAxes, fontsize=7, va='top')
fig.tight_layout(); fig.savefig(P + 'fig/fig7_het.pdf'); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.3, 2.4))
labs = ['Admissible\n(% of tabled)', 'Approved\n(% of admissible)', 'Approved\n(% of tabled)']
for k, (c, col, nm) in enumerate([('mag', '#2b5d9c', 'Majority'), ('opp', '#a04a86', 'Opposition')]):
    v = [ST['raw_' + c]['adm'], ST['raw_' + c]['ap_adm'], ST['raw_' + c]['ap']]
    ax.bar(np.arange(3) + (k - .5) * .36, v, width=.34, color=col, label=nm)
    for i, x in enumerate(v): ax.text(i + (k - .5) * .36, x + 1.5, f'{x:.1f}', ha='center', fontsize=7)
ax.set_xticks(range(3)); ax.set_xticklabels(labs, fontsize=7.5); ax.set_ylabel('%'); ax.legend(frameon=False, fontsize=7)
fig.tight_layout(); fig.savefig(P + 'fig/fig8_stages.pdf'); plt.close(fig)

# ---- sito: eterogeneità e curva delle specificazioni ----
txt_het = ('Il legame è forte per i partiti di opposizione (PD, M5S, AVS) e assente o negativo per FdI, il primo partito di governo, che chiede soldi '
           'soprattutto dove è relativamente più debole. Gli intervalli dei partiti piccoli sono larghi.')
for site in ('site', 'site2'):
    fn = B + site + '/analisi_multi.json'
    if not os.path.exists(fn): continue
    a = json.load(open(fn))
    a['het'] = {g: dict(b=HET[g]['pooled']['b'], se=HET[g]['pooled']['se']) for g in PARTIES}; a['het_txt'] = txt_het
    a['spec'] = [dict(b=s['b'], se=s['se'], lab=f"{s['out']} · {s['samp']} · {s['years']} · FE {s['fe']} · {s['metro']}") for s in SPEC]
    ss = X['spec_sum']
    a['spec_txt'] = (f"Le stime più basse vengono quasi tutte dai modelli che confrontano solo province della stessa regione o partiti diversi nella stessa provincia: "
                     f"lì il legame si riduce. Mediane per tipo di confronto: " + '; '.join(f"{k} {v:.1f}" for k, v in ss['by_fe'].items()).replace('.', ',') + '.')
    json.dump(a, open(fn, 'w'), ensure_ascii=False, separators=(',', ':'))
print(json.dumps({k: X[k] for k in ['within_prov', 'within_prov_gr', 'mp_pooled', 'mp_prov', 'mp_within', 'mp_only_prov', 'corr_s_mp', 'ppml_reg', 'ppml_prov', 'close27', 'majhet', 'spec_sum', 'stages']}, indent=0, default=float))
