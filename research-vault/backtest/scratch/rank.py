import csv, statistics as st
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
def f(v): return None if v in ('','NA','nan',None) else float(v)
groups=defaultdict(list)   # (sym, YYYY-MM) -> rows
for r in panel: groups[(r['sym'],r['date'][:7])].append(r)
bydate={(r['sym'],r['date']):r for r in panel}
def rank_stats(feat, high_is_low_rank=False):
    """fraction of same-sym-month days with feature value BELOW the buy day's value
    -> 1.0 means buy day was the highest in its month"""
    ranks=[]; missing=0
    for t in tr:
        key=(t['sym'],t['buy_date'])
        if key not in bydate: missing+=1; continue
        g=groups[(t['sym'],t['buy_date'][:7])]
        x=f(bydate[key][feat])
        vals=[f(r[feat]) for r in g]
        vals=[v for v in vals if v is not None]
        if x is None or len(vals)<2: missing+=1; continue
        below=sum(1 for v in vals if v<x); ties=sum(1 for v in vals if v==x)
        ranks.append((below+0.5*(ties-1))/(len(vals)-1))
    return ranks, missing
for feat in ['vix','vix_pctile_252d','vix_chg5d','rsi14','close','dd_from_20d_high_pct']:
    r,m=rank_stats(feat)
    print("%-22s n=%d missing=%d  mean rank %.4f  median %.4f  frac>0.9 %.3f"%(
        feat,len(r),m,st.mean(r),st.median(r),sum(1 for x in r if x>0.9)/len(r)))
# paired difference vix_pctile - vix
rp,_=rank_stats('vix_pctile_252d'); rv,_=rank_stats('vix')
d=[a-b for a,b in zip(rp,rv)]
print("paired mean diff (pctile - vix) = %+.4f  sd %.4f  se %.4f  t=%.2f"%(
    st.mean(d),st.pstdev(d),st.pstdev(d)/len(d)**0.5, st.mean(d)/(st.pstdev(d)/len(d)**0.5)))
print("n where diff!=0:",sum(1 for x in d if abs(x)>1e-9))
# correlation of the two features within month (spearman-ish via rank diff)
