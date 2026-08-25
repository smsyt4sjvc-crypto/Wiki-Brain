import csv, statistics as st
from collections import defaultdict

P="/home/user/INMA-/research-vault/backtest/out/daily_panel.csv"
F="/home/user/INMA-/research-vault/backtest/out/oracle_features.csv"

panel=list(csv.DictReader(open(P)))
print("panel rows",len(panel))
bysym=defaultdict(int)
for r in panel: bysym[r['sym']]+=1
print("rows per sym",dict(bysym))

# month cells
cells=defaultdict(list)
for r in panel:
    key=(r['sym'], r['date'][:7])
    cells[key].append(r)
print("n month-cells in panel",len(cells))
months=sorted(set(k[1] for k in cells))
print("months",len(months),months[0],months[-1])
for k in sorted(cells):
    pass
# check cells per sym
c=defaultdict(int)
for k in cells: c[k[0]]+=1
print("cells per sym",dict(c))
# days per cell distribution
dl=sorted((len(v),k) for k,v in cells.items())
print("smallest cells",dl[:4]); print("largest",dl[-3:])
