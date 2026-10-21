"""Build aggregate manuscript evidence from verified immutable experiment runs."""

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .aggregation import weighted_metrics
from .config import Config
from .metrics import membership
from .paper_extensions import conditional_reference, spending_sensitivity
from .provenance import ROOT, sha256, write_json
from .reporting import verify_run
from .selection import select_capacity

SOURCES = {
    "2023 E1": "primary-e1-20260930",
    "2023 primary": "primary-e2-20260930",
    "2023 unweighted": "paper-e2-unweighted-20261002",
    "2023 adult core": "paper-e2-core-20261002",
    "2023 legacy missing": "paper-e2-missing-20261002",
    "2021 E1": "paper-replication-2021-e1-20261002",
    "2021 replication": "paper-replication-2021-e2-20261002",
    "2023 cost": "paper-cost-20261001",
    "2023 RF": "paper-rf-20261002",
}


def capacity_sensitivity(source: Path, label: str) -> list[dict]:
    config = Config(**json.loads((source / "config.json").read_text()))
    reference = pd.read_parquet(source / "reference.parquet").set_index("DUPERSID")
    rows = []
    for model in ["logistic", "xgboost"]:
        base = (
            pd.read_parquet(source / f"B3_{model}_base.parquet")
            .set_index("DUPERSID")
            .loc[reference.index]
        )
        draws = pd.read_parquet(source / f"B3_{model}_refit_scores.parquet")
        for q in config.capacities:
            selected = select_capacity(
                base.score, reference.weight, reference.index, q, config.tie_seed
            )
            values = []
            for _, draw in draws.groupby("refit"):
                draw = draw.set_index("DUPERSID").loc[reference.index]
                chosen = select_capacity(
                    draw.score, reference.weight, reference.index, q, config.tie_seed
                )
                values.append(
                    membership(selected, chosen, reference.weight)["population_disagreement"]
                )
            if len(values) != config.refits or not np.isfinite(values).all():
                raise ValueError("Incomplete capacity sensitivity")
            rows.append(
                {
                    "sample": label,
                    "model": model,
                    "capacity": q,
                    "disagreement_mean": np.mean(values),
                    "refits": len(values),
                }
            )
    return rows


def make_tables(sources: dict, output: Path):
    performance, spending, stability, ledger = [], [], [], []
    for label, source in sources.items():
        manifest = verify_run(source)
        flow = json.loads((source / "cohort_flow.json").read_text())
        ledger.append(
            {
                "sample": label,
                "run_id": source.name,
                "experiment": manifest["experiment"],
                "analytic_n": flow["analytic_n"],
                "weight_sum": flow["weight_sum"],
                "manifest_sha256": sha256(source / "manifest.json"),
            }
        )
        if (source / "performance.csv").exists():
            perf = pd.read_csv(source / "performance.csv")
            for (block, model), g in perf.groupby(["block", "model"]):
                performance.append(
                    {
                        "sample": label,
                        "block": block,
                        "model": model,
                        **weighted_metrics(
                            g,
                            ["auc", "brier", "average_precision"],
                            manifest["config"]["folds"] * len(manifest["config"]["seeds"]),
                        ),
                    }
                )
            s = pd.read_csv(source / "policies_aggregate.csv")
            s = s[s.requested_capacity == 0.3]
            for (block, model), g in s.groupby(["block", "model"]):
                spending.append(
                    {
                        "sample": label,
                        "block": block,
                        "model": model,
                        **g[["mean", "sd", "cv", "zero_share", "capacity"]]
                        .mean(skipna=False)
                        .to_dict(),
                    }
                )
        if (source / "refit_metrics.csv").exists():
            data = pd.read_csv(source / "refit_metrics.csv").query(
                "refit >= 0 and policy == 'weighted_capacity'"
            )
            for (block, model), g in data.groupby(["block", "model"]):
                if len(g) != manifest["config"]["refits"]:
                    raise ValueError("Missing refits")
                stability.append(
                    {
                        "sample": label,
                        "block": block,
                        "model": model,
                        "refits": len(g),
                        **g[["auc", "jaccard", "population_disagreement", "mean", "sd", "cv"]]
                        .mean(skipna=False)
                        .to_dict(),
                    }
                )
    cost = sources["2023 cost"]
    perf = pd.read_csv(cost / "cost_performance.csv").rename(columns={"rank_auc": "auc"})
    performance.append(
        {
            "sample": "2023 cost",
            "block": "B3",
            "model": "two_part",
            **weighted_metrics(perf, ["auc", "cost_mae", "cost_rmse"], 10),
        }
    )
    s = pd.read_csv(cost / "cost_policies.csv").query(
        "model == 'two_part' and requested_capacity == .3"
    )
    spending.append(
        {
            "sample": "2023 cost",
            "block": "B3",
            "model": "two_part",
            **s[["mean", "sd", "cv", "zero_share", "capacity"]].mean(skipna=False).to_dict(),
        }
    )
    s = pd.read_csv(cost / "cost_refit_metrics.csv").rename(columns={"rank_auc": "auc"})
    if len(s) != 200:
        raise ValueError("Missing cost refits")
    stability.append(
        {
            "sample": "2023 cost",
            "block": "B3",
            "model": "two_part",
            "refits": len(s),
            **s[["auc", "jaccard", "population_disagreement", "mean", "sd", "cv"]]
            .mean(skipna=False)
            .to_dict(),
        }
    )
    for name, rows in [
        ("performance", performance),
        ("spending", spending),
        ("stability", stability),
        ("run_ledger", ledger),
    ]:
        pd.DataFrame(rows).to_csv(output / f"{name}.csv", index=False)


def figures(output: Path):
    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "svg.fonttype": "none",
        }
    )
    stability = pd.read_csv(output / "stability.csv")
    selected = stability[
        (stability.block == "B3")
        & stability["sample"].isin(["2023 primary", "2021 replication", "2023 cost"])
    ]
    fig, ax = plt.subplots(figsize=(7.5, 3.8))
    labels = [f'{r["sample"]} / {r["model"]}' for _, r in selected.iterrows()]
    ax.barh(
        labels,
        selected.population_disagreement * 100,
        color=["#176b87", "#dc7f32", "#176b87", "#dc7f32", "#4d8a57"],
    )
    ax.invert_yaxis()
    ax.set_xlabel("Mean reference-population disagreement (%)")
    ax.set_title("Membership instability at 30% weighted capacity")
    fig.tight_layout()
    for suffix in ["svg", "png"]:
        fig.savefig(output / f"stability.{suffix}", dpi=220)
    plt.close(fig)
    data = pd.read_csv(output / "capacity.csv")
    fig, axes = plt.subplots(1, 2, figsize=(8, 3.6), sharey=True)
    for ax, (sample, g) in zip(axes, data.groupby("sample")):
        for model, d in g.groupby("model"):
            ax.plot(d.capacity * 100, d.disagreement_mean * 100, "o-", label=model)
        ax.set(title=sample, xlabel="Weighted capacity (%)")
        ax.grid(alpha=0.2)
        ax.legend(frameon=False)
    axes[0].set_ylabel("Mean disagreement (%)")
    fig.tight_layout()
    for suffix in ["svg", "png"]:
        fig.savefig(output / f"capacity.{suffix}", dpi=220)
    plt.close(fig)


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    sources = {k: ROOT / "analysis/research_runs" / v for k, v in SOURCES.items()}
    for source in sources.values():
        verify_run(source)
    args.output.mkdir(parents=True, exist_ok=False)
    make_tables(sources, args.output)
    capacity = []
    for label in ["2023 primary", "2021 replication"]:
        conditional_reference(
            sources[label], args.output / f"{label[:4]}_conditional_reference.json"
        )
        capacity.extend(capacity_sensitivity(sources[label], label))
    pd.DataFrame(capacity).to_csv(args.output / "capacity.csv", index=False)
    spending_sensitivity(sources["2023 E1"], args.output / "tail_sensitivity.csv")
    figures(args.output)
    write_json(
        args.output / "evidence_manifest.json",
        {
            "source_manifests": {k: sha256(v / "manifest.json") for k, v in sources.items()},
            "generator_sha256": {p.name: sha256(p) for p in Path(__file__).parent.glob("*.py")},
            "interpretation": "All supplemental comparisons exploratory; no unconditional population or prospective claim.",
            "outputs": {p.name: sha256(p) for p in args.output.iterdir() if p.is_file()},
        },
    )


if __name__ == "__main__":
    main()
