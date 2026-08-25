exec(open('/home/user/INMA-/research-vault/backtest/scratch/setup.py').read())
buy_dates=sorted(set(t['buy_date'] for t in trades)); sell_dates=sorted(set(t['sell_date'] for t in trades))
pby={r['date']:r for r in mpanel}
spx=[r for r in panel if r['sym']=='spx']; spx.sort(key=lambda r:r['date']); sby={r['date']:r for r in spx}
SHOCK=lambda d: (lambda x: None if x is None else abs(x)>=0.15)(f(pby[d],'ust_y10_chg5d')) if d in pby else None

print('=== DECONTAMINATION 1: rate-shock rate CONDITIONED on VIX 252d percentile tercile ===')
vals=sorted(x for x in (f(r,'vix_pctile_252d') for r in spx) if x is not None)
q1,q2=vals[len(vals)//3], vals[2*len(vals)//3]
print(f"  vix_pctile terciles at {q1:.3f} / {q2:.3f}")
def vb(d):
    r=sby.get(d);  x=f(r,'vix_pctile_252d') if r else None
    if x is None: return None
    return 'lo' if x<q1 else ('mid' if x<q2 else 'hi')
print(f"{'vixterc':<8}{'panelN':>7}{'panel%':>8}{'buyN':>6}{'buy%':>8}{'lift':>7}")
for b in ['lo','mid','hi']:
    P=[r['date'] for r in spx if vb(r['date'])==b]; B=[d for d in buy_dates if vb(d)==b]
    def fr(ds):
        v=[SHOCK(d) for d in ds]; v=[x for x in v if x is not None]
        return len(v), sum(v)/len(v)*100 if v else float('nan')
    pn,pp=fr(P); bn,bp=fr(B)
    print(f"{b:<8}{pn:>7}{pp:>8.1f}{bn:>6}{bp:>8.1f}{(bp/pp if pp else 0):>7.2f}")

print('\n=== DECONTAMINATION 2: conditioned on SPX realvol20 tercile ===')
vals=sorted(x for x in (f(r,'realvol20_ann_pct') for r in spx) if x is not None)
r1,r2=vals[len(vals)//3], vals[2*len(vals)//3]
print(f"  realvol20 terciles at {r1:.2f} / {r2:.2f}")
def rb(d):
    r=sby.get(d); x=f(r,'realvol20_ann_pct') if r else None
    if x is None: return None
    return 'lo' if x<r1 else ('mid' if x<r2 else 'hi')
for b in ['lo','mid','hi']:
    P=[r['date'] for r in spx if rb(r['date'])==b]; B=[d for d in buy_dates if rb(d)==b]
    def fr(ds):
        v=[SHOCK(d) for d in ds]; v=[x for x in v if x is not None]
        return len(v), sum(v)/len(v)*100 if v else float('nan')
    pn,pp=fr(P); bn,bp=fr(B)
    print(f"{b:<8}{pn:>7}{pp:>8.1f}{bn:>6}{bp:>8.1f}{(bp/pp if pp else 0):>7.2f}")

print('\n=== DECONTAMINATION 3: conditioned on SPX 5d return bucket ===')
def eb(d):
    r=sby.get(d); x=f(r,'ret_5d_pct') if r else None
    if x is None: return None
    return 'lt-2' if x<-2 else ('-2..0' if x<0 else ('0..2' if x<2 else 'gt2'))
for b in ['lt-2','-2..0','0..2','gt2']:
    P=[r['date'] for r in spx if eb(r['date'])==b]; B=[d for d in buy_dates if eb(d)==b]
    def fr(ds):
        v=[SHOCK(d) for d in ds]; v=[x for x in v if x is not None]
        return len(v), sum(v)/len(v)*100 if v else float('nan')
    pn,pp=fr(P); bn,bp=fr(B)
    print(f"{b:<8}{pn:>7}{pp:>8.1f}{bn:>6}{bp:>8.1f}{(bp/pp if pp else 0):>7.2f}")

print('\n=== SELL side: rate-shock rate at sells vs base ===')
for y in ['2023','2024','2025','2026','ALL']:
    P=[r['date'] for r in spx if y=='ALL' or r['date'][:4]==y]
    S=[d for d in sell_dates if y=='ALL' or d[:4]==y]
    def fr(ds):
        v=[SHOCK(d) for d in ds]; v=[x for x in v if x is not None]
        return len(v), sum(v)/len(v)*100 if v else float('nan')
    pn,pp=fr(P); sn,sp=fr(S)
    print(f"  {y}: panel {pp:5.1f}% (n={pn})  sell {sp:5.1f}% (n={sn}) lift {sp/pp if pp else 0:.2f}")

print('\n=== Alternative thresholds for |10Y 5d chg| (sensitivity, ALL years) ===')
for thr in [0.05,0.10,0.15,0.20,0.25,0.30]:
    P=[f(r,'ust_y10_chg5d') for r in mpanel]; P=[x for x in P if x is not None]
    B=[f(pby[d],'ust_y10_chg5d') for d in buy_dates]; B=[x for x in B if x is not None]
    pp=sum(1 for x in P if abs(x)>=thr)/len(P)*100; bp_=sum(1 for x in B if abs(x)>=thr)/len(B)*100
    print(f"  >={thr*100:.0f}bp: panel {pp:5.1f}% buy {bp_:5.1f}% lift {bp_/pp:.2f}  (buy n={len(B)})")
print('\n=== same for 2y and 30y (|5d chg|>=15bp) ===')
for c in ['ust_y2_chg5d','ust_y30_chg5d']:
    P=[f(r,c) for r in mpanel]; P=[x for x in P if x is not None]
    B=[f(pby[d],c) for d in buy_dates]; B=[x for x in B if x is not None]
    pp=sum(1 for x in P if abs(x)>=0.15)/len(P)*100; bp_=sum(1 for x in B if abs(x)>=0.15)/len(B)*100
    print(f"  {c}: panel {pp:5.1f}% buy {bp_:5.1f}% lift {bp_/pp:.2f}")
