"""Outcome-blind dwelling-unit partitions shared by every model."""

import numpy as np
from sklearn.model_selection import GroupKFold, GroupShuffleSplit


def outer_folds(frame, n_splits: int, seed: int):
    splitter = GroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for fold, (train, test) in enumerate(splitter.split(frame, groups=frame.DUID)):
        if set(frame.iloc[train].DUID) & set(frame.iloc[test].DUID):
            raise AssertionError("Dwelling leakage")
        yield fold, train, test


def reference_split(frame, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    first = GroupShuffleSplit(n_splits=1, train_size=0.6, random_state=seed)
    train, other = next(first.split(frame, groups=frame.DUID))
    second = GroupShuffleSplit(n_splits=1, train_size=0.5, random_state=seed + 1)
    calibration, reference = next(second.split(frame.iloc[other], groups=frame.iloc[other].DUID))
    return train, other[calibration], other[reference]
