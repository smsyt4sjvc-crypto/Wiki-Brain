import csv, statistics as st
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
def f(v): return None if v in ('','NA','nan',None) else float(v)
groups=defaultdict(list)
for r in panel: groups[(r['sym'],r['date'][:7])].append(r)
bydate={(r['sym'],r['date']):r for r in panel}
def conv(feat,mode):
    out=[]
    for t in tr:
        g=groups[(t['sym'],t['buy_date'][:7])]
        x=f(bydate[(t['sym'],t['buy_date'])][feat])
        vals=[f(r[feat]) for r in g]
        below=sum(1 for v in vals if v<x); ties=sum(1 for v in vals if v==x); n=len(vals)
        if mode=='A': out.append(below/(n-1))
        elif mode=='B': out.append((below+0.5*ties)/n)
        elif mode=='C': out.append(below/n)
        elif mode=='D': out.append((below+0.5*(ties-1))/(n-1))
    return st.mean(out)
for m in 'ABCD':
    print(m, "vix %.4f  pctile %.4f  diff %+.4f"%(conv('vix',m),conv('vix_pctile_252d',m),conv('vix_pctile_252d',m)-conv('vix',m)))
# how correlated are the two within a month? count months where within-month ordering identical
same=0; tot=0
import itertools
for k,g in groups.items():
    a=[f(r['vix']) for r in g]; b=[f(r['vix_pctile_252d']) for r in g]
    order_a=sorted(range(len(a)),key=lambda i:a[i]); order_b=sorted(range(len(b)),key=lambda i:b[i])
    tot+=1
    if order_a==order_b: same+=1
print("months with IDENTICAL within-month ordering of vix vs vix_pctile: %d/%d"%(same,tot))
# also: is pctile a monotone transform of vix globally?
pairs=sorted((f(r['vix']),f(r['vix_pctile_252d'])) for r in panel)
inv=sum(1 for i in range(len(pairs)-1) if pairs[i+1][1]<pairs[i][1])
print("global monotone violations (adjacent) %d/%d"%(inv,len(pairs)-1))
