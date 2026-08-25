import csv,json,statistics as st
from collections import defaultdict, Counter
OUT='/home/user/INMA-/research-vault/backtest/out/'
T=json.load(open(OUT+'oracle_trades.json'))
D=[r for r in csv.DictReader(open(OUT+'daily_panel.csv'))]
def f(x):
    try: return float(x)
    except: return None
# panel by sym, ordered
panel=defaultdict(list)
for r in D: panel[r['sym']].append(r)
for s in panel: panel[s].sort(key=lambda r:r['date'])

# per (sym,month) month stats from panel
M=defaultdict(list)
for s,rows in panel.items():
    for r in rows: M[(s,r['date'][:7])].append(r)

mstat={}
for k,rows in M.items():
    rows.sort(key=lambda r:r['date'])
    c0=f(rows[0]['close']); cN=f(rows[-1]['close'])
    prevclose=None
    # find prior month last close for true month return
    hi=max(f(r['high']) for r in rows); lo=min(f(r['low']) for r in rows)
    dailyret=[f(r['ret_1d_pct']) for r in rows if f(r['ret_1d_pct']) is not None]
    mstat[k]=dict(n=len(rows), first_close=c0,last_close=cN,
        bh_pct=100*(cN/c0-1),
        range_pct=100*(hi/lo-1), hi=hi, lo=lo,
        path=sum(abs(x) for x in dailyret),
        realvol=st.mean([f(r['realvol20_ann_pct']) for r in rows]),
        atr=st.mean([f(r['atr14_pct']) for r in rows]),
        vix=st.mean([f(r['vix']) for r in rows]),
        maxdd=min(f(r['dd_from_20d_high_pct']) for r in rows))
# proper buy&hold: prev month close -> this month close
for s,rows in panel.items():
    months=sorted(set(r['date'][:7] for r in rows))
    for i,m in enumerate(months):
        if i>0:
            prev=M[(s,months[i-1])][-1]
            mstat[(s,m)]['bh_pct']=100*(mstat[(s,m)]['last_close']/f(prev['close'])-1)

# trades by (sym,month)
tm=defaultdict(dict)
for t in T: tm[(t['sym'],t['month'])][t['leg']]=t

print("=== 1. HOLD DAYS ===")
h=[t['hold_days'] for t in T]
print("mean %.2f median %.1f min %d max %d"%(st.mean(h),st.median(h),min(h),max(h)))
print(sorted(Counter(h).items()))
print("same-day n=%d (%.1f%%)"%(sum(1 for x in h if x==0),100*sum(1 for x in h if x==0)/len(h)))
for lo,hi,lab in [(0,0,'0'),(1,3,'1-3'),(4,7,'4-7'),(8,14,'8-14'),(15,99,'15+')]:
    sub=[t for t in T if lo<=t['hold_days']<=hi]
    print("  %-5s n=%3d  meanret %.2f%%  medret %.2f%%  sumret %.1f%%  share_of_total %.1f%%"%(
        lab,len(sub),st.mean([t['ret_pct'] for t in sub]),st.median([t['ret_pct'] for t in sub]),
        sum(t['ret_pct'] for t in sub), 100*sum(t['ret_pct'] for t in sub)/sum(t['ret_pct'] for t in T)))
print("total sum ret all trades %.1f%%"%sum(t['ret_pct'] for t in T))

print()
print("=== 1b. BASE RATE: random h-day close-close hold, and h-day low->high ===")
# base rate: for each hold length bucket, all overlapping windows in panel
def windows(h):
    out=[]
    for s,rows in panel.items():
        for i in range(len(rows)-h):
            a,b=rows[i],rows[i+h]
            if a['date'][:7]!=b['date'][:7]: continue   # same calendar month only, matching oracle constraint
            out.append((100*(f(b['close'])/f(a['close'])-1), 100*(f(b['high'])/f(a['low'])-1)))
    return out
for hh in [0,1,2,3,5,7,10,14,20]:
    w=windows(hh) if hh>0 else [(0.0,100*(f(r['high'])/f(r['low'])-1)) for s in panel for r in panel[s]]
    cc=[x[0] for x in w]; lh=[x[1] for x in w]
    orc=[t['ret_pct'] for t in T if t['hold_days']==hh]
    print("h=%2d  base n=%4d  close-close mean %.2f%% med %.2f%%  | low->high mean %.2f%% med %.2f%% p90 %.2f%% max %.2f%% || oracle n=%2d mean %.2f%%"%(
        hh,len(w),st.mean(cc),st.median(cc),st.mean(lh),st.median(lh),sorted(lh)[int(.9*len(lh))],max(lh),
        len(orc), st.mean(orc) if orc else float('nan')))
