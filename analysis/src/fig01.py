import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, with_oof
from style import *
import matplotlib.pyplot as plt, numpy as np
d=prep(); x=d.TOTEXP23.values; w=d.PERWT23F.values
fig=plt.figure(figsize=(12.4,5.4)); gs=fig.add_gridspec(1,2,width_ratios=[1,1],wspace=0.24,left=0.055,right=0.985,top=0.76,bottom=0.15)

ax=fig.add_subplot(gs[0]); strip(ax)
o=np.argsort(-x); xs,ws=x[o],w[o]
cp=np.concatenate([[0],np.cumsum(ws)/ws.sum()*100]); cs=np.concatenate([[0],np.cumsum(xs*ws)/(xs*ws).sum()*100])
ax.plot(cp,cs,color=WARN,lw=2.6,zorder=4)
ax.plot([0,100],[0,100],color=NEU,lw=1.2,ls=(0,(4,3)),zorder=2)
ax.text(66,60,'perfect equality',color=NEU,fontsize=8.5,rotation=30,va='center')
notes=[(1,'Top 1% of members\n= 20% of all spending',10,-14),(5,'Top 5% of members\n= 49% of all spending',12,-4),(10,'Top 10% of members\n= 65% of all spending',14,-2)]
for f,lab,dx,dy in notes:
    v=100*top_share(x,w,f/100)
    ax.plot([f,f],[0,v],color=ACC,lw=0.9,ls=':',zorder=3)
    ax.scatter([f],[v],s=38,color=ACC,zorder=6,ec='white',lw=1.3)
    ax.annotate(lab, xy=(f,v), xytext=(f+dx,v+dy), fontsize=9.2, color=INK,
                fontweight='bold' if f==5 else 'normal', va='center',
                arrowprops=dict(arrowstyle='-',color=ACC,lw=0.9))
ax.set_xlim(0,100); ax.set_ylim(0,100)
ax.set_xlabel('Members ranked most expensive first (cumulative %)')
ax.set_ylabel('Cumulative share of total spending')
ax.xaxis.set_major_formatter(pct); ax.yaxis.set_major_formatter(pct)
ax.set_title('Half of all dollars sit with 5% of members',fontsize=10.4,color=INK,pad=10,loc='left')

ax2=fig.add_subplot(gs[1]); strip(ax2)
bins=np.arange(0,50001,1250)
hw,_=np.histogram(np.clip(x,0,49999),bins=bins,weights=w); hw=hw/w.sum()*100
ax2.bar(bins[:-1],hw,width=1250,align='edge',color='#c3d4e8',ec='white',lw=0.5,zorder=3)
med=wq(x,w,[.5])[0]; mn=wmean(x,w); below=100*w[x<mn].sum()/w.sum()
ax2.axvspan(0,mn,color=WARN,alpha=0.055,zorder=1)
ax2.axvline(med,color=GOOD,lw=2.3,zorder=6); ax2.axvline(mn,color=WARN,lw=2.3,zorder=6)
ax2.annotate(f'MEDIAN  ${med:,.0f}',xy=(med,27.5),xytext=(7400,30.5),color=GOOD,fontsize=10,fontweight='bold',
             arrowprops=dict(arrowstyle='->',color=GOOD,lw=1.1))
ax2.annotate(f'MEAN  ${mn:,.0f}',xy=(mn,20.0),xytext=(14200,24.0),color=WARN,fontsize=10,fontweight='bold',
             arrowprops=dict(arrowstyle='->',color=WARN,lw=1.1))
ax2.text(mn+900,13.2,f'{below:.0f}% of the population\nspends LESS than the average.\nThe mean sits at the 79th percentile.',
         ha='left',va='center',fontsize=9.8,color=WARN,fontweight='bold',linespacing=1.45)
ax2.set_xlim(0,50000); ax2.set_ylim(0,34)
ax2.annotate('31% of members spend under \$500',xy=(1100,32.4),xytext=(22000,30.6),fontsize=9,color=MUTED,va='center',arrowprops=dict(arrowstyle='->',color=MUTED,lw=0.9,connectionstyle='arc3,rad=0.12'))
ax2.set_xlabel('Total 2023 healthcare spending  (axis cut at $50k; 5% of members are above)')
ax2.set_ylabel('Share of population')
ax2.xaxis.set_major_formatter(usd); ax2.yaxis.set_major_formatter(pct)
ax2.set_title('The mean is a tail statistic, not a typical member',fontsize=10.4,color=INK,pad=10,loc='left')

head(fig,'The "average member" does not exist: 79% spend below the mean, and 5% of members carry half of all spending',
     'MEPS 2023 (HC-251). n = 18,463 person-years with positive survey weight, weighted to 334.5M people. Gini of annual spend = 0.78.', y=0.985)
foot(fig,'Source: MEPS HC-251 2023 consolidated file, PERWT23F-weighted. The bottom 50% of members account for 2.9% of total spending; 14% spend $0.')
fig.savefig('analysis/figures/01_concentration_mean_vs_median.png')
print('ok')
