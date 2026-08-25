import csv, statistics as st, random
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
def f(v):
    try: return float(v)
    except: return None
bysym=defaultdict(list)
for r in panel: bysym[r['sym']].append(r)
for s in bysym: bysym[s].sort(key=lambda r:r['date'])
def zone(r): return (f(r['rsi14'])>75) or (f(r['bb_pctB'])>1.0) or (f(r['consec_up_days'])>=5)
fwd={}
for s,rows in bysym.items():
    for i,r in enumerate(rows):
        c=f(r['close'])
        for h in (5,21):
            if i+h<len(rows): fwd[(s,r['date'],h)]=(f(rows[i+h]['close'])/c-1)*100
# build zone EPISODES (contiguous runs, per sym) as blocks
eps=[]
for s,rows in bysym.items():
    cur=[]
    for r in rows:
        if zone(r): cur.append(r)
        elif cur: eps.append(cur); cur=[]
    if cur: eps.append(cur)
print("zone episodes:",len(eps),"median len",st.median(len(e) for e in eps))
def m(rows,h):
    v=[fwd[(r['sym'],r['date'],h)] for r in rows if (r['sym'],r['date'],h) in fwd]
    return st.mean(v) if v else None
for h in (5,21):
    obs=m([r for e in eps for r in e],h)
    allm=m(panel,h)
    random.seed(0)
    bs=[]
    for _ in range(5000):
        samp=[r for _ in range(len(eps)) for r in random.choice(eps)]
        x=m(samp,h)
        if x is not None: bs.append(x)
    bs.sort()
    lo,hi=bs[int(.025*len(bs))],bs[int(.975*len(bs))]
    print(f"{h}d zone mean={obs:+.3f}%  block-bootstrap 95% CI [{lo:+.3f}%, {hi:+.3f}%]  all-day mean={allm:+.3f}%  -> all-day mean inside CI: {lo<=allm<=hi}")
