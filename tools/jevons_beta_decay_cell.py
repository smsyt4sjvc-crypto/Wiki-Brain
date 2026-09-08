# jevons_beta_decay_cell.py — DOES THE THESIS PRINT? (complete Colab cell)
# Jake 9/8: "All summer Nasdaq sold off hard when Iran/oil escalated... unknowns that are now known."
# T1 = beta to real yields + Brent, by period.  T2 = shock-day event study.
# PREDICTION: betas shrink CHOP->NOW, and the QQQ-DIA spread on oil-shock days flips negative -> positive.
# ⚠️ Cannot test the TOKEN-denominated seller: OpenAI/Anthropic are private, no listed pure-play.
# ⚠️ EPS-vs-multiple decomposition (T3) is a SEPARATE cell — ask for it if T1/T2 come back supportive.

import subprocess, sys, io, urllib.request, warnings
warnings.filterwarnings('ignore')
try:
    import yfinance as yf, pandas as pd, numpy as np
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas','numpy'])
    import yfinance as yf, pandas as pd, numpy as np

PERIODS = [('PRE  Jan-May26','2026-01-01','2026-05-31'),
           ('CHOP Jun-Aug26','2026-06-01','2026-08-31'),
           ('NOW  Sep26'    ,'2026-09-01','2026-12-31')]
OIL_SHOCK, REAL_SHOCK = 0.02, 5.0

BASKETS = {
 'SEMIS'          : ['NVDA','AVGO','MU','TSM','AMAT','LRCX','KLAC'],
 'COMPUTE-SELLERS': ['ORCL','CRWV','IREN','NBIS'],
 'SOFTWARE'       : ['MSFT','NOW','CRM','PLTR','ADBE'],
 'MEGACAP'        : ['AAPL','GOOGL','META','AMZN'],
 'OLD-ECON'       : ['CAT','DE','UPS','FDX','DAL','WMT'],
}
INDICES = ['QQQ','SPY','DIA','IGV','SOXX','XLE','XLI']
ALL_TK = sorted(set(sum(BASKETS.values(), []) + INDICES))

def fred(sid):
    try:
        u = f'https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}'
        raw = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent':'Mozilla/5.0'}), timeout=30).read()
        d = pd.read_csv(io.BytesIO(raw)); d.columns = ['DATE','V']
        d['DATE'] = pd.to_datetime(d['DATE']); d['V'] = pd.to_numeric(d['V'], errors='coerce')
        s = d.dropna().set_index('DATE')['V']
        print(f'  {sid}: {len(s)} obs, last {s.index[-1].date()} = {s.iloc[-1]}')
        return s
    except Exception as e:
        print(f'  {sid} FAILED: {str(e)[:60]}'); return None

print('FRED...')
real10, brent = fred('DFII10'), fred('DCOILBRENTEU')
if real10 is None: raise SystemExit('DFII10 unavailable')

print('\nPrices...')
px = yf.download(ALL_TK, start='2025-06-01', auto_adjust=True, progress=False, threads=True)['Close'].dropna(axis=1, how='all')
px.index = pd.to_datetime(px.index).tz_localize(None)
miss = [t for t in ALL_TK if t not in px.columns]
if miss: print('  no data:', ', '.join(miss))
ret = px.pct_change()

bask = pd.DataFrame(index=ret.index)
for n, mem in BASKETS.items():
    have = [t for t in mem if t in ret.columns]
    if have: bask[n] = ret[have].mean(axis=1)
for t in INDICES:
    if t in ret.columns: bask[t] = ret[t]

X = pd.DataFrame({
    'dreal': real10.reindex(bask.index, method='ffill').diff()*100.0,
    'doil' : brent.reindex(bask.index, method='ffill').pct_change() if brent is not None else np.nan,
}, index=bask.index)
COLS = [c for c in list(BASKETS.keys()) + INDICES if c in bask.columns]

def beta(y, x):
    d = pd.concat([y, x], axis=1).dropna()
    if len(d) < 8 or d.iloc[:,1].std() == 0: return np.nan, len(d)
    return float(np.polyfit(d.iloc[:,1].values, d.iloc[:,0].values, 1)[0]), len(d)

print('\n' + '='*92)
print('T1  BETA BY PERIOD   beta_real = bp equity move per +1bp 10Y REAL | beta_oil = % per +1% Brent')
print('    PREDICTION: both shrink toward zero from CHOP to NOW')
print('='*92)
print(f'{"BASKET":17}' + ''.join(f'{l:>25}' for l,_,_ in PERIODS))
print(f'{"":17}' + ''.join(f'{"real     oil     n":>25}' for _ in PERIODS))
for c in COLS:
    line = f'{c:17}'
    for _, a, b in PERIODS:
        m = (bask.index >= a) & (bask.index <= b)
        br, n = beta(bask[c][m], X['dreal'][m]); bo, _ = beta(bask[c][m], X['doil'][m])
        line += f'{br*100:>9.3f}{bo*100:>9.2f}{n:>7}' if br == br else f'{"n/a":>25}'
    print(line)

print('\n' + '='*92)
print(f'T2  SHOCK DAYS   OIL = Brent >= +{OIL_SHOCK*100:.0f}%  |  REAL = 10Y real >= +{REAL_SHOCK:.0f}bp')
print('='*92)
for nm, mask in [('OIL SHOCK', X['doil'] >= OIL_SHOCK), ('REAL-RATE SHOCK', X['dreal'] >= REAL_SHOCK)]:
    print(f'\n{nm} — mean return on those days (%)')
    print(f'{"BASKET":17}' + ''.join(f'{l:>17}' for l,_,_ in PERIODS))
    print(f'{"  (n days)":17}' + ''.join(f'{int((mask & (X.index>=a) & (X.index<=b)).sum()):>17}' for _,a,b in PERIODS))
    for c in COLS:
        line = f'{c:17}'
        for _, a, b in PERIODS:
            m = mask & (X.index >= a) & (X.index <= b)
            line += f'{bask.loc[m, c].mean()*100:>+17.2f}' if m.sum() else f'{"-":>17}'
        print(line)
    if 'QQQ' in bask.columns and 'DIA' in bask.columns:
        line = f'{"SPREAD QQQ-DIA":17}'
        for _, a, b in PERIODS:
            m = mask & (X.index >= a) & (X.index <= b)
            line += f'{(bask.loc[m,"QQQ"].mean()-bask.loc[m,"DIA"].mean())*100:>+17.2f}' if m.sum() else f'{"-":>17}'
        print(line + '   <- positive = Nasdaq OUTPERFORMS')

print('\n' + '='*92)
print('READ: T2 QQQ-DIA spread is the direct test. NEGATIVE in CHOP and POSITIVE in NOW = thesis prints.')
print('      T1 betas falling CHOP->NOW = the uncertainty-decay mechanism. Flat betas = it was sector mix.')
print('      n for NOW is ~6 sessions. A sign is a reading, not a result.')
print('='*92)
