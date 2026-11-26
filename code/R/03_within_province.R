# ---------------------------------------------------------------------
# 03. Same-province comparisons and elected deputies (Table 3)
# ---------------------------------------------------------------------
# (1) province x budget FE: compares DIFFERENT parties in the SAME province and budget
# (2) + party x region FE
# (3)-(6) add the number of the party's deputies elected in the province
T3 <- list(
  c1 = ols(any ~ s + factor(gy) + factor(py), D),
  c2 = ols(any ~ s + factor(gy) + factor(gr) + factor(py), D),
  c3 = rbind(s = ols(any ~ s + mp + factor(gy) + factor(reg) + lpop, D), mp = ols(any ~ s + mp + factor(gy) + factor(reg) + lpop, D, "mp")),
  c4 = rbind(s = ols(any ~ s + mp + factor(gy) + factor(py), D),         mp = ols(any ~ s + mp + factor(gy) + factor(py), D, "mp")),
  c5 = rbind(s = ols(any ~ s + mp + factor(gy) + factor(gr), D),         mp = ols(any ~ s + mp + factor(gy) + factor(gr), D, "mp")),
  c6 = ols(any ~ mp + factor(gy) + factor(py), D, "mp"))
cat("\nTable 3\n"); print(T3)
cat("Correlation between vote share and deputies:", round(cor(D$s, D$mp), 2), "\n")

# Contested provinces and the 2027 (pre-election) budget
D$close <- as.integer(D$marg < median(D$marg)); D$y27 <- as.integer(D$y == 2027)
m <- lm(any ~ s + s:close + s:y27 + s:close:y27 + factor(gy) + factor(gr), D)
V <- vcovCL(m, cluster = D$p, type = "HC1"); k <- c("s", "s:close", "s:y27", "s:close:y27")
cat("\nContested provinces\n"); print(round(cbind(b = coef(m)[k], se = sqrt(diag(V)[k])) * 100, 2))
# Majority vs opposition gradient
m <- lm(any ~ s + s:maj + factor(gy) + factor(gr), D); V <- vcovCL(m, cluster = D$p, type = "HC1")
print(round(cbind(b = coef(m)[c("s", "s:maj")], se = sqrt(diag(V)[c("s", "s:maj")])) * 100, 2))

# Counts: Poisson pseudo-maximum likelihood
pp <- glm(n ~ s + factor(gy) + factor(reg) + lpop, family = quasipoisson, data = D)
cat("PPML coefficient:", round(coef(pp)["s"], 3), "(s.e.", round(sqrt(vcovCL(pp, cluster = D$p, type = "HC0")["s", "s"]), 3), ")\n")
