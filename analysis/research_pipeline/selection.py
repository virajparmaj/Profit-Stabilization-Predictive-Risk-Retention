"""Outcome-independent ranking, explicit class direction and discrete weighted capacity."""

import hashlib

import numpy as np


def validate_vectors(values, weights) -> tuple[np.ndarray, np.ndarray]:
    x, w = np.asarray(values, float), np.asarray(weights, float)
    if x.ndim != 1 or x.shape != w.shape or not len(x):
        raise ValueError("Expected nonempty aligned vectors")
    if not np.isfinite(x).all() or not np.isfinite(w).all() or (w < 0).any() or w.sum() <= 0:
        raise ValueError("Invalid values or weights")
    return x, w


def weighted_quantile(values, weights, q: float) -> float:
    x, w = validate_vectors(values, weights)
    if not 0 <= q <= 1:
        raise ValueError("Quantile outside [0,1]")
    positive = w > 0
    x, w = x[positive], w[positive]
    order = np.argsort(x, kind="stable")
    index = min(np.searchsorted(np.cumsum(w[order]), q * w.sum()), len(x) - 1)
    return float(x[order[index]])


def tie_keys(ids, seed: int) -> np.ndarray:
    ids = np.asarray(ids).astype(str)
    if len(set(ids)) != len(ids):
        raise ValueError("Selection requires unique person IDs")
    return np.array([hashlib.sha256(f"{seed}:{i}".encode()).hexdigest() for i in ids])


def select_capacity(scores, weights, ids, capacity: float, seed: int = 7342) -> np.ndarray:
    scores, weights = validate_vectors(scores, weights)
    if len(ids) != len(scores) or not 0 <= capacity <= 1:
        raise ValueError("Invalid IDs or capacity")
    keys = tie_keys(ids, seed)
    order = np.lexsort((keys, -scores))
    order = order[weights[order] > 0]
    prefixes = np.r_[0.0, np.cumsum(weights[order])]
    size = int(np.argmin(np.abs(prefixes - capacity * weights.sum())))
    selected = np.zeros(len(scores), dtype=bool)
    selected[order[:size]] = True
    return selected
