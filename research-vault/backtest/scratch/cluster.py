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
rows={}
for key,rr in g.items():
    vv=[f(r,'vix') for r in rr]; hh=[f(r,'high') for r in rr]; ll=[f(r,'low') for r in rr]
    for r in rr: rows[(key,r['date'])]=dict(rvix=mr(vv,f(r,'vix')),rhigh=mr(hh,f(r,'high')),rlow=mr(ll,f(r,'low')))
# how much do SPX and NDX share dates?
for col in ['buy_date','sell_date']:
    d=defaultdict(set)
    for t in tr: d[(t['month'],t['leg'],col)].add(t[col])
    same=sum(1 for k,v in d.items() if len(v)==1)
    print(col,": month-leg cells where SPX and NDX picked the SAME date: %d/%d"%(same,len(d)))
sd=set(t['sell_date'] for t in tr); bd=set(t['buy_date'] for t in tr)
print("unique sell dates %d of 176; unique buy dates %d of 176"%(len(sd),len(bd)))

# cluster-robust (cluster by calendar date) t for sell vix rank deviation
def clustered_t(vals,keys,h0=0.5):
    n=len(vals); m=st.mean(vals)
    cl=defaultdict(list)
    for v,k in zip(vals,keys): cl[k].append(v-m)
    S=sum(sum(v)**2 for v in cl.values())
    se=math.sqrt(S)/n
    return n,len(cl),m,se,(m-h0)/se
for pre,dc in [('S_','sell_date'),('B_','buy_date')]:
    vals=[];keys=[]
    for t in tr:
        r=rows[((t['sym'],t[dc][:7]),t[dc])]; vals.append(r['rvix']); keys.append(t[dc])
    n,nc,m,se,tt=clustered_t(vals,keys)
    print("%s vix rank: n=%d clusters(dates)=%d mean=%.4f dev=%+.4f cluster-SE=%.4f t=%+.2f"%(pre,n,nc,m,m-0.5,se,tt))

# per-leg observed vs price-matched null
bins=defaultdict(list); binsl=defaultdict(list)
for r in rows.values():
    bins[min(9,int(r['rhigh']*10))].append(r['rvix']); binsl[min(9,int(r['rlow']*10))].append(r['rvix'])
print()
for leg in ['1','2']:
    o=[];p=[];pr=[]
    for t in tr:
        if t['leg']!=leg: continue
        r=rows[((t['sym'],t['sell_date'][:7]),t['sell_date'])]
        o.append(r['rvix']); p.append(st.mean(bins[min(9,int(r['rhigh']*10))])); pr.append(r['rhigh'])
    d=[a-b for a,b in zip(o,p)]
    print("SELL leg%s n=%d price_rank=%.3f obs=%.4f null=%.4f resid=%+.4f t=%+.2f"%(leg,len(o),st.mean(pr),st.mean(o),st.mean(p),st.mean(d),st.mean(d)/(st.stdev(d)/math.sqrt(len(d)))))

# ratio-of-deviations under the price-only null vs observed
nb=st.mean([st.mean(binsl[min(9,int(rows[((t['sym'],t['buy_date'][:7]),t['buy_date'])]['rlow']*10))]) for t in tr])
ns=st.mean([st.mean(bins[min(9,int(rows[((t['sym'],t['sell_date'][:7]),t['sell_date'])]['rhigh']*10))]) for t in tr])
print("\nPRICE-ONLY NULL predicts: buy dev %+.4f, sell dev %+.4f -> asymmetry ratio %.2fx"%(nb-.5,ns-.5,abs(nb-.5)/abs(ns-.5)))
print("OBSERVED: buy dev +0.2581, sell dev -0.0829 -> ratio 3.11x")

# vix_chg5d<-1 at sells, clustered
vals=[1.0 if f(t,'S_vix_chg5d')<-1 else 0.0 for t in tr]
keys=[t['sell_date'] for t in tr]
n,nc,m,se,tt=clustered_t(vals,keys,0.3247)
print("\nS_vix_chg5d<-1: k=%d p=%.4f base=0.3247 lift=%.2fx naiveSE=%.4f naive_z=%.2f | cluster-SE=%.4f cluster_z=%.2f (clusters=%d)"%(
    sum(vals),m,m/0.3247,math.sqrt(.3247*.6753/176),(m-.3247)/math.sqrt(.3247*.6753/176),se,tt,nc))
# and is it just "price rose over 5d"? base rate of vix_chg5d<-1 among panel days with ret_5d_pct>0
pos=[r for r in panel if f(r,'ret_5d_pct') is not None and f(r,'ret_5d_pct')>0]
b2=sum(1 for r in pos if f(r,'vix_chg5d')<-1)/len(pos)
print("CONDITIONAL base: P(vix_chg5d<-1 | ret_5d>0) = %.4f  n=%d  -> oracle sells lift vs THIS = %.2fx"%(b2,len(pos),m/b2))
srp=sum(1 for t in tr if f(t,'S_ret_5d_pct')>0)/176
print("share of oracle sells with ret_5d>0: %.3f  (panel base %.3f)"%(srp,len(pos)/1817))
# P(vix>25) at sells: CI on k=8
k=8;nn=176;p=k/nn
lo=p-1.96*math.sqrt(p*(1-p)/nn); hi=p+1.96*math.sqrt(p*(1-p)/nn)
print("\nP(vix>25) at sells k=8 p=%.4f 95%%CI [%.4f,%.4f] -> lift CI [%.2fx,%.2fx] vs base 0.0451"%(p,lo,hi,lo/.0451,hi/.0451))
