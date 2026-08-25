# ============================================================================
#  WHAT HAPPENS WHEN THE 30Y GOES ABOVE 5%?
#
#  READ THIS BEFORE THE OUTPUT -- the question as posed cannot be answered.
#
#  (1) 5% IS A ROUND NUMBER, NOT AN ECONOMIC THRESHOLD. Nothing activates at
#      5.00% that does not at 4.95%. Any result keyed to a round level is a
#      data-mined threshold, not a mechanism.
#
#  (2) THE SAMPLE INVERTS DEPENDING ON WHERE YOU START. The 30Y was above 5%
#      almost CONTINUOUSLY from 1977 to 1998 -- a window containing the greatest
#      equity bull run on record. Include it and ">5%" is bullish by construction.
#      Restrict to the post-2000 low-rate regime and you have roughly four
#      episodes: 2000, 2006-07, Oct-2023, mid-2025. Two were followed by
#      catastrophes and two by large rallies. n=4, split 2-2, is a coin flip.
#
#  (3) IT IS A STATE, NOT A TRIGGER. Per the vault's standing WARNING-vs-TRIGGER
#      rule, a level condition persists for years and times nothing. "30Y above
#      5%" is exactly the kind of unfalsifiable marker that rule exists to ban.
#
#  WHAT IS ACTUALLY ANSWERABLE -- and this cell tests all of it:
#      A. the naive level (shown so its uselessness is visible, not asserted)
#      B. 30Y at an N-YEAR HIGH -- relative, not absolute
#      C. SPEED -- change over 63 trading days. Rate of change breaks things;
#         the same level reached slowly does not.
#      D. THE DRIVER, which is the part that matters: is the rise in BREAKEVENS
#         (inflation) or REAL yields (term premium / growth)? And is the curve
#         BEAR-STEEPENING or bear-flattening?
#
#  Every figure is printed against the unconditional base rate over the same
#  sample. Forward MAX DRAWDOWN is reported alongside forward return, because
#  "what happens" is a path question, not a return question.
# ============================================================================
import subprocess, sys, io, urllib.request
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'yfinance']); import yfinance as yf
import numpy as np, pandas as pd

FRED = 'https://fred.stlouisfed.org/graph/fredgraph.csv?id={}'
def fred(series):
    raw = urllib.request.urlopen(FRED.format(series), timeout=30).read().decode()
    df = pd.read_csv(io.StringIO(raw))
    df.columns = ['date', series]
    df['date'] = pd.to_datetime(df['date'])
    df[series] = pd.to_numeric(df[series], errors='coerce')
    return df.set_index('date')[series].dropna()

print('pulling FRED: DGS30, DGS10, DGS2, T10YIE ...')
y30, y10, y2 = fred('DGS30'), fred('DGS10'), fred('DGS2')
try:    be = fred('T10YIE')                      # 10y breakeven, 2003+
except Exception: be = pd.Series(dtype=float)

spx = yf.download('^GSPC', start='1962-01-01', progress=False, auto_adjust=True)['Close']
if isinstance(spx, pd.DataFrame): spx = spx.iloc[:, 0]

d = pd.DataFrame({'y30': y30, 'y10': y10, 'y2': y2, 'spx': spx.reindex(y30.index)}).dropna(subset=['y30'])
d['spx'] = d['spx'].ffill()
d = d.dropna(subset=['spx'])
d['be'] = be.reindex(d.index).ffill()
d['real30'] = d['y30'] - d['be']
d['s2s30'] = d['y30'] - d['y2']

HOR = [21, 63, 126, 252]
v = d['spx'].to_numpy(dtype=float)
def fwd_min(a, h):
    out = None
    for k in range(1, h + 1):
        sh = np.concatenate([a[k:], np.full(k, np.nan)])
        out = sh.copy() if out is None else np.fmin(out, sh)
    return out
FR = {h: (np.concatenate([v[h:], np.full(h, np.nan)]) / v - 1) * 100 for h in HOR}
FD = {h: (fwd_min(v, h) / v - 1) * 100 for h in HOR}

def show(label, mask, note=''):
    n = int(mask.sum())
    if n < 30:
        print(f'  {label:<34}{n:>6}   too few observations'); return
    cells = []
    for h in HOR:
        fr, fd = FR[h][mask], FD[h][mask]
        ok = ~np.isnan(fr) & ~np.isnan(fd)
        if ok.sum() < 30: cells.append(f'{"n/a":>19}'); continue
        er = fr[ok].mean() - np.nanmean(FR[h])
        ed = fd[ok].mean() - np.nanmean(FD[h])
        cells.append(f'{er:>+10.2f} /{ed:>+7.2f}')
    print(f'  {label:<34}{n:>6}   ' + ''.join(cells) + ('   ' + note if note else ''))

hdr = f'  {"condition":<34}{"days":>6}   ' + ''.join(f'{str(h)+"d ret/maxDD EDGE":>19}' for h in HOR)

print(f'\nsample: {d.index[0].date()} -> {d.index[-1].date()}  ({len(d):,} daily obs)')
print(f'30Y today: {d["y30"].iloc[-1]:.2f}%   2s30s: {d["s2s30"].iloc[-1]:+.2f}pp'
      + (f'   10y breakeven: {d["be"].iloc[-1]:.2f}%' if not np.isnan(d['be'].iloc[-1]) else ''))
print('\nEDGE = conditional mean MINUS unconditional mean, same sample. Only EDGE means anything.')
print('Negative maxDD edge = a DEEPER hole than normal.')

print('\n' + '='*110)
print('  [A] THE NAIVE LEVEL -- shown so its uselessness is VISIBLE')
print('='*110); print(hdr)
show('30Y > 5%  (full sample)', (d['y30'] > 5).to_numpy())
post2000 = d.index >= '2000-01-01'
show('30Y > 5%  (2000+ only)', ((d['y30'] > 5) & post2000).to_numpy(), '<-- note how the sign flips')
print('  A condition whose sign depends on the start date is a start-date artifact.')

print('\n' + '='*110)
print('  [B] RELATIVE, NOT ABSOLUTE -- 30Y at an N-year high')
print('='*110); print(hdr)
for yrs in (1, 3, 5, 10):
    hi = d['y30'].rolling(252*yrs, min_periods=252).max()
    show(f'30Y at a {yrs}-year high', (d['y30'] >= hi - 1e-9).to_numpy())

print('\n' + '='*110)
print('  [C] SPEED -- it is the rate of change that breaks things, not the level')
print('='*110); print(hdr)
chg = (d['y30'] - d['y30'].shift(63)) * 100      # bp over ~3 months
for bp in (50, 75, 100, 150):
    show(f'30Y +{bp}bp in 63 trading days', (chg >= bp).to_numpy())
show('30Y +75bp AND above 5%', ((chg >= 75) & (d['y30'] > 5)).to_numpy())

print('\n' + '='*110)
print('  [D] THE DRIVER -- the only split that carries a mechanism')
print('='*110); print(hdr)
d2s30 = (d['s2s30'] - d['s2s30'].shift(63)) * 100
show('rising 30Y + BEAR STEEPENING',  ((chg >= 50) & (d2s30 > 0)).to_numpy())
show('rising 30Y + bear FLATTENING',  ((chg >= 50) & (d2s30 <= 0)).to_numpy())
if d['be'].notna().sum() > 500:
    dbe   = (d['be'] - d['be'].shift(63)) * 100
    dreal = (d['real30'] - d['real30'].shift(63)) * 100
    show('rising 30Y, BREAKEVEN-driven', ((chg >= 50) & (dbe > dreal)).to_numpy(), '(inflation)')
    show('rising 30Y, REAL-yield-driven', ((chg >= 50) & (dreal >= dbe)).to_numpy(), '(term premium/growth)')
else:
    print('  breakeven series too short for the driver split')

print('\n' + '='*110)
print('  base rates: ' + '  '.join(f'{h}d ret {np.nanmean(FR[h]):+.2f}% dd {np.nanmean(FD[h]):+.2f}%' for h in HOR))
print('  ~40 conditional comparisons -> expect ~2 to look significant on noise alone.')
print('  READ THE PATTERN ACROSS ROWS, NOT THE BEST CELL. A result that holds as you')
print('  tighten the speed threshold is real; one that appears at a single cut is not.')
print('='*110)
