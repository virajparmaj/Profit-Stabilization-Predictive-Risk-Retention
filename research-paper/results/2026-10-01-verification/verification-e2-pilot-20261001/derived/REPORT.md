# Research run verification-e2-pilot-20261001

Experiment: E2. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

**PILOT / feasibility only: not final research evidence.**

## Refit sensitivity

| block | model | policy | auc_mean | jaccard_mean | population_disagreement_mean | capacity_mean | auc_valid | auc_expected | jaccard_valid | jaccard_expected | population_disagreement_valid | population_disagreement_expected | baseline_member_loss_valid | baseline_member_loss_expected | probability_mad_valid | probability_mad_expected | mean_valid | mean_expected | sd_valid | sd_expected | cv_valid | cv_expected | capacity_valid | capacity_expected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2 | logistic | fixed_threshold | 0.63968 | 0.68081 | 0.13541 | 0.39038 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| B2 | logistic | weighted_capacity | 0.63968 | 0.80348 | 0.066246 | 0.3 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| B3 | logistic | fixed_threshold | 0.73769 | 0.8091 | 0.062143 | 0.29724 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| B3 | logistic | weighted_capacity | 0.73769 | 0.82251 | 0.058898 | 0.3 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| B3 | xgboost | fixed_threshold | 0.72888 | 0.70596 | 0.10566 | 0.30735 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| B3 | xgboost | weighted_capacity | 0.72888 | 0.7081 | 0.10298 | 0.30005 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| B4 | xgboost | fixed_threshold | 0.76688 | 0.66137 | 0.1182 | 0.28556 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| B4 | xgboost | weighted_capacity | 0.76688 | 0.66782 | 0.11961 | 0.30005 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |

Mean/SD across training refits describe learning sensitivity, not confidence intervals from independent patients.

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `eac98fb96c5f61b106565a17f1996f7ed8e2237f080cea6f581fdfa9c9ae673d`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
