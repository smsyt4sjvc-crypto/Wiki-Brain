import csv, statistics as st
from collections import defaultdict
OUT="/home/user/INMA-/research-vault/backtest/out/"
def load(p):
    with open(p) as f: return list(csv.DictReader(f))
dp=load(OUT+"daily_panel.csv"); tr=load(OUT+"oracle_features.csv")
def f(r,k):
    v=r.get(k,'')
    try: return float(v)
    except: return None
by=defaultdict(list)
for r in dp: by[r['sym']].append(r)
for s in by: by[s].sort(key=lambda r:r['date'])
# episode counting for vix cuts (contiguous runs, spx only to avoid double count)
for thr in [20,25]:
    for s in ['spx']:
        rows=by[s]; runs=0; prev=False; days=0
        for r in rows:
            hit=f(r,'vix')>thr
            if hit and not prev: runs+=1
            if hit: days+=1
            prev=hit
        print("vix>%d on %s: %d days in %d contiguous episodes (median %.1f days/episode) -> effective n is EPISODES, not days"%(thr,s,days,runs,days/runs))
for thr in [3,5]:
    rows=by['spx']; runs=0; prev=False; days=0
    for r in rows:
        hit=f(r,'vix_chg5d')>thr
        if hit and not prev: runs+=1
        if hit: days+=1
        prev=hit
    print("vix_chg5d>+%d on spx: %d days in %d episodes (%.1f days/ep)"%(thr,days,runs,days/runs))
# months represented
print("\nmonths with any vix>25 day:", len({r['date'][:7] for r in dp if f(r,'vix')>25}), "of", len({r['date'][:7] for r in dp}))
print("months with any vix_chg5d>+5 day:", len({r['date'][:7] for r in dp if f(r,'vix_chg5d')>5}))

# oracle return vs buy VIX
print("\n=== ORACLE TRADE RETURN by B_vix bucket (within-oracle, selection-conditioned) ===")
buck=[(0,15),(15,18),(18,20),(20,25),(25,99)]
for lo,hi in buck:
    sub=[t for t in tr if lo<=f(t,'B_vix')<hi]
    if not sub: continue
    print("  B_vix [%2d,%2d): n=%3d  mean ret %5.2f%%  median %5.2f%%  mean hold %.1fd"%(lo,hi,len(sub),
      st.mean([f(t,'ret_pct') for t in sub]),st.median([f(t,'ret_pct') for t in sub]),st.mean([f(t,'hold_days') for t in sub])))
print("  ALL: n=%d mean %.2f%% median %.2f%%"%(len(tr),st.mean([f(t,'ret_pct') for t in tr]),st.median([f(t,'ret_pct') for t in tr])))
print("\n=== by B_vix_chg5d bucket ===")
for lo,hi in [(-99,-2),(-2,0),(0,2),(2,5),(5,99)]:
    sub=[t for t in tr if lo<=f(t,'B_vix_chg5d')<hi]
    print("  chg5d [%3d,%3d): n=%3d mean ret %5.2f%% median %5.2f%%"%(lo,hi,len(sub),st.mean([f(t,'ret_pct') for t in sub]),st.median([f(t,'ret_pct') for t in sub])))
# same-day trades flag
sd=[t for t in tr if float(t['hold_days'])==0]
print("\nsame-day trades n=%d: mean B_vix %.2f (all buys %.2f), mean B_vix_chg5d %.2f (all %.2f), mean ret %.2f%%"%(
 len(sd),st.mean([f(t,'B_vix') for t in sd]),st.mean([f(t,'B_vix') for t in tr]),
 st.mean([f(t,'B_vix_chg5d') for t in sd]),st.mean([f(t,'B_vix_chg5d') for t in tr]),st.mean([f(t,'ret_pct') for t in sd])))
# recompute headline cuts EXCLUDING same-day
tr2=[t for t in tr if float(t['hold_days'])>0]
d=[f(r,'vix_chg5d') for r in dp]
for thr in [3,5]:
    base=sum(1 for x in d if x>thr)/len(d)
    b=sum(1 for t in tr2 if f(t,'B_vix_chg5d')>thr)/len(tr2)
    print("  ex-same-day: vix_chg5d>+%d base %.1f%% BUY %.1f%% (n=%d) lift %.2fx"%(thr,100*base,100*b,len(tr2),b/base))
