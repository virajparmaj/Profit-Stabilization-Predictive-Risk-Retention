import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep
d=prep()
w=d.PERWT23F.values; x=d.TOTEXP23.values
cuts=wq(x,w,[.1*i for i in range(1,10)])
d['SPEND_DEC']=np.digitize(x, cuts)+1
print("=== OOP BY TOTAL-SPEND DECILE (weighted) ===")
rows=[]
for dec,g in d.groupby('SPEND_DEC'):
    ww=g.PERWT23F.values
    tot=wmean(g.TOTEXP23.values,ww); oop=wmean(g.TOTSLF23.values,ww)
    inc=g.FAMINC23.clip(lower=0)
    hb=100*ww[(inc>0)&(g.TOTSLF23/inc.replace(0,np.nan)>0.10)].sum()/ww.sum()
    rows.append(dict(decile=dec, spend_lo=int(g.TOTEXP23.min()), spend_hi=int(g.TOTEXP23.max()),
        mean_total=tot, mean_oop=oop, oop_share_pct=100*oop/max(tot,1),
        share_of_all_spend=100*(g.TOTEXP23*ww).sum()/(d.TOTEXP23*w).sum(),
        share_of_all_oop=100*(g.TOTSLF23*ww).sum()/(d.TOTSLF23*w).sum(),
        pct_oop_gt10pct_income=hb))
R=pd.DataFrame(rows); print(R.round(1).to_string(index=False))
print("\ntop 10%% of spenders: %.1f%% of total spend but %.1f%% of total OOP"%(R.iloc[-1].share_of_all_spend, R.iloc[-1].share_of_all_oop))
print("Gini of TOTAL spend %.3f vs Gini of OOP spend %.3f"%(gini(x,w), gini(d.TOTSLF23.values,w)))
for f in [0.01,0.05,0.10]:
    print(f"top {f*100:.0f}%: {100*top_share(x,w,f):.1f}% of TOTAL spend | {100*top_share(d.TOTSLF23.values,w,f):.1f}% of OOP")
print("\n=== HIGH FINANCIAL BURDEN (OOP > 10% of family income) BY INCOME QUINTILE x SPEND GROUP ===")
inc=d.FAMINC23.clip(lower=0)
d['HB']=((inc>0)&(d.TOTSLF23/inc.replace(0,np.nan)>0.10)).astype(int)
d['SPEND_GRP']=np.where(d.SPEND_DEC>=10,'Top 10% spenders', np.where(d.SPEND_DEC>=8,'Decile 8-9','Bottom 70%'))
tab=pd.DataFrame(index=['Poor/negative','Near poor','Low income','Middle income','High income'],columns=['Bottom 70%','Decile 8-9','Top 10% spenders'],dtype=float)
nn=tab.copy()
for (p,s),g in d.groupby(['POV','SPEND_GRP'],observed=True):
    nn.loc[str(p),s]=len(g)
    if len(g)>=40: tab.loc[str(p),s]=100*g.PERWT23F[g.HB==1].sum()/g.PERWT23F.sum()
print("% with OOP > 10% of family income:"); print(tab.round(1).to_string()); print("n:"); print(nn.astype('Int64').to_string())
print("\n=== Overall: who are the people with OOP>10% of income? ===")
hb=d[d.HB==1]
print("weighted prevalence: %.1f%% (%.1f M people)"%(100*hb.PERWT23F.sum()/w.sum(), hb.PERWT23F.sum()/1e6))
print("of THEM, %% in the top 10%% of total spend: %.1f%%"%(100*hb.PERWT23F[hb.SPEND_DEC>=10].sum()/hb.PERWT23F.sum()))
print("of THEM, %% NOT in the top 20%% of total spend: %.1f%%"%(100*hb.PERWT23F[hb.SPEND_DEC<9].sum()/hb.PERWT23F.sum()))
print("median total spend of high-burden group: $%.0f ; median OOP: $%.0f ; median family income: $%.0f"%(
  wq(hb.TOTEXP23.values,hb.PERWT23F.values,[.5])[0], wq(hb.TOTSLF23.values,hb.PERWT23F.values,[.5])[0], wq(hb.FAMINC23.clip(lower=0).values,hb.PERWT23F.values,[.5])[0]))
