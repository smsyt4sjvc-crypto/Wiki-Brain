import csv,json,statistics as st
from collections import defaultdict, Counter
exec(open('/home/user/INMA-/research-vault/backtest/scratch/anat.py').read().split('print("=== 1. HOLD DAYS ===")')[0])
mt={k:list(d.values())[0]['month_total_pct'] for k,d in tm.items()}
ks=sorted(mt)
print("=== 8. BEST SINGLE LEG vs ORACLE 2-LEG (computed from panel) ===")
best1={}
for k in ks:
    rows=sorted(M[k],key=lambda r:r['date'])
    b=-9e9; lows=[f(r['low']) for r in rows]; highs=[f(r['high']) for r in rows]
    run=lows[0]
    for j in range(len(rows)):
        run=min(run,lows[j]); b=max(b,100*(highs[j]/run-1))
    best1[k]=b
add=[mt[k]-best1[k] for k in ks]
print("  best single low->high in month: mean %.2f%% median %.2f%%  (n=88)"%(st.mean(best1.values()),st.median(best1.values())))
print("  oracle 2-leg total            : mean %.2f%% median %.2f%%"%(st.mean(mt.values()),st.median(mt.values())))
print("  MARGINAL VALUE of 2nd leg     : mean %.2f%% median %.2f%%  = %.0f%% uplift over best single trade"%(
    st.mean(add),st.median(add),100*st.mean(add)/st.mean(list(best1.values()))))
print("  frac of months where 2nd leg adds >3pp: %.0f%%   <1pp: %.0f%%"%(
    100*sum(1 for x in add if x>3)/len(add),100*sum(1 for x in add if x<1)/len(add)))
print("  note: best-single is also the month high/low range when low precedes high; equals range in %d/88 cells"%(
    sum(1 for k in ks if abs(best1[k]-mstat[k]['range_pct'])<1e-6)))

print()
print("=== 9. EDGE (oracle - b&h) CONCENTRATION ===")
edge={k:mt[k]-mstat[k]['bh_pct'] for k in ks}
e=sorted(edge.values(),reverse=True)
print("  edge mean %.2f%% median %.2f%% min %.2f%% max %.2f%% ; frac positive %.0f%%"%(
    st.mean(e),st.median(e),min(e),max(e),100*sum(1 for x in e if x>0)/len(e)))
tot=sum(e)
for k_ in [4,8,11,22,44]: print("   top %2d/88 cells = %.1f%% of total edge (uniform would be %.1f%%)"%(k_,100*sum(e[:k_])/tot,100*k_/88))
def gini(v):
    v=sorted(v); n=len(v); c=sum((i+1)*x for i,x in enumerate(v))
    return (2*c)/(n*sum(v))-(n+1)/n
print("  gini: oracle-total %.3f | edge %.3f | b&h(positive-shifted) %.3f | month-range %.3f"%(
    gini(list(mt.values())),gini(e),gini([x-min(mstat[k]['bh_pct'] for k in ks)+.01 for x in [mstat[k]['bh_pct'] for k in ks]]),
    gini([mstat[k]['range_pct'] for k in ks])))
print("  ORACLE MIN month-cell = %.2f%% (%s) -> oracle never has a losing or flat month; b&h had %d negative of 88"%(
    min(mt.values()),[k for k in ks if mt[k]==min(mt.values())][0],sum(1 for k in ks if mstat[k]['bh_pct']<0)))
print("  top-5 edge cells:", [(k[0],k[1],round(edge[k],1)) for k in sorted(ks,key=lambda k:-edge[k])[:5]])

print()
print("=== 10. HOLD LENGTH vs MONTH VOL ===")
byk=defaultdict(list)
for t in T: byk[(t['sym'],t['month'])].append(t['hold_days'])
rs=sorted(ks,key=lambda k:mstat[k]['realvol'])
for i in range(4):
    q=rs[i*22:(i+1)*22]
    hs=[h for k in q for h in byk[k]]
    sd=sum(1 for h in hs if h==0)
    print("  realvol Q%d (%.1f-%.1f): median hold %.1f  mean %.1f  same-day %d/%d (%.0f%%)  oracle/mo %.2f%%"%(
        i+1,mstat[q[0]]['realvol'],mstat[q[-1]]['realvol'],st.median(hs),st.mean(hs),sd,len(hs),100*sd/len(hs),
        st.mean([mt[k] for k in q])))
print()
print("=== 11. RET_PCT DISTRIBUTION (176 trades) ===")
r=sorted(t['ret_pct'] for t in T)
print("  mean %.2f%% median %.2f%% sd %.2f min %.2f max %.2f ; deciles %s"%(
    st.mean(r),st.median(r),st.pstdev(r),min(r),max(r),[round(x,2) for x in st.quantiles(r,n=10)]))
print("  n<2%%: %d ; n>10%%: %d ; top 10 trades = %.1f%% of 846.7%% total"%(
    sum(1 for x in r if x<2),sum(1 for x in r if x>10),100*sum(r[-10:])/sum(r)))
