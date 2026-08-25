import csv, random, statistics as st
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
def f(v): return None if v in ('','NA','nan',None) else float(v)
groups=defaultdict(list)
for r in panel: groups[(r['sym'],r['date'][:7])].append(r)
bydate={(r['sym'],r['date']):r for r in panel}
def rk(t,feat):
    g=groups[(t['sym'],t['buy_date'][:7])]
    x=f(bydate[(t['sym'],t['buy_date'])][feat])
    vals=[f(r[feat]) for r in g]
    below=sum(1 for v in vals if v<x); ties=sum(1 for v in vals if v==x)
    return (below+0.5*ties)/len(vals)
rows=[(t['buy_date'], rk(t,'vix_pctile_252d')-rk(t,'vix')) for t in tr]
byd=defaultdict(list)
for d,x in rows: byd[d].append(x)
keys=list(byd)
random.seed(7)
bs=[]
for _ in range(5000):
    s=[]
    for _ in range(len(keys)):
        s+=byd[random.choice(keys)]
    bs.append(st.mean(s))
bs.sort()
print("paired rank diff (pctile-vix) point %+.4f  date-clustered 95%% CI [%+.4f, %+.4f]"%(
    st.mean([x for _,x in rows]), bs[125], bs[4874]))
print("frac of bootstrap draws where pctile BEATS vix: %.3f"%(sum(1 for b in bs if b>0)/len(bs)))
# matched-base-rate head-to-head at 10%: vix>22 vs pctile>90, clustered
def hits(feat,thr):
    return {t['buy_date']: None for t in tr}, None
def cnt(key,thr):
    return sum(1 for t in tr if f(t[key])>thr)
print("vix>22 hits %d (base 10.0%%)  pctile>90 hits %d (base 10.0%%)"%(cnt('B_vix',22),cnt('B_vix_pctile_252d',90)))
# bootstrap that gap by date
pair=[(t['buy_date'], (1 if f(t['B_vix'])>22 else 0)-(1 if f(t['B_vix_pctile_252d'])>90 else 0)) for t in tr]
bd=defaultdict(list)
for d,x in pair: bd[d].append(x)
bs2=[]
for _ in range(5000):
    s=[]
    for _ in range(len(bd)):
        s+=bd[random.choice(list(bd))]
    bs2.append(st.mean(s))
bs2.sort()
print("matched-10%% gap (vix>22 minus pctile>90), per-trade: %+.4f CI [%+.4f,%+.4f]"%(
    st.mean([x for _,x in pair]), bs2[125], bs2[4874]))
