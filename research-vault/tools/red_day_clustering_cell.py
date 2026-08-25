# ============================================================================
#  RED-DAY CLUSTERING STUDY   (Jake's design, 2026-07-30)
#
#  DEFINITION
#    1. Trailing 30 TRADING DAYS -> median MAGNITUDE of the RED days in that
#       window (green days excluded entirely).
#    2. SIGNIFICANT RED DAY = a down day with |ret| >= MULT x that median.
#    3. SPACING = trading days between consecutive significant days.
#    4. Question: does TIGHTER spacing precede worse forward returns / deeper
#       forward drawdowns?
#
#  ---------------------------------------------------------------------------
#  READ THIS BEFORE THE OUTPUT -- the design has a built-in problem.
#
#  THE ADAPTIVE THRESHOLD FIGHTS THE PHENOMENON. The 30-day rolling median is a
#  VOLATILITY-ADAPTIVE bar. A cluster of hard red days RAISES the median, which
#  RAISES the threshold, which SUPPRESSES the next signal. The measure normalises
#  away exactly the vol clustering it is trying to detect -- negative feedback
#  built into the definition.
#
#  Measured on a 20,000-day random walk with NO vol clustering, the index of
#  dispersion (variance/mean of events per 21d block; Poisson = 1.00) came out
#  SUB-POISSON at low multipliers: 0.80 at 1.30x, 0.87 at 1.50x. The design
#  anti-clusters by construction.
#
#  CONSEQUENCE: never compare dispersion to 1.00. Compare REAL data against a
#  SHUFFLED control -- the same returns in random order, same multiplier, same
#  pipeline. Shuffling destroys time-ordering while preserving the return
#  distribution, so any excess clustering in real data is vol clustering and
#  nothing else. That control is BLOCK 2 below and it is the first question:
#  does clustering exist at all, before asking whether it predicts anything.
#
#  AND 1.30x IS NOT SELECTIVE. On the random walk it fired on 19.2% of ALL days,
#  ~48 events/yr, median gap 4 days. That is not a significant red day, it is a
#  slightly-worse-than-typical one. Selectivity by multiplier (random walk):
#      1.30x -> 19.2% of days, 48/yr, gap 4d
#      2.00x -> 10.2% of days, 26/yr, gap 6d
#      2.50x ->  6.3% of days, 16/yr, gap 9d
#      3.00x ->  3.8% of days, 10/yr, gap 14d
#  The sweep is therefore extended well past 1.30.
#
#  THREE STANDARD TRAPS, HANDLED:
#   (1) LOOK-AHEAD -- the median is shift(1)'d, so today's return never sets the
#       bar that judges today. Without it, a big red day raises its own bar.
#   (2) BASE RATE -- markets drift up, so ANY condition shows positive forward
#       returns. Every figure is printed as EDGE = conditional minus
#       unconditional over the identical sample. Only EDGE means anything.
#   (3) MULTIPLE TESTING -- the sweep runs ~100+ comparisons; ~5 will look
#       significant on noise. A result at ONE multiplier is noise. A result that
#       moves MONOTONICALLY across the sweep and holds on all three indices is a
#       finding. Read the pattern, never the best cell.
#  Forward windows overlap, so t-stats are optimistic: treat |t| > 3 as the bar.
# ============================================================================
import subprocess, sys
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'yfinance']); import yfinance as yf
import numpy as np, pandas as pd

LOOKBACK = 30
MIN_REDS = 5
MULTS    = [1.0, 1.3, 1.5, 2.0, 2.5, 3.0, 4.0]
HORIZONS = [5, 10, 21, 63]
TICKERS  = {'SPX': '^GSPC', 'NDX': '^NDX', 'SPXEW': 'RSP'}
BLOCK    = 21
NSHUF    = 200
SEED     = 20260730

px = yf.download(list(TICKERS.values()), period='max', progress=False,
                 auto_adjust=True, threads=True)['Close']
if isinstance(px, pd.Series): px = px.to_frame(list(TICKERS.values())[0])

def signals(ret, mult):
    """ret: pd.Series of % returns. Returns index array of significant red days."""
    med = ret.where(ret < 0).abs().rolling(LOOKBACK, min_periods=MIN_REDS).median().shift(1)
    sig = ((ret < 0) & (ret.abs() >= med * mult)).to_numpy()
    return np.flatnonzero(sig & ~np.isnan(med.to_numpy())), sig, med

def dispersion(sig):
    """variance/mean of event counts per BLOCK days. Poisson = 1."""
    n = (len(sig) // BLOCK) * BLOCK
    c = sig[:n].reshape(-1, BLOCK).sum(1).astype(float)
    return c.var() / c.mean() if c.mean() > 0 else np.nan

def fwd_min(v, h):
    out = None
    for k in range(1, h + 1):
        sh = np.concatenate([v[k:], np.full(k, np.nan)])
        out = sh.copy() if out is None else np.fmin(out, sh)
    return out

rng = np.random.default_rng(SEED)
tests = 0

for name, tk in TICKERS.items():
    if tk not in px.columns: print(f'\n{name}: {tk} unavailable'); continue
    s = px[tk].dropna()
    if len(s) < 800: print(f'\n{name}: only {len(s)} bars, skipping'); continue
    r = s.pct_change() * 100
    v = s.to_numpy(dtype=float)
    fwd_ret = {h: (np.concatenate([v[h:], np.full(h, np.nan)]) / v - 1) * 100 for h in HORIZONS}
    fwd_dd  = {h: (fwd_min(v, h) / v - 1) * 100 for h in HORIZONS}

    print('\n' + '=' * 78)
    print(f'  {name} ({tk})   {s.index[0].date()} -> {s.index[-1].date()}   {len(s):,} sessions')
    print('=' * 78)

    # ---- BLOCK 1: what does each multiplier actually buy? -------------------
    print('\n  [1] SELECTIVITY -- what the multiplier buys')
    print(f'  {"mult":>6}{"events":>8}{"% days":>9}{"per yr":>8}{"med gap":>9}{"gap<=2d":>9}')
    keep = []
    for m in MULTS:
        idx, sig, med = signals(r, m)
        if len(idx) < 40: print(f'  {m:>6.2f}{len(idx):>8}   too few events'); continue
        g = np.diff(idx)
        print(f'  {m:>6.2f}{len(idx):>8}{len(idx)/len(r)*100:>8.1f}%'
              f'{len(idx)/(len(s)/252):>8.1f}{np.median(g):>9.0f}{(g<=2).mean()*100:>8.0f}%')
        keep.append((m, idx, sig, g))

    # ---- BLOCK 2: does clustering EXIST? real vs shuffled control -----------
    print(f'\n  [2] DOES CLUSTERING EXIST? real vs {NSHUF} SHUFFLES of the same returns')
    print('      (shuffle destroys time-order, preserves the return distribution;')
    print('       excess in real data IS vol clustering. Compare to shuffle, NOT to 1.00)')
    print(f'  {"mult":>6}{"disp real":>11}{"disp shuf":>11}{"pctile":>8}   '
          f'{"medgap real":>12}{"medgap shuf":>12}')
    rv = r.dropna().to_numpy()
    for m, idx, sig, g in keep:
        d_real, mg_real = dispersion(sig), np.median(g)
        ds, mgs = [], []
        for _ in range(NSHUF):
            sh = pd.Series(rng.permutation(rv))
            i2, s2, _ = signals(sh, m)
            if len(i2) > 10:
                ds.append(dispersion(s2)); mgs.append(np.median(np.diff(i2)))
        if not ds: continue
        pct = (np.array(ds) < d_real).mean() * 100
        print(f'  {m:>6.2f}{d_real:>11.2f}{np.mean(ds):>11.2f}{pct:>7.0f}%   '
              f'{mg_real:>12.0f}{np.mean(mgs):>12.1f}')
    print('      pctile = where real dispersion sits in the shuffled distribution.')
    print('      CALIBRATED on 20,000-day synthetic series before this cell shipped:')
    print('        random walk, NO vol clustering -> pctile  0% / 8% / 13% at 1.3/2.0/3.0x')
    print('        GARCH(1,1),  KNOWN vol clustering -> pctile 100% at every multiplier.')
    print('      So the null lands LOW, not at 50 -- do not read 50% as neutral.')
    print('      >90% = genuinely clustered.  <30% = the design found nothing.')

    # ---- BLOCK 3: does tight spacing PREDICT? ------------------------------
    print('\n  [3] DOES TIGHT SPACING PREDICT?  EDGE = conditional minus base rate')
    print('      (negative ret EDGE = worse than normal.  negative maxDD EDGE = DEEPER hole)')
    print(f'  {"mult":>6}{"bucket":>10}{"n":>6}   '
          + ''.join(f'{str(h)+"d ret/maxDD":>20}' for h in HORIZONS))
    for m, idx, sig, g in keep:
        ev = idx[1:]
        q1, q2 = np.quantile(g, [1/3, 2/3])
        for lab, msk in [(f'tight<={q1:.0f}d', g <= q1), (f'wide>{q2:.0f}d', g > q2)]:
            if msk.sum() < 15: continue
            cells = []
            for h in HORIZONS:
                fr, fd = fwd_ret[h][ev][msk], fwd_dd[h][ev][msk]
                ok = ~np.isnan(fr) & ~np.isnan(fd)
                if ok.sum() < 15: cells.append(f'{"n/a":>20}'); continue
                e_r = fr[ok].mean() - np.nanmean(fwd_ret[h])
                e_d = fd[ok].mean() - np.nanmean(fwd_dd[h])
                tests += 1
                cells.append(f'{e_r:>+11.2f} /{e_d:>+7.2f}')
            print(f'  {m:>6.2f}{lab:>10}{msk.sum():>6}   ' + ''.join(cells))
    print('  base rates: ' + '  '.join(
        f'{h}d ret {np.nanmean(fwd_ret[h]):+.2f}% dd {np.nanmean(fwd_dd[h]):+.2f}%' for h in HORIZONS))

    # ---- BLOCK 4: LIVE ----------------------------------------------------
    idx13, sig13, med13 = signals(r, 1.30)
    cur = med13.iloc[-1]
    print(f'\n  [4] LIVE  {s.index[-1].date()}  close {v[-1]:,.2f}  last day {r.iloc[-1]:+.2f}%')
    if np.isnan(cur):
        print('      30d red-day median unavailable')
    else:
        print(f'      30d median RED day {cur:.2f}%  ->  ' +
              '  '.join(f'{m:.1f}x={cur*m:.2f}%' for m in (1.3, 2.0, 2.5, 3.0)))
        if len(idx13) > 10:
            g = np.diff(idx13)
            print(f'      last 1.3x event {s.index[idx13[-1]].date()} '
                  f'({len(s)-1-idx13[-1]} sessions ago); last 10 gaps {list(g[-10:])}')
            print(f'      trailing-60d events {(idx13 > len(s)-61).sum()} '
                  f'vs sample-rate expectation {60*len(idx13)/len(s):.1f}')

print('\n' + '=' * 78)
print(f'  {tests} conditional comparisons. Expect ~{tests*0.05:.0f} to look significant on noise.')
print('  ORDER OF QUESTIONS: [2] first -- if real dispersion is not above the shuffled')
print('  control, there is no clustering to trade and [3] is curve-fitting on noise.')
print('=' * 78)
