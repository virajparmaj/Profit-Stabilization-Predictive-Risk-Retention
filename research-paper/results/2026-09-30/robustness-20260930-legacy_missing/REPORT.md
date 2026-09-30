# Research run robustness-20260930-legacy_missing

Experiment: E4. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

## Weighted average of within-fold metrics

| block | model | auc | brier | average_precision |
| --- | --- | --- | --- | --- |
| B3 | logistic | 0.75253 | 0.17453 | 0.53122 |
| B3 | xgboost | 0.74508 | 0.17759 | 0.52772 |

Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.

## Primary-capacity expenditure summaries

| seed | block | model | capacity | mean | sd | cv | zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | B3 | logistic | 0.29996 | 3192.1 | 10137 | 3.1757 | 0.25541 |
| 42 | B3 | xgboost | 0.29991 | 3346.4 | 10632 | 3.177 | 0.2575 |

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `a5966be4b792eb8120dd6c3e4eb0fe7f96b78f31b630cccd0a294788078e9b19`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
