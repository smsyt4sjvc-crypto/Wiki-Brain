exec(open('/home/user/INMA-/research-vault/backtest/scratch/setup.py').read())
buy_dates=sorted(set(t['buy_date'] for t in trades)); pby={r['date']:r for r in mpanel}
spx=[r for r in panel if r['sym']=='spx']; sby={r['date']:r for r in spx}
print('=== MECHANICAL CHANNEL: is intraday range wider on rate-shock days? (panel only) ===')
S=[];N=[]
for r in spx:
    u=f(pby[r['date']],'ust_y10_chg5d'); hi=f(r,'high'); lo=f(r,'low'); c=f(r,'close')
    if None in (u,hi,lo,c) or c==0: continue
    rng=(hi-lo)/c*100
    (S if abs(u)>=0.15 else N).append(rng)
print(f"  shock days: median range {st.median(S):.3f}% n={len(S)}   non-shock: {st.median(N):.3f}% n={len(N)}  ratio {st.median(S)/st.median(N):.2f}")
print('  -> rate-shock days ARE wider-range; a wider bar is mechanically likelier to hold the month low.')

print('\n=== Does the shock lift survive conditioning on intraday RANGE tercile? ===')
rr=[]
for r in spx:
    hi=f(r,'high'); lo=f(r,'low'); c=f(r,'close')
    if None in (hi,lo,c) or c==0: continue
    rr.append(((hi-lo)/c*100, r['date']))
vals=sorted(x for x,_ in rr); a1,a2=vals[len(vals)//3], vals[2*len(vals)//3]
rmap={d:x for x,d in rr}
def rb(d):
    x=rmap.get(d)
    return None if x is None else ('lo' if x<a1 else ('mid' if x<a2 else 'hi'))
print(f"  range terciles {a1:.3f}% / {a2:.3f}%")
for b in ['lo','mid','hi']:
    P=[d for _,d in rr if rb(d)==b]; B=[d for d in buy_dates if rb(d)==b]
    def fr(ds):
        v=[abs(f(pby[d],'ust_y10_chg5d'))>=0.15 for d in ds if d in pby and f(pby[d],'ust_y10_chg5d') is not None]
        return len(v), sum(v)/len(v)*100 if v else float('nan')
    pn,pp=fr(P); bn,bp=fr(B)
    print(f"  {b:<4} panel {pp:5.1f}% (n={pn})  buy {bp:5.1f}% (n={bn})  lift {bp/pp:.2f}")

print('\n=== DXY: 5d change at buys (level-agnostic), by year — mean bp and frac UP ===')
for y in ['2023','2024','2025','2026','ALL']:
    P=[f(r,'dxy_chg5d') for r in mpanel if y=='ALL' or r['date'][:4]==y]; P=[x for x in P if x is not None]
    B=[f(pby[d],'dxy_chg5d') for d in buy_dates if y=='ALL' or d[:4]==y]; B=[x for x in B if x is not None]
    print(f"  {y}: panel fracUP {sum(1 for x in P if x>0)/len(P)*100:5.1f}% (n={len(P)})  buy {sum(1 for x in B if x>0)/len(B)*100:5.1f}% (n={len(B)})  lift {(sum(1 for x in B if x>0)/len(B))/(sum(1 for x in P if x>0)/len(P)):.2f}")
print('\n=== hypothesis count check: distinct macro columns examined ===')
cols=['ust_y2','ust_y5','ust_y10','ust_y30','ust_m3','ust_y1','ust_y20','curve_2s10s','curve_2s30s','ust_y2_chg5d','ust_y10_chg5d','ust_y30_chg5d','dxy','dxy_chg5d','tlt','tlt_chg5d','hyg','hyg_chg5d','gold','gold_chg5d','wti','wti_chg5d']
print(' ',len(cols),'macro columns; tested at buy and sell, level+sign+magnitude+tail, x5 year slices')
