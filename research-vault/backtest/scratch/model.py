import csv, math, collections, random
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
buyset=set((r['sym'],r['buy_date']) for r in tr)
print("syms:",collections.Counter(r['sym'] for r in panel))
rows=[(float(r['rsi14']), 1 if (r['sym'],r['date']) in buyset else 0) for r in panel]
base=sum(y for _,y in rows)/len(rows)

def ll_step(cuts):
    cuts=[-1]+list(cuts)+[999]; tot=0
    for i in range(len(cuts)-1):
        s=[y for x,y in rows if cuts[i]<x<=cuts[i+1]]
        n=len(s); k=sum(s)
        if n==0: continue
        p=k/n
        if 0<p<1: tot+=k*math.log(p)+(n-k)*math.log(1-p)
    return tot
def ll_logit():
    # simple logistic on rsi via gradient descent
    b0,b1=0.0,0.0
    for it in range(20000):
        g0=g1=0
        for x,y in rows:
            z=b0+b1*x; p=1/(1+math.exp(-max(-30,min(30,z))))
            g0+=(y-p); g1+=(y-p)*x
        b0+=1e-3*g0/len(rows)*10; b1+=1e-3*g1/len(rows)*10/50
    tot=0
    for x,y in rows:
        z=b0+b1*x; p=1/(1+math.exp(-max(-30,min(30,z))))
        p=min(max(p,1e-9),1-1e-9); tot+=y*math.log(p)+(1-y)*math.log(1-p)
    return tot,b0,b1
ll_null=ll_step([])
lin,b0,b1=ll_logit()
st=ll_step([40,75])
print(f"logLik null (1 param)            = {ll_null:.2f}")
print(f"logLik LINEAR logit in RSI (2p)  = {lin:.2f}   b1={b1:.4f}")
print(f"logLik 3-LEVEL STEP @40,75 (3p)  = {st:.2f}")
print(f"AIC linear={-2*lin+4:.1f}   AIC step@40/75={-2*st+6:.1f}   (lower is better)")
# best single cut on the buy side by likelihood
best=None
for c in range(20,60):
    v=ll_step([c,75])
    if best is None or v>best[1]: best=(c,v)
print(f"best lower cut point by likelihood (upper fixed 75): RSI={best[0]}  ll={best[1]:.2f}")
# runs, fixed
alld=sorted({r['date'] for r in panel}); idx={d:i for i,d in enumerate(alld)}
runs=0
for s in set(r['sym'] for r in panel):
    ds=sorted(idx[d] for (sy,d) in buyset if sy==s); prev=-99
    for i in ds:
        if i!=prev+1: runs+=1
        prev=i
print(f"contiguous buy-day runs across both syms: {runs} (of 167 buy-days)")
