# Research run robustness-20260930-unweighted_training

Experiment: E4. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

Legacy manifest: scientific files are hash-verified; the original REPORT.md was not covered by the run manifest. This report is newly derived from verified scientific files.

## Weighted average of within-fold metrics

| block | model | auc | auc_valid | auc_expected | brier | brier_valid | brier_expected | average_precision | average_precision_valid | average_precision_expected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B3 | logistic | 0.75264 | 5 | 5 | 0.17523 | 5 | 5 | 0.5318 | 5 | 5 |
| B3 | xgboost | 0.75483 | 5 | 5 | 0.17459 | 5 | 5 | 0.53642 | 5 | 5 |

Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.

## Primary-capacity expenditure summaries

| seed | block | model | capacity | mean | sd | cv | zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | B3 | logistic | 0.30006 | 3248 | 9933.9 | 3.0585 | 0.25757 |
| 42 | B3 | xgboost | 0.29981 | 3330.5 | 10476 | 3.1455 | 0.26307 |
| 42 | random | random | 0.30016 | 8778.7 | 22749 | 2.5913 | 0.11829 |

Random comparator: one deterministic seeded ranking with the same within-fold capacity rule; not an average over random policies.

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `e312023838e12a730d0daf3efff59fec13729567ac7548219323a8744dfa9ea8`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
