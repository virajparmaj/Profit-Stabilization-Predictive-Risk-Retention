# Project reconstruction and data

> **Implementation update — 2026-09-30:** The original plan/evidence below is retained as a dated baseline. The corrected core pipeline and actual E1–E4 execution status are documented in [Implementation and results](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/17_IMPLEMENTATION_AND_RESULTS.md). Remaining paper requirements and protocol deviations are listed there; the study is not submission-complete.

**Updated:** 2026-09-25. **Status:** Verified repository reconstruction; corrected cohort not yet built.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

### The scientific problem that the existing work addresses

The implemented task is **retrospective classification of a same-year low-expenditure/low-acute-use label from progressively richer observed attributes**, followed by a cross-sectional analysis of spending distributions and subgroup composition. It is not yet prospective risk forecasting, retention modeling, profit optimization, or a test of behavioral interventions.

The original label is

`Y = 1[TOTEXP23 <= q30] × 1[ERTOT23 = 0] × 1[IPDIS23 = 0]`,

where the unweighted full-sample 30th percentile is **$484.40**. Because expenditure is recorded in whole dollars, the existing rounded description of a $484 cutoff yields the same classifications here. There are **5,579 positive labels out of 18,919 records**. The 18,463 positive-person-weight records represent approximately 334.53 million people; their weighted label prevalence is **30.725%**. The label identifies observed low use/spending, not low latent medical need.

The original ladder has 2, 6, 7, 8, 17, and 20 raw features in B0–B5. B1 includes general self-rated health as well as mental-health measures. B3 adds an indicator count described as chronic burden. B4 adds income/insurance/employment; B5 adds same-year office visits, outpatient visits, and prescriptions. The notebook uses a single stratified 75/25 split, seed 42, one-hot encoding of low-cardinality variables, and logistic regression, L1 logistic, nominal L2 logistic, random forest, and XGBoost. Default logistic and the explicit L2 logistic are substantively duplicate specifications here, with identical reported results: this is three main model families, not five independent families.

What was investigated, rather than implemented: incremental information across feature domains; retrospective label discrimination and probability error; descriptive spending concentration; selected-cohort cost profiles; and associations among coverage, recorded burden, utilization, and spending. Serialization, an API example, and dashboards are useful delivery artifacts but are not research contributions by themselves.

### Evidence ledger

| Observation | Evidence status | Defensible interpretation |
|---|---|---|
| Original B3 XGBoost AUROC 0.772639, Brier 0.168591 | Saved executed-notebook output; not freshly refitted | Moderate discrimination for the original retrospective label on one split |
| Original B3 logistic AUROC 0.774447, Brier 0.168068 | Saved output | Logistic is numerically slightly better on this block and split; no evidence of a meaningful difference yet |
| B0/B4/B5 XGBoost AUROC 0.579418/0.824610/0.949921 | Saved output | Additional domains predict this label; these values do not establish forecast validity or medical benefit |
| Cached five-fold B3 scores: unweighted AUROC **0.771998** | Independently recalculated from the cache | Confirms the reported arithmetic, not a new training reproduction |
| Same scores: person-weighted AUROC **0.747208** | Newly recalculated, exploratory | Evaluation weighting materially changes the reported discrimination; not proof of weighted-training superiority |
| Population mean $7,487; selected-cohort mean $2,779 | Independently recalculated | The historical selected cohort has lower same-year spending |
| Selected-cohort relative dispersion increases | Recalculated; see table below | An empirical absolute-versus-relative dispersion tradeoff exists in these cached outputs |
| Coverage gaps in low-spending labels | Recalculated under original and alternative indicator counts | Coverage is associated with label membership within broad burden strata; no causal or equal-need interpretation |
| B3 is the minimum stable model | **Not demonstrated** | Stability procedure and selection rationale are insufficient |
| Profits stabilized, retention improved, or future costs reduced | **Not demonstrated** | No premiums, contract liabilities, retention outcomes, intervention, or forward outcome evaluation |

## Data lineage and populations

| Asset | Actual role | Limitation |
|---|---|---|
| `data_raw/h251.csv` | 18,919 records from 2023 MEPS HC-251 | Cross-sectional annual observations; timing varies by item |
| `data_processed/meps_model_ready_2023.csv` | Existing 59-column derived table | Whole-sample preprocessing and construct issues require reconstruction |
| `notebooks/meps_model_ready_2023.csv` | Byte-identical duplicate of that table | A second path is not independent evidence |
| `analysis/.cache/oof.parquet` | Existing scores joined to 18,463 positive-person-weight respondents | Score arithmetic verified; training provenance incomplete |
| `data_processed/scored_members_2023.parquet` | Incompatible historical scored artifact | Exclude until regenerated and validated |

The historical positive-person-weight population is not the proposed adult SAQ population. Never paste the 18,463 denominator or its expenditure estimates into a corrected adult-results table without recomputing that population. All current monetary summaries use observed 2023 nominal all-payer expenditures.

A corrected dictionary must record original code, question text, eligibility, measurement round, allowed values, sentinel meaning, transformation, missing indicator, feature block, and weight rationale. Keep annual person identifiers, verified household identifiers, panel, strata and PSU fields outside the feature matrix unless deliberately justified. Do not infer household identity by slicing an ID without documentary verification.
