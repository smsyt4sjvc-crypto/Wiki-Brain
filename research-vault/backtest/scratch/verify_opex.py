import csv, statistics, random
from collections import defaultdict, Counter

OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
print("panel rows",len(panel),"trades",len(tr))

# 1. base rate
opex=[r for r in panel if r['is_opex_week'] in ('1','1.0','True')]
print("BASE: is_opex_week=1 ->",len(opex),"/",len(panel),"=",round(100*len(opex)/len(panel),3),"%")
print("distinct is_opex_week vals",Counter(r['is_opex_week'] for r in panel))

# what dto values map to opex week
m=defaultdict(Counter)
for r in panel:
    m[int(float(r['days_to_opex']))][r['is_opex_week']]+=1
print("dto -> opexweek counts (sorted):")
for k in sorted(m): print("  dto",k,dict(m[k]))
