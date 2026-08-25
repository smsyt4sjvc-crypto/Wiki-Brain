import csv, json, statistics as st
from collections import defaultdict

OUT="/home/user/INMA-/research-vault/backtest/out/"
trades=json.load(open(OUT+"oracle_trades.json"))
panel=list(csv.DictReader(open(OUT+"daily_panel.csv")))
for r in panel:
    r['month']=r['date'][:7]

# ---- oracle per (sym,month)
orc=defaultdict(float); legs=defaultdict(int)
for t in trades:
    orc[(t['sym'],t['month'])]+=t['ret_pct']; legs[(t['sym'],t['month'])]+=1
print("cells:",len(orc),"legs total:",sum(legs.values()),"legs per cell set:",set(legs.values()))
print("oracle sum:",round(sum(orc.values()),2))
# cross-check month_total_pct
mt={}
for t in trades: mt[(t['sym'],t['month'])]=t['month_total_pct']
mx=max(abs(orc[k]-mt[k]) for k in orc); print("max |sum legs - month_total_pct|:",round(mx,4))

# ---- panel per (sym,month): buy&hold (first close -> last close within month), range, realvol
bym=defaultdict(list)
for r in panel: bym[(r['sym'],r['month'])].append(r)
bh={}; rng={}; ndays={}
for k,rows in bym.items():
    rows.sort(key=lambda r:r['date'])
    c0=float(rows[0]['close']); c1=float(rows[-1]['close'])
    bh[k]=(c1/c0-1)*100
    lo=min(float(r['low']) for r in rows); hi=max(float(r['high']) for r in rows)
    rng[k]=(hi/lo-1)*100
    ndays[k]=len(rows)
print("panel cells:",len(bh))
missing=[k for k in orc if k not in bh]; print("orc cells missing in panel:",missing)

# buy&hold variant: prev-month-close -> last close (chained)
allrows=defaultdict(list)
for r in panel: allrows[r['sym']].append(r)
bh2={}
for s,rows in allrows.items():
    rows.sort(key=lambda r:r['date'])
    prev=None
    for i,r in enumerate(rows):
        pass
    # month boundaries
    idx=defaultdict(list)
    for i,r in enumerate(rows): idx[r['month']].append(i)
    for m,ii in idx.items():
        a=ii[0]; b=ii[-1]
        base=float(rows[a-1]['close']) if a>0 else float(rows[a]['close'])
        bh2[(s,m)]=(float(rows[b]['close'])/base-1)*100

def gini(x):
    x=sorted(x); n=len(x); s=sum(x)
    return sum((2*(i+1)-n-1)*v for i,v in enumerate(x))/(n*s)

def topshare(x,k):
    x=sorted(x,reverse=True); return sum(x[:k])/sum(x)*100

O=[orc[k] for k in sorted(orc)]
B=[bh[k] for k in sorted(orc)]
B2=[bh2[k] for k in sorted(orc)]
R=[rng[k] for k in sorted(orc)]
E=[o-b for o,b in zip(O,B)]

def rep(name,x,neg_ok=True):
    print(f"\n{name}: n={len(x)} sum={sum(x):.2f} mean={st.mean(x):.3f} median={st.median(x):.3f} min={min(x):.3f} max={max(x):.3f} sd={st.pstdev(x):.3f}")
    print(f"   neg count={sum(1 for v in x if v<0)}  CV={st.pstdev(x)/st.mean(x):.3f}  gini={gini(x):.4f}")
    for k in (4,8,22): print(f"   top{k}/{len(x)} = {topshare(x,k):.2f}% (uniform {k/len(x)*100:.1f}%)")

rep("ORACLE",O); rep("BUYHOLD first->last close",B); rep("BUYHOLD prevclose->last",B2); rep("RANGE hi/lo",R); rep("EDGE (orc-bh)",E)

# April 2025
for k in [('ndx','2025-04'),('spx','2025-04')]:
    print(k,"orc",round(orc[k],2),"bh",round(bh[k],2),"bh2",round(bh2[k],2),"range",round(rng[k],2),"edge",round(orc[k]-bh[k],2))
apr=sum(orc[k]-bh[k] for k in [('ndx','2025-04'),('spx','2025-04')])
print("apr edge sum",round(apr,2),"share of total edge",round(apr/sum(E)*100,2),"%")
# realvol/vix for apr
for k in [('ndx','2025-04'),('spx','2025-04')]:
    rows=bym[k]
    print(k,"mean realvol20",round(st.mean(float(r['realvol20_ann_pct']) for r in rows),2),
          "mean vix",round(st.mean(float(r['vix']) for r in rows),2) if 'vix' in rows[0] else 'n/a')

# months count
months=sorted(set(m for s,m in orc)); print("\nn months:",len(months),months[0],months[-1])
