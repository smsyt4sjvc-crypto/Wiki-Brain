import csv, statistics as st
from collections import defaultdict
B='/home/user/INMA-/research-vault/backtest/out/'
panel=list(csv.DictReader(open(B+'daily_panel.csv')))
tr=list(csv.DictReader(open(B+'oracle_features.csv')))
def f(x):
    try: return float(x)
    except: return None
# ---- variance decomposition: within sym-month vs total
bym=defaultdict(list)
for r in panel: bym[(r['sym'],r['date'][:7])].append(r)
FE=['dist_sma20_pct','dist_sma50_pct','dist_sma200_pct','dd_from_20d_high_pct','dd_from_63d_high_pct','dd_from_252d_high_pct','rsi14','up_from_20d_low_pct']
print("=== VARIANCE DECOMPOSITION (why the horizon gradient exists) ===")
print(f"{'feat':26s} {'sd_total':>9s} {'sd_within_month':>16s} {'within share of var':>20s}")
for c in FE:
    allv=[f(r[c]) for r in panel if f(r[c]) is not None]
    tot=st.pvariance(allv)
    wsum=0; n=0
    for k,days in bym.items():
        v=[f(d[c]) for d in days if f(d[c]) is not None]
        if len(v)>1: wsum+=st.pvariance(v)*len(v); n+=len(v)
    within=wsum/n
    print(f"{c:26s} {tot**.5:9.2f} {within**.5:16.2f} {within/tot*100:19.1f}%")

# ---- regime buckets on 88 sym-months
print("\n=== 88 SYM-MONTHS BUCKETED BY REGIME ===")
mrows=[]
for k,days in bym.items():
    dd252=[f(d['dd_from_252d_high_pct']) for d in days]
    s200=[f(d['dist_sma200_pct']) for d in days]
    mrows.append({'k':k,'min_dd252':min(dd252),'med_s200':st.median(s200),'min_s200':min(s200),'n':len(days)})
mm={r['k']:r for r in mrows}
def bucket_report(name, keyfn, order):
    g=defaultdict(list)
    for t in tr: g[keyfn(mm[(t['sym'],t['month'])])].append(t)
    print(f"\n-- {name} --")
    print(f"{'bucket':22s} {'nMo':>4s} {'nTr':>4s} {'medRet%':>8s} {'sumMoRet%':>10s} {'medB_dd252':>11s} {'medB_s200':>10s} {'medB_dd20':>10s} {'medB_rsi':>9s} {'medHold':>8s} {'%buyBelow200':>13s}")
    for b in order:
        ts=g.get(b,[])
        if not ts: continue
        nmo=len(set((t['sym'],t['month']) for t in ts))
        mo=set((t['sym'],t['month']) for t in ts)
        motot=[f(t['month_total_pct']) for t in ts]
        print(f"{b:22s} {nmo:4d} {len(ts):4d} {st.median([f(t['ret_pct']) for t in ts]):8.2f} "
              f"{st.median([f(t['month_total_pct']) for t in ts]):10.2f} "
              f"{st.median([f(t['B_dd_from_252d_high_pct']) for t in ts]):11.2f} "
              f"{st.median([f(t['B_dist_sma200_pct']) for t in ts]):10.2f} "
              f"{st.median([f(t['B_dd_from_20d_high_pct']) for t in ts]):10.2f} "
              f"{st.median([f(t['B_rsi14']) for t in ts]):9.1f} "
              f"{st.median([f(t['hold_days']) for t in ts]):8.1f} "
              f"{sum(1 for t in ts if f(t['B_dist_sma200_pct'])<0)/len(ts)*100:12.1f}%")
    # base rate per bucket from panel days
    print("   base rates (panel days in same buckets):")
    gd=defaultdict(list)
    for r in panel: gd[keyfn(mm[(r['sym'],r['date'][:7])])].append(r)
    for b in order:
        ds=gd.get(b,[])
        if not ds: continue
        print(f"   {b:22s} nDays {len(ds):5d} medDd252 {st.median([f(d['dd_from_252d_high_pct']) for d in ds]):7.2f} "
              f"medS200 {st.median([f(d['dist_sma200_pct']) for d in ds]):7.2f} "
              f"medDd20 {st.median([f(d['dd_from_20d_high_pct']) for d in ds]):7.2f} "
              f"medRsi {st.median([f(d['rsi14']) for d in ds]):6.1f} "
              f"%below200 {sum(1 for d in ds if f(d['dist_sma200_pct'])<0)/len(ds)*100:5.1f}%")
bucket_report("month max drawdown from 252d high",
  lambda m: 'A shallow >-3%' if m['min_dd252']>-3 else ('B mild -3..-7%' if m['min_dd252']>-7 else ('C correction -7..-15%' if m['min_dd252']>-15 else 'D deep <-15%')),
  ['A shallow >-3%','B mild -3..-7%','C correction -7..-15%','D deep <-15%'])
bucket_report("month position vs 200DMA (median)",
  lambda m: 'above200 (med>0)' if m['med_s200']>0 else 'below200 (med<=0)',
  ['above200 (med>0)','below200 (med<=0)'])
bucket_report("month touched below 200DMA?",
  lambda m: 'touched below200' if m['min_s200']<0 else 'never below200',
  ['touched below200','never below200'])
