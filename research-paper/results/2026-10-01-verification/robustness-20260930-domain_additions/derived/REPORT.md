# Research run robustness-20260930-domain_additions

Experiment: E4. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

Legacy manifest: scientific files are hash-verified; the original REPORT.md was not covered by the run manifest. This report is newly derived from verified scientific files.

## Weighted average of within-fold metrics

| block | model | auc | auc_valid | auc_expected | brier | brier_valid | brier_expected | average_precision | average_precision_valid | average_precision_expected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B3_INS | logistic | 0.78098 | 5 | 5 | 0.16461 | 5 | 5 | 0.59629 | 5 | 5 |
| B3_INS | xgboost | 0.77455 | 5 | 5 | 0.16791 | 5 | 5 | 0.58658 | 5 | 5 |
| B3_SES | logistic | 0.77501 | 5 | 5 | 0.16756 | 5 | 5 | 0.56909 | 5 | 5 |
| B3_SES | xgboost | 0.77069 | 5 | 5 | 0.17109 | 5 | 5 | 0.5586 | 5 | 5 |
| B3_UTIL | logistic | 0.9399 | 5 | 5 | 0.090065 | 5 | 5 | 0.83669 | 5 | 5 |
| B3_UTIL | xgboost | 0.93528 | 5 | 5 | 0.094772 | 5 | 5 | 0.83226 | 5 | 5 |

Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.

## Primary-capacity expenditure summaries

| seed | block | model | capacity | mean | sd | cv | zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | B3_INS | logistic | 0.29994 | 2960.8 | 9962.8 | 3.3649 | 0.27313 |
| 42 | B3_INS | xgboost | 0.29994 | 2978.6 | 10479 | 3.518 | 0.27149 |
| 42 | B3_SES | logistic | 0.30005 | 2863.8 | 9696.4 | 3.3859 | 0.27168 |
| 42 | B3_SES | xgboost | 0.29987 | 3192.4 | 10853 | 3.3996 | 0.26719 |
| 42 | B3_UTIL | logistic | 0.2999 | 751.61 | 2380.4 | 3.167 | 0.38839 |
| 42 | B3_UTIL | xgboost | 0.3 | 904.86 | 4917.2 | 5.4342 | 0.38731 |
| 42 | random | random | 0.30016 | 8778.7 | 22749 | 2.5913 | 0.11829 |

Random comparator: one deterministic seeded ranking with the same within-fold capacity rule; not an average over random policies.

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `ad933012c9ab7d62ac1ace5cd52c2051625eb4d9eb981382724816404feaa90e`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
