"""Compare targeted reruns with historical evidence and export to a fresh directory."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from .config import Config
from .experiments import aggregate_policies
from .export_results import export_run, paired_learning_summary, robustness_summary
from .figures import plot_calibration, plot_spending, plot_stability
from .provenance import ROOT, sha256, write_json
from .reporting import verify_run
from .selection import select_capacity


def identical(left: pd.DataFrame, right: pd.DataFrame, keys: list[str]) -> None:
    left = left.sort_values(keys).reset_index(drop=True)
    right = right.sort_values(keys).reset_index(drop=True)
    pd.testing.assert_frame_equal(left, right, check_exact=True)


def compare_e1(original: Path, rerun: Path) -> dict:
    config = Config(**json.loads((rerun / "config.json").read_text()))
    old = pd.read_parquet(original / "scores.parquet")
    old = old[
        old.block.isin(config.blocks) & old.model.isin(config.models) & old.seed.isin(config.seeds)
    ]
    new = pd.read_parquet(rerun / "scores.parquet")
    keys = ["seed", "fold", "block", "model", "DUPERSID"]
    identical(old.drop(columns="run_id"), new.drop(columns="run_id"), keys)
    memberships = 0
    for group_key, group in old.groupby(keys[:-1]):
        other = new
        for key, value in zip(keys[:-1], group_key):
            other = other[other[key] == value]
        group = group.sort_values("DUPERSID")
        other = other.sort_values("DUPERSID")
        for capacity in config.capacities:
            a = select_capacity(
                group.score, group.weight, group.DUPERSID, capacity, config.tie_seed
            )
            b = select_capacity(
                other.score, other.weight, other.DUPERSID, capacity, config.tie_seed
            )
            np.testing.assert_array_equal(a, b)
            memberships += len(a)
    old_performance = pd.read_csv(original / "performance.csv")
    old_performance = old_performance[
        old_performance.block.isin(config.blocks)
        & old_performance.model.isin(config.models)
        & old_performance.seed.isin(config.seeds)
    ]
    new_performance = pd.read_csv(rerun / "performance.csv")
    identical(
        old_performance.drop(columns="run_id"), new_performance.drop(columns="run_id"), keys[:-1]
    )
    for name in ["cohort.parquet", "splits.csv"]:
        if name == "cohort.parquet":
            identical(pd.read_parquet(original / name), pd.read_parquet(rerun / name), ["DUPERSID"])
        else:
            old_split = pd.read_csv(original / name)
            identical(
                old_split[old_split.seed.isin(config.seeds)],
                pd.read_csv(rerun / name),
                ["seed", "DUPERSID"],
            )
    return {
        "prediction_rows_identical": len(new),
        "membership_decisions_identical": memberships,
        "performance_rows_identical": len(new_performance),
        "cohort_and_splits_identical": True,
    }


def compare_e2(original: Path, rerun: Path) -> dict:
    comparisons = {}
    for new_file in sorted(rerun.glob("*_refit_scores.parquet")):
        new = pd.read_parquet(new_file)
        old = pd.read_parquet(original / new_file.name)
        old = old[old.refit.isin(new.refit.unique())]
        identical(old, new, ["refit", "DUPERSID"])
        comparisons[new_file.name] = len(new)
    for new_file in sorted(rerun.glob("*_base.parquet")):
        identical(
            pd.read_parquet(original / new_file.name), pd.read_parquet(new_file), ["DUPERSID"]
        )
    assert json.loads((original / "endpoint.json").read_text()) == json.loads(
        (rerun / "endpoint.json").read_text()
    )
    identical(
        pd.read_parquet(original / "reference.parquet"),
        pd.read_parquet(rerun / "reference.parquet"),
        ["DUPERSID"],
    )
    old = pd.read_csv(original / "refit_metrics.csv")
    new = pd.read_csv(rerun / "refit_metrics.csv")
    identical(old[old.refit.isin(new.refit.unique())], new, ["block", "model", "policy", "refit"])
    return {
        "prediction_rows_identical_by_anchor": comparisons,
        "base_predictions_identical": True,
        "endpoint_and_reference_identical": True,
        "metric_rows_identical": len(new),
    }


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    for name in ["original-e1", "original-e2", "original-pilot", "e1", "e2", "robustness-prefix"]:
        cli.add_argument(f"--{name}", required=True)
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    base = ROOT / "analysis/research_runs"
    old_e1, old_e2, old_pilot, new_e1, new_e2 = [
        base / name
        for name in [args.original_e1, args.original_e2, args.original_pilot, args.e1, args.e2]
    ]
    sensitivities = sorted(p for p in base.glob(args.robustness_prefix + "-*") if p.is_dir())
    if len(sensitivities) != 7:
        raise ValueError("Expected seven historical sensitivities")
    sources = [old_e1, old_e2, old_pilot, new_e1, new_e2] + sensitivities
    before = {
        str(path): sha256(path) for run in sources for path in run.rglob("*") if path.is_file()
    }
    for source in sources:
        verify_run(source)
    comparison = {
        "e1": compare_e1(old_e1, new_e1),
        "e2_vs_full": compare_e2(old_e2, new_e2),
        "e2_vs_pilot": compare_e2(old_pilot, new_e2),
    }
    # Existing finite policy summaries must remain unchanged; random is the only addition.
    original_config = Config(**json.loads((old_e1 / "config.json").read_text()))
    recomputed = aggregate_policies(pd.read_parquet(old_e1 / "scores.parquet"), original_config)
    old_policies = pd.read_csv(old_e1 / "policies_aggregate.csv")
    columns = ["seed", "block", "model", "requested_capacity"]
    pd.testing.assert_frame_equal(
        old_policies.sort_values(columns).reset_index(drop=True),
        recomputed[recomputed.model != "random"].sort_values(columns).reset_index(drop=True),
        rtol=1e-12,
        atol=1e-12,
    )
    comparison["historical_policy_rows_unchanged"] = len(old_policies)
    comparison["new_random_policy_rows"] = int((recomputed.model == "random").sum())
    comparison["run_diagnostics"] = {}
    for run in [new_e1, new_e2]:
        records = [json.loads(line) for line in (run / "fit_log.jsonl").read_text().splitlines()]
        assert all(record["status"] == "complete" for record in records)
        comparison["run_diagnostics"][run.name] = {
            "fits_including_bases": len(records),
            "warnings": sum(len(r["warnings"]) for r in records),
            "failed": 0,
            "elapsed_seconds": json.loads((run / "manifest.json").read_text())["elapsed_seconds"],
        }
    args.output.mkdir(parents=True, exist_ok=False)
    exports = [export_run(source, args.output) for source in sources]
    paired_learning_summary(old_e2, args.output)
    robustness_summary(sensitivities, args.output)
    figures = args.output / "figures"
    figures.mkdir()
    plot_spending(old_e1, figures)
    plot_stability(old_e2, figures)
    plot_calibration(old_e1, figures)
    comparison["source_files_unchanged"] = all(
        sha256(Path(path)) == digest for path, digest in before.items()
    )
    assert comparison["source_files_unchanged"]
    comparison["source_files_checked"] = len(before)
    write_json(args.output / "verification.json", comparison)
    write_json(
        args.output / "export_manifest.json",
        {
            "runs": exports,
            "generator_sha256": {f.name: sha256(f) for f in Path(__file__).parent.glob("*.py")},
            "figure_sources": {run.name: sha256(run / "manifest.json") for run in [old_e1, old_e2]},
            "scope": "Verified scientific sources; legacy REPORT.md not copied. Original aggregate files retained beside new derived tables and reports. Person-level files excluded.",
            "exported_files": {
                str(f.relative_to(args.output)): sha256(f)
                for f in sorted(args.output.rglob("*"))
                if f.is_file()
            },
        },
    )
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()
