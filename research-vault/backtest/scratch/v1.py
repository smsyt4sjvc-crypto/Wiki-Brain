import csv, statistics as st
from collections import defaultdict
O='/home/user/INMA-/research-vault/backtest/out/oracle_features.csv'
D='/home/user/INMA-/research-vault/backtest/out/daily_panel.csv'
tr=list(csv.DictReader(open(O)))
pan=list(csv.DictReader(open(D)))
print("n trades",len(tr),"n panel",len(pan))
def f(x):
    try: return float(x)
    except: return None
# 1. same-day legs
sd=[t for t in tr if int(float(t['hold_days']))==0]
print("same-day n",len(sd), "pct", 100*len(sd)/len(tr))
r=[f(t['ret_pct']) for t in sd]
print("sd ret mean %.4f med %.4f min %.4f max %.4f"%(st.mean(r),st.median(r),min(r),max(r)))
# do their returns equal that day's intraday range?
diffs=[]
for t in sd:
    lo=f(t['B_low']); hi=f(t['S_high']); rng=100*(hi-lo)/lo
    diffs.append(abs(rng-f(t['ret_pct'])))
print("max |ret - (S_high-B_low)/B_low|", max(diffs))
# panel intraday range
rng_all=[100*(f(p['high'])-f(p['low']))/f(p['low']) for p in pan]
rng_all_s=sorted(rng_all)
print("panel range mean %.4f med %.4f p90 %.4f max %.4f n=%d"%(st.mean(rng_all),st.median(rng_all),rng_all_s[int(.9*len(rng_all_s))],max(rng_all),len(rng_all)))
# percentile of each same-day leg's range among ALL 1817 days
import bisect
pcts=[]
for x in r:
    pcts.append(100*bisect.bisect_left(rng_all_s,x)/len(rng_all_s))
print("pctile med %.2f mean %.2f min %.2f  frac>90: %.3f"%(st.median(pcts),st.mean(pcts),min(pcts),sum(1 for p in pcts if p>90)/len(pcts)))
# same-symbol percentile (fairer denominator)
by=defaultdict(list)
for p in pan: by[p['sym']].append(100*(f(p['high'])-f(p['low']))/f(p['low']))
for k in by: by[k].sort()
pcts2=[100*bisect.bisect_left(by[t['sym']],f(t['ret_pct']))/len(by[t['sym']]) for t in sd]
print("same-sym pctile med %.2f mean %.2f min %.2f"%(st.median(pcts2),st.mean(pcts2),min(pcts2)))
print("sd split",{k:sum(1 for t in sd if t['sym']==k) for k in set(t['sym'] for t in sd)})
# contribution
tot=sum(f(t['ret_pct']) for t in tr); sds=sum(r)
print("total pp %.2f  sd pp %.2f  share %.3f%%"%(tot,sds,100*sds/tot))
