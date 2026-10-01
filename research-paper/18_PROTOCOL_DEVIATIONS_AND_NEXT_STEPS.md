# Protocol implementation decisions and remaining work

**Date:** 2026-09-30. **Status:** implementation record, not an untouched-data preregistration.

## Decisions made before the main runs

The primary population follows documented SAQ eligibility at AGE42X>=18, SAQELIG=1 and positive SAQ/person weights. DUID defines the grouped validation unit. The adult-core sensitivity uses AGELAST>=18 and person weights, excluding the K6/PHQ features. These populations are different estimands.

Validation uses outcome-blind shuffled GroupKFold with seeds 42 and 2026; it does not stratify by an outcome constructed before splitting. Model fitting uses normalized population weights. Numeric median imputation and scaling are learned on training rows. Fixed valid categorical code dictionaries prevent feature semantics from changing with fold cardinality.

The weighted quantile is the inverse empirical weighted CDF (first cumulative weight at or above the requested fraction). The legacy $484.40 definition remains separate. E2 fixes its original training endpoint across all refits, and refits preprocessing and model parameters. Algorithm seed remains fixed.

The full variance design is preserved for domain calculations. The implemented Rao–Wu n_h−1 bootstrap samples PSUs with replacement within strata and rescales their contributions by n_h/(n_h−1). Training replicates physically repeat sampled PSU rows so preprocessing is actually refitted on the resample. Fixed-reference variability is reported separately from conditional evaluation uncertainty.

## Scope achieved and deviations from the full plan

| Planned item | Implemented scope | Remaining work |
|---|---|---|
| E0 legacy and corrected comparison | Legacy label reconstruction, corrected source cohort and source-trained corrected models | Exact legacy notebook model reproduction across versions |
| Full dictionary | Source variables, categorical codes, sentinel handling, source documentation and broad timing | Full item question text and field-specific availability annotations |
| E1 paired ladder | D/C/B0/B2/B3/B4/B5, two models, five folds, two seeds, weighted metrics and calibration | B1 supplement and all secondary uncertainty contrasts |
| E2 refits | Four anchors, 200 paired PSU resamples each, fixed-reference probabilities/membership, frozen-threshold comparison | Reference-population uncertainty and joint/nested learning/evaluation uncertainty |
| E3 spending | Five capacities, mean/SD/CV, zero mass, positive-spender CV, $20k tails/excess, simple demographic/clinical and random controls | $10k/$50k threshold checks, Gini, outlier influence, stronger zero-mass and direct-cost comparisons |
| E4 robustness | Seven one-component/domain scenarios with 90 fits | Refit stability under those scenarios, full adjusted access/overlap analysis, PSU-held-out transport check |
| Inference | Primary B3 paired conditional intervals, 1,000 shared design replicates | Secondary multiplicity, justified equivalence/noninferiority margins and joint uncertainty |
| E5 replication | Not run | Harmonize another nonoverlapping year; freeze analysis before inspecting it |
| E6 comparators | RF supported by model factory but not run | RF and a two-part direct-expenditure baseline |
| E7 prospective | Not run | Linked longitudinal design, weights and genuinely prior predictors |

No significance-based model selection or threshold search was introduced. All seven E4 variants were run and retained. The unweighted-training accuracy reversal is reported rather than excluded. The primary AUROC interval includes zero; no noninferiority claim is made from the illustrative margin in the earlier plan.

## Provenance updates after the main experiments

Formatting and import cleanup did not change the scientific function syntax trees. A later defensive check rejects nonfinite endpoint/weight input before modeling; the actual HC-251 cohort has finite values and its reconstructed table is checked against the original completed run. Run manifests preserve the code hashes at execution rather than being rewritten to match later files.

Future runs now also save exact source copies and the dependency-lock hash. Main-run manifests already record code hashes but predate that source-copy addition. Source metadata for the legacy12 dictionary was corrected before the sensitivity runs; the earlier primary run uses dx10 and its computations are unaffected.

## Verification completed on 2026-10-01

[Verification report](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/19_VERIFICATION_AND_PR_READINESS.md) records the engineering verification plan now completed. Version 2 run manifests include the report before atomic finalization; historical runs stay untouched and explicitly retain their limited report integrity. Configuration-aware dictionaries, undefined-metric counts, incremental diagnostics, fresh aggregate exports and the seeded-random expenditure comparison are implemented. Ten E1 fits and the 80-refit E2 pilot matched original scores and membership exactly. The 46-test suite passed. No primary scientific definition or paper-readiness gate was changed.

## Highest-value follow-up

First quantify reference-sample uncertainty for the membership difference and repeat the central result under the training-weight/population sensitivities. Then add the direct-cost comparator and frozen independent-year replication. These strengthen the observed modest contribution more than adding a new architecture or expanding the dashboard.

## Original README discussion prompts retained for context

The initial README listed discussion with Prof. Jing about why ER is used, cost differences, behavioral predictors, how the model would be used and how it compares with existing models. It also mentioned insurance innovation and annuity/premium-investment ideas. Those are motivations and open application questions; the current MEPS experiments do not test investment returns, premium design, retention or insurer profitability.
