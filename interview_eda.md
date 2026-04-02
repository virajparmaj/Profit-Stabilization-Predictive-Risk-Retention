# Interview EDA and Data Preprocessing Explanation

This document is written as a detailed, interview-ready answer for explaining the **EDA and preprocessing pipeline** behind the MEPS-based healthcare machine learning project.

The structure is intentionally repetitive:

- `What`: what I looked at or built
- `How`: how I actually did it
- `Why this`: why that step mattered in this project
- `Why not`: why I did not choose the most obvious alternative

That format makes it easier to understand, easier to revise, and easier to speak clearly in an interview.

---

## How I Would Answer In an Interview

If an interviewer asked me to walk through my EDA and preprocessing pipeline end to end, I would explain it like this:

---

## 1. Understanding the Dataset

### What
I started with the **MEPS 2023 HC-251 consolidated file**, which is a healthcare survey dataset at the **person-year** level.

That means:

- each row represents one person
- each row covers one full calendar year
- the dataset combines demographics, insurance, health conditions, utilization, expenditures, and selected behavioral and mental health fields

The raw dataset had **18,919 rows and 1,374 columns**.  
After reducing the schema for analysis, I created a focused analytic table with **51 columns**.  
After preprocessing and feature engineering, the final model-ready table had **59 columns**.

The data includes:

- **Numerical variables**: age, family income, total expenditure, office visits, outpatient visits, prescription counts, ER visits, inpatient days
- **Categorical variables**: sex, race/ethnicity, education, marital status, insurance status, employment, poverty category
- **Binary clinical indicators**: hypertension, diabetes, stroke, asthma, cancer, and other chronic diagnoses

My target variable was **`LOW_RISK`**, which is a binary indicator.

### How
I defined the target in a way that matched the insurance use case:

- `LOW_SPEND = 1` if annual total expenditure was in the **bottom 30%**
- `LOW_RISK = 1` if the person was low spend **and** had:
  - **0 ER visits**
  - **0 inpatient days**

So the final label was not just low spending. It was low spending **plus no acute high-cost events**.

In the processed dataset:

- `LOW_RISK` prevalence was **29.49%**
- `LOW_SPEND` prevalence was **30.00%**
- `CATA_10K` prevalence was **19.36%**
- `CATA_20K` prevalence was **10.46%**

### Why This
This definition matters because a person can look low cost in one year simply by chance, but still be clinically unstable.

I wanted the label to represent a more **stable low-risk profile**, not just a temporarily cheap case.

That is important in an insurance setting because the end goal is not only prediction accuracy. The end goal is a segment that is stable enough to support pricing, retention, or outreach decisions.

### Why Not
I did **not** define low risk using only low annual spend, because that would be too loose.

I also did **not** define the target using utilization-heavy predictors inside the input feature set, because that would create **leakage**. Leakage means the model gets information that is too close to the answer, which inflates performance but weakens real-world validity.

---

## 2. Initial Data Inspection

### What
My first stage was basic data quality inspection.

I checked:

- row and column counts
- whether the file only contained **2023** records
- whether each `DUPERSID` appeared once
- duplicates
- basic descriptive statistics
- naming patterns in the raw MEPS columns

### How
I loaded the raw file and validated:

- raw shape: **18,919 x 1,374**
- all records had `DATAYEAR = 2023`
- unique `DUPERSID` count matched row count
- duplicate rows: **0**
- duplicate person IDs: **0**

I also inspected suffix patterns in column names. In MEPS, suffixes tell you whether a variable is:

- a year-level total like `...23`
- or a round-specific field like `...31`, `...42`, or `...53`

In the raw file:

- suffix `23` appeared **644** times
- suffix `31` appeared **129** times
- suffix `42` appeared **209** times
- suffix `53` appeared **86** times

That told me the dataset was structurally mixed: annual expenditure and utilization fields were complete, while some behavior and health-status fields were collected only in specific rounds.

### Why This
This step matters because before you model anything, you need to confirm the **unit of analysis** and the **structure of the source data**.

For example:

- if I had duplicate people, my model would overrepresent some cases
- if the file mixed years, the label logic would become inconsistent
- if I ignored the suffix structure, I could accidentally combine variables collected at different time resolutions without realizing it

In short, this is where I verified that the raw source could support a valid person-year predictive pipeline.

### Why Not
I did **not** jump directly to feature selection or model training, because wide healthcare survey files often contain structural traps:

- repeated codes
- survey-design columns
- round-specific fields
- payer splits
- and special missing-value encodings

Skipping this step would have made every downstream result less trustworthy.

---

## 3. Missing Value Analysis

### What
I analyzed missingness in two layers:

1. true blanks or `NaN`
2. MEPS-specific sentinel codes like `-7`, `-8`, and `-9`

Those sentinel values are especially important because they are not real measurements. They represent survey nonresponse or inapplicable cases.

### How
I first standardized MEPS missingness by converting sentinel values into proper missing values.

Then I checked missingness rates after reduction and preprocessing.

In the final model feature set, missingness was very low:

- `EMPST53`: about **0.94%**
- `EDUCYR`: about **0.88%**
- `MNHLTH53`: about **0.33%**
- `RTHLTH53`: about **0.33%**
- `MARRY53X`: about **0.11%**
- most other retained fields: **0%**

My treatment strategy was:

- for diagnosis flags, map valid yes/no codes into binary form and fill logically absent values with `0`
- for functional limitation flags, map valid yes/no codes into binary form and fill missing with `0` only when the feature meaning supported “no limitation”
- for behavior variables like exercise and smoking frequency, use **median imputation**
- keep minimal residual missingness in a few survey-coded categorical fields instead of overengineering them

**Imputation** means filling missing values with a substitute so the model can train on complete inputs.

### Why This
This mattered because a predictive pipeline needs a consistent way to represent missingness.

I wanted a strategy that was:

- reproducible
- interpretable
- low-risk

The data quality was already strong after recoding, so the simplest defensible choices were the best ones.

Median imputation worked well for the behavior variables because:

- they behave like ordered survey responses
- the median is robust to skew
- and the missingness was small

### Why Not
I did **not** use **KNN imputation** or **MICE**.

- **KNN imputation** fills missing values using the nearest similar records
- **MICE** estimates missing values using iterative predictive models

Those methods are useful when missingness is substantial and when the added complexity is justified.

I did not use them here because:

- missingness was already very low after cleanup
- the data is mostly survey-coded tabular data
- advanced imputation would add modeling assumptions
- and the payoff would likely be minimal

I also did **not** drop rows aggressively because the dataset preserved all **18,919 observations**, which gave me better sample stability.

---

## 4. Univariate Analysis

### What
I used univariate EDA to understand the shape of individual variables one at a time.

I focused especially on:

- `TOTEXP23`
- utilization counts
- behavior variables
- mental health variables
- engineered burden features

### How
I used:

- **summary statistics** like mean, median, min, max, and standard deviation
- **histograms** to visualize distributions
- **boxplots** to visualize spread and outliers

The strongest univariate finding was the expenditure distribution.

For `TOTEXP23`:

- mean: about **$8,422**
- median: about **$1,816**
- standard deviation: about **$21,664**
- max: about **$574,675**

That shows a strongly **right-skewed** distribution.

**Skewness** means the data is unevenly distributed and pulled heavily toward one side. In this case, most people are low or moderate cost, while a small minority are extremely high cost.

To stabilize that for analysis, I used a **log transform**:

- `LOG_TOTEXP23 = log(1 + TOTEXP23)`

After the transform:

- the range became much more compressed
- the distribution became easier to inspect visually
- and the heavy upper tail stopped dominating the chart

### Why This
This mattered because healthcare expenditure is not normally distributed, and the raw scale can hide what is happening for the majority of members.

The mean alone would have been misleading. The large gap between the mean and the median showed me immediately that a small number of expensive cases dominate the variance.

That insight influenced both:

- the label design
- and the later modeling decisions

In insurance risk work, those tail cases are real and important, so the goal is not to remove them. The goal is to understand them correctly.

### Why Not
I did **not** remove high-cost outliers as data errors, because here they are not errors. They are part of the real risk distribution.

I also did **not** rely only on the mean, because with this much skew, the mean can distort the story.

And I did **not** winsorize the main cost variable for the predictive framing, because clipping the tail would weaken the connection to real catastrophic risk.

---

## 5. Bivariate and Multivariate Analysis

### What
After understanding each variable individually, I looked at how features related to:

- the target
- each other
- and broader risk patterns

I was mainly trying to identify which domains actually separated low-risk people from the rest.

### How
I used a combination of:

- group comparisons by low-risk label
- simple correlation-style diagnostics
- targeted summary tables
- visual comparisons like boxplots

**Correlation** is a measure of the strength and direction of a linear relationship between two variables. It helps screen for signal, even though it does not prove causation.

A few of the strongest patterns were:

- correlation of `LOW_RISK` with `CHRONIC_CT`: about **-0.367**
- correlation with `OBTOTV23`: about **-0.313**
- correlation with `AGELAST`: about **-0.302**
- correlation with `RXTOT23`: about **-0.329**
- correlation with `LIMIT_CT`: about **-0.195**

I also looked at acute utilization effects. One especially clear result was:

- median total spend with **0 ER visits**: about **$1,271.50**
- median total spend with **1 ER visit**: about **$7,656.00**

That is a large jump after even a single ER event.

For group comparisons:

- low-risk members had better behavior profiles
- low-risk members had better self-rated physical and mental health
- low-risk members had lower distress and depression-screen values
- low-risk members had much lower functional limitation burden

For example:

- mean `LIMIT_CT` for non-low-risk group: about **0.50**
- mean `LIMIT_CT` for low-risk group: about **0.07**

### Why This
This stage mattered because it showed me where the predictive signal was coming from.

The biggest insight was that behavior alone had some signal, but not enough. Chronic burden, function, and mental health added much stronger separation.

That directly motivated the feature-block design:

- start with behavior
- then add mental health
- then function
- then chronic burden

This was not just EDA for presentation. It directly informed how I structured the experiment.

### Why Not
I did **not** overstate the analysis by pretending I ran a huge formal feature-selection pipeline at this stage.

I also did **not** rely on a single correlation matrix as the entire story, because:

- many features are categorical
- many healthcare counts are zero-inflated
- and survey-coded variables are not always well summarized by one linear statistic

Instead, I used targeted comparisons that were more interpretable for this dataset.

---

## 6. Feature Cleaning and Transformation

### What
The next stage was turning the reduced dataset into a model-compatible feature table.

This included:

- cleaning coded values
- recoding categorical and binary variables
- engineering compact burden features
- preparing the features for modeling pipelines

### How
I first normalized special missing codes.

Then I recoded diagnosis fields into binary indicators:

- `1 -> yes`
- `2 -> no`
- missing or invalid values handled consistently

I applied the same logic to the functional limitation fields.

Then I created:

- `CHRONIC_CT` as the sum of chronic diagnosis indicators
- `LIMIT_CT` as the sum of functional limitation indicators

I also used **median imputation** for:

- `PHYEXE53`
- `OFTSMK53`

For categorical modeling, I made the survey variables stable and machine-readable.

Then inside the actual training pipeline:

- **low-cardinality categorical variables** were **one-hot encoded**
- **continuous numeric variables** were **standardized**

**One-hot encoding** means converting a categorical variable into separate indicator columns.  
**Standardization** means putting continuous variables on a comparable scale by centering around zero and scaling by the standard deviation.

### Why This
This mattered because models do not understand raw survey coding semantics.

For example, a model should not treat insurance codes `1, 2, 3, 4` as if category `4` is “twice” category `2`. One-hot encoding prevents that kind of false numeric interpretation.

Standardization mattered for models like logistic regression because features measured on very different scales can destabilize training.

At the same time, tree-based models like random forest and XGBoost do not need scaling as much, but keeping preprocessing in a single pipeline made the system reusable and consistent across model families.

### Why Not
I did **not** use **label encoding** as the final modeling treatment for all categories, because that can accidentally imply ordinal meaning where none exists.

I also did **not** scale everything blindly, because some low-cardinality survey-coded fields are better treated as categories than as continuous numeric variables.

And I did **not** leave the feature handling outside the model pipeline, because that would make deployment and reproducibility weaker.

---

## 7. Feature Engineering

### What
Feature engineering was one of the most important parts of the workflow.

Rather than feeding many noisy raw survey fields directly into the model, I built compact features that better captured persistent risk structure.

### How
The two most important engineered variables were:

- `CHRONIC_CT`: total chronic condition count
- `LIMIT_CT`: total functional limitation count

`CHRONIC_CT` summarized the burden of conditions such as:

- hypertension
- diabetes
- coronary heart disease
- stroke
- COPD/emphysema
- arthritis
- asthma
- cancer
- and related clinical conditions

Its distribution looked like this:

- mean: about **2.05**
- median: **1**
- max: **12**

`LIMIT_CT` summarized functional difficulty across:

- activities of daily living
- instrumental daily living
- walking
- cognition
- work limitation
- social limitation

That gave me a much cleaner way to represent persistent health burden than keeping every raw field separate.

I also engineered:

- `LOW_SPEND`
- `LOW_RISK`
- `CATA_10K`
- `CATA_20K`

### Why This
This mattered because in insurance risk modeling, a compact burden score is often more useful than a long list of loosely related binary variables.

These engineered features:

- reduce noise
- improve interpretability
- simplify the feature space
- and make the model more stable

They also made the interview story stronger, because I could explain exactly why the model improved at `B2` and `B3`.

### Why Not
I did **not** keep every diagnosis flag as an equally important standalone input in the main deployment story, because that would make the model harder to explain and more fragile.

I also considered richer feature ideas like:

- interaction terms
- utilization ratios
- raw service-specific subcomponent counts

But I chose not to center the project on those because my main goal was the **minimum stable predictive structure**, not the most complicated feature set possible.

---

## 8. Feature Selection

### What
My feature-selection logic was practical and research-driven rather than purely automated.

I used:

- domain-led reduction
- leakage exclusion
- block-wise model comparison

### How
The process worked in three layers.

First, I reduced the raw MEPS file from **1,374 columns** to a focused set of policy-relevant variables.

Second, I excluded:

- IDs
- survey-design variables from the predictive matrix
- label columns
- and label-defining cost variables like `TOTEXP23`, `ERTOT23`, and `IPDIS23`

Third, I organized the remaining predictors into cumulative feature blocks:

- `B0_behavior`: exercise and smoking
- `B1_mental`: self-rated physical health, self-rated mental health, K6, PHQ-2
- `B2_functional`: limitation count
- `B3_chronic`: chronic burden count
- `B4_ses_ins`: SES and insurance
- `B5_util_nonlabel`: office visits, outpatient visits, prescriptions

This let me evaluate not just “which features matter,” but “when does the model become meaningfully useful and stable?”

If I define **feature importance** in plain English, it means how much a feature influences the model’s prediction.

In this project, I treated importance mainly through:

- block performance lift
- stability lift
- and domain relevance

### Why This
This mattered because my research question was deeper than simple ranking.

I was not only asking:

- which model is best

I was asking:

- what is the minimum amount of structure needed before low-risk segmentation becomes stable enough to trust

That is why the block ladder was more valuable than a one-shot feature ranking.

### Why Not
I did **not** claim a formal chi-square pipeline, mutual information filter, or correlation-threshold selection workflow, because that was not the real method used in the notebook.

I wanted the story to stay truthful to the actual project.

I also did **not** use automatic selection alone, because in a healthcare setting, domain meaning and governance matter just as much as raw predictive lift.

---

## 9. Data Splitting Strategy

### What
Once the features were ready, I needed an evaluation design that reflected real predictive performance without overstating it.

### How
I used a **75/25 train-test split** with **stratification** on the target.

That means:

- **75%** of the data was used for training
- **25%** was held out for final evaluation
- the train and test sets preserved the same approximate low-risk prevalence

Because `LOW_RISK` was about **29.49%**, stratification mattered. Without it, one split could end up too easy or too hard by accident.

I evaluated the models using:

- **AUC**: how well the model ranks positives above negatives across thresholds
- **precision**: of the people predicted low risk, how many are actually low risk
- **recall**: of all truly low-risk people, how many the model finds
- **F1**: a balance between precision and recall
- **Brier score**: how close predicted probabilities are to actual outcomes

I also ran **300 bootstrap resamples** on the holdout predictions to measure stability.

**Overfitting** means a model memorizes the training data instead of learning patterns that generalize.

### Why This
This mattered because in an insurance segmentation problem, I care about two things:

1. ranking quality
2. stability of the predicted segment

The train-test split gave me a clean holdout estimate.  
The bootstrap analysis told me whether that result was stable or just lucky.

That combination was more aligned with the business question than focusing only on one lucky holdout score.

### Why Not
I did **not** prioritize a full cross-validation sweep or an exhaustive hyperparameter search, because the project’s main question was about **minimum stable structure**, not squeezing out the last fraction of AUC.

I also did **not** optimize around accuracy alone. In an imbalanced classification problem, accuracy can look good even when the model is ignoring the positive class.

---

## 10. Key Insights From EDA

### What
The most important findings were about:

- the shape of the cost distribution
- the role of acute utilization
- the importance of chronic and functional burden
- and the fact that behavior alone was not enough

### How
The evidence came from both EDA and block-wise modeling.

From EDA:

- total spend was heavily right-skewed
- one ER visit sharply increased median spend
- low-risk members had better mental-health profiles
- low-risk members had much lower limitation burden

From the modeling ladder, using XGBoost:

- `B0`: **0.579**
- `B1`: **0.686**
- `B2`: **0.711**
- `B3`: **0.773**
- `B4`: **0.825**
- `B5`: **0.950**

At `B3`, the model first became meaningfully strong while still staying compact and governance-friendly.

In the bootstrap analysis for `B3`:

- AUC mean: about **0.7725**
- AUC SD: about **0.00741**
- low-risk rate mean: about **0.3003**
- low-risk rate SD: about **0.000496**

That low standard deviation on segment size was especially important.

### Why This
This stage is where EDA directly influenced decisions.

It told me:

- behavior-only risk segmentation would be too weak
- chronic burden is the first major stabilizing feature
- later blocks improve performance, but at a cost

So EDA did not just produce charts. It determined:

- the feature engineering strategy
- the feature block design
- and the final model-selection logic

### Why Not
I did **not** simply pick the highest-AUC model and stop there.

`B5` had the best performance, but I treated it as an **upper-bound benchmark**, not the deployment choice.

That is because:

- `B4` introduces fairness and regulatory sensitivity through SES and insurance
- `B5` moves very close to realized utilization behavior, which makes it less attractive for early-action segmentation

So the real project conclusion was not “the biggest model wins.”
The real conclusion was “`B3` is the minimum stable model.”

---

## 11. Limitations and Considerations

### What
I would always end by being honest about the limitations.

### How
I frame the main limitations in four parts:

1. **Survey bias**  
   MEPS contains self-reported measures, so some variables may contain reporting noise.

2. **Unmet need vs true low risk**  
   Low utilization does not always mean low underlying health risk. It can also reflect lack of access, especially among uninsured groups.

3. **Single-year generalizability**  
   The core analysis is based on MEPS 2023, so the next step would be temporal validation across future years or panels.

4. **Fairness and governance**  
   Even if I exclude SES from the deployable model, broader structural bias can still appear indirectly through correlated features.

I would also explain why I did not center the predictive pipeline on survey weights:

- survey weights are critical for population inference
- but this project focused on person-level predictive segmentation and stability

### Why This
This matters because a strong interview answer should show technical confidence **and** judgment.

The goal is not to pretend the dataset is perfect.  
The goal is to show that I understand:

- what the model can do
- what it cannot do
- and how to make decisions responsibly

### Why Not
I did **not** overclaim the model as a direct premium-setting engine.

I treated it as:

- a low-risk segmentation tool
- a stability-oriented predictive system
- and a strong foundation for future fairness, temporal, and policy validation

---

## Short Closing Version

If I needed to summarize the whole EDA and preprocessing story in a few lines, I would say:

> I started with the raw 2023 MEPS person-level file, validated the unit of analysis, reduced the schema from 1,374 columns to a compact policy-relevant feature set, cleaned MEPS missing-value codes, engineered chronic and functional burden summaries, and created a conservative low-risk label based on low annual spend plus no ER or inpatient use.  
>  
> My EDA showed that healthcare cost is highly right-skewed, acute utilization sharply separates risk, and chronic burden is the first feature block that makes low-risk segmentation stable. That is why I selected `B3` as the minimum stable model: it gave meaningful predictive separation and strong bootstrap stability without relying on SES-heavy or utilization-heavy features that are harder to justify in deployment.

---

## Quick Numbers to Remember

- Raw dataset: **18,919 rows x 1,374 columns**
- Reduced analytic table: **18,919 rows x 51 columns**
- Final model-ready table: **18,919 rows x 59 columns**
- Duplicate rows: **0**
- Duplicate person IDs: **0**
- `LOW_RISK` prevalence: **29.49%**
- `LOW_SPEND` prevalence: **30.00%**
- `CATA_10K` prevalence: **19.36%**
- `CATA_20K` prevalence: **10.46%**
- `TOTEXP23` mean: **$8,422**
- `TOTEXP23` median: **$1,816**
- `TOTEXP23` max: **$574,675**
- Median spend with 0 ER visits: **$1,271.50**
- Median spend with 1 ER visit: **$7,656.00**
- `LIMIT_CT` mean in low-risk group: **0.07**
- `LIMIT_CT` mean in non-low-risk group: **0.50**
- Train/test split: **75/25 stratified**
- Bootstrap resamples: **300**
- XGBoost AUC by block:
  - `B0`: **0.579**
  - `B1`: **0.686**
  - `B2`: **0.711**
  - `B3`: **0.773**
  - `B4`: **0.825**
  - `B5`: **0.950**
- `B3` bootstrap AUC mean: **0.7725**
- `B3` bootstrap AUC SD: **0.00741**
- `B3` low-risk segment mean: **0.3003**
- `B3` low-risk segment SD: **0.000496**

---

## Final Interview Positioning

The strongest way to present this project is:

- not as “I cleaned data and trained a model”
- but as “I used EDA to discover the minimum stable predictive structure for low-risk insurance segmentation”

That framing is stronger because it shows:

- statistical understanding
- preprocessing discipline
- business awareness
- and model-governance judgment

