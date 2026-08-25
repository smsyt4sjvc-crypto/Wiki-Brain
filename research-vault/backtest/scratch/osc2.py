import csv, statistics as st
from collections import defaultdict
OUT='/home/user/INMA-/research-vault/backtest/out/'
D=list(csv.DictReader(open(OUT+'daily_panel.csv')))
O=list(csv.DictReader(open(OUT+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
buys=set((r['sym'],r['buy_date']) for r in O); sells=set((r['sym'],r['sell_date']) for r in O)
for r in D: r['_isbuy']=(r['sym'],r['date']) in buys; r['_issell']=(r['sym'],r['date']) in sells
BASE=sum(1 for r in D if r['_isbuy'])/len(D); SBASE=sum(1 for r in D if r['_issell'])/len(D)
print("BASE buy=%.4f sell=%.4f"%(BASE,SBASE))

# --- COVERAGE (recall): what fraction of oracle buys satisfy each condition
nb=sum(1 for r in D if r['_isbuy'])
print("\n=== COVERAGE of oracle buys (recall), n_buydays=%d ==="%nb)
conds={'rsi<25':lambda r:f(r['rsi14'])<25,'rsi<30':lambda r:f(r['rsi14'])<30,'rsi<35':lambda r:f(r['rsi14'])<35,
 'rsi<40':lambda r:f(r['rsi14'])<40,'rsi>50':lambda r:f(r['rsi14'])>50,'rsi>60':lambda r:f(r['rsi14'])>60,
 'bb<0.1':lambda r:f(r['bb_pctB'])<0.1,'bb>0.5':lambda r:f(r['bb_pctB'])>0.5,'is_20d_low':lambda r:r['is_20d_low']=='1',
 'is_63d_low':lambda r:r['is_63d_low']=='1','cdown>=3':lambda r:f(r['consec_down_days'])>=3,
 'ANY of rsi<30/bb<0.1/20dlow':lambda r: f(r['rsi14'])<30 or f(r['bb_pctB'])<0.1 or r['is_20d_low']=='1',
 'NONE of those 3':lambda r: not(f(r['rsi14'])<30 or f(r['bb_pctB'])<0.1 or r['is_20d_low']=='1')}
for k,p in conds.items():
    hit=sum(1 for r in D if r['_isbuy'] and p(r)); allc=sum(1 for r in D if p(r))
    print("%-30s recall=%3d/%d=%.1f%%  precision=%.3f (lift %.2fx) alldays=%d"%(k,hit,nb,100*hit/nb,hit/allc if allc else 0,(hit/allc)/BASE if allc else 0,allc))

# --- FORWARD RETURNS from daily panel: the anti-tautology test
px=defaultdict(dict)
for r in D: px[r['sym']][r['date']]=f(r['close'])
dates={s:sorted(px[s]) for s in px}
idx={s:{d:i for i,d in enumerate(dates[s])} for s in px}
def fwd(sym,date,h):
    i=idx[sym][date]
    if i+h>=len(dates[sym]): return None
    a=px[sym][dates[sym][i]]; b=px[sym][dates[sym][i+h]]
    return 100*(b/a-1)
for r in D:
    for h in (5,10,21):
        r['_f%d'%h]=fwd(r['sym'],r['date'],h)
print("\n=== FORWARD RETURN (daily panel, ALL days — no oracle selection) ===")
def frow(name,sub):
    out=name.ljust(30)
    for h in (5,10,21):
        v=[r['_f%d'%h] for r in sub if r['_f%d'%h] is not None]
        if not v: out+=" h%d n=0"%h; continue
        out+="  h%02d n=%4d mean=%+.2f%% med=%+.2f%% pos=%.0f%%"%(h,len(v),st.mean(v),st.median(v),100*sum(1 for x in v if x>0)/len(v))
    print(out)
frow("ALL DAYS (base)",D)
for lo,hi in [(0,25),(25,30),(30,40),(40,50),(50,60),(60,70),(70,101)]:
    frow("rsi %d-%d"%(lo,hi),[r for r in D if lo<=f(r['rsi14'])<hi])
frow("bb_pctB<0.05",[r for r in D if f(r['bb_pctB'])<0.05])
frow("is_20d_low",[r for r in D if r['is_20d_low']=='1'])
frow("is_63d_low",[r for r in D if r['is_63d_low']=='1'])
frow("consec_down>=3",[r for r in D if f(r['consec_down_days'])>=3])
frow("rsi<30 & is_20d_low",[r for r in D if f(r['rsi14'])<30 and r['is_20d_low']=='1'])
frow("rsi>70",[r for r in D if f(r['rsi14'])>70])
frow("is_20d_high",[r for r in D if r['is_20d_high']=='1'])

# --- CONDITIONAL-ON-LOW test: does RSI add anything beyond 'price is locally low'?
print("\n=== RULE-3 TEST: does the oscillator add lift BEYOND 'price is locally low'? ===")
def rev2(name,sub):
    if not sub: print(name,"n=0"); return
    k=sum(1 for r in sub if r['_isbuy'])
    print("%-46s days=%4d P(buy)=%.3f lift=%.2fx"%(name,len(sub),k/len(sub),(k/len(sub))/BASE))
strat=[r for r in D if r['is_20d_low']=='1']
rev2("is_20d_low (all)",strat)
rev2("  is_20d_low & rsi<30",[r for r in strat if f(r['rsi14'])<30])
rev2("  is_20d_low & rsi>=30",[r for r in strat if f(r['rsi14'])>=30])
for lo,hi in [(-100,-5),(-5,-3),(-3,-1.5),(-1.5,-0.5),(-0.5,1)]:
    s=[r for r in D if lo<=f(r['dd_from_20d_high_pct'])<hi]
    rev2("dd_from_20d_high in [%s,%s)"%(lo,hi),s)
    rev2("   ^ & rsi<35",[r for r in s if f(r['rsi14'])<35])
    rev2("   ^ & rsi>=35",[r for r in s if f(r['rsi14'])>=35])

# --- WITHIN-MONTH RANK: is the oracle buy the month's lowest-RSI day?
print("\n=== WITHIN-MONTH RANK of oracle buy days ===")
groups=defaultdict(list)
for r in D: groups[(r['sym'],r['date'][:7])].append(r)
ranks=[];lowrsi_hit=0;months=0;nbuy=0
lowdd_hit=0
for k,g in groups.items():
    g2=sorted(g,key=lambda r:f(r['rsi14']))
    months+=1
    n=len(g2)
    best=g2[0]
    if best['_isbuy']: lowrsi_hit+=1
    for i,r in enumerate(g2):
        if r['_isbuy']: ranks.append((i+1)/n); nbuy+=1
    g3=sorted(g,key=lambda r:f(r['low']))
    if g3[0]['_isbuy']: lowdd_hit+=1
print("months(sym x month)=%d  buy days=%d"%(months,nbuy))
print("P(month's LOWEST-RSI day is an oracle buy) = %d/%d = %.3f ; random base ~ 2/21 = %.3f"%(lowrsi_hit,months,lowrsi_hit/months,2/21))
print("P(month's LOWEST-PRICE(low) day is an oracle buy) = %d/%d = %.3f"%(lowdd_hit,months,lowdd_hit/months))
print("mean within-month RSI percentile rank of oracle buys = %.3f (0=lowest RSI in month, 0.5=random)"%st.mean(ranks))
