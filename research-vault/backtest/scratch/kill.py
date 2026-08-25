import csv, statistics as st
from collections import defaultdict
O='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(O+'daily_panel.csv')))
tr=list(csv.DictReader(open(O+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
spx=[r for r in panel if r['sym']=='spx']
ndx=[r for r in panel if r['sym']=='ndx']
print("spx rows",len(spx),"ndx",len(ndx))
print("spx missing ret_5d",sum(1 for r in spx if f(r['ret_5d_pct']) is None))
# check hyg_chg5d units vs actual hyg pct change
h=[(r['date'],f(r['hyg'])) for r in spx]
h.sort()
for i in [10,200,500]:
    d,v=h[i]; d5,v5=h[i-5]
    print("  units check",d,"pct chg5d=%.3f"%(100*(v/v5-1)),"col=",[r['hyg_chg5d'] for r in spx if r['date']==d][0])
# regression hyg_chg5d ~ spx ret_5d_pct on unique dates (spx rows)
pts=[(f(r['ret_5d_pct']),f(r['hyg_chg5d'])) for r in spx if f(r['ret_5d_pct']) is not None]
n=len(pts); mx=st.mean(p[0] for p in pts); my=st.mean(p[1] for p in pts)
beta=sum((x-mx)*(y-my) for x,y in pts)/sum((x-mx)**2 for x,_ in pts); alpha=my-beta*mx
print("REG n=%d beta=%.4f alpha=%.4f"%(n,beta,alpha))
res={}
for r in spx:
    x=f(r['ret_5d_pct'])
    if x is None: continue
    res[r['date']]=f(r['hyg_chg5d'])-(alpha+beta*x)
rn=sum(1 for v in res.values() if v<0)
print("PANEL residual neg: %d/%d = %.1f%%  median %.4f"%(rn,len(res),100*rn/len(res),st.median(res.values())))
bd=defaultdict(list)
for t in tr: bd[t['buy_date']].append(t)
ub=[d for d in sorted(bd) if d in res]
bn=sum(1 for d in ub if res[d]<0)
print("BUY residual neg: %d/%d = %.1f%% lift %.2f median %.4f"%(bn,len(ub),100*bn/len(ub),(bn/len(ub))/(rn/len(res)),st.median(res[d] for d in ub)))
sd=defaultdict(list)
for t in tr: sd[t['sell_date']].append(t)
us=[d for d in sorted(sd) if d in res]
sn=sum(1 for d in us if res[d]<0)
print("SELL residual neg: %d/%d = %.1f%% median %.4f"%(sn,len(us),100*sn/len(us),st.median(res[d] for d in us)))
# residual by year
print("residual by year buy/panel:")
for y in ['2023','2024','2025','2026']:
    bb=[d for d in ub if d.startswith(y)]; pp=[d for d in res if d.startswith(y)]
    print("  %s %.1f (n=%d) / %.1f (n=%d)"%(y,100*sum(1 for d in bb if res[d]<0)/len(bb),len(bb),100*sum(1 for d in pp if res[d]<0)/len(pp),len(pp)))
# bucket conditioning on own equity ret_5d (trade-level uses own sym)
# use unique buy dates but each buy date may have spx/ndx; do per-sym row-level (trade-level)
panel_by=defaultdict(dict)
for r in panel: panel_by[r['sym']][r['date']]=r
qs=sorted(f(r['ret_5d_pct']) for r in panel if f(r['ret_5d_pct']) is not None)
def q(p): return qs[int(p*(len(qs)-1))]
cuts=[q(1/3.),q(2/3.)]
print("\nterciles of ret_5d_pct cut at",["%.2f"%c for c in cuts])
def bkt(x): return 0 if x<cuts[0] else (1 if x<cuts[1] else 2)
pb=defaultdict(list); bb=defaultdict(list)
for r in panel:
    x=f(r['ret_5d_pct'])
    if x is None: continue
    pb[bkt(x)].append(f(r['hyg_chg5d'])<0)
for t in tr:
    x=f(t['B_ret_5d_pct'])
    if x is None: continue
    bb[bkt(x)].append(f(t['B_hyg_chg5d'])<0)
for k in [0,1,2]:
    p=sum(pb[k])/len(pb[k]); b=sum(bb[k])/len(bb[k])
    print("  bucket %d: buy %.1f%% (n=%d) vs panel %.1f%% (n=%d) lift %.2f"%(k,100*b,len(bb[k]),100*p,len(pb[k]),b/p))
# pooled Mantel-Haenszel style: expected buys negative under bucket-matched panel rates
exp=sum(len(bb[k])*sum(pb[k])/len(pb[k]) for k in [0,1,2]); obs=sum(sum(bb[k]) for k in [0,1,2])
print("  pooled obs %d vs bucket-matched expected %.1f (N=%d)"%(obs,exp,sum(len(bb[k]) for k in [0,1,2])))
# sell-side residual bottom quartile
rq=sorted(res.values()); q1=rq[int(0.25*(len(rq)-1))]
print("\nSELL bottom-quartile residual: %.1f%% (n=%d) vs 25%% panel"%(100*sum(1 for d in us if res[d]<=q1)/len(us),len(us)))
