import csv, statistics as st, math
from collections import defaultdict
P="/home/user/INMA-/research-vault/backtest/out/"
daily=list(csv.DictReader(open(P+"daily_panel.csv")))
tr=list(csv.DictReader(open(P+"oracle_features.csv")))
def f(x):
    try: return float(x)
    except: return None
# is VIX identical across sym on same date?
byd=defaultdict(dict)
for r in daily: byd[r["date"]][r["sym"]]=r
diff=[abs(f(v["spx"]["vix"])-f(v["ndx"]["vix"])) for v in byd.values() if len(v)==2]
print("VIX identical across SPX/NDX same date? max abs diff =",max(diff),"on",len(diff),"paired dates")

# build per-sym ordered series, add smoothed VIX
ser=defaultdict(list)
for r in sorted(daily,key=lambda x:(x["sym"],x["date"])): ser[r["sym"]].append(r)
for sym,rows in ser.items():
    v=[f(r["vix"]) for r in rows]
    a=[abs(f(r["ret_1d_pct"])) for r in rows]
    for i,r in enumerate(rows):
        r["_vix_ma5"]=st.mean(v[max(0,i-4):i+1])
        r["_vix_ma10"]=st.mean(v[max(0,i-9):i+1])
        r["_vix_ma20"]=st.mean(v[max(0,i-19):i+1])
        r["_vix_lag5"]=v[i-5] if i>=5 else None
        r["_absret1"]=a[i]
idx={(r["sym"],r["date"]):r for r in daily}
dbym=defaultdict(list)
for r in daily: dbym[(r["sym"],r["date"][:7])].append(r)

def rank_of(row,col,key):
    vals=[r[col] if col.startswith("_") else f(r[col]) for r in dbym[key]]
    vals=[v for v in vals if v is not None]
    v=row[col] if col.startswith("_") else f(row[col])
    if v is None or not vals: return None
    lo=sum(1 for u in vals if u<v); eq=sum(1 for u in vals if u==v)
    return (lo+0.5*eq)/len(vals)

def report(col,label,rows_getter):
    rr=[];sk=0
    for r in tr:
        key=(r["sym"],r["buy_date"][:7])
        row=rows_getter(r)
        if row is None: sk+=1; continue
        rk=rank_of(row,col,key)
        if rk is None: sk+=1; continue
        rr.append(rk)
    m=st.mean(rr); se=st.pstdev(rr)/math.sqrt(len(rr))
    print(f"  {label:34s} mean={m:.3f} n={len(rr)} skipped={sk} SE={(m-0.5)/se:+.1f}")
    return m

buyrow=lambda r: idx.get((r["sym"],r["buy_date"]))
print("\nA) IS THE VIX EFFECT 'ONE-DAY RESOLUTION'? within-sym-month rank at buy day:")
for c,l in [("vix","vix same-day"),("_vix_ma5","vix 5d mean"),("_vix_ma10","vix 10d mean"),("_vix_ma20","vix 20d mean"),("_vix_lag5","vix LAGGED 5 trading days"),("_absret1","|ret_1d| (same-day realised)"),("realvol20_ann_pct","realvol20 (trailing 20d)")]:
    report(c,l,buyrow)

print("\nB) TAUTOLOGY TEST: naive 'lowest-close day of the sym-month' benchmark")
naive={}
for k,grp in dbym.items():
    naive[k]=min(grp,key=lambda r:f(r["low"]))
rr=[];rr2=[];rr3=[]
for k in naive:
    rr.append(rank_of(naive[k],"vix",k)); rr2.append(rank_of(naive[k],"realvol20_ann_pct",k)); rr3.append(rank_of(naive[k],"atr14_pct",k))
for nm,x in [("vix",rr),("realvol20",rr2),("atr14",rr3)]:
    m=st.mean(x); se=st.pstdev(x)/math.sqrt(len(x))
    print(f"  monthly-LOW day (no oracle, n={len(x)}): {nm:10s} rank={m:.3f}  SE={(m-0.5)/se:+.1f}")

print("\nC) DOES VIX SURVIVE CONDITIONING ON THE DAY'S PRICE RANK? (buys vs same-price-rank days)")
# for each buy, find days in same sym-month with close-rank within +-0.1 of buy's close-rank; compare vix rank
d=[]
for r in tr:
    key=(r["sym"],r["buy_date"][:7]); row=buyrow(r)
    if row is None: continue
    cr=rank_of(row,"low",key); vr=rank_of(row,"vix",key)
    grp=dbym[key]
    matched=[x for x in grp if abs(rank_of(x,"low",key)-cr)<=0.10]
    if len(matched)<2: continue
    exp=st.mean([rank_of(x,"vix",key) for x in matched])
    d.append(vr-exp)
m=st.mean(d); se=st.pstdev(d)/math.sqrt(len(d))
print(f"  buy-day VIX rank MINUS mean VIX rank of same-month days at same price rank: {m:+.3f} n={len(d)} SE={m/se:+.1f}")

print("\nD) within-sym-month DISPERSION, absolute (their 'barely moves' claim):")
for col in ["realvol20_ann_pct","atr14_pct","vix"]:
    iq=[]
    for k,grp in dbym.items():
        vals=sorted(f(r[col]) for r in grp)
        if len(vals)<10: continue
        n=len(vals); iq.append((vals[int(.9*n)]-vals[int(.1*n)])/st.median(vals))
    print(f"  {col:22s} median within-month p10-p90 spread / median = {st.median(iq)*100:.1f}%")
