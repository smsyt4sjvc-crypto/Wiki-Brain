import csv, statistics as st
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
def f(v): return None if v in ('','NA','nan',None) else float(v)
# independence check
print("distinct buy dates:",len(set(t['buy_date'] for t in tr)),"of",len(tr))
print("distinct sym-months:",len(set((t['sym'],t['buy_date'][:7]) for t in tr)))
dd=defaultdict(int)
for t in tr: dd[t['buy_date']]+=1
print("buy dates shared by both syms (dupes):",sum(1 for k,v in dd.items() if v>1))
# incremental: within raw-VIX terciles, does pctile still separate buys from all days?
vv=sorted(f(r['vix']) for r in panel)
q=[vv[len(vv)//3],vv[2*len(vv)//3]]
print("vix terciles cut at %.2f %.2f"%(q[0],q[1]))
def bucket(x): return 0 if x<=q[0] else (1 if x<=q[1] else 2)
for b in range(3):
    pool=[f(r['vix_pctile_252d']) for r in panel if bucket(f(r['vix']))==b]
    buys=[f(t['B_vix_pctile_252d']) for t in tr if bucket(f(t['B_vix']))==b]
    if not buys: continue
    thr=st.median(pool)
    base=sum(1 for x in pool if x>thr)/len(pool)
    hit=sum(1 for x in buys if x>thr)/len(buys)
    print(" vix bucket %d: pool n=%d buys n=%d  median-pctile-thr %.1f  base %.3f buys %.3f lift %.2fx"%(
        b,len(pool),len(buys),thr,base,hit,hit/base))
# reverse: within pctile terciles, does raw vix still separate?
pp=sorted(f(r['vix_pctile_252d']) for r in panel)
p=[pp[len(pp)//3],pp[2*len(pp)//3]]
def pb(x): return 0 if x<=p[0] else (1 if x<=p[1] else 2)
print("pctile terciles cut at %.2f %.2f"%(p[0],p[1]))
for b in range(3):
    pool=[f(r['vix']) for r in panel if pb(f(r['vix_pctile_252d']))==b]
    buys=[f(t['B_vix']) for t in tr if pb(f(t['B_vix_pctile_252d']))==b]
    if not buys: continue
    thr=st.median(pool)
    base=sum(1 for x in pool if x>thr)/len(pool)
    hit=sum(1 for x in buys if x>thr)/len(buys)
    print(" pctile bucket %d: pool n=%d buys n=%d  base %.3f buys %.3f lift %.2fx"%(
        b,len(pool),len(buys),base,hit,hit/base))
# TAUTOLOGY probe: high VIX at buy vs high VIX at SELL (sells are chosen because rally ENDED)
for k,lab in [('B_vix','buy'),('S_vix','sell')]:
    x=[f(t[k]) for t in tr]; print("%s vix mean %.2f  frac>20 %.3f"%(lab,st.mean(x),sum(1 for v in x if v>20)/len(x)))
for k,lab in [('B_vix_pctile_252d','buy'),('S_vix_pctile_252d','sell')]:
    x=[f(t[k]) for t in tr]; print("%s pctile mean %.2f  frac>80 %.3f"%(lab,st.mean(x),sum(1 for v in x if v>80)/len(x)))
