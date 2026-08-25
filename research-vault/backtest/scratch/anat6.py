import csv,json,statistics as st,random
from collections import defaultdict, Counter
exec(open('/home/user/INMA-/research-vault/backtest/scratch/anat.py').read().split('print("=== 1. HOLD DAYS ===")')[0])
random.seed(11)
mt={k:list(d.values())[0]['month_total_pct'] for k,d in tm.items()}
ks=sorted(mt)
print("=== 12. NULL for edge-of-month placement ===")
c1=c2=tot=0
for k,d in tm.items():
    h1,h2,N=d[1]['hold_days'],d[2]['hold_days'],d[1]['days_in_month']
    valid=[(b1,b2) for b1 in range(N) for b2 in range(b1+h1,N) if b2+h2<=N-1]
    if not valid: continue
    for _ in range(3000):
        b1,b2=random.choice(valid)
        if b1<3: c1+=1
        if b2+h2>=N-3: c2+=1
        tot+=1
print("  NULL P(leg1 buy in first 3 tdays)=%.0f%%  vs OBS 62%%"%(100*c1/tot))
print("  NULL P(leg2 sell in last 3 tdays)=%.0f%%  vs OBS 74%%"%(100*c2/tot))
# base rate in daily panel: frac of days that are in first3 / last3
d3=sum(1 for r in D if int(r['tday_in_month'])<3)/len(D)
print("  daily_panel base: %.0f%% of all days are in the first 3 tdays of their month"%(100*d3))

print()
print("=== 13. DOWN-MONTH CHECK, range-matched pairing ===")
# pair each down cell with up cells of similar range (+-1pp), compare oracle totals
dn=[k for k in ks if mstat[k]['bh_pct']<=0]; up=[k for k in ks if mstat[k]['bh_pct']>0]
diffs=[]
for k in dn:
    m=[j for j in up if abs(mstat[j]['range_pct']-mstat[k]['range_pct'])<=1.0]
    if m: diffs.append(mt[k]-st.mean([mt[j] for j in m]))
print("  range-matched (+-1pp) down-vs-up oracle total: n=%d matched down cells, mean diff %+.2f%% median %+.2f%% ; frac down<up %.0f%%"%(
    len(diffs),st.mean(diffs),st.median(diffs),100*sum(1 for x in diffs if x<0)/len(diffs)))
# capture ratio up vs down
print("  capture (oracle/range): UP %.3f (n=%d) DOWN %.3f (n=%d)"%(
    st.mean([mt[k]/mstat[k]['range_pct'] for k in up]),len(up),st.mean([mt[k]/mstat[k]['range_pct'] for k in dn]),len(dn)))
print("  path-capture (oracle/path): UP %.3f DOWN %.3f"%(
    st.mean([mt[k]/mstat[k]['path'] for k in up]),st.mean([mt[k]/mstat[k]['path'] for k in dn])))

print()
print("=== 14. CAPTURE RATIO STABILITY (headline denominator test) ===")
cap=[mt[k]/mstat[k]['range_pct'] for k in ks]
print("  n=88 cells. mean %.3f sd %.3f CV %.1f%% ; deciles %s"%(st.mean(cap),st.pstdev(cap),100*st.pstdev(cap)/st.mean(cap),[round(x,2) for x in st.quantiles(cap,n=10)]))
for y in ['2023','2024','2025','2026']:
    g=[k for k in ks if k[1][:4]==y]; print("   %s mean %.3f (n=%d)"%(y,st.mean([mt[k]/mstat[k]['range_pct'] for k in g]),len(g)))
for s in ['spx','ndx']:
    g=[k for k in ks if k[0]==s]; print("   %s  mean %.3f (n=%d)"%(s,st.mean([mt[k]/mstat[k]['range_pct'] for k in g]),len(g)))
rs=sorted(ks,key=lambda k:mstat[k]['range_pct'])
for i in range(4):
    q=rs[i*22:(i+1)*22]; print("   rangeQ%d mean %.3f"%(i+1,st.mean([mt[k]/mstat[k]['range_pct'] for k in q])))
print("  worst cell capture %.3f (%s), best %.3f (%s)"%(min(cap),ks[cap.index(min(cap))],max(cap),ks[cap.index(max(cap))]))

print()
print("=== 15. DEAD-END CHECKS ===")
def corr(a,b):
    ma,mb=st.mean(a),st.mean(b); return sum((x-ma)*(y-mb) for x,y in zip(a,b))/((sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))**.5)
# trade count is fixed at 2, so nothing there. tdays in month vs oracle:
print("  corr(oracle total, tdays in month) r=%+.3f (n=88)"%corr([mt[k] for k in ks],[mstat[k]['n'] for k in ks]))
# dow of buys
print("  buy dow counts:",Counter(t['buy_date'] and __import__('datetime').date.fromisoformat(t['buy_date']).weekday() for t in T))
print("  panel dow base:",Counter(__import__('datetime').date.fromisoformat(r['date']).weekday() for r in D))
# leg1 ret vs leg2 ret correlation within month
a=[tm[k][1]['ret_pct'] for k in ks]; b=[tm[k][2]['ret_pct'] for k in ks]
print("  corr(leg1 ret, leg2 ret) within month r=%+.3f"%corr(a,b))
print("  frac months leg2>leg1: %.0f%%"%(100*sum(1 for x,y in zip(a,b) if y>x)/len(a)))
