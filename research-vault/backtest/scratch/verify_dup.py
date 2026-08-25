import csv, json, collections, math, statistics as st

BT="/home/user/INMA-/research-vault/backtest/out/"
tr=json.load(open(BT+"oracle_trades.json"))
print("n trades:", len(tr))
syms=collections.Counter(t["sym"] for t in tr); print("by sym:", syms)
months=sorted({t["month"] for t in tr}); print("n months:", len(months), months[0], months[-1])
legs=collections.Counter(t["leg"] for t in tr); print("legs:", legs)

# index by (month,leg)
by=collections.defaultdict(dict)
for t in tr: by[(t["month"],t["leg"])][t["sym"]]=t
pairs=[k for k,v in by.items() if len(v)==2]
print("(month,leg) pairs with both syms:", len(pairs), "of", len(by))

from datetime import date
def d(s): y,m,dd=s.split("-"); return date(int(y),int(m),int(dd))

bsame=ssame=0; b1=s1=0
bdiff=[]; sdiff=[]
for k in pairs:
    a=by[k]["spx"]; b=by[k]["ndx"]
    db=(d(a["buy_date"])-d(b["buy_date"])).days
    ds=(d(a["sell_date"])-d(b["sell_date"])).days
    bdiff.append(db); sdiff.append(ds)
    if db==0: bsame+=1
    if ds==0: ssame+=1
    if abs(db)<=1: b1+=1
    if abs(ds)<=1: s1+=1
n=len(pairs)
print(f"identical buy_date: {bsame}/{n} = {bsame/n:.3%}")
print(f"identical sell_date: {ssame}/{n} = {ssame/n:.3%}")
print(f"within 1 cal day buy: {b1}, sell: {s1}")
print("buy diff dist:", collections.Counter(abs(x) for x in bdiff))
print("sell diff dist:", collections.Counter(abs(x) for x in sdiff))
