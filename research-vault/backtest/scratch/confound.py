import csv, statistics as st, math
from collections import defaultdict
P="/home/user/INMA-/research-vault/backtest/out/"
panel=list(csv.DictReader(open(P+"daily_panel.csv")))
tr=list(csv.DictReader(open(P+"oracle_features.csv")))
def f(r,k):
    try: return float(r[k])
    except: return None
g=defaultdict(list)
for r in panel: g[(r['sym'],r['date'][:7])].append(r)
def mr(vals,val):
    lt=sum(1 for v in vals if v<val); eq=sum(1 for v in vals if v==val)
    return (lt+0.5*eq)/len(vals)
# annotate every panel day with within-month rank of vix, high, low, and position
rows=[]
for key,rr in g.items():
    vv=[f(r,'vix') for r in rr]; hh=[f(r,'high') for r in rr]; ll=[f(r,'low') for r in rr]
    n=len(rr)
    for i,r in enumerate(sorted(rr,key=lambda x:x['date'])):
        rows.append(dict(key=key,date=r['date'],
            rvix=mr(vv,f(r,'vix')), rhigh=mr(hh,f(r,'high')), rlow=mr(ll,f(r,'low')),
            pos=(i+0.5)/n))
idx={(r['key'],r['date']):r for r in rows}
# PANEL relationship: mean vix-rank by price(high)-rank decile
bins=defaultdict(list)
for r in rows: bins[min(9,int(r['rhigh']*10))].append(r['rvix'])
print("PANEL: E[vix_rank | high_rank decile]  (n=1817 days)")
for b in sorted(bins): print("  high-rank %.1f-%.1f  n=%4d  mean vix rank %.3f"%(b/10,(b+1)/10,len(bins[b]),st.mean(bins[b])))
def pred_from_high(rh): return st.mean(bins[min(9,int(rh*10))])
# same for lows (buy side)
binsl=defaultdict(list)
for r in rows: binsl[min(9,int(r['rlow']*10))].append(r['rvix'])
def pred_from_low(rl): return st.mean(binsl[min(9,int(rl*10))])

def go(pre,datecol,rankcol,predfn,label):
    obs=[];pred=[];pr=[];pos=[]
    for t in tr:
        k=(t['sym'],t[datecol][:7]); rr=idx.get((k,t[datecol]))
        if rr is None: continue
        obs.append(rr['rvix']); pred.append(predfn(rr[rankcol])); pr.append(rr[rankcol]); pos.append(rr['pos'])
    d=[o-p for o,p in zip(obs,pred)]
    se=st.stdev(d)/math.sqrt(len(d))
    print("\n%s n=%d"%(label,len(obs)))
    print("  mean within-month PRICE rank at these dates: %.3f"%st.mean(pr))
    print("  mean position-in-month: %.3f"%st.mean(pos))
    print("  OBSERVED vix rank        %.4f"%st.mean(obs))
    print("  PRICE-MATCHED NULL       %.4f"%st.mean(pred))
    print("  residual                 %+.4f  SE %.4f  t %+.2f"%(st.mean(d),se,st.mean(d)/se))
go('S_','sell_date','rhigh',pred_from_high,"ORACLE SELLS vs price-matched VIX null")
go('B_','buy_date','rlow',pred_from_low,"ORACLE BUYS vs price-matched VIX null")

# the agent's null: month-high day only
mh=[]
for key,rr in g.items():
    b=max(rr,key=lambda r: f(r,'high')); mh.append(idx[(key,b['date'])])
print("\nAGENT'S NULL month-high day: n=%d vix rank %.4f, its own high-rank %.3f, pos %.3f"%(
    len(mh),st.mean([r['rvix'] for r in mh]),st.mean([r['rhigh'] for r in mh]),st.mean([r['pos'] for r in mh])))

# position confound: does vix rank drift through the month in this sample?
pb=defaultdict(list)
for r in rows: pb[min(4,int(r['pos']*5))].append(r['rvix'])
print("\nPANEL: E[vix_rank | position-in-month quintile]")
for b in sorted(pb): print("  q%d n=%4d mean vix rank %.3f"%(b+1,len(pb[b]),st.mean(pb[b])))
