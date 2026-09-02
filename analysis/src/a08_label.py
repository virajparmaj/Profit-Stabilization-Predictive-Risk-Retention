import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, boot_stat
d=prep()
print("LOW_SPEND threshold (p30 unweighted, as built): $%.0f"%pd.read_csv('data_processed/meps_model_ready_2023.csv').TOTEXP23.quantile(.30))
lr=d[d.LOW_RISK==1]; nr=d[d.LOW_RISK==0]
print("LOW_RISK n=%d (%.1f%% unw) weighted %.1f%%"%(len(lr),100*len(lr)/len(d),100*lr.PERWT23F.sum()/d.PERWT23F.sum()))
print("\n=== WHO IS IN THE 'LOW-RISK' COHORT? (weighted %) ===")
def wpct(g,mask): return 100*g.PERWT23F[mask].sum()/g.PERWT23F.sum()
rows=[]
checks={
 'Uninsured all year': lambda g: g.INSCOV23==3,
 'No usual source of care': lambda g: g.NO_USUAL_SOURCE==1,
 'Delayed any care': lambda g: g.DELAY_ANY==1,
 'Could not afford care': lambda g: g.AFFORD_BARRIER==1,
 '>=2 chronic conditions': lambda g: g.CHRONIC_CT>=2,
 '>=3 chronic conditions': lambda g: g.CHRONIC_CT>=3,
 '>=1 functional limitation': lambda g: g.LIMIT_CT>=1,
 'Fair/poor self-rated health': lambda g: g.RTHLTH53.isin([4,5]),
 'Fair/poor mental health': lambda g: g.MNHLTH53.isin([4,5]),
 'Age 55+': lambda g: g.AGELAST>=55,
 'Zero total spend': lambda g: g.TOTEXP23==0,
 'Poor/near-poor': lambda g: g.POVCAT23.isin([0,1]),
}
for k,f in checks.items():
    rows.append(dict(feature=k, low_risk=wpct(lr,f(lr)), rest=wpct(nr,f(nr))))
R=pd.DataFrame(rows); R['ratio']=R.low_risk/R.rest
print(R.round(1).to_string(index=False))
print("\n=== 'QUIET RISK' inside the low-risk cohort ===")
lr2=lr.copy()
lr2['quiet']=((lr2.CHRONIC_CT>=2)|(lr2.LIMIT_CT>=1)|(lr2.RTHLTH53.isin([4,5]))).astype(int)
lr2['access']=((lr2.INSCOV23==3)|(lr2.NO_USUAL_SOURCE==1)|(lr2.DELAY_ANY==1)|(lr2.AFFORD_BARRIER==1)).astype(int)
print("share of LOW_RISK with >=2 chronic OR >=1 limit OR fair/poor health: %.1f%% (weighted)"%wpct(lr2,lr2.quiet==1))
print("share of LOW_RISK with an access barrier (uninsured / no usual source / delayed / unaffordable): %.1f%%"%wpct(lr2,lr2.access==1))
print("share of LOW_RISK that is BOTH: %.1f%%"%wpct(lr2,(lr2.quiet==1)&(lr2.access==1)))
print("share of LOW_RISK that is NEITHER (clean healthy): %.1f%%"%wpct(lr2,(lr2.quiet==0)&(lr2.access==0)))
print("\n=== Same-year mirror: among LOW_SPEND (not requiring 0 ER/IP) ===")
ls=d[d.LOW_SPEND==1]
print("LOW_SPEND n=%d ; of these, %% with >=1 ER visit: %.1f%% ; %% with inpatient: %.1f%%"%(len(ls),wpct(ls,ls.ERTOT23>0),wpct(ls,ls.IPDIS23>0)))
print("\n=== UNINSURED CENSORING ===")
u=d[d.INSCOV23==3]
print("Uninsured: n=%d, weighted %.1f M (%.1f%%)"%(len(u),u.PERWT23F.sum()/1e6,100*u.PERWT23F.sum()/d.PERWT23F.sum()))
print("median spend $%.0f ; %% zero spend %.1f%% ; cat20 %.1f%%"%(wq(u.TOTEXP23.values,u.PERWT23F.values,[.5])[0], wpct(u,u.TOTEXP23==0), wpct(u,u.TOTEXP23>=20000)))
print("uninsured share OF the LOW_RISK cohort: %.1f%% (vs %.1f%% of everyone else)"%(wpct(lr,lr.INSCOV23==3), wpct(nr,nr.INSCOV23==3)))
print("P(classified LOW_RISK | uninsured) = %.1f%% vs P(LOW_RISK | insured) = %.1f%%"%(wpct(u,u.LOW_RISK==1), wpct(d[d.INSCOV23!=3], d[d.INSCOV23!=3].LOW_RISK==1)))
print("\nUninsured with >=2 chronic conditions classified low-risk: %.1f%%"%wpct(u[u.CHRONIC_CT>=2], u[u.CHRONIC_CT>=2].LOW_RISK==1))
print("Insured  with >=2 chronic conditions classified low-risk: %.1f%%"%wpct(d[(d.INSCOV23!=3)&(d.CHRONIC_CT>=2)], d[(d.INSCOV23!=3)&(d.CHRONIC_CT>=2)].LOW_RISK==1))
