import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, boot_stat
d=prep()
def decomp(g, T=5000):
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    routine=np.minimum(x,T); excess=np.maximum(x-T,0)
    return wmean(routine,w), wmean(excess,w), wmean(x,w), wq(x,w,[.5])[0], 100*w[x>=20000].sum()/w.sum()
print("=== ROUTINE (first $5k) vs CATASTROPHIC (excess >$5k) MEAN SPEND ===")
for dim in ['POV','INS','AGEBAND','RACE','SEXL','CHRONIC_B','LIMIT_B']:
    print(f"\n--- {dim} ---")
    for lvl,g in d.groupby(dim,observed=True):
        if len(g)<60: continue
        r,e,m,md,c = decomp(g)
        print(f"{str(lvl):<15} n={len(g):>5} median=${md:>7.0f}  mean=${m:>7.0f}  routine=${r:>6.0f}  excess=${e:>7.0f}  excess%ofmean={100*e/m:4.1f}%  cat20={c:4.1f}%")
print("\n=== POV, insured age<65 (composition-controlled) ===")
sub=d[(d.INSCOV23!=3)&(d.AGELAST<65)]
for lvl,g in sub.groupby('POV',observed=True):
    r,e,m,md,c=decomp(g)
    print(f"{str(lvl):<15} n={len(g):>5} median=${md:>6.0f} mean=${m:>6.0f} routine=${r:>5.0f} excess=${e:>6.0f} ({100*e/m:.0f}% of mean) cat20={c:.1f}%")
p=sub[sub.POV.isin(['Poor/negative','Near poor'])]; h=sub[sub.POV=='High income']
rp,ep,mp,mdp,cp=decomp(p); rh,eh,mh,mdh,ch=decomp(h)
print(f"\nPoor+Near-poor vs High income (insured, <65):")
print(f"  median gap: ${mdp:.0f} vs ${mdh:.0f}  -> {100*(mdp/mdh-1):+.0f}%")
print(f"  mean   gap: ${mp:.0f} vs ${mh:.0f}  -> {100*(mp/mh-1):+.0f}%")
print(f"  routine gap: ${rp:.0f} vs ${rh:.0f} -> {100*(rp/rh-1):+.0f}%")
print(f"  excess  gap: ${ep:.0f} vs ${eh:.0f} -> {100*(ep/eh-1):+.0f}%")
print(f"  cat20: {cp:.1f}% vs {ch:.1f}%")
