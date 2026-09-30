"""E2: pipeline refitting with fixed reference people and a fixed endpoint."""

import time
import warnings

import numpy as np
import pandas as pd

from .metrics import classification, membership, selected_spending
from .models import fit_model, positive_probability
from .provenance import write_json
from .selection import select_capacity, weighted_quantile
from .splits import reference_split
from .survey import resample_training
from .targets import cutoff, labels

ANCHORS = [("B2", "logistic"), ("B3", "logistic"), ("B3", "xgboost"), ("B4", "xgboost")]


def base_fit(training, calibration, reference, threshold, block, model, config):
    pipe = fit_model(training, labels(training, threshold), block, model, config, config.seeds[0])
    p = positive_probability(pipe, reference)
    pc = positive_probability(pipe, calibration)
    numerical = weighted_quantile(pc, calibration.weight, 1 - config.capacity)
    base = select_capacity(
        p, reference.weight, reference.DUPERSID, config.capacity, config.tie_seed
    )
    return p, base, numerical


def evaluate_refit(reference, p, original_p, base, numerical, threshold, config):
    selected = select_capacity(
        p, reference.weight, reference.DUPERSID, config.capacity, config.tie_seed
    )
    fixed = p >= numerical
    common = {
        **classification(labels(reference, threshold), p, reference.weight, calibration=False),
        "probability_mad": float(np.average(np.abs(p - original_p), weights=reference.weight)),
    }
    quota = {
        "policy": "weighted_capacity",
        **common,
        **membership(base, selected, reference.weight),
        **selected_spending(reference, selected, threshold=config.tail_threshold),
    }
    fixed_row = {
        "policy": "fixed_threshold",
        **common,
        **membership(original_p >= numerical, fixed, reference.weight),
        **selected_spending(reference, fixed, threshold=config.tail_threshold),
    }
    return [quota, fixed_row], selected


def run_anchor(training, calibration, reference, design, threshold, block, model, config, out):
    original_p, base, numerical = base_fit(
        training, calibration, reference, threshold, block, model, config
    )
    base_rows, _ = evaluate_refit(
        reference, original_p, original_p, base, numerical, threshold, config
    )
    rows = [{"refit": -1, "block": block, "model": model, **r} for r in base_rows]
    predictions, failures, diagnostics = [], [], []
    for b in range(config.refits):
        started = time.perf_counter()
        try:
            sampled = resample_training(training, design, config.refit_seed + b)
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                pipe = fit_model(
                    sampled, labels(sampled, threshold), block, model, config, config.seeds[0]
                )
                p = positive_probability(pipe, reference)
            summaries, selected = evaluate_refit(
                reference, p, original_p, base, numerical, threshold, config
            )
            rows.extend({"refit": b, "block": block, "model": model, **r} for r in summaries)
            predictions.append(
                pd.DataFrame(
                    {"DUPERSID": reference.DUPERSID, "score": p, "selected": selected, "refit": b}
                )
            )
            diagnostics.append(
                {
                    "refit": b,
                    "seconds": time.perf_counter() - started,
                    "warnings": [str(w.message) for w in caught],
                }
            )
        except Exception as error:
            failures.append({"refit": b, "type": type(error).__name__, "error": str(error)})
        if (b + 1) % 10 == 0:
            print(
                f"E2 {block}/{model}: {b+1}/{config.refits} refits, failures={len(failures)}",
                flush=True,
            )
    prefix = f"{block}_{model}"
    pd.DataFrame(
        {"DUPERSID": reference.DUPERSID, "score": original_p, "selected": base}
    ).to_parquet(out / f"{prefix}_base.parquet", index=False)
    if predictions:
        pd.concat(predictions).to_parquet(out / f"{prefix}_refit_scores.parquet", index=False)
    write_json(
        out / f"{prefix}_diagnostics.json",
        {
            "threshold": numerical,
            "failures": failures,
            "fits": diagnostics,
            "successful_refits": len(predictions),
            "requested_refits": config.refits,
        },
    )
    return rows, failures


def run_e2(frame, design, config, out) -> None:
    tr, ca, re = reference_split(frame, config.seeds[0])
    training, calibration, reference = [
        frame.iloc[ix].reset_index(drop=True) for ix in [tr, ca, re]
    ]
    threshold = cutoff(training, config.label)
    pd.concat(
        [
            part[["DUPERSID", "DUID"]].assign(partition=name)
            for part, name in [
                (training, "training"),
                (calibration, "calibration"),
                (reference, "reference"),
            ]
        ]
    ).to_csv(out / "splits.csv", index=False)
    reference.to_parquet(out / "reference.parquet", index=False)
    write_json(
        out / "endpoint.json",
        {
            "threshold": threshold,
            "fixed_across_refits": True,
            "n_train": len(training),
            "n_calibration": len(calibration),
            "n_reference": len(reference),
        },
    )
    rows, failed = [], []
    for block, model in ANCHORS:
        result, failures = run_anchor(
            training, calibration, reference, design, threshold, block, model, config, out
        )
        rows.extend(result)
        failed.extend({"block": block, "model": model, **f} for f in failures)
        pd.DataFrame(rows).to_csv(out / "refit_metrics.csv", index=False)
    write_json(out / "failures.json", failed)
    summarize_refits(out)
    if failed:
        raise RuntimeError(
            f"{len(failed)} prespecified refits failed; results saved, no replacement seeds"
        )


def summarize_refits(out) -> None:
    metrics = pd.read_csv(out / "refit_metrics.csv")
    keys = [
        "auc",
        "jaccard",
        "population_disagreement",
        "baseline_member_loss",
        "probability_mad",
        "mean",
        "sd",
        "cv",
        "capacity",
    ]
    grouped = metrics[metrics.refit >= 0].groupby(["block", "model", "policy"])[keys]
    summary = grouped.agg(["mean", "std", "min", "max"])
    summary.columns = ["_".join(c) for c in summary.columns]
    summary.to_csv(out / "refit_summary.csv")
    frequencies = []
    for path in sorted(out.glob("*_refit_scores.parquet")):
        values = pd.read_parquet(path)
        group = values.groupby("DUPERSID").agg(
            selection_frequency=("selected", "mean"),
            successful_refits=("selected", "size"),
            probability_sd=("score", "std"),
        )
        group["frequency_mc_se"] = np.sqrt(
            group.selection_frequency * (1 - group.selection_frequency) / group.successful_refits
        )
        group["specification"] = path.name.removesuffix("_refit_scores.parquet")
        frequencies.append(group.reset_index())
    if frequencies:
        pd.concat(frequencies).to_parquet(out / "selection_frequencies.parquet", index=False)
