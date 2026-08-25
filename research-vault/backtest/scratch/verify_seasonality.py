import csv, statistics as st, math
from collections import defaultdict

OF="/home/user/INMA-/research-vault/backtest/out/oracle_features.csv"
DP="/home/user/INMA-/research-vault/backtest/out/daily_panel.csv"

rows=list(csv.DictReader(open(OF)))
print("trades:",len(rows))

# sym-month level
sm={}
for r in rows:
    k=(r['sym'],r['month'])
    sm.setdefault(k,[]).append(r)
print("sym-months:",len(sm))
print("trades per sym-month distribution:", sorted({len(v) for v in sm.values()}))

# check month_total_pct constant within sym-month
bad=0
for k,v in sm.items():
    if len({round(float(x['month_total_pct']),6) for x in v})>1: bad+=1
print("sym-months with non-constant month_total_pct:",bad)

# check month_total_pct == sum of leg returns
diffs=[]
for k,v in sm.items():
    s=sum(float(x['ret_pct']) for x in v)
    diffs.append(abs(s-float(v[0]['month_total_pct'])))
print("max |sum(ret_pct)-month_total_pct|:",max(diffs))

mt={k:float(v[0]['month_total_pct']) for k,v in sm.items()}
vals=list(mt.values())
print("month_total_pct: n=%d mean=%.3f sd=%.3f min=%.2f max=%.2f"%(len(vals),st.mean(vals),st.stdev(vals),min(vals),max(vals)))

# by calendar month
bym=defaultdict(list)
byy=defaultdict(list)
for (sym,m),v in mt.items():
    y,mo=m.split('-')
    bym[int(mo)].append(v); byy[int(y)].append(v)
print("\n-- by calendar month --")
gm=st.mean(vals)
for mo in range(1,13):
    a=bym[mo]
    print("m%02d n=%d mean=%6.3f sd=%5.2f"%(mo,len(a),st.mean(a),st.stdev(a) if len(a)>1 else float('nan')))
mm=[st.mean(bym[mo]) for mo in range(1,13)]
print("sd across 12 month-means: %.3f  spread %.2f-%.2f"%(st.stdev(mm),min(mm),max(mm)))
print("\n-- by year --")
for y in sorted(byy):
    a=byy[y]; print(y,"n=%d mean=%.3f sd=%.2f"%(len(a),st.mean(a),st.stdev(a)))

# one-way ANOVA F for month-of-year
def anova(groups):
    groups=[g for g in groups if len(g)>0]
    N=sum(len(g) for g in groups); k=len(groups)
    gmean=sum(sum(g) for g in groups)/N
    ssb=sum(len(g)*(st.mean(g)-gmean)**2 for g in groups)
    ssw=sum(sum((x-st.mean(g))**2 for x in g) for g in groups)
    return ssb/(k-1)/(ssw/(N-k)), ssb/(ssb+ssw), k, N
F,eta,k,N=anova([bym[m] for m in range(1,13)])
print("\nmonth-of-year ANOVA F=%.3f df=(%d,%d) eta2=%.3f"%(F,k-1,N-k,eta))
F,eta,k,N=anova([byy[y] for y in sorted(byy)])
print("year ANOVA F=%.3f df=(%d,%d) eta2=%.3f"%(F,k-1,N-k,eta))

# within-cell pooled sd
gs=[bym[m] for m in range(1,13)]
Nn=sum(len(g) for g in gs)
pooled=math.sqrt(sum(sum((x-st.mean(g))**2 for x in g) for g in gs)/(Nn-12))
print("pooled within-month sd: %.3f  se(n=8)=%.3f se(n=6)=%.3f"%(pooled,pooled/math.sqrt(8),pooled/math.sqrt(6)))

# quarter-end months
qe=[v for (s,m),v in mt.items() if int(m.split('-')[1]) in (3,6,9,12)]
oq=[v for (s,m),v in mt.items() if int(m.split('-')[1]) not in (3,6,9,12)]
print("\nquarter-end months n=%d mean=%.3f ; other n=%d mean=%.3f ; ratio=%.3f"%(len(qe),st.mean(qe),len(oq),st.mean(oq),st.mean(qe)/st.mean(oq)))
# also verify via is_quarter_end_month flag
qe2=[]; oq2=[]
for k,v in sm.items():
    f=int(float(v[0]['B_is_quarter_end_month']))
    (qe2 if f else oq2).append(mt[k])
print("via B_is_quarter_end_month: qe n=%d mean=%.3f ; other n=%d mean=%.3f"%(len(qe2),st.mean(qe2),len(oq2),st.mean(oq2)))
