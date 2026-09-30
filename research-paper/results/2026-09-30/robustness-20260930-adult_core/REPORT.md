# Research run robustness-20260930-adult_core

Experiment: E4. Population: adult_core.

Analytic records: 14,907; weight sum: 262,219,405.46.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

## Weighted average of within-fold metrics

| block | model | auc | brier | average_precision |
| --- | --- | --- | --- | --- |
| B3 | logistic | 0.74922 | 0.17561 | 0.52477 |
| B3 | xgboost | 0.74518 | 0.17646 | 0.52148 |

Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.

## Primary-capacity expenditure summaries

| seed | block | model | capacity | mean | sd | cv | zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | B3 | logistic | 0.30022 | 3207.9 | 11308 | 3.525 | 0.29914 |
| 42 | B3 | xgboost | 0.30006 | 3086.2 | 10536 | 3.414 | 0.2985 |

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `b3557c4a647c8214fcabb0abf952a619ccde3261d3f4a3576643f31dcf4f85fc`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
