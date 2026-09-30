# Research run primary-e1-20260930

Experiment: E1. Population: adult_saq.

Analytic records: 9,776; weight sum: 258,426,861.98.

Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.

## Weighted average of within-fold metrics

| block | model | auc | brier | average_precision |
| --- | --- | --- | --- | --- |
| B0 | logistic | 0.53359 | 0.20682 | 0.31861 |
| B0 | xgboost | 0.5397 | 0.20665 | 0.32158 |
| B2 | logistic | 0.65527 | 0.19483 | 0.41791 |
| B2 | xgboost | 0.66084 | 0.19697 | 0.424 |
| B3 | logistic | 0.75277 | 0.17477 | 0.5285 |
| B3 | xgboost | 0.74833 | 0.17675 | 0.5265 |
| B4 | logistic | 0.79048 | 0.16183 | 0.60808 |
| B4 | xgboost | 0.78141 | 0.16681 | 0.59749 |
| B5 | logistic | 0.93927 | 0.089956 | 0.83133 |
| B5 | xgboost | 0.93755 | 0.093641 | 0.83571 |
| C | logistic | 0.76307 | 0.17145 | 0.54303 |
| C | xgboost | 0.74053 | 0.17932 | 0.50623 |
| D | logistic | 0.7072 | 0.18513 | 0.47892 |
| D | xgboost | 0.68922 | 0.19085 | 0.4439 |

Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.

## Primary-capacity expenditure summaries

| seed | block | model | capacity | mean | sd | cv | zero_share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42 | B0 | logistic | 0.30021 | 8209 | 20265 | 2.4687 | 0.13281 |
| 42 | B0 | xgboost | 0.30005 | 7732.4 | 19233 | 2.4873 | 0.13033 |
| 42 | B2 | logistic | 0.30002 | 4757.8 | 13437 | 2.8243 | 0.17929 |
| 42 | B2 | xgboost | 0.30031 | 4722.2 | 13316 | 2.8199 | 0.19864 |
| 42 | B3 | logistic | 0.30002 | 3132.5 | 9854.8 | 3.146 | 0.25636 |
| 42 | B3 | xgboost | 0.29984 | 3555.2 | 11130 | 3.1308 | 0.25605 |
| 42 | B4 | logistic | 0.29985 | 2784.3 | 9708.8 | 3.487 | 0.28238 |
| 42 | B4 | xgboost | 0.29995 | 2877.1 | 9048.5 | 3.145 | 0.27182 |
| 42 | B5 | logistic | 0.29982 | 739.8 | 2327.9 | 3.1467 | 0.3879 |
| 42 | B5 | xgboost | 0.30001 | 768.53 | 2502.6 | 3.2564 | 0.38666 |
| 42 | C | logistic | 0.2998 | 2715.5 | 9135.5 | 3.3642 | 0.24871 |
| 42 | C | xgboost | 0.30017 | 3221.5 | 10362 | 3.2165 | 0.23954 |
| 42 | D | logistic | 0.29972 | 3735.3 | 12535 | 3.3558 | 0.21942 |
| 42 | D | xgboost | 0.29962 | 4386.1 | 14611 | 3.3312 | 0.2139 |
| 2026 | B0 | logistic | 0.29953 | 8341.6 | 21671 | 2.598 | 0.13006 |
| 2026 | B0 | xgboost | 0.29984 | 7806.3 | 20515 | 2.628 | 0.12953 |
| 2026 | B2 | logistic | 0.29998 | 4875.1 | 13873 | 2.8456 | 0.17786 |
| 2026 | B2 | xgboost | 0.29995 | 4742.1 | 13760 | 2.9017 | 0.19603 |
| 2026 | B3 | logistic | 0.30011 | 3151.3 | 9832 | 3.1199 | 0.25515 |
| 2026 | B3 | xgboost | 0.30062 | 3537.7 | 11572 | 3.271 | 0.25363 |
| 2026 | B4 | logistic | 0.29998 | 2858.1 | 10050 | 3.5164 | 0.28004 |
| 2026 | B4 | xgboost | 0.29996 | 2792.5 | 9112.1 | 3.2631 | 0.28144 |
| 2026 | B5 | logistic | 0.29979 | 731.29 | 2271.3 | 3.1059 | 0.38538 |
| 2026 | B5 | xgboost | 0.30008 | 784.05 | 2613.4 | 3.3332 | 0.38723 |
| 2026 | C | logistic | 0.29974 | 2691.3 | 9210.3 | 3.4223 | 0.24859 |
| 2026 | C | xgboost | 0.3 | 3380.8 | 11102 | 3.2838 | 0.23414 |
| 2026 | D | logistic | 0.29994 | 3622.2 | 12353 | 3.4103 | 0.21831 |
| 2026 | D | xgboost | 0.3002 | 4402.4 | 13766 | 3.127 | 0.20546 |

## B3 logistic minus XGBoost

| metric | estimate | se | low | high |
| --- | --- | --- | --- | --- |
| auc | 0.0044337 | 0.0038983 | -0.0032068 | 0.012074 |
| brier | -0.0019798 | 0.0013918 | -0.0047077 | 0.00074819 |
| mean | -404.54 | 237.03 | -869.11 | 60.028 |
| sd | -1507.8 | 1155.3 | -3772 | 756.52 |
| cv | -0.067907 | 0.18378 | -0.42811 | 0.2923 |
| mean_excess | -279.25 | 178.43 | -628.97 | 70.469 |

Intervals condition on fitted predictions and grouped folds; learning variation is separate.

## Provenance

Input SHA-256: `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26`.

Protocol/config SHA-256: `25483a230e35c792a0115a62da5574116e20fd46f9f862b98ce28257933d07cf`.

Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.
