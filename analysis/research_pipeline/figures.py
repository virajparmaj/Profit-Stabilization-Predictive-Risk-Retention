"""Static paper figures from validated completed E1/E2 runs; no retraining."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .provenance import ROOT, sha256, write_json
from .reporting import verify_run


def plot_spending(e1: Path, out: Path) -> None:
    data = pd.read_csv(e1 / "policies_aggregate.csv")
    population = json.loads((e1 / "population_spending.json").read_text())
    p = 1 - population["zero_share"]
    data["cv_at_population_zero_mass"] = np.sqrt((data.positive_cv**2 + 1 - p) / p)
    mean = (
        data.groupby(["block", "model", "requested_capacity"])[
            ["mean", "sd", "cv", "positive_cv", "zero_share", "cv_at_population_zero_mass"]
        ]
        .mean()
        .reset_index()
    )
    mean.to_csv(out / "spending_and_zero_mass.csv", index=False)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    for (block, model), g in mean.groupby(["block", "model"]):
        if block not in ["D", "B3", "B4", "B5"]:
            continue
        for ax, key, label in zip(
            axes, ["mean", "sd", "cv"], ["Mean spending ($)", "Spending SD ($)", "CV (SD / mean)"]
        ):
            ax.plot(g.requested_capacity * 100, g[key], marker="o", ms=3, label=f"{block} {model}")
            ax.set(xlabel="Requested population capacity (%)", ylabel=label)
            ax.grid(alpha=0.2)
    axes[0].legend(fontsize=7)
    fig.suptitle("Same-year expenditure at matched capacity · mean over two split seeds")
    fig.tight_layout()
    fig.savefig(out / "expenditure_frontier.png", dpi=180)
    plt.close(fig)


def plot_stability(e2: Path, out: Path) -> None:
    data = pd.read_csv(e2 / "refit_metrics.csv")
    data = data[(data.refit >= 0) & (data.policy == "weighted_capacity")]
    fig, ax = plt.subplots(figsize=(7, 4.8))
    rows = []
    for color, ((block, model), group) in zip(
        plt.cm.tab10.colors, data.groupby(["block", "model"])
    ):
        x, y = group.auc.to_numpy(), group.population_disagreement.to_numpy() * 100
        ax.scatter(x, y, alpha=0.15, s=12, color=color)
        ax.scatter(x.mean(), y.mean(), s=70, edgecolors="black", color=color)
        ax.annotate(
            f"{block} {model}",
            (x.mean(), y.mean()),
            xytext=(7, 5),
            textcoords="offset points",
            fontsize=9,
        )
        rows.append(
            {
                "block": block,
                "model": model,
                "auc_mean": x.mean(),
                "population_disagreement_pct": y.mean(),
                "refits": len(group),
            }
        )
    ax.set(
        xlabel="Reference-set weighted AUROC",
        ylabel="Population membership disagreement (%)",
        title="Classification and identity reproducibility under training refits",
    )
    ax.grid(alpha=0.2)
    fig.text(
        0.01,
        0.01,
        "Each dot is a training refit, not an independent population sample.",
        fontsize=8,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    fig.savefig(out / "membership_vs_accuracy.png", dpi=180)
    plt.close(fig)
    pd.DataFrame(rows).to_csv(out / "membership_vs_accuracy.csv", index=False)


def plot_calibration(e1: Path, out: Path) -> None:
    data = pd.read_parquet(e1 / "scores.parquet")
    rows = []
    # Pool bin summaries descriptively; the scientific AUC remains within-fold.
    data["bin"] = np.minimum((data.score * 10).astype(int), 9)
    for (block, model, bin_id), group in data.groupby(["block", "model", "bin"]):
        rows.append(
            {
                "block": block,
                "model": model,
                "bin": bin_id,
                "predicted": np.average(group.score, weights=group.weight),
                "observed": np.average(group.y, weights=group.weight),
                "prediction_rows": len(group),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(out / "calibration_bins.csv", index=False)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    for (block, model), group in table[table.block == "B3"].groupby(["block", "model"]):
        ax.plot(group.predicted, group.observed, "o-", label=f"{block} {model}")
    ax.plot([0, 1], [0, 1], "k--", alpha=0.4)
    ax.set(
        xlabel="Mean predicted probability",
        ylabel="Weighted observed label fraction",
        title="B3 descriptive calibration across fold-specific targets",
        xlim=(0, 1),
        ylim=(0, 1),
    )
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / "calibration.png", dpi=180)
    plt.close(fig)


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--e1", required=True)
    cli.add_argument("--e2", required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    runs = [ROOT / "analysis/research_runs" / name for name in [args.e1, args.e2]]
    for run in runs:
        verify_run(run)
    args.output.mkdir(parents=True, exist_ok=True)
    plot_spending(runs[0], args.output)
    plot_stability(runs[1], args.output)
    plot_calibration(runs[0], args.output)
    write_json(
        args.output / "figure_sources.json",
        {
            "runs": {run.name: sha256(run / "manifest.json") for run in runs},
            "script_sha256": sha256(Path(__file__)),
            "interpretation": "Exploratory retrospective summaries; point clouds are learning variability, not population CIs",
        },
    )


if __name__ == "__main__":
    main()
