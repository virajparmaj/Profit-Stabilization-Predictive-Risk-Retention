import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *
from util import CACHE
df=load(); d=df[df.PERWT23F>0].copy()
d['AGEBAND']=pd.cut(d.AGELAST,[-1,17,29,44,54,64,74,120],labels=['0-17','18-29','30-44','45-54','55-64','65-74','75+'])
d['CHRONIC_B']=pd.cut(d.CHRONIC_CT,[-1,0,1,2,3,5,12],labels=['0','1','2','3','4-5','6+'])
d['LIMIT_B']=pd.cut(d.LIMIT_CT,[-1,0,1,2,6],labels=['0','1','2','3+'])
d['INS']=d.INSCOV23.map({1:'Any private',2:'Public only',3:'Uninsured all yr'})
d['POV']=d.POVCAT23.map({0:'Poor/neg',1:'Near poor',2:'Low income',3:'Middle',4:'High'})
d['SRH']=d.RTHLTH53.map({1:'Excellent',2:'Very good',3:'Good',4:'Fair',5:'Poor'})
d['MH']=d.MNHLTH53.map({1:'Excellent',2:'Very good',3:'Good',4:'Fair',5:'Poor'})
d['SEXL']=d.SEX.map({0:'A(sex=0)',1:'B(sex=1)'})
d['RACE']=d.RACETHX.map({0:'Hispanic?',1:'g1',2:'g2',3:'g3',4:'g4'})
d['REG']=d.REGION53.map({1:'Northeast',2:'Midwest',3:'South',4:'West',-1:'NA'})
d['SMOKE']=d.OFTSMK53.map({1:'Daily smoker',2:'Some days',3:'Not at all',-1:'Child/NA'})
d['EXER']=d.PHYEXE53.map({1:'Exercises 5x/wk',2:'Does not',-1:'Child/NA'})

def seg_stats(g):
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    if w.sum()==0 or len(g)<40: return None
    med=wq(x,w,[.5])[0]; p90=wq(x,w,[.9])[0]; p95=wq(x,w,[.95])[0]; p99=wq(x,w,[.99])[0]
    mean=wmean(x,w)
    cat20=100*w[x>=20000].sum()/w.sum(); cat50=100*w[x>=50000].sum()/w.sum(); cat10=100*w[x>=10000].sum()/w.sum()
    # CVaR: mean spend of the worst 5% of the segment
    o=np.argsort(-x); xs,ws=x[o],w[o]; cw=np.cumsum(ws)/ws.sum()
    k=np.searchsorted(cw,0.05)+1
    cvar5=np.sum(xs[:k]*ws[:k])/np.sum(ws[:k])
    return dict(n=len(g), popM=w.sum()/1e6, median=med, mean=mean, p90=p90, p95=p95, p99=p99,
                cat10=cat10, cat20=cat20, cat50=cat50, cvar5=cvar5,
                p95_med=p95/max(med,1), mean_med=mean/max(med,1),
                top5share=100*top_share(x,w,0.05), gini=gini(x,w),
                share_of_total_spend=100*(x*w).sum()/(d.TOTEXP23*d.PERWT23F).sum())
rows=[]
for var in ['AGEBAND','CHRONIC_B','LIMIT_B','INS','POV','SRH','MH','SEXL','RACE','REG','SMOKE','EXER']:
    for lvl,g in d.groupby(var, observed=True):
        s=seg_stats(g)
        if s: rows.append(dict(dim=var, level=str(lvl), **s))
R=pd.DataFrame(rows)
pd.set_option('display.width',250)
print(R.round(1).to_string(index=False))
R.to_csv(os.path.join(CACHE,'segscan.csv'),index=False)
