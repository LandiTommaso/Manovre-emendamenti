# ---------------------------------------------------------------------
# 04. What gets approved (Table 6) and where the majority premium arises (Figure 6)
# ---------------------------------------------------------------------
A <- am[am$lettura == 1 & am$manovra < 2027 & am$schieramento %in% c("Maggioranza", "Opposizione"), ]
A$ap  <- as.integer(A$esito == "Approvato")
A$adm <- as.integer(A$esito != "Inammissibile")
A$mag <- as.integer(A$schieramento == "Maggioranza")
A$loc <- as.integer(A$portata == "Locale")
A$pid <- ifelse(is.na(A$id_firmatario) | A$id_firmatario == "", A$primo_firmatario, as.character(A$id_firmatario))
A$th  <- ifelse(A$tema == "", "Altro", sub(";.*", "", A$tema))
euro  <- ifelse(is.na(A$euro_triennio), 0, A$euro_triennio)   # single rule: three-year cost only; a figure without years does not count
A$big <- as.integer(euro >= 1e8)
A$ry  <- paste(A$ramo, A$manovra)
cat("\nApproval sample:", nrow(A), "proposals,", length(unique(A$pid)), "first signatories\n")

fit <- function(f, d) { m <- lm(f, d); V <- vcovCL(m, cluster = d$pid, type = "HC1")
  v <- intersect(c("mag", "loc", "mag:loc", "log1p(n_firmatari)", "big"), names(coef(m)))
  round(cbind(b = coef(m)[v], se = sqrt(diag(V)[v])) * 100, 2) }
cat("\nTable 6\n")
print(fit(ap ~ mag + factor(ry), A))
print(fit(ap ~ mag * loc + factor(ry), A))
print(fit(ap ~ mag * loc + log1p(n_firmatari) + big + factor(ry) + factor(th), A))
print(fit(ap ~ loc + log1p(n_firmatari) + big + factor(ry) + factor(th) + factor(pid), A))
cat("Approval rate, opposition:", round(100 * mean(A$ap[A$mag == 0]), 2), "% ; majority:", round(100 * mean(A$ap[A$mag == 1]), 2), "%\n")

# Stages: admissibility, then approval among admissible proposals
stages <- sapply(c(Majority = 1, Opposition = 0), function(c) { s <- A[A$mag == c, ]
  c(admissible = 100 * mean(s$adm), approved_if_admissible = 100 * mean(s$ap[s$adm == 1]), approved = 100 * mean(s$ap)) })
print(round(stages, 1))
print(fit(adm ~ mag + loc + factor(ry) + factor(th), A))
print(fit(ap ~ mag + loc + factor(ry) + factor(th), A[A$adm == 1, ]))
write.csv(round(stages, 2), "output/stages.csv")
