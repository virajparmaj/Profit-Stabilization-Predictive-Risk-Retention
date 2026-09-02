import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, boot_stat
d=prep()
def ci(g): return boot_stat(g, lambda X,W: 100*W[X>=20000].sum()/W.sum(), B=800)
print("=== I3 cell CIs (cat20 %) ===")
cells=[((d.CHRONIC_CT<=1)&(d.LIMIT_CT>=2),'<=1 chronic + 2+ limits'),
 ((d.CHRONIC_CT.between(4,5))&(d.LIMIT_CT==0),'4-5 chronic + 0 limits'),
 ((d.CHRONIC_CT==2)&(d.LIMIT_CT>=2),'2 chronic + 2+ limits'),
 ((d.CHRONIC_CT>=6)&(d.LIMIT_CT==0),'6+ chronic + 0 limits'),
 ((d.CHRONIC_CT==2)&(d.LIMIT_CT==0),'2 chronic + 0 limits')]
for m,nm in cells:
    g=d[m]; x=g.TOTEXP23.values; w=g.PERWT23F.values
    lo,hi=ci(g)
    print(f"{nm:<26} n={len(g):>5} median=${wq(x,w,[.5])[0]:>7.0f} cat20={100*w[x>=20000].sum()/w.sum():5.1f}% [{lo:.1f},{hi:.1f}]")
print("\n=== within-chronic-band effect of 2+ limitations ===")
for lo_,hi_,lab in [(1,1,'1'),(2,2,'2'),(3,3,'3'),(4,5,'4-5'),(6,12,'6+')]:
    b=d[d.CHRONIC_CT.between(lo_,hi_)]
    a=b[b.LIMIT_CT==0]; c=b[b.LIMIT_CT>=2]
    if len(c)<40: continue
    ra=100*a.PERWT23F[a.TOTEXP23>=20000].sum()/a.PERWT23F.sum(); rc=100*c.PERWT23F[c.TOTEXP23>=20000].sum()/c.PERWT23F.sum()
    ma=wq(a.TOTEXP23.values,a.PERWT23F.values,[.5])[0]; mc=wq(c.TOTEXP23.values,c.PERWT23F.values,[.5])[0]
    print(f"chronic={lab:<4} 0 limits: n={len(a):>5} med=${ma:>7.0f} cat20={ra:5.1f}%   |  2+ limits: n={len(c):>4} med=${mc:>7.0f} cat20={rc:5.1f}%   ratio cat20={rc/ra:.2f}x  ratio median={mc/ma:.2f}x")
print("\n=== I2 CIs ===")
sub=d[(d.INSCOV23!=3)&(d.AGELAST<65)]
for nm,g in [('Poor+Near poor',sub[sub.POV.isin(['Poor/negative','Near poor'])]),('High income',sub[sub.POV=='High income'])]:
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    lo,hi=ci(g); mlo,mhi=boot_stat(g,lambda X,W: wq(X,W,[.5])[0],B=800); alo,ahi=boot_stat(g,lambda X,W: wmean(X,W),B=800)
    print(f"{nm:<16} n={len(g):>5} median=${wq(x,w,[.5])[0]:>6.0f} [{mlo:.0f},{mhi:.0f}] mean=${wmean(x,w):>6.0f} [{alo:.0f},{ahi:.0f}] cat20={100*w[x>=20000].sum()/w.sum():.1f}% [{lo:.1f},{hi:.1f}]")
print("\n=== I4 CIs ===")
for nm,g in [('uninsured, >=2 chronic',d[(d.INSCOV23==3)&(d.CHRONIC_CT>=2)]),('insured, >=2 chronic',d[(d.INSCOV23!=3)&(d.CHRONIC_CT>=2)]),
             ('uninsured all',d[d.INSCOV23==3]),('insured all',d[d.INSCOV23!=3])]:
    lo,hi=boot_stat(g, lambda X,W: 0, B=2)  # placeholder
    r=boot_stat(g, lambda X,W: np.nan, B=2)
    # bootstrap P(LOW_RISK)
    rng=np.random.default_rng(1); vals=[]
    lrv=g.LOW_RISK.values; ww=g.PERWT23F.values; n=len(g)
    for b in range(800):
        i=rng.integers(0,n,n); vals.append(100*ww[i][lrv[i]==1].sum()/ww[i].sum())
    print(f"{nm:<24} n={len(g):>5} P(LOW_RISK)={100*ww[lrv==1].sum()/ww.sum():5.1f}% [{np.percentile(vals,2.5):.1f},{np.percentile(vals,97.5):.1f}]")
