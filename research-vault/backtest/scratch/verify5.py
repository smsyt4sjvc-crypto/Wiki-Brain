import csv, statistics as st, math, random
from collections import defaultdict
P="/home/user/INMA-/research-vault/backtest/out/daily_panel.csv"; F="/home/user/INMA-/research-vault/backtest/out/oracle_features.csv"
panel=list(csv.DictReader(open(P))); trades=list(csv.DictReader(open(F)))
cells=defaultdict(list)
for r in panel: cells[(r['sym'],r['date'][:7])].append(r)
for k in cells: cells[k].sort(key=lambda r:r['date'])
keys=sorted(cells)
def corr(a,b):
    n=len(a);ma=sum(a)/n;mb=sum(b)/n
    sa=math.sqrt(sum((x-ma)**2 for x in a));sb=math.sqrt(sum((x-mb)**2 for x in b))
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/(sa*sb)
def two_leg(p):
    n=len(p)
    left=[0.0]*n; mn=p[0]; best=0.0
    for i in range(n):
        mn=min(mn,p[i]); best=max(best,p[i]/mn-1); left[i]=best
    right=[0.0]*n; mx=p[-1]; best=0.0
    for i in range(n-1,-1,-1):
        mx=max(mx,p[i]); best=max(best,mx/p[i]-1); right[i]=best
    return max(left[i]+right[i] for i in range(n))*100

oc=defaultdict(float)
for t in trades: oc[(t['sym'],t['month'])]+=float(t['ret_pct'])

# ---- REAL, close-only replication (same machinery the null will use) ----
realO=[];realP=[];realR=[];trueO=[]
for k in keys:
    rets=[float(r['ret_1d_pct']) for r in cells[k]]
    p=[100.0]
    for x in rets[1:]: p.append(p[-1]*(1+x/100))
    realO.append(two_leg(p)); realP.append(sum(abs(x) for x in rets))
    realR.append((max(p)-min(p))/min(p)*100); trueO.append(oc[k])
print("close-only 2-leg oracle vs the real intraday oracle: r=%.4f  means %.2f vs %.2f"%(
    corr(realO,trueO), sum(realO)/88, sum(trueO)/88))
print("REAL(close-only): r(oracle,range)=%.4f  r(oracle,path)=%.4f  gap=%+.4f"%(
    corr(realO,realR), corr(realO,realP), corr(realO,realR)-corr(realO,realP)))

# ---- NULL: shuffle daily returns WITHIN each month. path is EXACTLY invariant. ----
random.seed(3); gaps=[];rr=[];rp=[];effs=[];cvs=[];ups=[];dns=[]
for trial in range(400):
    O=[];PA=[];RG=[];BH=[]
    for k in keys:
        rets=[float(r['ret_1d_pct']) for r in cells[k]]
        s=rets[1:][:]; random.shuffle(s); s=[rets[0]]+s
        p=[100.0]
        for x in s[1:]: p.append(p[-1]*(1+x/100))
        O.append(two_leg(p)); PA.append(sum(abs(x) for x in s))
        RG.append((max(p)-min(p))/min(p)*100); BH.append((p[-1]/p[0]-1)*100)
    a=corr(O,RG); b=corr(O,PA); rr.append(a); rp.append(b); gaps.append(a-b)
    e=[O[i]/PA[i] for i in range(88)]; effs.append(sum(e)/88); cvs.append(st.stdev(e)/(sum(e)/88))
    u=[e[i] for i in range(88) if BH[i]>0]; d=[e[i] for i in range(88) if BH[i]<=0]
    if u and d: ups.append(sum(u)/len(u)); dns.append(sum(d)/len(d))
gaps.sort()
print("\n=== NULL (within-month return shuffle; NO market path structure survives) ===")
print("  r(oracle,range) mean %.4f | r(oracle,path) mean %.4f"%(sum(rr)/len(rr),sum(rp)/len(rp)))
print("  GAP r_range - r_path: mean %+.4f  [5th %.4f, 95th %.4f]  frac of trials with gap>0: %.3f"%(
  sum(gaps)/len(gaps), gaps[int(.05*len(gaps))], gaps[int(.95*len(gaps))], sum(1 for g in gaps if g>0)/len(gaps)))
print("  observed real gap (close-only) %+.4f -> percentile in null: %.1f%%"%(
  corr(realO,realR)-corr(realO,realP),
  100*sum(1 for g in gaps if g < corr(realO,realR)-corr(realO,realP))/len(gaps)))
print("\n  NULL path-efficiency oracle/path: mean %.4f (real 0.617), CV %.1f%% (real 28.6%%)"%(
  sum(effs)/len(effs), 100*sum(cvs)/len(cvs)))
print("  NULL up-month eff %.4f vs down-month eff %.4f  (real 0.709 vs 0.448)"%(
  sum(ups)/len(ups), sum(dns)/len(dns)))

# does 'not harvesting chop' hold holding PATH fixed? (their actual phrasing)
CH=[realP[i] and 0 for i in range(0)]
import itertools
O=[oc[k] for k in keys]
PAr=[sum(abs(float(r['ret_1d_pct'])) for r in cells[k]) for k in keys]
RGr=[(max(float(r['high']) for r in cells[k])-min(float(r['low']) for r in cells[k]))/min(float(r['low']) for r in cells[k])*100 for k in keys]
CH=[PAr[i]/RGr[i] for i in range(88)]
def ols(ys,Xs,names):
    k=len(Xs);nn=len(ys);p=k+1
    X=[[1.0]+[Xs[j][i] for j in range(k)] for i in range(nn)]
    XtX=[[sum(X[i][a]*X[i][b] for i in range(nn)) for b in range(p)] for a in range(p)]
    Xty=[sum(X[i][a]*ys[i] for i in range(nn)) for a in range(p)]
    A=[XtX[i][:]+[1.0 if j==i else 0.0 for j in range(p)] for i in range(p)]
    for c in range(p):
        piv=max(range(c,p),key=lambda r:abs(A[r][c])); A[c],A[piv]=A[piv],A[c]
        d=A[c][c]; A[c]=[v/d for v in A[c]]
        for r2 in range(p):
            if r2!=c:
                f2=A[r2][c]; A[r2]=[A[r2][j]-f2*A[c][j] for j in range(2*p)]
    inv=[[A[i][p+j] for j in range(p)] for i in range(p)]
    beta=[sum(inv[i][j]*Xty[j] for j in range(p)) for i in range(p)]
    pred=[sum(beta[j]*X[i][j] for j in range(p)) for i in range(nn)]
    res=[ys[i]-pred[i] for i in range(nn)]; s2=sum(r*r for r in res)/(nn-p)
    for i,nm in enumerate(["const"]+names):
        print("   %-7s b=%8.4f t=%6.2f"%(nm,beta[i],beta[i]/math.sqrt(s2*inv[i][i])))
print("\n=== conditioning matters: the claim flips sign depending on what you hold fixed ===")
print(" oracle ~ path + chop   (their phrasing: same total path, more oscillation)")
ols(O,[PAr,CH],["path","chop"])
print(" oracle ~ range + chop  (same envelope, more oscillation)")
ols(O,[RGr,CH],["range","chop"])
