import yfinance as yf, pandas as pd, numpy as np
tk=['DHT','FRO','DINO','VLO','MPC','PARR','HUM','ORCL','CRWV','MU','BNO','SPY']
raw=yf.download(tk,period='2y',interval='1d',auto_adjust=False,progress=False,threads=True)
O,H,L,C=raw['Open'],raw['High'],raw['Low'],raw['Close']
live=yf.download(tk,period='1d',interval='1m',progress=False,threads=True)['Close'].ffill().iloc[-1]
print('live ~', live.round(2).to_dict())
for t in tk:
    c=C[t].dropna(); h=H[t].reindex(c.index); l=L[t].reindex(c.index)
    prev=c.iloc[-2] if c.index[-1].date().isoformat()=='2026-10-12' else c.iloc[-1]
    today=(live[t]/prev-1)*100
    hist=pd.DataFrame({'c':c,'h':h,'l':l}).iloc[:-1] if c.index[-1].date().isoformat()=='2026-10-12' else pd.DataFrame({'c':c,'h':h,'l':l})
    r=hist.c.pct_change()*100
    up=(hist.h.shift(-1)/hist.c-1)*100; dn=(hist.l.shift(-1)/hist.c-1)*100; cc=(hist.c.shift(-1)/hist.c-1)*100
    base=pd.DataFrame({'r':r,'up':up,'dn':dn,'cc':cc}).dropna()
    def stats(df):
        n=len(df); 
        return n, (df.up>=3).mean()*100, (df.dn<=-3).mean()*100, ((df.up>=3)&(df.dn>-3)).mean()*100, (df.cc>=3).mean()*100, df.cc.mean()
    n,u,d,uo,c3,m=stats(base)
    lo,hi=(today-1.5,today+1.5)
    cond=base[(base.r>=min(lo, today-1.5))&(base.r<=hi)] if abs(today)<2 else (base[base.r>=today*0.6] if today>0 else base[base.r<=today*0.6])
    n2,u2,d2,uo2,c32,m2=stats(cond)
    print(f'{t:5} today {today:+5.1f}% | ALL n{n}: next-day high≥+3% {u:4.1f}% · low≤−3% {d:4.1f}% · close≥+3% {c3:4.1f}% · mean {m:+.2f}% | LIKE-TODAY n{n2}: high≥+3% {u2:4.1f}% · low≤−3% {d2:4.1f}% · close≥+3% {c32:4.1f}% · mean {m2:+.2f}%')
