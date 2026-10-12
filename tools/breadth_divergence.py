# BREADTH DIVERGENCE CHECK — token-free (set 2026-10-11 after the 8/18 weekly monitor was never run)
# The vault's registered condition (market-fragility 8/18, Roberts/Rubner): "a NEW INDEX HIGH on a FALLING
# breadth reading" = % of S&P members above their own 200-day average, read at each S&P record close.
# Also prints the drawdown-from-all-time-high buckets (price, NOT dividend-adjusted, vs intraday ATH —
# the convention that reproduced the 10/11 "84% are 10% below ATH" post to within a point).
# Usage: python3 tools/breadth_divergence.py   (≈2-4 min; Yahoo via yfinance; current members = survivorship caveat)
import io, json, sys, urllib.request, pandas as pd, yfinance as yf
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
def members():
    try:
        h = urllib.request.urlopen(urllib.request.Request('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=UA), timeout=25).read()
        t = pd.read_html(io.BytesIO(h))[0]
    except Exception:
        t = pd.read_csv(io.BytesIO(urllib.request.urlopen(urllib.request.Request('https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv', headers=UA), timeout=25).read()))
        t = t.rename(columns={'Sector': 'GICS Sector'})
    return dict(zip(t['Symbol'].str.replace('.', '-', regex=False), t['GICS Sector']))
sec = members(); tk = list(sec)
raw = yf.download(tk + ['^GSPC'], period='max', interval='1d', auto_adjust=False, progress=False, threads=True)
C, H, A = raw['Close'], raw['High'], raw['Adj Close']
asof = C.index[-1].date()
# 1) drawdown buckets (price vs intraday ATH)
rows = []
for t in tk:
    if t not in C.columns: continue
    c, h = C[t].dropna(), H[t].dropna()
    if len(c) < 2 or not len(h): continue
    rows.append(dict(t=t, sec=sec[t], dd=(c.iloc[-1] / h.max() - 1) * 100))
d = pd.DataFrame(rows)
print(f'AS OF {asof} · {len(d)} members · price vs intraday all-time high')
for k in (10, 20, 30, 50): print(f'  ≥{k}% below ATH: {(d.dd <= -k).mean()*100:.1f}%')
print('  by sector (≥10% below):'); print((d.groupby('sec').dd.apply(lambda x: (x <= -10).mean() * 100)).sort_values(ascending=False).round(1).to_string())
# 2) % above 200-day (dividend-adjusted closes) at each S&P record close since the start of last year
AA = A[[t for t in tk if t in A.columns]].loc['2024-01-01':].ffill(limit=3)
sma = AA.rolling(200, min_periods=200).mean(); ok = sma.notna() & AA.notna()
pct = ((AA > sma) & ok).sum(axis=1) / ok.sum(axis=1).replace(0, float('nan')) * 100
spx = C['^GSPC'].dropna(); rec = spx[spx >= spx.cummax() - 1e-9].loc['2025-01-01':]
print(f'\n% ABOVE 200-DAY now: {pct.iloc[-1]:.1f}%  (S&P {spx.iloc[-1]:.2f}; record close {spx.max():.2f} on {spx.idxmax().date()})')
print('RECORD CLOSES (last 12) with breadth:')
for i, v in rec.tail(12).items(): print(f'  {i.date()}  S&P {v:.2f}  above-200: {pct.loc[i]:.1f}%')
out = f'data/breadth/{asof}.csv'; d.to_csv(out, index=False); print('saved', out)
