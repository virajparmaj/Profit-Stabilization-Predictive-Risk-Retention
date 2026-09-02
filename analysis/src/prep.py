"""Derive the labelled analysis frame used by every downstream script."""
import os
import numpy as np
import pandas as pd
from util import load, CACHE

FEATS_B3 = ['PHYEXE53', 'OFTSMK53', 'RTHLTH53', 'MNHLTH53', 'K6SUM42', 'PHQ242', 'LIMIT_CT', 'CHRONIC_CT']
OOF_CACHE = os.path.join(CACHE, 'oof.parquet')

def prep():
    """Analysis frame: positive-weight records with readable segment labels attached."""
    d = load()
    d = d[d.PERWT23F > 0].copy()
    d['AGEBAND'] = pd.cut(d.AGELAST, [-1, 17, 29, 44, 54, 64, 74, 120],
                          labels=['0-17', '18-29', '30-44', '45-54', '55-64', '65-74', '75+'])
    d['CHRONIC_B'] = pd.cut(d.CHRONIC_CT, [-1, 0, 1, 2, 3, 5, 12], labels=['0', '1', '2', '3', '4-5', '6+'])
    d['LIMIT_B'] = pd.cut(d.LIMIT_CT, [-1, 0, 1, 6], labels=['0', '1', '2+'])
    d['INS'] = d.INSCOV23.map({1: 'Private', 2: 'Public only', 3: 'Uninsured'})
    d['POV'] = pd.Categorical(
        d.POVCAT23.map({0: 'Poor/negative', 1: 'Near poor', 2: 'Low income', 3: 'Middle income', 4: 'High income'}),
        ['Poor/negative', 'Near poor', 'Low income', 'Middle income', 'High income'], ordered=True)
    d['SEXL'] = d.SEX.map({0: 'Male', 1: 'Female'})
    d['RACE'] = d.RACETHX.map({0: 'Hispanic', 1: 'NH White', 2: 'NH Black', 3: 'NH Asian', 4: 'NH Other'})
    # Access-to-care items: 1 = yes, 2 = no, negatives = inapplicable/refused/unknown.
    # Composites are conservative: anything not an explicit "yes" is treated as "no".
    d['DELAY_ANY'] = (d[['DLAYCA42', 'DLAYDN42', 'DLAYPM42']] == 1).any(axis=1).astype(int)
    d['AFFORD_BARRIER'] = (d[['AFRDCA42', 'AFRDDN42', 'AFRDPM42']] == 1).any(axis=1).astype(int)
    d['NO_USUAL_SOURCE'] = (d.HAVEUS42 == 2).astype(int)
    return d

def with_oof(d):
    """Attach out-of-fold P(LOW_RISK) from the deployed B3 pipeline, cached."""
    if os.path.exists(OOF_CACHE):
        return d.merge(pd.read_parquet(OOF_CACHE), on='DUPERSID')
    import joblib
    from sklearn.base import clone
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from util import ROOT
    pipe = joblib.load(os.path.join(ROOT, 'notebooks', 'models', 'low_risk_model_B3_chronic_xgb.joblib'))
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    p = cross_val_predict(clone(pipe), d[FEATS_B3], d.LOW_RISK.values, cv=cv, method='predict_proba')[:, 1]
    out = pd.DataFrame({'DUPERSID': d.DUPERSID.values, 'P_OOF': p})
    os.makedirs(CACHE, exist_ok=True)
    out.to_parquet(OOF_CACHE)
    return d.merge(out, on='DUPERSID')


def boot_stat(frame, statfn, B=None, seed=None, key=None):
    """Back-compat wrapper used by the exploratory a*.py scripts.

    Delegates to the canonical bootstrap in ci_lib so that any interval printed
    by an exploration script matches the published ones. `statfn` here takes
    (x, w) arrays, matching the original exploratory signature.
    """
    from ci_lib import boot_ci
    k = key or f'adhoc:{getattr(statfn, "__name__", "lambda")}:{len(frame)}'
    return boot_ci(frame, lambda g: statfn(g.TOTEXP23.values, g.PERWT23F.values), k,
                   B=B or 4000)
