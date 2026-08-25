import csv, collections, math
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
print("panel rows",len(panel),"trades",len(tr))
# missingness
pm=sum(1 for r in panel if r['rsi14'] in ('','NA','nan'))
tm=sum(1 for r in tr if r['B_rsi14'] in ('','NA','nan'))
print("panel rsi missing",pm,"trade B_rsi missing",tm)
# do buy dates match panel keys?
pkey={(r['sym'],r['date']) for r in panel}
buys=[(r['sym'],r['buy_date']) for r in tr]
print("buys matched in panel:",sum(1 for b in buys if b in pkey),"of",len(buys))
print("unique buy (sym,date):",len(set(buys)))
dupes=[k for k,v in collections.Counter(buys).items() if v>1]
print("dup buy days:",len(dupes))
