import csv, collections, random, statistics as st, itertools
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
F=lambda x: float(x) if x not in ('','None') else None
bysm=collections.defaultdict(list)
for r in pn: bysm[(r['sym'],r['date'][:7])].append(r)
for k in bysm: bysm[k].sort(key=lambda r:r['date'])
tidx={}  # (sym,date)->0-based index in month
for k,v in bysm.items():
    for i,r in enumerate(v): tidx[(r['sym'],r['date'])]=i

# verify constraint / overlap
legs=collections.defaultdict(dict)
for r in tr: legs[(r['sym'],r['month'])][r['leg']]=r
bad=0; touch=0
for k,d in legs.items():
    a,b=d['1'],d['2']
    if not (a['buy_date']<=a['sell_date']<=b['buy_date']<=b['sell_date']): bad+=1
    if a['sell_date']==b['buy_date']: touch+=1
print("violations",bad,"sell1==buy2 (touching)",touch,"of",len(legs))

# ---------- ORDER-STATISTIC NULL ----------
random.seed(7)
NS=20000
null_buy=collections.Counter(); null_sell=collections.Counter()   # keyed by feature values
null_feat=collections.defaultdict(lambda: collections.Counter())
keys=[( r['sym'], r['month']) for r in tr]
monthkeys=sorted(legs.keys())
FEATS=['dow','is_turn_of_month','is_opex_week','days_to_opex','tday_in_month','pct_through_month','is_quarter_end_month']
nullB={f:collections.Counter() for f in FEATS}
nullS={f:collections.Counter() for f in FEATS}
nullB1={f:collections.Counter() for f in FEATS}; nullB2={f:collections.Counter() for f in FEATS}
nullS1={f:collections.Counter() for f in FEATS}; nullS2={f:collections.Counter() for f in FEATS}
for _ in range(NS):
    for mk in monthkeys:
        rows=bysm[mk]; T=len(rows)
        i1,j1,i2,j2=sorted(random.choices(range(T),k=4))
        for f in FEATS:
            nullB[f][rows[i1][f]]+=1; nullB[f][rows[i2][f]]+=1
            nullS[f][rows[j1][f]]+=1; nullS[f][rows[j2][f]]+=1
            nullB1[f][rows[i1][f]]+=1; nullB2[f][rows[i2][f]]+=1
            nullS1[f][rows[j1][f]]+=1; nullS2[f][rows[j2][f]]+=1
import pickle
pickle.dump({'nullB':{f:dict(nullB[f]) for f in FEATS},'nullS':{f:dict(nullS[f]) for f in FEATS},
 'nullB1':{f:dict(nullB1[f]) for f in FEATS},'nullB2':{f:dict(nullB2[f]) for f in FEATS},
 'nullS1':{f:dict(nullS1[f]) for f in FEATS},'nullS2':{f:dict(nullS2[f]) for f in FEATS}},
 open('/home/user/INMA-/research-vault/backtest/scratch/null.pkl','wb'))
print("null built, draws per slot:", NS*len(monthkeys))
