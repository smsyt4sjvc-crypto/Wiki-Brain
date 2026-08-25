import csv, statistics as st
from collections import defaultdict
B='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(B+'daily_panel.csv')))
tr=list(csv.DictReader(open(B+'oracle_features.csv')))
def f(x):
    try: return float(x)
    except: return None
FEATS=['dist_sma20_pct','dist_sma50_pct','dist_sma200_pct','dd_from_20d_high_pct','dd_from_63d_high_pct','dd_from_252d_high_pct','up_from_20d_low_pct','up_from_63d_low_pct','up_from_252d_low_pct','rsi14','ret_20d_pct','ret_5d_pct']
def q(v,p):
    v=sorted(v); i=(len(v)-1)*p; lo=int(i); hi=min(lo+1,len(v)-1)
    return v[lo]+(v[hi]-lo*0+0)*0 if False else v[lo]+(v[hi]-v[lo])*(i-lo)
print("=== DIST: buys vs all days vs sells ===")
print(f"{'feat':26s} {'buyMed':>8s} {'dayMed':>8s} {'sellMed':>8s} {'buyMean':>8s} {'dayMean':>8s} {'buyQ25':>8s} {'buyQ75':>8s} {'dayQ25':>8s} {'dayQ75':>8s}")
for c in FEATS:
    d=[f(r[c]) for r in panel]; d=[x for x in d if x is not None]
    b=[f(r['B_'+c]) for r in tr]; b=[x for x in b if x is not None]
    s=[f(r['S_'+c]) for r in tr]; s=[x for x in s if x is not None]
    print(f"{c:26s} {st.median(b):8.2f} {st.median(d):8.2f} {st.median(s):8.2f} {st.mean(b):8.2f} {st.mean(d):8.2f} {q(b,.25):8.2f} {q(b,.75):8.2f} {q(d,.25):8.2f} {q(d,.75):8.2f}")

print("\n=== BINARY SHARES: buys vs base rate ===")
def share(pred_day,pred_buy,label):
    d=sum(1 for r in panel if pred_day(r))/len(panel)
    b=sum(1 for r in tr if pred_buy(r))/len(tr)
    s=sum(1 for r in tr if pred_buy(r,'S_'))/len(tr) if pred_buy.__code__.co_argcount>1 else None
    print(f"{label:38s} buy {b*100:6.1f}%  base {d*100:6.1f}%  lift {b/d if d else float('nan'):5.2f}x")
def mk(col,op,thr):
    if op=='<': return (lambda r: f(r[col]) is not None and f(r[col])<thr), (lambda r,p='B_': f(r[p+col]) is not None and f(r[p+col])<thr)
    return (lambda r: f(r[col]) is not None and f(r[col])>thr), (lambda r,p='B_': f(r[p+col]) is not None and f(r[p+col])>thr)
for col,op,thr in [('dist_sma200_pct','<',0),('dist_sma200_pct','<',-5),('dist_sma50_pct','<',0),('dist_sma20_pct','<',0),('dist_sma20_pct','<',-2),
                   ('dd_from_20d_high_pct','<',-3),('dd_from_20d_high_pct','<',-5),('dd_from_63d_high_pct','<',-5),('dd_from_252d_high_pct','<',-5),('dd_from_252d_high_pct','<',-10),
                   ('dd_from_252d_high_pct','>',-1),('dist_sma20_pct','>',2),('up_from_20d_low_pct','<',1)]:
    pd_,pb=mk(col,op,thr); share(pd_,pb,f"{col} {op} {thr}")
