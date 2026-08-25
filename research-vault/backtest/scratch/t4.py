import csv, statistics as st
from collections import defaultdict
B='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(B+'daily_panel.csv')))
tr=list(csv.DictReader(open(B+'oracle_features.csv')))
def f(x):
    try: return float(x)
    except: return None
ser=defaultdict(list)
for r in panel: ser[r['sym']].append(r)
for s in ser: ser[s].sort(key=lambda r:r['date'])
H=10
rows=[]; dropped=0
for s,ds in ser.items():
    for i,d in enumerate(ds):
        if i+H>=len(ds): dropped+=1; continue
        c=f(d['close']); fut=ds[i+1:i+1+H]
        mx=max(f(x['high']) for x in fut)
        d2=dict(d); d2['fwd_maxup10']=(mx/c-1)*100
        d2['fwd_r5']=(f(ds[i+5]['close'])/c-1)*100
        d2['fwd_r10']=(f(ds[i+H]['close'])/c-1)*100
        rows.append(d2)
print(f"forward-return panel: {len(rows)} days (dropped {dropped} = last {H} days of each index; no lookahead available)")
def rep(label, sel):
    ss=[r for r in rows if sel(r)]
    if len(ss)<15: print(f"{label:42s} n={len(ss):4d}  (too few)"); return
    print(f"{label:42s} n={len(ss):4d}  medMaxUp10 {st.median([r['fwd_maxup10'] for r in ss]):6.2f}%  meanMaxUp10 {st.mean([r['fwd_maxup10'] for r in ss]):6.2f}%  medFwd5 {st.median([r['fwd_r5'] for r in ss]):6.2f}%  medFwd10 {st.median([r['fwd_r10'] for r in ss]):6.2f}%")
print("\n=== BASE: forward oracle-achievable upside by TREND/STRUCTURE bucket (ALL days, not oracle days) ===")
rep("ALL DAYS", lambda r: True)
print("-- by 200DMA --")
rep("above 200DMA", lambda r: f(r['dist_sma200_pct'])>0)
rep("below 200DMA", lambda r: f(r['dist_sma200_pct'])<=0)
print("-- by 20d drawdown --")
for lo,hi,lb in [(-1e9,-7,'dd20 < -7%'),(-7,-5,'dd20 -7..-5%'),(-5,-3,'dd20 -5..-3%'),(-3,-1,'dd20 -3..-1%'),(-1,1e9,'dd20 > -1%')]:
    rep(lb, lambda r,lo=lo,hi=hi: lo<=f(r['dd_from_20d_high_pct'])<hi)
print("-- DIP x TREND interaction (the anti-tautology test) --")
for tl,tsel in [('above200',lambda r: f(r['dist_sma200_pct'])>0),('below200',lambda r: f(r['dist_sma200_pct'])<=0)]:
    for lo,hi,lb in [(-1e9,-3,'dd20<-3'),(-3,1e9,'dd20>=-3')]:
        rep(f"{tl} & {lb}", lambda r,ts=tsel,lo=lo,hi=hi: ts(r) and lo<=f(r['dd_from_20d_high_pct'])<hi)
print("-- by 252d drawdown --")
for lo,hi,lb in [(-1e9,-15,'dd252 < -15%'),(-15,-7,'dd252 -15..-7%'),(-7,-3,'dd252 -7..-3%'),(-3,1e9,'dd252 > -3%')]:
    rep(lb, lambda r,lo=lo,hi=hi: lo<=f(r['dd_from_252d_high_pct'])<hi)

print("\n=== AMONG DIP DAYS ONLY (dd20<-3): does the oracle pick the uptrend dips? ===")
dip_days=[r for r in panel if f(r['dd_from_20d_high_pct'])<-3]
dip_tr=[t for t in tr if f(t['B_dd_from_20d_high_pct'])<-3]
print(f"dip days n={len(dip_days)}  share above200 = {sum(1 for r in dip_days if f(r['dist_sma200_pct'])>0)/len(dip_days)*100:.1f}%   med dist200 {st.median([f(r['dist_sma200_pct']) for r in dip_days]):.2f}")
print(f"oracle dip buys n={len(dip_tr)}  share above200 = {sum(1 for t in dip_tr if f(t['B_dist_sma200_pct'])>0)/len(dip_tr)*100:.1f}%   med dist200 {st.median([f(t['B_dist_sma200_pct']) for t in dip_tr]):.2f}")
print("\n=== within oracle: does buy-date structure predict the trade's return? (spearman-ish by quartile) ===")
for c in ['B_dd_from_252d_high_pct','B_dd_from_20d_high_pct','B_dist_sma200_pct','B_dist_sma20_pct','B_rsi14']:
    vs=sorted(tr,key=lambda t:f(t[c])); q=len(vs)//4
    qs=[vs[:q],vs[q:2*q],vs[2*q:3*q],vs[3*q:]]
    print(f"{c:26s} " + "  ".join(f"Q{i+1} med{st.median([f(t['ret_pct']) for t in g]):5.2f}%(n{len(g)})" for i,g in enumerate(qs)))
