"""Paired E1 classification and E3 expenditure comparisons on held-out people."""

import time
import warnings

import numpy as np
import pandas as pd

from .metrics import classification, selected_spending, spending
from .models import fit_model, positive_probability
from .provenance import write_json
from .selection import select_capacity, tie_keys
from .splits import outer_folds
from .targets import cutoff, labels


def policy_rows(test, scores, config, metadata: dict) -> list[dict]:
    rows = []
    for capacity in config.capacities:
        selected = select_capacity(scores, test.weight, test.DUPERSID, capacity, config.tie_seed)
        summary = selected_spending(test, selected, threshold=config.tail_threshold)
        summary["label_precision"] = (
            float(np.average(test.y[selected], weights=test.weight[selected]))
            if selected.any()
            else None
        )
        summary["uninsured_share"] = (
            float(np.average(test.INSCOV23[selected] == 3, weights=test.weight[selected]))
            if selected.any()
            else None
        )
        rows.append({**metadata, "requested_capacity": capacity, **summary})
    return rows


def evaluate_fit(train, test, threshold, block, model, config, seed):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        start = time.perf_counter()
        pipe = fit_model(train, labels(train, threshold), block, model, config, seed)
        p = positive_probability(pipe, test)
    return p, time.perf_counter() - start, [str(w.message) for w in caught]


def run_e1(frame, design, config, out) -> None:
    scores, performance, policies, assignments, diagnostics = [], [], [], [], []
    for seed in config.seeds:
        for fold, train_ix, test_ix in outer_folds(frame, config.folds, seed):
            train, test = frame.iloc[train_ix], frame.iloc[test_ix].copy()
            threshold = cutoff(train, config.label)
            test["y"] = labels(test, threshold)
            assignments.append(test[["DUPERSID", "DUID"]].assign(seed=seed, fold=fold))
            for block in config.blocks:
                for model in config.models:
                    p, elapsed, messages = evaluate_fit(
                        train, test, threshold, block, model, config, seed
                    )
                    meta = {
                        "seed": seed,
                        "fold": fold,
                        "block": block,
                        "model": model,
                        "cutoff": threshold,
                        "run_id": out.name,
                    }
                    performance.append(
                        {
                            **meta,
                            "n": len(test),
                            "weight_sum": test.weight.sum(),
                            **classification(test.y, p, test.weight),
                        }
                    )
                    columns = [
                        "DUPERSID",
                        "DUID",
                        "VARSTR",
                        "VARPSU",
                        "weight",
                        "TOTEXP23",
                        "INSCOV23",
                        "y",
                    ]
                    scores.append(test[columns].assign(score=p, **meta))
                    policies.extend(policy_rows(test, p, config, meta))
                    diagnostics.append({**meta, "fit_seconds": elapsed, "warnings": messages})
                    print(f"E1 seed={seed} fold={fold} {block}/{model}: {elapsed:.2f}s", flush=True)
            random_scores = np.argsort(np.argsort(tie_keys(test.DUPERSID, config.tie_seed))) / len(
                test
            )
            policies.extend(
                policy_rows(
                    test,
                    random_scores,
                    config,
                    {
                        "seed": seed,
                        "fold": fold,
                        "block": "random",
                        "model": "random",
                        "cutoff": threshold,
                        "run_id": out.name,
                    },
                )
            )
    scored = pd.concat(scores, ignore_index=True)
    if scored.duplicated(["seed", "block", "model", "DUPERSID"]).any():
        raise AssertionError("Duplicate held-out prediction")
    expected = len(frame) * len(config.seeds) * len(config.blocks) * len(config.models)
    if len(scored) != expected:
        raise AssertionError("Missing held-out predictions")
    scored.to_parquet(out / "scores.parquet", index=False)
    pd.concat(assignments).to_csv(out / "splits.csv", index=False)
    pd.DataFrame(performance).to_csv(out / "performance.csv", index=False)
    pd.DataFrame(policies).to_csv(out / "policies_by_fold.csv", index=False)
    write_json(out / "fit_diagnostics.json", diagnostics)
    write_json(
        out / "population_spending.json",
        spending(frame.TOTEXP23, frame.weight, config.tail_threshold),
    )
    aggregate_policies(scored, config).to_csv(out / "policies_aggregate.csv", index=False)


def aggregate_policies(scored, config) -> pd.DataFrame:
    """Apply each policy within fit/fold, then summarize selected people jointly."""
    rows = []
    for (seed, block, model), group in scored.groupby(["seed", "block", "model"]):
        group = group.reset_index(drop=True)
        for capacity in config.capacities:
            selected = np.zeros(len(group), bool)
            for _, indices in group.groupby("fold").groups.items():
                fold = group.loc[indices]
                selected[indices] = select_capacity(
                    fold.score, fold.weight, fold.DUPERSID, capacity, config.tie_seed
                )
            rows.append(
                {
                    "seed": seed,
                    "block": block,
                    "model": model,
                    "requested_capacity": capacity,
                    **selected_spending(group, selected, threshold=config.tail_threshold),
                }
            )
    return pd.DataFrame(rows)
