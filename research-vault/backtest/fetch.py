#!/usr/bin/env python3
"""Pull daily OHLCV from Yahoo chart API. Reads the ARRAYS, never meta.chartPreviousClose."""
import json, urllib.request, os, sys, time, csv
ROOT = os.path.dirname(os.path.abspath(__file__))
UA = {'User-Agent': 'Mozilla/5.0'}
TICKERS = {
    '^GSPC': 'spx', '^IXIC': 'ndx', '^VIX': 'vix', '^TNX': 'ust10y',
    '^FVX': 'ust5y', '^TYX': 'ust30y', '^IRX': 'ust13w', 'DX-Y.NYB': 'dxy',
    'CL=F': 'wti', 'GC=F': 'gold', 'HYG': 'hyg', 'TLT': 'tlt', 'QQQ': 'qqq', 'SPY': 'spy',
}
def pull(tk):
    u = (f'https://query2.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(tk)}'
         f'?period1=946684800&period2=9999999999&interval=1d&includePrePost=false')
    r = urllib.request.Request(u, headers=UA)
    d = json.load(urllib.request.urlopen(r, timeout=60))['chart']['result'][0]
    ts = d['timestamp']; q = d['indicators']['quote'][0]
    rows = []
    import datetime
    for i, t in enumerate(ts):
        o, h, l, c, v = (q['open'][i], q['high'][i], q['low'][i], q['close'][i], q.get('volume', [None]*len(ts))[i])
        if c is None: continue
        dt = datetime.datetime.utcfromtimestamp(t).strftime('%Y-%m-%d')
        rows.append((dt, o, h, l, c, v))
    return rows
for tk, name in TICKERS.items():
    try:
        rows = pull(tk)
        p = os.path.join(ROOT, 'data', name + '.csv')
        with open(p, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['date','open','high','low','close','volume']); w.writerows(rows)
        print(f'{name:<8} {len(rows):>5} rows  {rows[0][0]} .. {rows[-1][0]}')
    except Exception as e:
        print(f'{name:<8} FAIL {e}')
    time.sleep(0.4)
