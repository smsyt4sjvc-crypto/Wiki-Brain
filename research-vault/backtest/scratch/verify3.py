import csv, statistics as st, math, random
from collections import defaultdict
P="/home/user/INMA-/research-vault/backtest/out/daily_panel.csv"
F="/home/user/INMA-/research-vault/backtest/out/oracle_features.csv"
panel=list(csv.DictReader(open(P))); trades=list(csv.DictReader(open(F)))
cells=defaultdict(list)
for r in panel: cells[(r['sym'],r['date'][:7])].append(r)
for k in cells: cells[k].sort(key=lambda r:r['date'])
M={}
for k,rows in cells.items():
    path=sum(abs(float(r['ret_1d_pct'])) for r in rows)
    hi=max(float(r['high']) for r in rows); lo=min(float(r['low']) for r in rows)
    M[k]=dict(path=path,rng=(hi-lo)/lo*100,bh=(float(rows[-1]['close'])/float(rows[0]['close'])-1)*100)
oc=defaultdict(float)
for t in trades: oc[(t['sym'],t['month'])]+=float(t['ret_pct'])
keys=sorted(oc)
O=[oc[k] for k in keys]; PA=[M[k]['path'] for k in keys]; RG=[M[k]['rng'] for k in keys]; BH=[M[k]['bh'] for k in keys]
def corr(a,b):
    n=len(a); ma=sum(a)/n; mb=sum(b)/n
    sa=math.sqrt(sum((x-ma)**2 for x in a)); sb=math.sqrt(sum((x-mb)**2 for x in b))
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/(sa*sb)

r13=corr(O,PA); r12=corr(O,RG); r23=corr(RG,PA); n=88
print("r(oracle,range)=%.4f r(oracle,path)=%.4f r(range,path)=%.4f"%(r12,r13,r23))

# --- STEIGER's test for dependent correlations sharing one variable ---
def z(r): return 0.5*math.log((1+r)/(1-r))
rm=(r12+r13)/2
f_=(1-r23)/(2*(1-rm**2)); f_=min(f_,1.0)
h=(1-f_*rm**2)/(1-rm**2)
Z=(z(r12)-z(r13))*math.sqrt((n-3)/(2*(1-r23)*h))
print("Steiger Z = %.3f  (|Z|>1.96 => difference distinguishable)"%Z)

# --- bootstrap the difference ---
random.seed(7); diffs=[]
idx=list(range(88))
for _ in range(20000):
    s=[random.choice(idx) for _ in range(88)]
    o=[O[i] for i in s]; p=[PA[i] for i in s]; g=[RG[i] for i in s]
    try: diffs.append(corr(o,g)-corr(o,p))
    except ZeroDivisionError: pass
diffs.sort()
print("bootstrap r(range)-r(path): mean %.4f  95%%CI [%.4f, %.4f]  P(<=0)=%.4f"%(
    sum(diffs)/len(diffs), diffs[int(.025*len(diffs))], diffs[int(.975*len(diffs))],
    sum(1 for d in diffs if d<=0)/len(diffs)))

# --- STABILITY: which normalizer is actually stable? ---
print("\n--- CV of oracle/X across 88 cells (lower = more stable conversion) ---")
for name,D in [("path",PA),("range",RG)]:
    rr=[O[i]/D[i] for i in range(88)]
    m=sum(rr)/88
    print("  oracle/%-6s mean %.4f median %.4f sd %.4f CV %.1f%% min %.3f max %.3f"%(
        name,m,st.median(rr),st.stdev(rr),100*st.stdev(rr)/m,min(rr),max(rr)))

# --- DIRECT test of 'not harvesting chop' ---
# choppiness = path/range (how many times the month retraces its own envelope)
CH=[PA[i]/RG[i] for i in range(88)]
print("\nchoppiness path/range: mean %.3f median %.3f min %.3f max %.3f"%(sum(CH)/88,st.median(CH),min(CH),max(CH)))
print("r(oracle, chop) = %.4f"%corr(O,CH))
# OLS of oracle on range + chop
def ols(ys,Xs):
    k=len(Xs); nn=len(ys)
    X=[[1.0]+[Xs[j][i] for j in range(k)] for i in range(nn)]
    p=k+1
    A=[[sum(X[i][a]*X[i][b] for i in range(nn)) for b in range(p)]+[sum(X[i][a]*ys[i] for i in range(nn))] for a in range(p)]
    for c in range(p):
        piv=max(range(c,p),key=lambda r:abs(A[r][c])); A[c],A[piv]=A[piv],A[c]
        d=A[c][c]
        A[c]=[v/d for v in A[c]]
        for r2 in range(p):
            if r2!=c:
                fct=A[r2][c]; A[r2]=[A[r2][j]-fct*A[c][j] for j in range(p+1)]
    beta=[A[i][p] for i in range(p)]
    pred=[sum(beta[j]*X[i][j] for j in range(p)) for i in range(nn)]
    my=sum(ys)/nn
    ss=sum((ys[i]-pred[i])**2 for i in range(nn)); tt=sum((y-my)**2 for y in ys)
    resid=[ys[i]-pred[i] for i in range(nn)]
    return beta,1-ss/tt,resid
b,r2,_=ols(O,[RG,CH]); print("OLS oracle ~ range + chop: b=%s  R2=%.4f"%([round(x,4) for x in b],r2))
b,r2,_=ols(O,[RG]);    print("OLS oracle ~ range      : b=%s  R2=%.4f"%([round(x,4) for x in b],r2))
b,r2,_=ols(O,[PA]);    print("OLS oracle ~ path       : b=%s  R2=%.4f"%([round(x,4) for x in b],r2))
b,r2,_=ols(O,[RG,PA]); print("OLS oracle ~ range+path : b=%s  R2=%.4f"%([round(x,4) for x in b],r2))

# partial corr of oracle w/ path controlling range, and vice versa
def partial(y,x,c):
    _,_,ry=ols(y,[c]); _,_,rx=ols(x,[c]); return corr(ry,rx)
print("partial r(oracle,path | range) = %.4f"%partial(O,PA,RG))
print("partial r(oracle,range | path) = %.4f"%partial(O,RG,PA))

# does |bh| explain it? oracle vs abs net move
ABH=[abs(x) for x in BH]
print("\nr(oracle,|bh|)=%.4f  r(range,|bh|)=%.4f  r(path,|bh|)=%.4f"%(corr(O,ABH),corr(RG,ABH),corr(PA,ABH)))
print("count oracle/path > 1.0:",sum(1 for i in range(88) if O[i]/PA[i]>1.0))
