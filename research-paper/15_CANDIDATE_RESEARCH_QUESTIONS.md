# Eight candidate research questions and selection rationale

**Updated:** 2026-09-25. **Status:** Candidate hypotheses assessed; none established by the planned experiments yet.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

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

## Selected scope for the planned paper

Use RQ1 and RQ2 as the central investigation; treat RQ3–RQ6 as targeted robustness or secondary analysis rather than six independent discovery claims. RQ7 supplies a useful compact-model comparison. RQ8 requires longitudinal work and should remain a separate extension unless prospective prediction becomes the paper's main objective.

The candidate list is an options record. It does not authorize selecting whichever question produces the smallest p-value after inspecting new results. Changes to the main question belong in a dated protocol-deviation log.
