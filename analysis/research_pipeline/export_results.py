"""Export only aggregate research evidence, with verified source-run manifests."""

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

from .aggregation import weighted_metrics
from .provenance import ROOT, sha256, write_json
from .reporting import render_report, verify_run

PUBLIC_FILES = [
    "manifest.json",
    "config.json",
    "cohort_flow.json",
    "dictionary.json",
    "survey_mean.json",
    "performance.csv",
    "policies_by_fold.csv",
    "policies_aggregate.csv",
    "population_spending.json",
    "primary_contrast.json",
    "refit_summary.csv",
    "endpoint.json",
    "failures.json",
]


def export_run(source: Path, output: Path) -> dict:
    manifest = verify_run(source)
    target = output / source.name
    target.mkdir(parents=True, exist_ok=False)
    for name in PUBLIC_FILES:
        path = source / name
        if path.exists():
            if name != "manifest.json" and name not in manifest["outputs"]:
                raise ValueError(f"Unhashed export input: {name}")
            shutil.copy2(path, target / name)
    render_report(source, target / "derived")
    return {
        "run_id": source.name,
        "manifest_sha256": sha256(source / "manifest.json"),
        "experiment": manifest["experiment"],
        "pilot": manifest.get("pilot", False),
        "elapsed_seconds": manifest["elapsed_seconds"],
    }


def paired_learning_summary(source: Path, output: Path) -> None:
    frame = pd.read_csv(source / "refit_metrics.csv")
    frame = frame[(frame.refit >= 0) & (frame.policy == "weighted_capacity")]
    a = frame[(frame.block == "B3") & (frame.model == "logistic")].set_index("refit")
    b = frame[(frame.block == "B3") & (frame.model == "xgboost")].set_index("refit")
    if not a.index.equals(b.index):
        raise ValueError("Paired refits require matching successful replicate IDs")
    rows = []
    for metric in [
        "auc",
        "jaccard",
        "population_disagreement",
        "baseline_member_loss",
        "probability_mad",
        "mean",
        "sd",
        "cv",
    ]:
        difference = a[metric] - b[metric]
        expected = json.loads((source / "config.json").read_text())["refits"]
        valid = int(np.isfinite(difference).sum())
        complete = valid == expected and len(difference) == expected
        if not complete:
            difference = difference * np.nan
        rows.append(
            {
                "metric": metric,
                "mean_logistic_minus_xgboost": difference.mean(),
                "refit_sd": difference.std(),
                "refit_q025": difference.quantile(0.025),
                "refit_q975": difference.quantile(0.975),
                "mean_monte_carlo_se": difference.std() / np.sqrt(len(difference)),
                "paired_refits": len(difference),
                "valid_pairs": valid,
                "expected_pairs": expected,
            }
        )
    pd.DataFrame(rows).to_csv(output / "paired_learning_sensitivity.csv", index=False)


def robustness_summary(sources: list[Path], output: Path) -> None:
    rows = []
    for source in sources:
        config = json.loads((source / "config.json").read_text())
        perf = pd.read_csv(source / "performance.csv")
        policies = pd.read_csv(source / "policies_aggregate.csv")
        for (block, model), group in perf.groupby(["block", "model"]):
            chosen = policies[
                (policies.block == block)
                & (policies.model == model)
                & (policies.requested_capacity == config["capacity"])
            ].iloc[0]
            rows.append(
                {
                    "run_id": source.name,
                    "population": config["population"],
                    "block": block,
                    "model": model,
                    **weighted_metrics(
                        group, ["auc", "brier"], config["folds"] * len(config["seeds"])
                    ),
                    **{k: chosen[k] for k in ["capacity", "mean", "sd", "cv", "zero_share"]},
                }
            )
    pd.DataFrame(rows).to_csv(output / "robustness_comparison.csv", index=False)


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--e1", required=True)
    cli.add_argument("--e2", required=True)
    cli.add_argument("--robustness-prefix", required=True)
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    base = ROOT / "analysis/research_runs"
    primary = [base / args.e1, base / args.e2]
    sensitivities = sorted(p for p in base.glob(args.robustness_prefix + "-*") if p.is_dir())
    if len(sensitivities) != 7:
        raise ValueError("Expected all seven prespecified E4 variants")
    args.output.mkdir(parents=True, exist_ok=False)
    runs = [export_run(source, args.output) for source in primary + sensitivities]
    paired_learning_summary(primary[1], args.output)
    robustness_summary(sensitivities, args.output)
    write_json(
        args.output / "export_manifest.json",
        {
            "runs": runs,
            "export_script_sha256": sha256(Path(__file__)),
            "exclusions": "Person IDs, individual scores, reference records and split assignments stay local",
            "paired_learning_interpretation": "Refit quantiles and Monte Carlo SE; not population confidence intervals",
            "exported_files": {
                str(path.relative_to(args.output)): sha256(path)
                for path in sorted(args.output.rglob("*"))
                if path.is_file() and path.name != "export_manifest.json"
            },
        },
    )


if __name__ == "__main__":
    main()
