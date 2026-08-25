import csv,json,statistics as st,random,bisect
from collections import defaultdict, Counter
exec(open('/home/user/INMA-/research-vault/backtest/scratch/anat.py').read().split('print("=== 1. HOLD DAYS ===")')[0])
random.seed(7)
print("=== 2c. BASE RATE for 'leg2 buys below leg1 sell' ===")
# for each gap g: over all day pairs (t,t+g) within same calendar month, low(t+g)/high(t)-1
for g in [0,1,2,3,5,8]:
    vals=[]
    for s,rows in panel.items():
        for i in range(len(rows)-g):
            a,b=rows[i],rows[i+g]
            if a['date'][:7]!=b['date'][:7]: continue
            vals.append(100*(f(b['low'])/f(a['high'])-1))
    print("  g=%d base n=%4d: frac<0 %.1f%%  median %.2f%%  mean %.2f%%  p10 %.2f%%"%(
        g,len(vals),100*sum(1 for v in vals if v<0)/len(vals),st.median(vals),st.mean(vals),sorted(vals)[int(.1*len(vals))]))
obs=[]
for k,d in tm.items():
    if 1 in d and 2 in d: obs.append((d[2]['buy_i_in_month']-d[1]['sell_i_in_month'],100*(d[2]['buy_px']/d[1]['sell_px']-1)))
for lo,hi,lab in [(0,0,'g=0'),(1,2,'g=1-2'),(3,5,'g=3-5'),(6,99,'g>=6')]:
    sub=[v for g,v in obs if lo<=g<=hi]
    print("  ORACLE %-6s n=%2d median %.2f%% mean %.2f%%"%(lab,len(sub),st.median(sub),st.mean(sub)))

print()
print("=== 2d. NULL for gap distribution (random placement, same hold lengths) ===")
cnt=Counter();tot=0
for k,d in tm.items():
    if not(1 in d and 2 in d): continue
    h1,h2,N=d[1]['hold_days'],d[2]['hold_days'],d[1]['days_in_month']
    valid=[]
    for b1 in range(N):
        s1=b1+h1
        for b2 in range(s1,N):
            if b2+h2<=N-1: valid.append(b2-s1)
    if not valid: continue
    for _ in range(2000): cnt[random.choice(valid)]+=1
    tot+=2000
print("  NULL: P(gap=0)=%.1f%%  P(gap<=1)=%.1f%%  median=%d"%(100*cnt[0]/tot,100*(cnt[0]+cnt[1])/tot,
    sorted(cnt.elements())[tot//2]))
print("  OBS : P(gap=0)=27.3%  P(gap<=1)=38.6%  median=3")

print()
print("=== 3. MONTH TOTALS ===")
mt={}
for k,d in tm.items(): mt[k]=list(d.values())[0]['month_total_pct']
months=sorted(set(m for s,m in mt))
tot_or=sum(mt.values())
print("44 months x 2 syms = %d month-cells, sum oracle %.1f%%"%(len(mt),tot_or))
rows=[]
for k in sorted(mt, key=lambda k:-mt[k]):
    s,m=k; ms=mstat[k]
    rows.append((k,mt[k],ms['bh_pct'],ms['range_pct'],ms['realvol'],ms['vix'],ms['path'],ms['n']))
print("TOP 10 month-cells by oracle total:")
for r in rows[:10]: print("  %s %s  oracle %6.2f%%  b&h %6.2f%%  range %5.2f%%  rv %4.1f  vix %4.1f  path %5.1f%%"%(r[0][0],r[0][1],r[1],r[2],r[3],r[4],r[5],r[6]))
print("BOTTOM 8:")
for r in rows[-8:]: print("  %s %s  oracle %6.2f%%  b&h %6.2f%%  range %5.2f%%  rv %4.1f  vix %4.1f  path %5.1f%%"%(r[0][0],r[0][1],r[1],r[2],r[3],r[4],r[5],r[6]))
v=sorted(mt.values(),reverse=True)
for k_ in [4,8,11,22]:
    print("  top %2d of 88 cells = %.1f%% of total oracle return"%(k_,100*sum(v[:k_])/tot_or))
bh=[mstat[k]['bh_pct'] for k in mt]
print("  buy&hold concentration: top 8 of 88 months = %.1f%% of summed b&h (%.1f%%)"%(
    100*sum(sorted(bh,reverse=True)[:8])/sum(bh),sum(bh)))
