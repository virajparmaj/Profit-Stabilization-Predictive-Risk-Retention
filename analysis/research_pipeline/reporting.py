"""Regenerate compact research reports from immutable run outputs."""

import json
from pathlib import Path

import pandas as pd

from .provenance import sha256


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


def verify_run(out: Path) -> dict:
    manifest = json.loads((out / "manifest.json").read_text())
    if manifest["status"] != "complete":
        raise ValueError("Only complete runs can produce a completed-results report")
    for name, expected in manifest["outputs"].items():
        path = out / name
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Run output changed or missing: {name}")
    return manifest


def render_report(out: Path) -> None:
    manifest = verify_run(out)
    flow = json.loads((out / "cohort_flow.json").read_text())
    text = [
        f"# Research run {out.name}",
        f"Experiment: {manifest['experiment']}. Population: {manifest['config']['population']}.",
        f"Analytic records: {flow['analytic_n']:,}; weight sum: {flow['weight_sum']:,.2f}.",
        "Exploratory same-year evaluation. No prospective, causal, clinical-need or insurer-profit claim.",
    ]
    if (out / "performance.csv").exists():
        perf = pd.read_csv(out / "performance.csv")
        rows = []
        for (block, model), group in perf.groupby(["block", "model"]):
            total = group.weight_sum.sum()
            rows.append(
                {
                    "block": block,
                    "model": model,
                    **{
                        key: (group[key] * group.weight_sum).sum() / total
                        for key in ["auc", "brier", "average_precision"]
                    },
                }
            )
        text += [
            "## Weighted average of within-fold metrics",
            markdown_table(pd.DataFrame(rows)),
            "Folds/seeds are paired evaluations, not independent samples. AUROC is not pooled across fitted targets.",
        ]
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
        summary = pd.read_csv(out / "refit_summary.csv")
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
                    ]
                ]
            ),
            "Mean/SD across training refits describe learning sensitivity, not confidence intervals from independent patients.",
        ]
    text += [
        "## Provenance",
        f"Input SHA-256: `{manifest['input_sha256']}`.",
        f"Protocol/config SHA-256: `{manifest['config_sha256']}`.",
        "Full configuration, source hashes, software versions, warnings and output hashes are in manifest.json and diagnostics files.",
    ]
    (out / "REPORT.md").write_text("\n\n".join(text) + "\n")
