import csv, statistics as st
from collections import defaultdict
O='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(O+'daily_panel.csv')))
tr=list(csv.DictReader(open(O+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
print("panel rows",len(panel),"trades",len(tr))
# hyg macro identical across syms?
bydate=defaultdict(set)
for r in panel:
    bydate[r['date']].add(r['hyg_chg5d'])
multi=[d for d,s in bydate.items() if len(s)>1]
print("unique panel dates",len(bydate),"dates w/ differing hyg_chg5d across syms",len(multi))
missing=[d for d,s in bydate.items() if any(x=='' for x in s)]
print("panel dates with blank hyg_chg5d",len(missing))
# base rate unique-date basis
ud=sorted(d for d in bydate if all(x!='' for x in bydate[d]))
vals={d:float(list(bydate[d])[0]) for d in ud}
neg=sum(1 for d in ud if vals[d]<0)
print("BASE unique-date: %d/%d = %.1f%%"%(neg,len(ud),100*neg/len(ud)))
# row basis
rows=[f(r['hyg_chg5d']) for r in panel if r['hyg_chg5d']!='']
print("BASE row-basis: %d/%d = %.1f%%"%(sum(1 for v in rows if v<0),len(rows),100*sum(1 for v in rows if v<0)/len(rows)))
# buys
bd=defaultdict(list)
for t in tr: bd[t['buy_date']].append(t)
ub=sorted(bd)
print("unique buy dates",len(ub))
bvals={d:f(bd[d][0]['B_hyg_chg5d']) for d in ub}
bmiss=[d for d in ub if bvals[d] is None]
print("buy dates missing hyg",len(bmiss))
ubv=[d for d in ub if bvals[d] is not None]
bneg=sum(1 for d in ubv if bvals[d]<0)
print("BUY unique-date: %d/%d = %.1f%%  lift %.3f"%(bneg,len(ubv),100*bneg/len(ubv),(bneg/len(ubv))/(neg/len(ud))))
tvals=[f(t['B_hyg_chg5d']) for t in tr if t['B_hyg_chg5d']!='']
print("BUY trade-level: %d/%d = %.1f%%"%(sum(1 for v in tvals if v<0),len(tvals),100*sum(1 for v in tvals if v<0)/len(tvals)))
# sells
sd=defaultdict(list)
for t in tr: sd[t['sell_date']].append(t)
us=sorted(sd); svals={d:f(sd[d][0]['S_hyg_chg5d']) for d in us}
usv=[d for d in us if svals[d] is not None]
sneg=sum(1 for d in usv if svals[d]<0)
print("SELL unique-date: %d/%d = %.1f%%"%(sneg,len(usv),100*sneg/len(usv)))
# by year
print("\nBY YEAR (unique buy dates)")
for y in ['2023','2024','2025','2026']:
    bb=[d for d in ubv if d.startswith(y)]
    pp=[d for d in ud if d.startswith(y)]
    if not bb: continue
    b=sum(1 for d in bb if vals.get(d,bvals[d])<0)/len(bb)
    p=sum(1 for d in pp if vals[d]<0)/len(pp)
    print("  %s buy %.1f%% (n=%d) vs panel %.1f%% (n=%d) lift %.2f"%(y,100*b,len(bb),100*p,len(pp),b/p))
