import csv, statistics as st, math, json
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
print('panel rows',len(panel),'trades',len(tr))
def f(v):
    try: return float(v)
    except: return None
cols=[c for c in panel[0] if c not in ('sym','date','month')]
num=[c for c in cols if all(f(r[c]) is not None for r in panel)]
print('numeric complete cols',len(num),'of',len(cols))
missing=[c for c in cols if c not in num]
print('cols with blanks:',missing, {c:sum(1 for r in panel if f(r[c]) is None) for c in missing})
buys={(t['sym'],t['buy_date']) for t in tr}
sells={(t['sym'],t['sell_date']) for t in tr}
print('unique buy days',len(buys),'unique sell days',len(sells),'overlap',len(buys&sells))
keys={(r['sym'],r['date']) for r in panel}
print('buys in panel',len(buys&keys),'sells in panel',len(sells&keys))
base=len(buys)/len(panel); print('buy base rate %.4f'%base, 'sell base %.4f'%(len(sells)/len(panel)))
json.dump({'nb':len(buys),'ns':len(sells)},open('/tmp/x.json','w'))
