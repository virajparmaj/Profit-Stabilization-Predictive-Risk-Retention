# Paper structure, central argument and writing plan

> **Implementation update — 2026-09-30:** The original plan/evidence below is retained as a dated baseline. The corrected core pipeline and actual E1–E4 execution status are documented in [Implementation and results](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/17_IMPLEMENTATION_AND_RESULTS.md). Remaining paper requirements and protocol deviations are listed there; the study is not submission-complete.

**Updated:** 2026-09-25. **Status:** Manuscript blueprint; included abstract is explicitly preliminary, not submission-ready.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

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

## Results-to-manuscript map

| Paper asset | Source experiment | Evidence required before drafting as a result |
|---|---|---|
| Table 1: population and definitions | E0 | Corrected cohort flow, dictionary, missingness and weights |
| Table 2: compact-model comparison | E1 | Paired weighted discrimination, calibration and intervals |
| Figure 1: discrimination versus identity reproducibility | E1 + E2 | Same models, capacity and target; refit variability |
| Figure 2: expenditure frontier and zero-mass decomposition | E3 | Dollar mean/SD and CV shown together, with uncertainty |
| Table 3: integrated policy comparison | E1–E3 | Achieved capacity, membership, spend and simple controls |
| Figure/Table 4: robustness and replication | E4 + E5 | Prespecified sensitivity results and independent-year contrasts |
| Supplement | All | Full feature list, configurations, failures, broad exploratory scans and provenance |

The strongest paper is likely a focused empirical evaluation. Keep the main text centered on one decision-relevant contrast, with access composition as a secondary audit. Do not turn every interesting project observation into a competing main hypothesis.
