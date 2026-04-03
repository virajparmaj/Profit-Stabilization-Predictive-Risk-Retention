# Interview EDA and Data Preprocessing Explanation


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

### Why Not
I did **not** use **KNN imputation** or **MICE**.

- **KNN imputation** fills missing values using the nearest similar records
- **MICE** estimates missing values using iterative predictive models

---
## Outliers 

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

### Interaction terms

### Encoding 

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

### Why Not

- interaction terms
- utilization ratios
- raw service-specific subcomponent counts

But I chose not to center the project on those because my main goal was the **minimum stable predictive structure**, not the most complicated feature set possible.

## 9. Data Splitting Strategy

A model can have high AUC but bad Brier: it ranks people correctly but its probabilities are overconfident/underconfident.

A model can have decent Brier but mediocre AUC: probabilities are “reasonable on average,” but it doesn’t separate individuals well.

I also ran **300 bootstrap resamples** on the holdout predictions to measure stability.

**Overfitting** means a model memorizes the training data instead of learning patterns that generalize.

### Why Not
I did **not** prioritize a full cross-validation sweep or an exhaustive hyperparameter search, because the project’s main question was about **stable structure**, not squeezing out the last fraction of AUC.

I also did **not** optimize around accuracy alone. In an imbalanced classification problem, accuracy can look good even when the model is ignoring the positive class.

“Because 70% of people are not low risk, a model can hit ~70% accuracy by predicting the majority class and still fail completely at finding low-risk members. That’s why I focused on AUC, precision/recall, and probability calibration instead of accuracy alone.”

## 10. Key Insights From EDA

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

