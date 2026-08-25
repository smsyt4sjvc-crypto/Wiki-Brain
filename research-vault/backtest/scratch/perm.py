import csv, statistics as st, random
from collections import defaultdict
random.seed(7)
orc=list(csv.DictReader(open("/home/user/INMA-/research-vault/backtest/out/oracle_features.csv")))
dp=list(csv.DictReader(open("/home/user/INMA-/research-vault/backtest/out/daily_panel.csv")))
def f(r,k):
    v=r.get(k,"")
    return None if v in ("","nan","None",None) else float(v)
bym=defaultdict(list)
for r in dp: bym[(r["sym"],r["date"][:7])].append(r)
blocks=list(bym.values())

def stats(rows,key):
    v=[f(r,key) for r in rows]
    return st.median(v), sum(1 for x in v if x<-10)/len(v)*100, sum(1 for x in v if x<-15)/len(v)*100
def stats200(rows,key):
    v=[f(r,key) for r in rows]
    return st.median(v), sum(1 for x in v if x<0)/len(v)*100

obs_med,obs10,obs15=stats(orc,"B_dd_from_252d_high_pct")
obs_m200,obs_b200=stats200(orc,"B_dist_sma200_pct")
print(f"OBSERVED: dd252 med {obs_med:.2f}  <-10 {obs10:.1f}%  <-15 {obs15:.1f}%  | sma200 med {obs_m200:.2f} below {obs_b200:.1f}%")

N=20000
meds=[];p10=[];p15=[];m200=[];b200=[]
for _ in range(N):
    pick=[]
    for b in blocks: pick+=random.sample(b,2)
    a,b_,c=stats(pick,"dd_from_252d_high_pct"); d,e=stats200(pick,"dist_sma200_pct")
    meds.append(a);p10.append(b_);p15.append(c);m200.append(d);b200.append(e)
def pc(arr,x): return sum(1 for v in arr if v<=x)/len(arr)*100
def rng(arr): 
    s=sorted(arr); return s[int(.025*len(s))], s[int(.5*len(s))], s[int(.975*len(s))]
for nm,arr,o,lower_is_extreme in [("dd252 median",meds,obs_med,True),("dd252<-10 %",p10,obs10,False),
        ("dd252<-15 %",p15,obs15,False),("sma200 median",m200,obs_m200,True),("below200 %",b200,obs_b200,False)]:
    lo,md,hi=rng(arr)
    pct=pc(arr,o)
    print(f"{nm:15s} obs {o:8.2f} | null 2.5/50/97.5 = {lo:7.2f} {md:7.2f} {hi:7.2f} | obs at {pct:5.1f}th pctile of null")

# ceiling: 2 DEEPEST days per block
ceil=[]
for b in blocks:
    s=sorted(b,key=lambda r:f(r,"dd_from_252d_high_pct"))[:2]; ceil+=s
a,b_,c=stats(ceil,"dd_from_252d_high_pct")
print(f"\nCEILING (2 deepest days/block): dd252 med {a:.2f}  <-10 {b_:.1f}%  <-15 {c:.1f}%")
d,e=stats200(ceil,"dist_sma200_pct"); print(f"                                 sma200 med {d:.2f} below {e:.1f}%")

# how far obs travelled from null-median to ceiling
print(f"\nfloor->ceiling travel:")
for nm,nullmed,o,ce in [("dd252 median",rng(meds)[1],obs_med,a),("dd252<-10 %",rng(p10)[1],obs10,b_),
                        ("dd252<-15 %",rng(p15)[1],obs15,c),("below200 %",rng(b200)[1],obs_b200,e)]:
    print(f"  {nm:15s} null {nullmed:7.2f} -> obs {o:7.2f} -> ceiling {ce:7.2f}   = {(o-nullmed)/(ce-nullmed)*100:5.1f}% of available headroom")

# their contrast: 20d-horizon thresholds
od=[f(r,"B_dd_from_20d_high_pct") for r in orc]; dd=[f(r,"dd_from_20d_high_pct") for r in dp]
print("\n-- their cited contrast (20d-high thresholds) --")
for t in (-3,-5,-7,-10):
    a1=sum(1 for v in od if v<t)/len(od)*100; b1=sum(1 for v in dd if v<t)/len(dd)*100
    print(f"  dd20<{t}: oracle {a1:.1f}% base {b1:.1f}% lift {a1/b1:.2f}x")
    # ceiling for dd20
    cap=sum(min(2,sum(1 for r in b if f(r,"dd_from_20d_high_pct")<t)) for b in blocks)
    print(f"           ceiling under forced-monthly design = {cap/176*100:.1f}% (max lift {cap/176*100/b1:.2f}x)")
