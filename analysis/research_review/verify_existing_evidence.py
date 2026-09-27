"""Audit existing results without fitting models or altering project data.

Requires numpy, pandas, pyarrow and scikit-learn. Run from any directory.
The OOF checks validate cached predictions, not their training provenance.
The ten-item count below is a sensitivity analysis, not a validated index.
"""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[2]
DX = ["HIBPDX", "DIABDX_M18", "CHDDX", "MIDX", "STRKDX", "EMPHDX",
      "CHOLDX", "ARTHDX", "ASTHDX", "CANCERDX"]


def weighted_mean(values: pd.Series, weights: pd.Series) -> float:
    """Return the weighted arithmetic mean."""
    return float(np.average(values, weights=weights))


def pool_summary(frame: pd.DataFrame) -> dict:
    """Keep absolute and relative dispersion, and two tail estimands, separate."""
    x, w = frame.TOTEXP23, frame.PERWT23F
    mean = weighted_mean(x, w)
    sd = float(np.sqrt(weighted_mean((x - mean) ** 2, w)))
    total = float((x * w).sum())
    positive_x, positive_w = x[x > 0], w[x > 0]
    positive_mean = weighted_mean(positive_x, positive_w)
    positive_cv = float(np.sqrt(weighted_mean((positive_x - positive_mean) ** 2,
                                             positive_w))) / positive_mean
    return {
        "n": len(frame), "population_weight": float(w.sum()),
        "mean_usd": mean, "sd_usd": sd, "cv": sd / mean,
        "pct_zero_spend": 100 * weighted_mean(x == 0, w),
        "positive_spend_cv": positive_cv,
        "pct_ge_20k": 100 * weighted_mean(x >= 20000, w),
        "excess_above_20k_usd_per_person": weighted_mean((x - 20000).clip(lower=0), w),
        "pct_dollars_excess_above_20k": 100 * float(((x - 20000).clip(lower=0) * w).sum()) / total,
        "pct_dollars_from_people_ge_20k": 100 * float((x[x >= 20000] * w[x >= 20000]).sum()) / total,
    }


def burden_summary(frame: pd.DataFrame, count: str) -> dict:
    """Recalculate exploratory coverage gaps and zero-office-visit segments."""
    result = {}
    for label, mask in {"insured": frame.INSCOV23 != 3,
                        "uninsured": frame.INSCOV23 == 3}.items():
        g = frame[mask & (frame[count] >= 2)]
        result[label] = {"n": len(g), "pct_low_label": 100 * weighted_mean(g.LOW_RISK, g.PERWT23F)}
    g = frame[(frame[count] >= 3) & (frame.OBTOTV23 == 0)]
    result["three_plus_zero_office"] = {
        **pool_summary(g), "pct_low_label": 100 * weighted_mean(g.LOW_RISK, g.PERWT23F),
        "pct_acute_dollars": 100 * float(((g.ERTEXP23 + g.IPTEXP23) * g.PERWT23F).sum())
        / float((g.TOTEXP23 * g.PERWT23F).sum()),
        "n_with_outpatient_visits": int((g.OPTOTV23 > 0).sum()),
    }
    return result


def main() -> None:
    """Write a deterministic audit of local source files and cached outputs."""
    paths = {"raw": ROOT / "data_raw/h251.csv",
             "model_ready": ROOT / "data_processed/meps_model_ready_2023.csv",
             "notebook_copy": ROOT / "notebooks/meps_model_ready_2023.csv",
             "oof": ROOT / "analysis/.cache/oof.parquet",
             "stale_scores": ROOT / "data_processed/scored_members_2023.parquet"}
    cols = ["DUPERSID", "TOTEXP23", "PERWT23F", "INSCOV23", "OBTOTV23", "OPTOTV23",
            "ERTEXP23", "IPTEXP23", "ERTOT23", "IPDIS23", "ANYLMI23", "COVIDEVER53"] + DX
    raw = pd.read_csv(paths["raw"], usecols=cols)
    mr = pd.read_csv(paths["model_ready"], usecols=["DUPERSID", "LOW_RISK", "CHRONIC_CT"])
    d = raw.merge(mr, on="DUPERSID", validate="one_to_one")
    threshold = float(raw.TOTEXP23.quantile(.30))
    rebuilt = ((d.TOTEXP23 <= threshold) & (d.ERTOT23 == 0) & (d.IPDIS23 == 0)).astype(int)
    checks = {"raw_n": len(raw), "label_threshold_usd": threshold,
              "label_n": int(mr.LOW_RISK.sum()), "label_mismatches": int((rebuilt != d.LOW_RISK).sum()),
              "chronic_count_mismatches": int((d.CHRONIC_CT != d[DX + ["ANYLMI23", "COVIDEVER53"]].eq(1).sum(axis=1)).sum())}
    d = d[d.PERWT23F > 0].copy()
    d["DX10"] = d[DX].eq(1).sum(axis=1)
    checks["positive_weight_n"] = len(d)
    checks["weighted_label_pct"] = 100 * weighted_mean(d.LOW_RISK, d.PERWT23F)
    checks["burden_original"] = burden_summary(d, "CHRONIC_CT")
    checks["burden_dx10_sensitivity"] = burden_summary(d, "DX10")
    oof = pd.read_parquet(paths["oof"])
    scored = d.merge(oof, on="DUPERSID", validate="one_to_one")
    checks["cached_oof_auc_unweighted"] = float(roc_auc_score(scored.LOW_RISK, scored.P_OOF))
    checks["cached_oof_auc_weighted"] = float(roc_auc_score(scored.LOW_RISK, scored.P_OOF, sample_weight=scored.PERWT23F))
    checks["cached_oof_pools"] = {"population": pool_summary(scored)}
    for fraction in [.3, .1]:
        g = scored[scored.P_OOF >= scored.P_OOF.quantile(1 - fraction)]
        checks["cached_oof_pools"][str(fraction)] = pool_summary(g)
    stale = pd.read_parquet(paths["stale_scores"])
    merged = stale.merge(mr, on="DUPERSID", suffixes=("_stored", "_current"), validate="one_to_one")
    checks["stale_scores"] = {"n": len(stale), "joined_n": len(merged),
                             "label_n": int(stale.LOW_RISK.sum()),
                             "label_mismatches": int((merged.LOW_RISK_stored != merged.LOW_RISK_current).sum())}
    checks["sha256"] = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in paths.items()}
    checks["scope"] = "Descriptive recheck and cached-score evaluation; no fresh model fit or survey confidence intervals."
    output = Path(__file__).with_name("verified_metrics.json")
    output.write_text(json.dumps(checks, indent=2) + "\n")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
