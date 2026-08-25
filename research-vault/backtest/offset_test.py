#!/usr/bin/env python3
# =============================================================================
#  ROUND-2 TEST #1 — IS THE MONTH-EDGE RHYTHM REAL, OR AN ARTIFACT OF MY WINDOW?
#
#  Round 1 headline: leg-2 sells land in the last 2 trading days of the calendar
#  month 60.2% of the time (6.2x base), and it survived a 20k-sim order-statistic
#  null. But the ORACLE WAS DEFINED ON CALENDAR MONTHS. If the concentration is
#  really "sells cluster at the END OF WHATEVER WINDOW I CHOSE," it is my
#  definition talking, not the market.
#
#  THE TEST: re-run the identical oracle on windows OFFSET by k calendar days.
#  Then measure BOTH:
#    (a) share of leg-2 sells in the last 2 trading days OF THE WINDOW
#    (b) share of leg-2 sells in the last 2 trading days OF THE CALENDAR MONTH
#  ARTIFACT  => (a) stays high at every offset, (b) COLLAPSES when offset.
#  FLOWS     => (b) stays high even when the window is offset.
# =============================================================================
import csv,os,datetime,json
R=os.path.dirname(os.path.abspath(__file__))

def load(n):
    rows=[]
    for r in csv.DictReader(open(os.path.join(R,'data',n+'.csv'))):
        try: rows.append({'date':r['date'],'h':float(r['high']),'l':float(r['low'])})
        except (ValueError,TypeError): pass
    return [x for x in rows if x['date']>='2023-01-01']

def best_two(days):
    n=len(days); best=None
    for b1 in range(n):
        for s1 in range(b1,n):
            r1=days[s1]['h']/days[b1]['l']-1
            if r1<=0: continue
            if best is None or r1>best[0]: best=(r1,b1,s1,None,None)
            for b2 in range(s1,n):
                for s2 in range(b2,n):
                    r2=days[s2]['h']/days[b2]['l']-1
                    if r2<=0: continue
                    if r1+r2>best[0]: best=(r1+r2,b1,s1,b2,s2)
    return best

def windows(rows,offset):
    """Bucket trading days into windows whose boundary is the 1st of the month SHIFTED by `offset` days."""
    buckets={}
    for i,r in enumerate(rows):
        d=datetime.date.fromisoformat(r['date'])-datetime.timedelta(days=offset)
        buckets.setdefault((d.year,d.month),[]).append(i)
    return [v for k,v in sorted(buckets.items()) if len(v)>=8]

def month_end_flags(rows):
    """For each index: is it in the last 2 TRADING days of its CALENDAR month?"""
    bym={}
    for i,r in enumerate(rows): bym.setdefault(r['date'][:7],[]).append(i)
    flag=[False]*len(rows)
    for m,idx in bym.items():
        for i in idx[-2:]: flag[i]=True
    return flag

print(f"{'offset':>7} {'sym':>4} {'wins':>5} | leg2 sells at WINDOW-end | leg2 sells at CALENDAR month-end | leg1 buys at WINDOW-start")
print('-'*118)
out={}
for sym in ('spx','ndx'):
    rows=load(sym); mflag=month_end_flags(rows)
    for off in (0,7,14,21):
        wins=windows(rows,off)
        we=ce=ws=tot=0
        for idx in wins:
            days=[rows[i] for i in idx]
            res=best_two(days)
            if not res or res[3] is None: continue
            tot+=1
            _,b1,s1,b2,s2=res
            if s2>=len(idx)-2: we+=1                 # last 2 trading days OF THE WINDOW
            if mflag[idx[s2]]: ce+=1                 # last 2 trading days OF THE CALENDAR MONTH
            if b1<=1: ws+=1                          # first 2 trading days of the window
        if tot:
            out[(sym,off)]=(tot,we/tot,ce/tot,ws/tot)
            print(f"{off:>7} {sym:>4} {tot:>5} | {we:>3}/{tot} = {we/tot:6.1%}          | {ce:>3}/{tot} = {ce/tot:6.1%}                | {ws:>3}/{tot} = {ws/tot:6.1%}")
# base rate for "last 2 trading days of the calendar month"
rows=load('spx'); mf=month_end_flags(rows)
print(f"\nBASE RATE, last-2-trading-days-of-CALENDAR-month across all days: {sum(mf)}/{len(mf)} = {sum(mf)/len(mf):.1%}")
json.dump({f'{k[0]}_{k[1]}':v for k,v in out.items()}, open(os.path.join(R,'out','offset_test.json'),'w'), indent=1)
