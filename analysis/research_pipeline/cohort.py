"""Raw-to-cohort construction; original notebooks and data are never overwritten."""

from pathlib import Path

import numpy as np
import pandas as pd

from .config import Config
from .dictionary import CATEGORIES, DX, FUNCTION, INCOME, SENTINELS, blocks


def add_count(frame: pd.DataFrame, fields: list[str], prefix: str, legacy: bool) -> None:
    raw = frame[fields]
    valid = raw.isin([1, 2])
    if not raw.isin([1, 2] + SENTINELS).all().all():
        raise ValueError(f"Undocumented count code in {fields}")
    count = raw.eq(1).sum(axis=1).astype(float)
    frame[prefix] = count if legacy else count.where(valid.any(axis=1), np.nan)
    frame[f"{prefix}_unknown"] = 0 if legacy else (~valid).sum(axis=1)
    for code, label in [
        (-1, "inapplicable"),
        (-7, "refused"),
        (-8, "dont_know"),
        (-9, "not_ascertained"),
        (-15, "cannot_compute"),
    ]:
        frame[f"{prefix}_{label}"] = 0 if legacy else raw.eq(code).sum(axis=1)


def build_cohort(path: Path, config: Config) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    raw = pd.read_csv(path, dtype={"DUPERSID": str, "DUID": str})
    if raw.DUPERSID.isna().any() or not raw.DUPERSID.is_unique or raw.DUID.isna().any():
        raise ValueError("Missing/duplicate person ID or missing dwelling ID")
    weight = "SAQWT23F" if config.population == "adult_saq" else "PERWT23F"
    eligible = (
        (raw.SAQELIG == 1) & (raw.AGE42X >= 18)
        if config.population == "adult_saq"
        else raw.AGELAST >= 18
    )
    mask = eligible & (raw[weight] > 0) & (raw.PERWT23F > 0)
    frame = raw.loc[mask].copy().reset_index(drop=True)
    frame["weight"] = frame[weight]
    endpoints = frame[["TOTEXP23", "ERTOT23", "IPDIS23"]].to_numpy(float)
    if frame.empty or not np.isfinite(endpoints).all() or (endpoints < 0).any():
        raise ValueError("Empty cohort or invalid endpoint values")
    if not np.isfinite(frame.weight.to_numpy(float)).all():
        raise ValueError("Nonfinite survey weight")
    diagnoses = DX + ["ANYLMI23", "COVIDEVER53"] if config.burden == "legacy12" else DX
    legacy = config.missingness == "legacy_zero"
    add_count(frame, diagnoses, "DX_CT", legacy)
    add_count(frame, FUNCTION, "LIMIT_CT", legacy)
    features = list(dict.fromkeys(f for fs in blocks(config.population).values() for f in fs))
    missing = {}
    for name in features:
        values = frame[name]
        if values.isna().any() and not name.startswith(("DX_CT", "LIMIT_CT")):
            raise ValueError(f"Unexpected raw missing value in {name}")
        missing[name] = int(
            values.isna().sum() if name in INCOME else ((values < 0) | values.isna()).sum()
        )
        if name in CATEGORIES:
            if not values.isin(CATEGORIES[name] + SENTINELS).all():
                raise ValueError(f"Undocumented category in {name}")
            if legacy:
                frame[name] = values.where(values >= 0, 0)
        elif name not in INCOME and not name.startswith(("DX_CT", "LIMIT_CT")):
            # Preserve the reason for missingness separately from an imputed numeric value.
            frame[f"{name}_code"] = np.where(values < 0, values, 0)
            frame[name] = values.where(values >= 0, 0 if legacy else np.nan)
    design = raw[["VARSTR", "VARPSU"]].drop_duplicates().sort_values(["VARSTR", "VARPSU"])
    if design.isna().any().any() or (design.groupby("VARSTR").size() < 2).any():
        raise ValueError("Invalid design or singleton stratum; no silent variance adjustment")
    keep = list(
        dict.fromkeys(
            [
                "DUPERSID",
                "DUID",
                "PANEL",
                "VARSTR",
                "VARPSU",
                "weight",
                "TOTEXP23",
                "ERTOT23",
                "IPDIS23",
                "INSCOV23",
                "PERWT23F",
                "SAQWT23F",
            ]
            + features
            + [c for c in frame if c.endswith("_code")]
        )
    )
    flow = {
        "raw_n": len(raw),
        "eligible_n": int(eligible.sum()),
        "analytic_n": len(frame),
        "excluded_n": len(raw) - len(frame),
        "weight": weight,
        "weight_sum": float(frame.weight.sum()),
        "dwelling_units": frame.DUID.nunique(),
        "strata": design.VARSTR.nunique(),
        "psus": len(design),
        "missing_counts": missing,
        "legacy_label_threshold": float(raw.TOTEXP23.quantile(0.3)),
        "legacy_label_n": int(
            (
                (raw.TOTEXP23 <= raw.TOTEXP23.quantile(0.3))
                & (raw.ERTOT23 == 0)
                & (raw.IPDIS23 == 0)
            ).sum()
        ),
    }
    return frame[keep], design.reset_index(drop=True), flow
