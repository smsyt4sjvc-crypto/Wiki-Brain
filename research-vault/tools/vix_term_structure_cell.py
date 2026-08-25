
# ============================================================================
#  VIX TERM STRUCTURE — "CALM or COILED?"
#  Settles the 7/28 disagreement: is the low VIX genuine calm (Claude's read)
#  or pre-event paralysis with thin hedges (Jake's read, backed by Mag-7 RVOL)?
#  Run BEFORE the 11:00am PT FOMC.  Token-free. ONE batched download + retries.
# ============================================================================
import subprocess, sys, time
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance']); import yfinance as yf
import numpy as np, pandas as pd

CURVE = [('^VIX9D','VIX9D   9-day'), ('^VIX','VIX    30-day'),
         ('^VIX3M','VIX3M   3-month'), ('^VIX6M','VIX6M   6-month')]
EXTRA = [('^VVIX','VVIX   vol-of-vol'), ('^SKEW','SKEW   tail bid')]
MAG7  = ['NVDA','MSFT','AAPL','GOOGL','AMZN','META','TSLA']
ALL   = [t for t,_ in CURVE] + [t for t,_ in EXTRA] + ['^GSPC'] + MAG7

def fetch(tickers, period='1y', tries=3):
    """One batched, THREADED call, retried with backoff. Returns {ticker: Series}.
    Threaded on purpose: serial fetching 13 tickers behind a throttling Yahoo
    turns a 5-second cell into a multi-minute hang. Partial results are kept."""
    last, best = None, {}
    for i in range(tries):
        try:
            df = yf.download(tickers, period=period, progress=False,
                             auto_adjust=True, threads=True)['Close']
            if isinstance(df, pd.Series): df = df.to_frame(tickers[0])
            out = {c: df[c].dropna() for c in df.columns if df[c].dropna().size > 2}
            if len(out) > len(best): best = out          # keep the best partial
            if len(out) >= len(tickers) - 1: return out  # good enough, stop early
            last = f'{len(out)}/{len(tickers)} tickers returned'
        except Exception as e:
            last = e
        if i < tries-1:
            print(f'  ...fetch attempt {i+1}: {last}; retrying in {2**i}s')
            time.sleep(2**i)
    if best:
        print(f'  !! PARTIAL DATA after {tries} attempts ({len(best)}/{len(tickers)} tickers).'
              f' Sections below will say what is missing.')
        return best
    print(f'  !! ALL {tries} FETCH ATTEMPTS FAILED: {last}')
    return {}

print('='*66); print('  VIX TERM STRUCTURE — calm or coiled?'); print('='*66)
D = fetch(ALL)
if not D:
    print('\n  NO DATA RETURNED. Yahoo is blocking or the network is down.')
    print('  Re-run in 60s. If it persists, run the cell from a fresh Colab runtime.')
    raise SystemExit

def last(t):
    s = D.get(t)
    return (float(s.iloc[-1]), s) if s is not None and len(s) else (None, None)

# ---------- 1. the curve ----------
lv = {}
print('\n### THE CURVE (spot levels)')
for t, lab in CURVE + EXTRA:
    v, s = last(t)
    if v is None: print(f'  {lab:18} -- NOT AVAILABLE'); continue
    lv[t] = v
    ch = (v/float(s.iloc[-2])-1)*100 if len(s) > 1 else float('nan')
    print(f'  {lab:18}{v:>8.2f}   {ch:>+7.2f}%    (as of {s.index[-1].date()})')

# ---------- 2. THE DISCRIMINATOR ----------
print('\n### ★ THE DISCRIMINATOR  (VIX9D / VIX)')
if '^VIX9D' in lv and '^VIX' in lv:
    r = lv['^VIX9D']/lv['^VIX']
    a, b = D['^VIX9D'], D['^VIX']
    hs = (a/b.reindex(a.index).ffill()).dropna()
    pct = float((hs < r).mean()*100)
    print(f'  ratio {r:.3f}    ({pct:.0f}th pctile of the last 12 months)')
    if   r >= 1.05: v='COILED — near-dated event premium priced. JAKE: hedges thin, reaction unabsorbed.'
    elif r >= 1.00: v='MILDLY COILED — front end bid. Leans Jake.'
    elif r >= 0.92: v='NORMAL — no event premium priced. Leans Claude (genuine calm).'
    else:           v='COMPLACENT — front end unusually cheap vs 30d. Strongest form of the calm read.'
    print(f'  VERDICT: {v}')
else:
    print('  -- VIX9D or VIX missing; discriminator NOT computed.')

print('\n### SLOPE  (VIX / VIX3M)')
if '^VIX' in lv and '^VIX3M' in lv:
    r2 = lv['^VIX']/lv['^VIX3M']
    print(f'  ratio {r2:.3f}   ->  ' + ('BACKWARDATION = real stress, not just event risk' if r2 > 1.0
          else ('FLAT/kinked — transition' if r2 > 0.95 else 'CONTANGO = normal, no systemic bid')))
else:
    print('  -- VIX or VIX3M missing; slope NOT computed.')

# ---------- 3. is the low VIX just DISPERSION arithmetic? ----------
print('\n### ★ CORRELATION CHECK — is the low VIX just dispersion math?')
def rvol(s, n=10):
    lr = np.log(s/s.shift(1)).dropna()
    return float(lr.tail(n).std()*np.sqrt(252)*100) if len(lr) >= n else None
spx = D.get('^GSPC'); idx_v = rvol(spx) if spx is not None else None
comp = []
for t in MAG7:
    s = D.get(t); v = rvol(s) if s is not None else None
    if v is None: print(f'    {t:6}  -- n/a'); continue
    comp.append(v); print(f'    {t:6}{v:>7.1f}%')
if idx_v is None:
    print('    -- SPX history missing; correlation check NOT computed.')
elif not comp:
    print('    -- no Mag-7 history; correlation check NOT computed.')
else:
    avg = sum(comp)/len(comp); ratio = idx_v/avg
    print(f'    {"SPX":6}{idx_v:>7.1f}%   |  Mag-7 avg {avg:.1f}%  ({len(comp)}/7)  |  index/component = {ratio:.2f}')
    print('    ' + ('-> LOW ratio = correlation collapse. The low VIX is substantially DISPERSION\n'
                    '       ARITHMETIC, not a judgment that risk is contained. (Claude conceded 7/28.)'
                    if ratio < 0.55 else
                    '-> ratio normal/high = components moving TOGETHER. A low VIX here WOULD be a real\n'
                    '       judgment about risk rather than an artifact.'))

# ---------- 4. variance risk premium ----------
print('\n### ★ VARIANCE RISK PREMIUM  (VIX vs realised SPX vol)')
if idx_v is not None and '^VIX' in lv:
    vrp = lv['^VIX'] - idx_v
    print(f'  VIX {lv["^VIX"]:.2f}  -  realised10d {idx_v:.1f}  =  {vrp:+.1f} pts')
    print('  ' + ("-> NEGATIVE: implied is BELOW realised. Options cheap vs what the tape is doing.\n"
                  "     Strongest quantitative form of Jake's 'the hedge is underpriced' case."
                  if vrp < 0 else
                  '-> positive: normal insurance premium. Hedges are not obviously cheap.'))
else:
    print('  -- VIX or SPX history missing; VRP NOT computed.')

print('\n'+'='*66)
print('  HOW TO READ IT')
print('  VIX9D/VIX >= 1.00       -> COILED (event premium, thin hedges)  = Jake')
print('  VIX9D/VIX <  0.92       -> CALM   (no event premium priced)     = Claude')
print('  VIX/VIX3M  >  1.00      -> BACKWARDATION = real stress on top of event risk')
print('  index/component < 0.55  -> the low VIX is dispersion math, not a risk judgment')
print('  VRP negative            -> implied below realised = the hedge is genuinely cheap')
print('  COUNTER (do not skip): the base rate is VIX CRUSHING after the event, not popping.')
print('  Coiled pays on MAGNITUDE either direction, not on direction. In-line = expires worthless.')
print('='*66)
