# Results register: completed, provisional and pending

## Current execution update — 2026-09-30

The corrected core study has now run. See [actual implementation/results](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/17_IMPLEMENTATION_AND_RESULTS.md) and the aggregate exports under `results/2026-09-30/`. The September 25 historical checks below remain valid historical evidence.

| Experiment | Current status |
|---|---|
| E0 | Corrected cohort, legacy label/count checks and independent survey benchmark complete; exact legacy model reproduction pending |
| E1 | 140 fits complete; primary paired conditional inference with 1,000 PSU replicates complete; broader secondary inference pending |
| E2 | 800 refits complete with no failures; fixed-reference learning variability quantified; reference-population/joint uncertainty pending |
| E3 | Integrated expenditure metrics and capacity curves complete; zero-mass standardization exported; full threshold/outlier sensitivity pending |
| E4 | Seven declared sensitivity variants complete, 90 fits; E2 sensitivity and full adjusted access analyses remain |
| E5–E7 | Not run |
| E8–E10 | Optional; not run |

**Tests:** 23 passed. **Independent benchmark:** Python matched R survey 4.5 mean and SE. **Claim status:** bounded exploratory empirical evidence; no finished-paper, prospective, causal or profitability claim.



**Updated:** 2026-09-30. **Status:** Current corrected-study status above; historical checks and earlier pending slots retained below.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

## Historical execution record — 2026-09-25

**Last rerun:** 2026-09-25. **Command:** `/tmp/profit-stabilization-research-review-venv/bin/python analysis/research_review/verify_existing_evidence.py`, executed from the repository root. **Exit status:** 0. **Scope:** deterministic descriptive checks and existing-cache evaluation. No fresh model fits, refit-stability analysis, design-based confidence intervals or external replication were performed.

Exact machine-readable evidence: [verified_metrics.json](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/research_review/verified_metrics.json). Recheck source: [verify_existing_evidence.py](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/research_review/verify_existing_evidence.py).

## Completed data checks

| Check | Observed result | Interpretation |
|---|---:|---|
| Raw records | 18,919 | Existing HC-251 input |
| Positive PERWT23F records | 18,463 | Historical analytic frame |
| Legacy threshold | $484.40 | Full-sample unweighted p30 |
| Legacy positive labels | 5,579 | Original label |
| Reconstructed label disagreements | 0 | Exact reproduction of existing definition |
| Reconstructed original count disagreements | 0 | Confirms implementation, not construct validity |
| Weighted legacy prevalence | 30.7252% | Historical population |
| Stale scored rows | 15,268 | Incompatible artifact |
| Stale stored positive labels | 42 | Incompatible artifact |
| Stale label disagreements | 3,973 | Must exclude/regenerate |

The stale-file check succeeded in detecting a failure of that artifact. It does not mean the stale file passed validation.

## Recomputed cached-score results

Unweighted AUROC **0.771998**; person-weighted AUROC **0.747208**. Both use the same existing scores. Their difference is descriptive; no uncertainty for that difference has been estimated.

| Metric | Population | Nominal 30% | Nominal 10% |
|---|---:|---:|---:|
| Records | 18,463 | 5,548 | 1,891 |
| Mean annual spending | $7,487.26 | $2,778.55 | $2,186.53 |
| Spending SD | $19,807.63 | $9,993.32 | $8,250.17 |
| CV | 2.646 | 3.597 | 3.773 |
| Zero expenditure | 14.45% | 27.61% | 40.66% |
| Positive-spender CV | 2.417 | 3.015 | 2.836 |
| Spending >= $20,000 | 9.10% | 2.90% | 2.27% |
| Mean excess above $20,000 | $2,891.73 | $697.77 | $609.08 |


These are positive-person-weight, historical all-age descriptions using unweighted score quantiles. Actual population capacities are **33.45%** and **11.09%**. They are not corrected 30% and 10% weighted policies. No confidence intervals are available from this rerun. Cache evaluation does not establish the provenance of model training.

## Descriptive construct sensitivity

| Definition | Uninsured n, low-label % | Insured at least part-year n, low-label % |
|---|---|---|
| Original count >=2 | 284; 63.08% | 8,724; 12.39% |
| Ten-diagnosis sensitivity >=2 | 168; 58.37% | 6,268; 8.78% |

The ten-diagnosis sensitivity excludes ANYLMI23 and ever-COVID but retains the historical yes-versus-other counting convention for this descriptive check. It is not the fully corrected missingness-aware cohort or a validated clinical index. These groups do not hold disease severity or clinical need constant. Causal interpretation is unsupported.

Among the original 545 people with count >=3 and zero office visits, 104 have outpatient visits. With the ten-diagnosis sensitivity, the corresponding counts are 315 and 69. Use literal utilization terms.

## Historical notebook results — not rerun model results

| Saved specification | AUROC | Brier |
|---|---:|---:|
| B3 logistic | 0.774447 | 0.168068 |
| B3 XGBoost | 0.772639 | 0.168591 |

The small numerical difference does not establish superiority or equivalence. Saved B0/B4/B5 XGBoost AUROCs are 0.579418/0.824610/0.949921; their same-year label performance does not establish future cost prediction.

## Historical experiment status on 2026-09-25 (superseded by the update above)

| Experiment | Status | Evidence still required |
|---|---|---|
| E0 reconstruction/reproduction | PARTIAL: historical audit complete | Corrected dictionary/cohort, source-trained legacy reproduction and corrected score comparison |
| E1 paired model/block comparison | NOT RUN | Fold-local fits, weighted performance and paired survey intervals |
| E2 membership refitting | NOT RUN | Fixed-reference repeated full refits; selection frequencies, Jaccard, disagreement |
| E3 expenditure comparison | NOT RUN; historical cache motivates it | Matched weighted-capacity policies, controls, decomposition and uncertainty |
| E4 robustness/access audit | NOT RUN; limited count sensitivity only | Missingness, population, coverage, weight, label and feature-ablation comparisons |
| E5 independent-year replication | NOT RUN | Harmonized nonoverlapping sample and frozen protocol |
| E6 RF/direct-cost baselines | NOT RUN | Paired benchmark results |
| E7 prospective panel test | NOT RUN | Temporally valid predictors, year-two outcomes and longitudinal weights |
| E8 pool simulation | OPTIONAL; NOT RUN | Assumptions and calibrated simulation outputs |
| E9 efficiency/explanation | OPTIONAL; NOT RUN | Measured compute or explanatory analysis |
| E10 external/distributional work | OPTIONAL; NOT RUN | Justified external data or distinct prediction protocol |

## Required format for future result entries

Record experiment/contrast ID, protocol version, run ID, code revision, source hashes, population, n/weight sum, model/block, seeds, target cutoff, policy and achieved capacity. Add estimate, paired difference, uncertainty method/interval, tail counts, failures, practical interpretation, limitation and output location. No blank result field should be replaced by an expected or hypothetical number.

## Documentation validation completed

On 2026-09-25, all 16 Markdown files passed title/status and balanced-code-fence checks. All 63 absolute local link occurrences resolved to existing files. The five evidence-input hashes still matched the successful audit; the model-ready table and notebook copy remained byte-identical. The completed label/count checks and stale-file disagreement count also matched the recorded results. Git showed only the new research-review artifacts and this new planning folder; no tracked source changes were introduced.

These checks verify document structure, navigation and evidence consistency; they do not validate unexecuted research.
