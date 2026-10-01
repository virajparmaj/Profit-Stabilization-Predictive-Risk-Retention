"""Separate classification, membership, dollar dispersion and relative dispersion."""

import numpy as np
from scipy.optimize import minimize
from scipy.special import expit, logit
from sklearn.metrics import average_precision_score, roc_auc_score

from .selection import validate_vectors, weighted_quantile


def classification(y, scores, weights, calibration: bool = True) -> dict:
    p, w = validate_vectors(scores, weights)
    y = np.asarray(y)
    if y.shape != p.shape or not set(np.unique(y)) <= {0, 1} or ((p < 0) | (p > 1)).any():
        raise ValueError("Invalid labels/probabilities")
    prevalence = float(np.average(y, weights=w))
    result = {
        "auc": None,
        "average_precision": None,
        "prevalence": prevalence,
        "brier": float(np.average((y - p) ** 2, weights=w)),
        "intercept_brier": prevalence * (1 - prevalence),
    }
    if len(np.unique(y[w > 0])) < 2:
        return result
    result.update(
        auc=float(roc_auc_score(y, p, sample_weight=w)),
        average_precision=float(average_precision_score(y, p, sample_weight=w)),
    )
    if calibration:
        z, wn = logit(np.clip(p, 1e-8, 1 - 1e-8)), w / w.sum()

        def loss(beta):
            eta = beta[0] + beta[1] * z
            residual = (expit(eta) - y) * wn
            return np.sum(wn * (np.logaddexp(0, eta) - y * eta)), np.array(
                [residual.sum(), residual @ z]
            )

        fitted = minimize(loss, [0.0, 1.0], jac=True, method="BFGS")
        result.update(
            calibration_intercept=float(fitted.x[0]) if fitted.success else None,
            calibration_slope=float(fitted.x[1]) if fitted.success else None,
            calibration_fit_success=bool(fitted.success),
        )
    return result


def spending(costs, weights, threshold: float = 20000) -> dict:
    x, w = validate_vectors(costs, weights)
    if (x < 0).any() or threshold <= 0:
        raise ValueError("Spending must be nonnegative and threshold positive")
    mean = float(np.average(x, weights=w))
    sd = float(np.sqrt(np.average((x - mean) ** 2, weights=w)))
    positive = (x > 0) & (w > 0)
    positive_cv = None
    if positive.any():
        pm = np.average(x[positive], weights=w[positive])
        positive_cv = float(np.sqrt(np.average((x[positive] - pm) ** 2, weights=w[positive])) / pm)
    excess = float(np.average(np.maximum(x - threshold, 0), weights=w))
    return {
        "n": int((w > 0).sum()),
        "weight_sum": float(w.sum()),
        "mean": mean,
        "sd": sd,
        "median": weighted_quantile(x, w, 0.5),
        "cv": sd / mean if mean else None,
        "zero_share": float(np.average(x == 0, weights=w)),
        "positive_cv": positive_cv,
        "tail_count": int(((x >= threshold) & (w > 0)).sum()),
        "tail_probability": float(np.average(x >= threshold, weights=w)),
        "mean_excess": excess,
        "relative_excess": excess / mean if mean else None,
        "effective_n": float(w.sum() ** 2 / (w @ w)),
    }


def selected_spending(frame, selected, weights=None, threshold: float = 20000) -> dict:
    w = frame.weight.to_numpy(float) if weights is None else np.asarray(weights, float)
    selected = np.asarray(selected, bool)
    if selected.shape != w.shape:
        raise ValueError("Membership shape mismatch")
    capacity = float(w[selected].sum() / w.sum())
    if not w[selected].sum():
        return {
            "n": 0,
            "weight_sum": 0.0,
            "capacity": capacity,
            "status": "empty",
            **{
                key: None
                for key in [
                    "mean",
                    "sd",
                    "median",
                    "cv",
                    "zero_share",
                    "positive_cv",
                    "tail_count",
                    "tail_probability",
                    "mean_excess",
                    "relative_excess",
                    "effective_n",
                ]
            },
        }
    return {
        **spending(frame.TOTEXP23.to_numpy()[selected], w[selected], threshold),
        "capacity": capacity,
        "status": "ok",
    }


def membership(base, changed, weights) -> dict:
    a, b = np.asarray(base, bool), np.asarray(changed, bool)
    _, w = validate_vectors(a.astype(float), weights)
    if a.shape != b.shape:
        raise ValueError("Membership shape mismatch")
    union, original = w[a | b].sum(), w[a].sum()
    return {
        "jaccard": float(w[a & b].sum() / union) if union else None,
        "population_disagreement": float(w[a ^ b].sum() / w.sum()),
        "baseline_member_loss": float(w[a & ~b].sum() / original) if original else None,
    }
