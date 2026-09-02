import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, boot_stat
d=prep()
def wp(g,m): return 100*g.PERWT23F[m].sum()/g.PERWT23F.sum()
d['OB_B']=pd.cut(d.OBTOTV23,[-1,0,2,5,10,1000],labels=['0','1-2','3-5','6-10','11+'])
print("=== ER-USE / ACUTE SHARE vs OFFICE VISITS, split by chronic burden ===")
for cb,lab in [(d.CHRONIC_CT<=1,'low burden (<=1 chronic)'),(d.CHRONIC_CT>=3,'high burden (>=3 chronic)')]:
    print(f"\n-- {lab} --")
    g0=d[cb]
    for lvl,g in g0.groupby('OB_B',observed=True):
        if len(g)<40: continue
        print(f" office visits {str(lvl):<6} n={len(g):>5} popM={g.PERWT23F.sum()/1e6:5.1f}  ER-any={wp(g,g.ERTOT23>0):5.1f}%  IP-any={wp(g,g.IPDIS23>0):5.1f}%  cat20={wp(g,g.TOTEXP23>=20000):5.1f}%  median=${wq(g.TOTEXP23.values,g.PERWT23F.values,[.5])[0]:>7.0f}  acute$share={100*(g.ERTEXP23+g.IPTEXP23).mul(g.PERWT23F).sum()/(g.TOTEXP23*g.PERWT23F).sum():4.1f}%")
print("\n=== 'DISENGAGED CHRONIC' segment: >=3 chronic conditions AND 0 office visits ===")
dis=d[(d.CHRONIC_CT>=3)&(d.OBTOTV23==0)]; eng=d[(d.CHRONIC_CT>=3)&(d.OBTOTV23>=3)]
for nm,g in [('Disengaged (>=3 chronic, 0 office visits)',dis),('Engaged (>=3 chronic, 3+ office visits)',eng)]:
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    print(f"{nm}: n={len(g)} popM={w.sum()/1e6:.1f} median=${wq(x,w,[.5])[0]:.0f} mean=${wmean(x,w):.0f} cat20={wp(g,g.TOTEXP23>=20000):.1f}% ER-any={wp(g,g.ERTOT23>0):.1f}% IP-any={wp(g,g.IPDIS23>0):.1f}% uninsured={wp(g,g.INSCOV23==3):.1f}% noUSC={wp(g,g.NO_USUAL_SOURCE==1):.1f}% share_acute={100*(g.ERTEXP23+g.IPTEXP23).mul(g.PERWT23F).sum()/max((g.TOTEXP23*g.PERWT23F).sum(),1):.1f}%")
print("\n=== ER share of TOTAL spend by office-visit band (all) ===")
for lvl,g in d.groupby('OB_B',observed=True):
    print(f"{str(lvl):<6} ER$/total$ = {100*(g.ERTEXP23*g.PERWT23F).sum()/max((g.TOTEXP23*g.PERWT23F).sum(),1):5.1f}%   IP$/total$ = {100*(g.IPTEXP23*g.PERWT23F).sum()/max((g.TOTEXP23*g.PERWT23F).sum(),1):5.1f}%")
