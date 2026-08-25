import csv, collections, itertools, statistics, sys
P='/home/user/INMA-/research-vault/backtest/out/'
p=list(csv.DictReader(open(P+'daily_panel.csv')))
bysym=collections.defaultdict(list)
for r in p: bysym[r['sym']].append(r)
for s in bysym: bysym[s].sort(key=lambda r:r['date'])

def best2(low,high):
    T=len(low); best=None
    for i1 in range(T):
        for j1 in range(i1,T):
            r1=high[j1]/low[i1]-1
            for i2 in range(j1,T):
                for j2 in range(i2,T):
                    tot=r1+high[j2]/low[i2]-1
                    if best is None or tot>best[0]: best=(tot,i1,j1,i2,j2)
    return best

def run(windows):
    """windows: list of list-of-row-dicts"""
    out=[]
    for w in windows:
        low=[float(r['low']) for r in w]; high=[float(r['high']) for r in w]
        tot,i1,j1,i2,j2=best2(low,high)
        out.append((w,(i1,j1),(i2,j2)))
    return out

# --- reproduce real calendar-month oracle ---
real=[]
for s,rows in bysym.items():
    bym=collections.defaultdict(list)
    for r in rows: bym[r['date'][:7]].append(r)
    for m in sorted(bym): real.append(bym[m])
res=run(real)
tot_sells=0; last2=0; leg2_last2=0; leg2_n=0; leg1_last2=0
recs=[]
for w,(i1,j1),(i2,j2) in res:
    T=len(w)
    for leg,(bi,si) in ((1,(i1,j1)),(2,(i2,j2))):
        tdte=T-1-si
        tot_sells+=1
        if tdte<=1: last2+=1
        if leg==2:
            leg2_n+=1
            if tdte<=1: leg2_last2+=1
        else:
            if tdte<=1: leg1_last2+=1
        recs.append((w[0]['sym'],w[0]['date'][:7],leg,w[bi]['date'],w[si]['date'],round(float(w[si]['high'])/float(w[bi]['low'])-1,6)))
print('REPRO n windows',len(res),'sells',tot_sells,'last2',last2,last2/tot_sells,'leg2',leg2_last2,leg2_n,leg2_last2/leg2_n,'leg1',leg1_last2)
import json
json.dump(recs,open('/home/user/INMA-/research-vault/backtest/scratch/repro.json','w'))
