# ---------------------------------------------------------------------
# 02. Main results (Tables 2, 4, 5 and 7)
# ---------------------------------------------------------------------
# Table 2. Local request (0/1) on 2022 vote share (10 points)
T2 <- list(
  c1 = ols(any ~ s + factor(gy), D),                          # party x budget FE
  c2 = ols(any ~ s + factor(gy) + factor(reg), D),            # + region FE
  c3 = ols(any ~ s + factor(gy) + factor(gr), D),             # party x region FE
  c4 = ols(ihs ~ s + factor(gy) + factor(reg), D) / c(100, 100, 1),
  c5 = ols(ihs ~ s + factor(gy) + factor(gr), D) / c(100, 100, 1),
  c6 = ols(anyA ~ s + factor(gy) + factor(reg), D[D$y < 2027, ]),  # approved requests, voted budgets
  c7 = ols(anyA ~ s + factor(gy) + factor(gr), D[D$y < 2027, ]))
cat("\nTable 2\n"); print(sapply(T2, show, digits = 3))
cat("Mean of the dependent variable (%):", round(100 * mean(D$any), 2), "\n")

# Table 4. Budget by budget
T4 <- t(sapply(years, function(t) {
  d <- D[D$y == t, ]
  c(pooled = show(ols(any ~ s + factor(g) + factor(reg), d)), within = show(ols(any ~ s + factor(gr), d)), mean = round(100 * mean(d$any), 1))
}))
rownames(T4) <- years; cat("\nTable 4\n"); print(T4)

# Table 5. One regression per party
T5 <- t(sapply(parties, function(k) show(ols(any ~ s + factor(y) + factor(reg), D[D$g == k, ]))))
cat("\nTable 5\n"); print(T5)

# Table 7. Robustness: other samples
rob <- function(d) c(pooled = show(ols(any ~ s + factor(gy) + factor(reg), d)), within = show(ols(any ~ s + factor(gy) + factor(gr), d)))
T7 <- rbind(
  baseline      = rob(D),
  chamber_only  = rob(build_panel(am$ramo == "Camera")),
  senate_only   = rob(build_panel(am$ramo == "Senato")),
  first_reading = rob(build_panel(am$lettura == 1)),
  excl_2023     = rob(D[D$y != 2023, ]),
  excl_2027     = rob(D[D$y != 2027, ]),
  excl_metro    = rob(D[D$metro == 0, ]))
cat("\nTable 7\n"); print(T7)

# Logit: average marginal effect of vote share (column 2 specification)
lg  <- glm(any ~ s + factor(gy) + factor(reg), family = binomial, data = D)
ame <- mean(dlogis(predict(lg, type = "link"))) * coef(lg)["s"] * 100
cat("Logit average marginal effect:", round(ame, 2), "points\n")

# Permutation test: reshuffle vote shares within party x region x budget (300 times)
set.seed(20261126)
fe <- model.matrix(~ factor(gy) + factor(gr), D)
res <- function(v) lm.fit(fe, v)$residuals
ry  <- res(D$any); b_obs <- sum(res(D$s) * ry) / sum(res(D$s)^2)
cell <- split(seq_len(nrow(D)), paste(D$g, D$reg, D$y))
perm <- replicate(300, { sp <- D$s; for (ix in cell) sp[ix] <- sp[ix][sample.int(length(ix))]; r <- res(sp); sum(r * ry) / sum(r^2) })
cat("Permutation p-value:", mean(abs(perm) >= abs(b_obs)), "\n")
write.csv(do.call(rbind, T2), "output/table2.csv")
