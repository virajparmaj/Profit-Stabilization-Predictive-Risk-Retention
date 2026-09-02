import pandas as pd, numpy as np
pd.set_option('display.width',200); pd.set_option('display.max_columns',80)
df = pd.read_csv('data_processed/meps_model_ready_2023.csv')
print(df.shape)
print(df.dtypes.to_string())
print("\n--- describe numeric key ---")
key=['AGELAST','TOTEXP23','ERTOT23','IPDIS23','OBTOTV23','OPTOTV23','RXTOT23','CHRONIC_CT','LIMIT_CT','K6SUM42','PHQ242','RTHLTH53','MNHLTH53','PHYEXE53','OFTSMK53','PERWT23F','FAMINC23','TTLP23X','EDUCYR']
print(df[key].describe(percentiles=[.01,.05,.25,.5,.75,.9,.95,.99]).T.to_string())
print("\n--- value counts categorical ---")
for c in ['SEX','RACETHX','HISPANX','POVCAT23','INSURC23','EMPST53','MARRY53X','PANEL','DATAYEAR','RTHLTH53','MNHLTH53','PHYEXE53','OFTSMK53','ANYLMI23','COVIDEVER53','PRVEV23','MCREV23','MCDEV23','UNINS23']:
    print(c, dict(df[c].value_counts(dropna=False).sort_index()))
print("\n--- nulls ---")
n=df.isna().sum(); print(n[n>0].to_string())
print("\n--- negatives (sentinels) per column ---")
for c in df.columns:
    if df[c].dtype.kind in 'if':
        neg = df[c][df[c]<0]
        if len(neg)>0:
            print(c, len(neg), dict(neg.value_counts().sort_index()))
