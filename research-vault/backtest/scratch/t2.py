import csv, statistics as st
from collections import defaultdict
B='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(B+'daily_panel.csv')))
tr=list(csv.DictReader(open(B+'oracle_features.csv')))
def f(x):
    try: return float(x)
    except: return None
# index panel by sym-month
bym=defaultdict(list)
for r in panel:
    bym[(r['sym'], r['date'][:7])].append(r)
print("sym-months in panel:", len(bym), " trades:", len(tr), " sym-months in trades:", len(set((t['sym'],t['month']) for t in tr)))
FE=['dist_sma20_pct','dist_sma50_pct','dist_sma200_pct','dd_from_20d_high_pct','dd_from_63d_high_pct','dd_from_252d_high_pct','up_from_20d_low_pct','rsi14']
print("\n=== WITHIN-MONTH PERCENTILE RANK of the BUY-day feature (0=lowest in its own month, 0.5=random day) ===")
print(f"{'feat':26s} {'meanPct':>8s} {'medPct':>8s} {'n':>5s}  {'<=0.25 share':>12s}  {'==min share':>11s}")
res={}
for c in FE:
    ps=[]; low=0; mn=0
    for t in tr:
        days=bym[(t['sym'],t['month'])]
        vals=[f(d[c]) for d in days if f(d[c]) is not None]
        v=f(t['B_'+c])
        if v is None or not vals: continue
        # percentile = fraction of month days strictly below, + half ties
        below=sum(1 for x in vals if x<v); tie=sum(1 for x in vals if x==v)
        p=(below+0.5*tie)/len(vals)
        ps.append(p)
        if p<=0.25: low+=1
        if v<=min(vals)+1e-9: mn+=1
    res[c]=ps
    print(f"{c:26s} {st.mean(ps):8.3f} {st.median(ps):8.3f} {len(ps):5d}  {low/len(ps)*100:11.1f}% {mn/len(ps)*100:10.1f}%")

print("\n=== SAME, split leg1 / leg2 ===")
for leg in ['1','2']:
    sub=[t for t in tr if t['leg']==leg]
    out=[]
    for c in FE:
        ps=[]
        for t in sub:
            days=bym[(t['sym'],t['month'])]; vals=[f(d[c]) for d in days if f(d[c]) is not None]; v=f(t['B_'+c])
            if v is None or not vals: continue
            below=sum(1 for x in vals if x<v); tie=sum(1 for x in vals if x==v)
            ps.append((below+0.5*tie)/len(vals))
        out.append(f"{c}={st.mean(ps):.3f}")
    print("leg",leg,"n=",len(sub)," ".join(out))
