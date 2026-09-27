# Tests and validation requirements

**Updated:** 2026-09-25. **Status:** Future scientific test specifications; only the historical evidence recheck has run.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

## Completed checks versus future tests

The existing verification script was rerun successfully on 2026-09-25. It reconstructed the legacy label/count, compared source hashes, evaluated cached scores and recomputed descriptive spending summaries. Exact results appear in document 10. It did not run the corrected pipeline, training refits or survey confidence intervals.

The tests below are **specifications to implement**, not a claimed passing suite. They target scientific failure modes and boundary cases; they are not cosmetic tests of file creation.

## Data and target tests

| Test ID | Test fixture / action | Required behavior | Failure prevented |
|---|---|---|---|
| D01 | Duplicate person ID in raw or scored input | Reject before joining | Silent row multiplication |
| D02 | Historical raw release and derived label | 18,919 rows, 5,579 positives, zero label disagreements at $484.40 rule | Wrong source/label |
| D03 | Codes yes/no/unknown/refused/inapplicable | Preserve declared semantics; unknown never silently becomes no | Missing-as-absence distortion |
| D04 | ANYLMI23=1 with diagnosis items all no | Correct diagnosis count stays zero; functional feature may differ | Construct overlap |
| D05 | Only ever-COVID=1 | Diagnosis count stays zero; separate sensitivity variable available | Ever infection treated as chronic disease |
| D06 | Adult/SAQ boundaries and zero weights | Eligibility matches documented rule; exclusions and weight sums reconcile | Wrong target population |
| D07 | Modify only held-out expenditure | Training-estimated label cutoff stays identical | Outcome leakage |
| D08 | Exact/just-above cutoff, positive ER/IP | Correct inclusive spending boundary and both zero-use conditions | Misdefined endpoint |
| D09 | All-item diagnosis unknown | Preserve missingness; do not portray count as confirmed disease-free | False health interpretation |

D02 reproduces the historical table only. It is not the expected denominator for the new SAQ analysis.

## Splitting, fitting and cache tests

| Test ID | Test fixture / action | Required behavior |
|---|---|---|
| F01 | Household with multiple people | All members remain in one outer fold and one reference partition |
| F02 | Paired model comparison | Identical test IDs, outcomes, target cutoff and evaluation weights |
| F03 | Held-out outlier and unseen category | Training imputation/scaling unchanged; defined unseen-category handling |
| F04 | Estimator with reversed `classes_` ordering | Locate Y=1 column by class value, not fixed column position |
| F05 | E2 repeated fits with different training replicates | Imputer, encoder/scaler and estimator refitted; reference people unchanged |
| F06 | E2 reference outcome modification | Fitted scores and selected memberships unchanged |
| F07 | Change feature list, input hash, code revision, config or dependency versions | Invalidate score cache; no silent reuse |
| F08 | Missing scores, nonfinite values or duplicate OOF records | Fail with explicit count and reason |
| F09 | Refitting failure | Record failed replicate and diagnostic; do not replace seed until success |
| F10 | Same seed/config/environment | Deterministic outputs within declared numerical tolerance; disclose nondeterministic backend behavior |

## Selection and metric tests

| Test ID | Fixture | Expected result |
|---|---|---|
| S01 | Scores 0.9/0.6/0.2, equal weights, one-third capacity | Select score 0.9 |
| S02 | Scores tied, inputs permuted | Same IDs selected with fixed tie seed |
| S03 | Unequal weights and unattainable exact capacity | Choose documented nearest prefix; report achieved fraction and discrepancy |
| S04 | Zero/full capacity | Empty/full set with explicit empty-summary conventions |
| S05 | Frozen threshold and shifted score distribution | Capacity may change; never recompute a hidden quantile |
| M01 | Identical selected sets | Jaccard=1; disagreement=0; member loss=0 |
| M02 | Disjoint equal-capacity sets | Jaccard=0; disagreement=2q if q<=0.5; member loss=1 |
| M03 | Independently shuffled fixed-size sets | Size constant while identity varies; large equal-weight Jaccard approaches q/(2-q) |
| M04 | Nonnegative costs with known zeros | Mixture identity CV²=(CVpositive²+1-p)/p holds within floating tolerance |
| M05 | Multiply all costs by k>0 | Mean/SD scale by k; CV and zero share unchanged; scale tail threshold too for corresponding tail comparison |
| M06 | Multiply all evaluation weights by same positive constant | Normalized means, AUROC, CV and capacity unchanged |
| M07 | All-zero spending or empty positive group | Undefined CV metrics marked; no arbitrary zero/finite substitute |
| M08 | Constant positive costs | SD=0, CV=0 |
| M09 | Costs exactly at t and above t | Exceedance at >=t; dollar excess zero at t; distinguish all dollars of high spenders from excess dollars |
| M10 | One outcome class in evaluation sample | AUROC undefined with explicit status; never fabricate 0.5 |

## Survey and inference tests

| Test ID | Required validation |
|---|---|
| V01 | Replicate design preserves specified strata/PSU structure and uses the validated rescaling method; row bootstrap rejected |
| V02 | Compare a simple weighted mean and its uncertainty with a trusted survey implementation on the same design |
| V03 | Domain estimates preserve the complete design information; singleton handling explicit and reproducible |
| V04 | Paired contrasts use the same reference respondents and same evaluation replicates, including overlap with full population |
| V05 | Conditional-prediction intervals labeled distinctly from uncertainty including model refitting |
| V06 | No t-test that treats folds, seeds, model refits or all refit pairs as independent clinical samples |
| V07 | Report Monte Carlo error / stability of interval endpoints as replicate count grows |
| V08 | Practical equivalence/noninferiority uses the prespecified difference, margin and interval; CI overlap alone never qualifies |

## Reporting gates

Every table row must include cohort definition, outcome definition, model/block, policy, achieved capacity, n, weight sum, estimate, uncertainty type and run ID. Every tail claim must report event counts. A manuscript number must trace to a structured result row, not a manually selected notebook cell. Tables must include prespecified null and failed comparisons. Reproduce the primary table in a clean environment before submission.
