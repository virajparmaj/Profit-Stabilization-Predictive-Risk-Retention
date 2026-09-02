import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep
d=prep(); w=d.PERWT23F.values; x=d.TOTEXP23.values
def wp(g,m): return 100*g.PERWT23F[m].sum()/g.PERWT23F.sum()
print("=== WHERE DOES THE TAIL COME FROM? profile of catastrophic spenders ===")
grps={'ALL':d, 'Top 10% (>=$18.3k)':d[d.TOTEXP23>=wq(x,w,[.9])[0]],
      'Top 5% (>=$34.1k)':d[d.TOTEXP23>=wq(x,w,[.95])[0]],
      'Top 1% (>=$93.5k)':d[d.TOTEXP23>=wq(x,w,[.99])[0]]}
rows=[]
for k,g in grps.items():
    rows.append(dict(group=k, n=len(g),
      pop_M=g.PERWT23F.sum()/1e6,
      pct_chronic_le1=wp(g,g.CHRONIC_CT<=1),
      pct_lowburden=wp(g,(g.CHRONIC_CT<=1)&(g.LIMIT_CT==0)),
      pct_lowburden_and_good_health=wp(g,(g.CHRONIC_CT<=1)&(g.LIMIT_CT==0)&(g.RTHLTH53.isin([1,2,3]))),
      pct_under45=wp(g,g.AGELAST<45),
      pct_excellent_vg_health=wp(g,g.RTHLTH53.isin([1,2])),
      pct_any_IP=wp(g,g.IPDIS23>0), pct_any_ER=wp(g,g.ERTOT23>0)))
print(pd.DataFrame(rows).round(1).to_string(index=False))
print("\n=== ABSOLUTE COUNT/POPULATION OF 'LOOKS HEALTHY BUT CATASTROPHIC' ===")
lb = d[(d.CHRONIC_CT<=1)&(d.LIMIT_CT==0)]
print("low-burden pool: n=%d, %.1f M people (%.1f%% of population)"%(len(lb), lb.PERWT23F.sum()/1e6, 100*lb.PERWT23F.sum()/w.sum()))
print(" of low-burden pool: cat20 rate %.2f%%, cat50 %.2f%%, median $%.0f, mean $%.0f"%(
  wp(lb,lb.TOTEXP23>=20000), wp(lb,lb.TOTEXP23>=50000), wq(lb.TOTEXP23.values,lb.PERWT23F.values,[.5])[0], wmean(lb.TOTEXP23.values,lb.PERWT23F.values)))
print(" low-burden members with >=$20k: %.1f M people = %.1f%% of ALL $20k+ members"%(
  lb.PERWT23F[lb.TOTEXP23>=20000].sum()/1e6, 100*lb.PERWT23F[lb.TOTEXP23>=20000].sum()/d.PERWT23F[d.TOTEXP23>=20000].sum()))
print(" their share of total national spend: %.1f%%"%(100*(lb.TOTEXP23*lb.PERWT23F).sum()/(d.TOTEXP23*w).sum()))
print(" share of the low-burden pool's OWN total spend held by its top 5%%: %.1f%%"%(100*top_share(lb.TOTEXP23.values,lb.PERWT23F.values,0.05)))
print("\n=== EXPECTED-COST DECOMPOSITION FOR THE LOW-BURDEN POOL ===")
for name,g in [('Low-burden (<=1 chronic, 0 limits)',lb), ('High-burden (>=4 chronic or >=2 limits)', d[(d.CHRONIC_CT>=4)|(d.LIMIT_CT>=2)])]:
    xx=g.TOTEXP23.values; ww=g.PERWT23F.values; m=wmean(xx,ww)
    for T in [5000,20000]:
        share=100*wmean(np.maximum(xx-T,0),ww)/m
        print(f"  {name}: mean ${m:.0f}; {share:.1f}% of expected cost is spend above ${T:,}")
print("\n=== PANEL 27 vs 28 (survey-tenure composition check) ===")
for p,g in d.groupby('PANEL'):
    print(f"panel {p}: n={len(g)} mean chronic {g.CHRONIC_CT.mean():.2f}, mean limit {g.LIMIT_CT.mean():.2f}, median spend ${wq(g.TOTEXP23.values,g.PERWT23F.values,[.5])[0]:.0f}, mean ${wmean(g.TOTEXP23.values,g.PERWT23F.values):.0f}, cat20 {wp(g,g.TOTEXP23>=20000):.1f}%, mean age {g.AGELAST.mean():.1f}")
