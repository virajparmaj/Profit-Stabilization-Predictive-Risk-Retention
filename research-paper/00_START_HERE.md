# Research-paper development pack

**Updated:** 2026-09-25. **Status:** Planning and evidence pack; study extension not yet implemented.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

## Recommendation

Develop a focused empirical paper asking whether classification-based model choices remain persuasive when low-spending cohorts are evaluated for **membership reproducibility and absolute versus relative expenditure variability at matched population capacity**.

The plausible novelty is the decision-relevant empirical comparison. Existing literature already covers prediction instability, spending-versus-need proxy bias and variability beyond means. The new contribution has to be established through corrected experiments; it is not guaranteed by combining familiar metrics.

**Working title:** Evaluating Low-Spending Healthcare Cohorts: Membership Stability and Expenditure Dispersion in MEPS.

## Current state

- **Done:** repository/evidence review, targeted literature review, deterministic legacy-label/count checks, cached-score evaluation, descriptive burden sensitivity, this implementation and paper plan.
- **Not done:** corrected cohort/pipeline, fresh model reproduction, paired model experiments, repeated training refits, survey confidence intervals, independent-year replication or a completed manuscript.
- **Main existing signal:** nominal 30% selection lowers spending mean from $7,487 to $2,779 and SD from $19,808 to $9,993, while CV rises from 2.65 to 3.60. These historical cache summaries need corrected, matched-capacity validation.
- **Critical blockers:** reversed selection in the old stability notebook, size-versus-identity confusion, diagnosis/limitation construct overlap, missing-code handling and survey/eligibility issues.

## Reading map

| File | Purpose |
|---|---|
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

## Smallest credible next step

Implement E0/P0–P4: reconstruct scientific variables, group splits correctly, define weighted selection, train the two B3 anchors from source and validate the statistical helpers. Then run a feasibility pilot followed by E1–E4. Prioritize an independent-year replication before expensive model expansion. A prospective claim requires the additional longitudinal E7 design.

The 16 Markdown files are intended to become the evidence and methods backbone of a paper. Their “proposed” and “not run” labels are deliberate: plans, saved notebook outputs, cached-score rechecks and fresh experiments are different kinds of evidence.

## Maintaining this pack

The results register is authoritative for execution status. Documents 06–09 define planned work; the original audit's Python/JSON files supply exact historical numbers. Update results and provenance together, record protocol deviations, and only replace preliminary paper language after corrected outputs exist. No original data, notebook or model implementation was changed when this folder was created.
