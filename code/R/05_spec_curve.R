# ---------------------------------------------------------------------
# 05. Specification curve: 144 ways to estimate the vote-request gradient
# ---------------------------------------------------------------------
outcomes <- list("Any request" = rep(TRUE, nrow(am)), "Local only" = am$portata == "Locale", "Admissible only" = am$esito != "Inammissibile")
samples  <- list("Both chambers" = rep(TRUE, nrow(am)), "Chamber only" = am$ramo == "Camera", "Senate only" = am$ramo == "Senato", "First readings" = am$lettura == 1)
budgets  <- list("All budgets" = 2023:2027, "Excl. 2023" = 2024:2027, "Excl. 2027" = 2023:2026)
fes      <- c("Region" = "factor(gy) + factor(reg)", "Party x region" = "factor(gy) + factor(gr)",
              "Province x year" = "factor(gy) + factor(py)", "Party x region + province x year" = "factor(gy) + factor(gr) + factor(py)")
SPEC <- NULL
for (o in names(outcomes)) for (sa in names(samples)) {
  d0 <- build_panel(outcomes[[o]] & samples[[sa]])
  for (yb in names(budgets)) for (fe in names(fes)) for (met in 0:1) {
    if (yb != "All budgets" && sa != "Both chambers") next      # keeps the grid at 144
    d <- d0[d0$y %in% budgets[[yb]] & (met == 0 | d0$metro == 0), ]
    r <- ols(as.formula(paste("any ~ s +", fes[fe])), d)
    SPEC <- rbind(SPEC, data.frame(outcome = o, sample = sa, budgets = yb, fe = fe, metro = ifelse(met, "Excl. 4 metro", "All provinces"), b = r["b"], se = r["se"]))
  }
}
cat("\nSpecifications:", nrow(SPEC), "; positive:", sum(SPEC$b > 0), "; significant at 5%:", sum(SPEC$b / SPEC$se > 1.96),
    "; median:", round(median(SPEC$b), 2), "\n")
print(round(tapply(SPEC$b, SPEC$fe, median), 2))
write.csv(SPEC, "output/spec_curve.csv", row.names = FALSE)

S <- SPEC[order(SPEC$b), ]; x <- seq_len(nrow(S)); sig <- S$b / S$se > 1.96
pdf("output/fig_spec_curve.pdf", width = 7, height = 4)
plot(x, S$b, ylim = range(c(0, S$b - 1.96 * S$se, S$b + 1.96 * S$se)), pch = ifelse(sig, 19, 1), cex = .5, col = "#1757ac",
     xlab = "Specification (sorted by estimate)", ylab = "pp per +10 vote points", main = "Specification curve")
segments(x, S$b - 1.96 * S$se, x, S$b + 1.96 * S$se, col = "grey80"); points(x, S$b, pch = ifelse(sig, 19, 1), cex = .5, col = "#1757ac")
abline(h = 0)
dev.off()
