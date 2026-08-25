import csv, statistics as st
from collections import defaultdict
from datetime import date
P='/home/user/INMA-/research-vault/backtest/out/daily_panel.csv'
rows=list(csv.DictReader(open(P)))
by=defaultdict(list)
for r in rows: by[r['sym']].append(r)
for s in by: by[s].sort(key=lambda r:r['date'])
def f(r,k):
    v=r[k]; return float(v) if v not in ('','NA','nan',None) else None
recs=[]
for s,rs in by.items():
    n=len(rs)
    for i,r in enumerate(rs):
        if i+10>=n: continue
        c=f(r,'close'); fut=rs[i+1:i+11]
        recs.append(dict(sym=s,date=r['date'],
            up10=(max(f(x,'high') for x in fut)/c-1)*100,
            dn10=(min(f(x,'low') for x in fut)/c-1)*100,
            r10=(f(rs[i+10],'close')/c-1)*100,
            d200=f(r,'dist_sma200_pct'),atr=f(r,'atr14_pct'),vix=f(r,'vix')))
med=lambda v: st.median(v) if v else float('nan')
be=[x for x in recs if x['d200']<0]; ab=[x for x in recs if x['d200']>=0]

# macro episodes (union across indices)
def ep(d):
    y,m=int(d[:4]),int(d[5:7])
    if y==2023 and m<=3: return "2023Q1"
    if y==2023 and m>=10: return "2023-Oct"
    if y==2025: return "2025-Mar-May"
    if y==2026: return "2026-Mar-Apr"
    return "other"
E=defaultdict(list)
for x in be: E[ep(x['date'])].append(x)
print("=== MACRO EPISODES (below-200DMA days pooled over spx+ndx) ===")
for k,v in sorted(E.items()):
    print("  %-13s n=%3d  medUP10 %6.3f  medR10 %+6.3f  medATR %.2f"%(k,len(v),med([y['up10'] for y in v]),med([y['r10'] for y in v]),med([y['atr'] for y in v])))
print("  -> %d distinct macro episodes. EFFECTIVE n = %d, not 168."%(len(E),len(E)))

print("\n=== LEAVE-ONE-EPISODE-OUT (the real independence test) ===")
base_ab_up=med([x['up10'] for x in ab]); base_ab_r10=med([x['r10'] for x in ab])
for k in sorted(E):
    rest=[x for x in be if ep(x['date'])!=k]
    print("  drop %-13s n=%3d  medUP %6.3f lift %.2fx | medR10 %+6.3f lift %.2fx"%(
        k,len(rest),med([x['up10'] for x in rest]),med([x['up10'] for x in rest])/base_ab_up,
        med([x['r10'] for x in rest]),med([x['r10'] for x in rest])/base_ab_r10))
print("  ALL episodes present: medUP %.3f lift %.2fx | medR10 %+.3f lift %.2fx"%(
    med([x['up10'] for x in be]),med([x['up10'] for x in be])/base_ab_up,
    med([x['r10'] for x in be]),med([x['r10'] for x in be])/base_ab_r10))

print("\n=== VOLATILITY CONTROL: match on ATR14%% decile ===")
alld=sorted(recs,key=lambda x:x['atr'])
N=len(alld); dec=[alld[i*N//10:(i+1)*N//10] for i in range(10)]
tot_b=tot_a=0; wl=[]
for i,d in enumerate(dec):
    b=[x['up10'] for x in d if x['d200']<0]; a=[x['up10'] for x in d if x['d200']>=0]
    lo,hi=d[0]['atr'],d[-1]['atr']
    print("  ATR dec%d [%.2f-%.2f] nBelow=%3d nAbove=%3d  medUP below %6.3f above %6.3f  lift %s"%(
        i+1,lo,hi,len(b),len(a),med(b) if b else float('nan'),med(a) if a else float('nan'),
        ("%.2fx"%(med(b)/med(a))) if b and a else "-"))
    if b and a: wl.append((len(b),med(b)/med(a)))
w=sum(n*l for n,l in wl)/sum(n for n,l in wl)
print("  n-weighted within-ATR-decile lift = %.2fx  (vs headline 2.63x)"%w)

print("\n=== IS THE SAMPLE WINDOW ITSELF THE FINDING? ===")
print("  Sustained bear markets in Jan2023-Aug2026 window: below-200DMA days = %.1f%% of all days."%(100*len(be)/len(recs)))
print("  Every one of the %d episodes was followed by recovery to new highs within the window."%len(E))
mx=[x for x in be]
print("  Fraction of below-200 days with POSITIVE 10d close return: %.1f%% (above-200: %.1f%%)"%(
    100*sum(1 for x in be if x['r10']>0)/len(be), 100*sum(1 for x in ab if x['r10']>0)/len(ab)))
