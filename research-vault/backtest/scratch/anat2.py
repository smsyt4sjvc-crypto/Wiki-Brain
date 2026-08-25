import csv,json,statistics as st
from collections import defaultdict, Counter
exec(open('/home/user/INMA-/research-vault/backtest/scratch/anat.py').read().split('print("=== 1. HOLD DAYS ===")')[0])

# --- same-day legs: intraday range percentile ---
allrange=sorted(100*(f(r['high'])/f(r['low'])-1) for s in panel for r in panel[s])
def pctile(v,arr): 
    import bisect; return 100*bisect.bisect_left(arr,v)/len(arr)
sd=[t for t in T if t['hold_days']==0]
ps=[pctile(t['ret_pct'],allrange) for t in sd]
print("SAME-DAY LEGS n=%d: median intraday-range pctile vs all 1817 days = %.1f ; mean %.1f ; min %.1f ; frac above 90th pctile %.0f%%"%(
    len(sd),st.median(ps),st.mean(ps),min(ps),100*sum(1 for x in ps if x>=90)/len(ps)))
print("  their ret_pct:",[round(t['ret_pct'],2) for t in sd])
print("  base: mean daily range 1.22%%, median 1.05%%, p90 %.2f%%"%(allrange[int(.9*len(allrange))]))
print("  same-day months:",Counter(t['month'] for t in sd).most_common(6))
print("  same-day by sym:",Counter(t['sym'] for t in sd))

print()
print("=== 2. LEG1->LEG2 GAP ===")
gaps=[];pxgap=[];samebuy=0;pairs=0;overlap0=0
for k,d in tm.items():
    if 1 in d and 2 in d:
        pairs+=1
        t1,t2=d[1],d[2]
        g=t2['buy_i_in_month']-t1['sell_i_in_month']
        gaps.append(g)
        pxgap.append(100*(t2['buy_px']/t1['sell_px']-1))
        if t1['sell_date']==t2['buy_date']: samebuy+=1
print("pairs=%d  gap(trading days between leg1 sell and leg2 buy) dist:"%pairs, sorted(Counter(gaps).items()))
print("  gap==0 (leg2 buys same day leg1 sells) n=%d (%.1f%%)"%(sum(1 for g in gaps if g==0),100*sum(1 for g in gaps if g==0)/len(gaps)))
print("  gap<=1 n=%d (%.1f%%)  median gap %.1f  mean %.2f"%(sum(1 for g in gaps if g<=1),100*sum(1 for g in gaps if g<=1)/len(gaps),st.median(gaps),st.mean(gaps)))
print("  price gap leg2buy vs leg1sell: mean %.2f%% median %.2f%% ; frac negative(leg2 buys BELOW leg1 sell) %.1f%%"%(
    st.mean(pxgap),st.median(pxgap),100*sum(1 for x in pxgap if x<0)/len(pxgap)))
print("  frac leg2 buy below leg1 sell by >2%%: %.1f%%"%(100*sum(1 for x in pxgap if x<-2)/len(pxgap)))
# how deep is the intervening dip
print("  distribution of pxgap deciles:", [round(x,2) for x in st.quantiles(pxgap,n=10)])
# base rate: random pair of consecutive dates in month with same gap
print()
print("=== 2b. leg1 vs leg2 return split ===")
r1=[tm[k][1]['ret_pct'] for k in tm if 1 in tm[k]]
r2=[tm[k][2]['ret_pct'] for k in tm if 2 in tm[k]]
print("leg1 n=%d mean %.2f%% sum %.1f%% | leg2 n=%d mean %.2f%% sum %.1f%%"%(len(r1),st.mean(r1),sum(r1),len(r2),st.mean(r2),sum(r2)))
h1=[tm[k][1]['hold_days'] for k in tm if 1 in tm[k]]; h2=[tm[k][2]['hold_days'] for k in tm if 2 in tm[k]]
print("leg1 median hold %.1f  leg2 median hold %.1f"%(st.median(h1),st.median(h2)))
b1=[tm[k][1]['buy_i_in_month'] for k in tm if 1 in tm[k]]
print("leg1 buy tday-in-month: median %.1f ; frac in first 3 tdays %.0f%%"%(st.median(b1),100*sum(1 for x in b1 if x<3)/len(b1)))
s2=[tm[k][2]['sell_i_in_month']-tm[k][2]['days_in_month']+1 for k in tm if 2 in tm[k]]
print("leg2 sell rel to month end (0=last tday): median %.1f ; frac in last 3 tdays %.0f%%"%(st.median(s2),100*sum(1 for x in s2 if x>=-2)/len(s2)))
