# Existing findings and their interpretation

> **Implementation update — 2026-09-30:** The original plan/evidence below is retained as a dated baseline. The corrected core pipeline and actual E1–E4 execution status are documented in [Implementation and results](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/17_IMPLEMENTATION_AND_RESULTS.md). Remaining paper requirements and protocol deviations are listed there; the study is not submission-complete.

**Updated:** 2026-09-25. **Status:** Recomputed descriptions and cached-score evaluation, with saved notebook evidence labeled separately.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

### The most important numerical reinterpretation

These are weighted descriptions of groups selected using the cached scores and the existing **unweighted** rank cutoffs. They are not corrected-model study results.

| Metric | Full positive-weight sample | Highest P(low-label), nominal 30% | Nominal 10% |
|---|---:|---:|---:|
| Records | 18,463 | 5,548 | 1,891 |
| Mean annual spending | $7,487.26 | $2,778.55 | $2,186.53 |
| Spending SD | $19,807.63 | $9,993.32 | $8,250.17 |
| Coefficient of variation, SD/mean | 2.646 | 3.597 | 3.773 |
| Zero-spending share | 14.45% | 27.61% | 40.66% |
| CV among positive spenders only | 2.417 | 3.015 | 2.836 |
| Spending >= $20,000 | 9.10% | 2.90% | 2.27% |
| Mean excess above $20,000, E[(C−20k)+] | $2,891.73 | $697.77 | $609.08 |
| Excess above $20,000 / all spending | 38.62% | 25.11% | 27.86% |
| All spending of people spending >= $20,000 / all spending | 62.93% | 46.02% | 48.62% |

Selection reduces the mean by about 63%, the SD by about 50%, and absolute expected excess above $20,000 by about 76%. Therefore, **“selection does not reduce cost variance” is contradicted by the existing data**. Higher CV and Gini do not imply larger dollar variance, a heavier asymptotic tail, greater ruin probability, or lower profits. Even the relative excess-above-$20k share falls versus the population. Each metric answers a different question.

The nominal 30% group represents **33.45% of population weight**, not 30%. The nominal 10% group represents approximately **11.09%**. Ties also make record counts exceed the exact requested fractions. Capacity must be defined explicitly before comparing policies.

## 6. Hidden observations worth preserving

**The strongest existing clue is the divergence among evaluation targets.** The cached model lowers dollar SD while increasing CV, and the notebook's near-fixed headcount does not test membership at all. The research question is whether these distinctions change which compact model or policy one would choose. The local code bug is motivation for the audit, not the paper's entire contribution.

**Logistic is competitive with XGBoost.** Its B3 AUROC is higher by about 0.0018 and Brier lower by about 0.0005 in the saved split. This is too small and uncertain for a superiority claim but makes a simple baseline indispensable. The original averaged-across-blocks leaderboard obscures this point.

**Population weighting affects apparent performance.** The same cached probabilities give 0.772 unweighted and 0.747 person-weighted AUROC. This does not prove a statistically significant gap, but it is enough to require explicit estimands and a weighted analysis in a nationally framed study.

**Correcting burden definitions changes the group you are talking about.** As a limited sensitivity analysis, I removed `ANYLMI23` and `COVIDEVER53` from the original count, retaining the original yes/no mapping for the remaining ten indicators. The 3+-indicator/zero-office group shrank from 545 records (9.21M weighted people) to **315 records (4.83M)**. Its spending >=$20k rate rose from **8.36% to 13.69%**, acute spending share from **53.80% to 61.07%**, and low-label share fell from **52.03% to 45.12%**. These are new exploratory descriptions, with no survey-adjusted intervals or clinical validation; they demonstrate sensitivity, not a corrected final result.

The uninsured-versus-insured contrast within 2+ indicators persisted under that limited count sensitivity: **58.37% versus 8.78%** had the low label, versus 63.08%/12.39% originally. This merits follow-up, but it remains an unadjusted broad-stratum comparison with 168 uninsured records under the ten-item definition.

**Zero mass is part of the selected-pool story.** It nearly doubles in the 30% group and increases further at 10%. The positive-spender CV pattern changes under tighter selection, so “the remaining tail gets steadily worse” is an inadequate explanation.

**The report contains post hoc subgroup discovery.** Scripts such as `a04_segscan.py` and selected pair comparisons are useful exploration. A small-cell narrative found after scanning many groups cannot be promoted to confirmatory evidence using ordinary intervals alone. Register exact contrasts now and test them on another year if they become central.
