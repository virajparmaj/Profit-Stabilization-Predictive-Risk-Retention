# Research run robustness-20260930-legacy_label

Experiment: E4. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

Legacy manifest: scientific files are hash-verified; the original REPORT.md was not covered by the run manifest. This report is newly derived from verified scientific files.

## Weighted average of within-fold metrics

| block | model | auc | auc_valid | auc_expected | brier | brier_valid | brier_expected | average_precision | average_precision_valid | average_precision_expected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B3 | logistic | 0.75653 | 5 | 5 | 0.15897 | 5 | 5 | 0.48231 | 5 | 5 |
| B3 | xgboost | 0.75358 | 5 | 5 | 0.16071 | 5 | 5 | 0.47978 | 5 | 5 |

Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.

## Primary-capacity expenditure summaries

| seed | block | model | capacity | mean | sd | cv | zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | B3 | logistic | 0.29982 | 3266.6 | 10724 | 3.2829 | 0.25796 |
| 42 | B3 | xgboost | 0.30023 | 3413.2 | 10151 | 2.974 | 0.25368 |
| 42 | random | random | 0.30016 | 8778.7 | 22749 | 2.5913 | 0.11829 |

Random comparator: one deterministic seeded ranking with the same within-fold capacity rule; not an average over random policies.

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `dc473faef41f33c62c4141125756bbbe7165a61fbff0da3fe16f7f242a253fba`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
