import csv, statistics as st
from collections import Counter, defaultdict
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
trades=list(csv.DictReader(open(OUT+'oracle_features.csv')))
def f(d,k):
    v=d.get(k,'')
    if v is None or v=='' or v=='nan': return None
    try: return float(v)
    except: return None
# macro-unique panel: one row per date (macro identical across sym)
seen=set(); mpanel=[]
for r in panel:
    if r['date'] in seen: continue
    seen.add(r['date']); mpanel.append(r)
mpanel.sort(key=lambda r:r['date'])
