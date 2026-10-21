"""Regenerate compact research reports from immutable run outputs."""

import json
from pathlib import Path

import pandas as pd

from .aggregation import weighted_metrics
from .provenance import sha256, write_json


def markdown_table(frame: pd.DataFrame) -> str:
    def cell(value):
        if pd.isna(value):
            return "undefined"
        return f"{value:.5g}" if isinstance(value, float) else str(value)

    lines = [
        "| " + " | ".join(frame.columns) + " |",
        "| " + " | ".join(["---"] * len(frame.columns)) + " |",
    ]
    lines += [
        "| " + " | ".join(cell(v) for v in row) + " |"
        for row in frame.itertuples(index=False, name=None)
    ]
    return "\n".join(lines)


def required_outputs(manifest: dict) -> set[str]:
    names = {
        "config.json",
        "cohort_flow.json",
        "dictionary.json",
        "survey_mean.json",
        "cohort.parquet",
        "design.csv",
        "REPORT.md",
    }
    if manifest["experiment"] in {"E1", "E4"}:
        names |= {
            "performance.csv",
            "scores.parquet",
            "splits.csv",
            "policies_by_fold.csv",
            "policies_aggregate.csv",
            "fit_diagnostics.json",
            "population_spending.json",
            "fit_log.jsonl",
        }
    if manifest["experiment"] == "cost_baseline":
        names |= {
            "cost_scores.parquet",
            "cost_performance.csv",
            "cost_policies.csv",
            "reference.parquet",
            "splits.csv",
            "endpoint.json",
            "two_part_base.parquet",
            "cost_refit_metrics.csv",
            "two_part_refit_scores.parquet",
            "failures.json",
            "fit_log.jsonl",
        }
    if manifest["experiment"] == "E2":
        names |= {
            "refit_metrics.csv",
            "refit_summary.csv",
            "endpoint.json",
            "reference.parquet",
            "splits.csv",
            "failures.json",
            "selection_frequencies.parquet",
            "fit_log.jsonl",
        }
        from .refits import ANCHORS

        for block, model in ANCHORS:
            names |= {
                f"{block}_{model}_{suffix}"
                for suffix in ["base.parquet", "refit_scores.parquet", "diagnostics.json"]
            }
    return names


def verify_run(out: Path) -> dict:
    manifest = json.loads((out / "manifest.json").read_text())
    if manifest["status"] != "complete":
        raise ValueError("Only complete runs can produce a completed-results report")
    version = manifest.get("manifest_version", 1)
    if version not in (1, 2):
        raise ValueError("Unsupported manifest version")
    if version == 2 and not required_outputs(manifest) <= set(manifest["outputs"]):
        raise ValueError("Manifest missing required scientific outputs")
    for name, expected in manifest["outputs"].items():
        path = out / name
        if not path.resolve().is_relative_to(out.resolve()):
            raise ValueError("Output path escapes run directory")
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Run output changed or missing: {name}")
    if "config_sha256" in manifest:
        if (
            sha256(out / "config.json") != manifest["config_sha256"]
            or json.loads((out / "config.json").read_text()) != manifest["config"]
        ):
            raise ValueError("Run configuration changed")
    return manifest


def report_text(out: Path, manifest: dict, policies=None, refit_summary=None) -> str:
    flow = json.loads((out / "cohort_flow.json").read_text())
    text = [
        f"# Research run {out.name}",
        f"Experiment: {manifest['experiment']}. Population: {manifest['config']['population']}.",
        f"Analytic records: {flow['analytic_n']:,}; weight sum: {flow['weight_sum']:,.2f}.",
        "Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.",
    ]
    if manifest.get("pilot", False):
        text += ["**PILOT / feasibility only: not final research evidence.**"]
    if "data_year" in manifest:
        text += [f"Data year: {manifest['data_year']}. {manifest.get('scope', '')}"]
    if manifest.get("manifest_version", 1) == 1:
        text += [
            "Legacy manifest: scientific files are hash-verified; the original REPORT.md was not covered by the run manifest. This report is newly derived from verified scientific files."
        ]
    if (out / "performance.csv").exists():
        perf = pd.read_csv(out / "performance.csv")
        rows = []
        for (block, model), group in perf.groupby(["block", "model"]):
            rows.append(
                {
                    "block": block,
                    "model": model,
                    **weighted_metrics(
                        group,
                        ["auc", "brier", "average_precision"],
                        manifest["config"]["folds"] * len(manifest["config"]["seeds"]),
                    ),
                }
            )
        text += [
            "## Weighted average of within-fold metrics",
            markdown_table(pd.DataFrame(rows)),
            "Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.",
        ]
        if policies is None:
            policies = pd.read_csv(out / "policies_aggregate.csv")
        primary = policies[policies.requested_capacity == manifest["config"]["capacity"]]
        text += [
            "## Primary-capacity expenditure summaries",
            markdown_table(
                primary[["seed", "block", "model", "capacity", "mean", "sd", "cv", "zero_share"]]
            ),
        ]
    if (out / "primary_contrast.json").exists():
        contrast = json.loads((out / "primary_contrast.json").read_text())
        rows = [
            {"metric": k, **{field: v.get(field) for field in ["estimate", "se", "low", "high"]}}
            for k, v in contrast.items()
            if isinstance(v, dict)
        ]
        text += [
            "## B3 logistic minus XGBoost",
            markdown_table(pd.DataFrame(rows)),
            "Intervals condition on fitted predictions and grouped folds; learning variation is separate.",
        ]
    if (out / "refit_summary.csv").exists():
        summary = pd.read_csv(out / "refit_summary.csv") if refit_summary is None else refit_summary
        text += [
            "## Refit sensitivity",
            markdown_table(
                summary[
                    [
                        "block",
                        "model",
                        "policy",
                        "auc_mean",
                        "jaccard_mean",
                        "population_disagreement_mean",
                        "capacity_mean",
                        *[c for c in summary if c.endswith(("_valid", "_expected"))],
                    ]
                ]
            ),
            "Mean/SD across training refits describe learning sensitivity, not confidence intervals from independent patients.",
        ]
    if manifest["experiment"] == "cost_baseline":
        perf = pd.read_csv(out / "cost_performance.csv")
        perf = perf.rename(columns={"rank_auc": "auc"})
        text += [
            "## Direct-expenditure comparator",
            markdown_table(
                pd.DataFrame(
                    [
                        weighted_metrics(
                            perf,
                            ["auc", "cost_mae", "cost_rmse"],
                            manifest["config"]["folds"] * len(manifest["config"]["seeds"]),
                        )
                    ]
                )
            ),
            "AUROC evaluates ranking only: reciprocal predicted cost is not a calibrated label probability. RMSE is the weight-mass average of fold RMSEs.",
        ]
        metrics = pd.read_csv(out / "cost_refit_metrics.csv")
        from .aggregation import refit_statistics

        rows = [
            {"metric": key, **refit_statistics(metrics[key], manifest["config"]["refits"])}
            for key in ["rank_auc", "jaccard", "population_disagreement", "mean", "sd", "cv"]
        ]
        text += ["## Direct-cost refit sensitivity", markdown_table(pd.DataFrame(rows))]
    if manifest["experiment"] in {"E1", "E4"}:
        text += [
            "Random comparator: one deterministic seeded ranking with the same within-fold capacity rule; not an average over random policies."
        ]
    text += [
        "## Provenance",
        f"Input SHA-256: `{manifest['input_sha256']}`.",
        f"Protocol/config SHA-256: `{manifest['config_sha256']}`.",
        "Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.",
    ]
    return "\n\n".join(text) + "\n"


def render_report(out: Path, output: Path) -> None:
    """Derive a report without mutating a completed run, including legacy runs."""
    manifest = verify_run(out)
    # Never consume an unhashed scientific file that appeared after finalization.
    allowed = set(manifest["outputs"])
    required = {"config.json", "cohort_flow.json"}
    if manifest.get("manifest_version", 1) == 2 or "data_year" in manifest:
        required.add("dictionary.json")
    if manifest["experiment"] in {"E1", "E4"}:
        required |= {"performance.csv", "scores.parquet", "policies_aggregate.csv"}
    if manifest["experiment"] == "cost_baseline":
        required |= {"cost_performance.csv", "cost_refit_metrics.csv"}
    if manifest["experiment"] == "E2":
        required |= {"refit_metrics.csv", "refit_summary.csv"}
    if not required <= allowed:
        raise ValueError("Derived reports require hashed scientific inputs")
    for name in ["performance.csv", "primary_contrast.json", "refit_summary.csv"]:
        if (out / name).exists() and name not in allowed:
            raise ValueError(f"Unhashed scientific input: {name}")
    if output.resolve().is_relative_to(out.resolve()):
        raise ValueError("Derived output must be outside the immutable source run")
    output.mkdir(parents=True, exist_ok=False)
    policies, summary = None, None
    from .config import Config

    config = Config(**manifest["config"])
    if "scores.parquet" in allowed:
        from .experiments import aggregate_policies

        policies = aggregate_policies(pd.read_parquet(out / "scores.parquet"), config)
        policies.to_csv(output / "policies_aggregate.csv", index=False)
    if "refit_metrics.csv" in allowed:
        from .refits import refit_summary_table

        summary = refit_summary_table(pd.read_csv(out / "refit_metrics.csv"), config.refits)
        summary.to_csv(output / "refit_summary.csv", index=False)
    from .dictionary import dictionary

    # Preserve audited year-specific aliases and unavailable-variable metadata.
    # Only legacy dictionaries need regeneration from the corrected definitions.
    entries = (
        json.loads((out / "dictionary.json").read_text())
        if "dictionary.json" in required
        else dictionary(config.population, config.burden, config.missingness)
    )
    write_json(output / "dictionary.json", entries)
    (output / "REPORT.md").write_text(report_text(out, manifest, policies, summary))
    write_json(
        output / "derivation.json",
        {
            "parent_manifest_sha256": sha256(out / "manifest.json"),
            "parent_run": out.name,
            "legacy_report_integrity": (
                "not verified; original report not consumed"
                if manifest.get("manifest_version", 1) == 1
                else "verified"
            ),
            "generator_sha256": {f.name: sha256(f) for f in Path(__file__).parent.glob("*.py")},
            "outputs": {f.name: sha256(f) for f in output.iterdir() if f.is_file()},
        },
    )
