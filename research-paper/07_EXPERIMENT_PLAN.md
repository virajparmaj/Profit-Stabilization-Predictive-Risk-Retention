# Experiments, outputs and falsification criteria

> **Implementation update — 2026-09-30:** The original plan/evidence below is retained as a dated baseline. The corrected core pipeline and actual E1–E4 execution status are documented in [Implementation and results](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/17_IMPLEMENTATION_AND_RESULTS.md). Remaining paper requirements and protocol deviations are listed there; the study is not submission-complete.

**Updated:** 2026-09-25. **Status:** Proposed experiments E0–E10, not executed results.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

### ESSENTIAL

**E0. Reconstruct the scientific variables and reproduce the original experiment.**

- **Experimental change:** legacy versus corrected burden definitions, missing-code handling, eligible sample and weights. Change one component at a time, then the full corrected specification, so causes of numerical changes remain traceable.
- **Models:** no model for label/count checks; legacy B3 logistic/XGBoost and corrected B3 for scored consequences.
- **Split/sampling:** reproduce original seed/split for provenance; then use the common grouped protocol. Generate scores from source pipelines, not the stale parquet or silent cache reuse.
- **Metrics/tests:** row/ID/label equality and feature-range assertions; counts and weighted prevalence; AUROC/Brier and selected-group changes. Use paired survey intervals for substantive deltas, not significance tests for deterministic data consistency.
- **Table/figure:** flow diagram and data dictionary; legacy-versus-corrected result table with denominators, missingness and file hashes.
- **Claim supported:** the study measures the intended constructs and its results can be regenerated.
- **Weakening result:** the main pattern disappears after correcting variables. Report that correction; do not retain the legacy interpretation as if validated.

**E1. Re-run a compact, paired model/feature comparison.**

- **Experimental change:** D, C, and B0/B2/B3/B4/B5 feature sets, adding domain-level ablations where needed; compare logistic and XGBoost. Retain B1 in a small supplementary ladder if mental-health increment is discussed.
- **Split/sampling:** common five-fold grouped splits × two seeds; within-training preprocessing. Shared test respondents and target thresholds for each paired contrast.
- **Metrics:** weighted AUROC, average precision with prevalence reference, Brier versus intercept-only baseline, calibration intercept/slope and reliability curves; precision and actual weighted capacity at selection. Retain unweighted metrics as a labeled sensitivity.
- **Tests:** paired design-based intervals for metric differences. For RQ7, declare logistic noninferiority only if the lower bound for AUROC(logistic)−AUROC(XGB) exceeds −0.01, with margin justified in advance. Do not infer noninferiority of all metrics from this single test.
- **Outputs:** block-by-model performance/calibration table and curves, including age/sex baseline.
- **Claim supported:** the information-performance tradeoff for this retrospective target.
- **Weakening result:** corrected B3 is clearly inferior or no smaller block meets predefined tolerances. Then “minimum stable B3” must be dropped permanently.

**E2. Measure membership and probability instability under refitting.**

- **Experimental change:** resample training data and **refit the entire pipeline**; compare fixed-capacity versus fixed numerical threshold policies. Include a synthetic control with random rankings whose cohort size is exactly fixed, demonstrating why headcount cannot measure identity stability.
- **Models:** minimum anchor set: B2 logistic, B3 logistic, B3 XGBoost and B4 XGBoost. Extend to B5/RF if E1 makes them plausible candidates. Fix algorithm seed to isolate training-sample variation; vary it separately in a smaller sensitivity run.
- **Split/sampling:** a predetermined grouped train/calibration/reference split (60/20/20) from the defined target population; refit on 200 design-respecting training replicates, keeping reference people fixed. Increase repetitions if estimated selection probabilities remain imprecise. For fixed-threshold comparisons, calibrate once on the calibration sample and freeze the numerical cutoff; assess recalibration effects separately. This is internal post-exploration validation.
- **Metrics:** weighted Jaccard overlap, fraction of people changing membership, probability SD and mean absolute deviation, per-person selection probability, disagreement around the boundary; headcount only as context. At 30% capacity, independent random sets have approximate Jaccard 0.30/(2−0.30)=0.176 in the large equally weighted case; use simulated weighted controls in the actual sample.
- **Tests:** paired refit differences and their empirical distributions; interval estimates over independently resampled reference PSUs when making population statements. Do not label 200 bootstrap models as 200 independent clinical samples or use a naive t-test over refits. Report Monte Carlo error for selection frequencies.
- **Outputs:** membership-instability figure and instability/performance table, stratified by measured access where adequately supported.
- **Claim supported:** whether classification/headcount criteria conceal practically meaningful identity changes, and whether a simpler model improves reproducibility.
- **Weakening result:** all candidates have near-identical memberships or agree in ranking across accuracy and stability. Then instability is a validation result, not the central discovery.

**E3. Evaluate expenditure consequences and explain the zero-spending contribution.**

- **Experimental change:** selection capacities 10/20/30/40/50%; compare model selection, random equal-capacity selection, age/sex baseline, and diagnosis/functioning baseline. Add zero-mass-standardized descriptive distributions. Selection by observed spending is an explicitly labeled unattainable oracle diagnostic, never a usable predictor.
- **Models/splits:** E1 held-out predictions; use shared held-out respondents and paired survey replicates. Repeat anchor summaries across E2 refits to show training sensitivity. Compute policies within fold before aggregation; do not pool uncalibrated scores from different fits into one rank without justification.
- **Metrics:** mean, median, SD, CV, Gini, zero mass, positive-spender CV, exceedance probability, absolute mean excess `E[(C−t)+]`, and normalized excess for t=$10k/$20k/$50k. Report tail event counts and effective sample sizes; very small selected tails may be too imprecise for a claim.
- **Tests:** paired survey intervals for selected-minus-comparator differences, acknowledging overlap between full and selected samples. Primary 30% contrast and $20k threshold; other capacities/thresholds are robustness, with multiplicity handled as specified above. Compare the model to simple selection controls, not just to the entire population.
- **Outputs:** mean–SD–CV frontier and a decomposition panel; selection-policy table with absolute and relative tail quantities.
- **Claim supported:** which model/policy decisions change when expenditure distributions enter evaluation, and whether the tradeoff persists beyond zero mass.
- **Weakening result:** the result exists only for the legacy cache, a few outliers or one cutoff; or all models match the simplest baseline. A zero-mass-only explanation can be an informative negative result but should not be sold as a novel tail-risk mechanism.

For a nonnegative outcome with positive-spending probability p and positive-spender CV `CV+`, the exact mixture identity is

`CV² = (CV+² + 1 − p) / p`.

Use it to separate the role of p from changes in positive expenditure. This is standard algebra, not a new theorem. The current cache already warns against a simplistic monotone mechanism: positive-spender CV rises from 2.417 to 3.015 for the nominal 30% pool, but falls to 2.836 at 10%, even while overall CV increases further.

**E4. Test whether the principal result survives construction, population and access checks.**

- **Experimental change:** original versus corrected diagnosis count; valid-code/missing-indicator versus alternative reasonable imputation; weighted versus unweighted evaluation of the same predictions; legacy versus training-estimated target thresholds; adult core versus adult SAQ populations; insurance and utilization additions individually rather than only cumulatively. Keep one prespecified access marker outside the predictors for the audit.
- **Models/split:** primary B3 logistic/XGBoost plus B4/B5 where needed; use E1 paired folds, refitting only where inputs change. Missingness-only and age/sex models are controls. Never compare different samples as if only features changed.
- **Metrics:** deltas in E1–E3 primary metrics; selected-group prevalence of exact coverage, no-usual-source, reported delayed/unaffordable care and corrected diagnosis/functioning measures, with unknowns shown separately. Fit a survey-weighted descriptive model for label membership using nonlinear age, sex, diagnosis indicators, functioning and coverage, then standardize coverage-associated probabilities over common support. This is adjusted association, not a causal coverage effect.
- **Tests:** paired design-based intervals; prespecified interactions only, adjusted for multiplicity. Show lack of covariate overlap and avoid extrapolated subgroup claims. For any health measure used to judge a model, state whether it was also a predictor; leave it out in a dedicated validation variant if necessary.
- **Outputs:** robustness forest plot plus cohort-composition/availability table.
- **Claim supported:** the main result is not solely a coding, survey-target or questionnaire-eligibility artifact; access composition can qualify the label's interpretation.
- **Weakening result:** robustness changes reverse the conclusion, or an apparent access contrast vanishes after accounting for measured composition. Report the restricted scope or null finding.

### STRONGLY RECOMMENDED

**E5. Replicate the frozen retrospective protocol in a second MEPS year.**

- **Change/models:** a second harmonized year, the two main model families and anchor feature sets; evaluate both frozen-model transport and independently retrained replication, keeping them distinct.
- **Sampling:** exclude shared persons between training and external evaluation using documented IDs/panels; account for repeated households/design structure. Use valid year-specific weights and inflation-adjusted fixed-dollar thresholds; report separately any year-relative threshold.
- **Metrics/tests:** E1–E4 primary metrics, paired survey intervals within year and year-by-policy differences. No random cross-year row splitting.
- **Outputs/claim:** replication table and year-specific frontiers establish whether the finding extends beyond the explored year.
- **Weakening result:** no replication or a reversal tied to coding changes. Calendar transport still does not establish next-year person-level prediction.

**E6. Add RF and a direct-cost baseline.**

- **Change/models:** RF under equal evaluation, plus a simple two-part spending model: occurrence logistic and positive-spending Gamma GLM with log link; assess adequacy and use a suitable alternative if it fails. Rank by predicted expected spending.
- **Sampling/metrics/tests:** E1 folds and survey intervals; expected-spend error/calibration as well as matched-capacity membership and expenditure metrics. AUROC against the low label can be diagnostic but is not the direct-cost model's sole goal.
- **Outputs/claim:** target-choice/model comparison table; determines whether classifying a low-spending label has any practical advantage over predicting cost directly.
- **Weakening result:** direct-cost prediction dominates all practically relevant metrics. This would favor a negative result about the classification framing.

**E7. Prospective linked-panel evaluation—essential if the title or conclusion promises future risk.**

- **Change/models:** year-one inputs predict year-two labels/spending; reuse the best compact and richer baseline and add prior spending as an explicit comparator.
- **Sampling:** official two-year linked data, longitudinal weights, person/household-disjoint development and validation; no second-year predictors in year-one decisions. Document attrition and measurement dates. A separate panel is preferred for external validation.
- **Metrics/tests:** year-two discrimination/calibration, selection persistence, high-spending transition rates and cost distributions; paired longitudinal-design intervals and prespecified access subgroup contrasts.
- **Outputs/claim:** transition matrix and prospective comparison table; supports a bounded forecasting claim.
- **Weakening result:** label persistence or ranking collapses. It cannot support a causal intervention or retention claim even if prediction is strong.

### OPTIONAL

**E8. Finite-pool budget simulation.** Change pool size N=100/500/1,000 and budget rule; sample synthetic people from survey-weighted held-out expenditure distributions for each selection policy. Show an independent-draw model and a household-dependence sensitivity; do not treat survey PSUs as real insurance pools. Report dollar SD, proportional SD, 95th-percentile aggregate spending, and exceedance of a declared fixed-dollar or proportional budget. Compare policies using common random draws; bootstrap source PSUs for data uncertainty separately from simulation error. Figure: budget exceedance versus N. This supports an illustrative accounting consequence, not observed insurer solvency. No difference or strong dependence sensitivity weakens the operational story. Do not estimate extreme regulatory-tail risk from this sample or call all-payer spending insurer losses.

Under independent identical draws, `SD(mean cost)=SD(C)/sqrt(N)` and its relative SD is `CV(C)/sqrt(N)`. This explains why both dollar variability and proportional variability must be reported. It does not require a simulation to establish the identity.

**E9. Efficiency and explanation.** Change model family/feature set with the same hardware, fixed batch sizes and warm/cold timing; report fit time, inference latency, memory and artifact size over repeated runs, with bootstrap timing intervals. Use grouped permutation importance or leave-domain-out ablation on E1 held-out samples; avoid correlated-feature SHAP rankings as causal evidence. Figure/table: complexity–performance frontier. This supports a practical simplification result only when predictive and cohort criteria are already acceptable; overlapping timings or inferior accuracy weakens it.

**E10. External claims dataset or distributional prediction.** Only if a specific unresolved hypothesis demands it: validate the chosen policy on licensed claims with harmonized payer liabilities and timestamps, or compare a two-part distributional/quantile baseline with calibrated intervals. Use an external untouched cohort, subgroup coverage and tail-error metrics, paired intervals and documented exchangeability limitations. Figure: transport/calibration comparison. This could strengthen generalization, but new data or fancy uncertainty methods are not the minimum extension; failure to transfer should be reported directly.

**Minimum work package:** E0–E4, two existing model families, one corrected 2023 target population, one primary capacity and a short sensitivity grid. E0 is repair; E1–E4 are the four substantive experiment families. This can support a narrowly scoped empirical preprint/workshop submission **if** the corrected comparisons yield a practically informative result. No analysis plan can guarantee acceptance or force a novel result. For a stronger generalization claim, prioritize E5; for forecasting, E7 is mandatory. Extra figures or hyperparameter runs are lower value than these checks.

## Execution sequence

E0 → feasibility pilot → E1 → E2/E3 → E4 → E5 and E6 → manuscript. E7 is mandatory only if the final paper claims prospective prediction; otherwise it is a separate extension. E8–E10 should not delay the core study.

The pilot uses small, explicitly nonfinal runs to check computation and estimators. Keep all prespecified contrasts, even if the pilot is disappointing. Pilot outcomes cannot authorize choosing only favorable models, thresholds or subgroups.

No experiment in this document has been completed as a corrected study. The results register identifies the descriptive checks that actually ran and the evidence still missing.
