#!/usr/bin/env python3
# =============================================================================
#  ROUND-2 TEST #2 — OUT OF SAMPLE. The round-1 survivors were all measured on
#  the daily panel IN SAMPLE (2023-01 -> 2026-08). Fit on the first half, test
#  on the second. Also extends to 2022 -- the only real downtrend in the file.
# =============================================================================
import csv,os,math,statistics as st
R=os.path.dirname(os.path.abspath(__file__))
def load(n):
    rows=[]
    for r in csv.DictReader(open(os.path.join(R,'data',n+'.csv'))):
        try: rows.append((r['date'],float(r['close']),float(r['low'])))
        except: pass
    return rows
def rsi(v,i,n=14):
    if i<n: return None
    g=l=0.0
    for j in range(i-n+1,i+1):
        ch=v[j]-v[j-1]; g+=max(ch,0); l+=max(-ch,0)
    return 100.0 if l==0 else 100-100/(1+(g/n)/(l/n))

def run(sym,start,end,label):
    rows=[r for r in load(sym)]
    d=[r[0] for r in rows]; c=[r[1] for r in rows]; lo=[r[2] for r in rows]
    n=len(c); res={}
    def fwd(i,h): return c[i+h]/c[i]-1 if i+h<n else None
    for name,cond in (
        ('ALL', lambda i: True),
        ('RSI<25', lambda i: (rsi(c,i) or 99)<25),
        ('RSI<30', lambda i: (rsi(c,i) or 99)<30),
        ('20d low', lambda i: i>=19 and lo[i]==min(lo[i-19:i+1])),
        ('20dlow & RSI<30', lambda i: i>=19 and lo[i]==min(lo[i-19:i+1]) and (rsi(c,i) or 99)<30),
        ('5+ up days (AVOID)', lambda i: i>=5 and all(c[j]>c[j-1] for j in range(i-4,i+1))),
    ):
        f5=[]; f10=[]
        for i in range(220,n-10):
            if not (start<=d[i]<=end): continue
            try:
                if not cond(i): continue
            except Exception: continue
            a=fwd(i,5); b=fwd(i,10)
            if a is not None: f5.append(a)
            if b is not None: f10.append(b)
        if len(f5)>=12:
            res[name]=(len(f5), st.mean(f5)*100, 100*sum(1 for x in f5 if x>0)/len(f5), st.mean(f10)*100)
    print(f"\n--- {sym.upper()}  {label}  ({start} .. {end})")
    print(f"    {'condition':<20}{'n':>5}{'fwd5d mean':>12}{'% pos':>8}{'fwd10d mean':>13}   vs ALL")
    base=res.get('ALL')
    for k,(nn,m5,p,m10) in res.items():
        lift=f"{m5/base[1]:5.2f}x" if base and base[1] else ""
        print(f"    {k:<20}{nn:>5}{m5:>11.2f}%{p:>7.1f}%{m10:>12.2f}%   {lift}")

for sym in ('spx','ndx'):
    run(sym,'2023-01-01','2024-12-31','IN-SAMPLE  (fit window)')
    run(sym,'2025-01-01','2026-08-19','OUT-OF-SAMPLE')
    run(sym,'2022-01-01','2022-12-31','2022 — THE DOWNTREND')
    run(sym,'2000-01-01','2022-12-31','DEEP HISTORY — everything before the sample')
