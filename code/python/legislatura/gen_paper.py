import json
S = json.load(open('/home/claude/multi/paper/stats.json'))
T2, ROB, AP, BY, HET = S['T2'], S['ROB'], S['AP'], S['BY'], S['HET']
X = json.load(open('/home/claude/multi/paper/extra.json'))
SS = X['spec_sum']; STG = X['stages']; WP = X['within_prov']; MPp, MPv, MPw = X['mp_pooled'], X['mp_prov'], X['mp_within']; C27 = X['close27']
def n(x): return f"{x:,.0f}"
def c(d, k=2): return f"{d['b']:.{k}f}"
def se(d, k=2): return f"({d['se']:.{k}f})"
def st(d):
    z = abs(d['b'] / d['se']) if d['se'] else 0
    return '^{***}' if z > 3.29 else '^{**}' if z > 2.58 else '^{*}' if z > 1.96 else ''
def cell(d, k=2): return f"${c(d,k)}{st(d)}$"
D = {(x['y'], x['ramo']): x for x in S['DESC']}
ap_tot, ina_tot = S['NAP'], S['NINA']

desc_rows = []
for x in S['DESC']:
    desc_rows.append(f"{x['y']} & {x['ramo']} & {'First' if x['lett']==1 else 'Second'} & {n(x['n'])} & {n(x['maj'])} & {n(x['opp'])} & {n(x['ina'])} & {n(x['ap'])} & {n(x['loc'])} \\\\")
desc_rows = '\n'.join(desc_rows)
tot = dict(n=sum(x['n'] for x in S['DESC']), maj=sum(x['maj'] for x in S['DESC']), opp=sum(x['opp'] for x in S['DESC']), ina=ina_tot, ap=ap_tot, loc=S['NLOC'])

het_rows = '\n'.join(f"{g.replace('Azione / IV','Azione/IV')} & {'Majority' if g in ('FdI','Lega','FI','Noi Moderati') else 'Opposition'} & {cell(v['pooled'])} & {se(v['pooled'])} & {v['n_any']} \\\\" for g, v in HET.items())

rob = [('Baseline (Table 2, cols. 2--3)', dict(pooled=T2['c2'], within=T2['c3'])), ('Chamber of Deputies only', ROB['camera']), ('Senate only', ROB['senato']),
       ('First readings only', ROB['first']), ('Excluding 2023 (partial data)', ROB['no2023']), ('Excluding 2027 (not yet voted)', ROB['no2027']),
       ('Excluding Rome, Milan, Naples, Turin', ROB['nometro'])]
rob_rows = '\n'.join(f"{a} & {cell(b['pooled'])} & {se(b['pooled'])} & {cell(b['within'])} & {se(b['within'])} \\\\" for a, b in rob)

by_rows = '\n'.join(f"{y} & {cell(BY[str(y)]['pooled'])} & {se(BY[str(y)]['pooled'])} & {cell(BY[str(y)]['within'])} & {se(BY[str(y)]['within'])} & {BY[str(y)]['mean']:.1f} \\\\" for y in [2023, 2024, 2025, 2026, 2027])

a1, a2, a3, a4 = AP['a1'], AP['a2'], AP['a3'], AP['a4']
def apc(m, v): return cell(m[v]) if v in m else ''
def aps(m, v): return se(m[v]) if v in m else ''

tex = r"""\documentclass[12pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{setspace}
\usepackage{amsmath}
\usepackage{booktabs}
\usepackage{threeparttable}
\usepackage{graphicx}
\usepackage[font=small,labelfont=bf]{caption}
\usepackage[authoryear,round]{natbib}
\usepackage{xcolor}
\usepackage[colorlinks=true,linkcolor=black,citecolor=blue!50!black,urlcolor=blue!50!black]{hyperref}
\usepackage{float}
\usepackage{placeins}
\usepackage{needspace}
\usepackage{etoolbox}
\pretocmd{\section}{\FloatBarrier\Needspace{12\baselineskip}}{}{}
\pretocmd{\subsection}{\Needspace{7\baselineskip}}{}{}

\setlength{\bibsep}{3pt}
\begin{document}
\begin{titlepage}
\centering
\vspace*{0.2cm}
{\large WORKING PAPER}\\[1.2cm]
{\Large \textbf{WHERE THE VOTES ARE:\\[4pt] ELECTORAL STRENGTH AND LOCAL SPENDING REQUESTS\\[4pt] IN ITALIAN BUDGET LAWS, 2023--2027}}\\[1.4cm]
{\large Tommaso Landi}\\[4pt]
Sant'Anna School of Advanced Studies and University of Pisa\\[1.2cm]
This version: 26 November 2026 (version 2)\\[0.4cm]
Preliminary draft. Please do not circulate without the author's permission.\\[1.0cm]
\begin{minipage}{0.9\textwidth}\footnotesize\singlespacing
\noindent The research question, the dataset design and the empirical strategy are my own. I thank Riccardo Trezzi (\href{https://underlyinginflation.com}{UnderlyingInflation.com}) for the inspiration behind this project. \textbf{Use of AI.} This paper was produced with the fundamental help of Claude, an AI model developed by Anthropic, which wrote most of the code that downloads and parses the parliamentary files, implemented the estimators, ran the specification searches and drafted much of the text under my direction. I defined the questions, chose the specifications to report, checked the data against the official sources and am responsible for every claim and every error. I disclose this in full because readers should be able to judge the work knowing how it was made. The complete data and replication code will be made public so that every number can be reproduced without trusting either of us. Comments are welcome at \href{mailto:tomsciu@gmail.com}{tomsciu@gmail.com}. This is a preliminary draft and has not been peer reviewed.\\[6pt]
\textbf{Suggested citation:} Landi, T. (2026). Where the Votes Are: Electoral Strength and Local Spending Requests in Italian Budget Laws, 2023--2027. Working paper, v2, 26 November 2026.\\[4pt]
\copyright{} 2026 Tommaso Landi. All rights reserved. No part of this draft, its data or its code may be reproduced or redistributed without the author's written permission.
\end{minipage}
\end{titlepage}

\begin{center}
\textbf{Abstract}
\end{center}
\begin{quote}\small
I assemble every amendment tabled in the budget committees of both chambers of the Italian Parliament to the five budget laws of the XIX legislature (2023--2027): """ + n(S['N']) + r""" proposals with their first signatory, the signatory's group on the day the bill was examined, the official admissibility ruling and the final outcome. I read each text to identify requests of money for a specific municipality or province and match them to party vote shares in the 2022 general election. Ten extra points of vote share raise the probability that a party tables a local request for a province by """ + f"{T2['c2']['b']:.1f}" + r""" percentage points (mean """ + f"{T2['c2']['mean']:.1f}" + r"""). The gradient survives comparing parties within the same province and budget, which absorbs local need, and """ + f"{SS['sig']}" + r""" of """ + f"{SS['n']}" + r""" alternative specifications are positive and significant. Within regions, it runs largely through the geography of elected deputies rather than through party-level targeting. It is driven by opposition parties, while the main governing party targets provinces where it is relatively weaker. Outcomes depend on who asks. Majority proposals are more often ruled inadmissible, but once admitted they are approved """ + f"{STG['raw_mag']['ap_adm']:.0f}" + r"""\% of the time against """ + f"{STG['raw_opp']['ap_adm']:.0f}" + r"""\% for the opposition.
\end{quote}
\vspace{4pt}
\noindent\textbf{JEL:} D72, H61, H77, R50.\quad \textbf{Keywords:} distributive politics, pork barrel, budget amendments, Italian Parliament, legislative behaviour.

\newpage
\onehalfspacing

\section{Introduction}

Every autumn the Italian government sends Parliament a budget law, and every autumn members of Parliament answer with thousands of amendments. Many are general. They change a tax rate, extend a benefit, refinance a national fund. A visible minority asks for money for a single place, such as a bypass in a provincial town, a theatre, a hospital wing or a school gym. Newspapers call them \emph{marchette} or \emph{mance}, and political economists call them pork. They are seldom approved, yet they are tabled in large numbers, carefully signed and often publicised in local media.

This paper asks where these requests go. Classic theories of distributive politics give competing predictions. If parties reward their core supporters, requests should cluster where a party is electorally strong \citep{cox1986}. If they court swing voters, requests should go where elections are close \citep{lindbeck1987,dixit1996}. If what matters is the personal vote of individual legislators, requests should follow the geography of who was elected \citep{golden2008,carozzi2016}. Most of the evidence on these questions uses realised transfers. Realised transfers mix the demands of legislators with the choices of the government, the bureaucracy and the budget constraint. Amendments are cleaner. They record what each legislator \emph{asked for}, in writing and with a date, before anyone decided what to grant.

I build a new dataset of all amendments tabled in the budget committees of the Chamber of Deputies and of the Senate to the five budget laws of the current legislature, from the 2023 budget (December 2022) to the 2027 budget (November 2026). The data cover nine bill readings and """ + n(S['N']) + r""" proposals signed by """ + n(S['NSIGN']) + r""" distinct first signatories. For each proposal I record the first signatory and his or her group at the date of examination, the official admissibility ruling, and the outcome (approved, withdrawn, rejected or never voted). I then read the text to identify requests addressed to a specific municipality or province and the sums involved, and match each party--province pair to the party's vote share in the 2022 general election.

The paper documents five results. First, there is a robust positive association between a party's 2022 vote share in a province and the probability that the party tables a local request for that province. With party-by-budget and region fixed effects, ten additional points of vote share are associated with a """ + f"{T2['c2']['b']:.1f}" + r""" percentage-point increase in that probability, from a mean of """ + f"{T2['c2']['mean']:.1f}" + r"""\% (Table~\ref{tab:main}). The association is not explained by local need. Comparing different parties in the \emph{same province and budget}, which absorbs every province-level shock, the estimate is @@wp_b@@ points (s.e.\ @@wp_se@@). Across @@sp_n@@ specifications that vary the outcome, the sample, the fixed effects and the treatment of large cities, all @@sp_pos@@ estimates are positive and @@sp_sig@@ are significant at 5\% (Figure~\ref{fig:spec}).

Second, within regions the gradient runs largely through the geography of who was elected. I attribute each party's deputies to provinces through the 2022 list constituencies. Once the number of a party's deputies elected in a province is controlled for, the within-region vote-share coefficient falls from """ + f"{T2['c3']['b']:.1f}" + r""" to @@mpw_s@@ points and loses significance, while each additional deputy raises the probability of a request by @@mpw_mp@@ points (Table~\ref{tab:mp}). Across Italy, both matter. This is the pattern predicted by a common-pool view in which individual legislators claim resources for their own constituency \citep{weingast1981,perssontabellini1999}, rather than by a centralised party strategy.

Third, the association is driven by the opposition. Opposition parties (PD, M5S, AVS) ask for money where they are strong, whereas Fratelli d'Italia, the senior governing party, tables more local requests where it is relatively weaker (Table~\ref{tab:het}, Figure~\ref{fig:het}). Fourth, the gradient is steeper in provinces where the 2022 contest between the two strongest forces was close, while the interaction with the 2027 budget, the last before the next general election, is imprecisely estimated.

Fifth, what passes depends on who asks. A proposal by a majority legislator is """ + f"{a1['mag']['b']:.1f}" + r""" points more likely to be approved than one by the opposition, whose base approval rate is """ + f"{AP['base']:.1f}" + r"""\% (Table~\ref{tab:approval}). Decomposing the process by stage shows that the premium is created at the vote, not at the admissibility filter. Majority proposals are \emph{less} often ruled admissible (@@st_adm_m@@\% against @@st_adm_o@@\%), but once admitted @@st_apa_m@@\% of them pass against @@st_apa_o@@\% of opposition proposals (Figure~\ref{fig:stages}).

These results speak to three literatures. The first studies the electoral targeting of public spending \citep{cox1986,dixit1996,levitt1997,ansolabehere2006,berry2010}. I add evidence on the \emph{demand} side, at the level of individual proposals, and show that core-voter and swing-voter logics can coexist inside the same Parliament depending on whether a party governs. Because the unit of analysis is the request rather than the transfer, I can separate what legislators ask for from what the government grants, and compare parties inside the same province, which the literature on realised transfers usually cannot do. The second studies Italian distributive politics \citep{golden2008,carozzi2016,bracco2015,brollo2012}, which has focused on transfers to municipalities. I move the lens to the parliamentary stage of the budget. The third concerns legislative behaviour and position-taking \citep{mayhew1974}. The low approval rates suggest that many local amendments are signals to constituents rather than serious attempts to obtain funds, which is consistent with the electoral-connection view. The finding that the within-region gradient runs through elected legislators connects the evidence to the common-pool problem in budgeting \citep{weingast1981,perssontabellini1999} and to the role of individual legislators' constituencies in Italy \citep{carozzi2016}.

The data and an interactive version of every figure are public (Section~\ref{sec:avail}). Section~\ref{sec:background} describes the budget process. Section~\ref{sec:data} introduces the data, Section~\ref{sec:strategy} the empirical strategy, Section~\ref{sec:results} the results and Section~\ref{sec:robust} robustness checks, including a specification curve. Section~\ref{sec:concl} discusses the evidence, including the frequent claim that local spending pays for itself through multiplier effects, and concludes.

\section{Institutional background}\label{sec:background}

The Italian budget law is examined by both chambers under a compressed calendar between late October and the end of December. In recent years the two chambers have alternated in the role of first reader. The Chamber of Deputies examined the 2023, 2025 and 2027 budgets first, the Senate the 2024 and 2026 budgets. In practice, the substantive changes to the government's bill happen in the budget committee of the first chamber (the V Commission at the Chamber, the 5th Commission at the Senate). The second chamber receives a text that the majority treats as closed. Amendments are tabled and sometimes voted, but none is approved, because any change would require a third reading before the 31 December deadline.

Any member can table amendments. The committee chair then rules on admissibility. The two main grounds are lack of adequate financial coverage, under the constitutional requirement that new spending be funded, and extraneity of subject matter, because the budget law may only contain provisions with a direct financial effect. Since the number of proposals far exceeds the time available, groups are asked to flag a subset of \emph{segnalati} amendments on which votes are actually taken. Government and rapporteurs table their own amendments, often late in the process and often as reformulations of proposals by majority members. Reformulated texts (\emph{nuova formulazione}, \emph{testo 2}) are what is eventually approved.

Two examples from the data illustrate the range of requests. In the 2027 budget, near-identical amendments signed by members of Forza Italia, the Lega, the PD and Azione/Italia Viva (C.~3174-\emph{bis}, 8.09--8.014) proposed a tax credit for bars and restaurants serving draft beer, five million euro a year, which the press described as a beer bonus.\footnote{L.~Graziani, \emph{Open}, 19 November 2026, \url{https://www.open.online/2026/11/19/manovra-tasso-alcolico-spunta-bonus-forza-italia-birra-spina/}.} An amendment on the excise duty on beer had been approved in the 2025 budget (C.~2112-\emph{bis}, 8.066). In the same 2027 file, two amendments by a PD deputy elected in the list constituency that includes the province of Pistoia asked for 50 and 15 million euro over three years for the roads around Collodi and for the ``places of Pinocchio'' in Pescia (89.010 and 89.011). Both were ruled inadmissible as extraneous to the subject of the budget law. The first is a sectoral request replicated across parties, the second a textbook local request by a legislator for his own area. This paper is about the second kind.

Two features of this setting matter for what follows. First, tabling is cheap and observable. A legislator can show a local newspaper that he or she ``asked for'' a road or a grant, whatever the outcome. Second, approval is controlled by the government and the majority leadership, so the mapping from requests to outcomes is informative about the bargaining power of different legislators.

\section{Data}\label{sec:data}

\subsection{Sources}

For the Chamber of Deputies I use the official lists of amendments tabled in the V Commission for each budget bill (C.~643-\emph{bis}, C.~1627, C.~2112-\emph{bis}, C.~2750 and C.~3174-\emph{bis}), which report number, article, first signatory with a unique person identifier, and outcome. Texts come from the full amendment files published in the Commission bulletin when available (2024, 2025 and 2027) and otherwise from the individual amendment pages (2023 and 2026). For approved amendments in 2025 I use the text of the approved reformulation. For the Senate I use the full commission files of S.~442, S.~926, S.~1330 and S.~1689, which list for each proposal the signatories with their Senate identifier, the outcome and the text. Group affiliations, with start and end dates, come from the open-data services of the two chambers (\url{dati.camera.it}, \url{dati.senato.it}). Vote shares are list votes for the Chamber in the 25 September 2022 election (Ministry of the Interior, Eligendo), aggregated from municipalities to provinces. Population is ISTAT resident population on 1 January 2025.

\subsection{Construction}

The unit of observation is a proposal, identified by its number within a bill reading. Reformulations are merged into the original proposal, which is coded as approved if any of its formulations was approved. At the Senate, \emph{Accolto} is coded as approved. Ordini del giorno (non-binding resolutions) are excluded. The party of a proposal is the group of its first signatory on the date the bill was examined. Azione and Italia Viva, which ran on a joint list in 2022, are merged. Senate members of the AVS and Azione components of the Mixed group are assigned to those parties by name. Proposals by the government and rapporteurs are kept as a separate category. Sub-amendments, which amend other proposals (mostly those of the government and rapporteurs), are kept as proposals. There are 1,106 of them (398 in the 2023 Chamber file, 252 in the 2024 Senate, 221 in the 2025 Chamber and 235 in the 2026 Senate). Press and parliamentary counts usually exclude them. Without them, my counts are close to those reported at the time, with 5,748 proposals against 5,742 announced for the 2026 budget in the Senate committee, and 4,543 against about 4,500--4,560 reported for the 2025 budget in the Chamber.\footnote{2026 Senate: \emph{AGI} and \emph{Avvenire}, 14 November 2025 (5,742). 2025 Chamber: \emph{AGI}, 11 November 2024 (4,562), and \emph{Pagella Politica}, 20 November 2024 (4,511). For the 2027 budget, \emph{LaPresse} reported 6,559 proposals on 23 November 2026, against 6,558 in the file used here.}

A proposal is \emph{local} if its operative text, excluding the financial-coverage clause, names one or a few municipalities or provinces. I match names against the ISTAT list of municipalities, require an explicit context (``comune di'', ``città di'', ``provincia di'') for small or ambiguous names, and exclude national funds, street names and large infrastructure such as the Strait of Messina bridge. A proposal naming six or more places in at least three regions is classified as multi-territorial rather than local. Sums are read from the text over the three years of each budget. Because automatic reading of sums is error-prone, the main analysis uses counts rather than euros.

\subsection{Descriptive statistics}

Table~\ref{tab:desc} and Figure~\ref{fig:counts} summarise the data. The legislature produced """ + n(S['N']) + r""" proposals, of which """ + n(ina_tot) + r""" (""" + f"{100*ina_tot/S['N']:.1f}" + r"""\%) were ruled inadmissible and """ + n(ap_tot) + r""" (""" + f"{100*ap_tot/S['N']:.1f}" + r"""\%) were approved. In all, """ + n(S['NLOC']) + r""" proposals are local. Approvals occur only in first readings. Two data limitations deserve emphasis. For the 2023 budget the Chamber published the text only of proposals flagged by groups (""" + n(D[(2023,'Camera')]['n']) + r""" of about 3,000 tabled), so the 2023 Chamber figures are a selected sample. The 2027 budget had not yet been voted in committee at the time of writing, so its proposals have no outcome other than admissibility.

\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\begin{threeparttable}
\caption{Amendments to the budget laws of the XIX legislature}\label{tab:desc}
\begin{tabular}{llrrrrrrr}
\toprule
Budget & Chamber & Reading & Tabled & Majority & Opposition & Inadmissible & Approved & Local \\
\midrule
""" + desc_rows + r"""
\midrule
Total & & & """ + f"{n(tot['n'])} & {n(tot['maj'])} & {n(tot['opp'])} & {n(tot['ina'])} & {n(tot['ap'])} & {n(tot['loc'])}" + r""" \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} One observation per proposal in the budget committee of each chamber. Majority: FdI, Lega, FI, Noi Moderati. Opposition: PD, M5S, AVS, Azione/IV. Remaining proposals are by the government and rapporteurs, the Mixed group or the Autonomie group (Senate). Local: proposals naming one or a few specific municipalities or provinces. The 2023 Chamber figures cover flagged proposals only.
\end{tablenotes}
\end{threeparttable}
\end{table}

\begin{figure}[htbp]\centering
\includegraphics[width=\textwidth]{fig/fig1_counts.pdf}
\caption{Proposals by budget, chamber and outcome}\label{fig:counts}
\begin{minipage}{0.95\textwidth}\footnotesize \emph{Notes:} C = Chamber of Deputies, S = Senate; * second reading. The 2027 budget had not been voted in committee at the time of writing.\end{minipage}
\end{figure}

\section{Empirical strategy}\label{sec:strategy}

I build a balanced panel of """ + str(S['nprov']) + r""" provinces (Valle d'Aosta, which has no list vote, is excluded) $\times$ 8 parties $\times$ 5 budgets, for """ + n(S['nobs']) + r""" observations. The outcome $Y_{ipt}$ equals one if party $p$ tabled at least one local proposal naming province $i$ in budget $t$, in either chamber. I estimate linear probability models of the form
\begin{equation}
Y_{ipt} = \beta\, \text{Votes}_{ip} + \alpha_{pt} + \delta_{r(i)} + \varepsilon_{ipt},
\end{equation}
where $\text{Votes}_{ip}$ is the 2022 list vote share of party $p$ in province $i$, in units of ten percentage points, $\alpha_{pt}$ are party-by-budget fixed effects and $\delta_{r(i)}$ region fixed effects. Party-by-budget effects absorb differences in how many amendments each party tables each year, and region effects absorb the North--South gradient in both votes and requests. In the most demanding specification I replace $\delta_{r(i)}$ with party-by-region effects $\delta_{pr(i)}$. This compares, for the same party, provinces of the same region where the party did better or worse in 2022. Standard errors are clustered by province \citep{cameron2015}. All coefficients are multiplied by 100 and read as percentage points.

I add two designs. The first replaces region effects with province-by-budget effects $\mu_{it}$, so that $\beta$ is identified only by comparing \emph{different parties in the same province and budget}. If party A received more votes than party B in province $i$, is A more likely than B to ask for money for $i$? Province-by-budget effects absorb every characteristic of the province that is common to all parties, including local needs, size, the presence of a crisis and the amount of money on offer. The second adds $\text{MP}_{ip}$, the number of party $p$'s deputies elected in province $i$. Deputies elected on lists are attached to multi-province constituencies, so I attribute each of them to the provinces of the constituency in proportion to the provinces' registered voters. Group membership is taken from the current composition of the Chamber.\footnote{The attribution uses the 2022 constituency of each deputy listed by the Chamber in November 2026 and Ministry of the Interior data on registered voters by province and constituency. Deputies elected in single-member districts are attributed through their list constituency as well. Senators are not included, and changes of group during the legislature are not tracked in this variable.} The variable has mean @@mpmean@@ and standard deviation @@mpsd@@, and its correlation with vote share is @@corr@@. Because the number of deputies is itself an outcome of votes, the comparison is a decomposition (does the vote gradient run through elected legislators?) rather than a causal estimate.

The estimates are descriptive. Vote shares are not randomly assigned. Places where a party is strong may also have the local needs, such as industrial crises or infrastructure gaps, that its legislators choose to champion. The within-region design removes broad territorial differences but not province-specific shocks correlated with past votes. I therefore interpret $\beta$ as a description of where requests go, not as the causal effect of votes on requests.

\section{Results}\label{sec:results}

\subsection{Electoral strength and local requests}

Table~\ref{tab:main} reports the main estimates. Without geographic controls (column~1) ten points of vote share are associated with an increase of """ + f"{T2['c1']['b']:.1f}" + r""" points in the probability of a local request. Adding region fixed effects leaves the estimate essentially unchanged (column~2). With party-by-region effects the coefficient falls to """ + f"{T2['c3']['b']:.1f}" + r""" but remains precisely estimated (column~3). Most of the association is between regions, but a meaningful part is within them. Columns 4--5 use the inverse hyperbolic sine of local requests per 100,000 residents and confirm the sign \citep{bellemare2020}. Figure~\ref{fig:bin} shows the corresponding binned scatter plots.

Columns 6--7 turn to approved local requests in the four budgets that have been voted. Approved requests are also more frequent where parties are strong across Italy (""" + f"{T2['c6']['b']:.2f}" + r""" points, against a mean of """ + f"{T2['c6']['mean']:.1f}" + r"""\%), but the within-region coefficient is """ + f"{T2['c7']['b']:.2f}" + r""" with a standard error of """ + f"{T2['c7']['se']:.2f}" + r""". Legislators ask for money for their strongholds, but the budget does not obviously deliver it.

\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\begin{threeparttable}
\caption{Electoral strength and local spending requests}\label{tab:main}
\begin{tabular}{lccccccc}
\toprule
 & (1) & (2) & (3) & (4) & (5) & (6) & (7) \\
Dependent variable & \multicolumn{3}{c}{Local request (0/1)} & \multicolumn{2}{c}{asinh(requests per 100k)} & \multicolumn{2}{c}{Approved request (0/1)} \\
\cmidrule(lr){2-4}\cmidrule(lr){5-6}\cmidrule(lr){7-8}
Vote share 2022 (10 pp) & """ + ' & '.join(cell(T2[k], 3 if k in ('c4','c5') else 2) for k in ['c1','c2','c3','c4','c5','c6','c7']) + r""" \\
 & """ + ' & '.join(se(T2[k], 3 if k in ('c4','c5') else 2) for k in ['c1','c2','c3','c4','c5','c6','c7']) + r""" \\[3pt]
Party $\times$ budget FE & Yes & Yes & Yes & Yes & Yes & Yes & Yes \\
Region FE & No & Yes & -- & Yes & -- & Yes & -- \\
Party $\times$ region FE & No & No & Yes & No & Yes & No & Yes \\
Budgets & 2023--27 & 2023--27 & 2023--27 & 2023--27 & 2023--27 & 2023--26 & 2023--26 \\
Mean of dep. var. & """ + ' & '.join(f"{T2[k]['mean']:.2f}" for k in ['c1','c2','c3','c4','c5','c6','c7']) + r""" \\
Observations & """ + ' & '.join(n(T2[k]['n']) for k in ['c1','c2','c3','c4','c5','c6','c7']) + r""" \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} OLS. Unit: province $\times$ party $\times$ budget. Coefficients in columns 1--3 and 6--7 are in percentage points; means in percent. Standard errors clustered by province (""" + str(S['nprov']) + r""" clusters) in parentheses. $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.
\end{tablenotes}
\end{threeparttable}
\end{table}

\begin{figure}[htbp]\centering
\includegraphics[width=\textwidth]{fig/fig2_binscatter.pdf}
\caption{Vote share in 2022 and the probability of a local request}\label{fig:bin}
\begin{minipage}{0.95\textwidth}\footnotesize \emph{Notes:} Twenty equal-sized bins of residualised vote share; dashed line: OLS slope from Table~\ref{tab:main}, columns 2 and 3.\end{minipage}
\end{figure}

\subsection{Comparing parties within the same province}

Table~\ref{tab:mp} reports the two additional designs. Column~1 replaces region effects with province-by-budget effects, so that only differences between parties within the same province and budget identify the coefficient. The estimate, @@wp_b@@ points (s.e.\ @@wp_se@@), is as large as the one with region effects. Whatever makes a province attract requests in a given year, from an industrial crisis to a flood, the party that is stronger there asks for money for it more often than the party that is weaker. Adding party-by-region effects as well (column~2) gives @@wpg_b@@ points (s.e.\ @@wpg_se@@), close to the within-region estimate of Table~\ref{tab:main}.

\subsection{Party strategy or legislator geography?}

A party that wins more votes in a province also elects more deputies from there, and those deputies may simply ask for money for home. Columns 3--6 of Table~\ref{tab:mp} add the number of the party's deputies attributed to the province. Across Italy (column~3, with region effects and log population) both variables matter. The vote-share coefficient falls only from """ + f"{T2['c2']['b']:.1f}" + r""" to @@mpp_s@@, and each deputy adds @@mpp_mp@@ points. Within provinces (column~4) the picture is similar. Within regions (column~5) the deputy variable absorbs most of the gradient. The vote-share coefficient falls to @@mpw_s@@ (s.e.\ @@mpw_sse@@) and each deputy adds @@mpw_mp@@ points (s.e.\ @@mpw_mpse@@). Comparing provinces of the same region, a party asks for money where it has elected legislators, not where it is stronger as such.

This is consistent with the ``law of $1/n$'' of \citet{weingast1981}, in which each legislator internalises the benefit of spending in his or her constituency but only a small share of its cost. It is also consistent with the home bias documented for Italian transfers by \citet{carozzi2016}. The decomposition is not causal, because the number of deputies is itself a function of votes and of candidate selection.

\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\begin{threeparttable}
\caption{Within-province comparisons and the geography of elected deputies}\label{tab:mp}
\begin{tabular}{lcccccc}
\toprule
 & (1) & (2) & (3) & (4) & (5) & (6) \\
\midrule
Vote share 2022 (10 pp) & """ + cell(WP) + " & " + cell(X['within_prov_gr']) + " & " + cell(MPp['s']) + " & " + cell(MPv['s']) + " & " + cell(MPw['s']) + r""" & \\
 & """ + se(WP) + " & " + se(X['within_prov_gr']) + " & " + se(MPp['s']) + " & " + se(MPv['s']) + " & " + se(MPw['s']) + r""" & \\
Deputies of the party elected in the province & & & """ + cell(MPp['mp']) + " & " + cell(MPv['mp']) + " & " + cell(MPw['mp']) + " & " + cell(X['mp_only_prov']) + r""" \\
 & & & """ + se(MPp['mp']) + " & " + se(MPv['mp']) + " & " + se(MPw['mp']) + " & " + se(X['mp_only_prov']) + r""" \\[3pt]
Party $\times$ budget FE & Yes & Yes & Yes & Yes & Yes & Yes \\
Province $\times$ budget FE & Yes & Yes & No & Yes & No & Yes \\
Region FE, log population & No & No & Yes & -- & No & -- \\
Party $\times$ region FE & No & Yes & No & No & Yes & No \\
Observations & """ + ' & '.join(n(S['nobs']) for _ in range(6)) + r""" \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} OLS; dependent variable: local request (0/1), mean """ + f"{T2['c2']['mean']:.1f}" + r"""\%. Coefficients in percentage points. Deputies: number of the party's current deputies elected in the list constituencies that include the province, weighted by the province's share of the constituency's registered voters (mean @@mpmean@@, s.d.\ @@mpsd@@). Standard errors clustered by province in parentheses. $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.
\end{tablenotes}
\end{threeparttable}
\end{table}

\subsection{Budget by budget}

Figure~\ref{fig:byyear} and Table~\ref{tab:byyear} estimate the model separately for each budget. The cross-Italy coefficient is positive and significant every year. The within-region coefficient is positive in the first four budgets, between """ + f"{min(BY[str(y)]['within']['b'] for y in [2023,2024,2025,2026]):.1f}" + r""" and """ + f"{max(BY[str(y)]['within']['b'] for y in [2023,2024,2025,2026]):.1f}" + r""" points, though imprecise in single years. In the 2027 budget it is """ + f"{BY['2027']['within']['b']:.1f}" + r""" (s.e. """ + f"{BY['2027']['within']['se']:.1f}" + r"""). Excluding 2027, the pooled within-region estimate rises to """ + f"{ROB['no2027']['within']['b']:.1f}" + r""" (Table~\ref{tab:robust}). Whether 2027 marks a change, for instance as legislators approach the end of the legislature, or is noise, will become clearer with the Senate stage of that budget.

\begin{figure}[htbp]\centering
\includegraphics[width=\textwidth]{fig/fig3_byyear.pdf}
\caption{The vote--request gradient, budget by budget}\label{fig:byyear}
\begin{minipage}{0.95\textwidth}\footnotesize \emph{Notes:} Coefficients on 2022 vote share (10 pp) from separate regressions for each budget, with 95\% confidence intervals. Filled: party and region FE. Hollow: party $\times$ region FE.\end{minipage}
\end{figure}

\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\begin{threeparttable}
\caption{Estimates by budget}\label{tab:byyear}
\begin{tabular}{lccccc}
\toprule
Budget & \multicolumn{2}{c}{Party and region FE} & \multicolumn{2}{c}{Party $\times$ region FE} & Mean (\%) \\
\midrule
""" + by_rows + r"""
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Each row is a separate regression on 872 province--party observations; coefficients in percentage points, clustered standard errors in parentheses.
\end{tablenotes}
\end{threeparttable}
\end{table}

\subsection{Who targets strongholds?}

Table~\ref{tab:het} estimates the gradient separately for each party with region and budget fixed effects. The pooled result hides a sharp contrast. The three main opposition parties ask for money where they are strong, with """ + f"{HET['PD']['pooled']['b']:.1f}" + r""" points for the PD, """ + f"{HET['M5S']['pooled']['b']:.1f}" + r""" for the M5S and """ + f"{HET['AVS']['pooled']['b']:.1f}" + r""" for AVS, whose smaller vote shares mechanically produce larger coefficients. Fratelli d'Italia shows the opposite sign (""" + f"{HET['FdI']['pooled']['b']:.1f}" + r""", s.e. """ + f"{HET['FdI']['pooled']['se']:.1f}" + r"""). Within a region, its legislators table more local requests where the party did relatively worse in 2022. The estimates for the Lega and Forza Italia are negative but imprecise.

One interpretation is that governing and opposition parties use local amendments differently. For the opposition, an amendment is mainly a signal to its own voters, which is cheap and has a low chance of approval. For the senior governing party, whose requests have a real chance of passing, the amendment is an instrument to expand support where it is weaker, closer to the swing-voter logic of \citet{lindbeck1987} and \citet{dixit1996}. The evidence is suggestive, since it rests on one large governing party and on cross-sectional variation in vote shares.

\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\begin{threeparttable}
\caption{Heterogeneity by party}\label{tab:het}
\begin{tabular}{llccc}
\toprule
Party & Camp & Vote share (10 pp) & s.e. & Pairs with a request \\
\midrule
""" + het_rows + r"""
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Separate regressions for each party on 545 province--budget observations, with budget and region FE. Standard errors clustered by province.
\end{tablenotes}
\end{threeparttable}
\end{table}

Figure~\ref{fig:het} plots the same estimates together with the within-region ones. A single regression that interacts vote share with membership of the governing coalition gives a gradient of @@mh_s@@ points for opposition parties and a difference of @@mh_m@@ points (s.e.\ @@mh_mse@@) for majority parties, again with party-by-region effects.

\begin{figure}[htbp]\centering
\includegraphics[width=\textwidth]{fig/fig7_het.pdf}
\caption{The vote--request gradient by party}\label{fig:het}
\begin{minipage}{0.95\textwidth}\footnotesize \emph{Notes:} Coefficients on 2022 vote share (10 pp) from separate regressions for each party, all five budgets, with 95\% confidence intervals. Filled: budget and region FE. Hollow: budget and party $\times$ region FE.\end{minipage}
\end{figure}

\subsection{Contested provinces and the pre-election budget}

Swing-voter models predict that parties target provinces where the election is close \citep{lindbeck1987,dixit1996}, and models of electoral uncertainty predict that behaviour may change as the next election approaches \citep{alesina1990}. I define a province as contested if, in 2022, the gap between the two strongest of the centre-right (FdI, Lega, FI, Noi Moderati), the centre-left (PD, AVS, +Europa) and the M5S was below the median. The M5S ran alone and finished ahead of the centre-left in 27 of the 109 provinces, mostly in the South (first in 3, second in 24), so a gap between the centre-right and the centre-left would misclassify them. I then interact vote share with this indicator and with the 2027 budget, with party-by-budget and party-by-region effects. The gradient is @@c_s@@ points (s.e.\ @@c_sse@@) in safe provinces and @@c_cl@@ points higher (s.e.\ @@c_clse@@) in contested ones. The interaction with the 2027 budget is @@c_27@@ (s.e.\ @@c_27se@@) and the triple interaction @@c_c27@@ (s.e.\ @@c_c27se@@). Parties ask for money where they are strong, more so where the contest is open, and there is no clear sign that the pre-election budget is different. With a single pre-election budget, this last comparison has little power.

\subsection{What gets approved}

I now move to the level of the single proposal and estimate the probability that a proposal is approved, using all proposals by majority and opposition legislators in the four first readings that have been voted (""" + n(a1['n']) + r""" proposals, """ + n(a1['g']) + r""" first signatories). Table~\ref{tab:approval} reports linear probability models with chamber-by-budget fixed effects and standard errors clustered by first signatory.

Majority status is the dominant predictor. A majority proposal is """ + f"{a1['mag']['b']:.1f}" + r""" points more likely to pass, against an opposition base rate of """ + f"{AP['base']:.1f}" + r"""\% (column~1). In raw terms, """ + f"{AP['basemag']:.1f}" + r"""\% of majority proposals and """ + f"{AP['base']:.1f}" + r"""\% of opposition proposals were approved. Majority proposals are also more often ruled inadmissible (""" + f"{AP['ina_mag']:.1f}" + r"""\% against """ + f"{AP['ina_opp']:.1f}" + r"""\%), consistent with majority members tabling many narrow requests that the leadership later filters. Local proposals are not significantly more likely to pass once the signatory's camp is accounted for (column~2). Proposals co-signed by more legislators are more likely to pass and those asking for more than 100 million euro less likely (column~3). Comparing proposals by the same legislator (column~4), local requests are """ + f"{a4['loc']['b']:.1f}" + r""" points more likely to pass than the same legislator's general proposals. Figure~\ref{fig:approval} shows the majority--opposition gap budget by budget.

\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\begin{threeparttable}
\caption{Probability that a proposal is approved}\label{tab:approval}
\begin{tabular}{lcccc}
\toprule
 & (1) & (2) & (3) & (4) \\
\midrule
Majority signatory & """ + f"{apc(a1,'mag')} & {apc(a2,'mag')} & {apc(a3,'mag')} & " + r""" \\
 & """ + f"{aps(a1,'mag')} & {aps(a2,'mag')} & {aps(a3,'mag')} & " + r""" \\
Local proposal & & """ + f"{apc(a2,'loc')} & {apc(a3,'loc')} & {apc(a4,'loc')}" + r""" \\
 & & """ + f"{aps(a2,'loc')} & {aps(a3,'loc')} & {aps(a4,'loc')}" + r""" \\
Majority $\times$ local & & """ + f"{apc(a2,'mag:loc')} & {apc(a3,'mag:loc')} & " + r""" \\
 & & """ + f"{aps(a2,'mag:loc')} & {aps(a3,'mag:loc')} & " + r""" \\
log(1 + co-signatories) & & & """ + f"{apc(a3,'np.log1p(nf)')} & {apc(a4,'np.log1p(nf)')}" + r""" \\
 & & & """ + f"{aps(a3,'np.log1p(nf)')} & {aps(a4,'np.log1p(nf)')}" + r""" \\
Request $\geq$ 100 million euro & & & """ + f"{apc(a3,'big')} & {apc(a4,'big')}" + r""" \\
 & & & """ + f"{aps(a3,'big')} & {aps(a4,'big')}" + r""" \\[3pt]
Chamber $\times$ budget FE & Yes & Yes & Yes & Yes \\
Topic FE & No & No & Yes & Yes \\
First-signatory FE & No & No & No & Yes \\
Observations & """ + ' & '.join(n(m['n']) for m in [a1,a2,a3,a4]) + r""" \\
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} Linear probability models; coefficients in percentage points. Sample: proposals by majority and opposition legislators in the first readings of the 2023--2026 budgets. Standard errors clustered by first signatory in parentheses. $^{*}p<0.05$, $^{**}p<0.01$, $^{***}p<0.001$.
\end{tablenotes}
\end{threeparttable}
\end{table}

\begin{figure}[htbp]\centering
\includegraphics[width=\textwidth]{fig/fig5_approval.pdf}
\caption{Approval rates by camp, first readings}\label{fig:approval}
\end{figure}

\subsection{Where the majority premium arises}

The approval gap can arise at two stages, the admissibility ruling by the committee chair or the vote, which in practice reflects the opinion of the government and of the rapporteurs. Figure~\ref{fig:stages} separates them. Majority proposals are \emph{less} likely to be ruled admissible, at @@st_adm_m@@\% against @@st_adm_o@@\% for the opposition, @@st_admb@@ points (s.e.\ @@st_admse@@) with chamber-by-budget and topic effects. Local proposals are also more often inadmissible (@@st_admloc@@ points, s.e.\ @@st_admlocse@@), mostly for extraneity of subject matter. Among admissible proposals, however, @@st_apa_m@@\% of majority proposals are approved against @@st_apa_o@@\% of opposition ones, a gap of @@st_apb@@ points (s.e.\ @@st_apse@@). The premium is created at the vote, not by the procedural filter. Selection is a concern, because majority legislators may table more proposals that have already been negotiated with the government. Among approved local requests by majority parties, @@g_fdi@@ were signed by FdI, @@g_lega@@ by the Lega and @@g_fi@@ by Forza Italia, so the smaller coalition partners obtain far more local approvals than their seat shares would suggest.

\begin{figure}[htbp]\centering
\includegraphics[width=\textwidth]{fig/fig8_stages.pdf}
\caption{Admissibility and approval by camp, first readings 2023--2026}\label{fig:stages}
\begin{minipage}{0.95\textwidth}\footnotesize \emph{Notes:} Proposals by majority and opposition legislators in the first readings of the 2023--2026 budgets. Admissible: not ruled inadmissible by the committee chair.\end{minipage}
\end{figure}

\subsection{The geography of requests}

Figure~\ref{fig:map} maps local requests per 100,000 residents over the whole legislature and the number of approved local requests. Requests are dense in Tuscany, Sicily and Apulia, regions where several opposition legislators are prolific signatories, and in provinces with industrial crises such as Taranto and Siracusa. Approved requests are much rarer, with 73 province mentions spread over 38 provinces, led by Rome with nine.

\begin{figure}[htbp]\centering
\includegraphics[width=\textwidth]{fig/fig4_map.pdf}
\caption{Local requests, 2023--2027 budgets}\label{fig:map}
\begin{minipage}{0.95\textwidth}\footnotesize \emph{Notes:} Proposals by legislators (excluding government and rapporteurs) naming a province or one of its municipalities, both chambers. A proposal naming several provinces counts once for each.\end{minipage}
\end{figure}

\section{Robustness}\label{sec:robust}

Table~\ref{tab:robust} re-estimates the two main specifications on different samples. The cross-Italy coefficient is positive and significant in every case. The within-region coefficient is positive and significant at the 5\% level in every sample, including each chamber separately, first readings only, and excluding the four largest metropolitan provinces. Excluding the 2023 budget, for which the Chamber published only flagged proposals, leaves the estimates unchanged. A logit model gives an average marginal effect of """ + f"{ROB['logit_ame']:.1f}" + r""" points (s.e. """ + f"{ROB['logit_ame_se']:.1f}" + r""") for the specification of column~2 of Table~\ref{tab:main}. Finally, I permute vote shares across provinces within each party, region and budget """ + str(ROB['nperm']) + r""" times. A within-region coefficient as large as the observed one occurs in """ + f"{100*ROB['perm_p']:.0f}" + r"""\% of permutations.


\paragraph{Specification curve.} To show that the result does not depend on a particular set of choices, I estimate every combination of three outcome definitions (any local request, local requests only, or admissible requests only), four samples (both chambers, the Chamber, the Senate, or first readings), three sets of budgets for the pooled sample (all, all but 2023, or all but 2027), four sets of fixed effects (region, party $\times$ region, province $\times$ budget, or both) and two sets of provinces (all, or all but Rome, Milan, Naples and Turin), for @@sp_n@@ specifications \citep{simonsohn2020}. Figure~\ref{fig:spec} sorts the estimates. All are positive, ranging from @@sp_min@@ to @@sp_max@@ points, and @@sp_sig@@ are significant at 5\%. The median is @@sp_med@@. The median estimate is @@sp_fe_reg@@ with region effects, @@sp_fe_py@@ with province-by-budget effects, @@sp_fe_gr@@ with party-by-region effects and @@sp_fe_both@@ with both: the comparisons within regions are the ones that shrink the gradient.

\paragraph{Counts.} A Poisson pseudo-maximum-likelihood model for the number of local requests \citep{santossilva2006}, with party-by-budget and region effects and log population, gives a coefficient of @@pp_r@@ (s.e.\ @@pp_rse@@): ten points of vote share are associated with @@pp_rirr@@ times as many requests. With province-by-budget effects the coefficient is @@pp_p@@ (s.e.\ @@pp_pse@@).

\begin{figure}[htbp]\centering
\includegraphics[width=\textwidth]{fig/fig6_spec.pdf}
\caption{Specification curve}\label{fig:spec}
\begin{minipage}{0.95\textwidth}\footnotesize \emph{Notes:} Upper panel: coefficient on 2022 vote share (10 pp) with 95\% confidence intervals, clustered by province, in @@sp_n@@ specifications sorted by size; filled points are significant at 5\%. Lower panel: the choices that define each specification. Chamber-only, Senate-only and first-reading samples use all five budgets.\end{minipage}
\end{figure}
\begin{table}[htbp]\centering\footnotesize\setlength{\tabcolsep}{4pt}
\begin{threeparttable}
\caption{Robustness}\label{tab:robust}
\begin{tabular}{lcccc}
\toprule
 & \multicolumn{2}{c}{Region FE} & \multicolumn{2}{c}{Party $\times$ region FE} \\
\cmidrule(lr){2-3}\cmidrule(lr){4-5}
Sample & Coef. & s.e. & Coef. & s.e. \\
\midrule
""" + rob_rows + r"""
\bottomrule
\end{tabular}
\begin{tablenotes}\footnotesize
\item \emph{Notes:} All regressions include party $\times$ budget FE. Dependent variable: local request (0/1). Coefficients on 2022 vote share (10 pp), in percentage points; standard errors clustered by province.
\end{tablenotes}
\end{threeparttable}
\end{table}

\section{Discussion and conclusion}\label{sec:concl}

Members of the Italian Parliament ask for local money where their party is strong. The pattern is stable across five budgets, both chambers and @@sp_n@@ specifications, and it holds when parties are compared within the same province and budget. Within regions it runs through the geography of elected deputies, which points to individual legislators claiming resources for their own constituencies rather than to a centrally planned party strategy. It is driven by the opposition, while the senior governing party leans towards provinces where it is weaker. Whether a request becomes law depends overwhelmingly on whether the signatory sits in the majority. The premium arises at the vote, not at the admissibility stage, and approved local money does not track electoral strength within regions.
Proponents of local spending often defend it as an investment that pays for itself through its effects on the local economy. The evidence on local fiscal multipliers does not support that argument as a general rule. Estimates based on Italian provinces find output multipliers of about 1.5 for public works \citep{acconcia2014}, and the cross-regional literature finds multipliers of a similar size \citep{chodorowreich2019}. These are relative effects that partly reflect resources moved from elsewhere in the country, and a multiplier of 1.5 is far from what would be needed for spending to finance itself through tax revenue. A text search of the dataset finds no local amendment that quantifies such an effect.


Three caveats apply. The analysis is descriptive, and local needs correlated with past votes may explain part of the gradient. Places and sums are extracted automatically from legal texts. I validated the procedure on samples but errors remain, and I avoid relying on euro amounts. The data are not homogeneous across years. The 2023 Chamber file covers flagged proposals only, second readings are mostly symbolic, and the 2027 budget is still under examination.

The dataset opens several avenues. The approved amendments can be linked to the financial effects certified by the parliamentary budget services to measure how much of the final budget is shaped in Parliament. The attribution of deputies to provinces can be refined with single-member districts, senators and the place of birth or residence of each legislator, and the scheduled calendar of municipal elections offers a source of variation in the timing of local incentives that is plausibly unrelated to budget politics. The Senate stage of the 2027 budget will show whether the weaker within-region pattern of that year persists.

\section*{Data availability}\label{sec:avail}\sloppy
The dataset and a replication package (R code that reproduces every table and figure from the CSV files) have been prepared and are available from the author on request and will be made public upon publication. All primary sources are public on the websites of the Chamber of Deputies, the Senate of the Republic, the Ministry of the Interior and ISTAT.

\begin{thebibliography}{99}\small
\bibitem[Acconcia et~al.(2014)]{acconcia2014} Acconcia, A., Corsetti, G., and Simonelli, S. (2014). Mafia and public spending: Evidence on the fiscal multiplier from a quasi-experiment. \emph{American Economic Review}, 104(7), 2185--2209.
\bibitem[Alesina and Tabellini(1990)]{alesina1990} Alesina, A., and Tabellini, G. (1990). A positive theory of fiscal deficits and government debt. \emph{Review of Economic Studies}, 57(3), 403--414.
\bibitem[Ansolabehere and Snyder(2006)]{ansolabehere2006} Ansolabehere, S., and Snyder, J.~M. (2006). Party control of state government and the distribution of public expenditures. \emph{Scandinavian Journal of Economics}, 108(4), 547--569.
\bibitem[Bellemare and Wichman(2020)]{bellemare2020} Bellemare, M.~F., and Wichman, C.~J. (2020). Elasticities and the inverse hyperbolic sine transformation. \emph{Oxford Bulletin of Economics and Statistics}, 82(1), 50--61.
\bibitem[Berry et~al.(2010)]{berry2010} Berry, C.~R., Burden, B.~C., and Howell, W.~G. (2010). The president and the distribution of federal spending. \emph{American Political Science Review}, 104(4), 783--799.
\bibitem[Bracco et~al.(2015)]{bracco2015} Bracco, E., Lockwood, B., Porcelli, F., and Redoano, M. (2015). Intergovernmental grants as signals and the alignment effect: Theory and evidence. \emph{Journal of Public Economics}, 123, 78--91.
\bibitem[Brollo and Nannicini(2012)]{brollo2012} Brollo, F., and Nannicini, T. (2012). Tying your enemy's hands in close races: The politics of federal transfers in Brazil. \emph{American Political Science Review}, 106(4), 742--761.
\bibitem[Cameron and Miller(2015)]{cameron2015} Cameron, A.~C., and Miller, D.~L. (2015). A practitioner's guide to cluster-robust inference. \emph{Journal of Human Resources}, 50(2), 317--372.
\bibitem[Carozzi and Repetto(2016)]{carozzi2016} Carozzi, F., and Repetto, L. (2016). Sending the pork home: Birth town bias in transfers to Italian municipalities. \emph{Journal of Public Economics}, 134, 42--52.
\bibitem[Chodorow-Reich(2019)]{chodorowreich2019} Chodorow-Reich, G. (2019). Geographic cross-sectional fiscal spending multipliers: What have we learned? \emph{American Economic Journal: Economic Policy}, 11(2), 1--34.
\bibitem[Cox and McCubbins(1986)]{cox1986} Cox, G.~W., and McCubbins, M.~D. (1986). Electoral politics as a redistributive game. \emph{Journal of Politics}, 48(2), 370--389.
\bibitem[Dixit and Londregan(1996)]{dixit1996} Dixit, A., and Londregan, J. (1996). The determinants of success of special interests in redistributive politics. \emph{Journal of Politics}, 58(4), 1132--1155.
\bibitem[Golden and Picci(2008)]{golden2008} Golden, M.~A., and Picci, L. (2008). Pork-barrel politics in postwar Italy, 1953--94. \emph{American Journal of Political Science}, 52(2), 268--289.
\bibitem[Levitt and Snyder(1997)]{levitt1997} Levitt, S.~D., and Snyder, J.~M. (1997). The impact of federal spending on House election outcomes. \emph{Journal of Political Economy}, 105(1), 30--53.
\bibitem[Lindbeck and Weibull(1987)]{lindbeck1987} Lindbeck, A., and Weibull, J.~W. (1987). Balanced-budget redistribution as the outcome of political competition. \emph{Public Choice}, 52(3), 273--297.
\bibitem[Mayhew(1974)]{mayhew1974} Mayhew, D.~R. (1974). \emph{Congress: The Electoral Connection}. New Haven: Yale University Press.
\bibitem[Persson and Tabellini(1999)]{perssontabellini1999} Persson, T., and Tabellini, G. (1999). Political economics and macroeconomic policy. In J.~B. Taylor and M.~Woodford (eds.), \emph{Handbook of Macroeconomics}, Vol.~1C, ch.~22, 1397--1482. Amsterdam: Elsevier.
\bibitem[Santos Silva and Tenreyro(2006)]{santossilva2006} Santos Silva, J.~M.~C., and Tenreyro, S. (2006). The log of gravity. \emph{Review of Economics and Statistics}, 88(4), 641--658.
\bibitem[Simonsohn et~al.(2020)]{simonsohn2020} Simonsohn, U., Simmons, J.~P., and Nelson, L.~D. (2020). Specification curve analysis. \emph{Nature Human Behaviour}, 4(11), 1208--1214.
\bibitem[Weingast et~al.(1981)]{weingast1981} Weingast, B.~R., Shepsle, K.~A., and Johnsen, C. (1981). The political economy of benefits and costs: A neoclassical approach to distributive politics. \emph{Journal of Political Economy}, 89(4), 642--664.
\end{thebibliography}
\end{document}
"""
VALS = {
 'wp_b': f"{WP['b']:.1f}", 'wp_se': f"{WP['se']:.1f}", 'wpg_b': f"{X['within_prov_gr']['b']:.1f}", 'wpg_se': f"{X['within_prov_gr']['se']:.1f}",
 'mpw_s': f"{MPw['s']['b']:.1f}", 'mpw_sse': f"{MPw['s']['se']:.1f}", 'mpw_mp': f"{MPw['mp']['b']:.1f}", 'mpw_mpse': f"{MPw['mp']['se']:.1f}",
 'mpp_s': f"{MPp['s']['b']:.1f}", 'mpp_sse': f"{MPp['s']['se']:.1f}", 'mpp_mp': f"{MPp['mp']['b']:.1f}", 'mpp_mpse': f"{MPp['mp']['se']:.1f}",
 'mpv_s': f"{MPv['s']['b']:.1f}", 'mpv_sse': f"{MPv['s']['se']:.1f}", 'mpv_mp': f"{MPv['mp']['b']:.1f}", 'mpv_mpse': f"{MPv['mp']['se']:.1f}",
 'mpo': f"{X['mp_only_prov']['b']:.1f}", 'mpo_se': f"{X['mp_only_prov']['se']:.1f}", 'corr': f"{X['corr_s_mp']:.2f}", 'mpmean': f"{X['mp_mean']:.2f}", 'mpsd': f"{X['mp_sd']:.2f}",
 'pp_r': f"{X['ppml_reg']['b']:.2f}", 'pp_rse': f"{X['ppml_reg']['se']:.2f}", 'pp_rirr': f"{X['ppml_reg']['irr']:.2f}",
 'pp_p': f"{X['ppml_prov']['b']:.2f}", 'pp_pse': f"{X['ppml_prov']['se']:.2f}", 'pp_pirr': f"{X['ppml_prov']['irr']:.2f}",
 'c_s': f"{C27['s']['b']:.1f}", 'c_sse': f"{C27['s']['se']:.1f}", 'c_cl': f"{C27['s:close']['b']:.1f}", 'c_clse': f"{C27['s:close']['se']:.1f}",
 'c_27': f"{C27['s:y27']['b']:.1f}", 'c_27se': f"{C27['s:y27']['se']:.1f}", 'c_c27': f"{C27['s:close:y27']['b']:.1f}", 'c_c27se': f"{C27['s:close:y27']['se']:.1f}",
 'mh_s': f"{X['majhet']['s']['b']:.1f}", 'mh_sse': f"{X['majhet']['s']['se']:.1f}", 'mh_m': f"{X['majhet']['smaj']['b']:.1f}", 'mh_mse': f"{X['majhet']['smaj']['se']:.1f}",
 'sp_n': str(SS['n']), 'sp_pos': str(SS['pos']), 'sp_sig': str(SS['sig']), 'sp_med': f"{SS['med']:.1f}",
 'sp_fe_reg': f"{SS['by_fe']['Region']:.1f}", 'sp_fe_gr': f"{SS['by_fe']['Party×region']:.1f}", 'sp_fe_py': f"{SS['by_fe']['Province×year']:.1f}", 'sp_fe_both': f"{SS['by_fe']['Party×region + province×year']:.1f}",
 'sp_min': f"{min(x['b'] for x in X['spec']):.1f}", 'sp_max': f"{max(x['b'] for x in X['spec']):.1f}",
 'st_adm_m': f"{STG['raw_mag']['adm']:.1f}", 'st_adm_o': f"{STG['raw_opp']['adm']:.1f}", 'st_apa_m': f"{STG['raw_mag']['ap_adm']:.1f}", 'st_apa_o': f"{STG['raw_opp']['ap_adm']:.1f}",
 'st_admb': f"{STG['adm']['mag']['b']:.1f}", 'st_admse': f"{STG['adm']['mag']['se']:.1f}", 'st_admloc': f"{STG['adm']['loc']['b']:.1f}", 'st_admlocse': f"{STG['adm']['loc']['se']:.1f}",
 'st_apb': f"{STG['ap_given_adm']['mag']['b']:.1f}", 'st_apse': f"{STG['ap_given_adm']['mag']['se']:.1f}", 'st_aploc': f"{STG['ap_given_adm']['loc']['b']:.1f}", 'st_aplocse': f"{STG['ap_given_adm']['loc']['se']:.1f}",
 'g_fdi': str(X['gamson']['FdI']['ap_local']), 'g_lega': str(X['gamson']['Lega']['ap_local']), 'g_fi': str(X['gamson']['FI']['ap_local']),
}
import re as _re
tex = _re.sub(r'@@(\w+)@@', lambda m: VALS[m.group(1)], tex)
open('/home/claude/multi/paper/landi_budget_amendments_wp.tex', 'w').write(tex)
print('ok')
