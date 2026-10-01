# Implemented research extension and actual findings

**Date:** 2026-09-30. **Branch:** `viraj/research`. **Status:** executable core study and exploratory results; remaining paper-readiness requirements explicitly listed.

**Verification update (2026-10-01):** [Verification report](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/19_VERIFICATION_AND_PR_READINESS.md) documents stronger manifest/report integrity, conservative missing-metric aggregation, durable fit diagnostics, the random comparator and exact targeted reruns. The original results below remain unchanged; current derived figures and reports are in `results/2026-10-01-verification/`.

## What changed

The project now has a source-driven research package, not just an implementation plan. It reconstructs the adult SAQ cohort, corrects the diagnosis/function overlap, preserves missing-code meanings and income losses, splits by documented dwelling units, fits preprocessing inside training samples, and evaluates high-probability low-spending selection at explicit weighted capacity. The original notebooks, data and cached evidence remain preserved.

The package implements E1 classification comparisons, E2 full-pipeline refitting, E3 spending evaluation within those runs, and a declared E4 sensitivity runner. E0's data reconstruction and legacy-label checks are complete; exact historical model reproduction remains separate. A reusable implementation prompt is in `16_IMPLEMENTATION_PROMPT.md`.

## What actually ran

| Work | Completed evidence |
|---|---|
| Corrected cohort | 9,776 SAQ respondents; 6,807 dwelling units; 105 variance strata and 262 PSUs |
| Independent survey check | Python mean/SE matched R survey 4.5: $8,947.954861 / $275.828695 |
| E1 | 7 blocks × 2 models × 5 grouped folds × 2 seeds = 140 source-trained fits |
| E1 conditional inference | 1,000 shared Rao–Wu PSU replicates; primary B3 logistic-minus-XGBoost contrast |
| E2 pilot | 20 refits × 4 anchors = 80 fits; no failures |
| E2 main | 200 refits × 4 anchors = 800 fits, plus four original fits; no failures or estimator warnings |
| E4 | 7 declared variants, 90 source-trained fits; all completed |
| Automated tests | 23 tests passed, including reference-outcome independence, failure recording and local HC-251/R benchmark |
| Figures | Expenditure frontier, membership-versus-accuracy plot and descriptive calibration plot regenerated |

Full E1 took about 358 seconds and full E2 about 479 seconds in the local recorded environment. Concurrent work affected timing; these are observed runs, not portable performance benchmarks. The environment is isolated and pinned. Platform cache-probing messages from Arrow/fontconfig did not prevent completion; model fit diagnostics recorded no estimator warnings in the primary runs.

## Primary empirical finding

**Similar discrimination coexists with materially different membership reproducibility in this internal experiment.** B3 logistic achieved weighted AUROC 0.75277 versus 0.74833 for XGBoost. The paired conditional difference was 0.00443, with a 95% interval [-0.00321, 0.01207]. This does not establish an accuracy winner or prove noninferiority.

Across 200 training refits at 30% weighted capacity, B3 logistic averaged **6.15% population membership disagreement** with its original fit, compared with **10.54%** for B3 XGBoost. Weighted Jaccard overlap averaged **0.8152** and **0.7022**, respectively. The paired mean disagreement difference was **−4.38 percentage points**, with a Monte Carlo SE of approximately **0.15 percentage points**. Its 2.5th–97.5th refit percentiles were approximately **−8.36 to −0.21 percentage points**.

These are distributions across paired training resamples on a fixed reference set, **not population confidence intervals**. Disagreement uses the entire weighted reference population as its denominator; it is not the percentage of selected members lost. Those are separate exported metrics.

| block | model | mean_Jaccard | mean_disagreement | achieved_capacity |
| --- | --- | --- | --- | --- |
| B2 | logistic | 0.80437 | 0.065534 | 0.30001 |
| B3 | logistic | 0.81524 | 0.061539 | 0.30004 |
| B3 | xgboost | 0.70216 | 0.10538 | 0.3 |
| B4 | xgboost | 0.67282 | 0.11746 | 0.30003 |

B4 XGBoost improves reference-set discrimination over B3 XGBoost but also has higher average disagreement. That is a model/feature tradeoff worth studying. It does not establish B3 as the minimum sufficient model, particularly because B4 logistic was not an E2 anchor and the C demographic/diagnosis/function baseline also performs well in E1.

![Membership and accuracy](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/results/2026-09-30/figures/membership_vs_accuracy.png)

## Classification results

| block | model | weighted_AUROC | weighted_Brier |
| --- | --- | --- | --- |
| B0 | logistic | 0.53359 | 0.20682 |
| B0 | xgboost | 0.5397 | 0.20665 |
| B2 | logistic | 0.65527 | 0.19483 |
| B2 | xgboost | 0.66084 | 0.19697 |
| B3 | logistic | 0.75277 | 0.17477 |
| B3 | xgboost | 0.74833 | 0.17675 |
| B4 | logistic | 0.79048 | 0.16183 |
| B4 | xgboost | 0.78141 | 0.16681 |
| B5 | logistic | 0.93927 | 0.089956 |
| B5 | xgboost | 0.93755 | 0.093641 |
| C | logistic | 0.76307 | 0.17145 |
| C | xgboost | 0.74053 | 0.17932 |
| D | logistic | 0.7072 | 0.18513 |
| D | xgboost | 0.68922 | 0.19085 |

Metrics average within-fold evaluations using test weight mass. The endpoint cutoff is estimated on each training fold. Scores targeting different fold-specific cutoffs are not pooled into a single AUROC. Repeated folds/seeds are not independent clinical samples. The C logistic baseline reaches AUROC 0.76307, so a special advantage of the original B3 ladder is not established.

The primary logistic-minus-XGBoost Brier difference was -0.00198, with conditional interval [-0.00471, 0.00075]. Model-comparison intervals condition on fixed predictions and splits; they do not encompass all learning uncertainty.

## Absolute versus relative expenditure

The corrected adult population has mean expenditure **$8,947.95**, SD **$21,778.33**, and CV **2.434**. B3 selected-cohort summaries below average the two outer-split seeds at roughly 30% weighted capacity:

| model | mean | sd | cv | zero_share | positive_cv |
| --- | --- | --- | --- | --- | --- |
| logistic | 3141.9 | 9843.4 | 3.133 | 0.25576 | 2.6551 |
| xgboost | 3546.5 | 11351 | 3.2009 | 0.25484 | 2.7166 |

Both B3 policies reduce absolute spending level and SD relative to the population, while CV increases. For logistic, mean expenditure is about $3,142, SD $9,843 and CV 3.13. Higher relative dispersion does not imply larger dollar variance, a worse insurer balance sheet or a clinical risk increase.

The between-model selected-mean difference is about −$405 (logistic minus XGBoost); its conditional interval spans approximately −$869 to $60. The SD, CV and excess-spending contrast intervals also include zero. Therefore, the current evidence is stronger for a descriptive membership-reproducibility difference than for asserting a superior expenditure policy.

The figure export computes `CV_at_population_zero_mass = sqrt((CV_positive² + 1 − p_population) / p_population)` separately per seed before averaging. This is a descriptive standardization using an established identity, not a new method or a causal decomposition. See `figures/spending_and_zero_mass.csv` for the exact results.

![Expenditure frontier](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/results/2026-09-30/figures/expenditure_frontier.png)

## Robustness results and limits

All seven prespecified E4 variants completed: reference, legacy burden, partial legacy missingness encoding, legacy $484.40 label, unweighted training, adult core population and separate insurance/SES/utilization additions. The adult-core version removes K6/PHQ SAQ features and changes the target population and weights; it is not a like-for-like perturbation of identical people.

The unweighted-training sensitivity reverses the small B3 accuracy ordering: XGBoost has an AUROC point estimate around 0.755 versus 0.753 for logistic. Both are still evaluated with population weights. This warns against claiming universal logistic superiority. Insurance, SES and utilization additions improve same-year discrimination, with utilization adding the most; that does not imply prospective forecasting value.

The partial legacy-missingness variant collapses unknown counts and numeric missing values toward zero and categorical reserved codes into a common category. Numeric missing-reason fields remain available. It is a declared sensitivity, not an exact reconstruction of the historical full-sample imputation pipeline. The historical notebook was not silently repaired and replayed.

E4 results currently describe discrimination and expenditure sensitivity. They do not rerun E2 under every variant or supply multiplicity-adjusted inference for every secondary contrast. `robustness_comparison.csv` contains all variants, including unfavorable results.

## What this supports as modest novelty

The defensible empirical story is: **for a corrected MEPS low-spending target, familiar classifiers with similar aggregate discrimination can differ substantially in reproducibility of selected identities, while additional features and expenditure metrics introduce separate tradeoffs.** The source-built evaluation makes those differences measurable and reproducible.

Prediction instability, proxy labels and the distinction between absolute and relative variability are already established in prior research. This work does not invent those concepts. Its possible contribution is the bounded empirical comparison and decision consequence. Independent replication and stronger reference-population uncertainty are still needed before treating this as a finished generalizable research finding.

## Remaining requirements before paper submission

1. Replicate the primary contrast on a frozen nonoverlapping year/sample (E5), with harmonized variables and overlap checks.
2. Add the direct-expenditure/two-part baseline and broader model comparison (E6). RF support exists in the model factory but was not part of the primary runs.
3. Quantify population uncertainty for membership results while distinguishing training and reference-sample variation; extend joint or nested design-aware uncertainty as justified.
4. Complete prespecified secondary paired contrasts/multiplicity, tail-threshold sensitivity, outlier influence, and robustness of the central E2 result itself.
5. Complete exact historical model reproduction if reporting that comparison; resolve package-version changes rather than forcing identical outputs.
6. Finalize the complete codebook dictionary and literature review around the final claim. Feature metadata currently documents source variables, coding and broad timing, not every full questionnaire item.
7. Perform E7 with longitudinal data before making any prospective claim. It is outside the present same-year study.

## Reproducibility and evidence

Aggregate results are committed under `research-paper/results/2026-09-30/`. Individual records, scores, memberships and split IDs stay in ignored `analysis/research_runs/` directories. Run manifests include raw-data, configuration, source-code and output hashes, Git state and package versions. Reports can be regenerated only from complete, hash-consistent local runs.

The exact code hashes record the state at run start. The primary E1 run preceded a dictionary-only change that added correct source metadata for the legacy12 sensitivity, and the corresponding CLI argument; its scientific computation was unaffected. Later report/export/formatting changes do not rewrite those manifests. The final validation report records any additional changes separately.

Original data and notebooks were not changed. The main README now describes the verified study and removes unsupported deployment, minimum-stable-model and financial-benefit assertions.
