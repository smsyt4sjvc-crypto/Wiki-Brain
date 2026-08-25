#!/usr/bin/env python3
"""Jake's claim: 'the most violent spikes occur in downtrends.' Test it."""
import csv,os,statistics as st
R=os.path.dirname(os.path.abspath(__file__))
def load(n):
    rows=[]
    for r in csv.DictReader(open(os.path.join(R,'data',n+'.csv'))):
        try: rows.append((r['date'],float(r['close']),float(r['high']),float(r['low'])))
        except: pass
    return rows
for sym in ('spx','ndx','qqq'):
    rows=load(sym); c=[r[1] for r in rows]; d=[r[0] for r in rows]
    n=len(c)
    sma200=[None]*n; dd=[None]*n
    for i in range(n):
        if i>=199: sma200[i]=sum(c[i-199:i+1])/200
        if i>=251: dd[i]=c[i]/max(c[i-251:i+1])-1
    # forward 10-day max run-up from each day's close
    runup=[None]*n
    for i in range(n-10):
        runup[i]=max(c[i+1:i+11])/c[i]-1
    rec=[(d[i],runup[i],c[i]>sma200[i],dd[i]) for i in range(n)
         if runup[i] is not None and sma200[i] is not None and dd[i] is not None and d[i]>='2023-01-01']
    if not rec: continue
    above=[x[1] for x in rec if x[2]]; below=[x[1] for x in rec if not x[2]]
    top=sorted(rec,key=lambda x:-x[1])[:int(len(rec)*0.05)]  # top 5% spikes
    tb=sum(1 for x in top if not x[2]); base_below=len(below)/len(rec)
    print(f"\n=== {sym.upper()}  n={len(rec)} days, 2023-01 -> now")
    print(f"  fwd 10d max run-up | ABOVE 200DMA: mean {st.mean(above)*100:5.2f}%  n={len(above)}")
    print(f"                     | BELOW 200DMA: mean {st.mean(below)*100:5.2f}%  n={len(below)}")
    print(f"  TOP 5% SPIKES (n={len(top)}): {tb} were BELOW the 200DMA = {tb/len(top):.1%}  vs base rate {base_below:.1%}  LIFT {tb/len(top)/base_below if base_below else 0:.2f}x")
    for lo,hi,lbl in ((-1,-0.10,'dd < -10%'),(-0.10,-0.05,'-10% to -5%'),(-0.05,-0.02,'-5% to -2%'),(-0.02,1,'within 2% of high')):
        b=[x[1] for x in rec if lo<=x[3]<hi]
        if len(b)>15: print(f"    {lbl:<20} n={len(b):>4}  mean fwd-10d max run-up {st.mean(b)*100:5.2f}%  |  95th pct {sorted(b)[int(len(b)*.95)]*100:5.2f}%")
