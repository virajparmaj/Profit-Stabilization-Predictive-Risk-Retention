# Research run primary-e2-20260930

Experiment: E2. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

## Refit sensitivity

| block | model | policy | auc_mean | jaccard_mean | population_disagreement_mean | capacity_mean |
| --- | --- | --- | --- | --- | --- | --- |
| B2 | logistic | fixed_threshold | 0.63585 | 0.72154 | 0.11254 | 0.3646 |
| B2 | logistic | weighted_capacity | 0.63585 | 0.80437 | 0.065534 | 0.30001 |
| B3 | logistic | fixed_threshold | 0.73506 | 0.79193 | 0.067257 | 0.2884 |
| B3 | logistic | weighted_capacity | 0.73506 | 0.81524 | 0.061539 | 0.30004 |
| B3 | xgboost | fixed_threshold | 0.7267 | 0.70176 | 0.10639 | 0.30267 |
| B3 | xgboost | weighted_capacity | 0.7267 | 0.70216 | 0.10538 | 0.3 |
| B4 | xgboost | fixed_threshold | 0.7662 | 0.66095 | 0.11722 | 0.28034 |
| B4 | xgboost | weighted_capacity | 0.7662 | 0.67282 | 0.11746 | 0.30003 |

Mean/SD across training refits describe learning sensitivity, not confidence intervals from independent patients.

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `25483a230e35c792a0115a62da5574116e20fd46f9f862b98ce28257933d07cf`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
