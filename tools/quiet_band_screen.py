# QUIET + (LOWER-BAND OR POSITIVE-MARKS) SCREEN — Jake's spec 2026-10-12 ~10:00am PT:
# "a signal that has moved less than its two-week daily median, AND is either at the bottom of its Bollinger band
#  or has positive marks in the vault."  Token-free (yfinance). Universe = S&P 500 members + every ticker marked in
#  data/money/marks.csv in the last 120 days. Also backtests the band leg (quiet day + %B<=0.10) on the ±3%/5-session
#  bracket against the all-days baseline. Usage: python3 tools/quiet_band_screen.py [--pctb 0.10]
import io, sys, csv, json, datetime, urllib.request, pandas as pd, numpy as np, yfinance as yf
PCTB = float(sys.argv[sys.argv.index('--pctb')+1]) if '--pctb' in sys.argv else 0.10
UA={'User-Agent':'Mozilla/5.0'}
def sp500():
    try:
        h=urllib.request.urlopen(urllib.request.Request('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',headers=UA),timeout=25).read()
        t=pd.read_html(io.BytesIO(h))[0]; return list(t['Symbol'].str.replace('.','-',regex=False))
    except Exception: return []
today=datetime.date.today(); cut=today-datetime.timedelta(days=120)
net={}
for r in csv.DictReader(open('data/money/marks.csv')):
    try: d=datetime.date.fromisoformat(r['date'][:10])
    except Exception: continue
    if d<cut: continue
    s={'bull':1,'bear':-1}.get(r['col'].strip().lower(),0)
    net[r['ticker'].strip()]=net.get(r['ticker'].strip(),0)+s*float(r['weight'] or 0)
tk=sorted(set(sp500())|set(net))
raw=yf.download(tk,period='2y',interval='1d',auto_adjust=True,progress=False,threads=True)
C,H,L=raw['Close'],raw['High'],raw['Low']
rows=[]; bt=[]
for t in tk:
    if t not in C.columns: continue
    c=C[t].dropna()
    if len(c)<60: continue
    h=H[t].reindex(c.index); l=L[t].reindex(c.index)
    r=c.pct_change()
    med10=r.abs().shift(1).rolling(10).median()            # two-week median |daily move|, excluding the day itself
    sma=c.rolling(20).mean(); sd=c.rolling(20).std()
    pctb=(c-(sma-2*sd))/(4*sd)
    quiet=r.abs()<med10
    rows.append(dict(t=t,last=c.iloc[-1],dt=c.index[-1].date(),today=r.iloc[-1]*100,med10=med10.iloc[-1]*100,
                     quiet=bool(quiet.iloc[-1]),pctb=pctb.iloc[-1],net=net.get(t,0.0)))
    # backtest the band leg: entry at close t, +3% / -3% within 5 sessions
    ci,hi,li=c.values,h.values,l.values; q=quiet.values; pb=pctb.values
    for i in range(30,len(c)-6):
        if np.isnan(pb[i]): continue
        e=ci[i]; out='none'
        for j in range(1,6):
            up=hi[i+j]/e-1>=0.03; dn=li[i+j]/e-1<=-0.03
            if up and dn: out='both'; break
            if up: out='T'; break
            if dn: out='S'; break
        bt.append((bool(q[i]), pb[i]<=PCTB, out))
d=pd.DataFrame(rows)
hit=d[d.quiet & ((d.pctb<=PCTB)|(d.net>0))].copy()
print(f'AS OF {d.dt.max()} (intraday if markets are open) · universe {len(d)} · %B threshold {PCTB}')
print(f'PASS: {len(hit)} names — quiet today AND (lower band OR positive marks)')
b=hit[hit.pctb<=PCTB].sort_values('pctb'); m=hit[(hit.net>0)].sort_values('net',ascending=False)
print('\n— LOWER-BAND LEG (quiet, %B ≤ threshold), lowest %B first:')
for _,x in b.head(25).iterrows(): print(f"  {x.t:6} {x['last']:9.2f}  today {x.today:+5.2f}% vs 2wk median {x.med10:4.2f}%  %B {x.pctb:+.2f}  marks {x.net:+.1f}")
print('\n— POSITIVE-MARKS LEG (quiet, net marks > 0), strongest first:')
for _,x in m.iterrows(): print(f"  {x.t:6} {x['last']:9.2f}  today {x.today:+5.2f}% vs 2wk median {x.med10:4.2f}%  %B {x.pctb:+.2f}  marks {x.net:+.1f}")
B=pd.DataFrame(bt,columns=['quiet','band','o'])
def line(lab,x):
    n=len(x)
    if n: print(f"  {lab:34} n{n:6} · +3% first {(x.o=='T').mean()*100:4.1f}% · −3% first {(x.o=='S').mean()*100:4.1f}% · both {(x.o=='both').mean()*100:3.1f}% · neither {(x.o=='none').mean()*100:4.1f}% · ratio {((x.o=='T').mean()/max((x.o=='S').mean(),1e-9)):.2f}")
print('\nBACKTEST (2y, this universe, entry at the close, ±3% within 5 sessions):')
line('ALL days (same-universe baseline)',B); line('quiet day only',B[B.quiet]); line('lower band only',B[B.band]); line('QUIET + LOWER BAND (the screen)',B[B.quiet&B.band])
lo=hit[(hit.net>0)&(hit.pctb<=0.30)].sort_values('pctb')
print('\n— BOTH LEGS LEANING (quiet, positive marks, lower 30% of the band):')
for _,x in lo.iterrows(): print(f"  {x.t:6} {x['last']:9.2f}  today {x.today:+5.2f}% vs 2wk median {x.med10:4.2f}%  %B {x.pctb:+.2f}  marks {x.net:+.1f}")
d.to_csv(f'data/studies/{today}-quiet-band-screen.csv',index=False)
