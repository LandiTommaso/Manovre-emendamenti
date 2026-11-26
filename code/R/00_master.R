# =====================================================================
# Where the Votes Are: Electoral Strength and Local Spending Requests
# in Italian Budget Laws, 2023-2027 -- Tommaso Landi
# Replication package: runs every script in order.
#
# HOW TO RUN: open R (or RStudio) in the main folder of the repository
# (the one that contains "data", "code" and "output") and type
#     source("code/R/00_master.R")
# Packages needed: sandwich, lmtest (install.packages(c("sandwich","lmtest")))
# Run time: about 2-3 minutes on a laptop.
# =====================================================================
rm(list = ls())
library(sandwich)
library(lmtest)
dir.create("output", showWarnings = FALSE)

source("code/R/01_panel.R")          # builds the province x party x budget panel
source("code/R/02_main_tables.R")    # Tables 2, 4, 5, 7 of the paper
source("code/R/03_within_province.R")# Table 3: same-province comparisons, elected deputies
source("code/R/04_approval.R")       # Table 6, approval by stage (Figure 6)
source("code/R/05_spec_curve.R")     # Figure 8: specification curve (144 models)
source("code/R/06_figures.R")        # Figures 1-5, 7
source("code/R/99_check.R")          # compares the R results with the numbers in the paper
