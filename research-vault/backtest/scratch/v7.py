import csv, statistics as st, random
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/daily_panel.csv'
rows=list(csv.DictReader(open(P)))
def f(x):
    try: return float(x)
    except: return None
by=defaultdict(list)
for r in rows: by[r['sym']].append(r)
for s in by: by[s].sort(key=lambda r:r['date'])
per={}
for s,v in by.items():
    arr=[]
    for i in range(len(v)-5):
        lo=f(v[i]['low']); H=max(f(x['high']) for x in v[i:i+6])
        arr.append(dict(rng=(H-lo)/lo*100, ret=(f(v[i+5]['close'])-f(v[i]['close']))/f(v[i]['close'])*100,
                        vix=f(v[i]['vix'])))
    per[s]=arr
pool=per['spx']+per['ndx']
def stats(sub):
    return st.mean(a['rng'] for a in sub), st.mean(a['ret'] for a in sub), 100*sum(1 for a in sub if a['ret']>0)/len(sub)
br,bt,bp=stats(pool)
print("ALL n=%d rng=%.3f ret=%.3f P(up)=%.1f"%(len(pool),br,bt,bp))
for th in (18,20,22,25):
    s=[a for a in pool if a['vix']>th]
    r,t,p=stats(s)
    print(" vix>%2d n=%4d (uniq dates %d) rng=%.3f x%.2f | ret=%.3f x%.2f (+%.2fpp) | P(up)=%.1f (+%.1fpp)"%(
        th,len(s),len(s)//2,r,r/br,t,t/bt,t-bt,p,p-bp))
# episode-level directional, spx
for s_,arr in per.items():
    for th in (20,25):
        eps=[];cur=[]
        for a in arr:
            if a['vix']>th: cur.append(a['ret'])
            else:
                if cur: eps.append(st.mean(cur)); cur=[]
        if cur: eps.append(st.mean(cur))
        base=st.mean(a['ret'] for a in arr)
        print("  %s vix>%d: %d episodes, episode-mean ret=%.3f vs base %.3f; episodes>0: %d/%d"%(
            s_,th,len(eps),st.mean(eps),base,sum(1 for e in eps if e>0),len(eps)))
