# ---------------------------------------------------------------------
# 06. Figures (simple base-R versions of the paper's figures)
# ---------------------------------------------------------------------
pdf("output/figures.pdf", width = 7, height = 4.5)
# Figure 1. Proposals by budget, chamber and outcome
tab <- table(paste(am$manovra, substr(am$ramo, 1, 1)), am$esito)
barplot(t(tab[, c("Approvato", "Inammissibile", "Ritirato", "Non approvato")]), col = c("#2b7bb9", "#b8322a", "#d99a1e", "#c9ced8"),
        legend.text = c("Approved", "Inadmissible", "Withdrawn", "Rejected / not voted"), las = 2, main = "Proposals by budget and chamber")

# Figure 2. Binned scatter (residuals on party x budget and region FE)
rx <- resid(lm(share ~ factor(gy) + factor(reg), D)); ry <- resid(lm(any ~ factor(gy) + factor(reg), D))
q <- cut(rx, quantile(rx, 0:20 / 20), include.lowest = TRUE)
plot(tapply(rx, q, mean), 100 * tapply(ry, q, mean), pch = 19, col = "#1757ac",
     xlab = "Vote share 2022 (residualised, points)", ylab = "Pr(local request), residualised, pp", main = "Binned scatter")
abline(lm(I(100 * ry) ~ rx), lty = 2)

# Figure 3. Coefficient by budget
est <- t(sapply(years, function(t) { d <- D[D$y == t, ]; c(ols(any ~ s + factor(g) + factor(reg), d)[1:2], ols(any ~ s + factor(gr), d)[1:2]) }))
plot(years - .1, est[, 1], ylim = range(c(est[, 1] - 2 * est[, 2], est[, 1] + 2 * est[, 2], est[, 3] - 2 * est[, 4], est[, 3] + 2 * est[, 4])),
     pch = 19, xlab = "Budget", ylab = "pp per +10 vote points", main = "The gradient budget by budget")
segments(years - .1, est[, 1] - 1.96 * est[, 2], years - .1, est[, 1] + 1.96 * est[, 2])
points(years + .1, est[, 3], pch = 1); segments(years + .1, est[, 3] - 1.96 * est[, 4], years + .1, est[, 3] + 1.96 * est[, 4]); abline(h = 0)
legend("topleft", c("region FE", "party x region FE"), pch = c(19, 1), bty = "n")

# Figure 7. By party
het <- t(sapply(parties, function(k) ols(any ~ s + factor(y) + factor(reg), D[D$g == k, ])[1:2]))
plot(seq_along(parties), het[, 1], ylim = range(c(het[, 1] - 2 * het[, 2], het[, 1] + 2 * het[, 2])), pch = 19, xaxt = "n",
     col = ifelse(parties %in% majority, "#2b5d9c", "#a04a86"), xlab = "", ylab = "pp per +10 vote points", main = "The gradient by party")
axis(1, seq_along(parties), parties, cex.axis = .8); segments(seq_along(parties), het[, 1] - 1.96 * het[, 2], seq_along(parties), het[, 1] + 1.96 * het[, 2]); abline(h = 0)
dev.off()
cat("\nFigures saved in output/figures.pdf\n")
