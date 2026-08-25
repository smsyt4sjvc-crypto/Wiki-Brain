import csv,random,statistics
from collections import defaultdict,Counter
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
I=lambda r,k:int(float(r[k]))
pm=defaultdict(list)
for r in panel: pm[(r['sym'],r['date'][:7])].append(r)
for k in pm: pm[k].sort(key=lambda r:r['date'])
pos={(k[0],r['date']):i for k,v in pm.items() for i,r in enumerate(v)}
months=sorted(set((t['sym'],t['month'][:7]) for t in tr))
byk=defaultdict(dict)
for t in tr: byk[(t['sym'],t['month'][:7])][t['leg']]=(pos[(t['sym'],t['buy_date'])],pos[(t['sym'],t['sell_date'])])

# STRICT Mon-Fri opex week (dto 0..4)
strictset={k:[i for i,r in enumerate(v) if 0<=I(r,'days_to_opex')<=4] for k,v in pm.items()}
lens={k:len(v) for k,v in pm.items()}
def hold(assign):
    hd=hdo=0
    for k,legs in byk.items():
        S=assign[k]
        for leg,(b,s) in legs.items():
            for i in range(b,s+1): hd+=1; hdo+= i in S
    return hdo/hd,hd
obs,hd=hold({k:set(strictset[k]) for k in months})
random.seed(3); pool=[strictset[k] for k in months]; vals=[]
for _ in range(20000):
    a={}
    for k in months:
        while True:
            S=set(i for i in random.choice(pool) if i<lens[k])
            if S: break
        a[k]=S
    vals.append(hold(a)[0])
mu=statistics.mean(vals); sd=statistics.pstdev(vals)
print(f"STRICT Mon-Fri opex week: obs hold {obs:.4f} (n={hd}) null {mu:.4f} sd {sd:.4f} z={(obs-mu)/sd:.2f} lift {obs/mu:.3f}")

# SPX vs NDX overlap: same buy/sell dates?
d=defaultdict(dict)
for t in tr: d[(t['month'][:7],t['leg'])][t['sym']]=(t['buy_date'],t['sell_date'])
same_b=sum(1 for k,v in d.items() if len(v)==2 and list(v.values())[0][0]==list(v.values())[1][0])
same_s=sum(1 for k,v in d.items() if len(v)==2 and list(v.values())[0][1]==list(v.values())[1][1])
print(f"month-leg pairs with BOTH syms: {sum(1 for v in d.values() if len(v)==2)}; identical buy date {same_b}, identical sell date {same_s}")
print("=> SPX/NDX are NOT independent: effective months ~44, not 88")
