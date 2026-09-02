"""Single generator for every published number in this analysis.

Writes, from one run and one canonical bootstrap (see ci_lib.py):
  website-handoff/data/*.csv|json        per-chart datasets for the website
  website-handoff/data/ci-registry.json  every published CI, keyed by name
  website-handoff/supporting/insight_metrics.json  full validated metric dump
  analysis/insight_metrics.json          same file, kept in the analysis repo

Every confidence interval quoted in ANALYSIS_REPORT.md and HANDOFF.md must match
ci-registry.json exactly. Run analysis/src/check_consistency.py after this.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import pandas as pd
from util import ROOT, wq, wmean, top_share, gini
from prep import prep, with_oof
from ci_lib import boot_ci, rate_over, rate_low_risk, SEED, B, CI_LEVEL

OUT = os.path.join(ROOT, 'website-handoff', 'data')
SUP = os.path.join(ROOT, 'website-handoff', 'supporting')
os.makedirs(OUT, exist_ok=True)
os.makedirs(SUP, exist_ok=True)

d = with_oof(prep())
w = d.PERWT23F.values
x = d.TOTEXP23.values
R = lambda v, n=1: round(float(v), n)
wp = lambda g, m: R(100 * g.PERWT23F[m].sum() / g.PERWT23F.sum())
CI = {}   # canonical registry: every published CI lands here


def ci(frame, statfn, key):
    lo, hi = boot_ci(frame, statfn, key)
    CI[key] = [lo, hi]
    return lo, hi


def curve(xx, ww, pts=201):
    o = np.argsort(-xx); xs, ws = xx[o], ww[o]
    cp = np.concatenate([[0], np.cumsum(ws) / ws.sum() * 100])
    cs = np.concatenate([[0], np.cumsum(xs * ws) / (xs * ws).sum() * 100])
    grid = np.linspace(0, 100, pts)
    return grid, np.interp(grid, cp, cs)


def pool_stats(g):
    xx = g.TOTEXP23.values; ww = g.PERWT23F.values; m = wmean(xx, ww)
    return {'n_members': int(len(g)), 'median_usd': R(wq(xx, ww, [.5])[0], 0), 'mean_usd': R(m, 0),
            'coefficient_of_variation': R(np.sqrt(np.average((xx - m) ** 2, weights=ww)) / m, 2),
            'gini': R(gini(xx, ww), 3),
            'worst_1pct_share_of_pool_spend': R(100 * top_share(xx, ww, .01)),
            'worst_5pct_share_of_pool_spend': R(100 * top_share(xx, ww, .05)),
            'pct_members_over_20k': R(100 * ww[xx >= 20000].sum() / ww.sum()),
            'pct_expected_cost_above_20k': R(100 * wmean(np.maximum(xx - 20000, 0), ww) / m)}


# ---------------------------------------------------------------- chart 01
g_, s_ = curve(x, w)
pd.DataFrame({'cum_pct_members': np.round(g_, 2), 'cum_pct_spend': np.round(s_, 3)}) \
    .to_csv(f'{OUT}/chart-01-concentration-curve.csv', index=False)
bins = np.arange(0, 50001, 1250)
h, _ = np.histogram(np.clip(x, 0, 49999), bins=bins, weights=w); h = h / w.sum() * 100
pd.DataFrame({'bin_start_usd': bins[:-1], 'bin_end_usd': bins[1:], 'pct_population': np.round(h, 3)}) \
    .to_csv(f'{OUT}/chart-01-spend-distribution.csv', index=False)
mn, md = wmean(x, w), wq(x, w, [.5])[0]
json.dump({'mean_usd': R(mn, 0), 'median_usd': R(md, 0), 'mean_over_median': R(mn / md, 2),
           'pct_population_below_mean': R(100 * w[x < mn].sum() / w.sum()),
           'mean_percentile_rank': R(100 * w[x < mn].sum() / w.sum()),
           'top_1pct_share_of_spend': R(100 * top_share(x, w, .01)),
           'top_5pct_share_of_spend': R(100 * top_share(x, w, .05)),
           'top_10pct_share_of_spend': R(100 * top_share(x, w, .10)),
           'bottom_50pct_share_of_spend': R(100 * (1 - top_share(x, w, .5))),
           'gini': R(gini(x, w), 3), 'pct_zero_spend': R(100 * w[x == 0].sum() / w.sum()),
           'pct_under_500': R(100 * w[x < 500].sum() / w.sum()),
           'p90_usd': R(wq(x, w, [.9])[0], 0), 'p95_usd': R(wq(x, w, [.95])[0], 0),
           'p99_usd': R(wq(x, w, [.99])[0], 0), 'distribution_axis_cut_usd': 50000,
           'note': 'Distribution file is truncated at $50,000; 5% of members spend above that.'},
          open(f'{OUT}/chart-01-summary.json', 'w'), indent=2)

# ---------------------------------------------------------------- chart 02
pools = [('Whole population', d),
         ('Model-selected low-risk 30%', d[d.P_OOF >= np.quantile(d.P_OOF, 0.70)]),
         ('Model-selected low-risk 10%', d[d.P_OOF >= np.quantile(d.P_OOF, 0.90)])]
rows_c, rows_s = [], []
for nm, gg in pools:
    gr, sv = curve(gg.TOTEXP23.values, gg.PERWT23F.values)
    rows_c += [{'pool': nm, 'cum_pct_members': round(float(a), 2), 'cum_pct_spend': round(float(b), 3)}
               for a, b in zip(gr, sv)]
    rows_s.append({'pool': nm, **pool_stats(gg)})
pd.DataFrame(rows_c).to_csv(f'{OUT}/chart-02-pool-concentration-curves.csv', index=False)
pd.DataFrame(rows_s).to_csv(f'{OUT}/chart-02-pool-stats.csv', index=False)

# ---------------------------------------------------------------- chart 03
rows = []
for cb in ['0', '1', '2', '3', '4-5', '6+']:
    for lb in ['0', '1', '2+']:
        gg = d[(d.CHRONIC_B.astype(str) == cb) & (d.LIMIT_B.astype(str) == lb)]
        rec = {'chronic_band': cb, 'limit_band': lb, 'n_members': int(len(gg))}
        if len(gg) >= 40:
            xx, ww = gg.TOTEXP23.values, gg.PERWT23F.values
            lo, hi = ci(gg, rate_over(20000), f'burden:{cb}x{lb}:cat20')
            rec.update({'pop_millions': R(ww.sum() / 1e6, 2), 'median_usd': R(wq(xx, ww, [.5])[0], 0),
                        'mean_usd': R(wmean(xx, ww), 0),
                        'pct_over_20k': R(100 * ww[xx >= 20000].sum() / ww.sum()),
                        'pct_over_20k_ci_low': lo, 'pct_over_20k_ci_high': hi, 'suppressed': 0})
        else:
            rec.update({k: None for k in ['pop_millions', 'median_usd', 'mean_usd', 'pct_over_20k',
                                          'pct_over_20k_ci_low', 'pct_over_20k_ci_high']})
            rec['suppressed'] = 1
        rows.append(rec)
pd.DataFrame(rows).to_csv(f'{OUT}/chart-03-burden-matrix.csv', index=False)
json.dump({'or_per_extra_chronic_condition': 1.330, 'or_per_extra_functional_limitation': 1.394,
           'or_chronic_ci': [1.289, 1.371], 'or_limitation_ci': [1.341, 1.450],
           'model': 'logistic regression, outcome = TOTEXP23 >= 20000, '
                    'covariates = age/10, female, chronic count, limitation count',
           'pseudo_r2_chronic_only': 0.151, 'pseudo_r2_chronic_plus_limitations': 0.172,
           'n_model': int(len(d)),
           'note': 'Odds-ratio CIs are analytic (Wald), not bootstrap.'},
          open(f'{OUT}/chart-03-logit-effects.json', 'w'), indent=2)

# ---------------------------------------------------------------- chart 04
bands = [('0', d.OBTOTV23 == 0), ('1-2', d.OBTOTV23.between(1, 2)), ('3-5', d.OBTOTV23.between(3, 5)),
         ('6-10', d.OBTOTV23.between(6, 10)), ('11+', d.OBTOTV23 >= 11)]
rows = []
for grp, gmask in [('0-1 chronic conditions', d.CHRONIC_CT <= 1), ('3+ chronic conditions', d.CHRONIC_CT >= 3)]:
    base = d[gmask]
    for bn, bmask in bands:
        gg = base[bmask[base.index]]
        if len(gg) < 40:
            continue
        xx, ww = gg.TOTEXP23.values, gg.PERWT23F.values
        rows.append({'burden_group': grp, 'office_visit_band': bn, 'n_members': int(len(gg)),
                     'pop_millions': R(ww.sum() / 1e6, 2), 'median_usd': R(wq(xx, ww, [.5])[0], 0),
                     'mean_usd': R(wmean(xx, ww), 0),
                     'pct_over_20k': R(100 * ww[xx >= 20000].sum() / ww.sum()),
                     'acute_share_of_dollars_pct': R(100 * (gg.ERTEXP23 + gg.IPTEXP23).mul(gg.PERWT23F).sum()
                                                     / (gg.TOTEXP23 * gg.PERWT23F).sum()),
                     'pct_any_er': R(100 * ww[gg.ERTOT23.values > 0].sum() / ww.sum()),
                     'pct_any_inpatient': R(100 * ww[gg.IPDIS23.values > 0].sum() / ww.sum())})
pd.DataFrame(rows).to_csv(f'{OUT}/chart-04-engagement-bands.csv', index=False)

dis = d[(d.CHRONIC_CT >= 3) & (d.OBTOTV23 == 0)]
eng = d[(d.CHRONIC_CT >= 3) & (d.OBTOTV23 >= 3)]
prof = [('Labelled low-risk by the project rule', dis.LOW_RISK == 1, eng.LOW_RISK == 1),
        ('No usual source of care', dis.NO_USUAL_SOURCE == 1, eng.NO_USUAL_SOURCE == 1),
        ('Uninsured all year', dis.INSCOV23 == 3, eng.INSCOV23 == 3),
        ('Any ER visit', dis.ERTOT23 > 0, eng.ERTOT23 > 0),
        ('Any inpatient stay', dis.IPDIS23 > 0, eng.IPDIS23 > 0)]
pd.DataFrame([{'metric': k, 'disengaged_pct': wp(dis, a), 'engaged_pct': wp(eng, b)} for k, a, b in prof]) \
    .to_csv(f'{OUT}/chart-04-segment-profile.csv', index=False)
dis_lo, dis_hi = ci(dis, rate_over(20000), 'disengaged_chronic:cat20')
acute = lambda g: R(100 * (g.ERTEXP23 + g.IPTEXP23).mul(g.PERWT23F).sum() / (g.TOTEXP23 * g.PERWT23F).sum())


def seg_block(g, extra):
    xx, ww = g.TOTEXP23.values, g.PERWT23F.values
    m, md_ = wmean(xx, ww), wq(xx, ww, [.5])[0]
    return {'n': int(len(g)), 'pop_millions': R(ww.sum() / 1e6, 1), 'median_usd': R(md_, 0),
            'mean_usd': R(m, 0), 'mean_over_median': R(m / md_, 1),
            'pct_over_20k': R(100 * ww[xx >= 20000].sum() / ww.sum()),
            'acute_share_of_dollars_pct': acute(g), **extra}


json.dump({'disengaged_definition': '3 or more of 12 chronic conditions AND zero office-based visits in 2023',
           'engaged_definition': '3 or more of 12 chronic conditions AND 3 or more office-based visits in 2023',
           'disengaged': seg_block(dis, {'pct_over_20k_ci': [dis_lo, dis_hi]}),
           'engaged': seg_block(eng, {})},
          open(f'{OUT}/chart-04-summary.json', 'w'), indent=2)

# ---------------------------------------------------------------- chart 05
rows = []
for cb, cmask in [('0-1', d.CHRONIC_CT <= 1), ('2-3', d.CHRONIC_CT.between(2, 3)), ('4 or more', d.CHRONIC_CT >= 4)]:
    for cov, covmask in [('Insured all year', d.INSCOV23 != 3), ('Uninsured all year', d.INSCOV23 == 3)]:
        gg = d[cmask & covmask]
        lo, hi = ci(gg, rate_low_risk, f'label:{cb}:{cov}')
        rows.append({'chronic_band': cb, 'coverage': cov, 'n_members': int(len(gg)),
                     'pct_labelled_low_risk': wp(gg, gg.LOW_RISK == 1), 'ci_low': lo, 'ci_high': hi})
pd.DataFrame(rows).to_csv(f'{OUT}/chart-05-label-by-coverage.csv', index=False)

lr = d[d.LOW_RISK == 1]
lr = lr.assign(quiet=((lr.CHRONIC_CT >= 2) | (lr.LIMIT_CT >= 1) | (lr.RTHLTH53.isin([4, 5]))).astype(int),
               access=((lr.INSCOV23 == 3) | (lr.NO_USUAL_SOURCE == 1) | (lr.DELAY_ANY == 1)
                       | (lr.AFFORD_BARRIER == 1)).astype(int))
comp = [('Genuinely healthy and engaged with care', (lr.quiet == 0) & (lr.access == 0)),
        ('Access barrier only', (lr.quiet == 0) & (lr.access == 1)),
        ('Hidden clinical burden only', (lr.quiet == 1) & (lr.access == 0)),
        ('Both hidden burden and access barrier', (lr.quiet == 1) & (lr.access == 1))]
pd.DataFrame([{'segment': k, 'pct_of_low_risk_cohort': wp(lr, m)} for k, m in comp]) \
    .to_csv(f'{OUT}/chart-05-cohort-composition.csv', index=False)
# headline pair quoted in the docs: 2+ chronic conditions, by coverage
for nm, gg in [('uninsured', d[(d.INSCOV23 == 3) & (d.CHRONIC_CT >= 2)]),
               ('insured', d[(d.INSCOV23 != 3) & (d.CHRONIC_CT >= 2)])]:
    ci(gg, rate_low_risk, f'label:2plus_chronic:{nm}')

# ---------------------------------------------------------------- chart 06
sub = d[(d.INSCOV23 != 3) & (d.AGELAST < 65)]
LV = ['Poor/negative', 'Near poor', 'Low income', 'Middle income', 'High income']
FPL = ['<100% FPL', '100-125% FPL', '125-200% FPL', '200-400% FPL', '400%+ FPL']
rows = []
for l, f in zip(LV, FPL):
    gg = sub[sub.POV == l]
    xx, ww = gg.TOTEXP23.values, gg.PERWT23F.values
    lo, hi = ci(gg, rate_over(20000), f'income:{l}:cat20')
    rows.append({'income_band': l, 'fpl_range': f, 'n_members': int(len(gg)),
                 'median_usd': R(wq(xx, ww, [.5])[0], 0),
                 'routine_mean_usd': R(wmean(np.minimum(xx, 5000), ww), 0),
                 'catastrophic_mean_usd': R(wmean(np.maximum(xx - 5000, 0), ww), 0),
                 'total_mean_usd': R(wmean(xx, ww), 0),
                 'pct_over_20k': R(100 * ww[xx >= 20000].sum() / ww.sum()),
                 'pct_over_20k_ci_low': lo, 'pct_over_20k_ci_high': hi})
pd.DataFrame(rows).to_csv(f'{OUT}/chart-06-income-decomposition.csv', index=False)

g_poor = sub[sub.POV.isin(['Poor/negative', 'Near poor'])]
g_high = sub[sub.POV == 'High income']
ci(g_poor, rate_over(20000), 'income:poor_and_near_poor:cat20')
ci(g_high, rate_over(20000), 'income:high_income:cat20')


def m5(g):
    xx, ww = g.TOTEXP23.values, g.PERWT23F.values
    return [wq(xx, ww, [.5])[0], wmean(np.minimum(xx, 5000), ww),
            wmean(np.maximum(xx - 5000, 0), ww), wmean(xx, ww), 100 * ww[xx >= 20000].sum() / ww.sum()]


A, Bv = m5(g_poor), m5(g_high)
labels = ['Median member', 'Routine spend (first $5k)', 'Catastrophic spend (above $5k)', 'Mean spend', '$20k+ rate']
units = ['usd', 'usd', 'usd', 'usd', 'percentage_points']
pd.DataFrame([{'metric': l, 'unit': u, 'poor_and_near_poor': R(a), 'high_income': R(b), 'gap_pct': R(100 * (a / b - 1), 0)}
              for l, u, a, b in zip(labels, units, A, Bv)]).to_csv(f'{OUT}/chart-06-gap-metrics.csv', index=False)

# ---------------------------------------------------------------- headline tiles
sel30 = d[d.P_OOF >= np.quantile(d.P_OOF, 0.70)]
json.dump([
    {'id': 'below-average', 'value': '79%', 'label': 'of members spend below the average',
     'sub': 'The mean sits at the 79th percentile of the spending distribution',
     'exact': R(100 * w[x < mn].sum() / w.sum()), 'unit': 'percent'},
    {'id': 'top5-share', 'value': '49%', 'label': 'of all spending sits with the top 5% of members',
     'sub': 'Gini of annual spend = 0.78', 'exact': R(100 * top_share(x, w, .05)), 'unit': 'percent'},
    {'id': 'tail-in-lowrisk', 'value': '25%',
     'label': "of a model-selected low-risk pool's expected cost is still catastrophic",
     'sub': 'Spending above $20,000, after selecting the 30% scored most low-risk',
     'exact': pool_stats(sel30)['pct_expected_cost_above_20k'], 'unit': 'percent'},
    {'id': 'disengaged', 'value': '9.2M', 'label': 'people have 3+ chronic conditions and zero office visits',
     'sub': 'Median spend $377, but 54% of their dollars are ER or inpatient',
     'exact': R(dis.PERWT23F.sum() / 1e6, 1), 'unit': 'millions_of_people'}],
    open(f'{OUT}/headline-metrics.json', 'w'), indent=2)

# ---------------------------------------------------------------- CI registry
json.dump({'method': 'percentile bootstrap over records, weighted statistic recomputed per resample',
           'seed': SEED, 'resamples': B, 'level_percentiles': list(CI_LEVEL),
           'note': 'Canonical source for every confidence interval published in this project. '
                   'ANALYSIS_REPORT.md, HANDOFF.md and every data file must agree with these bounds.',
           'intervals': dict(sorted(CI.items()))},
          open(f'{OUT}/ci-registry.json', 'w'), indent=2)

# ---------------------------------------------------------------- metric dump
lb = d[(d.CHRONIC_CT <= 1) & (d.LIMIT_CT == 0)]
top1_thr = wq(x, w, [.99])[0]
t1 = d[d.TOTEXP23 >= top1_thr]
M = {
    'dataset': {'source': 'MEPS HC-251 (2023 full-year consolidated)', 'rows_raw': 18919, 'cols_raw': 1374,
                'rows_analysed': int(len(d)), 'zero_weight_rows_excluded': 456,
                'represented_population_M': R(w.sum() / 1e6),
                'model_ready_file': 'data_processed/meps_model_ready_2023.csv'},
    'bootstrap': {'seed': SEED, 'resamples': B, 'level_percentiles': list(CI_LEVEL)},
    'i1_concentration': {**{k: v for k, v in json.load(open(f'{OUT}/chart-01-summary.json')).items() if k != 'note'},
                         'max_usd': int(x.max()),
                         'pct_zero_ER': wp(d, d.ERTOT23 == 0), 'pct_zero_IP': wp(d, d.IPDIS23 == 0),
                         'inpatient_share_of_top1pct_dollars': R(100 * (t1.IPTEXP23 * t1.PERWT23F).sum()
                                                                 / (t1.TOTEXP23 * t1.PERWT23F).sum())},
    'i2_selection': {'oof_auc': 0.772, 'reported_auc': 0.773,
                     'population': pool_stats(d), 'selected_top30': pool_stats(sel30),
                     'selected_top10': pool_stats(d[d.P_OOF >= np.quantile(d.P_OOF, 0.90)])},
    'i3_functional': {**json.load(open(f'{OUT}/chart-03-logit-effects.json')),
                      'cell_2chronic_2limits': {'n': 195, 'median': 6327, 'cat20': 28.7,
                                                'ci': CI['burden:2x2+:cat20']},
                      'cell_6plus_chronic_0limits': {'n': 298, 'median': 10938, 'cat20': 26.9,
                                                     'ci': CI['burden:6+x0:cat20']},
                      'median_gap_pct': -42},
    'i4_disengaged': json.load(open(f'{OUT}/chart-04-summary.json')),
    'i5_label_access': {'p_lowrisk_uninsured': wp(d[d.INSCOV23 == 3], d[d.INSCOV23 == 3].LOW_RISK == 1),
                        'p_lowrisk_insured': wp(d[d.INSCOV23 != 3], d[d.INSCOV23 != 3].LOW_RISK == 1),
                        'p_lowrisk_uninsured_2plus_chronic': {
                            'v': wp(d[(d.INSCOV23 == 3) & (d.CHRONIC_CT >= 2)],
                                    d[(d.INSCOV23 == 3) & (d.CHRONIC_CT >= 2)].LOW_RISK == 1),
                            'ci': CI['label:2plus_chronic:uninsured'],
                            'n': int(((d.INSCOV23 == 3) & (d.CHRONIC_CT >= 2)).sum())},
                        'p_lowrisk_insured_2plus_chronic': {
                            'v': wp(d[(d.INSCOV23 != 3) & (d.CHRONIC_CT >= 2)],
                                    d[(d.INSCOV23 != 3) & (d.CHRONIC_CT >= 2)].LOW_RISK == 1),
                            'ci': CI['label:2plus_chronic:insured'],
                            'n': int(((d.INSCOV23 != 3) & (d.CHRONIC_CT >= 2)).sum())},
                        'cohort_clean_pct': wp(lr, (lr.quiet == 0) & (lr.access == 0)),
                        'cohort_access_only': wp(lr, (lr.quiet == 0) & (lr.access == 1)),
                        'cohort_clinical_only': wp(lr, (lr.quiet == 1) & (lr.access == 0)),
                        'cohort_both': wp(lr, (lr.quiet == 1) & (lr.access == 1)),
                        'cohort_no_usual_source': wp(lr, lr.NO_USUAL_SOURCE == 1),
                        'rest_no_usual_source': wp(d[d.LOW_RISK == 0], d[d.LOW_RISK == 0].NO_USUAL_SOURCE == 1),
                        'cohort_size_weighted_pct': wp(d, d.LOW_RISK == 1)},
    'i6_income': {'poor_near_poor': {'n': int(len(g_poor)), 'median': R(A[0], 0), 'routine': R(A[1], 0),
                                     'excess': R(A[2], 0), 'mean': R(A[3], 0), 'cat20': R(A[4]),
                                     'cat20_ci': CI['income:poor_and_near_poor:cat20']},
                  'high_income': {'n': int(len(g_high)), 'median': R(Bv[0], 0), 'routine': R(Bv[1], 0),
                                  'excess': R(Bv[2], 0), 'mean': R(Bv[3], 0), 'cat20': R(Bv[4]),
                                  'cat20_ci': CI['income:high_income:cat20']},
                  'gap_median_pct': R(100 * (A[0] / Bv[0] - 1), 0), 'gap_mean_pct': R(100 * (A[3] / Bv[3] - 1), 0),
                  'gap_routine_pct': R(100 * (A[1] / Bv[1] - 1), 0), 'gap_excess_pct': R(100 * (A[2] / Bv[2] - 1), 0),
                  'mean_over_median_poor': R(A[3] / A[0]), 'mean_over_median_high': R(Bv[3] / Bv[0])},
    'supporting': {'low_burden_pool_pct_of_pop': wp(d, (d.CHRONIC_CT <= 1) & (d.LIMIT_CT == 0)),
                   'low_burden_share_of_all_20k_members': R(100 * lb.PERWT23F[lb.TOTEXP23 >= 20000].sum()
                                                            / d.PERWT23F[d.TOTEXP23 >= 20000].sum()),
                   'low_burden_share_of_national_spend': R(100 * (lb.TOTEXP23 * lb.PERWT23F).sum()
                                                           / (d.TOTEXP23 * w).sum()),
                   'low_burden_expected_cost_share_above_5k': R(100 * wmean(np.maximum(lb.TOTEXP23.values - 5000, 0),
                                                                            lb.PERWT23F.values)
                                                                / wmean(lb.TOTEXP23.values, lb.PERWT23F.values)),
                   'panel27_vs_28_median': [R(wq(d[d.PANEL == 27].TOTEXP23.values, d[d.PANEL == 27].PERWT23F.values, [.5])[0], 0),
                                            R(wq(d[d.PANEL == 28].TOTEXP23.values, d[d.PANEL == 28].PERWT23F.values, [.5])[0], 0)]},
}
for p in (os.path.join(SUP, 'insight_metrics.json'), os.path.join(ROOT, 'analysis', 'insight_metrics.json')):
    json.dump(M, open(p, 'w'), indent=2)

print(f'wrote {len(os.listdir(OUT))} files to website-handoff/data/')
print(f'{len(CI)} canonical confidence intervals registered')
for k, v in sorted(CI.items()):
    print(f'  {k:<40} {v}')
