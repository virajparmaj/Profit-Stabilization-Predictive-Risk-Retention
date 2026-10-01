# Research-paper development pack

**Updated:** 2026-10-01. **Status:** Core research pipeline implemented and exploratory E1–E4 results available; independent replication and remaining inference are pending.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

[Verification report](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/19_VERIFICATION_AND_PR_READINESS.md) records the completed integrity fixes, exact numerical comparisons, and new derived evidence.

## Recommendation

Develop a focused empirical paper asking whether classification-based model choices remain persuasive when low-spending cohorts are evaluated for **membership reproducibility and absolute versus relative expenditure variability at matched population capacity**.

The plausible novelty is the decision-relevant empirical comparison. Existing literature already covers prediction instability, spending-versus-need proxy bias and variability beyond means. The new contribution has to be established through corrected experiments; it is not guaranteed by combining familiar metrics.

**Working title:** Evaluating Low-Spending Healthcare Cohorts: Membership Stability and Expenditure Dispersion in MEPS.

## Current state

- **Implemented:** corrected source-built cohort, grouped model evaluation, weighted selection, full-pipeline refits, survey-aware conditional inference, sensitivity runner and immutable provenance.
- **Completed:** 140 E1 fits, 800 main E2 refits, 80 pilot refits, 90 E4 fits, R survey benchmark, and the original 23 scientific tests. The verification pass now has 46 passing tests plus 10 repeat E1 fits and 80 repeat E2 refits.
- **Main result:** B3 models have similar AUROC, but logistic averages 6.15% membership disagreement versus 10.54% for XGBoost at matched capacity. This is internal exploratory evidence, not a population confidence claim.
- **Remaining:** independent-year replication, direct-cost baselines, fuller secondary/reference-population inference and final manuscript validation.

Read [Implementation and results](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/17_IMPLEMENTATION_AND_RESULTS.md) first. The [execution prompt](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/16_IMPLEMENTATION_PROMPT.md) records the requested work and acceptance criteria.

## Reading map

| File | Purpose |
|---|---|
| [16_IMPLEMENTATION_PROMPT.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/16_IMPLEMENTATION_PROMPT.md) | Reusable execution prompt and acceptance criteria. |
| [17_IMPLEMENTATION_AND_RESULTS.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/17_IMPLEMENTATION_AND_RESULTS.md) | Actual code, experiment results, figures and remaining paper requirements. |
| [18_PROTOCOL_DEVIATIONS_AND_NEXT_STEPS.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/18_PROTOCOL_DEVIATIONS_AND_NEXT_STEPS.md) | Scope decisions, limitations and prioritized follow-up. |
| [01_PROJECT_AND_DATA.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/01_PROJECT_AND_DATA.md) | What was actually investigated; dataset, labels, models and populations. |
| [02_NOVELTY_AND_RESEARCH_QUESTIONS.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/02_NOVELTY_AND_RESEARCH_QUESTIONS.md) | Recommended modest contribution, priorities, hypotheses and falsifiers. |
| [03_RELATED_WORK.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/03_RELATED_WORK.md) | Closest papers, overlapping contributions and remaining research boundary. |
| [04_VERIFIED_FINDINGS.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/04_VERIFIED_FINDINGS.md) | Supported observations, expenditure interpretation and hidden results. |
| [05_VALIDITY_CORRECTIONS.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/05_VALIDITY_CORRECTIONS.md) | Fourteen validity issues and the repair order. |
| [06_STUDY_PROTOCOL.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/06_STUDY_PROTOCOL.md) | Population, estimands, splits, weights, refits and uncertainty. |
| [07_EXPERIMENT_PLAN.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/07_EXPERIMENT_PLAN.md) | Essential E0–E4, recommended E5–E7, optional E8–E10. |
| [08_IMPLEMENTATION_ROADMAP.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/08_IMPLEMENTATION_ROADMAP.md) | Concrete modules, work packages, dependencies and completion gates. |
| [09_TEST_SPECIFICATIONS.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/09_TEST_SPECIFICATIONS.md) | Scientific invariants, edge cases and validation requirements. |
| [10_RESULTS_REGISTER.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md) | Actual completed checks and explicit pending experiment slots. |
| [11_PAPER_BLUEPRINT.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/11_PAPER_BLUEPRINT.md) | Title, argument, preliminary abstract, sections and result-to-figure map. |
| [12_CONCLUSIONS_AND_DECISION_GATES.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/12_CONCLUSIONS_AND_DECISION_GATES.md) | Current conclusion, null-result paths and readiness criteria. |
| [13_REPRODUCIBILITY_AND_HANDOFF.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/13_REPRODUCIBILITY_AND_HANDOFF.md) | Commands, evidence paths, checksums and implementation handoff. |
| [14_LITERATURE_SEARCH_LOG.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/14_LITERATURE_SEARCH_LOG.md) | Sources, queries, access limitations and submission follow-up. |
| [15_CANDIDATE_RESEARCH_QUESTIONS.md](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/15_CANDIDATE_RESEARCH_QUESTIONS.md) | Eight research questions with hypotheses, novelty risks and required work. |

Start with **02 → 08 → 10 → 12** for the research decision, execution plan, actual evidence and readiness assessment. Read **05 → 06 → 09** before implementing. Use **11** only after new results justify manuscript claims.

## Original minimum implementation plan (now partly executed)

Implement E0/P0–P4: reconstruct scientific variables, group splits correctly, define weighted selection, train the two B3 anchors from source and validate the statistical helpers. Then run a feasibility pilot followed by E1–E4. Prioritize an independent-year replication before expensive model expansion. A prospective claim requires the additional longitudinal E7 design.

These Markdown files are intended to become the evidence and methods backbone of a paper. Their “proposed” and “not run” labels are deliberate: plans, saved notebook outputs, cached-score rechecks and fresh experiments are different kinds of evidence.

## Maintaining this pack

The results register is authoritative for execution status. Documents 06–09 define planned work; the original audit's Python/JSON files supply exact historical numbers. Update results and provenance together, record protocol deviations, and only replace preliminary paper language after corrected outputs exist. Original data and notebooks remain unchanged. A new corrected pipeline was added on 2026-09-30; dated plans below must be read alongside the implementation report.
