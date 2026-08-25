import csv, math, statistics as st
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
    r['_b']=(r['sym'],r['date']) in buys; r['_s']=(r['sym'],r['date']) in sells
mo=defaultdict(list)
for r in panel: mo[(r['sym'],r['date'][:7])].append(r)
print('sym-months:',len(mo),'sizes',min(len(v) for v in mo.values()),max(len(v) for v in mo.values()))
# within-month percentile of buy days for each feature
cols=[c for c in panel[0] if c not in ('sym','date','month','_b','_s')]
out=[]
for c in cols:
    ps=[]
    for k,rows in mo.items():
        vals=[f(r[c]) for r in rows]
        if any(v is None for v in vals): continue
        n=len(vals)
        for r in rows:
            if r['_b']:
                v=f(r[c]); lo=sum(1 for x in vals if x<v); eq=sum(1 for x in vals if x==v)
                ps.append((lo+0.5*eq)/n)
    if len(ps)<100: continue
    m=st.mean(ps); se=st.stdev(ps)/math.sqrt(len(ps))
    out.append((abs(m-0.5),m,c,len(ps),((m-0.5)/se) if se>0 else 0.0))
out.sort(reverse=True)
print('\n=== WITHIN-SYM-MONTH PERCENTILE OF ORACLE BUY DAYS (0.5 = no info; the box is fully controlled)')
for d,m,c,n,z in out[:16]: print('%-24s mean pctile=%.3f  n=%d  z=%+6.2f'%(c,m,n,z))
print('\n  (bottom / least informative)')
for d,m,c,n,z in out[-8:]: print('%-24s mean pctile=%.3f  n=%d  z=%+6.2f'%(c,m,n,z))
print('\n=== how ORDINARY do perfect entries look? (unique buy-days n=167)')
ub=[r for r in panel if r['_b']]
def sh(name,cond,rows=ub):
    n=sum(1 for r in rows if cond(r)); pn=sum(1 for r in panel if cond(r))
    print('%-38s buys %3d/%d = %5.1f%%   panel %4d/1817 = %5.1f%%  lift %.2fx'%(name,n,len(rows),100*n/len(rows),pn,100*pn/1817,(n/len(rows))/(pn/1817)))
sh('is_20d_low',lambda r:f(r['is_20d_low'])==1)
sh('rsi14<30',lambda r:f(r['rsi14'])<30)
sh('rsi14>50',lambda r:f(r['rsi14'])>50)
sh('dd_from_20d_high > -1% (near highs)',lambda r:f(r['dd_from_20d_high_pct'])>-1)
sh('NONE of {20dlow,rsi<40,dd>3%}',lambda r: not(f(r['is_20d_low'])==1 or f(r['rsi14'])<40 or f(r['dd_from_20d_high_pct'])<=-3))
sh('ANY of {20dlow,rsi<40,dd>3%}',lambda r: (f(r['is_20d_low'])==1 or f(r['rsi14'])<40 or f(r['dd_from_20d_high_pct'])<=-3))
print('\n=== SELL SIDE mirror (unique sell-days n=173, base %.4f)'%(173/1817))
us=[r for r in panel if r['_s']]
def sh2(name,cond):
    n=sum(1 for r in us if cond(r)); pn=sum(1 for r in panel if cond(r))
    print('%-38s sells %3d/%d = %5.1f%%  panel %4d = %5.1f%%  lift %.2fx'%(name,n,len(us),100*n/len(us),pn,100*pn/1817,(n/len(us))/(pn/1817)))
sh2('is_20d_high',lambda r:f(r['is_20d_high'])==1)
sh2('rsi14>70',lambda r:f(r['rsi14'])>70)
sh2('bb_pctB>0.95',lambda r:f(r['bb_pctB'])>0.95)
sh2('rsi14<50 (sold into weakness)',lambda r:f(r['rsi14'])<50)
