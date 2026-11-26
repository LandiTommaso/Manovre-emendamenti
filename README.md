# Where the Votes Are: Electoral Strength and Local Spending Requests in Italian Budget Laws, 2023–2027

**Tommaso Landi** (Sant'Anna School of Advanced Studies and University of Pisa) · Preliminary draft, v2, 26 November 2026

> **Private repository. This is preliminary work: please do not circulate it without the author's permission.**
> The data and code will be made public when the paper is published.

This repository covers every amendment tabled in the budget committees of the Italian Chamber of Deputies and Senate to the five budget laws of the XIX legislature (2023–2027): **24,977 proposals** in all. For each proposal it records:
- the first signatory and their group;
- the admissibility ruling and the outcome;
- the places named, the amounts requested and a link to the official record.

The local spending requests are then matched to party vote shares in the 2022 general election.

| | |
|---|---|
| 📄 Working paper | [`paper/landi_budget_amendments_wp.pdf`](paper/landi_budget_amendments_wp.pdf) |
| 🗺️ Interactive explorers | the `docs/` folder (see below for how to open them locally) |
| 🔎 2027 budget explorer (public) | <https://claude.ai/artifact/D5WQFUaW1R2Z67CGSseZGe> |
| 🧭 Research roadmap | [`ROADMAP.md`](ROADMAP.md) |

## Main results

1. Ten extra points of 2022 vote share raise the probability that a party tables a local request for a province by **12.2 percentage points**. The mean probability is 13.4%.
2. The gradient holds when comparing different parties **within the same province and budget**, at 12.4 points. All 144 alternative specifications are positive and 137 are significant at 5%.
3. Within regions, the gradient runs through the **deputies elected in the province**.
4. It is driven by the **opposition**. Fratelli d'Italia asks for money where it is relatively weaker.
5. **Who asks matters most.** 12.4% of majority proposals are approved, against 2.9% for the opposition. The premium arises **at the vote**, not at the admissibility stage.

## Replication (R)

```r
# from the root folder of the repository
install.packages(c("sandwich", "lmtest"))
source("code/R/00_master.R")
```

There is one script per table or figure, and each is written to be read by a person. A full run takes about 2–3 minutes.

| Script | Output |
|---|---|
| `01_panel.R` | Province × party × budget panel (4,360 observations) |
| `02_main_tables.R` | Tables 2, 4, 5 and 7, the logit model and the permutation test |
| `03_within_province.R` | Table 3 (same province, elected deputies), contested provinces and PPML |
| `04_approval.R` | Table 6 and approval by stage (Figure 6) |
| `05_spec_curve.R` | Specification curve with 144 models (Figure 8) |
| `06_figures.R` | Figures in base R |
| `99_check.R` | Checks the R results against the numbers in the paper ([`code/paper_numbers.csv`](code/paper_numbers.csv)) |

Standard errors are clustered by province with the CR1 correction (`sandwich::vcovCL`, `type = "HC1"`). The same estimates were produced independently in Python (`code/python/legislatura/paper_stats.py` and `paper_extra.py`). Python and R agree to three decimal places.

## Data (`data/`)

| File | Content |
|---|---|
| `emendamenti_2023_2027.csv` | One row per proposal (24,977); the columns are listed below. |
| `testi_emendamenti_2023_2027.csv.gz` | The full text of each proposal, as published. |
| `voti_camera_2022_province.csv` | 2022 Chamber list votes by province (Ministry of the Interior, Eligendo) and ISTAT population on 1 January 2025. |
| `elettori_provincia_collegio_2022.csv` | Registered voters by province and list constituency (Eligendo). |
| `deputati_collegi.csv` | Sitting deputies, with group and constituency of election (dati.camera.it). |
| `panel_provincia_partito_manovra.csv` | The estimation panel. |

The columns of `emendamenti_2023_2027.csv` are:
- budget, chamber, bill, reading, number and article;
- first signatory, their ID, their group on the date of the budget and their camp;
- co-signatories, outcome and reason for inadmissibility;
- scope (local, several places or national), and the provinces, regions and places named;
- topic, annual and three-year euros, and a flag for large works;
- funding source, title and official link.

Variable names and labels are in Italian, as in the official sources.

**Caveats**
- For the 2023 budget the Chamber published only the proposals *flagged* by the groups (1,043 of about 3,000).
- No amendment is approved in second readings.
- The 2027 budget had not yet been voted in committee when the data were collected.
- Places and amounts are read automatically from the texts. Before citing a single case, check the official record linked in `link_ufficiale`.
- The data include 1,106 sub-amendments. Without them, the counts match the figures reported at the time.

## How the data were built (`code/python/`)

The original Python pipeline does four things:
1. It downloads and parses the official files and lists of the Chamber and the Senate.
2. It assigns parliamentary groups from the open data of the two chambers.
3. It classifies texts, places and amounts.
4. It exports the data for the websites.

Paths refer to the original working environment, and some comments are in Italian. The primary sources are listed in the paper and in the "Fonti" section of the explorers.

## Websites (`docs/`)

The folder holds the interactive explorers for the 2023–2027 legislature and the 2027 budget, both in Italian, English, Spanish and French, plus a press summary in Italian. To open them locally:

```
cd docs
python3 -m http.server 8000
# then open http://localhost:8000 in a browser
```

Do not enable GitHub Pages on this repository until the work is published.

## Use of AI

This project was carried out with the fundamental help of **Claude** (Anthropic). Under the author's direction, Claude wrote most of the code that collects and analyses the data, ran the specifications and drafted part of the text. The research question, the design of the data and the estimates, the checks against official sources and the interpretation are the author's. The author is responsible for every claim. The data and code will be public on publication, so that anyone can verify every number.

## Citation

> Landi, T. (2026). *Where the Votes Are: Electoral Strength and Local Spending Requests in Italian Budget Laws, 2023–2027*. Preliminary draft, v2.

See also [`CITATION.cff`](CITATION.cff).

## Licence

© 2026 Tommaso Landi. All rights are reserved for the code, the derived data and the working paper (see `LICENSE`). Open licences will be chosen on publication. The primary sources (Chamber of Deputies, Senate of the Republic, Ministry of the Interior and ISTAT) remain subject to their own terms of use.

I thank Riccardo Trezzi ([UnderlyingInflation.com](https://underlyinginflation.com)) for the inspiration.
