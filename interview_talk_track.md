# 30-Minute Technical Talk + Demo (Talk Track + Slide Outline)

Audience: ML/DS + policy (UChicago Harris style)
Goal: Explain the ML pipeline and why the model ladder shows the minimum stable structure for profit stabilization.

---

## 0) Timed Talk Structure (30 minutes total)

1. Problem framing + policy motivation (3 to 4 min)
2. Data + label construction (4 to 5 min)
3. Feature blocks + modeling approach (6 to 7 min)
4. Results + stability evidence (6 to 7 min)
5. Corporate/policy implications (3 to 4 min)
6. Live demo (5 to 7 min)
7. Closing + Q&A buffer (1 to 2 min)

---

## 1) Slide Outline + Speaker Notes

### Slide 1: Title + one-sentence thesis
**Title:** Profit Stabilization via Minimum Stable Risk Structure
**Thesis (say this verbatim):**
"Using MEPS 2023, I show that a compact feature set that includes chronic burden is the minimum structure that yields stable, policy-usable low-risk segmentation."

**Speaker notes (30 to 45 sec):**
- Briefly define the objective: identify stable low-risk members for pricing stability and retention.
- Set expectations: I will show the model ladder, why B3 is the inflection point, and how this becomes a deployable system.

---

### Slide 2: Problem + fairness gap in premium pricing
**Main point:** Low-utilization members often pay the same premiums as high-risk members, creating a fairness and efficiency gap.

**Speaker notes (1 min):**
- Explain the policy motivation: current premium structures often pool low-risk and high-risk populations.
- Argue the need for stable segmentation under uncertainty, not just high AUC.
- Position the problem: identify a low-risk segment that is stable enough to inform pricing and retention decisions.

---

### Slide 3: Data overview
**Facts (from notebooks):**
- MEPS 2023 consolidated file (HC-251)
- Unit: adult person-year
- n = 18,919 (model-ready rows)

**Speaker notes (1 min):**
- Explain why MEPS is appropriate: national, policy-relevant, detailed utilization and cost.
- Clarify that this is a single-year cross-section for the core analysis.

---

### Slide 4: Label definition funnel
**Label logic (verbatim):**
- LOW_SPEND = bottom 30% of TOTEXP23
- LOW_RISK = LOW_SPEND + (ERTOT23 = 0) + (IPDIS23 = 0)
- Prevalence: LOW_SPEND ~ 0.300, LOW_RISK ~ 0.295

**Speaker notes (1.5 min):**
- Explain why low cost alone is not stable enough: acute shocks destabilize cost.
- Add the acute utilization constraint to define a stable, conservative low-risk cohort.
- Emphasize this is an operational label used to test the minimum predictive structure.

---

### Slide 5: Feature blocks and the model ladder
**Blocks:**
- B0: behavior (exercise, smoking)
- B1: + mental health
- B2: + functional limitations
- B3: + chronic burden
- B4: + SES and insurance
- B5: + utilization (non-label)

**Speaker notes (1.5 min):**
- Explain the core design: cumulative blocks to test minimal structure, not maximal accuracy.
- Make the claim early: the key is the inflection point at B3.

---

### Slide 6: Modeling pipeline
**Key steps:**
- Train/test split (25% test, stratified)
- Preprocessing in pipeline (standardize numeric, one-hot categorical)
- Model families: logistic, RF, XGBoost
- Leakage control: exclude TOTEXP23, ERTOT23, IPDIS23 from predictors

**Speaker notes (1.5 min):**
- Stress that the pipeline is reusable at inference (saved joblib pipeline).
- Each block is a valid production candidate; not a single monolithic model.

---

### Slide 7: Block AUC table (XGBoost)
**AUC values (XGB):**
- B0 0.579
- B1 0.686
- B2 0.711
- B3 0.773
- B4 0.825
- B5 0.950

**Speaker notes (1.5 min):**
- Point out the inflection at B3: first time the model becomes meaningfully separable.
- B4 and B5 improve AUC, but add fairness and leakage concerns.

---

### Slide 8: Calibration + Brier
**Brier (XGB):**
- B0 0.202
- B1 0.190
- B2 0.184
- B3 0.169
- B4 0.151
- B5 0.081

**Speaker notes (1 min):**
- Define calibration and why it matters for policy decisions.
- B3 is not just accurate; it is also probability-reliable enough for segmentation.

---

### Slide 9: Bootstrap stability (core contribution)
**Bootstrapped SD (B3):**
- AUC SD ~ 0.00741 (CV ~ 0.96%)
- Low-risk rate SD ~ 0.000496 (CV ~ 0.17%)

**Speaker notes (1.5 min):**
- Explain stability as the policy-usable criterion.
- After B3, segment size is nearly invariant under resampling.
- This is why B3 is the minimum stable structure.

---

### Slide 10: Why not B4/B5?
**B4 (SES/insurance):** fairness sensitivity, regulatory risk, harder to justify.
**B5 (utilization):** proxy leakage, less actionable for early intervention.

**Speaker notes (1.5 min):**
- B4 and B5 are useful as benchmarks but not necessary for stability.
- Policy context: avoid features that are ethically or legally sensitive.

---

### Slide 11: Corporate/policy significance
**Implications:**
- Stable low-risk cohort supports pricing stability and retention
- Reduces volatility in premium pools
- Creates a defensible analytic basis for tiering and outreach

**Speaker notes (1 min):**
- Translate the ML results into insurance operations: segmentation drives pricing, retention, and member engagement.
- Emphasize stability over maximized accuracy as the governance-friendly choice.

---

### Slide 12: Demo placeholder + recap
**Recap points (say verbatim):**
1. Minimal stable structure is B3 (behavior + mental + functional + chronic)
2. Stability is the central success metric
3. Deployable pipeline + analytics app operationalize the result

**Speaker notes (30 to 45 sec):**
- Transition to the demo or to Q&A depending on timing.

---

## 2) Live Demo Script (5 to 7 minutes)

**Goal:** Show the model and stability story inside the product interface.

1. Start on Overview
- Show that the app is an analytic product, not just a chart gallery.

2. Upload and validate a cohort
- Use demo CSV or drag-and-drop upload
- Point out schema validation against the live model card

3. Scoring page
- Show batch scoring and that predictions come from a saved B3 pipeline

4. Segmentation and Low-Risk Profile
- Highlight the low-risk segment definition and profile differences

5. Risk Lab or Uncertainty
- Show stability or bootstrap-related outputs

6. Fairness
- Explain why SES is monitored rather than used in the deployable model

7. Pricing Simulator (if time)
- Link stable segmentation to pricing scenarios

8. Reports/Export (optional)
- Emphasize reproducible outputs for policy or stakeholder review

---

## 3) Objection Handling and Q&A (1 to 2 minutes)

**Q1: Why use the bottom 30% threshold?**
A: It is a policy-aligned, quantile-based definition that is robust to prevalence shifts and consistent with insurer segmentation practice.

**Q2: Why not use survey weights?**
A: The goal is segmentation stability for model deployment, not population inference. We use person-level features for predictive consistency, not weighted population estimates.

**Q3: Why not just use B5 if it is best?**
A: B5 is closest to realized cost behavior, so it inflates AUC and risks proxy leakage. It is less actionable for early intervention.

**Q4: Why exclude SES from the deployable model?**
A: SES introduces fairness and regulatory concerns; B3 already yields stability without those sensitivities.

**Q5: How generalizable is this beyond MEPS 2023?**
A: The pipeline is year-agnostic, and the next step is temporal validation across panels.

**Q6: What are the next steps?**
A: Temporal validation, SHAP comparisons (B3 vs B5), and a formal fairness audit.

---

## 4) Quick Reference Numbers (for confidence in Q&A)

- n = 18,919 (model-ready 2023 rows)
- LOW_SPEND rate = 0.3000
- LOW_RISK rate = 0.2949
- XGB AUC by block: B0 0.579, B1 0.686, B2 0.711, B3 0.773, B4 0.825, B5 0.950
- XGB Brier by block: B0 0.202, B1 0.190, B2 0.184, B3 0.169, B4 0.151, B5 0.081
- Bootstrap SD (B3): AUC 0.00741, LOW_RISK rate 0.000496

---

## 5) Sources used for this script
- notebooks/eda_pre-processing.ipynb
- notebooks/profit_stabilization_meps.ipynb
- /Users/veerr_89/Work/website/risk-stability-insights/notes/00_overview.md

---

## 6) ML Engineer Interview Answer (Detailed Written Version)

If an interviewer asked me to walk through the project end to end, I would answer it like this:

### 1. Problem Framing

I framed this as a **probabilistic binary classification** problem. The target is the probability that a person is **low risk**, where `LOW_RISK = 1` means the person is in the bottom 30% of annual spend and also had **zero ER visits** and **zero inpatient days** in 2023.

This is a classification problem because the final label is binary: low risk or not low risk. It is also a probabilistic modeling problem because I do not just want a hard yes or no. I want a **probability score**, because insurance decisions are usually tiered. A person with a 0.82 probability of being low risk should be treated differently from someone at 0.51.

The business goal is to build a stable way to identify healthier, lower-cost members who may justify lower premiums or targeted retention offers. The social goal is to use that same segmentation logic to explore whether coverage can be expanded for underinsured or uninsured groups without creating an unstable risk pool. I am careful not to claim that low utilization always means true health, especially for uninsured groups, but it is still a useful operational starting point for scenario analysis.

### 2. Data Preprocessing And Feature Engineering

I used a processed **MEPS 2023 adult person-year dataset** with **18,919 rows** and **59 columns**. The data included demographics, self-reported physical and mental health, chronic condition burden, functional limitations, insurance status, income, and non-label utilization variables such as office visits and prescriptions.

The first preprocessing step was **leakage control**. Leakage means the model is given information that directly reveals the answer. Because the label uses `TOTEXP23`, `ERTOT23`, and `IPDIS23`, I removed those fields from the predictor set. That matters because otherwise the model would look artificially strong but would not be valid in production.

I organized features into a cumulative ladder:

- `B0_behavior`: exercise and smoking
- `B1_mental`: self-rated physical health, self-rated mental health, K6 distress, PHQ-2
- `B2_functional`: limitation count
- `B3_chronic`: chronic condition count
- `B4_ses_ins`: poverty, income, employment, insurance coverage
- `B5_util_nonlabel`: office visits, outpatient visits, prescriptions

That design let me answer a deeper question than “what model is best?” It let me answer “what is the **minimum feature structure** needed before the signal becomes stable and usable?”

For preprocessing inside the pipeline, I used:

- **One-hot encoding** for categorical or low-cardinality survey-coded variables. This means converting category values into machine-readable indicator columns.
- **Standardization** for continuous numeric variables. This means putting them on a comparable scale so models like logistic regression train more reliably.
- **Sparse missingness handling by preservation**, not crude imputation. MEPS has many sentinel survey codes like `-1` or `-15`, and a small amount of true nulls in fields like employment or self-rated health. I preserved those as informative categories instead of filling them with a mean, because in survey data “missing” can itself carry information.

The most important engineered features were:

- `LIMIT_CT`: aggregate count of functional limitations
- `CHRONIC_CT`: aggregate count of chronic conditions
- grouped health blocks rather than many disconnected raw variables

These matter because low-risk insurance status is not explained well by one behavior alone. It is better captured by a combination of behavior, mental health, function, and chronic burden.

Alternative approaches I considered but did not use:

- Raw diagnosis flags for every condition: more detailed, but noisier and harder to explain
- Interaction features: could help, but would reduce transparency early in the project
- Target encoding: powerful, but riskier for leakage and less interview-friendly
- Survey weights in training: useful for population inference, but my goal here was predictive segmentation stability, not national prevalence estimation
- Student status as a direct model feature: I kept student analysis downstream in scenario exploration rather than inside the deployable risk model

### 3. Baseline Model

I started with **logistic regression** as the baseline because it is simple, fast, and interpretable. Logistic regression estimates the log-odds of the positive class as a linear combination of the inputs, so it gives me a clean first read on whether there is usable signal at all.

My first baseline was logistic regression on the `B0_behavior` block only. That model reached:

- **AUC = 0.586**
- **Approximate accuracy = 0.705**
- **Recall = 0.000** at the default threshold

Here, **accuracy** means overall percentage of correct predictions. **Recall** means the share of truly low-risk people the model successfully captures. In this case, accuracy looked superficially decent only because about 70.5% of the sample is not low risk. The model was mostly predicting the majority class and missing almost all true low-risk people.

That baseline told me two things:

1. Behavior alone is not enough.
2. Accuracy by itself is a weak metric for this problem because the class distribution is imbalanced.

### 4. Model Exploration

I compared several model families across every feature block:

- **Logistic Regression**
  Why I used it: strong baseline, easy to interpret, stable on tabular data.
  Strength: transparent coefficients and fast training.
  Weakness: assumes mostly linear relationships unless I manually add interactions.

- **Random Forest**
  Why I used it: strong tabular baseline for nonlinear structure.
  Strength: captures interactions automatically and is robust to mixed feature types.
  Weakness: probability calibration is often weaker, and forests can be less efficient than boosting on structured tabular problems.

- **XGBoost**
  Why I used it: gradient-boosted trees are often one of the strongest choices for tabular risk data.
  Strength: captures nonlinear patterns, handles mixed signals well, and usually gives excellent ranking performance.
  Weakness: more tuning-sensitive and less immediately interpretable than logistic regression.

- **Neural Networks**
  Considered but not pursued deeply.
  Reason: this is a moderate-sized tabular dataset, and in that setting boosted trees usually outperform standard neural nets unless I invest heavily in architecture and tuning. That added complexity was not justified for the research question.

The key result from model exploration was that **feature depth mattered more than algorithm choice**. At `B3`, logistic regression, random forest, and XGBoost all landed in roughly the same range. That told me the big unlock was not a fancy model. It was adding the right health structure, especially chronic burden.

### 5. Training And Evaluation Strategy

I used a **75/25 train-test split** with **stratification**. Stratification means the train and test sets keep roughly the same low-risk prevalence, which is important when the positive class is about **29.49%**.

I evaluated models using four main metrics:

- **Accuracy**: how often predictions are correct overall. In this problem, high accuracy can be misleading because a model can ignore the minority class and still look decent.
- **Precision**: of the people predicted to be low risk, how many really are low risk. High precision matters because low precision could lead to underpricing people who are actually risky.
- **Recall**: of all truly low-risk people, how many the model finds. High recall matters because low recall means we miss good candidates for lower-cost coverage.
- **AUC-ROC**: how well the model ranks low-risk people above non-low-risk people across thresholds. AUC is useful here because I care about ranking quality, not only one fixed cutoff.

I also used two probability-quality diagnostics:

- **Brier score**: average squared error of predicted probabilities. Lower is better. It tells me whether predicted probabilities are close to reality.
- **Calibration curve**: compares predicted probability with observed probability. Good calibration matters because insurers need the scores to mean something, not just rank well.

For the selected XGBoost family, the AUC by cumulative block was:

- `B0 = 0.579`
- `B1 = 0.686`
- `B2 = 0.711`
- `B3 = 0.773`
- `B4 = 0.825`
- `B5 = 0.950`

That progression is the core empirical story. `B3` is the first point where separation becomes meaningfully strong.

For `B3 + XGBoost`, the main holdout metrics were:

- **AUC = 0.773**
- **Brier = 0.169**
- **Precision = 0.573**
- **Recall = 0.421**
- **Approximate accuracy = 0.737**

Interpretation:

- AUC around `0.77` means the model has good, though not perfect, ability to separate low-risk from non-low-risk members.
- Brier around `0.17` means the probability estimates are reasonably well aligned with observed outcomes.
- Precision around `0.57` means more than half of the members flagged as low risk really are low risk.
- Recall around `0.42` means the model captures a meaningful share of the true low-risk population without being overly aggressive.

### 6. Hyperparameter Tuning

I want to describe this part honestly: I did **constrained manual tuning and model comparison**, not a giant automated hyperparameter sweep.

Why tuning matters:

- It controls model complexity.
- It helps reduce overfitting.
- It can improve ranking quality and probability estimates.

The settings I used were:

- **Logistic regression**:
  standard logistic, `L1`, and `L2` regularized variants
- **Random forest**:
  `n_estimators=400`, `min_samples_leaf=10`
- **XGBoost**:
  `n_estimators=600`, `max_depth=4`, `learning_rate=0.05`, `subsample=0.9`, `colsample_bytree=0.9`, `reg_lambda=1.0`

I did not use a full **Grid Search** or **Bayesian Optimization** loop. Grid search means trying every combination in a predefined parameter grid. Bayesian optimization means using past results to choose promising new settings more efficiently. Both are valid, but I deferred them for two reasons:

1. The main research question was about the **minimum stable feature structure**, not squeezing out the last 0.5% of AUC.
2. The early experiments already showed that moving from `B0` to `B3` changed performance much more than small parameter changes did.

So the tuning strategy was deliberate: keep models well-regularized and credible, but focus effort on the feature ladder and stability analysis.

### 7. Final Model Selection

The final deployed model was **`B3_chronic + XGBoost`**.

There are two reasons for that choice.

First, `B3` is the **inflection point** in the ladder. It is the first block where discrimination becomes strong enough and segment stability becomes operationally reliable.

Second, XGBoost was the strongest overall algorithm family across the full ladder. It had the best mean AUC across blocks and the best overall Brier performance in the model leaderboard. Importantly, at `B3`, logistic regression and XGBoost were very close. I see that as a strength, not a weakness. It means the project is not depending on one fragile algorithm trick. The feature structure is doing the heavy lifting.

I did **not** deploy `B4` or `B5` even though they scored higher.

- I rejected `B4` for deployment because SES and insurance variables raise fairness and regulatory concerns.
- I rejected `B5` for deployment because utilization variables are very close to realized cost behavior. They improve AUC, but they are less actionable for early intervention and can behave like proxy leakage.

So my final selection logic was: choose the first block that is accurate, calibrated, and stable enough to be useful, while still staying explainable and governance-friendly.

### 8. Key Insights And Impact

The most important modeling insight was that **chronic burden is the minimum stabilizing signal**. Behavior and mental health help, but they are not enough on their own. Once I add functional limitations and especially chronic condition count, the model becomes much more reliable.

The second big insight was about **stability**. I ran **300 bootstrap resamples** on the test predictions. Bootstrapping means repeatedly resampling the evaluation set with replacement to measure how much the results move around.

For `B3`, the bootstrap summary was:

- **AUC mean = 0.7725**
- **AUC SD = 0.00741**
- **Low-risk rate mean = 0.3003**
- **Low-risk rate SD = 0.000496**

Those numbers matter because they show that the size of the predicted low-risk segment is extremely stable. That is exactly what an insurer would care about if the output will influence pricing tiers, retention strategy, or targeted acquisition.

Operationally, insurers could use the model in three ways:

- Identify a defensible low-risk segment for lower-premium or retention offers
- Size outreach opportunities in currently underserved groups
- Support analytics products that score cohorts, return `low_risk_probability`, and assign a simple risk tier

I kept the business interpretation conservative. This model supports **segmentation and scenario analysis**, not direct premium optimization. MEPS does not contain full plan-level premium economics or insurer profit margins, so I treat revenue impact as directional: a more stable low-risk segment can reduce volatility in the risk pool and improve the precision of targeting, which should help pricing discipline and member acquisition.

### 9. Limitations And Future Work

There are four main limitations.

First, this is a **single-year cross-sectional dataset**, so the next step is temporal validation across future MEPS releases or panels.

Second, low utilization can reflect **unmet need**, not just true health. That is especially important for uninsured populations. So I frame uninsured expansion as a scenario-sizing use case, not proof that the uninsured subgroup is genuinely healthier.

Third, the label is operational, not clinical. It is useful for segmentation, but it is still based on spend and acute utilization rules rather than a full actuarial risk construct.

Fourth, fairness still matters even when I exclude SES from deployment. The model can still inherit structural patterns from the data, so subgroup auditing is necessary.

The next improvements I would make are:

- Temporal validation across years
- SHAP analysis comparing `B3` and `B5`
- Formal fairness auditing across race, income, and insurance subgroups
- Threshold optimization for specific business goals like higher precision or higher recall
- Stronger production validation around schema checks and score monitoring

### Likely Follow-Up Questions

**Why not optimize for accuracy?**  
Because accuracy hides class imbalance. My baseline already showed that a model can get about `70.5%` accuracy while finding essentially none of the true low-risk members.

**Why not just deploy `B5` since it is best on AUC?**  
Because `B5` is closer to realized cost behavior, which makes it less actionable and more vulnerable to proxy leakage. I used it as an upper-bound benchmark, not as the governance-friendly deployment choice.

**Why not use SES features in production?**  
Because `B4` improves prediction, but it raises fairness and regulatory concerns. `B3` already gives me a stable segment without needing those features.

**Why no survey weights?**  
Because I am solving a predictive segmentation problem, not estimating a nationally weighted prevalence. If I were doing policy inference, weights would matter much more.

**Why no neural net?**  
Because this is moderate-sized tabular data. In that setting, boosted trees usually give a better accuracy-to-complexity tradeoff and are easier to govern.

**What did production look like?**  
I serialized the final pipeline with `joblib` and exposed a lightweight FastAPI `/score` endpoint that returns `low_risk_probability` and a simple `risk_tier`. That means the exact preprocessing and model logic used in training can be reused at inference time without retraining.
