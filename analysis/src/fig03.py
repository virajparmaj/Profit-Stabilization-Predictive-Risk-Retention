import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, with_oof
from style import *
import matplotlib.pyplot as plt, numpy as np
from matplotlib.colors import LinearSegmentedColormap
d=prep()
CH=['0','1','2','3','4-5','6+']; LM=['0','1','2+']
cat=np.full((6,3),np.nan); med=np.full((6,3),np.nan); nn=np.zeros((6,3),int)
for i,cb in enumerate(CH):
    for j,lb in enumerate(LM):
        g=d[(d.CHRONIC_B.astype(str)==cb)&(d.LIMIT_B.astype(str)==lb)]
        nn[i,j]=len(g)
        if len(g)>=40:
            x=g.TOTEXP23.values; w=g.PERWT23F.values
            cat[i,j]=100*w[x>=20000].sum()/w.sum(); med[i,j]=wq(x,w,[.5])[0]
fig=plt.figure(figsize=(12.4,5.9)); gs=fig.add_gridspec(1,2,width_ratios=[1.25,1],wspace=0.26,left=0.075,right=0.985,top=0.755,bottom=0.13)
cmap=LinearSegmentedColormap.from_list('r',['#f4f8fd','#a9c7ea','#5f8fd4','#2b5fa8','#12305c'])
ax=fig.add_subplot(gs[0])
im=ax.imshow(cat,cmap=cmap,vmin=0,vmax=48,aspect='auto')
ax.set_xticks(range(3)); ax.set_xticklabels(['0','1','2 or more'])
ax.set_yticks(range(6)); ax.set_yticklabels(CH)
ax.set_xlabel('Functional limitations  (ADL, IADL, walking, cognitive, work, social)')
ax.set_ylabel('Chronic conditions (count of 12)')
ax.grid(False)
for i in range(6):
    for j in range(3):
        if np.isnan(cat[i,j]):
            ax.text(j,i,f'n={nn[i,j]}',ha='center',va='center',fontsize=7.6,color=NEU); continue
        c='white' if cat[i,j]>24 else INK
        ax.text(j,i-0.14,f'{cat[i,j]:.0f}%',ha='center',va='center',fontsize=12,fontweight='bold',color=c)
        ax.text(j,i+0.22,f'median \\${med[i,j]:,.0f}',ha='center',va='center',fontsize=7.8,color=c,alpha=0.85)
cb=fig.colorbar(im,ax=ax,pad=0.02,fraction=0.045); cb.set_label('% of members with $20k+ spend',fontsize=8.6); cb.outline.set_visible(False)
ax.set_title('Catastrophic-spend rate ($20k+) by burden type',fontsize=10.4,color=INK,pad=10,loc='left')
# highlight the two compared cells
for (i,j) in [(2,2),(5,0)]:
    ax.add_patch(plt.Rectangle((j-0.5,i-0.5),1,1,fill=False,ec=WARN,lw=2.6,zorder=6))

ax2=fig.add_subplot(gs[1]); strip(ax2)
labs=['2 chronic\n+ 2 or more limitations','6+ chronic\n+ no limitations']
mm=[med[2,2],med[5,0]]; cc=[cat[2,2],cat[5,0]]; import json as _j; _R=_j.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'..','website-handoff','data','ci-registry.json')))['intervals']
ci=[tuple(_R['burden:2x2+:cat20']),tuple(_R['burden:6+x0:cat20'])]
xp=np.arange(2)
ax2b=ax2.twinx(); ax2b.grid(False)
ax2.bar(xp-0.2,mm,0.36,color='#c3d4e8',zorder=3,label='Median annual spend')
for i,v in enumerate(mm): ax2.text(i-0.2,v+280,f'\\${v:,.0f}',ha='center',fontsize=9.4,fontweight='bold',color='#3c5f8a')
ax2b.bar(xp+0.2,cc,0.36,color=WARN,zorder=3,label='Catastrophic rate')
for i,v in enumerate(cc):
    ax2b.errorbar(i+0.2,v,yerr=[[v-ci[i][0]],[ci[i][1]-v]],fmt='none',ecolor=INK,elinewidth=1.3,capsize=4,zorder=5)
    ax2b.text(i+0.2,ci[i][1]+1.4,f'{v:.1f}%',ha='center',fontsize=9.4,fontweight='bold',color=WARN)
ax2.set_ylim(0,17200); ax2.yaxis.set_major_formatter(usd); ax2.set_ylabel('Median annual spend',color='#3c5f8a')
ax2b.set_ylim(0,49); ax2b.yaxis.set_major_formatter(pct); ax2b.set_ylabel('% with $20k+ spend  (95% CI)',color=WARN)
for s in ['top']: ax2.spines[s].set_visible(False); ax2b.spines[s].set_visible(False)
ax2.set_xticks(xp); ax2.set_xticklabels(labs,fontsize=9.2)
ax2.set_title('Same tail risk. 42% lower typical cost.',fontsize=10.4,color=INK,pad=10,loc='left')
ax2.text(0.5,14700,'Diagnosis counts move the median.\nFunctional limitations move the tail.',ha='center',fontsize=9.5,color=INK,fontweight='bold',linespacing=1.4)

head(fig,'Counting diagnoses misses tail risk: 2 chronic conditions plus functional limitations carry the same catastrophic risk as 6+ conditions alone',
     'Adjusted for age and sex and for each other, each additional functional limitation multiplies the odds of a $20k+ year by 1.39 — more than each additional chronic condition (1.33). Adding limitations lifts pseudo-R² from 0.151 to 0.172.',y=0.985)
foot(fig,'MEPS 2023, PERWT23F-weighted; cells with n<40 suppressed. 2 chronic + 2 or more limitations: 28.7% [21.0-36.7], median $6,327 (n=195). 6+ chronic + no limitations: 26.9% [21.2-32.5], median $10,938 (n=298). 95% CIs from 4,000 bootstrap resamples, seed 20260824.')
fig.savefig('analysis/figures/03_chronic_vs_functional_tail_risk.png')
print('ok')
