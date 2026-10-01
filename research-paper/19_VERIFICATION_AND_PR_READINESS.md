# Verification fixes and PR readiness

**Date:** 2026-10-01. **Branch:** `viraj/research`. **Status:** verification plan implemented; targeted reruns reproduce the saved results. This completes the engineering verification pass, not the research-paper submission gates.

## Changes and reasons

| Gap | Implemented behavior |
|---|---|
| Reports were generated after final output hashing | Version 2 manifests are finalized atomically only after report generation. Reports, configuration and required scientific outputs are checked before reuse. Completed runs reject finalization again. |
| Legacy reports had no run-manifest hash | Legacy scientific outputs remain readable and hash-checked. A report command requires a new output directory; it generates text from scientific inputs and explicitly identifies the historical report-integrity limitation. It never copies the old report as verified evidence. |
| A missing fold metric could silently dilute a weighted mean | Shared aggregation leaves a required incomplete metric undefined and emits valid/expected counts. Refit and paired-learning summaries also expose counts and remain undefined when incomplete. Empty selected cohorts retain an explicit undefined metric schema. |
| Warnings and earlier fit diagnostics could disappear after an exception | Every fit appends and flushes an event to `fit_log.jsonl`, including context, elapsed time, warnings and failure/interruption. E2 base fits are included. Failed E2 replicates keep their declared IDs and are never replaced. |
| Random ranking appeared only in fold-level tables | Aggregate tables and the expenditure figure now apply that same seeded ranking within each fold, then summarize the selected people jointly. This is one seeded random policy, not an expectation over random policies. |
| Dictionary metadata did not describe sensitivity coding | Dictionary entries now name population weights, burden definition, missingness mode, derived numeric code indicators and the partial legacy-zero limitation. Full questionnaire text remains future work. |
| Ambiguous experiment configurations were accepted | Empty/duplicate capacities, absent primary capacity, duplicate blocks/models and fewer than two variability replicates are rejected. Pilot reports prominently say feasibility only. |
| An export could mix with old files | Export commands require a fresh directory, use an aggregate-file allowlist, and hash the resulting artifacts. Source-run manifests and new derivation manifests remain separate. |

SIGINT/KeyboardInterrupt and SystemExit leave an interrupted status; ordinary exceptions leave failed status. Hard process termination can leave a running status. None is accepted as a completed-results run. These checks detect accidental artifact changes relative to stored manifests; they are not a digital signature or protection against someone deliberately rewriting both data and hashes.

## Verification performed

| Check | Result |
|---|---|
| Full local automated suite | 46 passed, including the HC-251 cohort/R benchmark regression |
| Same suite with no dataset in its working directory | 45 passed, 1 explicitly skipped |
| Fresh E1 verification | B3 logistic and XGBoost, five folds, seed 42, original 600-tree settings: 10 fits, zero failures/warnings |
| E1 numerical comparison | 19,552 prediction rows and 10 performance rows exactly equal to the corresponding original run subset; cohort and split assignments exactly equal |
| E1 membership comparison | 97,760 selection decisions across five capacities exactly equal |
| Fresh E2 pilot | Four original anchors × 20 refits, plus four base fits: 84 fits, zero failures/warnings |
| E2 numerical comparison | 157,520 refit prediction/membership rows and 168 metric rows exactly equal to both the original pilot and the corresponding first 20 full-run replicates |
| E2 fixed inputs | Base predictions, endpoint and reference table exactly equal |
| Aggregate regeneration | All 140 original model-policy rows unchanged within 1e-12; ten seeded-random rows added |
| Preservation | All 263 files across the twelve source runs remained byte-identical during verification/export |
| Figures | Three static figures regenerated; expenditure frontier includes the seeded-random comparator |
| Final artifact checks | All 163 exported-file hashes and derivation hashes valid; aggregate-only CSV schemas; original September 30 export hashes intact; 86 local document links resolve |
| Formatting and patch checks | Black, isort and git diff checks passed |

The targeted E1 and E2 runs took about 5.31 and 16.98 seconds in this session. Timing is environment-dependent, not a performance claim. Arrow emitted sandbox CPU-cache probing messages outside estimator fits; the runs completed successfully.

The previous 140-fit E1, 800-refit E2, 80-refit pilot and 90-fit E4 results have not been replaced or presented as freshly repeated in full. Exact targeted comparisons justify retaining their scientific outputs for this verification-only change. The new E2 run is explicitly a pilot.

## Evidence and interpretation

New evidence is under `results/2026-10-01-verification/`. Start with `verification.json` and `export_manifest.json`. Each run folder contains copies of its original allowlisted aggregate evidence. Its `derived/` folder contains the current report, corrected dictionary, updated applicable summaries and a derivation manifest recording parent-manifest and generator hashes. Original legacy aggregate files are retained for audit; use the derived tables for corrected presentation. Person-level files remain local and are not exported.

The original `results/2026-09-30/` folder is unchanged. Its legacy REPORT.md files were not covered by their original run manifests; the new reports document this limit instead of silently rewriting history. The new version 2 runs cover their reports in the run manifest.

At requested 30% capacity, the seeded-random comparator averages approximately $8,772 mean spending, $22,756 SD and CV 2.594 across the two outer-split seeds. B3's lower dollar spending and higher relative CV therefore remain visible against a concrete comparator. These are descriptive within-sample comparisons with one random ranking, not new statistical significance claims.

The central finding remains unchanged: B3 logistic and XGBoost have similar AUROC, while mean reference-population membership disagreement across training refits is 6.15% versus 10.54%. The paired conditional AUROC interval includes zero; refit variability is not reference-population uncertainty. Unweighted training still reverses the small accuracy ordering. See `17_IMPLEMENTATION_AND_RESULTS.md` for full findings.

## Reproduce the verification

Run from the repository root with the locked environment and local raw data. Use fresh run IDs and a fresh output path when repeating these commands.

```sh
.venv-research/bin/python -m pytest analysis/tests/research_pipeline -q
.venv-research/bin/python -m analysis.research_pipeline run \
  --experiment E1 --run-id verification-e1-20261001 \
  --config analysis/research_pipeline/configs/verification_2023.yaml
.venv-research/bin/python -m analysis.research_pipeline run \
  --experiment E2 --run-id verification-e2-pilot-20261001 --pilot
MPLCONFIGDIR=/tmp/meps-matplotlib XDG_CACHE_HOME=/tmp/meps-cache \
.venv-research/bin/python -m analysis.research_pipeline.verify_completed \
  --original-e1 primary-e1-20260930 --original-e2 primary-e2-20260930 \
  --original-pilot pilot-e2-20260930 \
  --e1 verification-e1-20261001 --e2 verification-e2-pilot-20261001 \
  --robustness-prefix robustness-20260930 \
  --output research-paper/results/2026-10-01-verification
```

This comparison requires the original ignored local run directories. Aggregate exports alone cannot reconstruct person-level predictions. New users must first execute the original study commands; the exported configuration and hashes document that provenance. Exact prediction equality was established in this environment and may require matching platform/library builds elsewhere.

To derive just a report without modifying a run:

```sh
.venv-research/bin/python -m analysis.research_pipeline report \
  --run-id primary-e1-20260930 --output /tmp/meps-derived-report-new
```

Run manifests preserve the exact source snapshot at execution, including uncommitted source hashes. The comparison/export helper was added afterward; its hashes are separately recorded in the export and derivation manifests. Revisions are not retroactively assigned to earlier experiments.

## Paper work still required

Independent-year E5 replication, direct-expenditure/two-part E6 comparators, reference-population/joint uncertainty, secondary multiplicity and fuller E2 robustness remain pending. This pass adds no datasets, new trained model families or hypothesis searches. It strengthens the credibility and reproducibility of the modest empirical contribution; it does not establish a new method or a submission-ready paper.
