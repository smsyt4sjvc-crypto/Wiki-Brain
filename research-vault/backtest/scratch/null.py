import csv, json, statistics as st, random, math
from collections import defaultdict
P='/home/user/INMA-/research-vault/backtest/out/'
rows=list(csv.DictReader(open(P+'daily_panel.csv')))
by=defaultdict(list)
for r in rows: by[(r['sym'], r['date'][:7])].append(r)
cells=sorted(by)

def b1(lo,hi):
    rl=lo[0]; b=-9e9
    for j in range(len(lo)):
        rl=min(rl,lo[j]); b=max(b,hi[j]/rl-1)
    return b*100
def b2(lo,hi):
    n=len(lo); f=[0]*n; rl=lo[0]; b=0.0
    for j in range(n):
        rl=min(rl,lo[j]); b=max(b,hi[j]/rl-1); f[j]=b
    g=[0]*n; rh=hi[-1]; b=0.0
    for i in range(n-1,-1,-1):
        rh=max(rh,hi[i]); b=max(b,rh/lo[i]-1); g[i]=b
    return max(f[j]+g[j] for j in range(n))*100

# --- 1. IS THE FLOOR MECHANICAL? best2 >= best1 + (same-bar range on best1's sell day)
floors=[]; margs=[]; allrange=[]
for k in cells:
    rs=sorted(by[k],key=lambda r:r['date'])
    lo=[float(r['low']) for r in rs]; hi=[float(r['high']) for r in rs]
    allrange += [(hi[i]/lo[i]-1)*100 for i in range(len(lo))]
    # find sell index of best single pair
    rl=lo[0]; best=-9e9; bj=0
    for j in range(len(lo)):
        rl=min(rl,lo[j])
        if hi[j]/rl-1>best: best=hi[j]/rl-1; bj=j
    floors.append((hi[bj]/lo[bj]-1)*100)
    margs.append(b2(lo,hi)-b1(lo,hi))
print('mean daily intraday high-low range: %.3f%% (median %.3f%%, n=%d bars)'%(st.mean(allrange),st.median(allrange),len(allrange)))
print('GUARANTEED floor on marginal (same-bar range of best1 sell day): mean %.3f min %.3f'%(st.mean(floors),min(floors)))
print('actual marginal: mean %.3f min %.3f'%(st.mean(margs),min(margs)))
print('cells where floor alone already >=1pp: %d/88'%sum(1 for f in floors if f>=1))
print('marginal/floor ratio median %.2f'%st.median([m/f for m,f in zip(margs,floors)]))

# --- 2. NULL A: shuffle bar ORDER within each cell (destroys all V-shape/path structure)
random.seed(7); NS=200
r_real=[]; 
for k in cells:
    rs=sorted(by[k],key=lambda r:r['date'])
    lo=[float(r['low']) for r in rs]; hi=[float(r['high']) for r in rs]
    r_real.append((b1(lo,hi), b2(lo,hi)))
real_ratio=st.mean([x[1] for x in r_real])/st.mean([x[0] for x in r_real])
sh=[]
for s in range(NS):
    a=[];b=[]
    for k in cells:
        rs=sorted(by[k],key=lambda r:r['date'])
        idx=list(range(len(rs))); random.shuffle(idx)
        lo=[float(rs[i]['low']) for i in idx]; hi=[float(rs[i]['high']) for i in idx]
        a.append(b1(lo,hi)); b.append(b2(lo,hi))
    sh.append((st.mean(a),st.mean(b),st.mean([y-x for x,y in zip(a,b)]),min(y-x for x,y in zip(a,b))))
print('\nNULL A shuffled-bar-order (200 reps, all 88 cells each):')
print('  best1 mean %.3f | best2 mean %.3f | marginal mean %.3f | uplift ratio %.3f'%(
  st.mean([x[0] for x in sh]), st.mean([x[1] for x in sh]), st.mean([x[2] for x in sh]),
  st.mean([x[1] for x in sh])/st.mean([x[0] for x in sh])))
print('  reps where min marginal across 88 cells <1pp: %d/200'%sum(1 for x in sh if x[3]<1))
print('  REAL uplift ratio %.3f'%real_ratio)

# --- 3. NULL B: GBM random walk, zero drift, vol matched per cell, synthetic OHLC via 24 intraday steps
def sim_cell(nd, sig_d, rng):
    lo=[];hi=[]; px=100.0
    for d in range(nd):
        p=px; mn=p; mx=p
        for s in range(24):
            p*=math.exp(rng.gauss(0,sig_d/math.sqrt(24)))
            mn=min(mn,p); mx=max(mx,p)
        lo.append(mn); hi.append(mx); px=p
    return lo,hi
rng=random.Random(11)
# per-cell daily log-ret sd from closes
res=[]
for s in range(200):
    a=[];b=[]
    for k in cells:
        rs=sorted(by[k],key=lambda r:r['date'])
        c=[float(r['close']) for r in rs]
        lr=[math.log(c[i+1]/c[i]) for i in range(len(c)-1)]
        sd=st.pstdev(lr) if len(lr)>1 else 0.01
        lo,hi=sim_cell(len(rs), sd, rng)
        a.append(b1(lo,hi)); b.append(b2(lo,hi))
    res.append((st.mean(a),st.mean(b),min(y-x for x,y in zip(a,b))))
print('\nNULL B zero-drift GBM, vol matched per cell (200 reps):')
print('  best1 mean %.3f | best2 mean %.3f | uplift ratio %.3f | reps with any cell <1pp: %d/200'%(
  st.mean([x[0] for x in res]), st.mean([x[1] for x in res]),
  st.mean([x[1] for x in res])/st.mean([x[0] for x in res]), sum(1 for x in res if x[2]<1)))

# --- 4. buy&hold definition check
c_all=defaultdict(list)
for r in rows: c_all[r['sym']].append((r['date'],float(r['close'])))
bh2=[]
for sym in c_all:
    ser=sorted(c_all[sym]); 
    idx={}
    for i,(d,c) in enumerate(ser): idx.setdefault(d[:7],[]).append(i)
    for m in sorted(idx):
        i0=idx[m][0]; i1=idx[m][-1]
        base=ser[i0-1][1] if i0>0 else ser[i0][1]
        bh2.append((ser[i1][1]/base-1)*100)
print('\nbuy&hold prev-month-close base: mean %.4f (n=%d)  [agent claimed 1.96]'%(st.mean(bh2),len(bh2)))

print('\n--- ratio distribution under GBM null ---')
rats=sorted([x[1]/x[0] for x in res])
print('GBM uplift ratio: p05 %.3f p25 %.3f median %.3f p75 %.3f p95 %.3f'%(
 rats[9],rats[49],rats[99],rats[149],rats[189]))
print('REAL 1.471 -> percentile of GBM null: %.0f%%'%(100*sum(1 for r in rats if r<1.4709)/len(rats)))
# calibrate synthetic intraday range vs real
rng2=random.Random(99); rr=[]
for k in cells:
    rs=sorted(by[k],key=lambda r:r['date'])
    c=[float(r['close']) for r in rs]
    lr=[math.log(c[i+1]/c[i]) for i in range(len(c)-1)]
    sd=st.pstdev(lr)
    lo,hi=sim_cell(len(rs), sd, rng2)
    rr += [(hi[i]/lo[i]-1)*100 for i in range(len(lo))]
print('synthetic mean daily range %.3f%% vs real %.3f%% (synthetic UNDER-states range -> null is conservative)'%(st.mean(rr),1.216))
