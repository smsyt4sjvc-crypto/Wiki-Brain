import csv, statistics as st
from collections import defaultdict
tr=list(csv.DictReader(open('/home/user/INMA-/research-vault/backtest/out/oracle_features.csv')))
pan=list(csv.DictReader(open('/home/user/INMA-/research-vault/backtest/out/daily_panel.csv')))
def f(x): return float(x)
M=defaultdict(list)
for p in pan: M[(p['sym'],p['date'][:7])].append(100*(f(p['high'])-f(p['low']))/f(p['low']))
sd=[t for t in tr if int(f(t['hold_days']))==0]
rat=[];rank=[]
for t in sd:
    k=(t['sym'],t['buy_date'][:7]); m=sorted(M[k],reverse=True)
    rat.append(f(t['ret_pct'])/m[0])
    rank.append(sum(1 for x in m if x>f(t["ret_pct"])*1.0001)+1)
print("same-day leg / its OWN month's widest day: mean %.3f med %.3f min %.3f  (>=1.0: %d/%d)"%(st.mean(rat),st.median(rat),min(rat),sum(1 for x in rat if x>=0.999),len(rat)))
print("rank within own month (1=widest day):",sorted(rank))
print("is the leg-day the widest day of its month? %d/%d = %.0f%%"%(sum(1 for r in rank if r==1),len(rank),100*sum(1 for r in rank if r==1)/len(rank)))
print("median month length (days):",st.median([len(v) for v in M.values()]))
# how many months does each sym have
print("n month-sym cells:",len(M))
