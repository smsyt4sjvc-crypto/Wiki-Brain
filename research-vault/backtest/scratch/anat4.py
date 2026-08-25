import csv,json,statistics as st
from collections import defaultdict, Counter
exec(open('/home/user/INMA-/research-vault/backtest/scratch/anat.py').read().split('print("=== 1. HOLD DAYS ===")')[0])
mt={k:list(d.values())[0]['month_total_pct'] for k,d in tm.items()}
def corr(a,b):
    ma,mb=st.mean(a),st.mean(b)
    num=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    return num/((sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))**.5)
def spear(a,b):
    def rk(v):
        s=sorted(range(len(v)),key=lambda i:v[i]); r=[0]*len(v)
        for j,i in enumerate(s): r[i]=j
        return r
    return corr(rk(a),rk(b))
ks=sorted(mt)
O=[mt[k] for k in ks]
print("=== 4. WHAT EXPLAINS MONTH ORACLE TOTAL? (n=88 month-cells) ===")
for name in ['range_pct','path','realvol','atr','vix','n','bh_pct','maxdd']:
    X=[mstat[k][name] for k in ks]
    print("  %-10s pearson r=%+.3f  spearman=%+.3f"%(name,corr(O,X),spear(O,X)))
X=[abs(mstat[k]['bh_pct']) for k in ks]; print("  |bh_pct|   pearson r=%+.3f  spearman=%+.3f"%(corr(O,X),spear(O,X)))
# capture ratio
cap=[mt[k]/mstat[k]['range_pct'] for k in ks]
print("  CAPTURE = oracle_total / month high-low range: mean %.3f median %.3f min %.3f max %.3f sd %.3f"%(
    st.mean(cap),st.median(cap),min(cap),max(cap),st.pstdev(cap)))
capp=[mt[k]/mstat[k]['path'] for k in ks]
print("  oracle_total / month PATH (sum |daily ret|): mean %.3f median %.3f sd %.3f min %.3f max %.3f"%(
    st.mean(capp),st.median(capp),st.pstdev(capp),min(capp),max(capp)))
# linear fit oracle ~ range
mr=st.mean([mstat[k]['range_pct'] for k in ks])
b=sum((mstat[k]['range_pct']-mr)*(mt[k]-st.mean(O)) for k in ks)/sum((mstat[k]['range_pct']-mr)**2 for k in ks)
print("  fit: oracle = %.3f + %.3f * range   (R2=%.3f)"%(st.mean(O)-b*mr,b,corr(O,[mstat[k]['range_pct'] for k in ks])**2))
print("  base rate for 'range': daily_panel month ranges mean %.2f%% median %.2f%%"%(
    st.mean([mstat[k]['range_pct'] for k in ks]),st.median([mstat[k]['range_pct'] for k in ks])))

print()
print("=== 5. UP vs DOWN MONTHS ===")
up=[k for k in ks if mstat[k]['bh_pct']>0]; dn=[k for k in ks if mstat[k]['bh_pct']<=0]
for lab,g in [('UP',up),('DOWN',dn)]:
    print("  %-4s n=%2d  oracle mean %6.2f%%  median %6.2f%%  |  b&h mean %6.2f%%  |  EDGE(oracle-b&h) %6.2f%%  |  range mean %5.2f%%  |  capture(or/range) %.3f"%(
        lab,len(g),st.mean([mt[k] for k in g]),st.median([mt[k] for k in g]),st.mean([mstat[k]['bh_pct'] for k in g]),
        st.mean([mt[k]-mstat[k]['bh_pct'] for k in g]),st.mean([mstat[k]['range_pct'] for k in g]),
        st.mean([mt[k]/mstat[k]['range_pct'] for k in g])))
# control for range: within similar-range buckets, up vs down
rs=sorted(ks,key=lambda k:mstat[k]['range_pct'])
print("  --- controlling for month range (quartiles of range) ---")
for i in range(4):
    q=rs[i*22:(i+1)*22]
    qu=[k for k in q if mstat[k]['bh_pct']>0]; qd=[k for k in q if mstat[k]['bh_pct']<=0]
    print("   Q%d range %.2f-%.2f%%: UP n=%2d oracle %5.2f%% | DOWN n=%2d oracle %5.2f%%"%(
        i+1,mstat[q[0]]['range_pct'],mstat[q[-1]]['range_pct'],len(qu),st.mean([mt[k] for k in qu]) if qu else 0,
        len(qd),st.mean([mt[k] for k in qd]) if qd else 0))

print()
print("=== 6. SPX vs NDX ===")
for s in ['spx','ndx']:
    g=[k for k in ks if k[0]==s]
    print("  %s: oracle sum %.1f%% mean/mo %.2f%% | b&h sum %.1f%% | range mean %.2f%% | hold med %.1f | same-day %d/88"%(
        s,sum(mt[k] for k in g),st.mean([mt[k] for k in g]),sum(mstat[k]['bh_pct'] for k in g),
        st.mean([mstat[k]['range_pct'] for k in g]),st.median([t['hold_days'] for t in T if t['sym']==s]),
        sum(1 for t in T if t['sym']==s and t['hold_days']==0)))
rat=[mt[('ndx',m)]/mt[('spx',m)] for m in sorted(set(m for _,m in ks))]
rrat=[mstat[('ndx',m)]['range_pct']/mstat[('spx',m)]['range_pct'] for m in sorted(set(m for _,m in ks))]
print("  NDX/SPX oracle ratio per month: mean %.3f median %.3f min %.3f max %.3f ; frac>1 %.0f%%"%(
    st.mean(rat),st.median(rat),min(rat),max(rat),100*sum(1 for x in rat if x>1)/len(rat)))
print("  NDX/SPX month-RANGE ratio     : mean %.3f median %.3f ; corr(oracle ratio, range ratio) r=%+.3f"%(
    st.mean(rrat),st.median(rrat),corr(rat,rrat)))
print("  NDX/SPX ratio of ratios (oracle ratio / range ratio): median %.3f"%st.median([a/b for a,b in zip(rat,rrat)]))

print()
print("=== 7. OVER TIME ===")
ms=sorted(set(m for _,m in ks))
for y in ['2023','2024','2025','2026']:
    g=[k for k in ks if k[1][:4]==y]
    print("  %s n=%2d cells: oracle mean %5.2f%%/mo  b&h mean %5.2f%%  range mean %5.2f%%  capture %.3f  hold med %.1f"%(
        y,len(g),st.mean([mt[k] for k in g]),st.mean([mstat[k]['bh_pct'] for k in g]),
        st.mean([mstat[k]['range_pct'] for k in g]),st.mean([mt[k]/mstat[k]['range_pct'] for k in g]),
        st.median([t['hold_days'] for t in T if t['month'][:4]==y])))
