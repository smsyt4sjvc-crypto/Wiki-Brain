import csv, json, statistics as st
from collections import defaultdict
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
trades=json.load(open(OUT+'oracle_trades.json'))
sells={(t['sym'],t['sell_date']) for t in trades}; buys={(t['sym'],t['buy_date']) for t in trades}
bys=defaultdict(list)
for r in panel: bys[r['sym']].append(r)
for s in bys:
    bys[s].sort(key=lambda r:r['date'])
    rr=bys[s]
    for h in (5,10,21):
        for i,r in enumerate(rr): r['fwd%d'%h]=100*(float(rr[i+h]['close'])/float(r['close'])-1) if i+h<len(rr) else None
rows=[r for s in bys for r in bys[s]]
for r in rows:
    r['_s']=(r['sym'],r['date']) in sells; r['_b']=(r['sym'],r['date']) in buys
N=len(rows); bs=len(sells)/N; bb=len(buys)/N

print("=== A. MATCHED-PREVALENCE COMPARISON (kill the lift-vs-lift claim) ===")
print("lift is bounded by 1/prevalence. Compare at IDENTICAL n instead.\n")
for k in (100,139,200,300,461):
    hi=sorted(rows,key=lambda r:-float(r['rsi14']))[:k]
    lo=sorted(rows,key=lambda r:float(r['rsi14']))[:k]
    sh=sum(1 for r in hi if r['_s']); bl=sum(1 for r in lo if r['_b'])
    print(f" top/bottom {k:4d} RSI days: SELL {sh:3d}/{k} = {100*sh/k:5.2f}% lift {sh/k/bs:4.2f}x  |  BUY {bl:3d}/{k} = {100*bl/k:5.2f}% lift {bl/k/bb:4.2f}x")
print()
for k in (139,461):
    hi=sorted(rows,key=lambda r:float(r['dd_from_20d_high_pct']),reverse=True)[:k]   # closest to 20d high
    lo=sorted(rows,key=lambda r:float(r['up_from_20d_low_pct']))[:k]                 # closest to 20d low
    sh=sum(1 for r in hi if r['_s']); bl=sum(1 for r in lo if r['_b'])
    print(f" {k:4d} days nearest 20d-high/low: SELL lift {sh/k/bs:4.2f}x ({sh}/{k})  |  BUY lift {bl/k/bb:4.2f}x ({bl}/{k})")

print("\nRECALL (prevalence-free): frac of oracle events captured by the flag")
h20=[r for r in rows if float(r['is_20d_high'])==1]; l20=[r for r in rows if float(r['is_20d_low'])==1]
print(f"  is_20d_high: prevalence {100*len(h20)/N:5.2f}%  recall {100*sum(1 for r in h20 if r['_s'])/len(sells):5.1f}%  lift {(sum(1 for r in h20 if r['_s'])/len(h20))/bs:.2f}x  ceiling {N/len(h20):.2f}x  = {100*((sum(1 for r in h20 if r['_s'])/len(h20))/bs)/(N/len(h20)):.0f}% of ceiling")
print(f"  is_20d_low : prevalence {100*len(l20)/N:5.2f}%  recall {100*sum(1 for r in l20 if r['_b'])/len(buys):5.1f}%  lift {(sum(1 for r in l20 if r['_b'])/len(l20))/bb:.2f}x  ceiling {N/len(l20):.2f}x  = {100*((sum(1 for r in l20 if r['_b'])/len(l20))/bb)/(N/len(l20)):.0f}% of ceiling")

print("\n=== B. THE 5-DAY HORIZON THE CLAIM DID NOT REPORT ===")
allv=[r['fwd5'] for r in rows if r['fwd5'] is not None]
print(f"  ALL days      fwd5 mean {st.mean(allv):+.3f}%  n={len(allv)}")
for lab,thr in [("rsi>65",65),("rsi>70",70),("rsi>75",75),("rsi>80",80)]:
    v=[r['fwd5'] for r in rows if float(r['rsi14'])>thr and r['fwd5'] is not None]
    print(f"  {lab:10s}    fwd5 mean {st.mean(v):+.3f}%  n={len(v):3d}  diff vs base {st.mean(v)-st.mean(allv):+.3f}%  %pos {100*sum(1 for x in v if x>0)/len(v):.1f}%")

print("\n=== C. YEAR STABILITY of 'RSI>70 has ABOVE-average fwd returns' ===")
for h in (5,10,21):
    print(f" horizon {h}d:")
    for y in ('2023','2024','2025','2026'):
        v=[r['fwd%d'%h] for r in rows if r['date'][:4]==y and float(r['rsi14'])>70 and r['fwd%d'%h] is not None]
        a=[r['fwd%d'%h] for r in rows if r['date'][:4]==y and r['fwd%d'%h] is not None]
        print(f"   {y}: n={len(v):4d} rsi>70 {st.mean(v):+7.3f}%  base {st.mean(a):+7.3f}%  EXCESS {st.mean(v)-st.mean(a):+7.3f}%")
    v=[r['fwd%d'%h] for r in rows if r['date'][:4]!='2026' and float(r['rsi14'])>70 and r['fwd%d'%h] is not None]
    a=[r['fwd%d'%h] for r in rows if r['date'][:4]!='2026' and r['fwd%d'%h] is not None]
    print(f"   EX-2026 pooled: n={len(v)} rsi>70 {st.mean(v):+.3f}%  base {st.mean(a):+.3f}%  EXCESS {st.mean(v)-st.mean(a):+.3f}%  <-- sign flips")
