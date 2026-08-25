import csv, statistics as st
OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(p) as f: return list(csv.DictReader(f))
tr=load(OUT+"oracle_features.csv"); dp=load(OUT+"daily_panel.csv")
def f(r,k):
    v=r.get(k,'')
    try: return float(v)
    except: return None
def cut(name, col, pred):
    d=[f(r,col) for r in dp]; d=[x for x in d if x is not None]
    b=[f(r,'B_'+col) for r in tr]; b=[x for x in b if x is not None]
    s=[f(r,'S_'+col) for r in tr]; s=[x for x in s if x is not None]
    br=sum(1 for x in d if pred(x))/len(d)
    bb=sum(1 for x in b if pred(x))/len(b)
    ss=sum(1 for x in s if pred(x))/len(s)
    print("%-34s base=%5.1f%% (n=%4d)  BUY=%5.1f%% (k=%3d/%d) lift=%4.2fx   SELL=%5.1f%% (k=%3d) lift=%4.2fx"%(
        name,100*br,len(d),100*bb,int(round(bb*len(b))),len(b),bb/br if br else float('nan'),
        100*ss,int(round(ss*len(s))),ss/br if br else float('nan')))

print("=== VIX LEVEL ===")
for t in [15,18,20,22,25,30]:
    cut(f"vix > {t}", 'vix', lambda x,t=t: x>t)
print("\n=== VIX 252d PERCENTILE ===")
for t in [50,60,70,75,80,90]:
    cut(f"vix_pctile_252d > {t}", 'vix_pctile_252d', lambda x,t=t: x>t)
for t in [10,20,25]:
    cut(f"vix_pctile_252d < {t}", 'vix_pctile_252d', lambda x,t=t: x<t)
print("\n=== VIX 5d CHANGE ===")
for t in [0,1,2,3,4,5]:
    cut(f"vix_chg5d > +{t}", 'vix_chg5d', lambda x,t=t: x>t)
for t in [0,-1,-2,-3]:
    cut(f"vix_chg5d < {t}", 'vix_chg5d', lambda x,t=t: x<t)
print("\n=== ATR14% ===")
for t in [1.0,1.25,1.5,2.0]:
    cut(f"atr14_pct > {t}", 'atr14_pct', lambda x,t=t: x>t)
print("\n=== REALVOL20 ===")
for t in [12,15,18,22,25]:
    cut(f"realvol20_ann_pct > {t}", 'realvol20_ann_pct', lambda x,t=t: x>t)
print("\n=== VOL vs 20d ===")
for t in [1.0,1.1,1.2,1.3]:
    cut(f"vol_vs_20d > {t}", 'vol_vs_20d', lambda x,t=t: x>t)
