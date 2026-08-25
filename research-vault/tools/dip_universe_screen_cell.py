# ============================================================================
#  DIP-UNIVERSE SCREEN — "where do I put the money." NOT constrained to names
#  you already own.   (Jake, 2026-07-31: "It doesn't have to be my names.")
#
#  WHY THIS SUPERSEDES movement_capture_screen_cell.py:
#  That one ran your 23-name basket + ETFs = 34 tickers. AMAT topping THAT list
#  may only mean it is the best of 34. This runs the WHOLE S&P 500 + the liquid
#  ETF set. At $1,037 per position liquidity is not a constraint, so the only
#  reason to exclude a name is that it fails the test.
#
#  ⚠️ AND WIDENING THE UNIVERSE CREATES THE PROBLEM THIS CELL EXISTS TO SOLVE:
#  500 names x 4 horizons = ~2,000 comparisons. At p=0.05 you get ~100 that
#  "look significant" on pure noise. THE TOP OF ANY 500-NAME RANKING IS NOISE
#  UNLESS YOU CONTROL FOR IT. Three controls, and they are the whole point:
#
#   [A] OUT-OF-SAMPLE SPLIT — the strongest one. Split at 2021-01-01 and require
#       the edge to hold in BOTH halves. A name that worked 2015-20 and died
#       2021-26 is a regime artifact, not an edge. This kills most of the noise.
#   [B] HORIZON CONSISTENCY — require e21 AND e63 to agree in sign. A single hot
#       cell is a coin flip; agreement across horizons is much harder to fake.
#   [C] MINIMUM SAMPLE — n >= 25 events. Below that the error bars swallow it.
#
#  Everything is EDGE vs THAT NAME's own base rate over the same window, because
#  a high-drift name shows positive forward returns measured from anywhere.
#
#  SURVIVORSHIP, STATED NOT HIDDEN: this is TODAY's S&P 500. Every company that
#  was deleted -- bankruptcies, collapses, takeunders -- is ABSENT. Dip-buying
#  results are therefore FLATTERED, and flattered MORE at 500 names than at 34.
#  Treat the level as optimistic and the RANKING as the usable output.
# ============================================================================
import subprocess, sys, io, urllib.request
try:
    import yfinance as yf; import pandas as pd; import numpy as np
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas','lxml'])
    import yfinance as yf; import pandas as pd; import numpy as np

UA = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
LOOKBACK, THRESH, COOL = 63, 0.08, 21
HOR   = [10, 21, 63]
SPLIT = '2021-01-01'      # out-of-sample boundary
MIN_N = 25
START = '2015-01-01'
ETFS  = 'SPY QQQ IWM MDY SOXX SMH XLK XLF XLE XLV XLI XLP XLU XLB XLRE XBI KRE ITB GLD SLV TLT HYG'.split()

def get_constituents():                      # reused from sp500_full_sweep_cell.py
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
for e in ETFS: sectors.setdefault(e, 'ETF')
print(f'{len(tickers)} tickers ({src} + {len(ETFS)} ETFs). Downloading — this is the slow part.')

px = yf.download(tickers, start=START, auto_adjust=True, progress=False, threads=True)['Close']
print(f'got {px.shape[1]} price series, {px.shape[0]} rows\n')

def analyse(s):
    s = s.dropna()
    v = s.to_numpy(float); n = len(v)
    if n < 900: return None
    hi   = pd.Series(v).rolling(LOOKBACK, min_periods=LOOKBACK).max().to_numpy()
    dd   = v/hi - 1
    sma  = pd.Series(v).rolling(20).mean().to_numpy()
    ev, last = [], -10**9
    for i in range(LOOKBACK, n):
        if dd[i] <= -THRESH and dd[i-1] > -THRESH and i-last >= COOL:
            ev.append(i); last = i
    if len(ev) < MIN_N: return None
    ev = np.array(ev)
    fwd  = {h: (np.r_[v[h:], np.full(h, np.nan)]/v - 1)*100 for h in HOR}
    base = {h: np.nanmean(fwd[h]) for h in HOR}
    dates = s.index
    early = ev[dates[ev] <  pd.Timestamp(SPLIT)]
    late  = ev[dates[ev] >= pd.Timestamp(SPLIT)]

    def edge(idx, h):
        if len(idx) < 8: return np.nan
        x = fwd[h][idx]; x = x[~np.isnan(x)]
        return x.mean()-base[h] if len(x) >= 8 else np.nan

    mae = []
    for t in ev:
        w = v[t:t+22]
        mae.append((w.min()/v[t]-1)*100 if len(w) > 3 else np.nan)
    lag = []
    for t in ev:
        below = next((j for j in range(t, min(t+63,n)) if not np.isnan(sma[j]) and v[j] < sma[j]), None)
        if below is None: continue
        r = next((j for j in range(below+1, min(t+63,n)) if not np.isnan(sma[j]) and v[j] > sma[j]), None)
        if r is not None: lag.append(r-t)

    o = dict(n=len(ev), n_early=len(early), n_late=len(late),
             per_yr=len(ev)/(len(v)/252), heat=np.nanmedian(mae),
             lag=np.median(lag) if lag else np.nan,
             vol=s.pct_change().std()*np.sqrt(252)*100)
    for h in HOR:
        o[f'e{h}'] = edge(ev, h); o[f'E{h}'] = edge(early, h); o[f'L{h}'] = edge(late, h)
    return o

rows = {}
for t in tickers:
    if t in px.columns:
        try:
            a = analyse(px[t])
            if a: rows[t] = a
        except Exception: pass
R = pd.DataFrame(rows).T
R['sector'] = [sectors.get(i,'?') for i in R.index]
print(f'{len(R)} names passed n>={MIN_N}\n')

# ---- THE THREE CONTROLS ----------------------------------------------------
R['consistent'] = (np.sign(R['e21']) == np.sign(R['e63'])) & (R['e63'] > 0)          # [B]
R['oos']        = (R['E63'] > 0) & (R['L63'] > 0)                                     # [A] both halves
R['survives']   = R['consistent'] & R['oos']
R['per_heat']   = R['e63'] / R['heat'].abs()

surv = R[R['survives']].sort_values('e63', ascending=False)
print('='*126)
print(f'  SURVIVORS — positive e63, e21 AGREES in sign, AND positive in BOTH sample halves')
print(f'  {len(surv)} of {len(R)} names ({len(surv)/len(R)*100:.0f}%).  A pure-noise universe would leave ~12%.')
print('='*126)
print(f'  {"tkr":<6}{"sector":<24}{"n":>4}{"/yr":>5}{"vol":>5}{"HEAT":>6}{"lag":>5}'
      f'{"e21":>7}{"e63":>7}  | {"pre-21":>7}{"post-21":>8} | {"e63/HEAT":>9}  entry')
for t, x in surv.head(30).iterrows():
    entry = 'DIRECT' if x['lag'] <= 9 else ('WAIT-RECLAIM' if x['lag'] >= 12 else 'either')
    print(f'  {t:<6}{str(x["sector"])[:23]:<24}{int(x["n"]):>4}{x["per_yr"]:>5.1f}{x["vol"]:>5.0f}'
          f'{x["heat"]:>+6.1f}{x["lag"]:>5.0f}{x["e21"]:>+7.1f}{x["e63"]:>+7.1f}  | '
          f'{x["E63"]:>+7.1f}{x["L63"]:>+8.1f} | {x["per_heat"]:>9.2f}  {entry}')

print('\n' + '='*126)
print('  TOP 15 BY EDGE-PER-HEAT (the sizing-aware ranking — what you can actually hold through)')
print('='*126)
for t, x in surv.sort_values('per_heat', ascending=False).head(15).iterrows():
    print(f'  {t:<6}{str(x["sector"])[:23]:<24} e63 {x["e63"]:>+5.1f}  HEAT {x["heat"]:>+5.1f}  '
          f'ratio {x["per_heat"]:>5.2f}  {x["per_yr"]:.1f} dips/yr  lag {x["lag"]:.0f}')

print('\n' + '='*126)
print('  SECTOR TALLY OF SURVIVORS — is the edge a NAME effect or a SECTOR effect?')
print('='*126)
tal = surv.groupby('sector').agg(names=('e63','size'), med_e63=('e63','median'), med_heat=('heat','median'))
allc = R.groupby('sector').size()
tal['of_total'] = [f'{int(v)}/{int(allc.get(i,0))}' for i, v in zip(tal.index, tal['names'])]
print(tal.sort_values('names', ascending=False).to_string())
print('\n  ** If survivors CLUSTER in one or two sectors, you are looking at a SECTOR trade')
print('     wearing single-name clothes -- and you should size it as ONE position, not four. **')

print('\n' + '='*126)
print('  ⚠️ HOW TO READ THIS')
print('   1. SURVIVORSHIP: today\'s S&P 500. Deleted names are ABSENT -> every number is FLATTERED,')
print('      and MORE so at 500 names than at 34. The RANKING is usable; the LEVEL is optimistic.')
print('   2. The OOS split is the load-bearing control. A name that fails post-2021 is a regime')
print('      artifact. If the survivor count is near ~12% of the universe, the whole screen is noise.')
print('   3. HEAT is the sizing input. e63/HEAT is the ranking that respects what you can sit through.')
print('   4. lag <=9 -> BUY THE DIP DIRECTLY.  lag >=12 -> WAIT FOR THE 20-SMA RECLAIM.')
print('      (Measured 7/31: the reclaim filter HALVES the edge on fast names, doubles it on slow ones.)')
print('   5. ~4 dips/yr means ~1 setup per name per 90 days. Four names ~= four shots. Plan patience.')
print('='*126)
