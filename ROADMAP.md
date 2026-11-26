# Research roadmap (private)

These are ideas for extending the project after the 2027 general election and before submission to a journal. None of them has been started.

## 1. Complete the 2027 budget
- Add the committee votes on the 2027 budget in the Chamber and the Senate's second reading once they are published.
- Re-estimate every model with the final 2027 outcomes.

## 2. Earlier legislatures
- Extend the dataset backwards to the XVIII (2018–2022), XVII (2013–2018) and XVI (2008–2013) legislatures. Go further back where the files exist.
- **First, check which years have amendment files in machine-readable form.** Older budget sessions may survive only as scanned bulletins.
- Match each legislature to its own election results and constituency maps. The electoral system changed in 2005 and 2017, and the number of seats was cut in 2020, so the constituencies change from one period to the next.

## 3. Do amendments pay off at the next election?
- **Question:** is tabling, or obtaining, local money associated with a legislator's re-election, or with the party's change in vote share in that province?
- **Unit:** legislator × election, or party × province × election.
- **Outcomes:** whether the legislator is re-nominated or re-elected, and the change in the party's vote share.
- **Prediction (machine learning):** predict these outcomes from amendment features, for example with gradient boosting or a regularised logit. Validate with backtests that train on earlier legislatures and test on the next one, never on the same legislature.
- **Caveats:**
  - Elections are about five years apart, so there are few out-of-sample tests.
  - Parties decide re-nomination, so it is endogenous.
  - A good prediction is not a causal effect.
- **Cleaner causal designs:** close races in single-member districts, or the timing of scheduled municipal elections.

## 4. Other extensions
- Attribute senators and deputies elected in single-member districts to provinces, and add each legislator's birthplace and residence.
- Link approved amendments to the financial effects certified by the parliamentary budget services.
- Measure template amendments, where several parties sign the same text, with text-similarity methods.

## What to study first
- Panel econometrics with high-dimensional fixed effects (the `fixest` package in R).
- Regression discontinuity designs: Cattaneo, Idrobo and Titiunik, *A Practical Introduction to Regression Discontinuity Designs* (Cambridge Elements).
- Prediction and validation: James, Witten, Hastie and Tibshirani, *An Introduction to Statistical Learning*, with applications in R. Pay particular attention to time-ordered cross-validation.
