"""Canonical bootstrap for every confidence interval in the analysis.

All CIs quoted anywhere -- ANALYSIS_REPORT.md, website-handoff/HANDOFF.md,
insight_metrics.json and the per-chart data files -- must come from this module,
so that the same statistic always produces byte-identical bounds.

Determinism: one global SEED plus a stable CRC32 of the statistic's key. Python's
built-in hash() is salted per process and must not be used here.
"""
import zlib
import numpy as np

SEED = 20260824          # fixed; do not change without regenerating every artifact
B = 4000                 # resamples; large enough that bounds are stable to 0.1pp
CI_LEVEL = (2.5, 97.5)   # percentile bootstrap, 95%

def _rng(key: str) -> np.random.Generator:
    return np.random.default_rng(SEED + zlib.crc32(key.encode()))

def boot_ci(frame, statfn, key: str, B: int = B):
    """Percentile bootstrap CI of statfn(resampled_frame), resampling records.

    frame  : DataFrame of the segment
    statfn : callable(DataFrame) -> float
    key    : stable identifier for this statistic (drives the seed)
    """
    rng = _rng(key)
    n = len(frame)
    idx_all = np.arange(n)
    out = np.empty(B, dtype=float)
    for b in range(B):
        out[b] = statfn(frame.iloc[rng.choice(idx_all, n, replace=True)])
    lo, hi = np.percentile(out, CI_LEVEL)
    return round(float(lo), 1), round(float(hi), 1)

def rate_over(threshold: float):
    """Weighted % of members with TOTEXP23 >= threshold."""
    def f(g):
        x = g.TOTEXP23.values; w = g.PERWT23F.values
        return 100 * w[x >= threshold].sum() / w.sum()
    return f

def rate_low_risk(g):
    """Weighted % of members labelled LOW_RISK."""
    w = g.PERWT23F.values; v = g.LOW_RISK.values
    return 100 * w[v == 1].sum() / w.sum()
