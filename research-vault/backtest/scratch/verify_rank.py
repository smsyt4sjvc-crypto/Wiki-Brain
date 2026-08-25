import csv, statistics as st, math
from collections import defaultdict
OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(OUT+p) as f: return list(csv.DictReader(f))
dp=load("daily_panel.csv"); tr=load("oracle_features.csv")
def fl(r,k):
    try: return float(r[k])
    except: return None
# group daily by sym+month
grp=defaultdict(list)
for r in dp:
    grp[(r["sym"],r["date"][:7])].append(r)
byd={(r["sym"],r["date"]):r for r in dp}

def prank(vals,x):
    n=len(vals); lt=sum(1 for v in vals if v<x); eq=sum(1 for v in vals if v==x)
    return (lt+0.5*eq)/n

for feat in ["vix","vix_chg5d","rsi14","dist_sma20_pct","atr14_pct","realvol20_ann_pct","close","dd_from_20d_high_pct"]:
    rs=[]; miss=0
    for t in tr:
        key=(t["sym"],t["buy_date"][:7]); bd=(t["sym"],t["buy_date"])
        if key not in grp or bd not in byd: miss+=1; continue
        x=fl(byd[bd],feat)
        vals=[fl(r,feat) for r in grp[key] if fl(r,feat) is not None]
        if x is None or len(vals)<2: miss+=1; continue
        rs.append(prank(vals,x))
    m=st.mean(rs); sd=st.stdev(rs); se=sd/math.sqrt(len(rs))
    print("%-22s n=%d dropped=%d meanrank=%.3f dev=%+.3f sd=%.3f SEunits(emp)=%.1f SEunits(unif)=%.1f"%(
        feat,len(rs),miss,m,m-0.5,sd,(m-0.5)/se,(m-0.5)/(math.sqrt(1/12)/math.sqrt(len(rs)))))
