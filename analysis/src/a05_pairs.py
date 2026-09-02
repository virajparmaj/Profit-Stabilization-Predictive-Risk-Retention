import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, boot_stat
d=prep()
print("=== A. NEAR-POOR vs HIGH-INCOME (insured only, adults) ===")
for label,sub in [('ALL', d), ('Insured only', d[d.INSCOV23!=3]), ('Insured, age<65', d[(d.INSCOV23!=3)&(d.AGELAST<65)])]:
    print(f"\n-- {label} --")
    for lvl,g in sub.groupby('POV', observed=True):
        x=g.TOTEXP23.values; w=g.PERWT23F.values
        med=wq(x,w,[.5])[0]; cat20=100*w[x>=20000].sum()/w.sum(); mean=wmean(x,w)
        ci=boot_stat(g, lambda X,W: 100*W[X>=20000].sum()/W.sum())
        cim=boot_stat(g, lambda X,W: wq(X,W,[.5])[0])
        print(f"{lvl:<15} n={len(g):>5} median=${med:>7.0f} [{cim[0]:.0f},{cim[1]:.0f}]  mean=${mean:>7.0f}  cat20={cat20:5.1f}% [{ci[0]:.1f},{ci[1]:.1f}]  mean/med={mean/max(med,1):5.1f}")
print("\n=== B. AGE 0-17 vs 18-29 ===")
for lvl,g in d[d.AGEBAND.isin(['0-17','18-29','30-44'])].groupby('AGEBAND',observed=True):
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    med=wq(x,w,[.5])[0]; mean=wmean(x,w); cat20=100*w[x>=20000].sum()/w.sum(); cat50=100*w[x>=50000].sum()/w.sum()
    ci=boot_stat(g, lambda X,W: 100*W[X>=20000].sum()/W.sum())
    print(f"{lvl:<8} n={len(g):>5} median=${med:>7.0f} mean=${mean:>7.0f} cat20={cat20:5.2f}% [{ci[0]:.2f},{ci[1]:.2f}] cat50={cat50:4.2f}% top5share={100*top_share(x,w,.05):.1f}%")
print("\n=== C. PRIVATE vs PUBLIC-ONLY, age stratified ===")
for ab,gg in d[d.INSCOV23!=3].groupby('AGEBAND',observed=True):
    row=[]
    for lvl,g in gg.groupby('INS',observed=True):
        if len(g)<60: continue
        x=g.TOTEXP23.values; w=g.PERWT23F.values
        row.append(f"{lvl}: n={len(g)} med=${wq(x,w,[.5])[0]:.0f} mean=${wmean(x,w):.0f} cat20={100*w[x>=20000].sum()/w.sum():.1f}%")
    print(f"{ab:<8} | " + "  ||  ".join(row))
