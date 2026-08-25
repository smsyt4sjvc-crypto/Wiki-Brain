import csv, collections, statistics as st
OUT='/home/user/INMA-/research-vault/backtest/out/'
tr=list(csv.DictReader(open(OUT+'oracle_features.csv')))
pn=list(csv.DictReader(open(OUT+'daily_panel.csv')))
F=lambda x: float(x)
bysym=collections.defaultdict(list)
for r in pn: bysym[r['sym']].append(r)
for k in bysym: bysym[k].sort(key=lambda r:r['date'])

def best2(L,H):
    T=len(L)
    A=[None]*T; mn=L[0]; mi=0; bv=H[0]/L[0]-1; ba=(0,0)
    for t in range(T):
        if L[t]<mn: mn=L[t]; mi=t
        v=H[t]/mn-1
        if v>bv: bv=v; ba=(mi,t)
        A[t]=(bv,ba)
    B=[None]*T; mx=H[T-1]; xi=T-1; cv=H[T-1]/L[T-1]-1; cb=(T-1,T-1)
    for t in range(T-1,-1,-1):
        if H[t]>mx: mx=H[t]; xi=t
        v=mx/L[t]-1
        if v>cv: cv=v; cb=(t,xi)
        B[t]=(cv,cb)
    best=(-9e9,None)
    for t in range(T):
        v=A[t][0]+B[t][0]
        if v>best[0]: best=(v,(A[t][1][0],A[t][1][1],B[t][1][0],B[t][1][1]))
    return best

legs=collections.defaultdict(dict)
for r in tr: legs[(r['sym'],r['month'])][r['leg']]=r
def month_bnds(rows):
    b=[]; cur=rows[0]['date'][:7]; s=0
    for i,r in enumerate(rows):
        if r['date'][:7]!=cur: b.append((s,i)); s=i; cur=r['date'][:7]
    b.append((s,len(rows))); return b

ok=0; tot=0; real=[]
for s in ('spx','ndx'):
    rows=bysym[s]
    for a,b in month_bnds(rows):
        w=rows[a:b]; v,idx=best2([F(r['low']) for r in w],[F(r['high']) for r in w])
        m=w[0]['date'][:7]; A,B2=legs[(s,m)]['1'],legs[(s,m)]['2']
        got=(w[idx[0]]['date'],w[idx[1]]['date'],w[idx[2]]['date'],w[idx[3]]['date'])
        exp=(A['buy_date'],A['sell_date'],B2['buy_date'],B2['sell_date'])
        ok+=got==exp; tot+=1; real.append((len(w),idx))
print(f"DP reproduces oracle {ok}/{tot}")

def stats(runs):
    n=len(runs)
    return (sum(i1<=1 for T,(i1,j1,i2,j2) in runs)/n,
            sum(j2>=T-2 for T,(i1,j1,i2,j2) in runs)/n,
            sum((i1<=1)+(i2<=1) for T,(i1,j1,i2,j2) in runs)/(2*n),
            sum((j1>=T-2)+(j2>=T-2) for T,(i1,j1,i2,j2) in runs)/(2*n), n)
r=stats(real); print(f"REAL: leg1buy_first2={r[0]:.3f} leg2sell_last2={r[1]:.3f} anybuy_first2={r[2]:.3f} anysell_last2={r[3]:.3f} n={r[4]}")

shift_res=[]
for k in list(range(1,22))+list(range(-21,0)):
    runs=[]
    for s in ('spx','ndx'):
        rows=bysym[s]
        for a,b in month_bnds(rows):
            a2,b2=a+k,b+k
            if a2<0 or b2>len(rows) or b2-a2<2: continue
            w=rows[a2:b2]
            v,idx=best2([F(x['low']) for x in w],[F(x['high']) for x in w]); runs.append((len(w),idx))
    st_=stats(runs); shift_res.append((k,)+st_)
    print(f"shift {k:+3d}: leg1buy_first2={st_[0]:.3f} leg2sell_last2={st_[1]:.3f} anybuy_first2={st_[2]:.3f} anysell_last2={st_[3]:.3f} n={st_[4]}")
import statistics
for i,lbl in ((1,'leg1buy_first2'),(2,'leg2sell_last2'),(3,'anybuy_first2'),(4,'anysell_last2')):
    v=[x[i] for x in shift_res]
    print(f"SHIFT NULL {lbl}: mean={statistics.mean(v):.3f} sd={statistics.pstdev(v):.3f} min={min(v):.3f} max={max(v):.3f}  REAL={r[i-1]:.3f}  z={(r[i-1]-statistics.mean(v))/statistics.pstdev(v):+.2f}  lift={r[i-1]/statistics.mean(v):.2f}")
