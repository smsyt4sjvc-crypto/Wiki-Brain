import csv, statistics as st, math, random
from collections import defaultdict
P="/home/user/INMA-/research-vault/backtest/out/daily_panel.csv"; F="/home/user/INMA-/research-vault/backtest/out/oracle_features.csv"
panel=list(csv.DictReader(open(P))); trades=list(csv.DictReader(open(F)))
cells=defaultdict(list)
for r in panel: cells[(r['sym'],r['date'][:7])].append(r)
for k in cells: cells[k].sort(key=lambda r:r['date'])
M={}
for k,rows in cells.items():
    M[k]=dict(path=sum(abs(float(r['ret_1d_pct'])) for r in rows),
              rng=(max(float(r['high']) for r in rows)-min(float(r['low']) for r in rows))/min(float(r['low']) for r in rows)*100,
              bh=(float(rows[-1]['close'])/float(rows[0]['close'])-1)*100,
              intraday=sum((float(r['high'])-float(r['low']))/float(r['low'])*100 for r in rows),
              nd=len(rows))
oc=defaultdict(float)
for t in trades: oc[(t['sym'],t['month'])]+=float(t['ret_pct'])
keys=sorted(oc)
O=[oc[k] for k in keys]; PA=[M[k]['path'] for k in keys]; RG=[M[k]['rng'] for k in keys]
BH=[M[k]['bh'] for k in keys]; ID=[M[k]['intraday'] for k in keys]
CH=[PA[i]/RG[i] for i in range(88)]
def corr(a,b):
    n=len(a);ma=sum(a)/n;mb=sum(b)/n
    sa=math.sqrt(sum((x-ma)**2 for x in a));sb=math.sqrt(sum((x-mb)**2 for x in b))
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/(sa*sb)

print("--- what definition gives path mean 15.9? ---")
print("incl 1st day: %.3f | intra-month only: %.3f"%(sum(PA)/88, sum(sum(abs(float(r['ret_1d_pct'])) for r in cells[k][1:]) for k in keys)/88))
print("mean daily |ret_1d| over 1817 rows: %.4f  x mean days/cell %.2f = %.3f"%(
  sum(abs(float(r['ret_1d_pct'])) for r in panel)/1817, 1817/88, sum(abs(float(r['ret_1d_pct'])) for r in panel)/1817*1817/88))

print("\n--- 'lift over buy&hold' arithmetic ---")
print("their lift: 0.617 / (1.96/15.9=%.4f) = %.2fx"%(1.96/15.9, 0.617/(1.96/15.9)))
print("MY ratio-of-means bh/path = %.4f ; oracle ratio-of-means = %.4f -> consistent lift %.2fx"%(
  sum(BH)/sum(PA), sum(O)/sum(PA), (sum(O)/sum(PA))/(sum(BH)/sum(PA))))
pc=[BH[i]/PA[i] for i in range(88)]
print("MEAN-OF-RATIOS bh/path per cell = %.4f (median %.4f); n negative = %d"%(sum(pc)/88, st.median(pc), sum(1 for x in pc if x<0)))
print("  -> consistent mean-of-ratios lift = %.2fx  (they mixed mean-of-ratios numerator with ratio-of-means denominator)"%(0.6169/(sum(pc)/88)))

print("\n--- the claimed 1.0 ceiling ---")
rr=[O[i]/PA[i] for i in range(88)]
print("cells with oracle/path > 1.0: %d (max %.3f). A hard 1.0 ceiling does NOT exist:"%(sum(1 for x in rr if x>1),max(rr)))
print("  path is CLOSE-to-CLOSE; oracle fills at intraday LOW->HIGH, so it can exceed close-to-close path.")
print("true intraday capacity (sum daily (H-L)/L) mean %.2f%% vs path mean %.2f%%; oracle/intraday mean %.4f"%(
  sum(ID)/88, sum(PA)/88, sum(O[i]/ID[i] for i in range(88))/88))

print("\n--- OLS with t-stats: oracle ~ range + chop ---")
def ols(ys,Xs,names):
    k=len(Xs);nn=len(ys);p=k+1
    X=[[1.0]+[Xs[j][i] for j in range(k)] for i in range(nn)]
    XtX=[[sum(X[i][a]*X[i][b] for i in range(nn)) for b in range(p)] for a in range(p)]
    Xty=[sum(X[i][a]*ys[i] for i in range(nn)) for a in range(p)]
    A=[XtX[i][:]+[0.0]*p for i in range(p)]
    for i in range(p): A[i][p+i]=1.0
    for c in range(p):
        piv=max(range(c,p),key=lambda r:abs(A[r][c])); A[c],A[piv]=A[piv],A[c]
        d=A[c][c]; A[c]=[v/d for v in A[c]]
        for r2 in range(p):
            if r2!=c:
                f2=A[r2][c]; A[r2]=[A[r2][j]-f2*A[c][j] for j in range(2*p)]
    inv=[[A[i][p+j] for j in range(p)] for i in range(p)]
    beta=[sum(inv[i][j]*Xty[j] for j in range(p)) for i in range(p)]
    pred=[sum(beta[j]*X[i][j] for j in range(p)) for i in range(nn)]
    res=[ys[i]-pred[i] for i in range(nn)]
    s2=sum(r*r for r in res)/(nn-p)
    se=[math.sqrt(s2*inv[i][i]) for i in range(p)]
    for i,nm in enumerate(["const"]+names):
        print("   %-8s b=%8.4f se=%7.4f t=%6.2f"%(nm,beta[i],se[i],beta[i]/se[i]))
    my=sum(ys)/nn
    print("   R2=%.4f"%(1-sum(r*r for r in res)/sum((y-my)**2 for y in ys)))
ols(O,[RG,CH],["range","chop"])
print("\n   oracle ~ range + path")
ols(O,[RG,PA],["range","path"])

print("\n--- bootstrap: partial r(oracle,path|range) ---")
random.seed(11)
def resid_on(y,c):
    n=len(y); mc=sum(c)/n; my=sum(y)/n
    b=sum((c[i]-mc)*(y[i]-my) for i in range(n))/sum((c[i]-mc)**2 for i in range(n))
    a=my-b*mc; return [y[i]-(a+b*c[i]) for i in range(n)]
bs=[]
for _ in range(20000):
    s=[random.randrange(88) for _ in range(88)]
    o=[O[i] for i in s];p=[PA[i] for i in s];g=[RG[i] for i in s]
    try: bs.append(corr(resid_on(o,g),resid_on(p,g)))
    except: pass
bs.sort()
print("partial r(oracle,path|range): point %.4f  95%%CI [%.4f, %.4f]  P(<=0)=%.4f"%(
  corr(resid_on(O,RG),resid_on(PA,RG)), bs[int(.025*len(bs))], bs[int(.975*len(bs))], sum(1 for x in bs if x<=0)/len(bs)))

print("\n--- up/down separation: is path-eff really the sharpest? (Cohen's d) ---")
up=[i for i in range(88) if BH[i]>0]; dn=[i for i in range(88) if BH[i]<=0]
def d(v):
    a=[v[i] for i in up]; b=[v[i] for i in dn]
    sp=math.sqrt(((len(a)-1)*st.stdev(a)**2+(len(b)-1)*st.stdev(b)**2)/(len(a)+len(b)-2))
    return (sum(a)/len(a)-sum(b)/len(b))/sp, sum(a)/len(a), sum(b)/len(b)
for nm,v in [("oracle/path",[O[i]/PA[i] for i in range(88)]),
             ("oracle/range",[O[i]/RG[i] for i in range(88)]),
             ("oracle/intraday",[O[i]/ID[i] for i in range(88)]),
             ("oracle_total",O),("chop path/range",CH)]:
    dd,ma,mb=d(v); print("   %-16s d=%5.2f  up %.4f  dn %.4f"%(nm,dd,ma,mb))
