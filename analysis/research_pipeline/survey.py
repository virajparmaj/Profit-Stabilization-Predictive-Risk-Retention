"""With-replacement survey inference using the full released strata/PSU design.

Rao-Wu n_h-1 bootstrap: draw n_h-1 PSUs with replacement per stratum;
multiply weights by n_h/(n_h-1) times selection multiplicity. No FPC.
This matches R survey::subbootweights. Singleton strata are rejected.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm


def replicate_design(design: pd.DataFrame, replicates: int, seed: int) -> pd.DataFrame:
    if replicates < 1 or design.duplicated(["VARSTR", "VARPSU"]).any():
        raise ValueError("Invalid replicate count or duplicate PSU")
    rng = np.random.default_rng(seed)
    result = design.copy().reset_index(drop=True)
    arrays = np.zeros((len(result), replicates))
    for _, indices in result.groupby("VARSTR", sort=True).groups.items():
        idx = np.array(indices)
        n = len(idx)
        if n < 2:
            raise ValueError("Singleton stratum: specify a justified alternative, never drop it")
        counts = rng.multinomial(n - 1, np.ones(n) / n, size=replicates).T
        arrays[idx] = counts * n / (n - 1)
    return pd.concat(
        [result, pd.DataFrame(arrays, columns=[f"r{b}" for b in range(replicates)])], axis=1
    )


def multipliers(frame: pd.DataFrame, replicated: pd.DataFrame) -> np.ndarray:
    joined = frame[["VARSTR", "VARPSU"]].merge(
        replicated, how="left", validate="many_to_one", sort=False
    )
    values = joined[[c for c in replicated if c.startswith("r")]].to_numpy()
    if not np.isfinite(values).all():
        raise ValueError("Evaluation PSU absent from complete survey design")
    return values


def resample_training(training, design, seed: int):
    replicated = replicate_design(design, 1, seed)
    factors = multipliers(training, replicated)[:, 0]
    sizes = design.groupby("VARSTR").size()
    scale = training.VARSTR.map(sizes).to_numpy(float)
    scale = scale / (scale - 1)
    counts = np.rint(factors / scale).astype(int)
    index = np.repeat(np.arange(len(training)), counts)
    sampled = training.iloc[index].copy().reset_index(drop=True)
    sampled["weight"] = sampled.weight.to_numpy() * scale[index]
    return sampled


def taylor_mean(frame, design, value: str, weight: str = "weight") -> dict:
    """Linearized ratio mean with zero contributions for out-of-domain PSUs."""
    w = frame[weight].to_numpy(float)
    x = frame[value].to_numpy(float)
    if not np.isfinite(x).all() or not np.isfinite(w).all() or (w < 0).any() or w.sum() <= 0:
        raise ValueError("Invalid survey mean data")
    mean = float(np.average(x, weights=w))
    work = frame[["VARSTR", "VARPSU"]].copy()
    work["linearized"] = w * (x - mean) / w.sum()
    totals = work.groupby(["VARSTR", "VARPSU"], as_index=False).linearized.sum()
    complete = design.merge(totals, how="left", validate="one_to_one").fillna({"linearized": 0.0})
    variance = 0.0
    for _, group in complete.groupby("VARSTR"):
        n = len(group)
        if n < 2:
            raise ValueError("Singleton stratum")
        values = group.linearized.to_numpy()
        variance += n / (n - 1) * np.sum((values - values.mean()) ** 2)
    return {"mean": mean, "se": float(np.sqrt(variance)), "variance": float(variance)}


def paired_interval(estimate: float, replicates) -> dict:
    """Normal interval from MSE-centered Rao-Wu replicates, conditional on predictions."""
    values = np.asarray(replicates, float)
    valid = np.isfinite(values)
    if valid.sum() != len(values) or len(values) < 2:
        return {
            "estimate": estimate,
            "se": None,
            "low": None,
            "high": None,
            "valid_replicates": int(valid.sum()),
            "status": "invalid_replicates",
        }
    se = float(np.sqrt(np.mean((values - estimate) ** 2)))
    half_se = float(np.sqrt(np.mean((values[: len(values) // 2] - estimate) ** 2)))
    return {
        "estimate": estimate,
        "se": se,
        "low": estimate - norm.ppf(0.975) * se,
        "high": estimate + norm.ppf(0.975) * se,
        "valid_replicates": len(values),
        "half_replicate_se": half_se,
        "se_relative_mc_approx": float(1 / np.sqrt(2 * len(values))),
        "status": "conditional_fixed_predictions",
    }
