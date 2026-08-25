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
print("=== EPISODE COUNT for the 'below 200DMA' and 'deep dd' subsamples (autocorrelation honesty) ===")
for lbl,sel in [('below200',lambda r: f(r['dist_sma200_pct'])<=0),('dd252<-15',lambda r: f(r['dd_from_252d_high_pct'])<-15),('dd20<-7',lambda r: f(r['dd_from_20d_high_pct'])<-7)]:
    for s,ds in ser.items():
        runs=[];cur=[]
        for d in ds:
            if sel(d): cur.append(d['date'])
            else:
                if cur: runs.append(cur); cur=[]
        if cur: runs.append(cur)
        print(f"  {lbl:12s} {s}: {sum(len(r) for r in runs):4d} days in {len(runs)} runs -> " + ", ".join(f"{r[0]}..{r[-1]}({len(r)})" for r in runs))
print("\n=== the 5 sym-months with median dist_sma200<=0 ===")
bym=defaultdict(list)
for r in panel: bym[(r['sym'],r['date'][:7])].append(r)
for k,ds in sorted(bym.items()):
    m=st.median([f(d['dist_sma200_pct']) for d in ds])
    if m<=0: print("  ",k,f"med dist200 {m:.2f}  minDd252 {min(f(d['dd_from_252d_high_pct']) for d in ds):.2f}")
print("\n=== BUY vs SELL asymmetry, within-month percentile ===")
for c in ['dist_sma20_pct','dist_sma50_pct','dist_sma200_pct','dd_from_20d_high_pct','dd_from_252d_high_pct','rsi14']:
    for p in ['B_','S_']:
        ps=[]
        for t in tr:
            days=bym[(t['sym'],t['month'])]; vals=[f(d[c]) for d in days if f(d[c]) is not None]; v=f(t[p+c])
            below=sum(1 for x in vals if x<v); tie=sum(1 for x in vals if x==v)
            ps.append((below+0.5*tie)/len(vals))
        print(f"  {p+c:28s} meanPct {st.mean(ps):.3f}", end='')
    print()
print("\n=== above/below SMA shares: buy, sell, base ===")
for c,thr in [('dist_sma20_pct',0),('dist_sma50_pct',0),('dist_sma200_pct',0)]:
    b=sum(1 for t in tr if f(t['B_'+c])<thr)/len(tr); s=sum(1 for t in tr if f(t['S_'+c])<thr)/len(tr)
    d=sum(1 for r in panel if f(r[c])<thr)/len(panel)
    print(f"  {c:20s} below: buy {b*100:5.1f}%  sell {s*100:5.1f}%  base {d*100:5.1f}%   lift_buy {b/d:.2f}x lift_sell {s/d:.2f}x")
print("\n=== how many buys are in a 'real correction' state? ===")
for lbl,sel in [('B_dd252 < -10%',lambda t: f(t['B_dd_from_252d_high_pct'])<-10),('B_dd252 < -15%',lambda t: f(t['B_dd_from_252d_high_pct'])<-15),('B below 200DMA',lambda t: f(t['B_dist_sma200_pct'])<0),('B_dd252 > -2% (near high)',lambda t: f(t['B_dd_from_252d_high_pct'])>-2)]:
    n=sum(1 for t in tr if sel(t)); print(f"  {lbl:26s} {n:3d}/176 = {n/176*100:.1f}%")
for lbl,sel in [('dd252 < -10%',lambda r: f(r['dd_from_252d_high_pct'])<-10),('dd252 < -15%',lambda r: f(r['dd_from_252d_high_pct'])<-15),('below 200DMA',lambda r: f(r['dist_sma200_pct'])<0),('dd252 > -2%',lambda r: f(r['dd_from_252d_high_pct'])>-2)]:
    n=sum(1 for r in panel if sel(r)); print(f"  base {lbl:21s} {n:4d}/1817 = {n/1817*100:.1f}%")
