# ============================================================================
#  EQUAL-WEIGHT CHECK — verify the "worst relative month on record" claim
#
#  A social post asserted: EW NDX is underperforming EW SPX by 6.8pp in July,
#  EW SPX +2.2% MTD at an ALL-TIME HIGH, EW NDX -4.6% near its mid-May low,
#  "worst relative monthly performance on record", "no month in 20 years worse
#  than 5pp".  The statistics may well be right.  The vault does not take a
#  number from a paraphrase again — that error class cost three load-bearing
#  claims on 7/28 and it is cheap to close.
#
#  Proxies: RSP = Invesco S&P 500 Equal Weight.  QQQE = Direxion NDX-100 Equal
#  Weighted.  Both are ETFs, so MTD price change carries a little fee/tracking
#  drift vs the underlying index — fine for a 6.8pp claim, NOT fine for arguing
#  about 20bp.
# ============================================================================
import subprocess, sys
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'yfinance']); import yfinance as yf
import pandas as pd

T   = ['RSP', 'QQQE', 'SPY', 'QQQ']
LAB = {'RSP': 'EW  S&P 500', 'QQQE': 'EW  NDX 100', 'SPY': 'cap S&P 500', 'QQQ': 'cap NDX 100'}

df = yf.download(T, period='max', progress=False, auto_adjust=True, threads=True)['Close']
if isinstance(df, pd.Series): df = df.to_frame(T[0])
df = df.dropna(how='all')

prior = df.loc[:'2026-06-30']
base, bdate = prior.iloc[-1], prior.index[-1].date()
last, ldate = df.iloc[-1], df.index[-1].date()

print('=' * 70)
print(f'  EQUAL-WEIGHT CHECK   base {bdate} close  ->  last {ldate}')
print('=' * 70)
print(f'\n  {"":13}{"base":>10}{"last":>10}{"MTD%":>9}{"ATH":>10}{"vs ATH%":>9}  ATH date')
for t in T:
    s = df[t].dropna()
    if s.empty: print(f'  {LAB[t]:13}  -- no data'); continue
    b, l, a = float(base[t]), float(last[t]), float(s.max())
    print(f'  {LAB[t]:13}{b:>10,.2f}{l:>10,.2f}{(l/b-1)*100:>+9.2f}'
          f'{a:>10,.2f}{(l/a-1)*100:>+9.2f}  {s.idxmax().date()}')

ew  = (float(last["QQQE"])/float(base["QQQE"]) - float(last["RSP"])/float(base["RSP"])) * 100
cap = (float(last["QQQ"]) /float(base["QQQ"])  - float(last["SPY"])/float(base["SPY"])) * 100
print(f'\n  EQUAL-WEIGHT  NDX - SPX, month to date : {ew:+.2f} pp   (claim: -6.80)')
print(f'  CAP-WEIGHT    NDX - SPX, month to date : {cap:+.2f} pp')
print(f'  EW-minus-CAP spread                    : {ew-cap:+.2f} pp')
print('  If EW is much worse than CAP, the damage is in the SMALL/CROWDED tail of the')
print('  NDX, not in the mega-caps -- which is a momentum unwind, not "profit-taking".')

# ---- the 20-year distribution: is 6.8pp actually unprecedented? ----------
m = df[['RSP', 'QQQE']].dropna().resample('ME').last().pct_change().dropna()
if len(m) > 12:
    rel = (m['QQQE'] - m['RSP']) * 100
    hist = rel.iloc[:-1]                       # exclude the partial current month
    print(f'\n  MONTHLY EW NDX-minus-EW SPX, {hist.index[0].date()} -> {hist.index[-1].date()} '
          f'({len(hist)} complete months)')
    print(f'    worst   {hist.min():+.2f} pp  ({hist.idxmin().date()})')
    print(f'    best    {hist.max():+.2f} pp  ({hist.idxmax().date()})')
    print(f'    st.dev  {hist.std():.2f} pp     months below -5pp: {(hist < -5).sum()}')
    print(f'    current month to date: {rel.iloc[-1]:+.2f} pp  '
          f'= {abs(rel.iloc[-1]/hist.std()):.1f} standard deviations')
    print('\n  NOTE: QQQE launched 2012, so "no month in 20 years" cannot be checked from')
    print('  this series alone. State the ACTUAL span above rather than repeating "20 years".')

print('\n' + '=' * 70)
print('  THE LINE THAT MATTERS IS "vs ATH%" FOR EW S&P 500.')
print('  At ~0%, money leaving tech is ROTATING INSIDE the index, not leaving it —')
print('  containment. When that number turns decisively negative, the rotation has')
print('  become a broad de-rate and the containment case is dead. That is the trigger.')
print('=' * 70)
