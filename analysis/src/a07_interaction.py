import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, boot_stat
import statsmodels.api as sm
d=prep()
print("=== CAT20 RATE (%) BY CHRONIC x LIMIT (weighted) ; cells with n>=40 ===")
for m,name in [(lambda g: 100*g.PERWT23F[g.TOTEXP23>=20000].sum()/g.PERWT23F.sum(),'cat20%'),
               (lambda g: wq(g.TOTEXP23.values,g.PERWT23F.values,[.5])[0],'median$'),
               (lambda g: wmean(g.TOTEXP23.values,g.PERWT23F.values),'mean$')]:
    print(f"\n--- {name} ---")
    tab=pd.DataFrame(index=['0','1','2','3','4-5','6+'],columns=['0','1','2+'],dtype=float)
    nt=tab.copy()
    for (c,l),g in d.groupby(['CHRONIC_B','LIMIT_B'],observed=True):
        nt.loc[str(c),str(l)]=len(g)
        if len(g)>=40: tab.loc[str(c),str(l)]=m(g)
    print(tab.round(1).to_string()); print("n:"); print(nt.astype('Int64').to_string())
print("\n=== Does LIMIT add tail risk beyond CHRONIC + AGE? (logit on CAT20) ===")
sub=d.dropna(subset=['CHRONIC_CT','LIMIT_CT','AGELAST']).copy()
sub['y']=(sub.TOTEXP23>=20000).astype(int)
X=pd.DataFrame({'const':1.0,'age':sub.AGELAST/10,'female':(sub.SEXL=='Female').astype(float),
                'chronic':sub.CHRONIC_CT,'limit':sub.LIMIT_CT})
for cols,label in [(['const','age','female','chronic'],'chronic only'),(['const','age','female','chronic','limit'],'chronic+limit')]:
    r=sm.Logit(sub.y, X[cols]).fit(disp=0)
    print(f"\n[{label}] pseudoR2={r.prsquared:.4f}")
    print(pd.DataFrame({'coef':r.params,'OR':np.exp(r.params),'p':r.pvalues,'OR_lo':np.exp(r.conf_int()[0]),'OR_hi':np.exp(r.conf_int()[1])}).round(4).to_string())
print("\n=== Marginal: +1 chronic vs +1 limitation, holding other constant ===")
r=sm.Logit(sub.y, X).fit(disp=0)
print("OR per +1 chronic condition: %.3f ; OR per +1 functional limitation: %.3f"%(np.exp(r.params['chronic']),np.exp(r.params['limit'])))
print("\n=== Same, restricted to LOW chronic burden (<=1) ===")
s2=sub[sub.CHRONIC_CT<=1]
for lvl,g in s2.groupby('LIMIT_B',observed=True):
    if len(g)<30: continue
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    ci=boot_stat(g, lambda X_,W_: 100*W_[X_>=20000].sum()/W_.sum())
    print(f"chronic<=1, limit={lvl}: n={len(g):>5} median=${wq(x,w,[.5])[0]:>6.0f} mean=${wmean(x,w):>7.0f} cat20={100*w[x>=20000].sum()/w.sum():5.1f}% [{ci[0]:.1f},{ci[1]:.1f}]")
