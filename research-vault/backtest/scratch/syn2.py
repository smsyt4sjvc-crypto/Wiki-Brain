import csv, statistics as st, math, random
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(P+'daily_panel.csv')))
tr=list(csv.DictReader(open(P+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
buys={(t['sym'],t['buy_date']) for t in tr}
sells={(t['sym'],t['sell_date']) for t in tr}
for r in panel:
    r['_b']=1 if (r['sym'],r['date']) in buys else 0
    r['_s']=1 if (r['sym'],r['date']) in sells else 0
N=len(panel); B=sum(r['_b'] for r in panel); S=sum(r['_s'] for r in panel)
base=B/N
print('=== A: BUY-DAY PREDICATES (n, precision, recall, lift). base=%.4f (%d/%d)'%(base,B,N))
preds={
 'is_20d_low==1': lambda r: f(r['is_20d_low'])==1,
 'is_63d_low==1': lambda r: f(r['is_63d_low'])==1,
 'rsi14<30': lambda r: f(r['rsi14'])<30,
 'rsi14<40': lambda r: f(r['rsi14'])<40,
 'bb_pctB<0.05': lambda r: f(r['bb_pctB'])<0.05,
 'dd_from_20d_high>3%': lambda r: f(r['dd_from_20d_high_pct'])<=-3,
 'dd_from_20d_high>5%': lambda r: f(r['dd_from_20d_high_pct'])<=-5,
 'vix_chg5d>+2': lambda r: f(r['vix_chg5d'])>2,
 'vix_chg5d>+4': lambda r: f(r['vix_chg5d'])>4,
 'vix_pctile>0.8': lambda r: f(r['vix_pctile_252d'])>0.8,
 'ret_1d<-1%': lambda r: f(r['ret_1d_pct'])<-1,
 'ret_5d<-3%': lambda r: f(r['ret_5d_pct'])<-3,
 'consec_down>=3': lambda r: f(r['consec_down_days'])>=3,
 'hyg_chg5d<-0.5%': lambda r: f(r['hyg_chg5d'])<-0.5,
 'atr14_pct>1.2': lambda r: f(r['atr14_pct'])>1.2,
 'realvol20>20': lambda r: f(r['realvol20_ann_pct'])>20,
 'dist_sma20<-2%': lambda r: f(r['dist_sma20_pct'])<-2,
}
rows=[]
for name,p in preds.items():
    sub=[r for r in panel if p(r)]
    n=len(sub); h=sum(r['_b'] for r in sub)
    if n==0: continue
    prec=h/n; rows.append((prec/base,name,n,h,prec,h/B))
for lift,name,n,h,prec,rec in sorted(rows,reverse=True):
    print('%-22s n=%4d hits=%3d prec=%5.1f%% recall=%5.1f%% lift=%4.2fx'%(name,n,h,prec*100,rec*100,lift))

print()
print('=== C: INCREMENTAL — within is_20d_low days only (the tautology-stripped stratum)')
strat=[r for r in panel if f(r['is_20d_low'])==1]
n0=len(strat); b0=sum(r['_b'] for r in strat); print('stratum n=%d buys=%d base=%.4f'%(n0,b0,b0/n0))
sb=b0/n0
for name,p in preds.items():
    sub=[r for r in strat if p(r)]
    n=len(sub); h=sum(r['_b'] for r in sub)
    if n<15: continue
    print('%-22s n=%4d hits=%3d prec=%5.1f%% lift_within=%4.2fx'%(name,n,h,h/n*100,(h/n)/sb))
