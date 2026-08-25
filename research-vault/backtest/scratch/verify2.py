import csv, statistics as st, math
from collections import defaultdict
P="/home/user/INMA-/research-vault/backtest/out/daily_panel.csv"
F="/home/user/INMA-/research-vault/backtest/out/oracle_features.csv"
panel=list(csv.DictReader(open(P)))
trades=list(csv.DictReader(open(F)))
print("trades",len(trades))

cells=defaultdict(list)
for r in panel: cells[(r['sym'],r['date'][:7])].append(r)
for k in cells: cells[k].sort(key=lambda r:r['date'])

def f(x):
    try: return float(x)
    except: return None

M={}
for k,rows in cells.items():
    path=sum(abs(f(r['ret_1d_pct'])) for r in rows)                 # incl. first day (spans prev month)
    path_ex=sum(abs(f(r['ret_1d_pct'])) for r in rows[1:])          # intra-month only
    hi=max(f(r['high']) for r in rows); lo=min(f(r['low']) for r in rows)
    rng=(hi-lo)/lo*100
    rng_c=(max(f(r['close']) for r in rows)-min(f(r['close']) for r in rows))/min(f(r['close']) for r in rows)*100
    bh=(f(rows[-1]['close'])/f(rows[0]['close'])-1)*100             # first close -> last close
    M[k]=dict(path=path,path_ex=path_ex,rng=rng,rng_c=rng_c,bh=bh,nd=len(rows),
              lo=lo,hi=hi,first=f(rows[0]['close']),last=f(rows[-1]['close']))

# oracle total per cell
oc=defaultdict(float); legs=defaultdict(int); mtot={}
for t in trades:
    k=(t['sym'],t['month']); oc[k]+=float(t['ret_pct']); legs[k]+=1
    mtot[k]=float(t['month_total_pct'])
print("oracle cells",len(oc),"legs per cell set",set(legs.values()))
# cross-check month_total_pct vs sum of legs
d=[abs(oc[k]-mtot[k]) for k in oc]
print("max |sum legs - month_total_pct|",max(d))

keys=sorted(oc)
def corr(a,b):
    n=len(a); ma=sum(a)/n; mb=sum(b)/n
    sa=math.sqrt(sum((x-ma)**2 for x in a)); sb=math.sqrt(sum((x-mb)**2 for x in b))
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/(sa*sb)

O=[oc[k] for k in keys]
PA=[M[k]['path'] for k in keys]; PAX=[M[k]['path_ex'] for k in keys]
RG=[M[k]['rng'] for k in keys]; RGC=[M[k]['rng_c'] for k in keys]; BH=[M[k]['bh'] for k in keys]

print("\n--- BASE RATES (88 month-cells) ---")
for name,v in [("path(incl 1st day)",PA),("path(intra-month)",PAX),("range hi/lo",RG),("range close",RGC),("buy&hold",BH),("oracle_total",O)]:
    print(f"{name:22s} mean {sum(v)/len(v):7.3f}  median {st.median(v):7.3f}  sd {st.pstdev(v):6.3f}")
print("mean |bh|", sum(abs(x) for x in BH)/88)

ratios=[oc[k]/M[k]['path'] for k in keys]
print("\n--- oracle/path per cell ---")
print("mean",sum(ratios)/88,"median",st.median(ratios),"sd(sample)",st.stdev(ratios),"sd(pop)",st.pstdev(ratios))
print("min",min(ratios),"max",max(ratios),"CV",st.stdev(ratios)/(sum(ratios)/88))
print("ratio of MEANS (agg)", sum(O)/sum(PA))

r_path=corr(O,PA); r_pathx=corr(O,PAX); r_rng=corr(O,RG); r_rngc=corr(O,RGC)
print("\n--- correlations with oracle_total ---")
print("r(path)",round(r_path,4),"r(path intra)",round(r_pathx,4),"r(range)",round(r_rng,4),"r(range close)",round(r_rngc,4))
print("r(path,range)",round(corr(PA,RG),4))

# up vs down months
up=[k for k in keys if M[k]['bh']>0]; dn=[k for k in keys if M[k]['bh']<=0]
print("\n--- up/down split ---  n_up",len(up),"n_dn",len(dn))
for lbl,g in [("up",up),("dn",dn)]:
    pe=[oc[k]/M[k]['path'] for k in g]; re_=[oc[k]/M[k]['rng'] for k in g]
    print(f"{lbl}: path-eff mean {sum(pe)/len(g):.4f} sd {st.pstdev(pe):.4f} | range-eff mean {sum(re_)/len(g):.4f} sd {st.pstdev(re_):.4f}")
