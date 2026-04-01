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
