# Research run robustness-20260930-legacy_count

Experiment: E4. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

## Weighted average of within-fold metrics

| block | model | auc | brier | average_precision |
| --- | --- | --- | --- | --- |
| B3 | logistic | 0.75533 | 0.17344 | 0.5386 |
| B3 | xgboost | 0.74873 | 0.17659 | 0.53606 |

Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.

## Primary-capacity expenditure summaries

| seed | block | model | capacity | mean | sd | cv | zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | B3 | logistic | 0.30011 | 3031.2 | 9639.7 | 3.1802 | 0.25298 |
| 42 | B3 | xgboost | 0.30038 | 3269.7 | 10117 | 3.0941 | 0.25854 |

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `b81b9aac8d4f46efe6c1d06277f6e5280c03495f9b5cc038cbed412ca43213ec`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
