import csv, statistics as st, math, random
from collections import defaultdict
OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(OUT+p) as f: return list(csv.DictReader(f))
dp=load("daily_panel.csv"); tr=load("oracle_features.csv")
def fl(r,k):
    try: return float(r[k])
    except: return None
byd={(r["sym"],r["date"]):r for r in dp}
buyrows=[byd[(t["sym"],t["buy_date"])] for t in tr]
print("buy rows matched:",sum(1 for t in tr if (t["sym"],t["buy_date"]) in byd),"/",len(tr))

# ---- 1. threshold-free AUC vs all days ----
def auc(feat):
    allv=[fl(r,feat) for r in dp if fl(r,feat) is not None]
    bv=[fl(r,feat) for r in buyrows if fl(r,feat) is not None]
    allv.sort()
    import bisect
    tot=0
    for x in bv:
        lo=bisect.bisect_left(allv,x); hi=bisect.bisect_right(allv,x)
        tot+=(lo+0.5*(hi-lo))/len(allv)
    return tot/len(bv), len(bv)
print("\n--- THRESHOLD-FREE AUC (P(buy value > random all-day)) ---")
for f in ["vix","vix_chg5d","vix_pctile_252d","ret_5d_pct","rsi14","dist_sma20_pct","dd_from_20d_high_pct","atr14_pct"]:
    a,n=auc(f); print("  %-22s AUC=%.3f  |AUC-.5|=%.3f n=%d"%(f,a,abs(a-0.5),n))

# ---- 2. threshold-grid robustness of the "change beats level" claim ----
print("\n--- LIFT AT MATCHED BASE RATES (quantile-matched, not hand-picked thresholds) ---")
def qthr(feat,p):
    v=sorted(fl(r,feat) for r in dp if fl(r,feat) is not None)
    return v[int((1-p)*len(v))]
for p in [0.40,0.30,0.20,0.15,0.10,0.075,0.05,0.03]:
    row=[]
    for f in ["vix_chg5d","vix","ret_5d_pct","dist_sma20_pct"]:
        sgn = -1 if f in ("ret_5d_pct","dist_sma20_pct") else 1
        v=sorted((sgn*fl(r,f)) for r in dp if fl(r,f) is not None)
        thr=v[int((1-p)*len(v))]
        base=sum(1 for x in v if x>=thr)/len(v)
        bs=[sgn*fl(r,f) for r in buyrows if fl(r,f) is not None]
        k=sum(1 for x in bs if x>=thr); hit=k/len(bs)
        row.append("%s %.2fx(k=%d,b=%.1f%%)"%(f,hit/base,k,base*100))
    print("  top%5.1f%%: "%(p*100)+" | ".join(row))

# ---- 3. clustering: how many independent episodes drive the tail cell? ----
dates=sorted({r["date"] for r in dp})
idx={d:i for i,d in enumerate(dates)}
def episodes(rows,gap=10):
    ds=sorted({idx[r["date"]] for r in rows}); eps=[]; 
    for i in ds:
        if eps and i-eps[-1][-1]<=gap: eps[-1].append(i)
        else: eps.append([i])
    return eps
tail=[r for r in buyrows if fl(r,"vix_chg5d")>5]
tailv=[r for r in buyrows if fl(r,"vix")>25]
print("\n--- INDEPENDENCE OF THE TAIL CELLS ---")
for name,rows in [("vix_chg5d>+5",tail),("vix>25",tailv)]:
    e=episodes(rows)
    print("  %-14s trades=%d uniq_dates=%d episodes(<=10td gap)=%d  spans=%s"%(
        name,len(rows),len({r['date'] for r in rows}),len(e),
        [ (dates[x[0]][:7]) for x in e]))
print("  ALL 176 buys: uniq dates=%d episodes=%d"%(len({r['date'] for r in buyrows}),len(episodes(buyrows))))

# ---- 4. within-month rank: is VIX-level rank just price rank? ----
grp=defaultdict(list)
for r in dp: grp[(r["sym"],r["date"][:7])].append(r)
def prank(vals,x):
    n=len(vals);lt=sum(1 for v in vals if v<x);eq=sum(1 for v in vals if v==x)
    return (lt+0.5*eq)/n
# correlation on ALL days between within-month rank of vix and of close
pv=[];pc=[];pch=[]
for key,rows in grp.items():
    v=[fl(r,"vix") for r in rows]; c=[fl(r,"close") for r in rows]; ch=[fl(r,"vix_chg5d") for r in rows]
    for r in rows:
        pv.append(prank(v,fl(r,"vix"))); pc.append(prank(c,fl(r,"close"))); pch.append(prank(ch,fl(r,"vix_chg5d")))
print("\n--- WITHIN-MONTH RANK CORRELATIONS ON ALL DAYS (n=%d) ---"%len(pv))
print("  corr(rank_vix, rank_close)      = %.3f"%st.correlation(pv,pc))
print("  corr(rank_vix_chg5d, rank_close)= %.3f"%st.correlation(pch,pc))

# ---- 5. price-stratified: within month AND within price decile of that month ----
print("\n--- PRICE-STRATIFIED WITHIN-MONTH TEST ---")
# for each buy, restrict candidate days to same sym-month days whose close-rank is within +-0.10 of buy's close-rank
res_v=[];res_c=[];sizes=[]
for t in tr:
    key=(t["sym"],t["buy_date"][:7]); bd=(t["sym"],t["buy_date"])
    rows=grp[key]; br=byd[bd]
    c=[fl(r,"close") for r in rows]
    brc=prank(c,fl(br,"close"))
    cand=[r for r in rows if abs(prank(c,fl(r,"close"))-brc)<=0.15]
    if len(cand)<3: continue
    sizes.append(len(cand))
    res_v.append(prank([fl(r,"vix") for r in cand],fl(br,"vix")))
    res_c.append(prank([fl(r,"vix_chg5d") for r in cand],fl(br,"vix_chg5d")))
for nm,rs in [("vix",res_v),("vix_chg5d",res_c)]:
    m=st.mean(rs);se=st.stdev(rs)/math.sqrt(len(rs))
    print("  %-10s n=%d (dropped %d for <3 candidates) meanrank=%.3f dev=%+.3f SE=%.1f"%(nm,len(rs),len(tr)-len(rs),m,m-0.5,(m-0.5)/se))
print("  median candidate set size:",st.median(sizes))
