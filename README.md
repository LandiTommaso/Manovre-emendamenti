# Where the Votes Are — Le manovre della legislatura, emendamento per emendamento

**Tommaso Landi** (Scuola Superiore Sant'Anna e Università di Pisa) · Working paper, v2, 26 novembre 2026

Tutte le **24.977 proposte di modifica** presentate nelle commissioni Bilancio di Camera e Senato alle cinque leggi di bilancio della XIX legislatura (2023–2027). Per ogni proposta il repository riporta primo firmatario e gruppo, ammissibilità, esito, territori citati, importi e link alla scheda ufficiale. Le richieste locali sono poi confrontate con i voti delle politiche del 2022.

| | |
|---|---|
| 📄 Working paper | [`paper/landi_budget_amendments_wp.pdf`](paper/landi_budget_amendments_wp.pdf) |
| 🗺️ Esploratore 2023–2027 | <https://landitommaso.github.io/manovre-emendamenti/legislatura/> |
| 🔎 Manovra 2027 nel dettaglio | <https://landitommaso.github.io/manovre-emendamenti/manovra-2027/> |
| 📰 Sintesi per la stampa | <https://landitommaso.github.io/manovre-emendamenti/sintesi/> |

## Risultati principali

1. Con 10 punti di voto in più nel 2022, la probabilità che un partito chieda soldi per una provincia sale di **12,2 punti** (media 13,4%).
2. Il legame regge confrontando partiti diversi **nella stessa provincia e manovra** (12,4 punti). Tutte le 144 specificazioni alternative sono positive e 137 sono significative al 5%.
3. Dentro la stessa regione il legame passa per i **deputati eletti nella provincia**.
4. È guidato dall'**opposizione**; FdI chiede dove è relativamente più debole.
5. Le proposte della maggioranza passano nel 12,4% dei casi, quelle dell'opposizione nel 2,9%. Il vantaggio nasce **al voto**, non all'ammissibilità.

## Replicare i risultati (R)

```r
# dalla cartella principale del repository
install.packages(c("sandwich", "lmtest"))
source("code/R/00_master.R")
```

Gli script sono pensati per essere letti da una persona, uno per tabella o figura. Il tempo di esecuzione è di circa 2–3 minuti.

| Script | Cosa produce |
|---|---|
| `01_panel.R` | Il pannello provincia × partito × manovra (4.360 osservazioni) |
| `02_main_tables.R` | Tabelle 2, 4, 5, 7; logit; test di permutazione |
| `03_within_province.R` | Tabella 3 (stessa provincia, deputati eletti), province contese, PPML |
| `04_approval.R` | Tabella 6 e approvazione per fasi (Figura 6) |
| `05_spec_curve.R` | Curva delle 144 specificazioni (Figura 8) |
| `06_figures.R` | Figure in R base |
| `99_check.R` | Confronta i numeri ottenuti in R con quelli del paper ([`code/paper_numbers.csv`](code/paper_numbers.csv)) |

Gli errori standard sono a cluster per provincia, con la correzione CR1 (`sandwich::vcovCL`, `type = "HC1"`). Gli stessi risultati sono stati prodotti in modo indipendente in Python (`code/python/legislatura/paper_stats.py`, `paper_extra.py`) e coincidono alla terza cifra decimale.

## Dati (`data/`)

| File | Contenuto |
|---|---|
| `emendamenti_2023_2027.csv` | Una riga per proposta (24.977). Contiene manovra, ramo, atto, lettura, numero, articolo, primo firmatario e id, gruppo alla data della manovra, schieramento, firmatari, esito, motivo di inammissibilità, portata (Locale / Più territori / Nazionale), province, regioni e luoghi citati, tema, euro annui e nel triennio, flag grande opera, copertura, oggetto e link ufficiale. |
| `testi_emendamenti_2023_2027.csv.gz` | Testo integrale di ogni proposta, come pubblicato. |
| `voti_camera_2022_province.csv` | Voti di lista alla Camera 2022 per provincia (Eligendo) e popolazione ISTAT all'1/1/2025. |
| `elettori_provincia_collegio_2022.csv` | Elettori per provincia e collegio plurinominale (Eligendo). |
| `deputati_collegi.csv` | Deputati in carica, gruppo e collegio di elezione (dati.camera.it). |
| `panel_provincia_partito_manovra.csv` | Il pannello di stima, già costruito. |

**Avvertenze sui dati**
- Per il 2023 la Camera ha pubblicato solo le proposte *segnalate* (1.043 su circa 3.000).
- In seconda lettura nessuna proposta è approvata.
- La manovra 2027 non è ancora stata votata in commissione.
- Luoghi e importi sono letti automaticamente dai testi. Prima di citare un caso, controlla la scheda ufficiale nella colonna `link_ufficiale`.

## Come sono stati costruiti i dati (`code/python/`)

Questa cartella contiene la pipeline originale, in Python: scarica e legge i fascicoli e gli elenchi ufficiali di Camera e Senato, attribuisce i gruppi tramite gli open data delle due Camere, classifica testi, luoghi e importi, ed esporta i dati dei siti. I percorsi sono quelli dell'ambiente di lavoro originale. Le fonti primarie sono elencate nel paper e nella sezione «Fonti» dell'esploratore.

## Siti (`docs/`)

Gli esploratori interattivi, pubblicati con GitHub Pages dalla cartella `docs/`.

## Uso dell'intelligenza artificiale

Il progetto è stato realizzato con l'aiuto fondamentale di **Claude** (Anthropic), che ha:
- scritto gran parte del codice di raccolta e analisi;
- eseguito le specificazioni;
- redatto parte del testo, sotto la direzione dell'autore.

La domanda di ricerca, il disegno dei dati e delle stime, i controlli sulle fonti ufficiali e l'interpretazione sono dell'autore, che è responsabile di ogni affermazione. Dati e codice sono pubblici perché chiunque possa verificare ogni numero.

## Citare

> Landi, T. (2026). *Where the Votes Are: Electoral Strength and Local Spending Requests in Italian Budget Laws, 2023–2027*. Working paper, v2.

Vedi anche [`CITATION.cff`](CITATION.cff).

## Licenze

- **Codice:** MIT (vedi `LICENSE`).
- **Dati derivati:** CC BY 4.0, citando questo repository e le fonti primarie (Camera dei deputati, Senato della Repubblica, Ministero dell'Interno, ISTAT).
- **Working paper:** © 2026 Tommaso Landi, tutti i diritti riservati.

Ringrazio Riccardo Trezzi ([UnderlyingInflation.com](https://underlyinginflation.com)) per l'ispirazione.
