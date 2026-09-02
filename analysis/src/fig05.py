import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep, with_oof
from style import *
import matplotlib.pyplot as plt, numpy as np
d=prep()
def wp(g,m): return 100*g.PERWT23F[m].sum()/g.PERWT23F.sum()
import json as _j
_R=_j.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),'..','website-handoff','data','ci-registry.json')))['intervals']
def bci(g, key):
    return _R[key]
bands=[('0-1',d.CHRONIC_CT<=1),('2-3',d.CHRONIC_CT.between(2,3)),('4 or more',d.CHRONIC_CT>=4)]
fig=plt.figure(figsize=(12.4,5.5)); gs=fig.add_gridspec(1,2,width_ratios=[1.12,1],wspace=0.25,left=0.06,right=0.985,top=0.755,bottom=0.15)
ax=fig.add_subplot(gs[0]); strip(ax)
xs=np.arange(3); wd=0.36
for k,(nm,mask,col) in enumerate([('Insured all year',d.INSCOV23!=3,ACC),('Uninsured all year',d.INSCOV23==3,WARN)]):
    vals=[];los=[];his=[]
    for _lbl,bm in bands:
        g=d[mask&bm]; vals.append(wp(g,g.LOW_RISK==1)); lo,hi=bci(g, f'label:{_lbl}:{nm}'); los.append(lo); his.append(hi)
    off=(k-0.5)*wd
    ax.bar(xs+off,vals,wd,color=col,zorder=3,label=nm)
    ax.errorbar(xs+off,vals,yerr=[np.array(vals)-los,np.array(his)-np.array(vals)],fmt='none',ecolor=INK,elinewidth=1.2,capsize=3.5,zorder=5)
    for i,v in enumerate(vals): ax.text(i+off,his[i]+1.8,f'{v:.0f}%',ha='center',fontsize=10,fontweight='bold',color=col)
ax.set_xticks(xs); ax.set_xticklabels([b[0] for b in bands])
ax.set_xlabel('Chronic conditions (count of 12)')
ax.set_ylabel('Share labelled LOW_RISK by the project rule')
ax.set_ylim(0,100); ax.yaxis.set_major_formatter(pct); ax.legend(loc='upper right')
ax.annotate('', xy=(2-wd/2,8.5), xytext=(2+wd/2,29.0), arrowprops=dict(arrowstyle='<->',color=INK,lw=1.5,connectionstyle='arc3,rad=-0.35'))
ax.text(2.36,17.5,'5.4x',ha='left',va='center',fontsize=13,fontweight='bold',color=INK)
ax.text(1.44,72,'Same measured disease burden.\n~5x difference in how often the\nlabel says "low-risk".',fontsize=8.9,color=MUTED,ha='left',va='top',linespacing=1.5)
ax.set_title('The label tracks coverage, not health',fontsize=10.4,color=INK,pad=10,loc='left')

ax2=fig.add_subplot(gs[1]); strip(ax2)
lr=d[d.LOW_RISK==1]
lr=lr.assign(quiet=((lr.CHRONIC_CT>=2)|(lr.LIMIT_CT>=1)|(lr.RTHLTH53.isin([4,5]))).astype(int),
             access=((lr.INSCOV23==3)|(lr.NO_USUAL_SOURCE==1)|(lr.DELAY_ANY==1)|(lr.AFFORD_BARRIER==1)).astype(int))
seg=[('Genuinely healthy and\nfully engaged with care',(lr.quiet==0)&(lr.access==0),GOOD),
     ('Access barrier only\n(uninsured / no usual source /\ndelayed or unaffordable care)',(lr.quiet==0)&(lr.access==1),'#e0a02a'),
     ('Hidden clinical burden only\n(2+ conditions, a limitation,\nor fair/poor health)',(lr.quiet==1)&(lr.access==0),ACC2),
     ('Both at once',(lr.quiet==1)&(lr.access==1),WARN)]
vals=[wp(lr,m) for _,m,_ in seg]
left=0
for (nm,m,c),v in zip(seg,vals):
    ax2.barh([0],[v],left=left,color=c,height=0.42,zorder=3,ec='white',lw=1.2)
    ax2.text(left+v/2,0,f'{v:.0f}%',ha='center',va='center',color='white',fontsize=13,fontweight='bold')
    left+=v
ys=[-0.42,-0.72,-1.02,-1.32]
for (nm,m,c),v,y in zip(seg,vals,ys):
    ax2.scatter([2],[y],s=95,color=c,marker='s',zorder=4)
    ax2.text(6,y,nm,va='center',fontsize=9.2,color=INK,linespacing=1.35)
ax2.set_xlim(0,100); ax2.set_ylim(-1.62,0.42)
ax2.set_yticks([]); ax2.xaxis.set_major_formatter(pct)
ax2.set_xlabel('Composition of the LOW_RISK cohort (weighted)')
ax2.spines['left'].set_visible(False); ax2.grid(axis='y',visible=False)
ax2.set_title('Only 39% of the "low-risk" cohort is unambiguously low-risk',fontsize=10.4,color=INK,pad=10,loc='left')

head(fig,'"Low spend" is partly a measure of access, not health: at identical disease burden, uninsured members are ~5x more likely to be labelled low-risk',
     'LOW_RISK = bottom-30% spend ($484) + zero ER visits + zero inpatient stays. Uninsured members consume less care at every level of illness, so the rule absorbs them:\n63% of uninsured members with 2+ chronic conditions are labelled low-risk, versus 12% of insured members with the same burden.',y=0.985)
foot(fig,'MEPS 2023, PERWT23F-weighted. Uninsured with 2+ conditions: 63.1% [56.4-69.9], n=284. Insured with 2+ conditions: 12.4% [11.5-13.3], n=8,724. 95% CIs from 4,000 bootstrap resamples, seed 20260824. This is an association in a single cross-section, not evidence that coverage causes the difference.')
fig.savefig('analysis/figures/05_low_risk_label_measures_access.png')
print('ok')
