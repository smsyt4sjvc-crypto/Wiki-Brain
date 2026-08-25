import csv, statistics as st, json
from collections import defaultdict
OUT='/home/user/INMA-/research-vault/backtest/out/'
D=list(csv.DictReader(open(OUT+'daily_panel.csv')))
O=list(csv.DictReader(open(OUT+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
buys=set((r['sym'],r['buy_date']) for r in O); sells=set((r['sym'],r['sell_date']) for r in O)
print("unique buy days",len(buys),"unique sell days",len(sells),"trades",len(O),"daily rows",len(D))
for r in D: r['_isbuy']=(r['sym'],r['date']) in buys; r['_issell']=(r['sym'],r['date']) in sells
matched=sum(1 for r in D if r['_isbuy'])
print("buy days matched into panel:",matched,"of",len(buys))
BASE=matched/len(D)
print("BASE RATE P(day is oracle buy) = %.4f"%BASE)

def dist(col,vals):
    v=sorted(x for x in vals if x is not None)
    q=lambda p: v[int(p*(len(v)-1))]
    return dict(n=len(v),mean=round(st.mean(v),3),med=round(q(.5),3),p10=round(q(.1),3),p25=round(q(.25),3),p75=round(q(.75),3),p90=round(q(.9),3))

FEATS=['rsi14','bb_pctB','consec_down_days','is_20d_low','is_63d_low','dd_from_20d_high_pct','ret_5d_pct','ret_1d_pct','consec_up_days','is_20d_high','is_63d_high','dd_from_63d_high_pct']
print("\n=== DISTRIBUTIONS: buy-day vs all-days vs sell-day ===")
for c in FEATS:
    all_=[f(r[c]) for r in D]
    b=[f(r[c]) for r in D if r['_isbuy']]
    s=[f(r[c]) for r in D if r['_issell']]
    print(c)
    print("   ALL ",dist(c,all_))
    print("   BUY ",dist(c,b))
    print("   SELL",dist(c,s))

print("\n=== REVERSE CONDITIONAL: P(oracle buy | condition) — THE NUMBER THAT MATTERS ===")
def rev(name,pred):
    sub=[r for r in D if pred(r)]
    if not sub: print("%-34s n=0"%name); return
    k=sum(1 for r in sub if r['_isbuy'])
    ks=sum(1 for r in sub if r['_issell'])
    print("%-34s days=%4d  P(buy)=%.3f lift=%.2fx  |  P(sell)=%.3f"%(name,len(sub),k/len(sub),(k/len(sub))/BASE,ks/len(sub)))
for th in [20,25,30,35,40,45,50,60,70,80]:
    rev("rsi14 < %d"%th, lambda r,t=th: f(r['rsi14'])<t)
print()
for th in [30,40,50,60,70,75,80]:
    rev("rsi14 > %d"%th, lambda r,t=th: f(r['rsi14'])>t)
print()
for lo,hi in [(0,25),(25,30),(30,35),(35,40),(40,45),(45,50),(50,55),(55,60),(60,65),(65,70),(70,75),(75,101)]:
    rev("rsi14 in [%d,%d)"%(lo,hi), lambda r,l=lo,h=hi: l<=f(r['rsi14'])<h)
print()
for th in [0.0,0.05,0.1,0.2,0.3,0.5]:
    rev("bb_pctB < %.2f"%th, lambda r,t=th: f(r['bb_pctB'])<t)
for th in [0.8,0.9,0.95,1.0]:
    rev("bb_pctB > %.2f"%th, lambda r,t=th: f(r['bb_pctB'])>t)
print()
for th in [1,2,3,4,5]:
    rev("consec_down_days >= %d"%th, lambda r,t=th: f(r['consec_down_days'])>=t)
for th in [1,2,3,4,5]:
    rev("consec_up_days >= %d"%th, lambda r,t=th: f(r['consec_up_days'])>=t)
print()
rev("is_20d_low==1", lambda r: r['is_20d_low']=='1')
rev("is_63d_low==1", lambda r: r['is_63d_low']=='1')
rev("is_20d_high==1", lambda r: r['is_20d_high']=='1')
rev("is_63d_high==1", lambda r: r['is_63d_high']=='1')
print()
rev("rsi<30 AND is_20d_low", lambda r: f(r['rsi14'])<30 and r['is_20d_low']=='1')
rev("rsi<35 AND bb_pctB<0.1", lambda r: f(r['rsi14'])<35 and f(r['bb_pctB'])<0.1)
rev("bb<0.05 AND is_20d_low", lambda r: f(r['bb_pctB'])<0.05 and r['is_20d_low']=='1')
rev("is_20d_low AND consecdown>=2", lambda r: r['is_20d_low']=='1' and f(r['consec_down_days'])>=2)
