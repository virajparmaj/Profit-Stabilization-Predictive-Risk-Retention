import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
INK='#16202b'; MUTED='#6b7683'; GRID='#e4e8ec'
ACC='#1f6feb'; WARN='#d1491d'; GOOD='#0f8b6c'; NEU='#9aa5b1'; ACC2='#7b4bd6'
plt.rcParams.update({
 'figure.dpi':160,'savefig.dpi':160,'figure.facecolor':'white','axes.facecolor':'white',
 'font.family':'DejaVu Sans','font.size':9.5,
 'axes.edgecolor':GRID,'axes.linewidth':1.0,'axes.labelcolor':MUTED,'axes.labelsize':9.5,
 'xtick.color':MUTED,'ytick.color':MUTED,'xtick.labelsize':9,'ytick.labelsize':9,
 'axes.grid':True,'grid.color':GRID,'grid.linewidth':0.8,'axes.axisbelow':True,
 'legend.frameon':False,'legend.fontsize':9,'savefig.bbox':'tight','savefig.pad_inches':0.35})
def _e(t):
    return t.replace('$','\\$') if isinstance(t,str) else t
def head(fig, title, sub=None, y=0.985):
    fig.text(0.012, y, _e(title), ha='left', va='top', fontsize=13.5, fontweight='bold', color=INK, wrap=True)
    if sub: fig.text(0.012, y-0.075, _e(sub), ha='left', va='top', fontsize=9.5, color=MUTED)
def foot(fig, txt, y=0.005):
    fig.text(0.012, y, _e(txt), ha='left', va='bottom', fontsize=7.6, color=MUTED, style='italic')
def strip(ax, left=True):
    for s in ['top','right']: ax.spines[s].set_visible(False)
    if not left: ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(GRID); ax.spines['left'].set_color(GRID)
usd=FuncFormatter(lambda v,p: f"${v:,.0f}")
pct=FuncFormatter(lambda v,p: f"{v:.0f}%")
