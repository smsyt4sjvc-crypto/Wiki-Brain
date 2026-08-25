import csv, statistics as st
from collections import defaultdict
OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(p) as f: return list(csv.DictReader(f))
dp=load(OUT+"daily_panel.csv"); tr=load(OUT+"oracle_features.csv")
def f(r,k):
    v=r.get(k,'')
    try: return float(v)
    except: return None
grp=defaultdict(list)
for r in dp: grp[(r['sym'],r['date'][:7])].append(r)
def rp(vals,x):
    vals=[v for v in vals if v is not None]
    if x is None or len(vals)<5: return None
    return (sum(1 for v in vals if v<x)+0.5*sum(1 for v in vals if v==x))/len(vals)

# 1) PRICE-NULL: the month's lowest-low day / highest-high day -- what VIX rank does pure price selection give?
print("=== PRICE-ONLY NULL (month's extreme price day) vs ACTUAL ORACLE, within-month VIX rank ===")
for col in ['vix','vix_chg5d','vix_pctile_252d','atr14_pct','realvol20_ann_pct','vol_vs_20d']:
    lows=[];highs=[]
    for key,rows in grp.items():
        vals=[f(r,col) for r in rows]
        lo=min(rows,key=lambda r:f(r,'low')); hi=max(rows,key=lambda r:f(r,'high'))
        a=rp(vals,f(lo,col)); b=rp(vals,f(hi,col))
        if a is not None: lows.append(a)
        if b is not None: highs.append(b)
    bo=[];so=[]
    for t in tr:
        bo.append(rp([f(r,col) for r in grp[(t['sym'],t['buy_date'][:7])]],f(t,'B_'+col)))
        so.append(rp([f(r,col) for r in grp[(t['sym'],t['sell_date'][:7])]],f(t,'S_'+col)))
    bo=[x for x in bo if x is not None]; so=[x for x in so if x is not None]
    print("%-20s price-null LOW-day %.3f (n=%d) | oracle BUY %.3f (n=%d) | price-null HIGH-day %.3f | oracle SELL %.3f"%(
      col,st.mean(lows),len(lows),st.mean(bo),len(bo),st.mean(highs),st.mean(so)))

# 2) within-month: predict vix rank from close rank (pooled daily mapping), compare buys
print("\n=== VIX rank RESIDUAL vs within-month CLOSE rank (pooled bins from all daily rows) ===")
pts=[]
for key,rows in grp.items():
    cl=[f(r,'close') for r in rows]
    for col in ['vix','vix_chg5d','atr14_pct','vol_vs_20d']:
        pass
    for r in rows:
        pts.append((rp(cl,f(r,'close')), {c:rp([f(x,c) for x in rows],f(r,c)) for c in ['vix','vix_chg5d','atr14_pct','vol_vs_20d','realvol20_ann_pct']}))
pts=[p for p in pts if p[0] is not None]
NB=10
bins=defaultdict(list)
for cr,d in pts: bins[min(NB-1,int(cr*NB))].append(d)
for col in ['vix','vix_chg5d','atr14_pct','vol_vs_20d','realvol20_ann_pct']:
    prof={b:st.mean([d[col] for d in v if d[col] is not None]) for b,v in bins.items()}
    resb=[];ress=[]
    for t in tr:
        rows=grp[(t['sym'],t['buy_date'][:7])]; cr=rp([f(r,'close') for r in rows],f(t,'B_close'))
        vr=rp([f(r,col) for r in rows],f(t,'B_'+col))
        if cr is not None and vr is not None: resb.append(vr-prof[min(NB-1,int(cr*NB))])
        rows=grp[(t['sym'],t['sell_date'][:7])]; cr=rp([f(r,'close') for r in rows],f(t,'S_close'))
        vr=rp([f(r,col) for r in rows],f(t,'S_'+col))
        if cr is not None and vr is not None: ress.append(vr-prof[min(NB-1,int(cr*NB))])
    se=lambda v: st.pstdev(v)/len(v)**.5
    print("%-20s BUY resid %+.3f (%.1f SE, n=%d)   SELL resid %+.3f (%.1f SE, n=%d)"%(
      col,st.mean(resb),st.mean(resb)/se(resb),len(resb),st.mean(ress),st.mean(ress)/se(ress),len(ress)))
    print("    (price-rank profile of %s across close-rank deciles: %s)"%(col," ".join("%.2f"%prof[b] for b in range(NB))))

# 3) vol_vs_20d vs |ret_1d| control
print("\n=== vol_vs_20d controlled for |1-day move| ===")
d=[(abs(f(r,'ret_1d_pct')),f(r,'vol_vs_20d')) for r in dp if f(r,'vol_vs_20d') is not None and f(r,'ret_1d_pct') is not None]
xs=[a for a,b in d]; ys=[b for a,b in d]
mx=st.mean(xs);my=st.mean(ys)
sl=sum((a-mx)*(b-my) for a,b in d)/sum((a-mx)**2 for a in xs); ic=my-sl*mx
res=[b-(ic+sl*a) for a,b in d]
print("corr=%.3f slope=%.3f  daily resid sd=%.3f"%(sum((a-mx)*(b-my) for a,b in d)/((sum((a-mx)**2 for a in xs)*sum((b-my)**2 for b in ys))**.5),sl,st.pstdev(res)))
br=[f(t,'B_vol_vs_20d')-(ic+sl*abs(f(t,'B_ret_1d_pct'))) for t in tr if f(t,'B_vol_vs_20d') is not None]
sr=[f(t,'S_vol_vs_20d')-(ic+sl*abs(f(t,'S_ret_1d_pct'))) for t in tr if f(t,'S_vol_vs_20d') is not None]
sd=st.pstdev(res)
print("BUY resid mean %+.4f (%.2f sd, n=%d) | SELL resid mean %+.4f (%.2f sd, n=%d)"%(st.mean(br),st.mean(br)/sd,len(br),st.mean(sr),st.mean(sr)/sd,len(sr)))
