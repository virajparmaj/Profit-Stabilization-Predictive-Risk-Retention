"""Conservative summaries: an undefined required observation stays undefined."""

import numpy as np
import pandas as pd


def weighted_metrics(group: pd.DataFrame, keys: list[str], expected: int | None = None) -> dict:
    expected = len(group) if expected is None else expected
    weights = group.weight_sum.to_numpy(float)
    result = {}
    for key in keys:
        values = group[key].to_numpy(float)
        valid = np.isfinite(values) & np.isfinite(weights) & (weights > 0)
        complete = valid.sum() == expected and len(group) == expected
        result[key] = float(np.average(values, weights=weights)) if complete else np.nan
        result[f"{key}_valid"] = int(valid.sum())
        result[f"{key}_expected"] = expected
    return result


def refit_statistics(values: pd.Series, expected: int) -> dict:
    valid = values[np.isfinite(values)]
    complete = len(valid) == expected and len(values) == expected
    return {
        **{
            key: float(getattr(valid, key)()) if complete else np.nan
            for key in ["mean", "std", "min", "max"]
        },
        "valid": len(valid),
        "expected": expected,
    }
