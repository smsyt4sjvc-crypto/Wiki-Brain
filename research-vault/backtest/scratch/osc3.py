import csv, statistics as st
from collections import defaultdict, Counter
OUT='/home/user/INMA-/research-vault/backtest/out/'
D=list(csv.DictReader(open(OUT+'daily_panel.csv')))
O=list(csv.DictReader(open(OUT+'oracle_features.csv')))
def f(v):
    try: return float(v)
    except: return None
buys=set((r['sym'],r['buy_date']) for r in O)
for r in D: r['_isbuy']=(r['sym'],r['date']) in buys
BASE=sum(1 for r in D if r['_isbuy'])/len(D)
def episodes(sub,gap=5):
    # cluster by date (union across syms) into episodes separated by >gap calendar days
    ds=sorted(set(r['date'] for r in sub))
    from datetime import date
    def p(s): y,m,d=map(int,s.split('-')); return date(y,m,d)
    ep=[];cur=[ds[0]] if ds else []
    for a,b in zip(ds,ds[1:]):
        if (p(b)-p(a)).days>gap: ep.append(cur);cur=[b]
        else: cur.append(b)
    if cur: ep.append(cur)
    return ep
print("=== CLUSTERING / EFFECTIVE INDEPENDENCE ===")
for name,pred in [("rsi<25",lambda r:f(r['rsi14'])<25),("rsi<30",lambda r:f(r['rsi14'])<30),
                  ("bb<0.05",lambda r:f(r['bb_pctB'])<0.05),("is_20d_low",lambda r:r['is_20d_low']=='1'),
                  ("is_63d_low",lambda r:r['is_63d_low']=='1'),("consec_down>=3",lambda r:f(r['consec_down_days'])>=3),
                  ("rsi<30 & 20dlow",lambda r:f(r['rsi14'])<30 and r['is_20d_low']=='1')]:
    sub=[r for r in D if pred(r)]
    ep=episodes(sub)
    ym=Counter(r['date'][:7] for r in sub)
    print("%-18s rows=%4d uniq_dates=%3d episodes(gap>5d)=%2d  top months: %s"%(name,len(sub),len(set(r['date'] for r in sub)),len(ep),", ".join("%s:%d"%x for x in ym.most_common(5))))
    print("      episode spans: %s"%("; ".join("%s..%s(%d)"%(e[0],e[-1],len(e)) for e in ep)))

# sell-side reverse conditionals with sell base
sells=set((r['sym'],r['sell_date']) for r in O)
for r in D: r['_issell']=(r['sym'],r['date']) in sells
SB=sum(1 for r in D if r['_issell'])/len(D)
print("\n=== SELL SIDE, lift vs SELL base %.4f ==="%SB)
ns=sum(1 for r in D if r['_issell'])
for name,pred in [("rsi>70",lambda r:f(r['rsi14'])>70),("rsi>75",lambda r:f(r['rsi14'])>75),("rsi>80",lambda r:f(r['rsi14'])>80),
   ("bb>0.95",lambda r:f(r['bb_pctB'])>0.95),("bb>1.0",lambda r:f(r['bb_pctB'])>1.0),("is_20d_high",lambda r:r['is_20d_high']=='1'),
   ("is_63d_high",lambda r:r['is_63d_high']=='1'),("consec_up>=3",lambda r:f(r['consec_up_days'])>=3),
   ("is_20d_high & rsi>70",lambda r:r['is_20d_high']=='1' and f(r['rsi14'])>70),
   ("rsi<40 (sells!)",lambda r:f(r['rsi14'])<40)]:
    sub=[r for r in D if pred(r)]; k=sum(1 for r in sub if r['_issell'])
    print("%-22s days=%4d P(sell)=%.3f lift=%.2fx recall=%d/%d=%.0f%%"%(name,len(sub),k/len(sub),(k/len(sub))/SB,k,ns,100*k/ns))

# how many oracle SELLS were at RSI<50 / not overbought
print("\nsell-day RSI deciles:")
sv=sorted(f(r['rsi14']) for r in D if r['_issell'])
print("  sells: min %.1f p25 %.1f med %.1f p75 %.1f max %.1f ; frac RSI<50 = %.2f ; frac>70 = %.2f"%(sv[0],sv[len(sv)//4],sv[len(sv)//2],sv[3*len(sv)//4],sv[-1],sum(1 for x in sv if x<50)/len(sv),sum(1 for x in sv if x>70)/len(sv)))
bv=sorted(f(r['rsi14']) for r in D if r['_isbuy'])
print("  buys : frac RSI<30 = %.2f ; frac>50 = %.2f ; frac>60 = %.2f"%(sum(1 for x in bv if x<30)/len(bv),sum(1 for x in bv if x>50)/len(bv),sum(1 for x in bv if x>60)/len(bv)))

# per-index split (robustness)
print("\n=== PER-INDEX (spx vs ndx) for headline conditions ===")
for sym in ('spx','ndx'):
    Ds=[r for r in D if r['sym']==sym]; b=sum(1 for r in Ds if r['_isbuy'])/len(Ds)
    for name,pred in [("rsi<30",lambda r:f(r['rsi14'])<30),("is_20d_low",lambda r:r['is_20d_low']=='1'),("consec_down>=3",lambda r:f(r['consec_down_days'])>=3),("bb<0.05",lambda r:f(r['bb_pctB'])<0.05)]:
        sub=[r for r in Ds if pred(r)]; k=sum(1 for r in sub if r['_isbuy'])
        print("  %s %-16s days=%3d P(buy)=%.3f lift=%.2fx"%(sym,name,len(sub),k/len(sub) if sub else 0,(k/len(sub))/b if sub else 0))

# forward returns by year for rsi<30 (regime check)
px=defaultdict(dict)
for r in D: px[r['sym']][r['date']]=f(r['close'])
dates={s:sorted(px[s]) for s in px}; idx={s:{d:i for i,d in enumerate(dates[s])} for s in px}
def fwd(sym,date,h):
    i=idx[sym][date]
    if i+h>=len(dates[sym]): return None
    return 100*(px[sym][dates[sym][i+h]]/px[sym][dates[sym][i]]-1)
print("\n=== rsi<30 forward 5d by YEAR (regime check) ===")
byy=defaultdict(list); allby=defaultdict(list)
for r in D:
    v=fwd(r['sym'],r['date'],5)
    if v is None: continue
    allby[r['date'][:4]].append(v)
    if f(r['rsi14'])<30: byy[r['date'][:4]].append(v)
for y in sorted(allby):
    v=byy.get(y,[])
    print("  %s: rsi<30 n=%3d mean=%s  | ALL n=%4d mean=%+.2f%%"%(y,len(v),("%+.2f%%"%st.mean(v)) if v else "  n/a ",len(allby[y]),st.mean(allby[y])))
