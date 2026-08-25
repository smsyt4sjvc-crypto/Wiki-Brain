import csv, statistics as st
from collections import Counter, defaultdict

OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(p) as f: return list(csv.DictReader(f))
tr=load(OUT+"oracle_features.csv"); dp=load(OUT+"daily_panel.csv")
print("trades",len(tr),"daily",len(dp))
print("syms daily",Counter(r['sym'] for r in dp), "syms trades",Counter(r['sym'] for r in tr))
def f(r,k):
    v=r.get(k,'')
    if v is None or v=='' or v=='nan': return None
    try: return float(v)
    except: return None
# missingness on vol cols
cols=['vix','vix_chg5d','vix_pctile_252d','atr14_pct','realvol20_ann_pct','vol_vs_20d']
for c in cols:
    dm=sum(1 for r in dp if f(r,c) is None)
    bm=sum(1 for r in tr if f(r,'B_'+c) is None)
    sm=sum(1 for r in tr if f(r,'S_'+c) is None)
    print(f"{c:22s} daily_missing={dm:4d} B_missing={bm:3d} S_missing={sm:3d}")
# distribution summary
def q(xs,p):
    xs=sorted(xs); i=p*(len(xs)-1); lo=int(i); hi=min(lo+1,len(xs)-1); return xs[lo]+(xs[hi]-xs[lo])*(i-lo)
print("\n%-22s %8s %8s %8s %8s %8s %8s"%("col/src","n","mean","p10","p25","med","p75"))
for c in cols:
    for lbl,vals in [("daily",[f(r,c) for r in dp]),("BUY",[f(r,'B_'+c) for r in tr]),("SELL",[f(r,'S_'+c) for r in tr])]:
        v=[x for x in vals if x is not None]
        print("%-22s %8d %8.2f %8.2f %8.2f %8.2f %8.2f"%(c+"/"+lbl,len(v),st.mean(v),q(v,.10),q(v,.25),q(v,.50),q(v,.75)))
