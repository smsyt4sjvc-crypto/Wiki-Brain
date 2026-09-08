# jevons_beta_decay_cell.py v2 — no FRED (it times out from Colab and lags 3-5 days). All Yahoo, one download.
# Jake 9/8: "All summer Nasdaq sold off hard when Iran/oil escalated... unknowns that are now known."
# T1 = beta to the 10Y yield and to Brent, by period.  T2 = shock-day event study.
# PREDICTION: betas shrink CHOP->NOW, and the QQQ-DIA spread on oil-shock days flips negative -> positive.
# ⚠️ v1 failed in Colab: FRED read timeout, AND DFII10 lags to 9/4 / DCOILBRENTEU to 9/1 — the NOW column
#    would have had almost no factor data even on success. v2 uses ^TNX (nominal 10Y) and BZ=F, both same-day.
# ⚠️ Cannot test the TOKEN-denominated seller: OpenAI/Anthropic private, no listed pure-play.

import subprocess, sys, warnings
warnings.filterwarnings('ignore')
try:
    import yfinance as yf, pandas as pd, numpy as np
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas','numpy'])
    import yfinance as yf, pandas as pd, numpy as np

PERIODS = [('PRE  Jan-May26','2026-01-01','2026-05-31'),
           ('CHOP Jun-Aug26','2026-06-01','2026-08-31'),
           ('NOW  Sep26'    ,'2026-09-01','2026-12-31')]
OIL_SHOCK, RATE_SHOCK = 0.02, 5.0          # Brent >= +2% ; 10Y yield >= +5bp

BASKETS = {
 'SEMIS'          : ['NVDA','AVGO','MU','TSM','AMAT','LRCX','KLAC'],
 'COMPUTE-SELLERS': ['ORCL','CRWV','IREN','NBIS'],
 'SOFTWARE'       : ['MSFT','NOW','CRM','PLTR','ADBE'],
 'MEGACAP'        : ['AAPL','GOOGL','META','AMZN'],
 'OLD-ECON'       : ['CAT','DE','UPS','FDX','DAL','WMT'],
}
INDICES  = ['QQQ','SPY','DIA','IGV','SOXX','XLE','XLI']
FACTORS  = ['^TNX','BZ=F','CL=F']
ALL_TK   = sorted(set(sum(BASKETS.values(), []) + INDICES + FACTORS))

print('Downloading...')
px = yf.download(ALL_TK, start='2025-06-01', auto_adjust=True, progress=False, threads=True)['Close']
px = px.dropna(axis=1, how='all')
px.index = pd.to_datetime(px.index).tz_localize(None)
miss = [t for t in ALL_TK if t not in px.columns]
if miss: print('  no data:', ', '.join(miss))
print(f'  {px.shape[1]} tickers, {px.index[0].date()} -> {px.index[-1].date()}')

ret = px.pct_change()
bask = pd.DataFrame(index=ret.index)
for n, mem in BASKETS.items():
    have = [t for t in mem if t in ret.columns]
    if have: bask[n] = ret[have].mean(axis=1)
for t in INDICES:
    if t in ret.columns: bask[t] = ret[t]

tnx = px['^TNX'] if '^TNX' in px.columns else None
if tnx is None: raise SystemExit('^TNX unavailable')
if tnx.median() > 20: tnx = tnx / 10.0          # Yahoo sometimes quotes ^TNX as yield x10
oil = px['BZ=F'] if 'BZ=F' in px.columns else (px['CL=F'] if 'CL=F' in px.columns else None)
print(f'  10Y last = {tnx.dropna().iloc[-1]:.3f}%   oil last = {oil.dropna().iloc[-1]:.2f}' if oil is not None else '  no oil series')
X = pd.DataFrame({'drate': tnx.diff()*100.0,
                  'doil' : oil.pct_change() if oil is not None else np.nan}, index=bask.index)
COLS = [c for c in list(BASKETS.keys()) + INDICES if c in bask.columns]

def beta(y, x):
    d = pd.concat([y, x], axis=1).dropna()
    if len(d) < 6 or d.iloc[:,1].std() == 0: return np.nan, len(d)
    return float(np.polyfit(d.iloc[:,1].values, d.iloc[:,0].values, 1)[0]), len(d)

print('\n' + '='*92)
print('T1  BETA BY PERIOD    beta_rate = bp equity move per +1bp on the 10Y | beta_oil = % per +1% Brent')
print('    PREDICTION: both shrink toward zero from CHOP to NOW')
print('='*92)
print(f'{"BASKET":17}' + ''.join(f'{l:>25}' for l,_,_ in PERIODS))
print(f'{"":17}' + ''.join(f'{"rate     oil     n":>25}' for _ in PERIODS))
for c in COLS:
    line = f'{c:17}'
    for _, a, b in PERIODS:
        m = (bask.index >= a) & (bask.index <= b)
        br, n = beta(bask[c][m], X['drate'][m]); bo, _ = beta(bask[c][m], X['doil'][m])
        line += (f'{br*100:>9.3f}' if br == br else f'{"n/a":>9}') + (f'{bo*100:>9.2f}' if bo == bo else f'{"n/a":>9}') + f'{n:>7}'
    print(line)

print('\n' + '='*92)
print(f'T2  SHOCK DAYS    OIL = Brent >= +{OIL_SHOCK*100:.0f}%   |   RATE = 10Y >= +{RATE_SHOCK:.0f}bp')
print('='*92)
for nm, mask in [('OIL SHOCK', X['doil'] >= OIL_SHOCK), ('RATE SHOCK', X['drate'] >= RATE_SHOCK)]:
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
print('READ: T2 QQQ-DIA on OIL SHOCK days is the direct test. NEGATIVE in CHOP, POSITIVE in NOW = thesis.')
print('      T1 betas falling CHOP->NOW = uncertainty decay. Flat betas = it was sector mix.')
print('      NOW has ~6 sessions. A sign is a reading, not a result.')
print('='*92)
