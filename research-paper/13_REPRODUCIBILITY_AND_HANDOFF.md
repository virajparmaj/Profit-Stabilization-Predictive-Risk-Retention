# Reproducibility and implementation handoff

**Updated:** 2026-09-25. **Status:** Current evidence provenance plus a proposed future reproducibility contract.

[Folder index](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/00_START_HERE.md) · [Results register](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/research-paper/10_RESULTS_REGISTER.md)

## Existing executable verification

The current audit can be run from the repository root with:

```sh
/tmp/profit-stabilization-research-review-venv/bin/python analysis/research_review/verify_existing_evidence.py
```

This temporary task-specific venv currently obtains dependencies through the existing global environment's site-packages path. It is sufficient for this local recheck but is not a portable, independently locked research environment. The script requires numpy, pandas, pyarrow and scikit-learn. Build and lock a clean per-project environment during P0 before fresh modeling. Do not mistake the successful audit for environment reproducibility of the saved XGBoost models.

The script rewrites only its adjacent `verified_metrics.json`; it does not fit models or alter source data. Preserve a versioned snapshot if rerunning against changed inputs. The script must stay at its existing repository location because it resolves the project root relative to itself.

## Evidence paths

- [Audit source](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/research_review/verify_existing_evidence.py)
- [Exact audited metrics](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/research_review/verified_metrics.json)
- [Full original research advisory](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/research_review/RESEARCH_ADVISORY.md)
- [Original literature search log](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/research_review/SEARCH_LOG.md)
- [Raw MEPS file](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/data_raw/h251.csv)
- [Model-ready file](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/data_processed/meps_model_ready_2023.csv)
- [Existing cached scores](/Users/veerr_89/Work/projects/Profit-Stabilization-Predictive-Risk-Retention/analysis/.cache/oof.parquet)

## Input fingerprints at the successful recheck

| Input | SHA-256 |
|---|---|
| raw | `f00d63d42e6454d00f520b6b1535dd6ef1dfcb90b128adb90f791538b4232d26` |
| model_ready | `c3218010eac28cfd4916ff099ed3943efe7963aff19f9849149252caa3d07cb8` |
| notebook_copy | `c3218010eac28cfd4916ff099ed3943efe7963aff19f9849149252caa3d07cb8` |
| oof | `60c86973c387a805581fd30916ddc754be8f277bad74d42b7368aaaf299819f1` |
| stale_scores | `49149d9afa53c24207826120cabf829e72bbf6d6fbc8b0c61aea1d1ee6f75627` |


Identical model-ready and notebook-copy hashes confirm duplication. Hash agreement verifies file identity, not scientific correctness. A valid cache needs a manifest linking data, code, features, folds, model configuration and environment; the existing OOF cache does not establish all of that.

## Future run manifest

Store run ID, UTC timestamp, protocol/config hash, Git revision and dirty-state description, source checksums, package versions and lock hash, OS/architecture, estimator settings, thread count, random seeds, split manifest hash, target cutoffs, design variables, weight normalization, selection/tie rule, failures, warnings, and output hashes. Document licensing/access conditions for external datasets and publish download instructions when redistribution is unsuitable.

Save individual held-out scores with ID, fold, model/block, target definition, score class, survey weight and run ID. Save repeated-refit scores with refit ID and fixed reference-set ID. Keep raw sensitive or identifying additions out of public exports; this plan currently uses public MEPS records.

## Handoff order

1. Read documents 02, 05 and 06 to understand the scientific target and corrections.
2. Implement P0–P4 from document 08 with the meaningful tests in document 09.
3. Freeze the protocol/configuration and log deviations before running E1–E4.
4. Append actual results to document 10, keeping legacy and corrected estimates separate.
5. Apply the decision gates in document 12; then draft document 11's manuscript structure using actual outputs.

This Markdown pack is the navigable planning and evidence layer. The existing Python/JSON audit remains the canonical source for historical numeric rechecks. Do not manually update a table without updating or identifying its evidence source. This task created documentation and reran the audit; it did not implement the proposed pipeline, change the original analysis or execute a new training study.
