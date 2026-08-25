import csv, statistics as st, math
from collections import defaultdict
P="/home/user/INMA-/research-vault/backtest/out/"
daily=list(csv.DictReader(open(P+"daily_panel.csv")))
tr=list(csv.DictReader(open(P+"oracle_features.csv")))
print("daily rows",len(daily),"trades",len(tr))
def f(x):
    try: return float(x)
    except: return None

# --- 1. base rates / means
for col in ["realvol20_ann_pct","atr14_pct","vix","vix_pctile_252d"]:
    dv=[f(r[col]) for r in daily]; dv=[v for v in dv if v is not None]
    bv=[f(r["B_"+col]) for r in tr]; miss=sum(1 for v in bv if v is None); bv=[v for v in bv if v is not None]
    print(f"{col}: daily n={len(dv)} mean={st.mean(dv):.3f} med={st.median(dv):.3f} | buys n={len(bv)} (miss {miss}) mean={st.mean(bv):.3f} med={st.median(bv):.3f}")

# --- 2. threshold cuts, all days
def cut(col,thr,op=">"):
    dv=[f(r[col]) for r in daily]; dv=[v for v in dv if v is not None]
    bv=[f(r["B_"+col]) for r in tr]; bv=[v for v in bv if v is not None]
    if op==">":
        b=sum(1 for v in dv if v>thr)/len(dv); k=sum(1 for v in bv if v>thr)
    p=k/len(bv)
    print(f"  {col}>{thr}: base {b*100:.1f}%  buys {p*100:.1f}% (k={k}/{len(bv)})  lift {p/b:.2f}x")
print("\nthreshold cuts (all days denominator):")
for t in [18,22,25]: cut("realvol20_ann_pct",t)
for t in [1.5,2.0]: cut("atr14_pct",t)
for t in [18,20,25]: cut("vix",t)

# --- 3. within-sym-month rank
dbym=defaultdict(list)
for r in daily:
    dbym[(r["sym"],r["date"][:7])].append(r)
def wrank(col,tcol):
    rr=[]; skipped=0
    for r in tr:
        key=(r["sym"],r["buy_date"][:7])
        grp=dbym.get(key)
        if not grp: skipped+=1; continue
        vals=[f(x[col]) for x in grp]; vals=[v for v in vals if v is not None]
        v=f(r[tcol])
        if v is None or not vals: skipped+=1; continue
        # midrank fraction
        lo=sum(1 for u in vals if u<v); eq=sum(1 for u in vals if u==v)
        rk=(lo+0.5*eq)/len(vals)
        rr.append(rk)
    return rr,skipped
print("\nwithin-sym-month rank of BUY day (null=0.500):")
res={}
for col in ["realvol20_ann_pct","atr14_pct","vix","vix_pctile_252d","vix_chg5d","close","low","rsi14","ret_1d_pct","dd_from_20d_high_pct"]:
    rr,sk=wrank(col,"B_"+col)
    m=st.mean(rr); sd=st.pstdev(rr); se=sd/math.sqrt(len(rr))
    res[col]=rr
    print(f"  {col:22s} mean={m:.3f} sd={sd:.3f} n={len(rr)} skipped={sk}  SE_iid={(m-0.5)/se:+.1f}")
    # cluster by sym-month (2 legs each) -> cluster-robust
    cl=defaultdict(list)
    for r,rk in zip([x for x in tr],rr): pass
print()
# cluster-robust for key cols
def clustered(col):
    rr=[];keys=[]
    for r in tr:
        key=(r["sym"],r["buy_date"][:7]); grp=dbym.get(key)
        if not grp: continue
        vals=[f(x[col]) for x in grp]; vals=[v for v in vals if v is not None]
        v=f(r["B_"+col])
        if v is None: continue
        lo=sum(1 for u in vals if u<v); eq=sum(1 for u in vals if u==v)
        rr.append((lo+0.5*eq)/len(vals)); keys.append(key)
    g=defaultdict(list)
    for k,v in zip(keys,rr): g[k].append(v)
    means=[st.mean(v) for v in g.values()]
    m=st.mean(rr); se=st.pstdev(means)/math.sqrt(len(means))
    print(f"  {col:22s} cluster n={len(means)} mean={m:.3f} SE_clu={(m-0.5)/se:+.1f}")
print("cluster-robust (sym-month clusters):")
for c in ["realvol20_ann_pct","atr14_pct","vix","vix_pctile_252d"]: clustered(c)

# --- 4. how much do these vary WITHIN a sym-month? (their mechanism claim)
print("\nwithin-sym-month dispersion (median across months of [max-min]/median):")
for col in ["realvol20_ann_pct","atr14_pct","vix","vix_pctile_252d","close"]:
    rel=[]
    for k,grp in dbym.items():
        vals=[f(x[col]) for x in grp]; vals=[v for v in vals if v is not None]
        if len(vals)<5: continue
        md=st.median(vals)
        if md==0: continue
        rel.append((max(vals)-min(vals))/abs(md))
    print(f"  {col:22s} median rel range={st.median(rel)*100:.1f}%  (n months={len(rel)})")
