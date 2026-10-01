# Concrete implementation roadmap

> **Implementation update — 2026-09-30:** The original plan/evidence below is retained as a dated baseline. The corrected core pipeline and actual E1–E4 execution status are documented in [Implementation and results](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/17_IMPLEMENTATION_AND_RESULTS.md). Remaining paper requirements and protocol deviations are listed there; the study is not submission-complete.

**Updated:** 2026-09-25. **Status:** Implementation specification only; pipeline code has not been changed.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

## Scope and recommended first implementation

Build a small reproducible Python research pipeline using the existing raw data, feature-domain idea and model families. Start with E0 and a feasibility run; preserve notebooks as historical evidence. This folder plans that implementation. The proposed modules and commands below do not exist yet.

**First development milestone:** one command builds a corrected cohort with an explicit dictionary, validates grouped splits and target construction, trains B3 logistic and B3 XGBoost, and writes provenance-complete held-out scores. That unlocks the scientific work; a dashboard does not.

## Proposed module boundaries

Place the future package under `analysis/research_pipeline/` and tests under `analysis/tests/research_pipeline/`. Keep existing `analysis/src/` report generation intact until replacement results are validated.

| Proposed module | Responsibility | Output / acceptance contract |
|---|---|---|
| `config.py` + `configs/primary_2023.yaml` | Validate experiment settings and freeze a protocol hash | Population, features, label rule, model settings, policies, seeds and uncertainty method are explicit |
| `dictionary.py` | Codebook-backed field mapping and sentinel semantics | Every feature has definition, timing, eligibility, category map and block |
| `cohort.py` | Raw ingestion, population filters, corrected counts, missingness flags | Unique person IDs; flow counts; weight sums; no source mutation |
| `splits.py` | Verified household-grouped outer and reference splits | Saved person/fold IDs; no group overlap; shared across models |
| `targets.py` | Legacy and train-estimated label definitions | Cutoff learned only where allowed; threshold saved per fit |
| `models.py` | Fold-local sklearn pipelines and weighted fits | Correct class-probability lookup; frozen model settings; full refit support |
| `selection.py` | Weighted capacity and frozen-threshold policies | Deterministic outcome-independent ties; achieved capacity logged |
| `metrics.py` | Classification, membership and spending estimands | Named denominators, boundary handling and unit-tested formulas |
| `survey.py` | Documented survey replicate weights / estimators | Strata/PSU-preserving design; benchmark agreement; separate uncertainty modes |
| `refits.py` | E2 full preprocessing/model refits on fixed reference people | Per-refit scores, membership and failures; no silent seed replacement |
| `experiments.py` | Execute E0–E6 configurations and contrasts | Structured long-format metrics and paired effects |
| `reporting.py` | Regenerate paper tables and figures from results | Every output links to a run manifest and contrast ID |
| `__main__.py` | Validated CLI with explicit legacy/corrected modes | Refuses mismatched caches and incomplete protocol settings |

## Work packages and completion gates

| Order | Work package | Concrete deliverable | Must pass before next stage |
|---|---|---|---|
| P0 | Preserve evidence and lock environment | Input hashes, version list, isolated venv and dependency lock | Cached scores cannot masquerade as a fresh run |
| P1 | Resolve scientific variables | Dictionary, population flow, legacy/corrected cohorts | Sentinel, count, eligibility and weight checks in document 09 |
| P2 | Implement splits, targets and policies | Split manifest and deterministic selection helpers | No leakage; correct direction; ties and capacity verified |
| P3 | Implement paired base models | B3 logistic/XGBoost held-out scores with run manifest | One prediction per expected person/fold; class mapping correct |
| P4 | Validate survey estimators and refit driver | Benchmark estimates and full-pipeline refit output | Design-respecting uncertainty and reference-set integrity |
| P5 | Feasibility pilot | 20 refits on anchor models plus small design-replicate smoke run | Runtime/memory/errors measured; estimates labeled nonfinal |
| P6 | Run E1–E4 | Frozen paired results, 200 initial refits, 1,000 initial design replicates | Monte Carlo precision assessed; all failed runs disclosed |
| P7 | Strengthen validation | E5 frozen replication and E6 direct-cost/RF comparisons | Harmonized definitions; no hidden person overlap or retuning |
| P8 | Assemble manuscript | Final tables, figures, result-linked text and limitations | Every claim satisfies the evidence gates in document 12 |

P1–P4 are scientific and engineering prerequisites. Do not spend substantial compute on a pipeline that has not passed them. Counts of replicates are starting budgets, not guarantees of sufficient precision: at 200 independent refits, worst-case selection-frequency Monte Carlo SE is about 0.035. More replicates may be needed for fine distinctions.

## Minimum compute scope

E1's main D/C/B0/B2/B3/B4/B5 × two models × five folds × two seeds gives 140 base fits before any inner tuning. The initial E2 set of four anchors × 200 refits gives 800 fits, plus base fits. The feasibility subset uses four anchors × 20 = 80 refits. Record wall time, peak memory, software/hardware and threads in the pilot before estimating full runtime. Do not invent a completion time from fit counts alone.

Keep algorithm seeds fixed for the primary E2 resampling comparison. Use identical replicate plans across candidate models for paired comparisons. Assess algorithm-seed variation separately; mixing it silently into training-sample variation changes the question.

## Proposed CLI contract — not executable yet

```text
python -m analysis.research_pipeline build --config analysis/research_pipeline/configs/primary_2023.yaml
python -m analysis.research_pipeline validate --config analysis/research_pipeline/configs/primary_2023.yaml
python -m analysis.research_pipeline run --experiment E1 --config analysis/research_pipeline/configs/primary_2023.yaml
python -m analysis.research_pipeline run --experiment E2 --config analysis/research_pipeline/configs/primary_2023.yaml
python -m analysis.research_pipeline report --run-id <verified-run-id>
```

Run outputs should live under `analysis/research_runs/<run-id>/`, with a configuration copy, manifest, cohort flow, split IDs, score files, long-form estimates, replicate diagnostics, logs, tables and figures. Keep personal machine paths out of a public manifest; use repository-relative paths and hashes there.

## Decisions to resolve during P1–P4

Verify household identity and SAQ eligibility from the codebook; select and validate the exact survey-variance implementation; set category scaling and missingness rules; record practical margins; and choose a nonoverlapping replication cohort after checking available releases. These are implementation gates, not reasons to invent study results. If a decision changes an estimand, version the protocol and explain it.

Use existing settings initially. Add tuning only if a diagnosed modeling problem justifies it. The objective is a credible comparison, not an exhaustive performance contest.
