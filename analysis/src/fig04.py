import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, with_oof
from style import *
import matplotlib.pyplot as plt, numpy as np
d=prep()
bands=[('0',d.OBTOTV23==0),('1-2',d.OBTOTV23.between(1,2)),('3-5',d.OBTOTV23.between(3,5)),('6-10',d.OBTOTV23.between(6,10)),('11+',d.OBTOTV23>=11)]
def stats(g):
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    acute=100*(g.ERTEXP23+g.IPTEXP23).mul(g.PERWT23F).sum()/max((g.TOTEXP23*g.PERWT23F).sum(),1)
    return dict(n=len(g),pop=w.sum()/1e6,med=wq(x,w,[.5])[0],mean=wmean(x,w),acute=acute,
                cat20=100*w[x>=20000].sum()/w.sum())
hi=d[d.CHRONIC_CT>=3]; lo=d[d.CHRONIC_CT<=1]
H=[stats(hi[m[hi.index]]) for _,m in bands]; L=[stats(lo[m[lo.index]]) for _,m in bands]
fig=plt.figure(figsize=(13.4,5.6)); gs=fig.add_gridspec(1,3,width_ratios=[1.05,1.05,1.1],wspace=0.40,left=0.055,right=0.985,top=0.755,bottom=0.155)
xs=np.arange(5)
ax=fig.add_subplot(gs[0]); strip(ax)
ax.plot(xs,[h['acute'] for h in H],'-o',color=WARN,lw=2.4,ms=7,label='3 or more chronic conditions',zorder=4)
ax.plot(xs,[l['acute'] for l in L],'-o',color=ACC,lw=2.4,ms=7,label='0-1 chronic conditions',zorder=4)
ax.annotate(f"{H[0]['acute']:.0f}%",xy=(0,H[0]['acute']),xytext=(0.18,H[0]['acute']+3.2),fontsize=10,fontweight='bold',color=WARN)
ax.annotate(f"{H[-1]['acute']:.0f}%",xy=(4,H[-1]['acute']),xytext=(3.4,H[-1]['acute']-6.5),fontsize=10,fontweight='bold',color=WARN)
ax.set_xticks(xs); ax.set_xticklabels([b[0] for b in bands])
ax.set_ylim(0,62); ax.yaxis.set_major_formatter(pct)
ax.set_xlabel('Office-based visits in 2023'); ax.set_ylabel('ER + inpatient share of the group’s dollars')
ax.legend(loc='upper right',fontsize=8.6)
ax.set_title('Fewer office visits → more of the money\narrives through the emergency door',fontsize=10.2,color=INK,pad=8,loc='left')

ax2=fig.add_subplot(gs[1]); strip(ax2)
ax2.plot(xs,[h['med'] for h in H],'-o',color=WARN,lw=2.4,ms=7,zorder=4)
ax2.plot(xs,[h['mean'] for h in H],'--o',color=NEU,lw=2.0,ms=6,zorder=4,label='Mean')
ax2.plot([],[],'-o',color=WARN,lw=2.4,ms=7,label='Median')
ax2.legend(loc='upper left',fontsize=8.6)
ax2.annotate(f"median ${H[0]['med']:,.0f}",xy=(0,H[0]['med']),xytext=(0.16,-1900),fontsize=9.2,color=WARN,fontweight='bold',
             arrowprops=dict(arrowstyle='->',color=WARN,lw=1.0))
ax2.annotate(f"mean ${H[0]['mean']:,.0f}",xy=(0,H[0]['mean']),xytext=(0.30,12600),fontsize=9.2,color=MUTED,
             arrowprops=dict(arrowstyle='->',color=NEU,lw=1.0))
ax2.text(1.25,20500,'16x gap between\nmean and median',fontsize=9.2,color=INK,fontweight='bold',linespacing=1.35)
ax2.set_xticks(xs); ax2.set_xticklabels([b[0] for b in bands])
ax2.set_ylim(-3600,31000); ax2.yaxis.set_major_formatter(usd)
ax2.axhline(0,color=GRID,lw=1)
ax2.set_xlabel('Office-based visits in 2023'); ax2.set_ylabel('Annual spend, members with 3+ chronic conditions')
ax2.set_title('The disengaged look cheapest on the median\nand nothing like it on the mean',fontsize=10.2,color=INK,pad=8,loc='left')

ax3=fig.add_subplot(gs[2]); strip(ax3)
dis=d[(d.CHRONIC_CT>=3)&(d.OBTOTV23==0)]; eng=d[(d.CHRONIC_CT>=3)&(d.OBTOTV23>=3)]
def wp(g,m): return 100*g.PERWT23F[m].sum()/g.PERWT23F.sum()
rows=['Labelled "low-risk"\nby the project rule','No usual source\nof care','Uninsured all year','Any ER visit','Any inpatient stay']
A=[wp(dis,dis.LOW_RISK==1),wp(dis,dis.NO_USUAL_SOURCE==1),wp(dis,dis.INSCOV23==3),wp(dis,dis.ERTOT23>0),wp(dis,dis.IPDIS23>0)]
B=[wp(eng,eng.LOW_RISK==1),wp(eng,eng.NO_USUAL_SOURCE==1),wp(eng,eng.INSCOV23==3),wp(eng,eng.ERTOT23>0),wp(eng,eng.IPDIS23>0)]
yp=np.arange(5)[::-1]
ax3.barh(yp+0.19,A,0.36,color=WARN,label='0 office visits (9.2M people)',zorder=3)
ax3.barh(yp-0.19,B,0.36,color=NEU,label='3+ office visits (64.8M people)',zorder=3)
for y,a,b in zip(yp,A,B):
    ax3.text(a+1.0,y+0.19,f'{a:.0f}%',va='center',fontsize=9,fontweight='bold',color=WARN)
    ax3.text(b+1.0,y-0.19,f'{b:.0f}%',va='center',fontsize=9,color=MUTED)
ax3.set_yticks(yp); ax3.set_yticklabels(rows,fontsize=8.8)
ax3.set_xlim(0,68); ax3.xaxis.set_major_formatter(pct)
ax3.set_xlabel('Share of the group')
ax3.legend(loc='lower right',fontsize=8.2,bbox_to_anchor=(1.02,-0.055))
ax3.set_title('Half of them are scored "low-risk"\ndespite 3+ chronic conditions',fontsize=10.2,color=INK,pad=8,loc='left')

head(fig,'The cheapest median in the population is also the most emergency-driven: 9.2M members with 3+ chronic conditions and zero office visits',
     'Median $377, versus $8,692 for chronically ill members who do see a doctor — a 23x gap on typical cost, but only a 3x gap on catastrophic-spend rate (8.4% [5.9-11.1] vs 26.0%).\n54% of their dollars go to the ER or an inpatient bed, versus 24% for the engaged group. Their mean is $6,157 — 16x their median.',y=0.985)
foot(fig,'MEPS 2023, PERWT23F-weighted. n=545 (0 visits) and n=4,523 (3+ visits) among members with 3 or more of 12 chronic conditions. Zero office visits mechanically lowers total spend; the non-mechanical findings are the ER/inpatient SHARE of dollars and the access-barrier profile. 95% CI from 4,000 bootstrap resamples, seed 20260824.')
fig.savefig('analysis/figures/04_disengaged_chronic_segment.png')
print('ok')
