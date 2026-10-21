"""Reproducible direct-expenditure and conditional stability supplements.

All experiment outputs remain local. Direct expenditure rankings are not
probabilities of the low-spending classification label.
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import GammaRegressor
from sklearn.metrics import roc_auc_score

from .cohort import build_cohort
from .config import Config
from .diagnostics import record_fit
from .dictionary import dictionary
from .experiments import aggregate_policies
from .metrics import membership, selected_spending
from .models import fit_model, make_pipeline, positive_probability
from .provenance import ROOT, finish_run, sha256, start_run, write_json
from .reporting import verify_run
from .selection import select_capacity, weighted_quantile
from .splits import outer_folds, reference_split
from .survey import multipliers, paired_interval, replicate_design, resample_training, taylor_mean
from .targets import cutoff, labels


class TwoPartCost:
    """Logistic occurrence × Gamma log-link conditional positive mean."""

    def fit(self, training, config, seed):
        positive = training.TOTEXP23.to_numpy() > 0
        if not positive.any():
            raise ValueError("No positive training expenditures")
        self.occurrence = (
            None
            if positive.all()
            else fit_model(training, positive.astype(int), "B3", "logistic", config, seed)
        )
        subset = training.loc[positive]
        w = subset.weight.to_numpy() if config.weighted_training else np.ones(len(subset))
        self.scale = float(np.average(subset.TOTEXP23, weights=w))
        self.amount = make_pipeline(subset, "B3", "logistic", config, seed)
        self.amount.set_params(model=GammaRegressor(alpha=1.0, max_iter=2000, tol=1e-7))
        self.amount.fit(subset, subset.TOTEXP23 / self.scale, model__sample_weight=w / w.mean())
        return self

    def predict(self, frame):
        occurrence = (
            np.ones(len(frame))
            if self.occurrence is None
            else positive_probability(self.occurrence, frame)
        )
        expected = occurrence * self.amount.predict(frame) * self.scale
        if not np.isfinite(expected).all() or (expected < 0).any():
            raise ValueError("Invalid expected expenditure")
        return expected


def ranking(cost):
    return 1 / (1 + np.asarray(cost, float))


def run_cost(frame, design, config, out):
    records, perf = [], []
    for seed in config.seeds:
        for fold, tr, te in outer_folds(frame, config.folds, seed):
            train, test = frame.iloc[tr], frame.iloc[te].copy()
            endpoint = cutoff(train, config.label)
            with record_fit(
                out, experiment="cost_e1", seed=seed, fold=fold, model="two_part", block="B3"
            ):
                model = TwoPartCost().fit(train, config, seed)
                cost = model.predict(test)
            test["y"], test["score"] = labels(test, endpoint), ranking(cost)
            test["predicted_cost"] = cost
            cols = [
                "DUPERSID",
                "DUID",
                "VARSTR",
                "VARPSU",
                "weight",
                "TOTEXP23",
                "INSCOV23",
                "y",
                "score",
                "predicted_cost",
            ]
            records.append(test[cols].assign(seed=seed, fold=fold, model="two_part", block="B3"))
            perf.append(
                {
                    "seed": seed,
                    "fold": fold,
                    "weight_sum": test.weight.sum(),
                    "rank_auc": roc_auc_score(test.y, test.score, sample_weight=test.weight),
                    "cost_mae": np.average(np.abs(test.TOTEXP23 - cost), weights=test.weight),
                    "cost_rmse": np.sqrt(
                        np.average((test.TOTEXP23 - cost) ** 2, weights=test.weight)
                    ),
                }
            )
    scores = pd.concat(records, ignore_index=True)
    scores.to_parquet(out / "cost_scores.parquet", index=False)
    pd.DataFrame(perf).to_csv(out / "cost_performance.csv", index=False)
    aggregate_policies(scores, config).to_csv(out / "cost_policies.csv", index=False)
    tr, ca, re = reference_split(frame, config.seeds[0])
    train, reference = frame.iloc[tr], frame.iloc[re].reset_index(drop=True)
    reference.to_parquet(out / "reference.parquet", index=False)
    pd.concat(
        [
            frame.iloc[ix][["DUPERSID", "DUID"]].assign(partition=name)
            for ix, name in [(tr, "training"), (ca, "calibration"), (re, "reference")]
        ]
    ).to_csv(out / "splits.csv", index=False)
    threshold = cutoff(train, config.label)
    write_json(out / "endpoint.json", {"threshold": threshold, "fixed_across_refits": True})
    with record_fit(
        out, experiment="cost_e2", refit=-1, seed=config.seeds[0], model="two_part", block="B3"
    ):
        original = ranking(TwoPartCost().fit(train, config, config.seeds[0]).predict(reference))
    base = select_capacity(
        original, reference.weight, reference.DUPERSID, config.capacity, config.tie_seed
    )
    pd.DataFrame({"DUPERSID": reference.DUPERSID, "score": original, "selected": base}).to_parquet(
        out / "two_part_base.parquet", index=False
    )
    rows, predictions, failures = [], [], []
    for b in range(config.refits):
        try:
            with record_fit(
                out,
                experiment="cost_e2",
                refit=b,
                seed=config.seeds[0],
                resample_seed=config.refit_seed + b,
                model="two_part",
                block="B3",
            ):
                sampled = resample_training(train, design, config.refit_seed + b)
                p = ranking(TwoPartCost().fit(sampled, config, config.seeds[0]).predict(reference))
                chosen = select_capacity(
                    p, reference.weight, reference.DUPERSID, config.capacity, config.tie_seed
                )
                rows.append(
                    {
                        "refit": b,
                        "rank_auc": roc_auc_score(
                            labels(reference, threshold), p, sample_weight=reference.weight
                        ),
                        **membership(base, chosen, reference.weight),
                        **selected_spending(reference, chosen, threshold=config.tail_threshold),
                    }
                )
                predictions.append(
                    pd.DataFrame(
                        {"DUPERSID": reference.DUPERSID, "score": p, "selected": chosen, "refit": b}
                    )
                )
        except Exception as error:
            failures.append({"refit": b, "error": str(error)})
        if (b + 1) % 50 == 0:
            print(f"Cost baseline {b+1}/{config.refits}", flush=True)
    pd.DataFrame(rows).to_csv(out / "cost_refit_metrics.csv", index=False)
    if predictions:
        pd.concat(predictions).to_parquet(out / "two_part_refit_scores.parquet", index=False)
    write_json(out / "failures.json", failures)
    if failures:
        raise RuntimeError("Prespecified cost refits failed; not replaced")


def conditional_reference(source: Path, output: Path, replicates: int = 1000):
    if output.exists():
        raise FileExistsError(output)
    manifest = verify_run(source)
    reference = pd.read_parquet(source / "reference.parquet").set_index("DUPERSID")
    design = pd.read_csv(source / "design.csv")
    means = {}
    for model in ["logistic", "xgboost"]:
        base = pd.read_parquet(source / f"B3_{model}_base.parquet").set_index("DUPERSID")
        draws = pd.read_parquet(source / f"B3_{model}_refit_scores.parquet")
        wide = draws.pivot(index="DUPERSID", columns="refit", values="selected").reindex(
            reference.index
        )
        if wide.isna().any().any() or wide.shape[1] != manifest["config"]["refits"]:
            raise ValueError("Incomplete refit ensemble")
        means[model] = (
            wide.to_numpy(bool) != base.loc[reference.index, "selected"].to_numpy(bool)[:, None]
        ).mean(axis=1)
    reference["contrast"] = means["logistic"] - means["xgboost"]
    w = reference.weight.to_numpy()
    factors = multipliers(reference.reset_index(), replicate_design(design, replicates, 81273))
    point = np.average(reference.contrast, weights=w)
    estimates = (reference.contrast.to_numpy()[:, None] * w[:, None] * factors).sum(axis=0) / (
        w[:, None] * factors
    ).sum(axis=0)
    result = paired_interval(float(point), estimates)
    result.update(
        taylor=taylor_mean(reference.reset_index(), design, "contrast"),
        interpretation="Conditional reference-design sensitivity for fixed fitted ensemble and fixed selected memberships. Quotas not reapplied; not joint uncertainty.",
        source_manifest_sha256=sha256(source / "manifest.json"),
    )
    write_json(output, result)


def spending_sensitivity(source: Path, output: Path):
    if output.exists():
        raise FileExistsError(output)
    verify_run(source)
    scores = pd.read_parquet(source / "scores.parquet")
    config = Config(**json.loads((source / "config.json").read_text()))
    rows = []
    for (seed, model), g in scores[scores.block == "B3"].groupby(["seed", "model"]):
        g = g.reset_index(drop=True)
        chosen = np.zeros(len(g), bool)
        for _, ix in g.groupby("fold").groups.items():
            sub = g.loc[ix]
            chosen[ix] = select_capacity(
                sub.score, sub.weight, sub.DUPERSID, config.capacity, config.tie_seed
            )
        cap = weighted_quantile(g.TOTEXP23, g.weight, 0.99)
        for mode in ["original", "winsor_p99"]:
            changed = g.copy()
            if mode == "winsor_p99":
                changed["TOTEXP23"] = np.minimum(changed.TOTEXP23, cap)
            for tail in [10000, 20000, 50000]:
                rows.append(
                    {
                        "seed": seed,
                        "model": model,
                        "mode": mode,
                        "tail": tail,
                        "winsor_cutoff": cap,
                        **selected_spending(changed, chosen, threshold=tail),
                    }
                )
    pd.DataFrame(rows).to_csv(output, index=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    config = Config(blocks=["B3"])
    out, manifest = start_run(args.run_id, config, "cost_baseline")
    start = time.perf_counter()
    try:
        frame, design, flow = build_cohort(ROOT / config.raw, config)
        frame.to_parquet(out / "cohort.parquet", index=False)
        design.to_csv(out / "design.csv", index=False)
        write_json(out / "cohort_flow.json", flow)
        write_json(
            out / "dictionary.json",
            dictionary(config.population, config.burden, config.missingness),
        )
        write_json(out / "survey_mean.json", taylor_mean(frame, design, "TOTEXP23"))
        run_cost(frame, design, config, out)
        finish_run(out, manifest, "complete", time.perf_counter() - start)
    except BaseException as error:
        finish_run(
            out,
            manifest,
            "interrupted" if isinstance(error, (KeyboardInterrupt, SystemExit)) else "failed",
            time.perf_counter() - start,
            str(error),
        )
        raise
    print(out, flush=True)


if __name__ == "__main__":
    main()
