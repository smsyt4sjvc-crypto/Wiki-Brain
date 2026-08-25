import csv, collections, math, random
OUT='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(OUT+'daily_panel.csv')))
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
buyset=set((r['sym'],r['buy_date']) for r in tr)
base=len(buyset)/len(panel)
rows=[(float(r['rsi14']), 1 if (r['sym'],r['date']) in buyset else 0, r['sym'], r['date']) for r in panel]

def seg(lo,hi):
    s=[r for r in rows if lo<=r[0]<hi]
    k=sum(r[1] for r in s); n=len(s)
    se=math.sqrt(k/n*(1-k/n)/n) if n else 0
    return n,k,k/n,(k/n)/base, se/base

print("=== A. Is there a STEP at 40? ===")
for lo,hi in [(0,40),(40,50),(40,75),(50,75)]:
    n,k,p,l,se=seg(lo,hi); print(f"  RSI[{lo},{hi}): n={n:5d} buys={k:3d} p={100*p:5.2f}%  lift={l:.2f} +-{1.96*se:.2f}")

print("\n=== B. Trend WITHIN RSI<40 (if gradient, rate should rise as RSI falls) ===")
sub=[r for r in rows if r[0]<40]
sub.sort(key=lambda r:r[0])
q=len(sub)//4
for i in range(4):
    part=sub[i*q:(i+1)*q] if i<3 else sub[3*q:]
    k=sum(r[1] for r in part)
    print(f"  quartile {i+1} rsi[{part[0][0]:.1f},{part[-1][0]:.1f}] n={len(part)} buys={k} p={100*k/len(part):5.2f}% lift={(k/len(part))/base:.2f}")
# rank correlation rsi vs buy within <40
n=len(sub); xs=[r[0] for r in sub]; ys=[r[1] for r in sub]
mx=sum(xs)/n; my=sum(ys)/n
num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
den=math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
r_in=num/den
print(f"  point-biserial corr(RSI, buy) within RSI<40: {r_in:+.4f}  (n={n})")
# permutation p
cnt=0; obs=abs(r_in)
for _ in range(20000):
    random.shuffle(ys)
    my=sum(ys)/n
    nu=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    de=math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    if abs(nu/de)>=obs: cnt+=1
print(f"  permutation two-sided p for that within-<40 trend: {cnt/20000:.3f}")

print("\n=== C. Where is the biggest single adjacent-bin jump? ===")
edges=[0,25,30,35,40,45,50,60,70,75,101]
L=[]
for i in range(len(edges)-1):
    n,k,p,l,se=seg(edges[i],edges[i+1]); L.append((edges[i],edges[i+1],n,k,l,se))
for i in range(len(L)-1):
    a,b_=L[i],L[i+1]
    print(f"  {a[0]}-{a[1]} ({a[4]:.2f}) -> {b_[0]}-{b_[1]} ({b_[4]:.2f})   ratio={a[4]/b_[4] if b_[4] else float('inf'):.2f}x")

print("\n=== D. [30,35) vs [35,40) inversion: magnitude in pp and sigma ===")
n1,k1,p1,l1,_=seg(30,35); n2,k2,p2,l2,_=seg(35,40)
d=p2-p1; se=math.sqrt(p1*(1-p1)/n1+p2*(1-p2)/n2)
print(f"  p[30,35)={100*p1:.2f}%  p[35,40)={100*p2:.2f}%  diff={100*d:.2f} pp = {d/se:.2f} sigma   (lift diff = {l2-l1:.2f} lift-units)")

print("\n=== E. Effective independence: SPX/NDX overlap + serial clustering ===")
bydate=collections.defaultdict(set)
for s,dt in buyset: bydate[dt].add(s)
both=sum(1 for d,v in bydate.items() if len(v)==2)
print(f"  distinct buy DATES={len(bydate)}, dates where BOTH SPX and NDX bought={both} ({100*both/len(bydate):.0f}%)")
print(f"  so 167 buy-days -> {len(bydate)} independent calendar dates at best")
# runs of consecutive buy days
alld=sorted({r[3] for r in rows})
idx={d:i for i,d in enumerate(alld)}
runs=0; prev=-99
for s in ['SPX','NDX']:
    ds=sorted(idx[d] for (sy,d) in buyset if sy==s)
    prev=-99
    for i in ds:
        if i!=prev+1: runs+=1
        prev=i
print(f"  167 buy-days form {runs} contiguous runs -> effective independent buy events ~{runs}")

print("\n=== F. Overbought cliff: where exactly, and how thin? ===")
for lo,hi in [(70,73),(73,75),(75,78),(78,80),(80,101)]:
    n,k,p,l,se=seg(lo,hi); print(f"  RSI[{lo},{hi}): n={n:4d} buys={k:2d} p={100*p:5.2f}% lift={l:.2f}")
