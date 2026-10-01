# MEPS research pipeline

This package evaluates same-year low-spending cohort selection. It reconstructs scientific variables from raw HC-251 data, learns preprocessing and endpoint cutoffs inside training partitions, and compares classification, membership reproducibility and expenditure distributions.

## Setup

Use Python 3.11 and obtain the public 2023 HC-251 CSV from the [official MEPS release](https://meps.ahrq.gov/data_stats/download_data/pufs/h251/h251doc.shtml). Place it at `data_raw/h251.csv`. The full release, person-level outputs and environments are ignored by Git.

```sh
python3.11 -m venv .venv-research
.venv-research/bin/python -m pip install -r analysis/research_pipeline/requirements-lock.txt
.venv-research/bin/python -m pytest analysis/tests/research_pipeline -q
```

The lock records the environment used for this implementation. Platform-specific wheels can differ; source/package/config fingerprints accompany every run. Tests use synthetic fixtures; the local HC-251/R-benchmark integration check skips explicitly when raw data are absent.

## Commands

Run from the repository root. Run IDs are immutable: rerunning an existing ID fails instead of silently loading old predictions.

```sh
.venv-research/bin/python -m analysis.research_pipeline validate --run-id my-validation
.venv-research/bin/python -m analysis.research_pipeline run --experiment E1 --run-id my-e1 --inference
.venv-research/bin/python -m analysis.research_pipeline run --experiment E2 --run-id my-e2-pilot --pilot
.venv-research/bin/python -m analysis.research_pipeline run --experiment E2 --run-id my-e2
.venv-research/bin/python -m analysis.research_pipeline.robustness --config analysis/research_pipeline/configs/primary_2023.yaml --prefix my-e4
.venv-research/bin/python -m analysis.research_pipeline report --run-id my-e1 --output /tmp/my-e1-derived-new
```

`build` and `validate` reconstruct and validate the cohort/design and emit the same core artifacts. `validate` is not a replacement for the pytest suite or the independent R check. `E1` also performs E3 expenditure evaluation; `--inference` adds the prespecified B3 logistic-minus-XGBoost contrast using survey PSU replicates. `E2` uses four anchors regardless of the E1 block/model list. `--pilot` reduces E2 to 20 refits per anchor and conditional inference to 50 evaluation replicates; pilot status is saved in the manifest and prominently labeled in the report.

Outputs are written to `analysis/research_runs/<run-id>/`. Models are trained from source each run; legacy joblib/cache files are never loaded. Model serialization and production deployment are outside this package's purpose.

## Statistical choices

- Primary cohort: SAQELIG=1, AGE42X>=18, SAQWT23F>0 and PERWT23F>0. The weight defines the SAQ adult population, not the original all-age target.
- DUID is the documented dwelling-unit ID. Paired outer validation uses grouped folds; E2 uses grouped 60/20/20 training/calibration/reference partitions.
- Counts retain affirmative items plus unknown/code counts; all-unknown rows have missing counts rather than zero. ANYLMI23 and COVIDEVER53 are excluded from primary diagnosis burden. Counts are pragmatic indicators, not validated clinical scales.
- Numeric preprocessing is training-only. Known categorical codes, including distinct reserved codes, have a fixed encoding dictionary. FAMINC23/TTLP23X preserve negative income values.
- The endpoint combines a training-estimated weighted expenditure p30 with zero ER and inpatient use. E2 holds the initial training endpoint fixed across refits. The $484.40 legacy endpoint is an explicit E4 sensitivity.
- Select highest P(Y=1). Weighted capacity uses the nearest ranked prefix; hash-based ties depend on ID/seed, never outcomes. Actual capacity is reported. E2 separately freezes a model-specific probability threshold on calibration data; ties can change its capacity.
- E1 AUROCs are calculated within folds, then weighted by evaluation weight mass. They are not pooled across fold-specific targets. Repeated seeds are not independent samples.
- E2 draws n_h−1 PSUs with replacement within each complete survey stratum, duplicates selected training PSU rows and applies n_h/(n_h−1) weight rescaling. Preprocessing and models are refitted. Algorithm seed is held fixed. Zero-member sampled PSUs remain part of the design rather than being silently omitted.
- Survey evaluation uses the same Rao–Wu design multipliers for paired models, with full-design zero contributions for domains. Singleton strata fail explicitly. Normal intervals use mean squared replicate deviations from the point estimate. They condition on fitted predictions and fixed validation partitions; they do not incorporate all model-training uncertainty.
- The primary B3 contrast is prespecified. Other model/endpoint summaries and E4 sensitivities are descriptive; no family of unadjusted significance claims or proof of noninferiority is emitted.

Method references: [MEPS design documentation](https://meps.ahrq.gov/data_stats/download_data/pufs/h251/h251doc.shtml), [R survey bootstrap weights](https://r-survey.r-forge.r-project.org/survey/html/bootweights.html), and [Riley & Collins on prediction instability](https://arxiv.org/abs/2211.01061).

## Independent survey check

With R and the `survey` package installed in an isolated library:

```sh
Rscript analysis/research_pipeline/validate_survey.R data_raw/h251.csv /tmp/meps-survey-check.csv
```

Compare its mean/SE with a `validate` run's `survey_mean.json`. This validates the Taylor mean against R, not every nonlinear bootstrap statistic. Synthetic tests additionally check known variance, PSU resampling and domain behavior.

## Limits

The study is exploratory and retrospective. The corrected population differs from the historical cache population. SAQ timing can extend into early 2024; inputs are not a prospective 2023 baseline. Report refit distributions as learning sensitivity, not population confidence intervals. E4 adult-core and missingness variants change the measurement problem and must be named. No independent-year replication, longitudinal forecast, direct-cost baseline, clinical intervention evaluation or insurer-liability analysis is implied by this package.

## Artifact integrity and verification

Version 2 runs generate `REPORT.md` before hashing outputs and atomically marking completion. Reports, configuration and required scientific files are verified on reuse. Completed runs cannot be overwritten. Fit events are flushed incrementally to `fit_log.jsonl`, including warnings before failures, interruptions, and E2 base fits. Failed/interrupted/running runs cannot produce completed-results exports.

The `report` command requires a new directory outside its source run. Legacy manifests remain read-only: their scientific inputs are hash-checked, while the original unhashed report is explicitly excluded. Derived reports and applicable tables record parent-manifest and generator hashes. Exports and figures also require fresh destinations. Exported run manifests describe the full local run; their person-level files are intentionally absent from the aggregate export, which has its own manifest.

Weighted summaries require all declared folds/seeds to be finite and present; otherwise the metric is undefined, with valid/expected counts. Refit summaries expose valid/expected replicate counts. Random expenditure summaries use one deterministic seeded ranking and the same within-fold quota rule as the model policies.

`configs/verification_2023.yaml` selects the original B3 models and seed 42 for a five-fold verification run. `python -m analysis.research_pipeline.verify_completed --help` describes the reproducible targeted-comparison and aggregate-export command. See `research-paper/19_VERIFICATION_AND_PR_READINESS.md` for exact commands, outputs and remaining paper requirements.
