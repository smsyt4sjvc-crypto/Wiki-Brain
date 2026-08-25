# ============================================================================
#  ANCHORED VWAP — is it a "SENTIMENT" statistic, or a price average with a
#  story attached?   (built 2026-07-30 for Jake's question)
#
#  THE CLAIM: AVWAP = "the average cost basis of everyone who transacted since
#  the anchor," so price above it means the average buyer is in profit, and that
#  makes it sentiment. It is quoted as "the ultimate sentiment-driven statistic."
#
#  READ THIS BEFORE THE OUTPUT — three problems, and the cell tests all three.
#
#  (1) THE ANCHOR IS A FREE PARAMETER CHOSEN AFTER SEEING THE CHART. There are
#      hundreds of plausible anchors (every swing high/low, every Fed day, every
#      earnings). With enough of them ONE IS ALWAYS NEAR PRICE. Nobody publishes
#      the anchors that failed. => THIS CELL USES ONLY MECHANICAL ANCHORS,
#      defined by a rule, computed from price, never eyeballed.
#
#  (2) "AVERAGE COST BASIS OF PARTICIPANTS" IS FALSE FOR SPY SPECIFICALLY.
#      SPY volume is dominated by intraday churn that ends the day flat; it has
#      daily creation/redemption at NAV that never prints on tape; ES futures
#      dwarf it; and option-hedging flow transacts without holding a view.
#      Volume in SPY is not position-taking, so the denominator is not "people
#      who own it." The interpretation that makes AVWAP a SENTIMENT measure is
#      the part that does not survive SPY's market structure.
#
#  (3) IT IS A DETERMINISTIC FUNCTION OF PRICE AND VOLUME. There is no sentiment
#      input. Sentiment is put/call, AAII, positioning, flows. This is arithmetic.
#
#  THE THREE CONTROLS THAT DECIDE IT
#   [A] vs a plain SMA over the IDENTICAL window. If AVWAP does not beat it, the
#       volume weighting adds nothing and "cost basis" is decoration.
#   [B] *** SHUFFLED VOLUME — THE DECISIVE TEST. *** Recompute AVWAP with the
#       volume series randomly permuted. If the signal SURVIVES random volume,
#       then volume was never doing any work and AVWAP is a price average.
#       (Same logic as the shuffled control in red_day_clustering_cell.py.)
#   [C] EDGE vs the unconditional base rate over the identical sample. Markets
#       drift up; ANY condition looks positive. Only EDGE means anything.
#
#  ~60 conditional comparisons here -> expect ~3 to look significant on noise.
#  READ THE PATTERN ACROSS ANCHORS, NOT THE BEST CELL.
# ============================================================================
import subprocess, sys
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'yfinance']); import yfinance as yf
import numpy as np, pandas as pd

TICKER   = 'SPY'
START    = '1995-01-01'
HORIZONS = [5, 21, 63]
NSHUF    = 200
SEED     = 20260730
DD_TRIG  = 0.05          # drawdown depth that defines a "trough" anchor

df = yf.download(TICKER, start=START, progress=False, auto_adjust=False)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df = df.dropna(subset=['Close', 'Volume'])
c = df['Close'].to_numpy(float)
tp = ((df['High'] + df['Low'] + df['Close']) / 3).to_numpy(float)   # typical price
v = df['Volume'].to_numpy(float)
n = len(c)
print(f'{TICKER}  {df.index[0].date()} -> {df.index[-1].date()}  {n:,} sessions')

# ---------------- MECHANICAL ANCHORS (rule-defined, never eyeballed) --------
def anchors_ath():
    rm = np.maximum.accumulate(c);  return c >= rm - 1e-9
def anchors_52wlow():
    s = pd.Series(c).rolling(252, min_periods=252).min().to_numpy()
    return (c <= s + 1e-9) & ~np.isnan(s)
def anchors_quarter():
    q = df.index.to_period('Q'); return np.r_[True, q[1:] != q[:-1]]
def anchors_dd_trough():
    """min point of each episode where drawdown from the running peak exceeded DD_TRIG"""
    rm = np.maximum.accumulate(c); dd = c / rm - 1
    out = np.zeros(n, bool); i = 0
    while i < n:
        if dd[i] <= -DD_TRIG:
            j = i
            while j < n and dd[j] < 0: j += 1        # episode runs until a new high
            k = i + int(np.argmin(c[i:j]))
            out[k] = True; i = j
        else:
            i += 1
    return out

ANCHORS = {'ATH': anchors_ath(), '52w-low': anchors_52wlow(),
           'quarter-start': anchors_quarter(), f'-{DD_TRIG:.0%} trough': anchors_dd_trough()}

# ---------------- AVWAP from the MOST RECENT anchor of each type ------------
def last_anchor_idx(flags):
    idx = np.full(n, -1, int); last = -1
    for i in range(n):
        if flags[i]: last = i
        idx[i] = last
    return idx

def avwap(flags, vol):
    a = last_anchor_idx(flags)
    cpv = np.concatenate([[0.0], np.cumsum(tp * vol)])
    cv  = np.concatenate([[0.0], np.cumsum(vol)])
    out = np.full(n, np.nan)
    ok = a >= 0
    num = cpv[np.arange(n) + 1] - cpv[a]
    den = cv[np.arange(n) + 1] - cv[a]
    out[ok] = np.where(den[ok] > 0, num[ok] / den[ok], np.nan)
    return out, a

def sma_matched(flags):
    """plain average of typical price over the IDENTICAL window -- the volume control"""
    a = last_anchor_idx(flags)
    ctp = np.concatenate([[0.0], np.cumsum(tp)])
    out = np.full(n, np.nan); ok = a >= 0
    ln = (np.arange(n) - a + 1).astype(float)
    out[ok] = (ctp[np.arange(n) + 1] - ctp[a])[ok] / ln[ok]
    return out

# ---------------- forward returns ------------------------------------------
FR = {h: (np.concatenate([c[h:], np.full(h, np.nan)]) / c - 1) * 100 for h in HORIZONS}
BASE = {h: np.nanmean(FR[h]) for h in HORIZONS}

def edge(mask, h):
    x = FR[h][mask]; x = x[~np.isnan(x)]
    return (x.mean() - BASE[h], len(x)) if len(x) >= 30 else (np.nan, len(x))

print('\nEDGE = conditional mean MINUS unconditional mean, same sample. Only EDGE counts.')
print('base rates: ' + '  '.join(f'{h}d {BASE[h]:+.2f}%' for h in HORIZONS))

rng = np.random.default_rng(SEED)
print('\n' + '=' * 96)
print('  [A] ABOVE vs BELOW the line — AVWAP against an IDENTICAL-WINDOW SMA')
print('=' * 96)
print(f'  {"anchor":<16}{"measure":<10}{"side":<8}{"n":>7}   ' + ''.join(f'{str(h)+"d EDGE":>12}' for h in HORIZONS))
store = {}
for name, flags in ANCHORS.items():
    av, a = avwap(flags, v)
    sm = sma_matched(flags)
    store[name] = (flags, av, a)
    for lab, line in (('AVWAP', av), ('SMA', sm)):
        good = ~np.isnan(line)
        for side, m in (('above', good & (c > line)), ('below', good & (c < line))):
            cells = ''.join((lambda e, k: f'{e:>+12.2f}' if not np.isnan(e) else f'{"n/a":>12}')(*edge(m, h))
                            for h in HORIZONS)
            print(f'  {name:<16}{lab:<10}{side:<8}{int(m.sum()):>7}   {cells}')
    print()
print('  READ: if the AVWAP rows do not BEAT the SMA rows, volume weighting adds nothing')
print('  and the "average cost basis" story is decoration on a moving average.')

print('\n' + '=' * 96)
print(f'  [B] *** THE DECISIVE TEST *** — AVWAP on {NSHUF} SHUFFLES of the volume series')
print('=' * 96)
print('  If randomising volume leaves the edge intact, VOLUME NEVER MATTERED.')
print(f'  {"anchor":<16}{"horizon":<9}{"real":>9}{"shuffled mean":>15}{"pctile":>9}   verdict')
for name, (flags, av, a) in store.items():
    real_mask = ~np.isnan(av) & (c > av)
    for h in HORIZONS:
        e_real, _ = edge(real_mask, h)
        if np.isnan(e_real): continue
        es = []
        for _ in range(NSHUF):
            av2, _ = avwap(flags, rng.permutation(v))
            m2 = ~np.isnan(av2) & (c > av2)
            e2, _ = edge(m2, h)
            if not np.isnan(e2): es.append(e2)
        if not es: continue
        pct = (np.array(es) < e_real).mean() * 100
        verdict = 'volume MATTERS' if pct >= 95 else ('volume is NOISE' if pct <= 80 else 'ambiguous')
        print(f'  {name:<16}{str(h)+"d":<9}{e_real:>+9.2f}{np.mean(es):>+15.2f}{pct:>8.0f}%   {verdict}')
print('  A real "cost basis" effect should sit ABOVE ~95% of shuffles. Anything below')
print('  ~80% means the same edge appears with RANDOM volume => it is a price average.')

print('\n' + '=' * 96)
print('  [C] DISTANCE from AVWAP as a continuous signal (quintiles) — ATH anchor')
print('=' * 96)
flags, av, a = store['ATH']
d = (c / av - 1) * 100
ok = ~np.isnan(d)
qs = np.nanquantile(d[ok], [.2, .4, .6, .8])
print(f'  {"bucket":<22}{"n":>7}   ' + ''.join(f'{str(h)+"d EDGE":>12}' for h in HORIZONS))
lo = -np.inf
for i, hi in enumerate(list(qs) + [np.inf]):
    m = ok & (d > lo) & (d <= hi)
    cells = ''.join((lambda e, k: f'{e:>+12.2f}' if not np.isnan(e) else f'{"n/a":>12}')(*edge(m, h))
                    for h in HORIZONS)
    print(f'  Q{i+1} {lo:>+7.1f}%..{hi:>+7.1f}%{int(m.sum()):>7}   {cells}')
    lo = hi
print('  A real level effect is MONOTONIC across quintiles. A single hot bucket is noise.')

print('\n' + '=' * 96)
print(f'  [D] LIVE — {TICKER} {df.index[-1].date()}  close {c[-1]:,.2f}')
print('=' * 96)
print(f'  {"anchor":<18}{"anchored":<13}{"AVWAP":>10}{"dist":>9}{"SMA(same win)":>15}{"sessions":>10}')
for name, (flags, av, aidx) in store.items():
    if np.isnan(av[-1]): continue
    sm = sma_matched(flags)
    print(f'  {name:<18}{str(df.index[aidx[-1]].date()):<13}{av[-1]:>10.2f}'
          f'{(c[-1]/av[-1]-1)*100:>+8.2f}%{sm[-1]:>15.2f}{n-1-aidx[-1]:>10}')
print('\n  NOTE the AVWAP vs SMA columns: as the anchor recedes the two CONVERGE, because')
print('  a long-anchored AVWAP is a nearly-horizontal line. The "signal" decays into a')
print('  static level dressed up as a dynamic one.')
print('=' * 96)
