import csv, statistics as st
from collections import defaultdict
OUT="/home/user/INMA-/research-vault/backtest/out/"
panel=list(csv.DictReader(open(OUT+"daily_panel.csv")))
feat=list(csv.DictReader(open(OUT+"oracle_features.csv")))
print("panel rows",len(panel),"trades",len(feat))
print("panel cols",len(panel[0]),"feat cols",len(feat[0]))
print("panel index vals",set(r.get('index',r.get('symbol','?')) for r in panel[:5]))
print("panel keys sample",list(panel[0].keys())[:8])
print("feat keys sample",list(feat[0].keys())[:8])
