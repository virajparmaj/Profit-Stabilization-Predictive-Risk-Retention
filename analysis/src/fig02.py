import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, with_oof
from style import *
import matplotlib.pyplot as plt, numpy as np
d=with_oof(prep())
pools=[('Whole population',d,NEU),('Model-selected\n"low-risk" 30%',d[d.P_OOF>=np.quantile(d.P_OOF,0.70)],ACC),
       ('Model-selected\n"low-risk" 10%',d[d.P_OOF>=np.quantile(d.P_OOF,0.90)],ACC2)]
fig=plt.figure(figsize=(12.4,5.4)); gs=fig.add_gridspec(1,3,width_ratios=[1,1,1.15],wspace=0.30,left=0.055,right=0.985,top=0.75,bottom=0.14)

# P1 cost level
ax=fig.add_subplot(gs[0]); strip(ax)
xs=np.arange(3); wdt=0.38
med=[wq(g.TOTEXP23.values,g.PERWT23F.values,[.5])[0] for _,g,_ in pools]
mnv=[wmean(g.TOTEXP23.values,g.PERWT23F.values) for _,g,_ in pools]
ax.bar(xs-wdt/2,med,wdt,color=GOOD,label='Median',zorder=3)
ax.bar(xs+wdt/2,mnv,wdt,color=WARN,label='Mean',zorder=3)
for i,(m,a) in enumerate(zip(med,mnv)):
    ax.text(i-wdt/2,m+230,f'${m:,.0f}',ha='center',fontsize=8.8,color=GOOD,fontweight='bold')
    ax.text(i+wdt/2,a+230,f'${a:,.0f}',ha='center',fontsize=8.8,color=WARN,fontweight='bold')
ax.set_xticks(xs); ax.set_xticklabels([p[0] for p in pools],fontsize=8.2)
ax.set_ylim(0,9200); ax.yaxis.set_major_formatter(usd); ax.set_ylabel('Annual spend')
ax.legend(loc='upper right',ncol=1)
ax.set_title('1. Selection works on the LEVEL\nmean cost falls 63%',fontsize=10.2,color=INK,pad=8,loc='left')

# P2 concentration inside pool
ax2=fig.add_subplot(gs[1]); strip(ax2)
g1=[100*top_share(g.TOTEXP23.values,g.PERWT23F.values,0.01) for _,g,_ in pools]
gg=[gini(g.TOTEXP23.values,g.PERWT23F.values) for _,g,_ in pools]
ax2.bar(xs,g1,0.55,color=[p[2] for p in pools],zorder=3)
for i,(v,gi) in enumerate(zip(g1,gg)):
    ax2.text(i,v+0.7,f'{v:.0f}%',ha='center',fontsize=10,fontweight='bold',color=INK)
    ax2.text(i,1.4,f'Gini {gi:.2f}',ha='center',fontsize=8.6,color='white',fontweight='bold')
ax2.annotate('',xy=(2,g1[2]+4.5),xytext=(0,g1[0]+4.5),arrowprops=dict(arrowstyle='->',color=WARN,lw=1.8,connectionstyle='arc3,rad=-0.22'))
ax2.text(0.62,g1[0]+11.2,'MORE concentrated,\nnot less',ha='center',fontsize=9.6,color=WARN,fontweight='bold')
ax2.set_xticks(xs); ax2.set_xticklabels([p[0] for p in pools],fontsize=8.8)
ax2.set_ylim(0,44); ax2.yaxis.set_major_formatter(pct)
ax2.set_ylabel("Share of the pool's own spend\nheld by its worst 1% of members")
ax2.set_title('2. But NOT on the SHAPE\nthe pool gets more tail-driven',fontsize=10.2,color=INK,pad=8,loc='left')

# P3 within-pool concentration curves
ax3=fig.add_subplot(gs[2]); strip(ax3)
for nm,g,c in pools:
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    o=np.argsort(-x); xs_,ws_=x[o],w[o]
    cp=np.concatenate([[0],np.cumsum(ws_)/ws_.sum()*100]); cs=np.concatenate([[0],np.cumsum(xs_*ws_)/(xs_*ws_).sum()*100])
    ax3.plot(cp,cs,color=c,lw=2.4,label=nm.replace('\n',' '),zorder=3)
ax3.plot([0,100],[0,100],color=GRID,lw=1.2,ls=(0,(4,3)))
ax3.set_xlim(0,30); ax3.set_ylim(0,90)
ax3.xaxis.set_major_formatter(pct); ax3.yaxis.set_major_formatter(pct)
ax3.set_xlabel("Pool members, most expensive first")
ax3.set_ylabel("Cumulative share of the pool's spend")
ax3.legend(loc='lower right',fontsize=8.6)
ax3.text(15.5,26,'Curves shift UP as the pool\ngets "cleaner": a smaller\nminority owns more of it.',fontsize=9,color=MUTED,linespacing=1.4)
ax3.set_title('3. Every selected pool is steeper than the population',fontsize=10.2,color=INK,pad=8,loc='left')

head(fig,'Risk selection lowers the cost level but makes the remaining pool MORE tail-concentrated — it is risk reduction, not risk elimination',
     'Out-of-fold predictions from the deployed B3-chronic XGBoost pipeline (5-fold CV, AUC 0.772 — reproduces the project\'s reported 0.773). "Selected" = members with the highest predicted low-risk probability.',y=0.985)
foot(fig,'Even in the model-selected top-30% pool, 2.9% of members still cross $20,000 and 25% of the pool\'s expected cost comes from spending above $20,000. MEPS 2023, PERWT23F-weighted.')
fig.savefig('analysis/figures/02_selection_shifts_level_not_shape.png')
print('ok')
