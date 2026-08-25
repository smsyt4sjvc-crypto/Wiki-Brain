import csv,random,statistics
from collections import defaultdict
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
I=lambda r,k:int(float(r[k]))
pm=defaultdict(list)
for r in panel: pm[(r['sym'],r['date'][:7])].append(r)
for k in pm: pm[k].sort(key=lambda r:r['date'])
pos={(k[0],r['date']):i for k,v in pm.items() for i,r in enumerate(v)}
months=sorted(set((t['sym'],t['month'][:7]) for t in tr))
cal=sorted(set(m for _,m in months))
byk=defaultdict(dict)
for t in tr: byk[(t['sym'],t['month'][:7])][t['leg']]=(pos[(t['sym'],t['buy_date'])],pos[(t['sym'],t['sell_date'])])
opexset={k:[i for i,r in enumerate(v) if I(r,'is_opex_week')] for k,v in pm.items()}
lens={k:len(v) for k,v in pm.items()}
def stats(a):
    b=s=hd=hdo=0
    for k,legs in byk.items():
        S=a[k]
        for leg,(bi,si) in legs.items():
            b+= bi in S; s+= si in S
            for i in range(bi,si+1): hd+=1; hdo+= i in S
    return b/176,s/176,hdo/hd
obs=stats({k:set(opexset[k]) for k in months})
random.seed(5); pool=[opexset[k] for k in months]
A=[[],[],[]]
for _ in range(20000):
    a={}
    for cm in cal:              # SAME permuted window for both syms of a calendar month (clustered)
        src=random.choice(pool)
        for sym in ('spx','ndx','SPX','NDX'):
            k=(sym,cm)
            if k in lens:
                S=set(i for i in src if i<lens[k])
                a[k]=S if S else {0}
    v=stats(a)
    for j in range(3): A[j].append(v[j])
for j,nm in enumerate(['buys','sells','hold']):
    mu=statistics.mean(A[j]); sd=statistics.pstdev(A[j])
    print(f"CLUSTERED null {nm:5} obs {obs[j]:.4f} null {mu:.4f} sd {sd:.4f} z {(obs[j]-mu)/sd:+.2f} lift {obs[j]/mu:.3f}  2sigma-lift-band [{(mu-2*sd)/mu:.2f},{(mu+2*sd)/mu:.2f}]")
