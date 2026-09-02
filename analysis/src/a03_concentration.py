import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *
df=load()
print("zero weight rows:", (df.PERWT23F<=0).sum(), " pos weight:", (df.PERWT23F>0).sum())
d=df[df.PERWT23F>0].copy()
x=d.TOTEXP23.values; w=d.PERWT23F.values
print("represented population: %.1f M" % (w.sum()/1e6))
print("\n=== UNWEIGHTED vs WEIGHTED ===")
qs=[.1,.25,.5,.75,.9,.95,.99,.999]
print("unw pct:", dict(zip(qs, np.round(np.quantile(df.TOTEXP23,qs),0))))
print("wtd pct:", dict(zip(qs, np.round(wq(x,w,qs),0))))
print("unw mean %.0f  wtd mean %.0f"%(df.TOTEXP23.mean(), wmean(x,w)))
mean_w=wmean(x,w)
# percentile rank of the mean
pr = np.sum(w[x<mean_w])/w.sum()
print("weighted %% of people below the MEAN: %.1f%%"%(100*pr))
print("mean/median ratio: %.2f"%(mean_w/wq(x,w,[.5])[0]))
print("\n=== CONCENTRATION (weighted) ===")
for f in [0.001,0.01,0.05,0.10,0.20,0.50]:
    print(f"top {f*100:>5.1f}% of people -> {100*top_share(x,w,f):5.1f}% of spend")
print("bottom 50%% -> %.1f%% of spend"%(100*(1-top_share(x,w,0.5))))
print("Gini (weighted): %.3f"%gini(x,w))
print("Gini (unweighted): %.3f"%gini(df.TOTEXP23.values, np.ones(len(df))))
print("\nzero-spend share (wtd): %.1f%%"%(100*w[x==0].sum()/w.sum()))
print("<$500 share (wtd): %.1f%%"%(100*w[x<500].sum()/w.sum()))
print("\n=== SERVICE-LINE DECOMPOSITION OF THE TAIL (weighted $) ===")
lines={'Inpatient':'IPTEXP23','Rx':'RXEXP23','Office-based':'OBVEXP23','Outpatient':'OPTEXP23','ER':'ERTEXP23','Dental':'DVTEXP23','Home health':'HHAEXP23'}
thr=wq(x,w,[0.99])[0]
top1 = d[d.TOTEXP23>=thr]; rest=d[d.TOTEXP23<thr]
print("top1%% threshold $%.0f"%thr)
tot_all=(d.TOTEXP23*d.PERWT23F).sum()
for k,v in lines.items():
    a=(top1[v]*top1.PERWT23F).sum(); b=(rest[v]*rest.PERWT23F).sum()
    print(f"{k:<14} top1%: ${a/1e9:6.1f}B ({100*a/tot_all:4.1f}% of ALL spend)   rest: ${b/1e9:6.1f}B")
print("\n=== WHO PAYS THE TAIL ===")
pay={'Out-of-pocket':'TOTSLF23','Medicare':'TOTMCR23','Medicaid':'TOTMCD23','Private':'TOTPRV23','Other':'TOTOTH23','VA':'TOTVA23'}
for grp,sub in [('top 1%',top1),('bottom 99%',rest)]:
    tt=(sub.TOTEXP23*sub.PERWT23F).sum()
    print(grp, {k: round(100*(sub[v]*sub.PERWT23F).sum()/tt,1) for k,v in pay.items()})
