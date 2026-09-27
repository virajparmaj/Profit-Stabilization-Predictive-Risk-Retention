# Research advisory: from low-spending classification to a defensible empirical study

**Review date:** September 25, 2026. **Status:** research assessment and proposed protocol, not a completed paper. **Recommendation:** develop a focused empirical evaluation of low-spending cohort selection; retire the current claim that B3 has been shown to stabilize profits or to be the minimum stable model.

There is a plausible paper here, but its contribution must be earned by the next experiments. The strongest economical direction is to test whether model and feature choices that look attractive by classification accuracy also produce reproducible cohort membership and favorable expenditure distributions. Distinguish absolute spending dispersion from dispersion relative to the mean. Treat access and measured health burden as a secondary construct-validity audit. Neither cost-versus-health label bias nor the need to assess prediction instability is a new discovery.

The pasted request contained a project-material placeholder. I used this repository as the supplied project material. I inspected the preprocessing and modeling notebooks and their saved outputs, analysis scripts and report, cached predictions, raw MEPS documentation/codebook, processed datasets, chart exports, all six main research figures, and relevant dashboard/interview documentation. I independently recomputed selected descriptive results and evaluated existing cached scores. **I did not retrain the models, establish the cache's training provenance independently, or execute the proposed completed study.**

Companion files in this directory:

- `verify_existing_evidence.py`: repeatable local verification, with no model fitting or source-data changes.
- `verified_metrics.json`: exact recomputed numbers and source-file SHA-256 hashes.
- `SEARCH_LOG.md`: literature-search scope, queries, access limitations, and primary-source links.

## 1. Reconstructing the actual investigation

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

### The most important numerical reinterpretation

These are weighted descriptions of groups selected using the cached scores and the existing **unweighted** rank cutoffs. They are not corrected-model study results.

| Metric | Full positive-weight sample | Highest P(low-label), nominal 30% | Nominal 10% |
|---|---:|---:|---:|
| Records | 18,463 | 5,548 | 1,891 |
| Mean annual spending | $7,487.26 | $2,778.55 | $2,186.53 |
| Spending SD | $19,807.63 | $9,993.32 | $8,250.17 |
| Coefficient of variation, SD/mean | 2.646 | 3.597 | 3.773 |
| Zero-spending share | 14.45% | 27.61% | 40.66% |
| CV among positive spenders only | 2.417 | 3.015 | 2.836 |
| Spending >= $20,000 | 9.10% | 2.90% | 2.27% |
| Mean excess above $20,000, E[(C−20k)+] | $2,891.73 | $697.77 | $609.08 |
| Excess above $20,000 / all spending | 38.62% | 25.11% | 27.86% |
| All spending of people spending >= $20,000 / all spending | 62.93% | 46.02% | 48.62% |

Selection reduces the mean by about 63%, the SD by about 50%, and absolute expected excess above $20,000 by about 76%. Therefore, **“selection does not reduce cost variance” is contradicted by the existing data**. Higher CV and Gini do not imply larger dollar variance, a heavier asymptotic tail, greater ruin probability, or lower profits. Even the relative excess-above-$20k share falls versus the population. Each metric answers a different question.

The nominal 30% group represents **33.45% of population weight**, not 30%. The nominal 10% group represents approximately **11.09%**. Ties also make record counts exceed the exact requested fractions. Capacity must be defined explicitly before comparing policies.

### Corrections required before making scientific claims

1. **Wrong score direction in the stability calculation.** Executed notebook cell 46 uses `predict_proba(... )[:,1]`, the probability of `LOW_RISK=1`, then selects `proba <= quantile(proba, .30)`. This selects the least likely positive-label people. The later `analysis/src/fig02.py` correctly selects high probabilities. The two analyses study different groups.
2. **Segment-size stability is largely imposed by the rule.** Recomputing a quantile inside each resample forces approximately 30% membership. B0's approximately 40% reflects ties from a coarse score, not evidence of an unstable biological or financial population. The procedure holds the fitted model fixed and resamples test rows; it does not measure training-data-induced score or membership instability. A fixed-size set can change every member while retaining exactly the same size.
3. **The chronic count mixes constructs.** Preprocessing cell 115 includes `ANYLMI23`, misdescribed as mental illness, and `COVIDEVER53`, an ever-COVID indicator. `ANYLMI23` summarizes functional/activity limitations and overlaps the functional domain. Remove it from diagnosis burden; treat ever-COVID separately, rather than equating it with chronic disease. The remaining ten diagnosis indicators are a pragmatic count, not automatically a validated multimorbidity instrument; overlapping conditions also need acknowledgment. The [official HC-251 documentation](https://meps.ahrq.gov/data_stats/download_data/pufs/h251/h251doc.shtml) verifies the variable meaning.
4. **Missing does not mean absent.** Diagnosis and limitation fields are mapped to binary and filled with zero. Access indicators also turn non-yes responses into no. Rebuild from raw codes, distinguish inapplicability from unknown/refusal, and preserve uncertainty. The direction of resulting association bias is not established; the report's claim that it necessarily attenuates effects is too strong.
5. **Survey point weights do not fix uncertainty estimates.** `ci_lib.py` resamples individual records, ignoring strata and PSUs. `a07_interaction.py` fits an unweighted ordinary logistic model, despite the report's blanket weighting statement. Population inference needs a documented design-based analysis. SAQ-derived predictors also require explicit eligibility and weight handling; the [MEPS weight hierarchy and variance instructions](https://meps.ahrq.gov/data_stats/download_data/pufs/h251/h251doc.shtml) specify `SAQWT23F` for analyses involving SAQ variables and `VARSTR`/`VARPSU` for design-based variance.
6. **“Identical disease burden” is not the comparison performed.** The 63.1% versus 12.4% contrast combines everyone with at least two original indicators. Groups can differ in exact diagnoses, counts, severity, age, and diagnosis ascertainment. Use “within the 2+ indicator stratum,” then adjusted descriptive standardization with overlap checks.
7. **Overlapping intervals do not establish equivalence.** The 28.7% versus 26.9% subgroup comparison neither proves equivalence nor rules out meaningful differences. A prespecified equivalence margin and an interval for the difference would be required. The selected cells were also found exploratorily. Comparing per-unit ORs for two differently constructed counts does not establish which domain is more predictive.
8. **Same-year measurements are not baseline forecasts.** Excluding the exact label columns is useful but insufficient for a prospective claim. B5 utilization is strongly linked to spending, and B3 also contains health measurements collected during the outcome year. A temporal availability diagram is required for any forecasting extension.
9. **No office visits is not no ambulatory contact.** Of the 545 original “disengaged” records, **104 have outpatient visits**. Low office use does not establish nonadherence, preventability, unmet need, or a future emergency. Ratios of acute spending to total spending also rise mechanically when office spending is absent. Use a literal group name and show absolute acute dollars and event rates.
10. **A stale scored file is demonstrably incompatible.** `scored_members_2023.parquet` contains 15,268 records, only 42 positive labels, and **3,973 label disagreements** against the canonical table on a one-to-one ID join. Exclude it from evidence until regenerated with provenance. Cached OOF values lack a manifest containing input/model hashes and fold assignments.
11. **The same holdout was used for comparisons and model choice.** The notebook chooses the model family by mean AUROC across blocks, then assigns B3 manually. That is not a predefined minimum-feature decision rule, and the holdout is not an independent confirmation of the selected choice.
12. **Terminology needs restraint.** `TOTEXP23` is all-payer healthcare spending, not an insurer's net claim liability. Dollars below/above $5,000 are capped/excess expenditures, not observed “routine” versus “catastrophic” care types. No observed access marker does not mean “genuinely healthy and engaged.”
13. **The insured comparison is not continuously insured.** Figures 5 and 6 label `INSCOV23 != 3` as “insured all year,” but that condition includes coverage for only part of the year. Use “insured for at least part of the year,” or reconstruct continuous coverage from monthly indicators and eligibility months. Restricting to under-65 people also does not eliminate all Medicare coverage. These facts weaken the report's claims to have removed coverage and Medicare composition effects.
14. **Preprocessing precedes the split.** The preprocessing notebook imputes behavioral items and fits category mappings on the full dataset before writing the model-ready file. This is not direct use of test outcomes, but it breaks a strict train-only preprocessing protocol. Fit these steps within training folds and retain raw category meanings in the canonical dictionary.

**Code evidence map:** [selection-direction calculation, notebook JSON line 2376](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/notebooks/profit_stabilization_meps_executed.ipynb:2376); [misdescribed limitation variable, preprocessing notebook line 1932](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/notebooks/eda_pre-processing.ipynb:1932); [cached OOF implementation](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/src/prep.py:31); [record bootstrap](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/src/ci_lib.py:20); [unweighted regression](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/src/a07_interaction.py:22); [correct high-score selection in the later figure](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/src/fig02.py:6). Notebook line links refer to serialized JSON; cell numbers in the text identify the notebook-view equivalents.

**Already demonstrated:** retrospective label discrimination and several descriptive spending associations. **Strongly suggested:** selection metrics can tell materially different stories, and the low-spending label includes people with recorded burden or access markers. **Not demonstrated:** membership stability after refitting, a smallest sufficient feature set, prospective utility, causal mechanisms, medical ground truth, or transferable financial benefit.

## 2. Closest existing research and the novelty boundary

This is a targeted scoping review, not a systematic review or a guarantee that no equivalent study exists. Searches prioritized 2021–2026 and followed foundational work. arXiv, publisher/journal sources, AHRQ benchmarks, and conference proceedings were accessible. Google Scholar and Semantic Scholar searches were attempted directly and through indexed results, but their search interfaces were inaccessible; I do not claim complete coverage of those databases. Search-engine crawl dates were not treated as publication dates.

The following entries distinguish what a paper directly studied from the remaining opportunity in this project. “Not covered” means outside the study described in the inspected source, not absent from all literature. Published AUROCs below are not directly comparable to your different outcome and population.

### Closest conceptual and methodological competitors

**R1. Riley & Collins (2023), “Stability of clinical prediction models developed using statistical or machine learning methods,” Biometrical Journal.** Question: how stable are individual risk estimates across development samples? Methods/data: simulations and clinical examples including GUSTO-I; regression and ML, bootstrap refitting, prediction/calibration/classification instability assessment. Result: apparently reasonable aggregate models can have substantial individual instability; the paper specifies practical diagnostics. It does not jointly evaluate low-spending MEPS cohort selection and absolute/relative expenditure distributions. **Overlap:** very strong on your proposed stability methodology. **Remaining contribution:** a careful application that quantifies downstream cohort and expenditure consequences; bootstrap refitting itself is not novel. [Paper](https://arxiv.org/abs/2211.01061).

**R2. Zanger-Tishler, Nyarko & Goel (2024), “Risk scores, label bias, and everything but the kitchen sink,” Science Advances.** Question: can adding predictors improve a proxy while harming the intended outcome? Methods/data: formal analysis, partially synthetic recidivism data, and a synthetic release approximating the Obermeyer healthcare dataset; simple health-only versus richer feature models predicting future costs. Result: the simpler healthcare model selected more high-need and Black patients across enrollment capacities. It does not test your MEPS low-spending rule or spending-dispersion/stability combination. **Overlap:** directly anticipates a B3-versus-B4/B5 “more information can be worse” argument. **Remaining contribution:** measured effects on low-spending cohort membership and spending profiles; do not claim to discover the general phenomenon. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC10980258/).

**R3. Oskam, van Kleef & Douven (online 2023; journal issue 2024), “Heteroscedasticity of residual spending after risk equalization,” European Journal of Health Economics.** Question: can financial risk differ even when mean residual spending is equalized? Methods/data: Dutch administrative data used for the 2021 risk-equalization model; subgroup residual SD and 99.5th percentiles, portfolio simulations and risk-sharing analyses. Result: residual variability can sustain selection incentives despite mean compensation. This studies spending net of payments, unlike your all-payer outcome. **Overlap:** strong prior art against “mean cost is not financial risk” as a new contribution. **Remaining contribution:** reproducible evidence about learned low-spending classifiers and cohort stability, without importing their insurer-profit conclusions. [Paper](https://doi.org/10.1007/s10198-023-01592-9).

**R4. Singh & Ramamurthy (2019), “Understanding racial bias in health using the Medical Expenditure Panel Survey data,” arXiv.** Question: does cost-based prediction inherit racial disparities in MEPS? Methods/data: longitudinal Panels 19 and 20, logistic regression using first-year demographic, diagnosis, health and limitation information, followed by reweighing. Result: mitigation changed predicted high-expenditure representation to 11% for Black versus 9.9% for White respondents, with balanced accuracy just above 71%. It studies next-year high spending and race, rather than your low-spending cohort stability. **Overlap:** same dataset family and cost/need mismatch. **Remaining contribution:** coverage/access and low-spending selection analysis with materially different outcomes—not “first evidence of MEPS label bias.” [Full text](https://arxiv.org/html/1911.01509v1).

**R5. Obermeyer et al. (2019), “Dissecting racial bias in an algorithm used to manage the health of populations,” Science.** Question: does a commercial cost-based score identify health need equitably? Methods/data: algorithm audit against healthcare utilization and clinical information in a health-system population. Result: Black patients were sicker at comparable scores; correcting the discrepancy was estimated to increase their share receiving additional help from 17.7% to 46.5%. It is not a MEPS low-spending or stability benchmark. **Overlap:** establishes the central cost-versus-need warning. **Remaining contribution:** a specific empirical audit with proper definitions; your cross-sectional access markers are not equivalent to their clinical validation. [Paper](https://doi.org/10.1126/science.aax2342).

**R6. Fleishman & Cohen (2010), “Using Information on Clinical Conditions to Predict High-Cost Patients,” Health Services Research.** Question: which clinical summaries predict next-year high spending? Methods/data: MEPS Panels 1–8; logistic models developed on 52,918 observations and validated on 61,155; diagnosis counts, DCG scores, self-rated health and functioning. Result: the combined model achieved c=0.836; functioning and self-rated health added only modest discrimination beyond other predictors. It does not evaluate low-spending cohort membership stability. **Overlap:** directly covers your chronic/functional feature comparison and has stronger temporal evaluation. **Remaining contribution:** endpoint-specific incremental value or selection consequences, not the discovery that functional limitations predict spending. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC2838159/).

### Recent adjacent studies and benchmarks

| Source | Question, methods, dataset, and reported result | Not covered; overlap and remaining opportunity |
|---|---|---|
| **R7. Hernandez-Viver & Mitchell, AHRQ Statistical Brief 560 (March 2025)**, [2018–2022 concentration benchmark](https://www.meps.ahrq.gov/data_files/publications/st560/stat560.shtml) | Weighted MEPS spending distributions and characteristics of expenditure groups. In 2022, the top 5% accounted for 49.7% of spending; the bottom 50% for 2.8%. | Your 2023 48.7% and 2.9% observations largely replicate a known distribution. No learned-selection/refit experiment. Use as validation/background, not novelty. |
| **R8. Zhang, Ding & Peng (2021)**, [OOP factor ranking and selection](https://pmc.ncbi.nlm.nih.gov/articles/PMC8184979/) | MEPS 2016–2017; forward/backward selection, RF and LASSO votes for predictors of OOP spending above $1,000. Reported test MSE on its transformed target improved from 0.462 to 0.382; selected insurance, age, asthma, family size, race and office visits. | Already combines feature reduction and expenditure prediction. Different outcome, no cohort stability or total-spending tail evaluation. A compact model alone is insufficient novelty. |
| **R9. Gao & Chan (June 2026)**, [transferable medical-cost workflow](https://www.frontiersin.org/journals/health-services/articles/10.3389/frhs.2026.1742807/full) | MEPS example with 3,064 people, 2,955 positive spenders, predominantly Medicare-age adults; OLS/robust/GLM/mixture/tree/ensemble comparisons. Reports GBR as best overall and strong chronic-burden associations; survey design omitted by the authors. The inspected methods do not clearly identify the MEPS year. | Strong overlap with a generic “research-to-dashboard pipeline” pitch. Not a survey-aware low-spending stability audit. Do not adopt its design omissions or infer clinical/policy effectiveness. |
| **R10. Kresin et al. (July 2026), arXiv preprint**, [financial vulnerability after COVID-19](https://arxiv.org/html/2607.15446v1) | MEPS 2019/2021, OOP costs >10% of family income; weighted subgroup analyses, logistic/RF/gradient boosting, cross-year testing. Reports AUROC 0.857 for boosting, 0.840 RF and 0.838 logistic; RF has higher F1; temporal deterioration described as modest. | Affordability plus standard ML plus temporal comparison is already occupied. Different from total spending and membership stability. Reported associations involving income/spending partly reflect its constructed target; not a template for causal claims. |
| **R11. Yang (2024)**, [Diagnostics for Regression Models with Semicontinuous Outcomes](https://arxiv.org/abs/2401.06347), linked to Biometrics | Develops residual diagnostics for zero-plus-positive outcomes, applicable to Tobit, Tweedie and two-part models; simulations and a MEPS expenditure application. Reports detection of misspecification and evaluation of predictive distributions. | Zero inflation and inadequate ordinary diagnostics are established issues. Your opportunity is to show how zero mass versus positive spending affects selected-cohort metrics, not invent semicontinuous modeling. |
| **R12. Wang et al., AISTATS 2023**, [Probabilistic Conformal Prediction Using Conditional Random Samples](https://proceedings.mlr.press/v206/wang23n.html) | Conditional generative draws construct prediction sets; theory, simulations and nine public benchmarks including MEPS19/20/21. Reports marginal coverage guarantees and sharper sets than comparators. | Prediction sets are not cohort stability or portfolio risk. MEPS benchmark names do not establish that their target is your `TOTEXP23`. Simply adding conformal prediction is not sufficient novelty. |
| **R13. Zaffran et al., ICML 2023**, [Conformal Prediction with Missing Values](https://proceedings.mlr.press/v202/zaffran23a.html) | Theory, simulations and critical-care data; missing-data augmentation for coverage conditional on missingness patterns. Reports that marginal validity can coexist with undercoverage in missingness subgroups and proposes a remedy. | Relevant to your eligibility/missingness audit, not a direct MEPS spending competitor. A new MEPS application would need a specific new empirical finding, and ordinary conformal guarantees do not automatically cover complex-survey deployment. |
| **R14. Oskam, van Kleef & van Vliet (2025 issue; online November 2024)**, [high-risk pooling](https://onlinelibrary.wiley.com/doi/full/10.1111/jori.12500) | Historical Dutch spending/risk-adjuster data identify an undercompensated 1% with average annual undercompensation €6,050. Residual-based pooling reduces mean undercompensation across chronic-disease groups by 42%, outperforming the examined outlier-sharing comparison. | Financial benefit needs payments, longitudinal data and an explicit mechanism. Your spending-only classifier cannot claim equivalent profit, reinsurance or selection-incentive results. |
| **R15. Matijevic & Yau (February 2026), arXiv preprint**, [bootstrap regularization](https://arxiv.org/abs/2602.11360) | A neural-network training regularizer embeds bootstrap stability; simulations plus GUSTO-I, Framingham and SUPPORT. Reports prediction deviations of 0.019 versus 0.059 in GUSTO-I and 0.057 versus 0.088 in Framingham while maintaining discrimination. | Stability interventions already exist. Your minimum extension should evaluate the existing simple models before attempting a new stability algorithm. Different population and endpoint. |

An additional foundational lead is Sushmita et al., **Population Cost Prediction on Public Healthcare Datasets**, ACM Digital Health 2015, DOI 10.1145/2750511.2750521. Its existence and venue are verified by the [conference program](https://wp.cs.ucl.ac.uk/acm-digitalhealth-2015/detailed-programme/) and [author publication list](https://faculty.washington.edu/ankurt/publications.html). The primary full paper was inaccessible in this review, so I have not treated secondary descriptions of its dataset years or performance as verified comparative evidence. Retrieve it before submission.

**Has essentially the same work already been published?** The broad ingredients have: MEPS prediction, compact feature sets, functioning/chronic comparisons, proxy-label bias, prediction instability, and mean-versus-financial-risk distinctions. I did not identify an exact study joining your low-spending selection policy, corrected feature ladder, training-refit membership stability, and absolute-versus-relative cost evaluation. That is a **candidate empirical gap**, not a certified novelty claim. The difference must change an empirical conclusion or model-selection decision, not merely combine established plots.

## 3. Novelty-gap analysis

| Possible contribution | Defensibility and effort | What would actually make it research-worthy |
|---|---|---|
| **Joint evaluation of membership reproducibility and expenditure distributions** | Best fit to the existing infrastructure; moderate extension; novelty conditional | Show that classification-only or headcount-only evaluation selects a materially different model/policy than membership and spending criteria, with paired uncertainty and explicit tradeoffs |
| **Absolute versus relative dispersion under low-spending selection** | Strong existing descriptive clue; low additional analysis, moderate validation | Show a robust result across corrected models and selection capacities; decompose zero spending and benchmark against simple selection rules. Merely observing SD/mean arithmetic is insufficient |
| **Insurance/utilization features improve a proxy but alter burden/access composition** | Important but crowded by R2/R4/R5; moderate effort | Demonstrate the incremental change at matched capacity and comparable baseline composition, with an independent measured outcome. Without ground truth, call it construct discordance, not harm proved |
| **Survey estimand changes model conclusions** | New local clue: 0.772 versus 0.747 AUROC; low-to-moderate effort | Show reproducible changes in rankings or selected populations under valid weighting and sampling, not just two versions of a metric |
| **Eligibility/missingness creates apparent feature gains** | Plausible, not established; moderate effort | Same eligible respondents across blocks, explicit missingness-only and demographic baselines, and prespecified preprocessing sensitivity reveal an interpretation reversal |
| **Functional burden contributes more to a tail endpoint than to low-label AUROC** | Reasonable secondary analysis; modest novelty after R6 | Remove construct overlap, compare incremental held-out performance on both endpoints, avoid OR magnitude comparisons, and establish useful incremental effect |
| **Simple model is sufficient for a defined operational tolerance** | Cheap to test; crowded contribution | Prespecified noninferiority plus cost/membership outcomes and measured complexity benefit; one favorable split is insufficient |
| **Temporal failure or stability of the same policy** | Higher credibility, additional data work | A frozen prospective protocol, no person overlap, year-one measurements to year-two outcomes, appropriate longitudinal weights; distinguish calendar transport from forecasting |
| **Reproducibility/coding failure case study** | Already supported as a local engineering finding | Could support a methods note only if its general mechanism and practical consequences are demonstrated beyond an isolated coding mistake |
| New dataset, architecture, SHAP plot, dashboard, or exact model–year combination | No credible novelty by itself | MEPS is established; existing models are standard. SHAP/latency can explain a result, not substitute for one |

The highest-value addition is measurement of **who moves and what decision changes**, not more model families. Do not start with a deep network, ensemble stack, energy benchmark, or large hyperparameter search.

## 4. Eight candidate research questions

The distinctness assessments are qualitative judgments, not probabilities of acceptance.

**RQ1 — Does classification performance identify reproducible low-spending cohorts?**

- **Question:** At 30% target-population capacity, do B2/B3/B4/B5 logistic and XGBoost models with similar or better held-out AUROC produce more stable membership after training resampling?
- **Hypothesis:** AUROC and fixed-quota headcount stability do not reliably rank models by weighted membership disagreement.
- **Why it matters:** Resource lists and cohort analyses depend on identities, not just the number selected.
- **Established / unknown:** R1 establishes prediction instability; the measured disagreement and model-ranking consequences for this selection task remain untested.
- **Existing evidence:** Ladder and flawed headcount bootstrap; no valid membership experiment yet.
- **Additional work:** Correct direction/constructs, paired refits, fixed reference respondents, weighted Jaccard/turnover and individual selection probabilities.
- **Distinctness / risk:** Moderate as an empirical application with consequences; low as a generic stability claim. It may show close agreement between metrics and no practically important instability.

**RQ2 — Does choosing lower expected spending change absolute and relative dispersion differently?**

- **Question:** Across capacities 10%, 20%, 30%, 40%, and 50%, how do mean, SD, CV, zero-spending mass, and expected excess spending change for selected cohorts?
- **Hypothesis:** Mean and SD decrease while CV can increase; zero mass explains part, but not necessarily all, of the increase.
- **Why it matters:** “Stable” can reverse meaning depending on the denominator.
- **Established / unknown:** R3/R11 and standard variance identities cover the general concepts; corrected low-label policies and their consequences remain to be measured.
- **Existing evidence:** Clear cached-score absolute/relative tradeoff; positive-spender CV is nonmonotone under tighter selection.
- **Additional work:** Refit corrected models, matched-capacity baselines, paired design-based intervals, two-part decomposition and simple selection controls.
- **Distinctness / risk:** Moderate only with substantive model-policy consequences; otherwise a descriptive replication. All changes may be predictable composition effects with no additional insight.

**RQ3 — What does adding coverage and utilization change beyond label AUROC?**

- **Question:** At equal weighted capacity, do B4/B5 select different access-marker and measured-burden profiles than B3, and are those changes robust to age/health composition?
- **Hypothesis:** Some AUROC gains coincide with greater selection of people with low use and access markers, without proportionate improvement in independently held-out health indicators.
- **Why it matters:** Model quality is relative to the target being optimized.
- **Established / unknown:** R2/R4/R5 already show proxy problems; the direction and magnitude in this low-spending setting are unknown.
- **Existing evidence:** Coverage gaps and B4/B5 performance gains, but no paired selected-cohort analysis.
- **Additional work:** Split B4 into insurance and SES additions; compare B3+utilization separately; reserve at least one health measure from predictors; report descriptive standardization and support diagnostics.
- **Distinctness / risk:** Low-to-moderate; high overlap with R2. Measured burden is itself imperfect and may be mechanically related to inputs. Coverage differences alone do not prove unfairness.

**RQ4 — Does the feature-block conclusion survive correct survey targeting?**

- **Question:** Does the preferred model/block change when evaluating the population targeted by the relevant MEPS weights rather than the convenience distribution of records?
- **Hypothesis:** Weighted evaluation changes some subgroup performance or model-selection conclusions.
- **Why it matters:** A “national population” conclusion requires that estimand.
- **Established / unknown:** Survey weighting is standard; the model-ranking sensitivity here is untested.
- **Existing evidence:** Cached-score weighted AUROC is about 0.025 lower, without confidence bounds.
- **Additional work:** Harmonized eligibility, weighted evaluation of identical predictions, normalized weighted-training sensitivity and design-based uncertainty.
- **Distinctness / risk:** Low-to-moderate standalone, useful secondary contribution. The AUROC shift may leave all practical comparisons unchanged.

**RQ5 — Are behavioral gains or failures driven by questionnaire eligibility?**

- **Question:** How much of the B0-to-B3 performance progression persists within adults eligible for the same instruments, after adding age/sex and missingness indicators?
- **Hypothesis:** Instrument eligibility and sentinel patterns explain a material portion of observed differences, but not all clinical signal.
- **Why it matters:** “Behavior does not work” should not mean “children were not asked the questions.”
- **Established / unknown:** Missingness-dependent behavior is established generally; its contribution in these blocks is unknown.
- **Existing evidence:** Adult-only behavioral questions and extensive SAQ structural missingness.
- **Additional work:** Eligible-sample ladder, missingness-only baseline, within-fold imputation and alternate count construction.
- **Distinctness / risk:** Moderate as a documented interpretation reversal; weak if changes are small. Complete-case restriction can introduce a new selection bias and must not be treated as a universal fix.

**RQ6 — Does functioning add endpoint-specific information beyond diagnosis burden?**

- **Question:** After separating diagnosis and functional constructs, is the incremental value of functioning larger for $20k exceedance than for low-spending-label classification?
- **Hypothesis:** Functioning contributes useful tail discrimination/calibration even where low-label AUROC changes little.
- **Why it matters:** Feature value depends on which outcome matters.
- **Established / unknown:** R6 establishes incremental prognostic information; the endpoint-specific magnitude with this compact feature set is unknown.
- **Existing evidence:** Exploratory heatmaps and an unweighted logit, compromised by overlapping counts.
- **Additional work:** Corrected counts, separate classifier outcomes, matched held-out tests, nonlinear age adjustment and prespecified interactions.
- **Distinctness / risk:** Low-to-moderate; likely secondary. The published pattern could disappear after removing the functional indicator from the chronic count.

**RQ7 — Is logistic regression practically sufficient?**

- **Question:** Is corrected B3 logistic regression noninferior to XGBoost in AUROC within 0.01, while producing comparable calibration and cohort spending and lower membership instability?
- **Hypothesis:** Logistic is competitive and may be more reproducible for this small feature set.
- **Why it matters:** Complexity should purchase a measured benefit.
- **Established / unknown:** Simple-versus-complex comparisons are common; paired sufficiency for this selection objective is unknown.
- **Existing evidence:** Logistic slightly outperforms XGBoost on B3 in the stored split.
- **Additional work:** Paired repeated evaluation, a justified prespecified margin, bootstrap refits, optional fit-time/model-size measurements.
- **Distinctness / risk:** Low standalone; useful baseline/result. Failure to reject a difference is not noninferiority, and 0.01 is a proposed margin requiring justification before execution.

**RQ8 — Does low-spending selection persist prospectively?**

- **Question:** Among linked MEPS respondents, do year-one selected low-spending groups remain low spending in year two, and do access markers identify discordant transitions?
- **Hypothesis:** Same-year performance overstates next-year discrimination; selected members show nontrivial transition rates.
- **Why it matters:** This is the necessary bridge to a risk forecast.
- **Established / unknown:** R4/R6 already perform MEPS prospective prediction; the stability/access behavior of this exact selection policy is unknown.
- **Existing evidence:** None longitudinal in the supplied analysis.
- **Additional work:** One documented two-year longitudinal panel at minimum, frozen year-one feature availability, longitudinal weights, person-disjoint evaluation; a second panel for transport.
- **Distinctness / risk:** Potentially stronger empirical contribution, more work. Attrition, panel overlap, timing ambiguity and weak external precision can prevent a convincing claim.

**Recommended combination:** RQ1+RQ2 as the main study; RQ3/RQ4/RQ5 as bounded robustness analyses. RQ7 is an important comparator, not a separate paper. Keep RQ6 exploratory unless it survives reconstruction. Add RQ8 before claiming forward risk management.

## 5. Minimum publishable extension: exact experiment plan

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

## 6. Hidden observations worth preserving

**The strongest existing clue is the divergence among evaluation targets.** The cached model lowers dollar SD while increasing CV, and the notebook's near-fixed headcount does not test membership at all. The research question is whether these distinctions change which compact model or policy one would choose. The local code bug is motivation for the audit, not the paper's entire contribution.

**Logistic is competitive with XGBoost.** Its B3 AUROC is higher by about 0.0018 and Brier lower by about 0.0005 in the saved split. This is too small and uncertain for a superiority claim but makes a simple baseline indispensable. The original averaged-across-blocks leaderboard obscures this point.

**Population weighting affects apparent performance.** The same cached probabilities give 0.772 unweighted and 0.747 person-weighted AUROC. This does not prove a statistically significant gap, but it is enough to require explicit estimands and a weighted analysis in a nationally framed study.

**Correcting burden definitions changes the group you are talking about.** As a limited sensitivity analysis, I removed `ANYLMI23` and `COVIDEVER53` from the original count, retaining the original yes/no mapping for the remaining ten indicators. The 3+-indicator/zero-office group shrank from 545 records (9.21M weighted people) to **315 records (4.83M)**. Its spending >=$20k rate rose from **8.36% to 13.69%**, acute spending share from **53.80% to 61.07%**, and low-label share fell from **52.03% to 45.12%**. These are new exploratory descriptions, with no survey-adjusted intervals or clinical validation; they demonstrate sensitivity, not a corrected final result.

The uninsured-versus-insured contrast within 2+ indicators persisted under that limited count sensitivity: **58.37% versus 8.78%** had the low label, versus 63.08%/12.39% originally. This merits follow-up, but it remains an unadjusted broad-stratum comparison with 168 uninsured records under the ten-item definition.

**Zero mass is part of the selected-pool story.** It nearly doubles in the 30% group and increases further at 10%. The positive-spender CV pattern changes under tighter selection, so “the remaining tail gets steadily worse” is an inadequate explanation.

**The report contains post hoc subgroup discovery.** Scripts such as `a04_segscan.py` and selected pair comparisons are useful exploration. A small-cell narrative found after scanning many groups cannot be promoted to confirmatory evidence using ordinary intervals alone. Register exact contrasts now and test them on another year if they become central.

## 7. Strongest defensible research argument

**Evidence-honest version available now:**

> Previous research has established that healthcare spending is concentrated, expenditure can be an imperfect proxy for medical need, and individual model predictions can be unstable across development samples.
>
> However, it remains insufficiently characterized in this project whether model choices for low-spending classification align with reproducible cohort membership and with both absolute and relative expenditure dispersion.
>
> We investigate these questions using MEPS 2023, a compact feature ladder, and standard classification models.
>
> Our existing experiments evaluate retrospective label discrimination and cross-sectional spending distributions; the proposed extension evaluates corrected constructs, training-refit membership changes, and matched-capacity expenditure tradeoffs.
>
> Our current audit shows that the existing headcount metric cannot establish membership stability, and cached selected-cohort estimates show lower mean spending and dollar dispersion alongside higher relative dispersion.
>
> These findings suggest that classification, membership reproducibility and expenditure variability should be evaluated separately before interpreting a low-spending cohort as stable.
>
> The proposed contribution is a reproducible empirical test of whether those distinctions change model and cohort-selection conclusions, with a secondary audit of measured burden and access composition.

For the completed paper, replace the last three paragraphs with the **actual corrected effect sizes and uncertainty**, identifying the precise model/policy comparison that changes the decision. If no comparison changes a defensible conclusion, describe a replication or validation study; do not advertise a new general principle already established by R1–R3.

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

## 9. Proposed paper structure

1. **Abstract:** state the retrospective selection problem, target population, primary comparison and actual corrected results. Give both absolute and relative expenditure effects. End with a bounded evaluation implication, not a profit or clinical-benefit promise.
2. **Introduction:** explain the distinct decisions implied by a spending label, fixed cohort capacity, stable identity and predictable dollars. Use the original project as motivation without presenting a coding error as a new statistical principle. State two primary hypotheses and one secondary audit.
3. **Related Work:** distinguish prediction stability (R1/R15), proxy labels and feature selection (R2/R4/R5), financial residual variability (R3/R14), and MEPS cost/feature benchmarks (R6–R12). Explain exactly what joint empirical comparison remains.
4. **Research Question / Hypotheses:** define the target population, selection capacity, time horizon, primary contrasts and practical margins. Say which hypotheses arose after exploration and which are tested on a later replication sample.
5. **Data:** describe HC-251, eligibility, weights/design, outcome creation, measurement timing, missingness, and corrected indicator definitions. Show the flow from 18,919 original records to each analytic population. No “12 chronic diseases” language.
6. **Methodology:** define score direction, the two selection policies, weighted metrics, membership instability, zero/positive spending decomposition and treatment of ties. Give the absolute/relative metric equations. Attribute established methods rather than claiming them as inventions.
7. **Experimental Setup:** specify grouped splits, training/calibration/reference separation, preprocessing, model settings, baseline rules, replicate procedures, computational environment and external validation if performed.
8. **Results:** lead with the primary decision-relevant comparison. Then show classification/calibration, membership refits and spending metrics on the same cohorts. Report null results, uncertainty, achieved capacities and tail counts.
9. **Robustness / Ablation Analysis:** show whether conclusions survive corrected constructs, weights, eligibility, alternate capacities/thresholds, feature order and zero-mass controls. Put broad scans in a labeled exploratory appendix.
10. **Discussion:** explain why disagreement among metrics matters for this use case. Distinguish measured expenditure, recorded illness, unmet need and financial liability. Compare actual findings with R1–R6; discuss when simple models suffice and when they do not.
11. **Limitations:** acknowledge exploratory origin, single-year scope if applicable, target-population restrictions, no latent-need ground truth, survey dependence/nonresponse, uncertainty in tails, and no intervention or insurer accounting evaluation.
12. **Conclusion:** make one claim supported by the primary contrast. Identify prospective validation as the next step if it has not been done. Release the reproducible analysis, not just dashboard screenshots.

## 10. The paper's central story and readiness decision

**Proposed title:** *Evaluating Low-Spending Healthcare Cohorts: Membership Stability and Expenditure Dispersion in MEPS*.

**One-sentence contribution:** A reproducible empirical evaluation of whether compact low-spending classifiers yield the same model-selection conclusions when judged by label accuracy, membership reproducibility, and absolute versus relative spending dispersion.

**Research gap:** These evaluation targets are established separately, but their joint consequences for this operational low-spending policy and feature ladder remain untested; exact novelty requires final literature checking and a substantive empirical result.

**Primary research question:** At matched population capacity, does choosing a model by retrospective label accuracy also choose a model with reproducible cohort identities and favorable expenditure profiles?

**Primary hypothesis:** At least one prespecified model/feature comparison will produce materially different conclusions across those criteria. This must be tested, not assumed.

**Novelty claim to pursue:** A bounded empirical finding about which evaluation choices change low-spending cohort decisions, supported by a transparent reusable protocol. No new algorithm, no first discovery of label bias, and no first discovery that means conceal risk.

**Most important experiment:** E2 paired whole-pipeline refitting, evaluated on fixed reference people, connected to E3 expenditure outcomes at the same capacity. This directly tests the original “stable segment” premise.

**Most important result needed:** A robust, interpretable discrepancy between accuracy-based choice and membership/expenditure-based choice that survives corrected variables, survey targeting, and simple baselines. The existing CV increase by itself is not enough.

**Minimum additional experiments:** E0 repair/reproduction and E1–E4. Avoid a full new modeling project. If those tests only reproduce established principles without a useful empirical distinction, prioritize E5 or E7 rather than drafting an inflated novelty claim.

**Potential abstract — working version, not a completed-results abstract:**

> Low realized healthcare expenditure is often treated as evidence of low risk, yet classification accuracy, cohort membership reproducibility, and expenditure dispersion describe different properties. We propose an empirical evaluation of compact low-spending classifiers using the 2023 Medical Expenditure Panel Survey. A preliminary audit of an existing feature-ladder pipeline identifies a reversed score-selection rule, a fixed-quantile headcount metric that does not establish membership stability, and overlap between diagnosis and functional-burden constructs. Recalculation using the existing cached predictions finds that the nominal 30% selected cohort has lower mean expenditure ($2,779 versus $7,487) and lower spending standard deviation ($9,993 versus $19,808), but a higher coefficient of variation (3.60 versus 2.65). These retrospective, exploratory estimates motivate a corrected comparison of logistic regression and gradient boosting under shared sampling, survey-aware evaluation, and whole-pipeline refitting. The completed study will test whether model choices based on classification performance remain defensible when cohort identity and expenditure distributions are assessed jointly. It will not infer prospective health risk, intervention effects, or insurer profitability from same-year expenditure labels.

Replace the preliminary/audit language with corrected study estimates and their intervals only after executing the protocol. This version honestly describes the present evidence; it is not ready to submit as a finished empirical manuscript.

**Three strongest figures/tables:**

1. **Accuracy versus membership-instability figure:** paired models at matched capacity, with refit uncertainty, showing the decision-relevant mismatch if present.
2. **Selected-cohort expenditure frontier:** mean, dollar SD and CV together, plus zero-mass/positive-spender decomposition; avoids misleading “risk got worse” language.
3. **Integrated comparison table:** baseline and feature blocks, AUROC/Brier/calibration, turnover, mean/excess spending and measured access/burden composition, with intervals and sample sizes.

**Closest competitors:** Riley & Collins for instability; Zanger-Tishler et al. for feature additions under proxy bias; Oskam et al. for financial variability beyond means; Singh & Ramamurthy and Fleishman & Cohen for MEPS prediction and health/cost discordance. The proposed difference is the tested decision consequence of jointly evaluating a low-spending selection policy—not a new model/data combination. R9 and R10 also make generic MEPS workflow/affordability pitches less distinctive.

**Claims not to make:**

- B3 is the minimum stable model, XGBoost is superior, or behavioral variables are intrinsically uninformative.
- Selection fails to reduce absolute cost variance, proves a heavier distributional tail, or cannot stabilize budgets.
- Low spending measures health, or absence of an observed access flag proves health/engagement.
- The coverage comparison holds medical need constant, proves underdiagnosis, or identifies causal access effects.
- Two subgroups are equivalent because their confidence intervals overlap.
- Missing-as-zero necessarily biases an association downward.
- Zero office visits means no ambulatory care, preventable emergency use, or future deterioration.
- $20,000 is a validated clinical catastrophic threshold or an actual policy's reinsurance attachment.
- A same-year score predicts future spending; panels observed in the same calendar year supply longitudinal validation.
- All-payer expenditure reduction establishes insurer profit, retention gains, safe pricing, fairness, or regulatory suitability.

**Readiness judgment:** The repository has enough substance to justify a focused research extension, but **does not currently support the paper claimed by its README**. E0–E4 are the concrete minimum for the recommended retrospective study, followed by honest interpretation of whatever they show. E5 materially improves credibility; E7 is required for prospective claims. A concise empirical preprint or workshop paper is a plausible first target after those checks, not a guaranteed outcome. A stronger journal submission would benefit most from independent replication or prospective validation, not from more dashboard functionality.
