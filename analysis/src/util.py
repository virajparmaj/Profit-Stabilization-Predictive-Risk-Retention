"""Weighted statistics helpers and the cached analysis frame builder.

Everything downstream loads the analysis table through load(), which builds a
cached join of the model-ready table and the raw MEPS fields on first use.
"""
import os
import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CACHE = os.path.join(ROOT, 'analysis', '.cache')
ENRICHED = os.path.join(CACHE, 'enriched.parquet')

RAW_FIELDS = [
    'DUPERSID', 'PANEL', 'REGION53', 'AGELAST', 'SEX',
    'TOTEXP23', 'TOTSLF23', 'TOTMCR23', 'TOTMCD23', 'TOTPRV23', 'TOTPTR23', 'TOTOTH23',
    'TOTOSR23', 'TOTVA23', 'TOTTRI23', 'TOTOFD23', 'TOTSTL23', 'TOTWCP23',
    'OBVEXP23', 'OPTEXP23', 'ERTEXP23', 'ERTSLF23', 'IPTEXP23', 'IPTSLF23', 'IPNGTD23',
    'RXEXP23', 'DVTEXP23', 'HHAEXP23',
    'ERTOT23', 'IPDIS23', 'OBTOTV23', 'OPTOTV23', 'RXTOT23', 'DVTOT23', 'HHTOTD23',
    'DLAYCA42', 'AFRDCA42', 'DLAYDN42', 'AFRDDN42', 'DLAYPM42', 'AFRDPM42', 'HAVEUS42',
    'ADILCR42', 'ADRTCR42', 'PERWT23F', 'VARSTR', 'VARPSU', 'SAQWT23F', 'INSCOV23', 'INSURC23',
]

def build_enriched():
    """Join data_processed/meps_model_ready_2023.csv to the extra raw MEPS fields."""
    raw_path = os.path.join(ROOT, 'data_raw', 'h251.csv')
    mr_path = os.path.join(ROOT, 'data_processed', 'meps_model_ready_2023.csv')
    header = pd.read_csv(raw_path, nrows=0).columns.tolist()
    cols = [c for c in RAW_FIELDS if c in header]
    raw = pd.read_csv(raw_path, usecols=cols)
    mr = pd.read_csv(mr_path)
    dup = [c for c in raw.columns if c in mr.columns and c != 'DUPERSID']
    df = mr.merge(raw.drop(columns=dup), on='DUPERSID', how='left', validate='1:1')
    os.makedirs(CACHE, exist_ok=True)
    df.to_parquet(ENRICHED)
    return df

def load():
    if not os.path.exists(ENRICHED):
        return build_enriched()
    return pd.read_parquet(ENRICHED)

def wq(x, w, qs):
    """Weighted quantiles."""
    x = np.asarray(x, float); w = np.asarray(w, float)
    m = ~np.isnan(x) & (w > 0); x, w = x[m], w[m]
    o = np.argsort(x); x, w = x[o], w[o]
    cw = np.cumsum(w); cw = (cw - 0.5 * w) / cw[-1]
    return np.interp(qs, cw, x)

def wmean(x, w):
    x = np.asarray(x, float); w = np.asarray(w, float)
    m = ~np.isnan(x) & (w > 0)
    return np.sum(x[m] * w[m]) / np.sum(w[m])

def top_share(x, w, frac):
    """Share of total spend held by the most expensive `frac` of members."""
    x = np.asarray(x, float); w = np.asarray(w, float)
    m = ~np.isnan(x) & (w > 0); x, w = x[m], w[m]
    o = np.argsort(-x); x, w = x[o], w[o]
    cw = np.cumsum(w) / np.sum(w)
    k = np.searchsorted(cw, frac) + 1
    tot = np.sum(x * w)
    if k >= len(x):
        return 1.0
    excess = cw[k - 1] - frac
    s = np.sum(x[:k] * w[:k]) - excess * np.sum(w) * x[k - 1]
    return s / tot

def gini(x, w):
    x = np.asarray(x, float); w = np.asarray(w, float)
    m = ~np.isnan(x) & (w > 0); x, w = x[m], w[m]
    o = np.argsort(x); x, w = x[o], w[o]
    cw = np.cumsum(w); cx = np.cumsum(x * w)
    cx_n = cx / cx[-1]; cw_n = cw / cw[-1]
    B = np.sum((cx_n[1:] + cx_n[:-1]) / 2 * np.diff(cw_n))
    return 1 - 2 * B
