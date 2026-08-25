import csv, statistics as st
from collections import defaultdict
OUT='/home/user/INMA-/research-vault/backtest/out/'
D=list(csv.DictReader(open(OUT+'daily_panel.csv')))
O=list(csv.DictReader(open(OUT+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
buys=set((r['sym'],r['buy_date']) for r in O)
for r in D: r['_isbuy']=(r['sym'],r['date']) in buys
NB=sum(1 for r in D if r['_isbuy']); BASE=NB/len(D)
print("=== EXCLUSION ZONE: exact counts ===")
for name,pred in [("rsi>75",lambda r:f(r['rsi14'])>75),("rsi>80",lambda r:f(r['rsi14'])>80),
  ("bb>1.0",lambda r:f(r['bb_pctB'])>1.0),("bb>0.8",lambda r:f(r['bb_pctB'])>0.8),
  ("consec_up>=5",lambda r:f(r['consec_up_days'])>=5),
  ("rsi>75 OR bb>1.0 OR cup>=5",lambda r:f(r['rsi14'])>75 or f(r['bb_pctB'])>1.0 or f(r['consec_up_days'])>=5),
  ("bb>0.8 AND rsi>65",lambda r:f(r['bb_pctB'])>0.8 and f(r['rsi14'])>65)]:
    sub=[r for r in D if pred(r)]; k=sum(1 for r in sub if r['_isbuy'])
    print("%-30s days=%4d buys=%2d P=%.4f lift=%.2fx  excludes %.0f%% of all days, misses %.1f%% of buys"%(name,len(sub),k,k/len(sub),(k/len(sub))/BASE,100*len(sub)/len(D),100*k/NB))
# forward return of the exclusion zone
px=defaultdict(dict)
for r in D: px[r['sym']][r['date']]=f(r['close'])
dates={s:sorted(px[s]) for s in px}; idx={s:{d:i for i,d in enumerate(dates[s])} for s in px}
def fwd(s,d,h):
    i=idx[s][d]
    return None if i+h>=len(dates[s]) else 100*(px[s][dates[s][i+h]]/px[s][dates[s][i]]-1)
print("\nforward 5d/21d of exclusion zone (rsi>75 OR bb>1 OR cup>=5) vs all:")
for nm,pr in [("EXCL",lambda r:f(r['rsi14'])>75 or f(r['bb_pctB'])>1.0 or f(r['consec_up_days'])>=5),("ALL",lambda r:True)]:
    for h in (5,21):
        v=[fwd(r['sym'],r['date'],h) for r in D if pr(r)]; v=[x for x in v if x is not None]
        print("  %s h%d n=%d mean=%+.2f%% pos=%.0f%%"%(nm,h,len(v),st.mean(v),100*sum(1 for x in v if x>0)/len(v)))
