# Research run robustness-20260930-reference

Experiment: E4. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

## Weighted average of within-fold metrics

| block | model | auc | brier | average_precision |
| --- | --- | --- | --- | --- |
| B3 | logistic | 0.75194 | 0.17475 | 0.52927 |
| B3 | xgboost | 0.74728 | 0.17695 | 0.52789 |

Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.

## Primary-capacity expenditure summaries

| seed | block | model | capacity | mean | sd | cv | zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | B3 | logistic | 0.30002 | 3132.5 | 9854.8 | 3.146 | 0.25636 |
| 42 | B3 | xgboost | 0.29984 | 3555.2 | 11130 | 3.1308 | 0.25605 |

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `917fc8f201cd25153b0b5fd649b469856220c8dada6cd63377f8d0043ccde599`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
