# MEPS 2023 Tail-Risk Analysis — Interview Deliverable

**Dataset:** MEPS HC-251, 2023 full-year consolidated file (18,919 person-years × 1,374 columns)
**Analysis frame:** 18,463 person-years with a positive survey weight (`PERWT23F`), representing 334.5M people
**All population figures are survey-weighted.** 456 zero-weight rows are excluded from weighted estimates.
**Reproduce:** scripts in `analysis/src/`, numbers in `analysis/insight_metrics.json`, charts in `analysis/figures/`

---

## Part 1 — What this project is actually asking, and what the data can answer

### The stated research question

> Can low-risk healthcare members be reliably identified using a reduced, behaviour-oriented feature set, and what is the minimum predictive structure needed to stabilise cost-risk segmentation under uncertainty?

### What the project has already established

| Existing result | Value |
|---|---|
| Model-ready table | 18,919 × 59, built from 51 selected raw fields |
| `LOW_SPEND` | bottom 30% of `TOTEXP23` (threshold **$484**) |
| `LOW_RISK` | `LOW_SPEND` **and** zero ER visits **and** zero inpatient discharges → 5,579 records (~29.5% unweighted) |
| `CHRONIC_CT` | count of 12 condition flags · `LIMIT_CT` count of 6 functional-limitation flags |
| Deployed model | XGBoost on the **B3_chronic** block, AUC ≈ 0.773 |
| Stability evidence | bootstrap variance of low-risk **segment size** |

I re-ran the deployed pipeline (`notebooks/models/low_risk_model_B3_chronic_xgb.joblib`) under a clean 5-fold cross-validation and reproduced it: **out-of-fold AUC 0.772**. The headline result is real and replicable.

### What the dataset *can* establish

- The **cross-sectional shape** of healthcare cost: where dollars concentrate, how fat the tail is, and how that shape differs between observable segments.
- **Who a pool contains** and how much of a pool's expected cost is tail-driven — which is the actual pricing question.
- **Associations** between measured burden (conditions, functional limitations, coverage, engagement with care) and same-year catastrophic spend.

### What it *cannot* establish

- **Anything longitudinal.** This is one calendar year. Panel 27 (survey year 2) and Panel 28 (survey year 1) are both 2023 observations, not two years of the same people. So there is **no within-person cost volatility, no persistence, no churn, and no next-year prediction** in this file. Every "volatility" statement below is *between-person dispersion inside a segment*, which is what a pricing pool actually faces — not year-over-year movement of an individual.
- **Causality.** Spend is jointly determined by illness, coverage, price, and access. Nothing here identifies a causal effect.
- **True risk for people who do not consume care.** Observed spend is censored by access. This turns out to be the single most consequential limitation of the project's label — see Insight 4.

### Which variables matter most

`TOTEXP23` is the outcome; **its tail, not its mean, is the business object.** The most informative predictors of tail behaviour turned out to be `LIMIT_CT` (functional limitations), `CHRONIC_CT`, `INSCOV23` (coverage), and `OBTOTV23` (ambulatory engagement). Behaviour variables (`PHYEXE53`, `OFTSMK53`) and the mental-health block (`K6SUM42`, `PHQ242`) are structurally sparse — `-1` or `-15` for 20% and 51% of rows respectively, because they come from adult-only and self-administered instruments. That sparsity, not weak signal, is the main reason the "behaviour-only" B0 block underperforms.

---

## Part 2 — The six findings

---

### Insight 1 — The "average member" does not exist: 79% spend below the mean, and 5% of members carry half of all spending

**Question.** If you had to describe this population's cost with one number, what would you get wrong?

**Finding.** Annual healthcare spending is so right-skewed that the mean is a tail statistic. The mean sits at the **79th percentile** of the distribution — it describes almost nobody. Half of all dollars belong to 5% of members, while the bottom half of the population accounts for 2.9% of spending.

**Key numbers.**
- Mean **$7,487** vs median **$1,584** — a **4.7×** gap; **78.9%** of people spend below the mean
- **Top 5% of members = 48.7% of all spending**; top 1% = 20.1%; top 10% = 65.2%
- Gini of annual spend **0.781**; 14.4% of people spend $0; 31.7% spend under $500

**Chart.** `analysis/figures/01_concentration_mean_vs_median.png`

**What the chart shows.** Left: a concentration curve with the top-1/5/10% shares marked. Right: the weighted spending distribution with the median and mean drawn on it, and the region below the mean shaded to show how much of the population it contains.

**Why it matters.** Every downstream decision in this project — pricing, budgeting, "cost saved per low-risk member" — is a statement about a mean. In a distribution this skewed, a per-member mean is an artefact of a handful of members, and a per-member median is an artefact of the 95% who never have a bad year. Reporting either one alone is misleading in opposite directions.

**Possible implication / course of action.** Stop reporting a single average cost per segment. Report a triple: **median (typical member), mean (budget), and $20k+ exceedance rate (tail exposure)**. Set the reserving question as "what fraction of expected cost sits above a threshold", not "what is the average".

**Limitation.** Concentration is measured within one year. Some of the top 1% are chronically expensive every year and some had one bad year; this file cannot separate them. Cross-year persistence would change how much of this concentration is actionable.

---

### Insight 2 — Risk selection lowers the cost level but makes the remaining pool *more* tail-concentrated

**Question.** The project selects a low-risk segment. Does that segment behave like a *stable* pool, or just a *cheaper* one?

**Finding.** Selecting the 30% of members the deployed model scores most "low-risk" cuts mean cost by 63% — but the resulting pool is **more** unequal than the population it came from, not less. Its Gini rises from 0.781 to 0.827, and the share of the pool's own dollars held by its worst 1% of members rises from 20.1% to 26.7%. A quarter of the selected pool's expected cost still comes from spending above $20,000.

**Key numbers.**
- Selected top-30%: median **$410** (−74%), mean **$2,779** (−63%) — but Gini **0.78 → 0.83**, worst-1% share **20.1% → 26.7%**, coefficient of variation **2.65 → 3.60**
- **2.9%** of the selected pool still crosses $20,000, and **25.1%** of its expected cost is spend above $20,000
- Tightening to the top 10% makes it worse, not better: worst-1% share **32.6%**, Gini **0.868**

**Chart.** `analysis/figures/02_selection_shifts_level_not_shape.png`

**What the chart shows.** Three panels: (1) median and mean fall sharply with selection; (2) internal concentration rises with selection; (3) the concentration curve of each selected pool sits *above* the population curve — a smaller minority owns more of it.

**Why it matters.** The project is called *Profit Stabilisation*, and its stability evidence measures the bootstrap variance of **segment size**. That is a different quantity from **cost variance**. A pool can be perfectly stable in headcount and still be one hospitalisation away from blowing its budget. This finding says selection buys you a lower expected cost, not a more predictable one — which is exactly the distinction an actuary would press on.

**Possible implication / course of action.** Add a **cost-dispersion metric to the stability dashboard** alongside segment size: Gini, CV, and the share of expected cost above $20k for each candidate segment. Any pricing built on this segmentation still needs stop-loss/reinsurance sized to the *selected* pool's tail, which is proportionally fatter than the population's.

**Limitation.** Out-of-fold prediction on a single year predicts a **same-year** label; it is not a forward-looking risk score. And the selected pool's low median is partly definitional, since the label is built from spend. The Gini/CV comparison is the part that is not definitional.

---

### Insight 3 — Counting diagnoses misses tail risk: 2 chronic conditions plus functional limitations carry the same catastrophic risk as 6+ conditions alone

**Question.** The model ladder treats chronic burden (B3) as the key addition. Is a condition count actually the right measure of burden for *tail* risk?

**Finding.** Functional limitations carry at least as much catastrophic-risk information per unit as chronic conditions, and they do it at a much lower typical cost. Members with **2 chronic conditions and 2+ functional limitations** have a $20k+ rate statistically indistinguishable from members with **6+ chronic conditions and no limitations** — at a **42% lower median cost**. The pattern holds inside every chronic band: adding 2+ limitations multiplies the catastrophic rate by 1.7× to 6.4×.

**Key numbers.**
- Adjusted logistic model (age, sex, mutually adjusted): **OR 1.394 per additional functional limitation vs OR 1.330 per additional chronic condition**; pseudo-R² rises **0.151 → 0.172** when limitations are added
- 2 chronic + 2+ limitations: **28.7%** [21.0–36.7] at $20k+, median **$6,327** (n=195)
- 6+ chronic + 0 limitations: **26.9%** [21.2–32.5] at $20k+, median **$10,938** (n=298)

**Chart.** `analysis/figures/03_chronic_vs_functional_tail_risk.png`

**What the chart shows.** A 6×3 heatmap of catastrophic-spend rate by chronic count × limitation count, with each cell's median spend annotated, and the two compared cells outlined. A companion panel plots median against catastrophic rate with 95% CIs for those two cells.

**Why it matters.** It explains *why* the project's own model ladder behaves the way it does. B2 (functional limits) contributes the structural signal about who can have a bad year; B3 (chronic count) contributes the signal about who is expensive on an ordinary day. AUC on a spend-based label rewards the second more visibly than the first — which is how a genuinely important tail marker can look like a modest AUC contributor.

**Possible implication / course of action.** Report chronic burden and functional burden as **two separate axes**, not one summed "burden score". Treat functional limitation as a monitoring flag in its own right: a member with 2 conditions and 2 limitations should not be triaged behind a member with 6 conditions and none.

**Limitation.** The two compared cells have overlapping confidence intervals — the honest claim is *equivalent* tail risk at lower typical cost, not *higher*. Functional limitations in MEPS come from round-3-1 items where missing was recoded to "no limitation" during preprocessing, which biases toward under-counting limitations and therefore **understates** this effect. Limitations and conditions are also correlated with age; the logistic model adjusts for age but cannot rule out residual confounding.

---

### Insight 4 — The cheapest median in the population is also the most emergency-driven: 9.2M members with 3+ chronic conditions and zero office visits

**Question.** Within people who are clinically similar, does low spending mean stability?

**Finding.** There is a large segment — 9.2M people — with three or more chronic conditions and **no office-based visits at all**. Their median annual spend is **$377**, the lowest median of any segment in this analysis. But **53.8% of every dollar they do spend goes to the ER or an inpatient bed**, versus 23.8% for chronically ill members who see a doctor. Their mean is 16× their median. Half of them are labelled "low-risk" by the project's rule.

**Key numbers.**
- Median **$377** vs **$8,692** for engaged chronic members (23× gap on typical cost) — but only a **3× gap on catastrophic rate**: 8.4% [5.9–11.1] vs 26.0%
- **53.8%** of their dollars are ER + inpatient, vs **23.8%** for the engaged group; mean **$6,157** = **16× their median**
- **30.1%** have no usual source of care and **11.4%** are uninsured (vs 8.8% and 0.8% for the engaged group); **52.0%** are labelled `LOW_RISK`

**Chart.** `analysis/figures/04_disengaged_chronic_segment.png`

**What the chart shows.** Panel 1: the acute (ER + inpatient) share of a group's dollars falls monotonically as office-visit volume rises, for both low- and high-burden members. Panel 2: median and mean spend by office-visit band for chronically ill members, showing the 16× gap at zero visits. Panel 3: a profile comparison of the disengaged and engaged groups.

**Why it matters.** This is the concrete face of "low spend ≠ low risk". These members are cheap this year, invisible in any spend-ranked report, and the money they do generate arrives through the most expensive door in the system. They are also the segment where an intervention plausibly changes the cost, rather than just observing it.

**Possible implication / course of action.** Create a standing operational flag — **"3+ chronic conditions and zero ambulatory contact in 12 months"** — as an outreach and care-gap KPI. It is computable from claims/enrolment data alone and does not require a model. Exclude this segment from any "low-risk" rating action until an ambulatory contact is confirmed.

**Limitation.** Zero office visits **mechanically** lowers total spend, so the median gap is partly circular. The non-mechanical results are the ones to quote: the **ER/inpatient share of dollars**, the **access-barrier profile**, and the fact that a group with 3+ diagnoses still has an 8.4% chance of a $20k year while being scored low-risk. Also, we cannot tell disengagement-by-barrier from disengagement-by-choice, or from milder disease, in a single cross-section.

---

### Insight 5 — "Low spend" is partly a measure of access, not health: at identical disease burden, uninsured members are ~5× more likely to be labelled low-risk

**Question.** What is the `LOW_RISK` label actually measuring?

**Finding.** Because the label is built from realised spend, it absorbs anyone who does not consume care — regardless of why. Holding measured disease burden constant, **uninsured members are about five times more likely to be labelled low-risk than insured members**. Only 39% of the resulting cohort is free of both hidden clinical burden and an access barrier.

**Key numbers.**
- Among members with **2+ chronic conditions**: **63.1%** [56.4–69.9] of uninsured are labelled low-risk vs **12.4%** [11.5–13.3] of insured — a **5.1× gap at identical measured burden**
- Overall: **75.4%** of uninsured members are labelled low-risk vs **27.7%** of insured
- Cohort composition: **39%** genuinely healthy and engaged, **37%** access-barrier only, **11%** hidden clinical burden only, **13%** both. **40.3%** of the cohort has no usual source of care, vs 17.8% of everyone else

**Chart.** `analysis/figures/05_low_risk_label_measures_access.png`

**What the chart shows.** Left: share labelled `LOW_RISK` by coverage status within each chronic-burden band, with bootstrap CIs — the coverage gap persists at every burden level. Right: the composition of the `LOW_RISK` cohort split by whether members carry hidden clinical burden, an access barrier, both, or neither.

**Why it matters.** This challenges the project's central construct. The model is trained to predict this label, so whatever the label conflates, the model learns. A segmentation that systematically scores uninsured and care-avoidant members as low-risk is not just statistically noisy — it is a fairness and adverse-selection exposure at the same time, because those members are the ones most likely to arrive later and more expensively.

**Possible implication / course of action.** Three concrete changes: (1) require **12-month continuous coverage** for label eligibility, or flag and report the uninsured share of any low-risk cohort; (2) add a **negative condition** to the label — no reported access barrier and a usual source of care — so "low spend" has to be corroborated; (3) publish the four-way cohort split alongside the headline cohort size, so the "29.5% low-risk" number is never quoted without its composition.

**Limitation.** This is an association in a single cross-section — it shows the label is *contaminated* by coverage, not that coverage causes lower true risk. Some uninsured members genuinely are healthy (they skew young). The strength of the evidence comes from holding chronic burden constant, but chronic conditions are themselves **diagnosed** conditions, so uninsured members are likely under-diagnosed and their true burden higher than measured — which makes this an under-estimate of the contamination.

---

### Insight 6 — Income predicts routine spending, not catastrophic spending: the poor-vs-rich cost gap is 62% on the median but only 18% on the mean

**Question.** Are low-income members actually cheaper, or do they just look cheaper?

**Finding.** Among insured members under 65 — so the comparison is not driven by Medicare or by uninsured non-utilisation — poor and near-poor members have a median cost **62% below** high-income members, but a mean only **18% below**. Decomposing spend into routine (first $5,000) and catastrophic (everything above $5,000) shows why: the income gradient is concentrated in routine care (−25%) and nearly vanishes in catastrophic care (−14%). Their $20k+ rates are 7.1% and 8.0% — a difference of under one percentage point.

**Key numbers.**
- Median gap **−62%** ($698 vs $1,827) but mean gap only **−18%** ($5,698 vs $6,928)
- Routine spend gap **−25%**; catastrophic spend gap **−14%**
- $20k+ rate **7.1%** [6.1–8.3] vs **8.0%** [7.1–8.8]
- Mean-to-median ratio: **8.2× for poor/near-poor vs 3.8× for high income**

**Chart.** `analysis/figures/06_income_gradient_routine_not_catastrophic.png`

**What the chart shows.** Left: mean spend by income band split into routine and catastrophic components, with the median member overlaid as a line — the median line has a steep gradient, the bar totals do not. Right: the poor-vs-rich gap measured five different ways, showing how the answer changes from −62% to −10% depending on which statistic you pick.

**Why it matters.** It is the cleanest demonstration in this dataset of *why averages mislead*, and it has a direct commercial consequence: a pool of low-income members priced off its median looks like a bargain and is not. Their catastrophic exposure is essentially the same as everyone else's; only their routine consumption is lower — and lower routine consumption among insured people is at least partly deferred care rather than better health.

**Possible implication / course of action.** When comparing segment costs, always report the **mean/median ratio** next to the level. A segment with a high ratio is one whose cost is dominated by events, not by consumption — budget it from the mean and monitor the exceedance rate, never from the median. Investigate whether the routine-care gap among *insured* low-income members reflects cost-sharing barriers, since that is the modifiable part.

**Limitation.** Restricting to insured under-65 removes the Medicare and uninsured confounds but not age or health composition within the band. The unrestricted picture is different — across the whole population the relationship is U-shaped, because low-income bands contain a large share of elderly and disabled members — and that composition effect is itself a caution against reading raw income-vs-cost charts.

---

## Part 3 — Interview summary

### Top 3 interview-worthy insights

#### 1. Risk selection lowers the cost level but concentrates the tail

- **Finding:** Selecting the model's most "low-risk" 30% of members cuts mean cost by 63% but raises the pool's internal Gini from 0.78 to 0.83, and the share of the pool's dollars held by its worst 1% from 20% to 27%.
- **Important number:** **25% of the selected pool's expected cost still comes from spending above $20,000.**
- **Why it matters:** The project's stability evidence measures the variance of *segment size*. This measures the variance of *cost*, which is what actually determines whether a pool is profitable. Selection buys a lower expected cost, not a more predictable one.
- **20–30 second explanation:** "I re-ran the deployed model under clean cross-validation and reproduced the 0.77 AUC. Then I asked a different question: what does the selected pool look like *as a pool*? Its mean cost drops 63%, which is the win. But its Gini goes *up*, from 0.78 to 0.83, and a quarter of its expected cost still sits above $20,000. So the segmentation reduces expected cost without reducing relative volatility — you still need stop-loss, and I'd argue the stability dashboard should track cost dispersion, not just segment headcount."

#### 2. The low-risk label is partly measuring access, not health

- **Finding:** Holding chronic burden constant, uninsured members are ~5× more likely to be labelled low-risk than insured members, because the label is built from realised spend.
- **Important number:** **63% of uninsured members with 2+ chronic conditions are labelled low-risk, versus 12% of insured members with the same burden.**
- **Why it matters:** The model is trained on this label, so it inherits the contamination. Only 39% of the "low-risk" cohort is free of both hidden clinical burden and an access barrier.
- **20–30 second explanation:** "The label is bottom-30% spend plus zero ER and zero inpatient. Spend is censored by access, so the label absorbs anyone who can't get care. I held disease burden constant and compared coverage groups: among people with two or more chronic conditions, 63% of the uninsured get called low-risk versus 12% of the insured. Same measured burden, five-fold difference in the label. My fix would be to require continuous coverage for label eligibility and publish the cohort's composition alongside its size."

#### 3. Counting diagnoses misses tail risk

- **Finding:** Functional limitations carry as much catastrophic-risk signal per unit as chronic conditions. Two conditions plus two limitations produces the same $20k+ rate as six-plus conditions with no limitations — at 42% lower typical cost.
- **Important number:** **OR 1.39 per functional limitation vs OR 1.33 per chronic condition**, age- and sex-adjusted and mutually adjusted.
- **Why it matters:** It explains the project's own model ladder. Functional status tells you who can *have* a bad year; condition count tells you who is expensive on an ordinary day. A spend-based AUC rewards the second more visibly.
- **20–30 second explanation:** "The project's story is that chronic burden was the key addition at B3. I tested whether a condition count is the right burden measure for the *tail*, and it isn't the whole story. In an adjusted logistic model, each functional limitation multiplies the odds of a $20k year by 1.39 versus 1.33 for each chronic condition, and adding limitations lifts pseudo-R² by 14%. Concretely, two conditions plus two limitations has the same catastrophic rate as six-plus conditions with none — at 42% lower median cost. So I'd report clinical and functional burden as two axes, not one score."

### Likely interviewer follow-ups

**How did you discover this?**
I started from the shape of the outcome rather than from the model. Once I saw a Gini of 0.78 and the mean sitting at the 79th percentile, I stopped asking "which segment is more expensive" and started asking "which segments have similar typical costs but different tail behaviour". I built a segment scan that computed median, mean, mean/median ratio, $20k+ rate, internal Gini and worst-1% share for every candidate cut, then pulled out the pairs where those metrics disagreed with each other.

**Why did you choose this metric?**
The $20,000 exceedance rate because it is the threshold the project already uses (`CATA_20K`) and it maps to a real reinsurance attachment concept. The mean/median ratio because it is a one-number diagnostic for "is this segment's cost driven by consumption or by events". The internal Gini and worst-1% share because they answer the pooling question directly — for a pool of members with the same observable profile, how much of the pool's cost sits with a handful of them.

**Why did you segment the data this way?**
Every cut had to be either operationally available (coverage status, ambulatory visit count) or already in the project's feature set (chronic count, limitation count, poverty category), so the findings are actionable rather than decorative. Where a raw comparison was confounded, I restricted rather than reweighted — the income comparison is insured-only and under-65 so the result isn't a Medicare artefact.

**What could explain this?**
For the label contamination: uninsured members face price barriers, so realised spend understates true risk. For the disengaged-chronic segment: some combination of access barriers, milder disease among the undiagnosed, and genuine non-adherence — this data cannot separate them. For the selection result: selecting on a spend-based label removes the *predictable* part of cost and leaves the *unpredictable* part, which is why relative dispersion rises.

**How did you validate it?**
Bootstrap confidence intervals (800 resamples) on every headline percentage; suppressed heatmap cells with n<40; reproduced the project's AUC out-of-fold before making any claim about the model. I also checked the two MEPS panels (27 vs 28) against each other for a survey-tenure artefact and found none — median $1,432 vs $1,685, mean chronic count 2.01 vs 2.12 — so the findings aren't a panel-composition effect.

**What could make this conclusion wrong?**
The biggest single risk is that everything here is one year. If catastrophic spend is highly persistent, then "the tail is unpredictable" is too strong — a lot of it would be forecastable from last year's spend, which I cannot see. The second risk is that MEPS spending is self-reported and provider-verified survey data, not claims, so extreme values have measurement error. The third is that the functional-limitation variables had missing values recoded to "no limitation" in preprocessing, which biases the limitation effect downward.

**What additional data would you want?**
Two consecutive MEPS panel years for the same people, to measure year-over-year cost persistence and cohort churn. Enrolment spans rather than a coverage summary, to distinguish genuinely uninsured from partial-year. And a claims-based utilisation feed, so the "zero ambulatory contact" flag could be computed in near-real-time rather than annually.

**What action could someone take from this?**
Three things that don't require a model: report median, mean and $20k+ rate together instead of a single average; add a "3+ chronic conditions with zero ambulatory contact" flag as a standing outreach list; and publish the composition of any low-risk cohort — specifically its uninsured and no-usual-source-of-care shares — alongside its size.

---

## Part 4 — Data-quality notes found along the way

These are repo issues rather than analytical insights, but worth knowing before an interview:

1. **`data_processed/scored_members_2023.parquet` is stale and internally inconsistent.** It contains 15,268 rows with `LOW_RISK` prevalence of **0.28%** (the correct value is ~29%) and an AUC of **0.99995** against its own stored scores. Something is misjoined or was written from a different label definition. I did not use it; I re-scored from the joblib under cross-validation instead. It should be regenerated or deleted before anyone reviews the repo.
2. **Behavioural and mental-health features are structurally sparse.** `PHYEXE53` / `OFTSMK53` are `-1` (inapplicable) for 3,833 rows (20.3%, children) and `K6SUM42` / `PHQ242` are `-1` or `-15` for 9,507–9,564 rows (~50%, adult self-administered questionnaire). These sentinels are currently passed to the model as ordinary categorical levels. That is defensible for a tree model, but it means "behaviour-only B0 is weak" is at least partly a coverage statement, not a signal statement — worth saying explicitly.
3. **Functional limitations were recoded with `.fillna(0)`** — missing treated as "no limitation". Given Insight 3, this systematically under-counts the strongest tail marker in the feature set.
4. **456 rows have `PERWT23F = 0`** and are out of scope for population estimates. The existing notebooks compute unweighted statistics on all 18,919 rows, which is why the reported mean ($8,422) differs from the weighted mean ($7,487). Both are correct; they answer different questions and should be labelled.

---

## Part 5 — WEBSITE HANDOFF

> For the separate website project. Do not implement here.

### Approved insight headlines, in recommended presentation order

| # | Headline | Chart file | Key numbers |
|---|---|---|---|
| 1 | **The "average member" does not exist: 79% spend below the mean, and 5% of members carry half of all spending** | `analysis/figures/01_concentration_mean_vs_median.png` | mean $7,487 vs median $1,584 (4.7×); 78.9% below the mean; top 5% = 48.7% of spend; Gini 0.781 |
| 2 | **Income predicts routine spending, not catastrophic spending: the poor-vs-rich cost gap is 62% on the median but only 18% on the mean** | `analysis/figures/06_income_gradient_routine_not_catastrophic.png` | median gap −62%, mean gap −18%, routine −25%, catastrophic −14%; $20k+ rate 7.1% vs 8.0% |
| 3 | **Counting diagnoses misses tail risk: 2 chronic conditions plus functional limitations carry the same catastrophic risk as 6+ conditions alone** | `analysis/figures/03_chronic_vs_functional_tail_risk.png` | OR 1.39 per limitation vs 1.33 per condition; 28.7% vs 26.9% at $20k+; 42% lower median |
| 4 | **The cheapest median in the population is also the most emergency-driven: 9.2M members with 3+ chronic conditions and zero office visits** | `analysis/figures/04_disengaged_chronic_segment.png` | median $377 vs $8,692; 53.8% of dollars are ER + inpatient vs 23.8%; mean is 16× median; 52% labelled low-risk |
| 5 | **"Low spend" is partly a measure of access, not health: at identical disease burden, uninsured members are ~5× more likely to be labelled low-risk** | `analysis/figures/05_low_risk_label_measures_access.png` | 63.1% vs 12.4% among members with 2+ chronic conditions; 75.4% vs 27.7% overall; only 39% of the cohort is unambiguously low-risk |
| 6 | **Risk selection lowers the cost level but makes the remaining pool more tail-concentrated — it is risk reduction, not risk elimination** | `analysis/figures/02_selection_shifts_level_not_shape.png` | mean −63%; Gini 0.78 → 0.83; worst-1% share 20.1% → 26.7%; 25.1% of expected cost still above $20k |

**Ordering rationale.** 1 establishes the shape of the problem. 2 and 3 show two different ways an average or a diagnosis count hides tail risk. 4 and 5 name the specific populations where that failure has consequences. 6 closes the loop by applying the lesson to the project's own model — it is the strongest ending because it is self-critical and quantified.

### Two-to-three sentence interpretations

**1 — Concentration.** Annual healthcare spending is so skewed that the mean sits at the 79th percentile: 79% of people spend less than the average member. Half of all dollars belong to 5% of members, while the bottom half of the population accounts for under 3%. Any per-member average is therefore a statement about the tail, not about a typical member.

**2 — Income.** Among insured members under 65, poor and near-poor members look 62% cheaper than high-income members on the median but only 18% cheaper on the mean. Splitting spend into routine and catastrophic shows why: the income gradient lives almost entirely in routine care and nearly disappears above $5,000. Their catastrophic-spend rates differ by less than one percentage point.

**3 — Functional burden.** Functional limitations carry at least as much catastrophic-risk signal per unit as chronic conditions, adjusted for age, sex and each other. Two chronic conditions plus two functional limitations produces the same $20k+ rate as six-plus chronic conditions with no limitations — at 42% lower typical cost. Clinical burden and functional burden should be reported as two axes, not summed into one score.

**4 — Disengaged chronic.** 9.2M people have three or more chronic conditions and no office-based visits at all. Their median annual spend of $377 is the lowest of any segment here, yet 54% of every dollar they do spend goes to the ER or an inpatient bed, versus 24% for chronically ill members who see a doctor. Half of them are currently scored "low-risk".

**5 — Access, not health.** Because the low-risk label is built from realised spending, it absorbs anyone who cannot get care. Among members with the same measured disease burden, uninsured people are about five times more likely to be labelled low-risk than insured people. Only 39% of the resulting cohort is free of both hidden clinical burden and an access barrier.

**6 — Selection.** Selecting the model's most low-risk 30% of members cuts mean cost by 63%, which is the win. But the resulting pool is more internally unequal than the population it came from — Gini rises from 0.78 to 0.83 — and a quarter of its expected cost still comes from spending above $20,000. Risk selection reduces expected cost without reducing relative volatility.

### Suggested headline KPIs for the top of the page

| KPI | Value | One-line gloss |
|---|---|---|
| Share of members below the average cost | **79%** | The mean describes almost nobody |
| Spending held by the top 5% of members | **49%** | Half of all dollars, one in twenty people |
| Catastrophic-cost share of a "low-risk" pool's expected cost | **25%** | Selection reduces cost, not tail exposure |
| Members with 3+ chronic conditions and zero office visits | **9.2M** | Cheapest median, most emergency-driven |

*(Optional fifth, if a fairness/label KPI is wanted: **5.1×** — how much more likely an uninsured member is to be labelled low-risk than an insured member with the same disease burden.)*

### Caveats that must remain visible on the page

1. **Single year, cross-sectional.** MEPS 2023 only. No within-person cost volatility, persistence, or next-year prediction. "Volatility" here means dispersion *between members inside a segment*, not movement of an individual over time.
2. **Association, not causation.** No result on this page identifies a causal effect. Spending is jointly determined by illness, coverage, price and access.
3. **Spending is censored by access.** Observed spend understates true risk for members who cannot obtain care. This is the mechanism behind Insight 5 and it limits how far any low-spend metric can be read as "healthy".
4. **Survey data, survey weights.** Estimates are `PERWT23F`-weighted to 334.5M people; 456 zero-weight rows are excluded. Model evaluation is record-level and *not* survey-weighted — the two should never be quoted as if they were the same population statistic.
5. **`LOW_RISK` is an operational label, not a clinical judgement.** It is bottom-30% spend ($484) plus zero ER visits plus zero inpatient stays. It is not a diagnosis and not a guarantee of future cost.
6. **Small-cell caution.** Heatmap cells with n<40 are suppressed; the 2-chronic/2+-limitation and 6+-chronic/0-limitation comparison has overlapping confidence intervals and should be described as *equivalent* tail risk, never as *higher*.
7. **Functional limitations are under-counted** — missing values were recoded to "no limitation" in preprocessing, which biases the Insight 3 effect downward.
