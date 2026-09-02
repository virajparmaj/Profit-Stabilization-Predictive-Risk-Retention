import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *
from util import CACHE; from prep import prep, boot_stat
d=prep()
oof=pd.read_parquet(os.path.join(CACHE,'oof.parquet'))
d=d.merge(oof,on='DUPERSID')
w=d.PERWT23F.values
def prof(g,name):
    x=g.TOTEXP23.values; ww=g.PERWT23F.values
    m=wmean(x,ww); med=wq(x,ww,[.5])[0]
    cv=np.sqrt(np.average((x-m)**2,weights=ww))/m
    print(f"{name:<34} n={len(g):>5} med=${med:>6.0f} mean=${m:>6.0f} mean/med={m/max(med,1):5.1f} CV={cv:4.2f} gini={gini(x,ww):.3f} top1%={100*top_share(x,ww,.01):4.1f}% top5%={100*top_share(x,ww,.05):4.1f}% cat20={100*ww[x>=20000].sum()/ww.sum():4.1f}% E[>20k]/E[X]={100*wmean(np.maximum(x-20000,0),ww)/m:4.1f}%")
print("=== I6: DOES SELECTION REDUCE VOLATILITY? ===")
prof(d,'Whole population')
for k in [0.3,0.2,0.1]:
    thr=np.quantile(d.P_OOF,1-k); prof(d[d.P_OOF>=thr], f'Model top-{k*100:.0f}% predicted low-risk')
prof(d[d.LOW_RISK==1],'Actual LOW_RISK label (by construction)')
print("\n=== I5: DISENGAGED CHRONIC, final ===")
dis=d[(d.CHRONIC_CT>=3)&(d.OBTOTV23==0)]; eng=d[(d.CHRONIC_CT>=3)&(d.OBTOTV23>=3)]; mid=d[(d.CHRONIC_CT>=3)&(d.OBTOTV23.between(1,2))]
for nm,g in [('>=3 chronic, 0 office visits',dis),('>=3 chronic, 1-2 visits',mid),('>=3 chronic, 3+ visits',eng)]:
    prof(g,nm)
    ww=g.PERWT23F
    print(f"      acute$share={100*(g.ERTEXP23+g.IPTEXP23).mul(ww).sum()/(g.TOTEXP23*ww).sum():.1f}%  ER-any={100*ww[g.ERTOT23>0].sum()/ww.sum():.1f}%  IP-any={100*ww[g.IPDIS23>0].sum()/ww.sum():.1f}%  noUSC={100*ww[g.NO_USUAL_SOURCE==1].sum()/ww.sum():.1f}%  uninsured={100*ww[g.INSCOV23==3].sum()/ww.sum():.1f}%  popM={ww.sum()/1e6:.1f}  labeled LOW_RISK={100*ww[g.LOW_RISK==1].sum()/ww.sum():.1f}%")
ci=boot_stat(dis, lambda X,W: 100*W[X>=20000].sum()/W.sum()); print("  disengaged cat20 95%% CI: [%.1f, %.1f]"%tuple(ci))
print("\n=== I3: key cell pairs ===")
pairs=[(( d.CHRONIC_CT<=1)&(d.LIMIT_CT>=2),'<=1 chronic + 2+ limitations'),
       ((d.CHRONIC_CT.between(4,5))&(d.LIMIT_CT==0),'4-5 chronic + 0 limitations'),
       ((d.CHRONIC_CT==2)&(d.LIMIT_CT>=2),'2 chronic + 2+ limitations'),
       ((d.CHRONIC_CT>=6)&(d.LIMIT_CT==0),'6+ chronic + 0 limitations')]
for m,nm in pairs: prof(d[m],nm)
print("\n=== I2: income decomposition, insured <65 ===")
sub=d[(d.INSCOV23!=3)&(d.AGELAST<65)]
for lvl,g in sub.groupby('POV',observed=True):
    x=g.TOTEXP23.values; ww=g.PERWT23F.values
    print(f"{str(lvl):<15} n={len(g):>5} med=${wq(x,ww,[.5])[0]:>6.0f} routine(<=5k)=${wmean(np.minimum(x,5000),ww):>5.0f} excess(>5k)=${wmean(np.maximum(x-5000,0),ww):>5.0f} mean=${wmean(x,ww):>5.0f} cat20={100*ww[x>=20000].sum()/ww.sum():4.1f}%")
print("\n=== I1: headline ===")
x=d.TOTEXP23.values
print("wtd mean $%.0f median $%.0f ; %% below mean %.1f%%"%(wmean(x,w),wq(x,w,[.5])[0],100*w[x<wmean(x,w)].sum()/w.sum()))
for f in [.01,.05,.10]: print(f"top {f*100:.0f}% -> {100*top_share(x,w,f):.1f}%")
print("bottom 50%% -> %.1f%%"%(100*(1-top_share(x,w,.5))))
