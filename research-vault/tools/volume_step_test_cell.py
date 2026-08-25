# ============================================================================
#  VOLUME STEP TEST — is the late-2016 "volume eruption" on the .SPX chart a
#  MARKET event or a DATA-SOURCE event?
#
#  A level SHIFT that never reverts is the signature of a methodology change.
#  Real volume is event-driven and MEAN-REVERTING: it spiked in 2008 and came
#  back down. A permanent 4-5x step that holds for a decade is not behaviour.
#
#  THE THREE TESTS
#   [1] Does the step exist in a DIFFERENT vendor's SPX volume, at the same date?
#       If the break moves or vanishes, it is vendor-specific.
#   [2] Does SPY -- a REAL instrument with REAL consolidated volume -- do the same
#       thing on the same date? SPX is an INDEX and does not trade, so any volume
#       on it is synthesised. SPY is the control.
#   [3] Is the ratio before/after a CLEAN CONSTANT? A source or units change gives
#       a flat multiple. A behavioural change does not.
#
#  PRIOR: a switch from PRIMARY-EXCHANGE volume to CONSOLIDATED-TAPE volume
#  produces roughly a 4-5x instantaneous step with no reversion -- which is about
#  the size on the chart. That is the hypothesis to kill or confirm.
# ============================================================================
import subprocess, sys
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'yfinance']); import yfinance as yf
import numpy as np, pandas as pd

TK = {'SPX index': '^GSPC', 'SPY etf': 'SPY', 'QQQ etf': 'QQQ', 'IWM etf': 'IWM'}
BREAK = '2016-12-01'

raw = yf.download(list(TK.values()), start='1995-01-01', progress=False,
                  auto_adjust=False, threads=True)
vol = raw['Volume'] if 'Volume' in raw else raw
m = vol.resample('ME').sum()

print('=' * 74)
print('  MONTHLY VOLUME — mean of the 24 months either side of', BREAK)
print('=' * 74)
print(f'  {"series":<12}{"pre-24m":>16}{"post-24m":>16}{"ratio":>9}')
for lab, tk in TK.items():
    if tk not in m.columns: print(f'  {lab:<12}  unavailable'); continue
    s = m[tk].replace(0, np.nan).dropna()
    pre  = s[:BREAK].tail(24); post = s[BREAK:].head(24)
    if len(pre) < 12 or len(post) < 12: print(f'  {lab:<12}  short sample'); continue
    print(f'  {lab:<12}{pre.mean():>16,.0f}{post.mean():>16,.0f}{post.mean()/pre.mean():>9.2f}x')

print('\n  READ: if SPX steps ~4-5x while SPY/QQQ/IWM do NOT, the SPX series changed')
print('  source and nothing happened in the market. If ALL of them step together,')
print('  it is the vendor. If none step, the step is unique to Jake\'s platform.')

print('\n' + '=' * 74)
print('  YEAR-BY-YEAR, to see whether the shift is a STEP or a TREND')
print('=' * 74)
y = vol.replace(0, np.nan).resample('YE').sum()
cols = [t for t in TK.values() if t in y.columns]
print(f'  {"year":<6}' + ''.join(f'{l:>18}' for l, t in TK.items() if t in cols))
for ts, row in y.loc['2010':'2022'].iterrows():
    print(f'  {ts.year:<6}' + ''.join(f'{row[t]:>18,.0f}' if not np.isnan(row[t]) else f'{"-":>18}'
                                      for t in cols))
print('\n  2017 WAS THE QUIETEST YEAR IN DECADES -- record-low VIX, lowest realised')
print('  vol since the 1960s. If real volume had permanently 5x-ed in Dec 2016,')
print('  2017 could not have been that year. That contradiction is the whole test.')

# ---- is the ratio a clean constant? a units/source change gives a flat multiple
if '^GSPC' in m.columns:
    s = m['^GSPC'].replace(0, np.nan).dropna()
    pre, post = s[:BREAK].tail(36), s[BREAK:].head(36)
    if len(pre) > 12 and len(post) > 12:
        print('\n' + '=' * 74)
        print('  IS THE BREAK A CLEAN MULTIPLE?  (source change => flat ratio)')
        print('=' * 74)
        print(f'  pre  36m: mean {pre.mean():,.0f}  sd/mean {pre.std()/pre.mean():.2f}')
        print(f'  post 36m: mean {post.mean():,.0f}  sd/mean {post.std()/post.mean():.2f}')
        print(f'  ratio of means {post.mean()/pre.mean():.2f}x')
        print('  If the dispersion (sd/mean) is similar either side and only the LEVEL')
        print('  moved, the series was rescaled. If dispersion also changed, something')
        print('  about the underlying activity changed too.')
print('=' * 74)
