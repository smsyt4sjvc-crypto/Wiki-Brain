exec(open('/home/user/INMA-/research-vault/backtest/scratch/setup.py').read())
buy_dates=sorted(set(t['buy_date'] for t in trades)); sell_dates=sorted(set(t['sell_date'] for t in trades))
pby={r['date']:r for r in mpanel}
spx=[r for r in panel if r['sym']=='spx']; spx.sort(key=lambda r:r['date']); sby={r['date']:r for r in spx}

print('=== A. equity/rate coupling by year: corr(spx ret_5d, ust_y10_chg5d) in PANEL ===')
def corr(a,b):
    n=len(a); ma=sum(a)/n; mb=sum(b)/n
    num=sum((x-ma)*(y-mb) for x,y in zip(a,b))
    den=(sum((x-ma)**2 for x in a)*sum((y-mb)**2 for y in b))**.5
    return num/den if den else float('nan')
for y in ['2023','2024','2025','2026','ALL']:
    A=[];Bv=[]
    for r in spx:
        if y!='ALL' and r['date'][:4]!=y: continue
        p=pby[r['date']]; e=f(r,'ret_5d_pct'); u=f(p,'ust_y10_chg5d')
        if None in (e,u): continue
        A.append(e);Bv.append(u)
    print(f"  {y}: corr={corr(A,Bv):+.3f}  n={len(A)}")

print('\n=== B. MAGNITUDE of yield impulse at buys vs base rate (bp, 5d chg) ===')
for c in ['ust_y2_chg5d','ust_y10_chg5d','ust_y30_chg5d']:
    P=[f(r,c) for r in mpanel]; P=[x for x in P if x is not None]
    B=[f(pby[d],c) for d in buy_dates if d in pby]; B=[x for x in B if x is not None]
    S=[f(pby[d],c) for d in sell_dates if d in pby]; S=[x for x in S if x is not None]
    ab=lambda v: sum(abs(x) for x in v)/len(v)
    print(f"  {c}: panel mean={sum(P)/len(P)*100:+5.1f}bp med={st.median(P)*100:+5.1f} |x|={ab(P)*100:4.1f} n={len(P)} | buy mean={sum(B)/len(B)*100:+5.1f} med={st.median(B)*100:+5.1f} |x|={ab(B)*100:4.1f} n={len(B)} | sell mean={sum(S)/len(S)*100:+5.1f} |x|={ab(S)*100:4.1f} n={len(S)}")

print('\n=== C. TAIL: |10Y 5d chg| >= 15bp (rate shock) at buys vs base, by year ===')
for y in ['2023','2024','2025','2026','ALL']:
    P=[f(pby[r['date']],'ust_y10_chg5d') for r in mpanel if y=='ALL' or r['date'][:4]==y]; P=[x for x in P if x is not None]
    B=[f(pby[d],'ust_y10_chg5d') for d in buy_dates if (y=='ALL' or d[:4]==y)]; B=[x for x in B if x is not None]
    pp=sum(1 for x in P if abs(x)>=0.15)/len(P)*100; bp_=sum(1 for x in B if abs(x)>=0.15)/len(B)*100 if B else float('nan')
    print(f"  {y}: panel {pp:5.1f}% (n={len(P)})  buy {bp_:5.1f}% (n={len(B)}) lift {bp_/pp if pp else 0:.2f}")

print('\n=== D. CURVE LEVEL by year: 2s10s at buys vs panel (level = calendar artifact check) ===')
for c in ['curve_2s10s','curve_2s30s','ust_y10','ust_y2']:
    print(' ',c)
    for y in ['2023','2024','2025','2026']:
        P=[f(r,c) for r in mpanel if r['date'][:4]==y]; P=[x for x in P if x is not None]
        B=[f(pby[d],c) for d in buy_dates if d[:4]==y]
        S=[f(pby[d],c) for d in sell_dates if d[:4]==y]
        print(f"    {y} panel med={st.median(P):+7.3f} (n={len(P)})  buy med={st.median(B):+7.3f} (n={len(B)})  sell med={st.median(S):+7.3f} (n={len(S)})  buy-panel={st.median(B)-st.median(P):+.3f}")

print('\n=== E. macro CHANGE across the oracle hold (sell minus buy), trade-level n=176 ===')
for c in ['ust_y2','ust_y10','ust_y30','curve_2s10s','dxy','tlt','hyg','gold','wti']:
    d=[]
    for t in trades:
        a=f(t,'B_'+c); b=f(t,'S_'+c)
        if None in (a,b): continue
        d.append(b-a)
    print(f"  {c}: median chg={st.median(d):+8.3f}  mean={sum(d)/len(d):+8.3f}  frac_down={sum(1 for x in d if x<0)/len(d)*100:5.1f}%  n={len(d)}")
