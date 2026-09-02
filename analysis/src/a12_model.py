import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from util import *; from prep import prep
from sklearn.metrics import roc_auc_score
s=pd.read_parquet('data_processed/scored_members_2023.parquet')
print(s.describe().T.to_string())
print("\nAUC of stored P_LOW_RISK vs LOW_RISK:", roc_auc_score(s.LOW_RISK, s.P_LOW_RISK))
print("prevalence LOW_RISK in scored file: %.3f"%s.LOW_RISK.mean())
print("\n=== CATASTROPHIC LEAKAGE BY PREDICTED-LOW-RISK CUTOFF (stored scores) ===")
for k in [0.1,0.2,0.3,0.4,0.5]:
    sel=s[s.P_LOW_RISK>=s.P_LOW_RISK.quantile(1-k)]
    print(f"top {k*100:.0f}% by predicted low-risk: n={len(sel)} precision(actual LOW_RISK)={sel.LOW_RISK.mean():.3f} CAT20K rate={100*sel.CAT20K.mean():.2f}% mean spend=${sel.TOTEXP.mean():.0f} share of total cohort spend from its worst 1%={100*np.sort(sel.TOTEXP)[-max(1,len(sel)//100):].sum()/sel.TOTEXP.sum():.1f}%")
print("\nbaseline CAT20K rate in scored file: %.2f%%"%(100*s.CAT20K.mean()))
