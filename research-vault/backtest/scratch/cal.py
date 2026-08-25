import csv, statistics as st, math, collections, json
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
print("trades",len(tr),"panel",len(pn))
def f(x):
    try: return float(x)
    except: return None
dates=sorted(r['date'] for r in pn)
print("panel date range",dates[0],dates[-1])
print("trade buy range",min(r['buy_date'] for r in tr),max(r['sell_date'] for r in tr))
# panel months per sym
pm=collections.Counter((r['sym'],r['date'][:7]) for r in pn)
print("panel n months per sym:", len(set(m for s,m in pm)))
sy=collections.Counter(r['sym'] for r in pn); print("panel by sym",sy)
tm=collections.Counter(r['sym'] for r in tr); print("trades by sym",tm)
print("legs",collections.Counter(r['leg'] for r in tr))
print("months in trades",len(set(r['month'] for r in tr)))
# which months missing per sym in panel
ms=collections.defaultdict(set)
for r in pn: ms[r['sym']].add(r['date'][:7])
print("spx-ndx month diff", sorted(ms['spx']^ms['ndx']))
# count trading days per sym-month
c=collections.Counter((r['sym'],r['date'][:7]) for r in pn)
last=sorted(set(m for s,m in c))[-1]
print("last month tdays", [(s,c[(s,last)]) for s in ('spx','ndx')])
print("hold_days dist", sorted(collections.Counter(int(float(r['hold_days'])) for r in tr).items())[:12])
