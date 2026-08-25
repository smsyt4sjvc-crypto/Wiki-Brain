import csv, json, statistics as st
from collections import defaultdict
B="/home/user/INMA-/research-vault/backtest/out/"
tr=json.load(open(B+"oracle_trades.json"))
panel=list(csv.DictReader(open(B+"daily_panel.csv")))
print("trades",len(tr),"panel",len(panel))

# panel indexed by (sym,month) in date order
by_sm=defaultdict(list)
for r in panel:
    by_sm[(r["sym"],r["month"])].append(r)
for k in by_sm: by_sm[k].sort(key=lambda r:r["date"])
idx={}  # (sym,date)->(sym,month,i)
for k,rows in by_sm.items():
    for i,r in enumerate(rows): idx[(r["sym"],r["date"])]=(k,i)
print("sym-months",len(by_sm), "syms",sorted(set(r['sym'] for r in panel)))
print("months per sym", {s:len({m for (sy,m) in by_sm if sy==s}) for s in sorted(set(r['sym'] for r in panel))})

legs=defaultdict(dict)
for t in tr: legs[(t["sym"],t["month"])][t["leg"]]=t
pairs=[(k,v[1],v[2]) for k,v in legs.items() if 1 in v and 2 in v]
print("complete leg pairs:",len(pairs),"| months w/ missing leg:",[k for k,v in legs.items() if len(v)!=2])
