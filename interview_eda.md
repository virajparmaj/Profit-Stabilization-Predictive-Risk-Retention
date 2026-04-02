# Interview EDA and Data Preprocessing Explanation


## 1. Understanding the Dataset

### What
I started with the **MEPS 2023 HC-251 consolidated file**  Medical Expenditure Panel Survey (MEPS)

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


### Why This

I wanted the label to represent a more **stable low-risk profile**, not just a temporarily cheap case.

end goal is not only prediction accuracy.segment that is stable enough to support pricing, retention, or outreach decisions.

### Why Not
I did **not** define low risk using only low annual spend, because that would be too loose.

I also did **not** define the target using utilization-heavy predictors inside the input feature set, because that would create **leakage**. Leakage means the model gets information that is too close to the answer, which inflates performance but weakens real-world validity.

---

## 3. Missing Value Analysis

### What

1. true blanks or `NaN`
2. MEPS-specific sentinel codes like `-7`, `-8`, and `-9`

They represent survey nonresponse or inapplicable cases.

### How
I first standardized MEPS missingness by converting sentinel values into proper missing values.

- `EMPST53`: about **0.94%**
- `EDUCYR`: about **0.88%**
- `MNHLTH53`: about **0.33%**
- `RTHLTH53`: about **0.33%**
- `MARRY53X`: about **0.11%**

My treatment strategy was:

- for diagnosis flags, map valid yes/no codes into binary form and fill logically absent values with `0`
- for functional limitation flags, map valid yes/no codes into binary form and fill missing with `0` only when the feature meaning supported “no limitation”
- for behavior variables like exercise and smoking frequency, use **median imputation**
- keep minimal residual missingness in a few survey-coded categorical fields instead of overengineering them

**Imputation** means filling missing values with a substitute so the model can train on complete inputs.

### Why This
This mattered because a predictive pipeline needs a consistent way to represent missingness.

- reproducible
- interpretable
- low-risk

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


For `TOTEXP23`:

- mean: about **$8,422**
- median: about **$1,816**
- standard deviation: about **$21,664**
- max: about **$574,675**

That shows a strongly **right-skewed** distribution.

To stabilize that for analysis, I used a **log transform**:

- `LOG_TOTEXP23 = log(1 + TOTEXP23)`

After the transform: range more compressed

### Why This
healthcare expenditure not normally distributed

The mean alone would have been misleading. The large gap between the mean and the median showed me immediately that a small number of expensive cases dominate the variance

### Why Not
I did **not** remove high-cost outliers as data errors, because here they are not errors. They are part of the real risk distribution.

I also did **not** rely only on the mean, because with this much skew, the mean can distort the story.

And I did **not** winsorize the main cost variable for the predictive framing, because clipping the tail would weaken the connection to real catastrophic risk. Winsorization is an outlier-handling technique where you cap extreme values at chosen percentiles instead of removing them.

---

## 5. Bivariate and Multivariate Analysis

### Correation

- Correlation of `LOW_RISK` (Low Risk) with `CHRONIC_CT` (Chronic Count): about **-0.367**
- Correlation with `OBTOTV23` (Office Visits): about **-0.313**
- Correlation with `AGELAST` (Age): about **-0.302**
- Correlation with `RXTOT23` (Rx Total): about **-0.329**
- Correlation with `LIMIT_CT` (Limit Count): about **-0.195**

I also looked at acute utilization effects. One especially clear result was:

- median total spend with **0 ER visits**: about **$1,271.50**
- median total spend with **1 ER visit**: about **$7,656.00**

That is a large jump after even a single ER event.

For example:

- mean `LIMIT_CT` for non-low-risk group: about **0.50**
- mean `LIMIT_CT` for low-risk group: about **0.07**

It’s built from these fields (after recoding to clean binary yes/no):
- `ADLHLP31` (ADL Help)
- `IADLHP31` (IADL Help)
- `WLKLIM31` (Walk Limit)
- `COGLIM31` (Cog Limit)
- `WRKLIM31` (Work Limit)
- `SOCLIM31` (Social Limit)

### Why This
This stage mattered because it showed me where the predictive signal was coming from.

The biggest insight was that behavior alone had some signal, but not enough. Chronic burden, function, and mental health added much stronger separation.

That directly motivated the feature-block design:

- start with behavior
- then add mental health
- then chronic burden

### Why Not

I also did **not** rely on a single correlation matrix as the entire story, because:

- many features are categorical
- many healthcare counts are zero-inflated
- and survey-coded variables are not always well summarized by one linear statistic

Instead, I used targeted comparisons that were more interpretable for this dataset.

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

Then inside the actual training pipeline:

- **low-cardinality categorical variables** were **one-hot encoded**
- **continuous numeric variables** were **standardized**

**One-hot encoding** means converting a categorical variable into separate indicator columns.  
**Standardization** means putting continuous variables on a comparable scale by centering around zero and scaling by the standard deviation.

### Why This

For example, a model should not treat insurance codes `1, 2, 3, 4` as if category `4` is “twice” category `2`. One-hot encoding prevents that kind of false numeric interpretation.

Standardization mattered for models like logistic regression because features measured on very different scales can destabilize training.

At the same time, tree-based models like random forest and XGBoost do not need scaling as much, but keeping preprocessing in a single pipeline made the system reusable and consistent across model families.

### Why Not
I did **not** use **label encoding** as the final modeling treatment for all categories, because that can accidentally imply ordinal meaning where none exists.

I also did **not** scale everything blindly, because some low-cardinality survey-coded fields are better treated as categories than as continuous numeric variables.


## 7. Feature Engineering

### What

 built compact features that better captured persistent risk structure.

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

### Why Not

- interaction terms
- utilization ratios
- raw service-specific subcomponent counts

But I chose not to center the project on those because my main goal was the **minimum stable predictive structure**, not the most complicated feature set possible.

## 8. Feature Selection

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

### Why Not
I did **not** claim a formal chi-square pipeline, mutual information filter, or correlation-threshold selection workflow, because that was not the real method used in the notebook.

I wanted the story to stay truthful to the actual project.

I also did **not** use automatic selection alone, because in a healthcare setting, domain meaning and governance matter just as much as raw predictive lift.

---

## 9. Data Splitting Strategy

### What
Once the features were ready, I needed an evaluation design that reflected real predictive performance without overstating it.

### How
I used a **75/25 train-test split** with **stratification** on the target. no overtraining to overfit

I evaluated the models using:

- **AUC**: how well the model ranks positives above negatives across thresholds
- **precision**: of the people predicted low risk, how many are actually low risk
- **recall**: of all truly low-risk people, how many the model finds
- **F1**: a balance between precision and recall
- **Brier score**: how close predicted probabilities are to actual outcomes,average squared error of the predicted probabilities:

A model can have high AUC but bad Brier: it ranks people correctly but its probabilities are overconfident/underconfident.

A model can have decent Brier but mediocre AUC: probabilities are “reasonable on average,” but it doesn’t separate individuals well.

I also ran **300 bootstrap resamples** on the holdout predictions to measure stability.

**Overfitting** means a model memorizes the training data instead of learning patterns that generalize.

### Why Not
I did **not** prioritize a full cross-validation sweep or an exhaustive hyperparameter search, because the project’s main question was about **stable structure**, not squeezing out the last fraction of AUC.

I also did **not** optimize around accuracy alone. In an imbalanced classification problem, accuracy can look good even when the model is ignoring the positive class.

“Because 70% of people are not low risk, a model can hit ~70% accuracy by predicting the majority class and still fail completely at finding low-risk members. That’s why I focused on AUC, precision/recall, and probability calibration instead of accuracy alone.”

## 10. Key Insights From EDA

### How
The evidence came from both EDA and block-wise modeling.

From EDA:

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

### Why This
This stage is where EDA directly influenced decisions.

It told me:

- behavior-only risk segmentation would be too weak
- chronic burden is the first major stabilizing feature
- later blocks improve performance, but at a cost

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

### Why Not

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

