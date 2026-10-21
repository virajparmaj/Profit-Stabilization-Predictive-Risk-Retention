"""Paired conditional evaluation uncertainty for the prespecified B3 model contrast."""

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from .metrics import selected_spending
from .provenance import write_json
from .selection import select_capacity
from .survey import multipliers, paired_interval, replicate_design


def contrast_metrics(group, weights, config) -> dict:
    selected = np.zeros(len(group), bool)
    auc_sum, brier_sum = 0.0, 0.0
    for _, indices in group.groupby("fold").groups.items():
        g, w = group.loc[indices], weights[indices]
        if w.sum() <= 0 or len(np.unique(g.y.to_numpy()[w > 0])) < 2:
            return {key: np.nan for key in ["auc", "brier", "mean", "sd", "cv", "mean_excess"]}
        auc_sum += w.sum() * roc_auc_score(g.y, g.score, sample_weight=w)
        brier_sum += np.sum(w * (g.y.to_numpy() - g.score.to_numpy()) ** 2)
        selected[indices] = select_capacity(
            g.score, w, g.DUPERSID, config.capacity, config.tie_seed
        )
    spend = selected_spending(group, selected, weights, config.tail_threshold)
    return {
        "auc": auc_sum / weights.sum(),
        "brier": brier_sum / weights.sum(),
        **{key: spend.get(key, np.nan) for key in ["mean", "sd", "cv", "mean_excess"]},
    }


def run_inference(scored, design, config, out) -> None:
    if not {"logistic", "xgboost"} <= set(scored.model) or "B3" not in set(scored.block):
        write_json(out / "primary_contrast.json", {"status": "not_applicable"})
        return
    replicated = replicate_design(design, config.design_replicates, config.design_seed)
    replicated.to_parquet(out / "evaluation_replicates.parquet", index=False)
    all_estimates = []
    for seed in config.seeds:
        model_results = {}
        for model in ["logistic", "xgboost"]:
            g = (
                scored[(scored.seed == seed) & (scored.block == "B3") & (scored.model == model)]
                .sort_values("DUPERSID")
                .reset_index(drop=True)
            )
            w = g.weight.to_numpy()
            factors = multipliers(g, replicated)
            results = [contrast_metrics(g, w, config)]
            for b in range(config.design_replicates):
                results.append(contrast_metrics(g, w * factors[:, b], config))
            model_results[model] = pd.DataFrame(results)
        diff = model_results["logistic"] - model_results["xgboost"]
        all_estimates.append(diff)
        print(f"Paired survey inference seed={seed} complete", flush=True)
    # Average paired contrasts over the predefined seeds; never treat seeds as independent samples.
    average = sum(all_estimates) / len(all_estimates)
    report = {
        key: paired_interval(float(average[key].iloc[0]), average[key].iloc[1:]) for key in average
    }
    report.update(
        contrast="B3 logistic minus B3 XGBoost",
        capacity=config.capacity,
        fold_aggregation="test-weight-mass weighted AUC/Brier; selection within fold",
        multiplicity="One prespecified model contrast; other endpoints descriptive, no omnibus significance claim",
        uncertainty="Rao-Wu PSU bootstrap; fixed predictions, fixed grouped folds; quota reapplied per replicate",
    )
    average.to_csv(out / "primary_contrast_replicates.csv", index=False)
    write_json(out / "primary_contrast.json", report)
