# ---------------------------------------------------------------------
# 01. Build the panel: province x party x budget
# ---------------------------------------------------------------------
# Amendments: one row per proposal (see data/README in the main README)
am <- read.csv("data/emendamenti_2023_2027.csv", encoding = "UTF-8", stringsAsFactors = FALSE)
vo <- read.csv("data/voti_camera_2022_province.csv", encoding = "UTF-8", stringsAsFactors = FALSE)
el <- read.csv("data/elettori_provincia_collegio_2022.csv", encoding = "UTF-8", stringsAsFactors = FALSE)
de <- read.csv("data/deputati_collegi.csv", encoding = "UTF-8", stringsAsFactors = FALSE)

parties <- c("FdI", "Lega", "FI", "Noi Moderati", "PD", "M5S", "AVS", "Azione / IV")
vote_col <- c(FdI = "voti_FdI", Lega = "voti_Lega", FI = "voti_FI", "Noi Moderati" = "voti_NM",
              PD = "voti_PD", M5S = "voti_M5S", AVS = "voti_AVS", "Azione / IV" = "voti_AzIV")
years <- 2023:2027
majority <- c("FdI", "Lega", "FI", "Noi Moderati")
table(am$manovra, am$ramo)     # 24,977 proposals, 9 bill readings

# Deputies attributed to provinces: each deputy elected in a list constituency is
# split across the provinces of the constituency in proportion to registered voters.
grp <- c(FDI = "FdI", LEGA = "Lega", "FI-PPE" = "FI", "NM(N-C-U-I)M-CP" = "Noi Moderati", "PD-IDP" = "PD",
         M5S = "M5S", AVS = "AVS", "AZ-PER-RE" = "Azione / IV", "IV-CR" = "Azione / IV")
de$party <- grp[de$gruppo]
de <- de[!is.na(de$party) & de$collegio_plurinominale != "", ]
el$share <- el$elettori / ave(el$elettori, el$collegio_plurinominale, FUN = sum)
de$n <- 1
ndep <- aggregate(n ~ party + collegio_plurinominale, data = de, FUN = sum)
mp <- merge(el, ndep, by = "collegio_plurinominale")
mp <- aggregate(cbind(mp = n * share) ~ provincia + party, data = mp, FUN = sum)

# build_panel(): keep = logical vector selecting the amendments that count as requests
build_panel <- function(keep = rep(TRUE, nrow(am))) {
  a <- am[keep & am$gruppo %in% parties & am$province != "", ]
  # one row per amendment x named province (a proposal naming 3 provinces counts once for each)
  pl <- strsplit(a$province, "; ")
  long <- data.frame(p = unlist(pl), g = rep(a$gruppo, lengths(pl)), y = rep(a$manovra, lengths(pl)),
                     app = rep(a$esito == "Approvato", lengths(pl)), id = rep(paste(a$manovra, a$ramo, a$emendamento), lengths(pl)))
  long <- unique(long)
  long$n <- 1; long$nA <- as.integer(long$app)
  cnt  <- aggregate(cbind(n, nA) ~ p + g + y, data = long, FUN = sum)
  d <- expand.grid(p = vo$provincia, g = parties, y = years, stringsAsFactors = FALSE)
  d <- merge(d, cnt, all.x = TRUE); d$n[is.na(d$n)] <- 0; d$nA[is.na(d$nA)] <- 0
  d <- merge(d, vo[, c("provincia", "regione", "popolazione_2025")], by.x = "p", by.y = "provincia")
  d$reg   <- d$regione
  v <- vo[match(d$p, vo$provincia), ]
  vm <- as.matrix(v[, vote_col]); d$share <- vm[cbind(seq_len(nrow(d)), match(d$g, names(vote_col)))] / v$voti_tot * 100
  d$s     <- d$share / 10                          # vote share in units of 10 points
  d$any   <- as.integer(d$n > 0)                   # at least one local request
  d$anyA  <- as.integer(d$nA > 0)                  # at least one approved local request
  d$ihs   <- asinh(d$n / d$popolazione_2025 * 1e5) # requests per 100,000 residents (asinh)
  d$lpop  <- log(d$popolazione_2025)
  d$gy <- paste(d$g, d$y); d$gr <- paste(d$g, d$reg); d$py <- paste(d$p, d$y)
  cdx <- (v$voti_FdI + v$voti_Lega + v$voti_FI + v$voti_NM) / v$voti_tot * 100
  csx <- (v$voti_PD + v$voti_AVS + v$voti_PiuE) / v$voti_tot * 100
  d$marg  <- abs(cdx - csx)
  d$maj   <- as.integer(d$g %in% majority)
  d$metro <- as.integer(d$p %in% c("Roma", "Milano", "Napoli", "Torino"))
  m <- mp[match(paste(d$p, d$g), paste(mp$provincia, mp$party)), "mp"]; d$mp <- ifelse(is.na(m), 0, m)
  d[order(d$y, d$g, d$p), ]
}
D <- build_panel()
cat("Panel:", nrow(D), "observations,", length(unique(D$p)), "provinces\n")   # 4,360 and 109
write.csv(D, "output/panel.csv", row.names = FALSE)

# helper: OLS with standard errors clustered by province (CR1, as in Stata)
ols <- function(f, d, var = "s", cl = "p") {
  m <- lm(f, data = d)
  V <- vcovCL(m, cluster = d[[cl]], type = "HC1")
  c(b = unname(coef(m)[var]) * 100, se = sqrt(V[var, var]) * 100, n = nobs(m))
}
stars <- function(b, se) { z <- abs(b / se); ifelse(z > 3.29, "***", ifelse(z > 2.58, "**", ifelse(z > 1.96, "*", ""))) }
show <- function(x, digits = 2) sprintf(paste0("%.", digits, "f%s (%.", digits, "f)"), x["b"], stars(x["b"], x["se"]), x["se"])
