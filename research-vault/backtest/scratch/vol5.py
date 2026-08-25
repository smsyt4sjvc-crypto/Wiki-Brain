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
print("sym-months in panel: %d ; oracle trade months: %d"%(len(grp),len({(t['sym'],t['month'][:7]) for t in tr})))
cols=['vix','vix_chg5d','vix_pctile_252d','atr14_pct','realvol20_ann_pct','vol_vs_20d']
def rank_pct(vals,x):
    vals=[v for v in vals if v is not None]
    if x is None or len(vals)<5: return None
    below=sum(1 for v in vals if v<x); eq=sum(1 for v in vals if v==x)
    return (below+0.5*eq)/len(vals)
print("\n=== WITHIN-MONTH PERCENTILE RANK of the buy/sell date (null = 0.500 uniform) ===")
print("%-20s %6s %8s %8s   %6s %8s %8s"%("col","n_buy","BUYmean","BUYmed","n_sell","SELLmean","SELLmed"))
for c in cols:
    br=[];sr=[]
    for t in tr:
        key=(t['sym'],t['buy_date'][:7]); vals=[f(r,c) for r in grp.get(key,[])]
        p=rank_pct(vals,f(t,'B_'+c))
        if p is not None: br.append(p)
        key=(t['sym'],t['sell_date'][:7]); vals=[f(r,c) for r in grp.get(key,[])]
        p=rank_pct(vals,f(t,'S_'+c))
        if p is not None: sr.append(p)
    se=lambda v: st.pstdev(v)/len(v)**.5
    print("%-20s %6d %8.3f %8.3f   %6d %8.3f %8.3f   (BUY dev %+.3f = %.1f SE ; SELL dev %+.3f = %.1f SE)"%(
      c,len(br),st.mean(br),st.median(br),len(sr),st.mean(sr),st.median(sr),
      st.mean(br)-.5,(st.mean(br)-.5)/se(br),st.mean(sr)-.5,(st.mean(sr)-.5)/se(sr)))
# and for price return, as the comparator
for c in ['ret_5d_pct','rsi14','close']:
    br=[];sr=[]
    for t in tr:
        key=(t['sym'],t['buy_date'][:7]); br.append(rank_pct([f(r,c) for r in grp.get(key,[])],f(t,'B_'+c)))
        key=(t['sym'],t['sell_date'][:7]); sr.append(rank_pct([f(r,c) for r in grp.get(key,[])],f(t,'S_'+c)))
    br=[x for x in br if x is not None]; sr=[x for x in sr if x is not None]
    print("%-20s %6d %8.3f %8.3f   %6d %8.3f %8.3f   [comparator]"%(c,len(br),st.mean(br),st.median(br),len(sr),st.mean(sr),st.median(sr)))

print("\n=== BUY->SELL PAIRED VIX CHANGE vs same-length random-window baseline ===")
by=defaultdict(list)
for r in dp: by[r['sym']].append(r)
for s in by: by[s].sort(key=lambda r:r['date'])
idx={(r['sym'],r['date']):i for s,rows in by.items() for i,r in enumerate(rows)}
dv=[];bv=[]
holds=[]
for t in tr:
    h=int(float(t['hold_days'])); holds.append(h)
    bv.append(f(t,'S_vix')-f(t,'B_vix'))
print("hold_days: median %d, mean %.1f, same-day(h=0) n=%d"%(st.median(holds),st.mean(holds),sum(1 for h in holds if h==0)))
print("oracle VIX change buy->sell: mean %+.2f pts, median %+.2f, n=%d ; frac falling %.1f%%"%(st.mean(bv),st.median(bv),len(bv),100*sum(1 for x in bv if x<0)/len(bv)))
# baseline: all windows of matched hold length
base=defaultdict(list)
for s,rows in by.items():
    for i,r in enumerate(rows):
        for h in set(holds):
            if i+h<len(rows): base[h].append(f(rows[i+h],'vix')-f(r,'vix'))
import statistics
exp=st.mean([st.mean(base[h]) for h in holds if base[h]])
allb=[x for h in holds for x in ([st.mean(base[h])] if base[h] else [])]
print("hold-matched random-window mean VIX change: %+.2f pts (n windows pooled=%d)"%(exp,sum(len(base[h]) for h in set(holds))))
fracfall=st.mean([sum(1 for x in base[h] if x<0)/len(base[h]) for h in holds if base[h]])
print("hold-matched baseline frac falling: %.1f%%  -> oracle lift %.2fx"%(100*fracfall,(sum(1 for x in bv if x<0)/len(bv))/fracfall))
