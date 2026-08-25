import csv, statistics as st, math
from collections import defaultdict
P="/home/user/INMA-/research-vault/backtest/out/"
panel=list(csv.DictReader(open(P+"daily_panel.csv")))
tr=list(csv.DictReader(open(P+"oracle_features.csv")))
def f(r,k):
    try: return float(r[k])
    except: return None
# group panel by (sym, YYYY-MM)
g=defaultdict(list)
for r in panel:
    g[(r['sym'],r['date'][:7])].append(r)
print("sym-months",len(g),"sizes min/med/max",min(len(v) for v in g.values()),st.median([len(v) for v in g.values()]),max(len(v) for v in g.values()))

def rank_in(month_rows,col,val):
    # midrank fraction: P(X<val)+0.5*P(X==val)
    vals=[f(r,col) for r in month_rows]; vals=[v for v in vals if v is not None]
    if not vals or val is None: return None
    lt=sum(1 for v in vals if v<val); eq=sum(1 for v in vals if v==val)
    return (lt+0.5*eq)/len(vals)

def summarize(label,ranks):
    n=len(ranks); m=st.mean(ranks); sd=st.stdev(ranks)
    se=sd/math.sqrt(n)
    print("%-28s n=%3d mean_rank=%.4f dev=%+.4f  SE=%.4f  t=%+.2f"%(label,n,m,m-0.5,se,(m-0.5)/se))
    return m

for col,pre in [('vix','B_'),('vix','S_')]:
    rk=[]
    for t in tr:
        key=(t['sym'], (t['buy_date'] if pre=='B_' else t['sell_date'])[:7])
        r=rank_in(g[key],col,f(t,pre+col))
        if r is not None: rk.append(r)
    summarize(pre+col,rk)

# price-only exit null: within each sym-month, the day with the highest HIGH
nullrk=[]
for key,rows in g.items():
    best=max(rows,key=lambda r: f(r,'high'))
    nullrk.append(rank_in(rows,'vix',f(best,'vix')))
summarize("month-high-day vix rank",nullrk)
# and month-low-day (buy null)
nullb=[]
for key,rows in g.items():
    best=min(rows,key=lambda r: f(r,'low'))
    nullb.append(rank_in(rows,'vix',f(best,'vix')))
summarize("month-low-day vix rank",nullb)

# leg-1 vs leg-2 sells separately
for leg in ['1','2']:
    rk=[]
    for t in tr:
        if t['leg']!=leg: continue
        key=(t['sym'],t['sell_date'][:7])
        rk.append(rank_in(g[key],'vix',f(t,'S_vix')))
    summarize("S_vix leg"+leg,rk)
    rkb=[]
    for t in tr:
        if t['leg']!=leg: continue
        key=(t['sym'],t['buy_date'][:7])
        rkb.append(rank_in(g[key],'vix',f(t,'B_vix')))
    summarize("B_vix leg"+leg,rkb)

# Is the sell just "the highest sell of the month"? compare sells that ARE the month high day
mh={}
for key,rows in g.items():
    mh[key]=max(rows,key=lambda r: f(r,'high'))['date']
same=sum(1 for t in tr if mh.get((t['sym'],t['sell_date'][:7]))==t['sell_date'])
print("sells landing exactly on month-high day: %d/176"%same)
