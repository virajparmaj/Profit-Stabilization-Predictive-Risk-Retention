"""Endpoints learned from training data only; fixed endpoint across primary E2 refits."""

import numpy as np

from .selection import weighted_quantile


def cutoff(training, definition: str) -> float:
    if definition == "legacy_484_4":
        return 484.4
    if definition != "training_weighted":
        raise ValueError("Unknown label definition")
    return weighted_quantile(training.TOTEXP23, training.weight, 0.3)


def labels(frame, threshold: float) -> np.ndarray:
    if threshold < 0 or not np.isfinite(threshold):
        raise ValueError("Invalid spending cutoff")
    return ((frame.TOTEXP23 <= threshold) & (frame.ERTOT23 == 0) & (frame.IPDIS23 == 0)).to_numpy(
        dtype=int
    )
