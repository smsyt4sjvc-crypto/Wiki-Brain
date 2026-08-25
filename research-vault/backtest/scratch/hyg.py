exec(open('/home/user/INMA-/research-vault/backtest/scratch/setup.py').read())
buy_dates=sorted(set(t['buy_date'] for t in trades))
sell_dates=sorted(set(t['sell_date'] for t in trades))
pby={r['date']:r for r in mpanel}
BD=set(buy_dates)
# ---- 1. CONDITIONAL on equity 5d return sign (use spx panel rows for equity ret; macro same) ----
spx=[r for r in panel if r['sym']=='spx']; spx.sort(key=lambda r:r['date'])
sby={r['date']:r for r in spx}
def bucket(d):
    r=sby.get(d)
    if not r: return None
    x=f(r,'ret_5d_pct')
    if x is None: return None
    if x < -2: return 'lt-2'
    if x < 0: return '-2..0'
    if x < 2: return '0..2'
    return 'gt2'
print('=== HYG down-5d rate, CONDITIONED on SPX 5d return bucket (removes equity co-move) ===')
print(f"{'bucket':<8}{'panelN':>7}{'panel%':>8}{'buyN':>6}{'buy%':>8}{'lift':>7}")
for b in ['lt-2','-2..0','0..2','gt2']:
    P=[r for r in spx if bucket(r['date'])==b]
    B=[sby[d] for d in buy_dates if bucket(d)==b]
    def fr(rows):
        v=[f(pby[r['date']],'hyg_chg5d') for r in rows]; v=[x for x in v if x is not None]
        return len(v), (sum(1 for x in v if x<0)/len(v)*100 if v else float('nan'))
    pn,pp=fr(P); bn,bp=fr(B)
    print(f"{b:<8}{pn:>7}{pp:>8.1f}{bn:>6}{bp:>8.1f}{(bp/pp if pp else 0):>7.2f}")

# ---- 2. RESIDUAL: hyg_chg5d in %, minus its OLS fit on spx ret_5d ----
X=[];Y=[];DT=[]
for r in spx:
    p=pby[r['date']]; h=f(p,'hyg_chg5d'); hl=f(p,'hyg'); e=f(r,'ret_5d_pct')
    if None in (h,hl,e) or hl==0: continue
    X.append(e); Y.append(h/(hl-h)*100.0); DT.append(r['date'])
mx=sum(X)/len(X); my=sum(Y)/len(Y)
beta=sum((a-mx)*(b-my) for a,b in zip(X,Y))/sum((a-mx)**2 for a in X)
alpha=my-beta*mx
res={d:y-(alpha+beta*x) for d,x,y in zip(DT,X,Y)}
print(f"\n=== HYG 5d %chg regressed on SPX 5d %ret: beta={beta:.3f} alpha={alpha:.4f} n={len(X)} ===")
allr=sorted(res.values()); import statistics as S
def q(v,p):
    v=sorted(v); return v[int(p*(len(v)-1))]
pr=[res[d] for d in DT]
br=[res[d] for d in buy_dates if d in res]
sr=[res[d] for d in sell_dates if d in res]
print(f"residual median  panel={S.median(pr):+.4f} (n={len(pr)})  buy={S.median(br):+.4f} (n={len(br)})  sell={S.median(sr):+.4f} (n={len(sr)})")
thr=q(pr,0.25)
print(f"panel 25th pct residual = {thr:+.4f}")
for name,v in [('panel',pr),('buy',br),('sell',sr)]:
    print(f"  frac residual<0: {name} {sum(1 for x in v if x<0)/len(v)*100:.1f}%   frac < panel-p25: {sum(1 for x in v if x<thr)/len(v)*100:.1f}%")
# by year residual
print('\nresidual frac<0 by year:')
for y in ['2023','2024','2025','2026']:
    P=[res[d] for d in DT if d[:4]==y]; B=[res[d] for d in buy_dates if d in res and d[:4]==y]
    print(f"  {y} panel {sum(1 for x in P if x<0)/len(P)*100:5.1f}% (n={len(P)})   buy {sum(1 for x in B if x<0)/len(B)*100:5.1f}% (n={len(B)})")
