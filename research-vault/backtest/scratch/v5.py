import csv, statistics as st
F='/home/user/INMA-/research-vault/backtest/out/oracle_features.csv'
tr=list(csv.DictReader(open(F)))
cols=tr[0].keys()
retcol=[c for c in cols if 'ret' in c.lower() and not c.startswith(('B_','S_'))]
print("n trades",len(tr)); print("non-prefixed cols:",[c for c in cols if not c.startswith(('B_','S_'))])
