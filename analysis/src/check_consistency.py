"""Verify that every published confidence interval agrees across all artifacts.

Compares ci-registry.json (the canonical source) against the CI values embedded
in the per-chart data files, insight_metrics.json, ANALYSIS_REPORT.md and
HANDOFF.md. Exits non-zero on any mismatch. Run after export_web_data.py.
"""
import json
import os
import re
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATA = os.path.join(ROOT, 'website-handoff', 'data')
REG = json.load(open(os.path.join(DATA, 'ci-registry.json')))
I = REG['intervals']
problems = []


def check(label, got, want):
    if [round(float(g), 1) for g in got] != [round(float(w), 1) for w in want]:
        problems.append(f'{label}: found {got}, canonical {want}')


# --- data files -------------------------------------------------------------
m = pd.read_csv(f'{DATA}/chart-03-burden-matrix.csv')
for _, r in m[m.suppressed == 0].iterrows():
    check(f"chart-03 {r.chronic_band}x{r.limit_band}",
          [r.pct_over_20k_ci_low, r.pct_over_20k_ci_high],
          I[f'burden:{r.chronic_band}x{r.limit_band}:cat20'])

s4 = json.load(open(f'{DATA}/chart-04-summary.json'))
check('chart-04 disengaged', s4['disengaged']['pct_over_20k_ci'], I['disengaged_chronic:cat20'])

m5 = pd.read_csv(f'{DATA}/chart-05-label-by-coverage.csv')
for _, r in m5.iterrows():
    check(f'chart-05 {r.chronic_band}/{r.coverage}', [r.ci_low, r.ci_high],
          I[f'label:{r.chronic_band}:{r.coverage}'])

m6 = pd.read_csv(f'{DATA}/chart-06-income-decomposition.csv')
for _, r in m6.iterrows():
    check(f'chart-06 {r.income_band}', [r.pct_over_20k_ci_low, r.pct_over_20k_ci_high],
          I[f'income:{r.income_band}:cat20'])

# --- metric dump ------------------------------------------------------------
for path in [os.path.join(ROOT, 'website-handoff', 'supporting', 'insight_metrics.json'),
             os.path.join(ROOT, 'analysis', 'insight_metrics.json')]:
    M = json.load(open(path))
    tag = os.path.relpath(path, ROOT)
    check(f'{tag} i3 cell 2x2+', M['i3_functional']['cell_2chronic_2limits']['ci'], I['burden:2x2+:cat20'])
    check(f'{tag} i3 cell 6+x0', M['i3_functional']['cell_6plus_chronic_0limits']['ci'], I['burden:6+x0:cat20'])
    check(f'{tag} i4 disengaged', M['i4_disengaged']['disengaged']['pct_over_20k_ci'], I['disengaged_chronic:cat20'])
    check(f'{tag} i5 uninsured', M['i5_label_access']['p_lowrisk_uninsured_2plus_chronic']['ci'],
          I['label:2plus_chronic:uninsured'])
    check(f'{tag} i5 insured', M['i5_label_access']['p_lowrisk_insured_2plus_chronic']['ci'],
          I['label:2plus_chronic:insured'])
    check(f'{tag} i6 poor', M['i6_income']['poor_near_poor']['cat20_ci'], I['income:poor_and_near_poor:cat20'])
    check(f'{tag} i6 high', M['i6_income']['high_income']['cat20_ci'], I['income:high_income:cat20'])

# --- markdown ---------------------------------------------------------------
known = {tuple(v) for v in I.values()}
pat = re.compile(r'\[(\d+\.\d+)[–-](\d+\.\d+)\]')
for md in [os.path.join(ROOT, 'analysis', 'ANALYSIS_REPORT.md'),
           os.path.join(ROOT, 'website-handoff', 'HANDOFF.md')]:
    text = open(md).read()
    for lo, hi in pat.findall(text):
        if (float(lo), float(hi)) not in known:
            problems.append(f'{os.path.relpath(md, ROOT)}: [{lo}–{hi}] is not in ci-registry.json')

if problems:
    print(f'FAIL — {len(problems)} inconsistency(ies):')
    for p in problems:
        print('  -', p)
    sys.exit(1)
print(f'OK — every CI matches ci-registry.json (seed {REG["seed"]}, {REG["resamples"]:,} resamples)')
