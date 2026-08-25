# ============================================================================
#  PERMUTATION TEST — is the 19% survivor rate REAL, or is it what noise does?
#
#  ⛔ WHY THIS CELL EXISTS: dip_universe_screen_cell.py printed
#         "96 of 500 names (19%). A pure-noise universe would leave ~12%."
#     THE ~12% WAS A GUESS. I derived it as 0.5^4 = 6.25% and doubled it by hand
#     because it felt too tight. That is not a null distribution, it is a vibe
#     with a decimal point, and it was load-bearing for the entire screen.
#
#  THE ONLY HONEST WAY TO GET THE NULL: run the EXACT SAME PIPELINE on data with
#  the same return distribution but NO relationship between a dip and what
#  follows it. Shuffle returns, rebuild the price path, re-screen, count
#  survivors. Repeat 100x. THAT distribution is the noise floor.
#
#  ⚠️⚠️ THREE NULLS, AND THE CHOICE OF NULL IS THE WHOLE ARGUMENT. Each one
#  destroys something real, and what it destroys is what it will FLATTER:
#
#   [IID]   shuffle each name's daily returns independently.
#           DESTROYS: volatility clustering AND cross-name correlation.
#           ⚠️ FLATTERS THE RESULT TWICE OVER. On synthetic Gaussian walks this
#           null measures ~11% — which is why my 12% guess LOOKED right. It was
#           right about the wrong question. Reported for contrast only.
#
#   [BLOCK] moving-block bootstrap, 21-day blocks, each name independently.
#           KEEPS: volatility clustering inside each block.
#           DESTROYS: cross-name correlation.
#           ⚠️ STILL FLATTERS. See [SYNC].
#
#   [SYNC]  ★ THE ONE TO JUDGE BY ★ — the SAME 21-day calendar reordering applied
#           to EVERY name at once. Keeps volatility clustering AND the entire
#           cross-sectional correlation structure. Only the TIME-ORDERING of
#           market-wide events is destroyed.
#           WHY THIS IS THE REAL TEST: the 500 names are NOT 500 independent
#           experiments. They all dipped together in Mar-2020 and recovered
#           together. Under a per-name shuffle the null universe has NO shared
#           crashes, so its survivor count has FAR less spread than the real
#           universe's — which makes the p-value look better than it is, purely
#           as an artifact. [SYNC] gives the null the same shared-crash structure
#           the real data has. IF THE REAL RESULT DOES NOT BEAT [SYNC], THE
#           SCREEN IS MEASURING "MARCH 2020 RECOVERED," NOT "DIPS MEAN-REVERT."
#
#  THREE QUESTIONS, and the count is the weakest of them:
#   Q1 SURVIVOR RATE   — does 19% beat the null rate?            (the headline)
#   Q2 TOP-OF-RANKING  — does the BEST real e63 beat the best null e63? The max
#                        of 500 random numbers is large. This is the test the
#                        14-name shortlist actually has to pass to be tradeable.
#   Q3 ETF SUBGROUP    — is ETFs-at-44% real? It is the finding with a mechanism
#                        (an index cannot have idiosyncratic bad news), so it is
#                        the one most worth defending or killing.
#
#  ⚠️ WHAT A PASS WOULD *NOT* MEAN. It does not fix survivorship (this is TODAY's
#     S&P 500; the bankruptcies are absent from the real run AND from every
#     shuffle, so the bias CANCELS out of the p-value and SURVIVES INTACT in the
#     level). And it says nothing about money: measured 7/31, $226 of expected
#     dip edge against an $1,805 theta bill. A statistically real edge that small
#     still loses money in long options.
#     THIS CELL TESTS "REAL OR NOT." IT DOES NOT TEST "PROFITABLE OR NOT."
# ============================================================================
import subprocess, sys, io, urllib.request, time
try:
    import yfinance as yf; import pandas as pd; import numpy as np
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas','lxml'])
    import yfinance as yf; import pandas as pd; import numpy as np

# ---- must MATCH dip_universe_screen_cell.py exactly, or the null is not the null
LOOKBACK, THRESH, COOL = 63, 0.08, 21
SPLIT   = pd.Timestamp('2021-01-01')
MIN_N   = 25
START   = '2015-01-01'
NSHUF   = 100         # shuffles per null -> p-value resolution 1/101 = 0.0099
BLOCK   = 21          # trading-month blocks
SEED    = 20260731
ETFS    = 'SPY QQQ IWM MDY SOXX SMH XLK XLF XLE XLV XLI XLP XLU XLB XLRE XBI KRE ITB GLD SLV TLT HYG'.split()
UA      = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

# ---- REUSE the price frame if dip_universe_screen_cell.py already ran ----------
if isinstance(globals().get('px'), pd.DataFrame) and globals()['px'].shape[1] > 400:
    print(f'reusing px already in memory: {px.shape[1]} series x {px.shape[0]} rows\n')
    if not isinstance(globals().get('sectors'), dict): sectors = {}
else:
    def get_constituents():
        try:
            req = urllib.request.Request('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', headers=UA)
            t = pd.read_html(io.BytesIO(urllib.request.urlopen(req, timeout=25).read()))[0]
            return dict(zip(t['Symbol'].str.replace('.','-',regex=False), t['GICS Sector'])), 'wikipedia'
        except Exception as e:
            print('wiki failed (', e, ') -> github fallback')
        req = urllib.request.Request('https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv', headers=UA)
        t = pd.read_csv(io.BytesIO(urllib.request.urlopen(req, timeout=25).read()))
        return dict(zip(t['Symbol'].str.replace('.','-',regex=False), t['GICS Sector'])), 'github-csv'
    sectors, src = get_constituents()
    tickers = sorted(set(list(sectors.keys()) + ETFS))
    print(f'{len(tickers)} tickers ({src}). Downloading — the slow part, ~60-90s.')
    px = yf.download(tickers, start=START, auto_adjust=True, progress=False, threads=True)['Close']
    print(f'got {px.shape[1]} series x {px.shape[0]} rows\n')
for e in ETFS: sectors.setdefault(e, 'ETF')

# ---- pre-extract clean arrays ONCE; 300 re-screens reuse them -----------------
SERIES = []
for t in px.columns:
    s = px[t].dropna()
    if len(s) >= 900:
        SERIES.append((t, s.to_numpy(float), s.index.to_numpy(), sectors.get(t, '?')))
print(f'{len(SERIES)} series with >=900 rows')

# ---- for [SYNC]: the subset with COMPLETE history over the common calendar ----
#      a synchronized row-shuffle only makes sense where every name has a value
#      on every row. names with partial history are dropped from the SYNC null
#      (and from its real-data comparison, so both arms match).
full = px.dropna(axis=1, how='any')
SYNC_DATES = full.index.to_numpy()
SYNC_V     = full.to_numpy(float)
SYNC_TKRS  = list(full.columns)
SYNC_SEC   = [sectors.get(t,'?') for t in SYNC_TKRS]
print(f'{SYNC_V.shape[1]} of {px.shape[1]} names have COMPLETE history since {START} — the [SYNC] universe\n')

# ---- the screen, stripped to ONLY what the survivor rule needs ----------------
#      (no HEAT, no lag, no vol — display fields, ~90% of the runtime. dropping
#       them is what makes 300 full re-screens feasible.)
SPLIT64 = SPLIT.to_datetime64()

def screen(v, dts):
    n = len(v)
    if n < 900: return None
    hi   = pd.Series(v).rolling(LOOKBACK, min_periods=LOOKBACK).max().to_numpy()
    dd   = v/hi - 1
    prev = np.r_[np.nan, dd[:-1]]
    cand = np.where((dd <= -THRESH) & (prev > -THRESH))[0]
    cand = cand[cand >= LOOKBACK]
    ev, last = [], -10**9
    for i in cand:
        if i - last >= COOL:
            ev.append(i); last = i
    if len(ev) < MIN_N: return None
    ev    = np.array(ev)
    early = ev[dts[ev] <  SPLIT64]
    late  = ev[dts[ev] >= SPLIT64]

    def edge(fwd, idx, base):
        if len(idx) < 8: return np.nan
        x = fwd[idx]; x = x[~np.isnan(x)]
        return x.mean() - base if len(x) >= 8 else np.nan

    out = {}
    for h in (21, 63):
        fwd  = (np.r_[v[h:], np.full(h, np.nan)]/v - 1)*100
        base = np.nanmean(fwd)
        out[f'e{h}'] = edge(fwd, ev, base)
        if h == 63:
            out['E63'] = edge(fwd, early, base)
            out['L63'] = edge(fwd, late,  base)
    return out

def survives(o):
    if o is None: return False
    a, b, c, d = o['e21'], o['e63'], o['E63'], o['L63']
    if np.isnan(a) or np.isnan(b) or np.isnan(c) or np.isnan(d): return False
    return (np.sign(a) == np.sign(b)) and b > 0 and c > 0 and d > 0

def tally(paths):
    """paths = iterable of (v, dts, is_etf). -> (tested, surv, best_e63, etf_t, etf_s)"""
    tested = surv = etf_t = etf_s = 0; best = -np.inf
    for v, dts, is_etf in paths:
        try:    o = screen(v, dts)
        except Exception: o = None
        if o is None: continue
        tested += 1; etf_t += is_etf
        if survives(o):
            surv += 1; etf_s += is_etf
            if o['e63'] > best: best = o['e63']
    return tested, surv, best, etf_t, etf_s

rng = np.random.default_rng(SEED)

def rebuild(v0, r):
    return v0*np.exp(np.r_[0.0, np.cumsum(r)])

def iid_paths():
    for t, v, dts, sec in SERIES:
        r = np.diff(np.log(v))
        yield rebuild(v[0], rng.permutation(r)), dts, sec == 'ETF'

def block_paths():
    for t, v, dts, sec in SERIES:
        r = np.diff(np.log(v)); n = len(r)
        nb = int(np.ceil(n/BLOCK))
        st = rng.integers(0, max(1, n-BLOCK+1), nb)
        r2 = np.concatenate([r[s:s+BLOCK] for s in st])[:n]
        yield rebuild(v[0], r2), dts, sec == 'ETF'

SYNC_R = np.diff(np.log(SYNC_V), axis=0)          # (n-1, k) — computed ONCE
def sync_paths():
    """ONE block reordering of the calendar, applied to EVERY name identically.
       preserves the cross-sectional correlation the other two nulls destroy."""
    n  = SYNC_R.shape[0]
    nb = int(np.ceil(n/BLOCK))
    st = rng.integers(0, max(1, n-BLOCK+1), nb)
    idx = np.concatenate([np.arange(s, s+BLOCK) for s in st])[:n]
    R2  = SYNC_R[idx]                              # same rows for all columns
    P   = SYNC_V[0]*np.exp(np.vstack([np.zeros(R2.shape[1]), np.cumsum(R2, axis=0)]))
    for j in range(P.shape[1]):
        yield P[:, j], SYNC_DATES, SYNC_SEC[j] == 'ETF'

def real_paths():
    for t, v, dts, sec in SERIES: yield v, dts, sec == 'ETF'
def real_sync_paths():
    for j in range(SYNC_V.shape[1]): yield SYNC_V[:, j], SYNC_DATES, SYNC_SEC[j] == 'ETF'

# ---- THE REAL RUNS, through THIS code path -------------------------------------
#      recomputed here rather than quoted from the earlier cell, so real and null
#      come from the SAME function. quoting 19.2% from a different implementation
#      would compare two numbers that were never measured the same way.
t0 = time.time()
Rt, Rs, Rbest, Ret, Res = tally(real_paths())
per_pass = time.time() - t0
St, Ss, Sbest, Set_, Ses = tally(real_sync_paths())
print('='*104)
print('  REAL DATA (recomputed through the permutation code path)')
print(f'    FULL universe : tested {Rt:>3}   survivors {Rs:>3} = {Rs/max(Rt,1)*100:5.1f}%   '
      f'best e63 {Rbest:+.2f}   ETFs {Res}/{Ret}')
print(f'    SYNC universe : tested {St:>3}   survivors {Ss:>3} = {Ss/max(St,1)*100:5.1f}%   '
      f'best e63 {Sbest:+.2f}   ETFs {Ses}/{Set_}')
print(f'    [{per_pass:.1f}s per pass -> total ~{per_pass*3*NSHUF/60:.0f} min for {3*NSHUF} shuffles]')
print('='*104 + '\n')

# ---- the three nulls ------------------------------------------------------------
NULLS, REALS = {}, {'IID': (Rt,Rs,Rbest,Ret,Res), 'BLOCK': (Rt,Rs,Rbest,Ret,Res),
                    'SYNC': (St,Ss,Sbest,Set_,Ses)}
for label, gen in (('IID', iid_paths), ('BLOCK', block_paths), ('SYNC', sync_paths)):
    rates, bests, etfr = [], [], []
    print(f'--- {label} null, {NSHUF} shuffles ' + '-'*56)
    for k in range(NSHUF):
        nt, ns_, nb, et, es = tally(gen())
        rates.append(ns_/nt*100 if nt else np.nan)
        bests.append(nb); etfr.append(es/et*100 if et else np.nan)
        if (k+1) % 20 == 0 or k == 0:
            print(f'   {k+1:>4}/{NSHUF}   rate {rates[-1]:5.1f}%   best e63 {bests[-1]:+6.2f}'
                  f'   (running mean {np.nanmean(rates):.1f}%)')
    NULLS[label] = (np.array(rates,float), np.array(bests,float), np.array(etfr,float))

# ---- verdict ---------------------------------------------------------------------
def pv(null, real):
    n = null[np.isfinite(null)]
    if not len(n) or not np.isfinite(real): return np.nan
    return (np.sum(n >= real) + 1)/(len(n) + 1)       # +1 counts the real run itself

def line(q, label, null, real, unit, kill):
    n = null[np.isfinite(null)]
    if not len(n): return
    p = pv(null, real)
    tag = 'REAL' if p <= 0.05 else ('marginal' if p <= 0.15 else kill)
    star = ' ★' if label == 'SYNC' else '  '
    print(f'  {q} {label:<6}{star}{n.mean():>10.{unit}f}{n.std():>9.{unit}f}'
          f'{np.percentile(n,95):>11.{unit}f}{real:>10.{unit}f}{p:>8.3f}   {tag}')

print('\n' + '='*104)
print('  VERDICT   (★ = [SYNC], the null with the real cross-sectional structure — JUDGE BY THIS ROW)')
print('='*104)
print(f'  {"":<10}{"NULL mean":>12}{"NULL sd":>9}{"NULL 95th":>11}{"REAL":>10}{"p":>8}   read')
print('  -- Q1  SURVIVOR RATE %  — does the screen keep more names than noise keeps? ------------')
for L in ('IID','BLOCK','SYNC'):
    t_,s_,b_,et_,es_ = REALS[L]
    line('Q1', L, NULLS[L][0], s_/max(t_,1)*100, 1, 'INDISTINGUISHABLE FROM NOISE')
print('  -- Q2  BEST SINGLE e63  — is the TOP of the ranking better than the best random name? --')
for L in ('IID','BLOCK','SYNC'):
    t_,s_,b_,et_,es_ = REALS[L]
    line('Q2', L, NULLS[L][1], b_, 2, 'THE TOP OF THE RANKING IS NOISE')
print(f'  -- Q3  ETF SUBGROUP %   — n={Ret} ETFs. SMALL subgroup, wide error bars. ---------------')
for L in ('IID','BLOCK','SYNC'):
    t_,s_,b_,et_,es_ = REALS[L]
    if et_: line('Q3', L, NULLS[L][2], es_/et_*100, 1, 'the ETF finding is noise')

print('\n' + '='*104)
print('  ⚠️ HOW TO READ THIS — the failure modes are as informative as a pass')
print('   1. JUDGE BY [SYNC]. [IID] and [BLOCK] shuffle each name separately, so their null')
print('      universes have NO shared crashes — the null spread is too tight and the p-value is')
print('      flattered. [SYNC] keeps the shared crashes. If SYNC says noise and the others say')
print('      real, THE ANSWER IS NOISE — the screen found "March 2020 recovered," not an edge.')
print('   2. Q1 PASS + Q2 FAIL is the most likely outcome and the most useful: "dip-buying works')
print('      broadly" survives while "these specific top names" does NOT. In that case the')
print('      tradeable unit is the BASKET or the INDEX, and the 14-name shortlist is decoration.')
print('   3. Q1 FAIL kills everything downstream — the 96 survivors, the sector rates, the')
print('      shortlist. No re-ranking rescues a rate that noise reproduces.')
print('   4. SURVIVORSHIP DOES NOT CANCEL INTO SAFETY: it is present in BOTH arms, so it drops')
print('      out of the p-value and stays FULLY INTACT in the level. A pass never means the')
print('      printed +% is achievable — only that the pattern is not reproducible by shuffling.')
print('   5. AND IT SAYS NOTHING ABOUT MONEY. Measured 7/31: $226 expected dip edge vs $1,805 of')
print('      theta. A real edge and a profitable trade are different claims; this tests the first.')
print('='*104)
