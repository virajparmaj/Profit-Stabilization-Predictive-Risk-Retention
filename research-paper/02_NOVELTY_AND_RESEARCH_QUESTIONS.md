# The modest novelty worth pursuing

**Updated:** 2026-09-25. **Status:** Proposed empirical contribution; novelty and primary hypotheses remain unproven.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

## Recommended contribution

**Test whether common model-evaluation choices lead to different low-spending cohort conclusions at the same population capacity.** Compare label discrimination/calibration, reproducibility of selected people after refitting, and absolute versus relative expenditure dispersion. The proposed novelty is an empirical decision consequence in a carefully defined setting, not a new metric or learning algorithm.

The most credible package is corrected E0–E4 plus a frozen independent-year replication (E5). The minimum investigation is E0–E4; it becomes a defensible empirical paper only if the findings are informative relative to prior art. A second year is the strongest economical addition once the pipeline works. It cannot rescue a trivial result by itself.

| Priority | Additional work | Why it strengthens the contribution |
|---|---|---|
| 1 | Correct constructs, eligibility, score direction and evaluation units | Establishes that the observed phenomenon is real rather than an implementation artifact |
| 2 | Refit compact models and evaluate the same reference people | Tests the unsupported stable-membership premise directly |
| 3 | Compare spending distributions at matched weighted capacity | Makes model comparisons meaningful and distinguishes dollar from relative variation |
| 4 | Decompose zero expenditure and test simple comparators | Determines whether the result is more informative than selection mechanically lowering the mean |
| 5 | Replicate a frozen comparison in another nonoverlapping year/sample | Reduces dependence on an already explored dataset |
| 6 | Add a two-part direct-cost baseline | Tests whether the custom classification target is useful relative to predicting expenditure directly |

Do not start with a new neural network, broad hyperparameter search, SHAP gallery, or dashboard redesign. Those do not answer the central unresolved question.

## Primary hypotheses and falsifiers

- **H1:** At least one prespecified model/block contrast differs materially in membership reproducibility despite similar classification performance, or its ordering changes between the two criteria. Falsifier: negligible or imprecise differences, or the same conclusions across criteria.
- **H2:** Lower mean and dollar SD can coexist with higher relative dispersion under corrected selection; quantify how much zero expenditure explains and whether it changes comparisons between candidate policies. Falsifier: disappearance after correction, dependence on a handful of observations, or no distinction from simple controls.
- **H3, secondary:** Insurance/utilization features change the measured composition of selected cohorts. This is descriptive construct validation, not evidence of causal access effects or clinical harm.

The primary H1 contrast is corrected B3 logistic versus B3 XGBoost at 30% weighted capacity. B2 versus B3, B3 versus B4, and B4 versus B5 are secondary paired contrasts. Do not pick a different primary contrast because the first one is null.

## What would count as a useful result?

A publishable result need not be a large AUROC gain. It could show that a compact model has comparable discrimination but materially different identity reproducibility, with a clear expenditure consequence and uncertainty. It could also show that an apparent relative-dispersion effect is mostly explained by zero mass and does not imply increased dollar variability. The latter needs a substantive empirical implication or replication; the algebra itself is established.

Do not force a single preferred model when criteria conflict. Report Pareto tradeoffs and state the objective under which a comparison matters. Without a specified clinical or financial utility, lower CV alone does not establish a better selection policy.

Practical margins must be justified and recorded before the new comparisons. The advisory's AUROC margin of 0.01 is a proposed operational tolerance, not a universal clinical standard. Show continuous effects and uncertainty even if a chosen margin is not crossed. Never optimize margins to obtain a favorable conclusion.

## Existing novelty-gap assessment

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

Eight alternative questions, hypotheses, prior-art boundaries and risks are retained in [15_CANDIDATE_RESEARCH_QUESTIONS.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/15_CANDIDATE_RESEARCH_QUESTIONS.md).
