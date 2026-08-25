import csv, statistics as st, random
from collections import defaultdict
O='/home/user/INMA-/research-vault/backtest/out/oracle_features.csv'
D='/home/user/INMA-/research-vault/backtest/out/daily_panel.csv'
tr=list(csv.DictReader(open(O))); pan=list(csv.DictReader(open(D)))
def f(x): return float(x)
S=defaultdict(list)
for p in pan: S[p['sym']].append(p)
for k in S: S[k].sort(key=lambda r:r['date'])
oh=defaultdict(list)
for t in tr: oh[int(f(t['hold_days']))].append(f(t['ret_pct']))

def windows(h):
    """all same-month h-windows grouped by (sym,month)"""
    g=defaultdict(list)
    for k,rows in S.items():
        for i in range(len(rows)-h):
            a,b=rows[i],rows[i+h]
            if a['date'][:7]!=b['date'][:7]: continue
            g[(k,a['date'][:7])].append(100*(f(b['high'])-f(a['low']))/f(a['low']))
    return g

print(" h | n_or | oracle | mean_win | lift_vs_MEAN | monthly_MAX | lift_vs_MAX | MAX/MEAN")
rows=[]
for h in sorted(oh):
    g=windows(h)
    allw=[x for v in g.values() for x in v]
    if not allw: continue
    mx=[max(v) for v in g.values() if v]
    om=st.mean(oh[h]); mn=st.mean(allw); mm=st.mean(mx)
    rows.append((h,len(oh[h]),om,mn,om/mn,mm,om/mm,mm/mn))
    print("%3d| %4d | %6.3f | %8.3f | %12.2f | %11.3f | %11.2f | %7.2f"%(h,len(oh[h]),om,mn,om/mn,mm,om/mm,mm/mn))

# trend tests on lift-vs-mean, weighted by n
import math
def wcorr(xs,ys,ws):
    sw=sum(ws); mx=sum(w*x for w,x in zip(ws,xs))/sw; my=sum(w*y for w,y in zip(ws,ys))/sw
    cov=sum(w*(x-mx)*(y-my) for w,x,y in zip(ws,xs,ys))/sw
    vx=sum(w*(x-mx)**2 for w,x in zip(ws,xs))/sw; vy=sum(w*(y-my)**2 for w,y in zip(ws,ys))/sw
    return cov/math.sqrt(vx*vy)
h_=[r[0] for r in rows]; L=[r[4] for r in rows]; N=[r[1] for r in rows]; LM=[r[6] for r in rows]; MM=[r[7] for r in rows]
print("\nweighted corr(h, lift_vs_MEAN) = %.3f"%wcorr(h_,L,N))
print("weighted corr(h, lift_vs_MAX)  = %.3f"%wcorr(h_,LM,N))
print("weighted corr(h, MAX/MEAN ratio, unweighted) = %.3f"%wcorr(h_,MM,[1]*len(h_)))
print("MAX/MEAN ratio: mean %.2f  min %.2f  max %.2f"%(st.mean(MM),min(MM),max(MM)))
print("lift_vs_MEAN : mean %.2f  min %.2f  max %.2f  sd %.2f"%(st.mean(L),min(L),max(L),st.pstdev(L)))
print("lift_vs_MAX  : mean %.2f  min %.2f  max %.2f"%(st.mean(LM),min(LM),max(LM)))

# bootstrap CI on lift for the h values THEY quoted
random.seed(0)
print("\nbootstrap 90%% CI on lift_vs_MEAN for quoted h:")
for h in [0,1,2,3,5,7,10,14]:
    if h not in oh: continue
    g=windows(h); mn=st.mean([x for v in g.values() for x in v])
    d=oh[h]; bs=sorted(st.mean(random.choices(d,k=len(d)))/mn for _ in range(4000))
    print("  h=%2d n=%2d lift=%.2f  CI[%.2f, %.2f]"%(h,len(d),st.mean(d)/mn,bs[200],bs[3800]))
