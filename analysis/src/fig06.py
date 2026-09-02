import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, with_oof
from style import *
import matplotlib.pyplot as plt, numpy as np
d=prep(); sub=d[(d.INSCOV23!=3)&(d.AGELAST<65)]
LV=['Poor/negative','Near poor','Low income','Middle income','High income']
SH=['Poor\n(<100% FPL)','Near poor\n(100-125%)','Low income\n(125-200%)','Middle\n(200-400%)','High\n(400%+)']
med=[];rout=[];exc=[];mean=[]
for l in LV:
    g=sub[sub.POV==l]; x=g.TOTEXP23.values; w=g.PERWT23F.values
    med.append(wq(x,w,[.5])[0]); rout.append(wmean(np.minimum(x,5000),w))
    exc.append(wmean(np.maximum(x-5000,0),w)); mean.append(wmean(x,w))
fig=plt.figure(figsize=(12.2,5.5)); gs=fig.add_gridspec(1,2,width_ratios=[1.18,1],wspace=0.28,left=0.06,right=0.985,top=0.755,bottom=0.16)
ax=fig.add_subplot(gs[0]); strip(ax)
xs=np.arange(5)
ax.bar(xs,rout,0.6,color='#b9cfe8',zorder=3,label='Routine: first $5,000 of spend')
ax.bar(xs,exc,0.6,bottom=rout,color=WARN,zorder=3,label='Catastrophic: spend above $5,000')
ax.plot(xs,med,'-o',color=GOOD,lw=2.4,ms=8,zorder=6,label='Median member')
for i in range(5):
    ax.text(i,mean[i]+230,f'${mean[i]:,.0f}',ha='center',fontsize=9.2,fontweight='bold',color=INK)
    ax.text(i,med[i]-700,f'${med[i]:,.0f}',ha='center',fontsize=8.8,fontweight='bold',color=GOOD)
ax.set_xticks(xs); ax.set_xticklabels(SH,fontsize=8.6)
ax.set_ylim(0,8800); ax.yaxis.set_major_formatter(usd)
ax.set_ylabel('Mean annual spend per member')
ax.legend(loc='upper left',fontsize=8.8)
ax.set_title('Where the income gradient actually lives',fontsize=10.4,color=INK,pad=10,loc='left')

ax2=fig.add_subplot(gs[1]); strip(ax2)
labs=['Median member','Routine spend\n(first $5k)','Catastrophic spend\n(above $5k)','Mean spend','$20k+ rate']
g1=sub[sub.POV.isin(['Poor/negative','Near poor'])]; g2=sub[sub.POV=='High income']
def m5(g):
    x=g.TOTEXP23.values; w=g.PERWT23F.values
    return [wq(x,w,[.5])[0], wmean(np.minimum(x,5000),w), wmean(np.maximum(x-5000,0),w), wmean(x,w), 100*w[x>=20000].sum()/w.sum()]
A=m5(g1); B=m5(g2); gap=[100*(a/b-1) for a,b in zip(A,B)]
cols=[WARN if abs(v)>40 else ('#e0a02a' if abs(v)>20 else GOOD) for v in gap]
yp=np.arange(5)[::-1]
ax2.barh(yp,gap,0.5,color=cols,zorder=3)
for v,y in zip(gap,yp):
    ax2.text(v-2.5,y,f'{v:+.0f}%',va='center',ha='right',fontsize=10.5,fontweight='bold',color=INK)
ax2.set_yticks(yp); ax2.set_yticklabels(labs,fontsize=9)
ax2.axvline(0,color=INK,lw=1.2)
ax2.set_xlim(-84,12); ax2.xaxis.set_major_formatter(pct)
ax2.set_xlabel('Gap: poor + near-poor members vs high-income members')
ax2.grid(axis='y',visible=False)
ax2.text(-82,-1.05,'Judged on the median, poor members look 62% cheaper.\nJudged on the mean, only 18% cheaper — and their\ncatastrophic-spend rate is nearly identical.',
         fontsize=9.3,color=INK,fontweight='bold',va='top',linespacing=1.5)
ax2.set_ylim(-2.35,4.55)
ax2.set_title('The "cheap" low-income member is a median artifact',fontsize=10.4,color=INK,pad=10,loc='left')

head(fig,'Income predicts routine spending, not catastrophic spending: the poor-vs-rich cost gap is 62% on the median but only 18% on the mean',
     'Insured members under 65 only, so the comparison is not driven by Medicare or by uninsured non-utilisation. Catastrophic exposure barely moves with income: the $20k+ rate is 7.1% [6.1-8.3] for poor and near-poor members vs 8.0% [7.1-8.8] for high-income members.',y=0.985)
foot(fig,'MEPS 2023, PERWT23F-weighted; n=2,410 (poor + near poor) and n=5,224 (high income), insured all year and aged under 65. Income bands are MEPS POVCAT23 categories relative to the federal poverty line. 95% CIs from 4,000 bootstrap resamples, seed 20260824.')
fig.savefig('analysis/figures/06_income_gradient_routine_not_catastrophic.png')
print('ok')
