# Interview Modelling Cross-Question Guide

> This project is not only about finding the highest-scoring model. It is about identifying the minimum feature structure needed to create a stable, policy-usable low-risk segment.

That is why the notebook has two ladders:

1. a **feature ladder** from `B0` to `B5`
2. a **model ladder** from logistic regression to tree-based models

The feature ladder answers the research question.  
The model ladder answers the engineering question.

## 1. Problem Setup

### What

This is a **classification** problem

The notebook makes this a **probabilistic classification** problem because it predicts a probability of being low risk, not only a hard class.

### Why

The insurance use case is segmentation, not exact spend forecasting. The business wants to know who belongs in a lower-risk cohort for pricing, retention, or outreach. That is more naturally handled by a probability-ranked cohort than by an exact spend estimate.

### How

### Why Not

Why not direct spend prediction with regression?

- **Regression** means predicting a continuous number like annual spend.
- `TOTEXP23` is extremely noisy and heavy-tailed.
- not perfect dollar prediction

### Cross-Questions You Should Expect

- Why is this classification and not regression?
- Why does the label use both spend and utilization?
- Why the bottom 30% and not 20% or 40%?
- Is this a retrospective label or a prospective label?

Strong short answer:

> I treated it as probabilistic classification because the action is stable cohort selection, not exact spend prediction. The bottom-30% rule gives a portable segment size, and adding zero ER plus zero inpatient use makes the label more stable than low spend alone.

## 2. Data Reality Before Modeling

Utilization counts are also **zero-inflated**, meaning many observations are exactly zero and the nonzero values form a separate behavior regime.

Zero shares:

- `OBTOTV23 = 0.260373`
- `OPTOTV23 = 0.741741`
- `ERTOT23 = 0.847191`
- `IPDIS23 = 0.925947`
- `RXTOT23 = 0.373223`

### How

### Why Not

Why not winsorize the cost target for the main modeling objective?

- **Winsorization** means capping extreme values at fixed percentiles
- that can be useful for some regression tasks
- here it would weaken the very risk structure the project is trying to understand

### Cross-Questions You Should Expect

- What did the spend distribution tell you before modeling?
- Why do you keep talking about the tail?
- Why does zero-inflation matter?
- Why was ER use such a big deal in the notebook?

Strong short answer:

> The data told me early that cost prediction was going to be tail-dominated and acute-event-sensitive. That is why I turned the problem into stable low-risk cohort identification instead of raw spend regression.

---

## 3. Upstream Feature Engineering

### Why

The modeling question is not just whether health variables matter. It is whether a small, defendable structural representation can stabilize risk segmentation.

`CHRONIC_CT` and `LIMIT_CT` are useful because they compress many messy survey variables into burden scores that are easy to explain and stable across model families.

### How

#### `CHRONIC_CT`

The preprocessing notebook maps diagnosis indicators into binary values and sums them:

- hypertension
- diabetes
- coronary heart disease
- myocardial infarction
- stroke
- COPD/emphysema
- high cholesterol
- arthritis
- asthma
- cancer
- any mental illness
- ever COVID diagnosis

#### `LIMIT_CT`

The notebook recodes six limitation variables into binary indicators and sums them:

- ADL help
- IADL help
- walking limitation
- cognitive limitation
- work limitation
- social limitation

After cleanup:

- mean `LIMIT_CT` for non-low-risk `0.50015`
- mean `LIMIT_CT` for low-risk `0.07349`

That is a large separation.

#### Mental-health block

The early non-behavioral signal comes from:

- `RTHLTH53`
- `MNHLTH53`
- `K6SUM42`
- `PHQ242`

Yes. In MEPS, those suffixes are time markers:

- `31` = Round **3/1** value (early year interview period)
- `42` = Round **4/2** value (middle period)
- `53` = Round **5/3** value (later period)
- `23` = status for calendar year **2023** (often end-of-year / full-year)

So for your examples:
- `RTHLTH53`, `MNHLTH53` = measured in Round 5/3
- `K6SUM42`, `PHQ242` = measured in Round 4/2

### Why Not

Why not use PCA or latent embeddings?

- **PCA** means principal component analysis, a dimensionality reduction method that builds synthetic linear combinations of features
- that could compress the space, but it would reduce interpretability

Why not engineer lots of manual interaction terms?

- it would create more tuning burden
- it would make the results harder to attribute to clean feature blocks

### Cross-Questions You Should Expect

- Why did you create `CHRONIC_CT` instead of keeping diagnoses separate?
- Why does `LIMIT_CT` matter?
- Are mental health variables predictive by themselves or only with chronic burden?
- Why engineer compact scores instead of using more raw variables?

Strong short answer:

> I engineered compact burden features because I wanted a stable, explainable structural representation. `LIMIT_CT` and especially `CHRONIC_CT` are the features that turn diffuse survey information into deployable predictors.

---

## 4. Feature Ladder: Why `B0` To `B5`

### What

The notebook defines a cumulative feature ladder:

| Block | Features | What It Tests |
| --- | --- | --- |
| `B0_behavior` | `PHYEXE53`, `OFTSMK53` | Minimal behavior-only feasibility |
| `B1_mental` | `B0 + RTHLTH53 + MNHLTH53 + K6SUM42 + PHQ242` | Latent health signal before structural burden |
| `B2_functional` | `B1 + LIMIT_CT` | Functional impairment as structural burden |
| `B3_chronic` | `B2 + CHRONIC_CT` | Chronic burden as the first full structural inflection |
| `B4_ses_ins` | `B3 + poverty + income + insurance + employment` | Extra lift from socioeconomic and coverage context |
| `B5_util_nonlabel` | `B4 + office/outpatient/Rx counts` | Upper bound with proximate utilization behavior |

### How

The blocks are cumulative:

- `B1` contains `B0`
- `B2` contains `B1`
- `B3` contains `B2`
- and so on

### Why Not

Why not train one giant feature set immediately?

- because you would lose the ability to explain where the performance came from
- you would know what won, but not why it won

Why not make the blocks independent instead of cumulative?

- because independent blocks are worse for testing incremental structure
- the cumulative setup mirrors the actual scientific question: what is the first point at which the system becomes good enough?

Why not stop at `B0` if the project is supposed to be behavior-oriented?

- because the notebook is explicitly testing whether behavior-only is enough
- the answer is no
- the whole point is to identify the minimum additional structure required after behavior

### Cross-Questions You Should Expect

- Why did you build cumulative blocks instead of one final dataset?
- What is the scientific reason for `B3` being special?
- Why include `B4` and `B5` if you knew you might not deploy them?

Strong short answer:

> The feature ladder is the experiment. It shows exactly where the model crosses from weak signal to stable segmentation. `B4` and `B5` are included as benchmarks so I can show what is gained by adding sensitive or proximate features, then justify why I still deploy `B3`.

---

## 5. Model Ladder: Why Multiple Algorithms

### What

The notebook uses five models:

- `logit`
- `logit_l1`
- `logit_l2`
- `rf`
- `xgb`

A **hyperparameter** is a model setting chosen by the engineer before training, like tree depth or regularization strength.

### Why

The project wants to know what kind of structure the problem needs:

- linear?
- sparse linear?
- interaction-heavy?
- boosted nonlinear?

Using multiple models is how the notebook tests that.

### How

#### `logit`

Standard logistic regression:

Role:

- clean linear baseline
- interpretable
- sanity check for whether the problem is already linearly separable

#### `logit_l1`

L1-regularized logistic regression:

**Regularization** means penalizing model complexity so the fitted solution does not become overly unstable.  
**Sparsity** means many coefficients are pushed toward zero so the solution becomes more selective.

Role:

- tests whether the signal can be captured with a sparse linear surface
- acts like weak built-in feature selection

#### `logit_l2`

L2-regularized logistic regression:

Role:

- stabilized linear benchmark
- useful when features are correlated

#### `rf`

Random forest:

```python
RandomForestClassifier(
    n_estimators=400,
    min_samples_leaf=10,
    n_jobs=-1,
    random_state=random_state
)
```

Role:

- nonlinear interaction benchmark
- tests whether bagged trees add meaningful lift

#### `xgb`

XGBoost:

```python
XGBClassifier(
    n_estimators=600,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    reg_lambda=1.0,
    random_state=random_state,
    eval_metric="logloss",
    n_jobs=-1
)
```

Role:

- strongest tabular production candidate
- chosen as the best model family for calibration and bootstrap analysis

### Why Not

Why not use only XGBoost from the start?

- then you would not know whether the gains came from algorithmic complexity or from feature structure

Why not use only logistic regression?

- because if nonlinear structure mattered a lot, a pure linear story would understate the problem

Why not use LightGBM or CatBoost?

- they are strong alternatives for tabular data
- they were not implemented in this notebook because the current model ladder was already enough to answer the structural question
- they could be better in a v2 if speed, categorical handling, or stronger boosting benchmarks become more important

Why not use neural networks?

- neural nets can work on tabular data, but they often need more tuning and larger data to clearly outperform boosted trees
- here the tabular benchmark space was better covered by logistic, forest, and boosting

### Cross-Questions You Should Expect

- Why so many models?
- Why include both `logit`, `logit_l1`, and `logit_l2`?
- Why not LightGBM?
- Why not neural nets?

Strong short answer:

> I used the model ladder to test what kind of structure the problem actually needed. The closeness of the results across model families tells me the main story is feature structure, not one magic algorithm.

---

## 6. Training Pipeline

### What

The modeling notebook uses:

- a `75/25` train-test split
- stratification by `LOW_RISK`
- block-specific preprocessing inside a reusable pipeline

Exact split counts:

- train rows `14,189`
- test rows `4,730`
- train positives `4,184`
- test positives `1,395`

### How

**Leakage** means the model sees information that is too close to the answer, which inflates apparent performance but weakens real-world validity.

Then it automatically infers feature treatment:

- low-cardinality numeric survey-coded fields are treated as categorical
- larger-range numeric fields are treated as continuous

The preprocessing object is:

```python
ColumnTransformer(
    [
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ]
)
```

**One-hot encoding** means turning a category into separate binary indicator columns.  
**Standardization** means rescaling numeric features so they are on a comparable scale, typically centered and scaled by variance.

Then the notebook wraps preprocessing and model training in one `Pipeline`.

### Why Not

Why not hard-code categorical and numeric columns manually?

- automatic inference is more robust to slight schema variation
- MEPS fields are often numeric in storage but categorical in meaning

Why not preprocess outside the pipeline?

- then training and inference could drift
- the saved artifact would no longer represent the full transformation chain

Why not aggressively impute everything before training?

- the reduced table already has low residual missingness
- many MEPS fields use sentinel-coded survey responses that are better preserved as categories than over-imputed

Why not use survey-weighted modeling?

- survey weights are crucial for population inference
- the notebook is solving predictive segmentation, not weighted national prevalence estimation
- survey-weighted modeling could be a better route if the next version shifts toward policy inference instead of deployment scoring

### Cross-Questions You Should Expect

- Why exclude `TOTEXP23`, `ERTOT23`, and `IPDIS23` from inputs?
- Why put preprocessing inside a pipeline?
- Why not use weights?
- Why are some numeric fields treated as categorical?

Strong short answer:

> I designed the pipeline to be leakage-safe, schema-robust, and deployable as one artifact. The point was to make the training logic and inference logic identical.

---

## 7. Evaluation Metrics

### Why

No single metric captures what the project needs.

**AUC** means Area Under the ROC Curve. It measures how well the model ranks positives above negatives across thresholds.  
**Average precision** means the area under the precision-recall curve. It tells you how well the model retrieves positives when threshold varies.  
**Precision** means: among people predicted low risk, how many truly are low risk?  
**Recall** means: among all truly low-risk people, how many did I find?  
**F1** means the harmonic mean of precision and recall at a chosen threshold.  
**Brier score** means mean squared error of predicted probabilities, so lower is better.  
**Calibration** means whether predicted probabilities match observed frequencies.

These metrics together answer different questions:

- ranking quality
- positive-class retrieval
- threshold behavior
- probability quality

### How

### Why Not

Why not optimize only for accuracy?

- because a model can get high accuracy by leaning on the majority class
- the `B0` baseline proves this

Why not optimize only for AUC?

- because a model can rank well but still be poorly calibrated

Why not optimize only for F1?

- because F1 depends on one threshold and hides probability quality

Why not optimize threshold directly from the start?

- because the notebook is first asking a structural question about blocks and model families
- threshold optimization could be a good v2 once the final production objective is locked

### Cross-Questions You Should Expect

- Why did you focus on AUC and Brier instead of accuracy?
- What does calibration add?
- Why use both threshold-based and threshold-free metrics?

Strong short answer:

> I used a multi-metric evaluation because the problem is about more than class labels. I need good ranking, reasonable threshold behavior, and reliable probabilities.

---

## 8. Main Results

### What

The mean leaderboard across all blocks is:

| Model | Mean AUC | Mean AP | Mean Brier |
| --- | ---: | ---: | ---: |
| `xgb` | `0.753823` | `0.562230` | `0.162820` |
| `logit_l1` | `0.753460` | `0.559737` | `0.163521` |
| `logit` | `0.753275` | `0.559624` | `0.163648` |
| `logit_l2` | `0.753275` | `0.559624` | `0.163648` |
| `rf` | `0.753249` | `0.561987` | `0.164620` |

XGBoost AUC by feature block:

- `B0 = 0.579418`
- `B1 = 0.685705`
- `B2 = 0.710644`
- `B3 = 0.772639`
- `B4 = 0.824610`
- `B5 = 0.949921`

### Why

This result supports a very specific interpretation:

- algorithm choice matters less than feature structure
- the big jump happens when chronic burden is added
- later blocks improve performance, but not all later blocks are equally deployable

### How

The strongest comparison row for the deployment story is `B3`.

`B3 + xgb`:

- AUC `0.772639`
- AP `0.556857`
- F1 `0.485124`
- precision `0.572683`
- recall `0.420789`
- Brier `0.168591`

`B3 + logit`:

- AUC `0.774447`
- AP `0.562234`
- F1 `0.469019`
- precision `0.586652`
- recall `0.390681`
- Brier `0.168068`

That is a very important finding:

> At `B3`, XGBoost and logistic regression are extremely close.

This means `B3` is not a fragile boosting trick. It is a structural sufficiency result.

### Why Not

Why not say XGBoost dominated everything?

- because that is not what the notebook shows
- the mean leaderboard is close
- at `B3`, logistic regression is actually slightly ahead on AUC and Brier

Why not say behavior-only worked fine?

- because `B0` is weak for every model family

Why not jump directly from `B0` to `B5`?

- because then you lose the notebook's main result: the inflection happens at `B3`

### Cross-Questions You Should Expect

- Did XGBoost actually beat logistic regression where it mattered?
- What exactly proves that `B3` is the inflection point?
- Why do later blocks not automatically win deployment?

Strong short answer:

> The notebook's real finding is not "XGBoost wins." It is "once chronic burden is added, every sensible model becomes usable, and that is the first point where the segment becomes stable enough to defend."

---

## 9. Why The `B0` Baseline Matters

### What

`B0_behavior + logit` gives:

- AUC `0.585799`
- AP `0.360270`
- F1 `0.000000`
- precision `0.000000`
- recall `0.000000`
- Brier `0.202384`

### Why

This is the best anti-accuracy example in the whole notebook.

It shows that sparse behavior-only signal is not enough to recover the low-risk cohort.

### How

At the default `0.5` threshold, the baseline behaves like a majority-class model. It fails to retrieve low-risk members even though the dataset is not extremely imbalanced.

### Why Not

Why not dismiss this baseline as useless?

- because it teaches you what the data can and cannot do
- it proves the project is not over-claiming behavior-only prediction

Why not lead with approximate accuracy here?

- because the baseline is precisely the case where accuracy is misleading

### Cross-Questions You Should Expect

- Why isn't accuracy enough here?
- What does the zero recall baseline tell you about the data?

Strong short answer:

> The baseline matters because it shows behavior-only signal is structurally underpowered. It also proves why I should not use accuracy as my main selection metric.

---

## 10. Bootstrap Stability

### What

The notebook runs a **bootstrap**, meaning repeated resampling with replacement, on the held-out test predictions.

Setup:

- best model family fixed to `xgb`
- blocks tested from `B0` to `B5`
- `N_BOOT = 300`

Per resample it computes:

- AUC
- Brier
- low-risk segment rate

### Why

This is the strongest modeling idea in the notebook.

The project does not just care about predictive accuracy. It cares about whether the low-risk cohort stays stable under sampling noise.

### How

Within each bootstrap sample:

```python
cutoff = np.quantile(proba, 0.30)
low_risk_flag = (proba <= cutoff).astype(int)
prevalence = low_risk_flag.mean()
```

So the operational segment is not "score above 0.5." It is a quantile-defined cohort.

`B3` bootstrap summary:

- AUC mean `0.772504`
- AUC SD `0.007410`
- Brier mean `0.168471`
- Brier SD `0.002903`
- low-risk rate mean `0.300303`
- low-risk rate SD `0.000496`

### Why Not

Why bootstrap and not only cross-validation?

- **Cross-validation** means repeatedly splitting the training data into folds to estimate performance
- it is useful, but the notebook's unique question is operational stability of the held-out segment
- bootstrap directly measures how much the final evaluated segment moves around under resampling

Why not nested cross-validation?

- nested CV would be stronger for full model-tuning rigor
- it was skipped because the notebook is more about feature sufficiency than exhaustive tuning
- it could be better in a v2 focused on final model optimization

Why not bootstrap all model families?

- the notebook first selects the best family, then studies block stability within that family
- broadening bootstrap across all families is a possible extension

### Cross-Questions You Should Expect

- Why bootstrap the test predictions?
- Why is segment-size stability more important than only AUC?
- Why did you not use repeated cross-validation instead?

Strong short answer:

> I used bootstrap because the deployment decision is about whether the resulting cohort is stable, not just whether a score is high on one split. Bootstrap lets me quantify that directly.

---

## 11. The `B0` Bootstrap Anomaly

### What

`B0_behavior` has:

- low-risk rate mean `0.400617`
- low-risk rate SD `0.007623`

That is the weird row in the stability table.

### Why

It is memorable and interview-useful because it shows weak models do not just rank poorly. They also generate unstable operational segmentation behavior.

### How

The likely explanation is score resolution and ties:

- with only two weak behavior features, predicted probabilities are coarse
- many observations cluster near the quantile cutoff
- the effective bottom-30% cohort expands because the score distribution is not well separated

### Why Not

Why not treat this as a coding bug immediately?

- because the logic is consistent across blocks
- only the weakest block shows the inflated segment size
- that pattern itself is evidence about score granularity, not just about AUC

Why not ignore it because `B0` is not deployable anyway?

- because it is one of the best pieces of evidence for why weak signal is operationally dangerous

### Cross-Questions You Should Expect

- Why is `B0` selecting about 40% under a 30% quantile rule?
- What does that tell you beyond "B0 is bad"?

Strong short answer:

> It tells me the weak block lacks score resolution. That is a stronger criticism than low AUC alone, because it means even the operational segment size becomes unstable.

---

## 12. Final Model Selection

### How

The practical reasoning is:

- `B0-B2` are not strong enough
- `B3` is the first stable inflection
- `B4` adds SES and insurance sensitivity
- `B5` adds utilization variables that are too close to realized cost behavior

This is where **proxy leakage** becomes important. Proxy leakage means the input is not literally the target, but it is so close to the target-generating process that performance becomes less informative for deployable early-stage prediction.

### Why Not

Why not deploy `B4`?

- because SES and insurance features raise fairness and regulatory concerns
- `B3` already gets to a stable deployable point without them

Why not deploy `B5`?

- because it uses utilization signals that are very close to realized cost behavior
- that makes it a useful upper-bound benchmark, not the cleanest deployment choice

Why not deploy logistic regression at `B3`, since it is very close?

- that would be defensible
- the notebook keeps `xgb` because it tops the overall model family leaderboard and remains the strongest general tabular production candidate

### Cross-Questions You Should Expect

- Why `B3 + xgb` and not `B3 + logit`?
- Why not `B4`?
- Why not `B5` if it is clearly strongest on metrics?

Strong short answer:

> I picked `B3 + xgb` because `B3` is the first stable structural block and `xgb` is the strongest overall model family. `B4` and `B5` improve score metrics, but they move the system away from the deployment objective I actually care about.

---

## 13. Production Artifact

### What

The notebook does not stop at evaluation. It saves the final pipeline and shows a simple inference API.


```python
reloaded_pipe = joblib.load(MODEL_PATH)
proba = reloaded_pipe.predict_proba(X_test.iloc[:10])[:, 1]
```

Then the notebook sketches a FastAPI endpoint:

```python
@app.post("/score")
def score_member(member: dict):
    df = pd.DataFrame([member])
    p_low_risk = model.predict_proba(df)[0, 1]

    return {
        "low_risk_probability": float(p_low_risk),
        "risk_tier": "Low" if p_low_risk >= 0.7 else "Standard"
    }
```

### Why Not

Why not export only the classifier weights?

- because then preprocessing would need to be rebuilt separately
- that is a common source of training-serving mismatch

Why not finalize a more complex API contract now?

- the notebook is demonstrating deployability, not finishing production API design
- schema validation and monitoring would be a logical v2 improvement

### Cross-Questions You Should Expect

- What exactly gets serialized?
- Can the pipeline score raw rows without retraining?
- What would you harden before putting the API in production?

Strong short answer:

> I serialized the full preprocessing-plus-model pipeline, not just the estimator. That means the same transformation logic used in training is reused at inference time.

---

## 14. Alternative Routes Skipped, Why They Were Skipped, And When They Could Be Better

This is the section to memorize if you want to sound strong when the interviewer asks, "Why did you not do X?"

| Alternative Route | Why It Was Skipped In This Notebook | When It Could Be Better |
| --- | --- | --- |
| Direct spend regression on `TOTEXP23` | Too tail-dominated and noisy for the main segmentation objective | Better if the product goal shifts to exact cost forecasting |
| Log-spend regression | More stable than raw spend, but still solves cost prediction, not low-risk cohort selection | Better if you want a smoother intermediate forecasting layer |
| Quantile regression | Useful for tail-aware spend modeling, but the notebook is focused on binary low-risk membership | Better for estimating spend bands or risk intervals |
| Two-stage model: acute-event classifier plus spend classifier | More complex pipeline than needed for the first structural study | Better if you want causal-style decomposition between acute shocks and chronic baseline cost |
| Multiclass or ordinal risk bands | Harder to calibrate and explain than one conservative low-risk cohort | Better if the business wants several pricing tiers, not just low-risk selection |
| LightGBM or CatBoost | Not necessary to answer the structural question once RF and XGB were already included | Better if categorical handling speed or stronger boosting benchmarks become important |
| Neural networks for tabular data | Higher tuning burden and weaker interpretability for this dataset size and structure | Better if you have much larger data, richer features, or strong representation-learning goals |
| Survey-weighted modeling | The project is predictive segmentation, not weighted population inference | Better for policy estimation or nationally representative inference |
| Class weighting as the main optimization lever | The positive class is not so rare that weighting had to be the first move, and the core problem was structure, not thresholding | Better if recall becomes a primary business requirement |
| Threshold tuning as the main optimization lever | The notebook first establishes ranking quality and stable structure before optimizing an operating point | Better when a business owner specifies the exact precision-recall tradeoff |
| Full grid search | Too expensive relative to the structural question | Better in a final production tuning pass |
| Bayesian optimization | Useful, but unnecessary before the block structure was validated | Better when you commit to one model family and want incremental gains |
| Nested cross-validation | Stronger for final model-selection rigor, but heavier than needed for a first structural notebook | Better in a publication-grade or final production optimization stage |
| Temporal forecasting across years or panels | Requires data design beyond the current same-year notebook | Better for true forward-looking actuarial prediction |

Short interview version:

> I intentionally skipped routes that would have answered a different question. This notebook's job was to identify the minimum stable predictive structure, not to exhaust every modeling variant.

---

## 15. Rapid-Fire Cross-Question Bank

### What is your strongest methodological contribution?

Using bootstrap stability of the low-risk cohort size, not just a score leaderboard, to define the deployment boundary.

### What is your strongest empirical finding?

Chronic burden is the first compact feature that makes the low-risk segment reliably separable and stable.

### What is your strongest governance finding?

You can stop at `B3` and still get a stable usable segment without relying on SES-heavy or utilization-heavy deployment features.

### What is the most honest weakness?

The notebook is based on a single-year same-year label, so it is better understood as stable segmentation research than as a full forward-looking actuarial forecast.

### What result would you never overclaim?

I would not say the notebook proves uninsured people are healthier. I would only say it helps size a possible outreach cohort under a conservative segmentation framework.

---

## 16. Numbers To Remember

These are the numbers worth memorizing because they are high-signal and likely to come up in cross-questioning.

### Dataset and split

- dataset size: `18,919`
- model-ready columns: `59`
- `LOW_RISK` prevalence: `0.2948887361911306`, or about `29.49%`
- train rows: `14,189`
- test rows: `4,730`
- train positives: `4,184`
- test positives: `1,395`

### Cost distribution

- `TOTEXP23` mean: `8422.054125`
- `TOTEXP23` median: `1816.000000`
- `TOTEXP23` 95th percentile: `37686.400000`
- `TOTEXP23` 99th percentile: `98447.080000`
- `TOTEXP23` max: `574675.000000`

### Catastrophic flags

- `CATA_10K = 0.193615`, or about `19.36%`
- `CATA_20K = 0.104551`, or about `10.46%`

### ER cost jump

- median spend with `0` ER visits: `1271.5`
- median spend with `1` ER visit: `7656.0`
- median spend with `2` ER visits: `14964.0`

### XGBoost AUC by block

- `B0 = 0.579418`
- `B1 = 0.685705`
- `B2 = 0.710644`
- `B3 = 0.772639`
- `B4 = 0.824610`
- `B5 = 0.949921`

### Overall leaderboard

- `xgb`: mean AUC `0.753823`, mean Brier `0.162820`
- `logit_l1`: mean AUC `0.753460`, mean Brier `0.163521`
- `logit`: mean AUC `0.753275`, mean Brier `0.163648`
- `rf`: mean AUC `0.753249`, mean Brier `0.164620`

### `B3 + xgb`

- AUC `0.772639`
- AP `0.556857`
- F1 `0.485124`
- precision `0.572683`
- recall `0.420789`
- Brier `0.168591`

### `B3 + logit`

- AUC `0.774447`
- AP `0.562234`
- F1 `0.469019`
- precision `0.586652`
- recall `0.390681`
- Brier `0.168068`

### Bootstrap `B3`

- AUC mean `0.772504`
- AUC SD `0.007410`
- Brier mean `0.168471`
- Brier SD `0.002903`
- low-risk rate mean `0.300303`
- low-risk rate SD `0.000496`

### Bootstrap anomaly to remember

- `B0` low-risk rate mean `0.400617`
- `B0` low-risk rate SD `0.007623`

Why this one matters:

- it is the cleanest evidence that weak signal hurts not only ranking but also operational segment stability

---

## 17. Final One-Paragraph Version To Memorize

> I built a leakage-safe, block-structured low-risk classification system on MEPS 2023. Upstream, I engineered compact burden features like chronic condition count and functional limitation count because raw healthcare cost is highly right-skewed and not the right direct modeling object for stable segmentation. In the modeling notebook, I compared logistic regression, sparse logistic, ridge logistic, random forest, and XGBoost across cumulative feature blocks from behavior-only to utilization-augmented. The key result was that model family mattered less than feature structure: behavior alone was weak, mental and functional features helped, and chronic burden was the first block that made the low-risk segment meaningfully stable. I selected `B3_chronic + XGBoost` not because it was the single most extreme score in the notebook, but because it was the first block that jointly met the requirements of discrimination, calibration, bootstrap stability, and deployment defensibility without relying on the most fairness-sensitive or most proxy-leakage-prone features.
