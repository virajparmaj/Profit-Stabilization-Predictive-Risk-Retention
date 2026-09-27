# Proposed study protocol and estimands

**Updated:** 2026-09-25. **Status:** Draft protocol to freeze before new model comparisons; no new study results.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

### Common protocol to freeze before running the new comparisons

This is a post-exploration protocol: freezing it now improves discipline but does not turn already inspected 2023 data into untouched confirmatory evidence.

- **Population:** for the primary full ladder, use the documented adult SAQ-eligible/responding population with positive `SAQWT23F`, retaining item nonresponse with explicit indicators. Use those weights for primary evaluation. Reproduce the original all-age `PERWT23F` analysis separately as historical context; run an adult core-variable analysis without SAQ features as sensitivity. Do not silently compare blocks on different respondents. Explicitly state that the principal corrected study targets adults, unlike the original all-age summaries.
- **Outcome:** retain the historical label as a named legacy definition. Primary revised definition uses a 30th-percentile spending cutoff estimated **only in each outer training sample**, with appropriate population weights, then frozen for that test fold, plus zero ER/inpatient use. Report the training thresholds. Compare the legacy $484.40 rule separately; do not pretend that changing population and threshold is a mere refactor.
- **Features:** rebuild from raw data and codebook; remove limitation summary and ever-COVID from diagnosis count. Keep ever-COVID as a separate sensitivity feature. Handle unknown and inapplicable separately. Add age/sex baseline D and D+corrected diagnosis/functioning baseline C. Freeze the literal feature list and encoding; preserve categorical semantics rather than inferring them afresh from a small fold's cardinality.
- **Splitting:** paired five-fold household-grouped evaluation with two predefined seeds; keep all respondents from a household in the same fold using a verified household identifier from the raw documentation. Fit imputers, transformations and any tuning within training only. Use identical splits across models. Repeated folds are not independent experimental observations. A held-out PSU sensitivity tests dependence at a broader level; it is a different transport challenge, not a replacement for survey variance estimation.
- **Models:** primary L2 logistic and XGBoost, reusing documented configurations; add RF as a strongly recommended check. A feature ladder is a diagnostic factorial comparison, not a contest where any winning metric authorizes a deployment claim. Use equal inner tuning budgets only if needed; an untuned comparison is acceptable when explicitly described.
- **Selection:** use high `P(Y=1)`. Primary policy selects 30% of **test-population weight**, with a reproducible outcome-independent tie rule and reported achieved capacity. Test-pool quantiles are legitimate for a capacity-constrained ranking policy because they use no test outcomes; they do not establish deployable fixed-threshold behavior. Evaluate the latter separately with a numerical threshold chosen on training calibration data and frozen for testing/refits.
- **Uncertainty:** for descriptive population estimates and paired differences, use documented survey Taylor linearization where applicable or a design-respecting rescaled PSU bootstrap within `VARSTR`, with domain estimation and singleton handling specified. Start with 1,000 design replicates for nonlinear summaries and increase until Monte Carlo error is negligible for reported precision. Separate uncertainty conditional on fixed predictions from uncertainty involving the training procedure. Do not bootstrap individual rows as if they were independent survey observations.
- **Confirmatory contrasts:** predeclare corrected B3 logistic versus B3 XGBoost, B2 versus B3, B3 versus B4, and B4 versus B5. Use paired 95% intervals and Holm adjustment within secondary contrast families. Report practical effect sizes; avoid claiming discovery from a list of marginal p-values.

## 8. Design of the completed study

| Element | Proposed specification |
|---|---|
| Research question | Do classification-based rankings of compact low-spending models agree with rankings based on membership reproducibility and expenditure profiles at matched capacity? |
| H1 | At least one prespecified model/block contrast has a material discrepancy between label-performance and membership-stability conclusions. Define materiality before running; report continuous effects even if no threshold is crossed. |
| H2 | Selected low-spending cohorts can reduce mean and SD while increasing CV; evaluate whether the effect survives corrected inputs, valid targeting and zero-mass decomposition. |
| H3, secondary | Insurance/utilization additions change measured access/burden composition beyond the health-only feature set; no directional causal interpretation. |
| Dataset | HC-251 2023; original all-age description plus primary adult SAQ target with proper weights, documented missing codes and corrected diagnosis count. Repeated-year replication strongly recommended. |
| Experimental design | E0–E4, paired grouped evaluation, whole-pipeline training refits, fixed-capacity versus fixed-threshold policies, and design-based uncertainty. |
| Models/baselines | L2 logistic, XGBoost, age/sex and diagnosis/functioning controls, random selection; RF and two-part direct-cost model recommended. |
| Primary metrics | Weighted membership turnover/Jaccard and mean/SD/CV of selected-cohort expenditure, interpreted jointly with AUROC and calibration. Do not collapse these into an arbitrary omnibus “stability score.” |
| Statistical testing | Paired survey-aware intervals; prespecified primary contrasts; Holm control for secondary families; no naive tests over correlated folds. Noninferiority/equivalence require prespecified justified margins. |
| Robustness | Eligibility/weight choice, count construction, missing codes, sample versus population capacity, selection ties, thresholds, seed variation, outlier influence; PSU-held-out sensitivity. |
| Ablations | B3 minus behavior, minus mental-health inputs, minus functioning, minus corrected diagnoses; B3+insurance, B3+SES, B3+utilization; shared respondents and availability dates. |
| Figures | Cohort/measurement timeline; accuracy-versus-membership instability; mean–SD–CV selection frontier with zero-mass decomposition; optional access composition and external replication. |
| Tables | Data/definitions/missingness; full performance and calibration; selected-cohort spending and membership statistics; robustness contrasts. |
| Primary result needed | A corrected, practically meaningful model/policy comparison whose interpretation changes when membership or expenditure criteria are added; supported uncertainty rather than one favorable point estimate. |
| Secondary results | Compact-model sufficiency, weight sensitivity, access composition, zero-mass contribution and endpoint-specific feature value. |
| Limitations | One explored year, no prospective outcome, limited high-cost counts, imperfect measured need, residual access/diagnosis confounding, survey nonresponse and expenditure error. |
| Threats to validity | Construct overlap, structural missingness, adaptation to the same dataset, subgroup multiplicity, household dependence, test-set selection, changing outcome thresholds, all-payer versus insurer outcome mismatch. |
| Reproducibility | Raw release links/version/checksums; canonical processing script; data dictionary; environment lock; model configs/seeds; fold/household IDs; weight/variance procedure; scored-output manifest; one command to regenerate tables/figures. |

The release should distinguish public downloadable raw data from local caches and trained artifacts. The current `prep.with_oof()` loads a serialized pipeline and returns any existing cache without input-version validation. Rebuild that path from explicit source configuration for the study; record software versions because saved notebook warnings indicate version drift. Keep all exclusion counts and weight sums in the results. Do not replace failed fits or unfavorable seeds without disclosure.

## Operational definitions to freeze

For reference people i with positive survey weights w_i and selected indicators s_i, define weighted capacity as sum(w_i s_i)/sum(w_i). Use descending P(Y=1). At a tied boundary, break ties by a documented deterministic hash of ID and a fixed seed, independent of outcomes. Select the ranked prefix whose total weight is nearest the requested capacity; allow the empty or full prefix at the endpoints. Report the achieved capacity and largest record weight. Do not claim exact weighted capacity from binary membership when discrete weights make it unattainable. Fractional boundary membership may be a separate analytic sensitivity, not the primary identity policy.

For a baseline selected set S_0 and refit set S_b:

- Weighted Jaccard = weight(S_0 intersect S_b) / weight(S_0 union S_b).
- Population membership disagreement = weight(S_0 symmetric-difference S_b) / weight(reference population).
- Baseline-member loss = weight(S_0 minus S_b) / weight(S_0).
- Selection frequency for person i = number of refits selecting i / number of valid refits.

These denominators answer different questions. Report them by name, not interchangeably as “turnover.” State a convention for empty unions; do not silently divide by zero. Show base-versus-refit summaries and optional pairwise-refit summaries separately.

For spending C, report weighted mean, population-form SD, CV=SD/mean, zero share, positive-spender CV, Pr(C>=t), and E[(C-t)+]. Gini and expenditure shares are secondary distribution summaries. Undefined CV or positive-spender summaries must be explicitly marked when their denominators vanish. Dollar thresholds are descriptive; no clinical or contract interpretation is implied.

## Separate the sources of variability

1. **E1:** estimate each outer training fold's weighted label cutoff and freeze it for its held-out fold. Compute performance per fold and aggregate predefined summaries. Do not treat scores targeting slightly different fold thresholds as automatically comparable in a pooled AUROC.
2. **E2 primary:** estimate the endpoint cutoff once in the original training split and hold that endpoint fixed across refits. Refit every feature preprocessing and model-fitting step. This isolates instability for a common scientific target. Re-estimating the label cutoff inside each refit is a separately labeled end-to-end target-construction sensitivity.
3. **E2 selection:** matched-capacity ranking is recomputed for each model on fixed reference people. A model-specific numerical probability threshold is chosen once on its base calibration sample and frozen for the fixed-threshold comparison. Recalibrating after each refit is a different policy and must be labeled.
4. **Survey uncertainty:** survey resampling of a fixed set of predictions estimates conditional evaluation uncertainty. Training resampling estimates learning sensitivity. A population claim about a trained procedure requires a design that includes both sources; neither source alone stands for the other.

The E2 endpoint clarification above governs implementation wherever a shorter experiment description says “whole pipeline.” It does not permit fitting preprocessing on reference people. Reference outcomes remain unavailable to model choice and threshold calibration.

## Training weights and algorithm settings

Primary model fits should use the target population weights normalized to mean one within each training sample, consistently for logistic and XGBoost loss. Evaluate using the documented original survey weights. An unweighted-training comparison is a sensitivity on the same splits, with the same weighted evaluation. Normalization matters because penalties and minimum-child-weight behavior can depend on weight scale; freeze that convention and report it.

Freeze literal category handling, scaling, logistic penalty/solver, XGBoost settings, thread count and seeds in configuration. Reusing historical hyperparameters reduces scope but does not make their performance optimal. Tuning, if introduced, occurs inside training data with comparable budgets and is repeated as part of refitting.

## Survey design gate

Validate the exact weight, strata, PSU and domain handling against the official HC-251 documentation before implementing variance estimates. Use full design information when estimating domains. Specify singleton-stratum handling and the chosen rescaled PSU bootstrap or Taylor method; cross-check simple estimates against a trusted survey implementation. Do not substitute weighted row sampling or an ordinary row bootstrap. Household grouping for validation and survey PSU resampling solve different problems.

Existing 2023 outcomes have been explored. This protocol is prospective with respect to future runs, not a preregistered untouched test of 2023. A frozen replication on nonoverlapping data offers stronger validation.
