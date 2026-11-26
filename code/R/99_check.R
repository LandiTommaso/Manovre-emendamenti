# ---------------------------------------------------------------------
# 99. Check: R results vs the numbers printed in the paper
# ---------------------------------------------------------------------
target <- read.csv("code/paper_numbers.csv", stringsAsFactors = FALSE)
got <- c(T2_c1 = T2$c1["b"], T2_c2 = T2$c2["b"], T2_c3 = T2$c3["b"], T2_c6 = T2$c6["b"], T2_c7 = T2$c7["b"],
         T2_c2_se = T2$c2["se"], T2_c3_se = T2$c3["se"], T3_c1 = T3$c1["b"], T3_c5_s = T3$c5["s", "b"], T3_c5_mp = T3$c5["mp", "b"])
names(got) <- sub("\\.(b|se)$", "", names(got))
cmp <- data.frame(stat = target$stat, paper = target$value, R = round(got[target$stat], 3))
cmp$ok <- abs(cmp$paper - cmp$R) < 0.01
print(cmp)
if (all(cmp$ok)) cat("\nAll checked numbers match the paper.\n") else cat("\nSOME NUMBERS DIFFER: see table above.\n")
