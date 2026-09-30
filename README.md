# Low-Spending Healthcare Cohort Research

This MEPS project studies whether models judged by classification accuracy also produce reproducible cohort membership and favorable expenditure distributions at the same population capacity.

The original repository name, **Profit-Stabilization-Predictive-Risk-Retention**, reflects its initial motivation. The available data measure retrospective all-payer expenditure. They do not establish insurer profit, retention, clinical need or future cost effects.

## Research implementation

The source-built package in `analysis/research_pipeline/` adds:

- A corrected adult SAQ cohort with documented eligibility and survey weights.
- Diagnosis and functional counts that preserve unknown responses and remove construct overlap.
- Shared dwelling-unit validation splits, training-only preprocessing and training-derived outcome thresholds.
- Paired logistic/XGBoost feature-block comparisons, weighted metrics and matched-capacity selection.
- Full-pipeline training refits on fixed reference people, with membership disagreement and Jaccard overlap.
- Absolute and relative spending summaries, survey-aware conditional intervals, and declared robustness variants.
- Immutable run manifests, meaningful scientific tests and aggregate research reports.

The research target is a low-expenditure/zero-ER/zero-inpatient label measured in the same year. High predicted probability selects the low-spending cohort. Cohort size, member identity, dollar SD and relative dispersion are evaluated separately.

## Run the study

Download the public [2023 HC-251 MEPS release](https://meps.ahrq.gov/data_stats/download_data/pufs/h251/h251doc.shtml) and place its CSV at `data_raw/h251.csv`. From the repository root:

```sh
python3.11 -m venv .venv-research
.venv-research/bin/python -m pip install -r analysis/research_pipeline/requirements-lock.txt
.venv-research/bin/python -m pytest analysis/tests/research_pipeline -q
.venv-research/bin/python -m analysis.research_pipeline validate --run-id my-validation
.venv-research/bin/python -m analysis.research_pipeline run --experiment E1 --run-id my-e1 --inference
.venv-research/bin/python -m analysis.research_pipeline run --experiment E2 --run-id my-e2-pilot --pilot
.venv-research/bin/python -m analysis.research_pipeline run --experiment E2 --run-id my-e2
```

Every run ID must be new. Source data, person-level scores, model environments and large outputs remain local under ignored directories. Aggregate results and scientific interpretation belong in `research-paper/`.

See `analysis/research_pipeline/README.md` for the exact statistical choices, E4 robustness runner, R survey benchmark and limitations. See `research-paper/16_IMPLEMENTATION_PROMPT.md` for the reusable execution prompt.

## Research materials

| Location | Role |
|---|---|
| `research-paper/` | Research questions, prior art, protocol, implementation plan, evidence register and paper blueprint |
| `analysis/research_pipeline/` | Corrected executable study package and pinned environment |
| `analysis/tests/research_pipeline/` | Synthetic scientific invariants and optional local-data integration checks |
| `analysis/research_runs/` | Ignored immutable local run outputs |
| `analysis/research_review/` | Historical audit and exact cached-score rechecks |
| `notebooks/` | Original exploratory notebooks, preserved for provenance |
| `analysis/src/` and `analysis/ANALYSIS_REPORT.md` | Historical analysis and figure pipeline |
| `site/` | Existing analytics presentation; not evidence of a validated production inference service |

## Interpreting the evidence

The historical pipeline contained a reversed probability-selection rule in its stability notebook, a quantile-based headcount measure that could not establish member stability, overlapping diagnosis/function constructs, and survey/missingness issues. Its claim that B3 was the “minimum stable model” is not an established conclusion. Historical notebooks and charts are preserved rather than silently rewritten.

The new implementation tests a bounded empirical contribution: whether membership reproducibility and expenditure evaluation change the conclusions drawn from ordinary classifier comparisons. Those evaluation concepts already exist in prior research; the contribution must come from the actual comparative findings and their robustness.

The study remains exploratory and retrospective. Independent-year replication, prospective panel validation, direct-cost baselines and broader uncertainty analysis are separate research requirements. Neither successful tests nor a working model pipeline alone make a completed research paper.
