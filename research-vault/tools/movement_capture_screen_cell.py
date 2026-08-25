# ============================================================================
#  MOVEMENT-CAPTURE SCREEN — "which stocks move most, and how to capture it"
#  (Jake's 90-day plan, 2026-07-31. Run in Colab BEFORE the 8pm reset — this is
#   the expensive part and it is FREE on your side. Fable then reasons on the
#   TABLE instead of spending its budget fetching prices.)
#
#  THE QUESTION, STATED SO IT IS ANSWERABLE:
#  You cannot predict WHICH name drops 8-10% or WHEN. seeing-vs-predicting is
#  the vault's capstone: **movement predicts MAGNITUDE, not SIGN.** So this does
#  NOT forecast. It measures, per name:
#     (1) HOW OFTEN it hands you a >=8% dip          <- your opportunity RATE
#     (2) WHAT HAPPENS AFTER, vs its own base rate   <- the EDGE, not the return
#     (3) HOW MUCH FURTHER IT FALLS FIRST            <- the heat you must sit through
#     (4) WHETHER THE 20-SMA RECLAIM FILTER HELPS    <- YOUR tested filter
#
#  (4) IS THE VAULT'S OWN FINDING, not a new idea. deep-value-reclaim:
#  "the 20-SMA reclaim requirement added ~3 points of CAGR while CUTTING VOL
#  NEARLY IN HALF." This re-tests it per-name so you know WHERE it works.
#
#  AND THE DESIGN LESSON FROM TODAY IS BAKED IN: this measures the TRANSITION
#  (the day the dip threshold is crossed), NOT the STATE (being down). The AVWAP
#  work found those give OPPOSITE signs -- -3.55 vs +2.50 on the same anchor --
#  because "in a dip" is dominated by 2008/2022 grinds while "just dipped" is
#  ordinary dips in uptrends. Entering is a transition. Measure the transition.
#
#  THREE TRAPS, HANDLED:
#   - BASE RATE: every number is EDGE vs THAT NAME's own mean over the same
#     sample. A high-drift name shows positive forward returns from anywhere.
#   - SURVIVORSHIP: yfinance gives you today's survivors. Names that went to
#     zero are absent, so ALL dip-buy results here are FLATTERED. Stated, not hidden.
#   - OVERLAP: 63d forward windows overlap heavily -> t-stats are optimistic.
#     Read the RANKING and the PATTERN, never a single cell.
# ============================================================================
import subprocess, sys
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance']); import yfinance as yf
import numpy as np, pandas as pd

# Jake's 23-name basket + the ETFs he can actually trade + the neocloud cohort
UNIV = ('NVDA ORCL QRVO TXN AVGO TSM INTC AMAT AMD IREN RNW CRWV COHR RIVN EWY NBIS MU '
        'LITE LRCX MP SWKS GFS ARM LLY NOW CRCL VG '
        'SPY QQQ QQQM IWM SOXX SMH XLK XLE GLD TLT').split()
LOOKBACK = 63        # trailing high window that defines "a dip"
THRESH   = 0.08      # >=8% off the trailing high == the event, per Jake
HOR      = [5, 10, 21, 63]
COOL     = 21        # min days between events, so one selloff isn't counted 15 times
START    = '2015-01-01'

px = yf.download(UNIV, start=START, progress=False, auto_adjust=True, threads=True)['Close']
if isinstance(px, pd.Series): px = px.to_frame(UNIV[0])

def analyse(s):
    v = s.dropna().to_numpy(float)
    n = len(v)
    if n < 400: return None
    roll_hi = pd.Series(v).rolling(LOOKBACK, min_periods=LOOKBACK).max().to_numpy()
    dd = v/roll_hi - 1
    sma20 = pd.Series(v).rolling(20).mean().to_numpy()

    # TRANSITION events: the day dd first crosses below -THRESH, with a cooloff
    ev, last = [], -10**9
    for i in range(LOOKBACK, n):
        if dd[i] <= -THRESH and dd[i-1] > -THRESH and i - last >= COOL:
            ev.append(i); last = i
    if len(ev) < 6: return None
    ev = np.array(ev)

    fwd = {h: (np.r_[v[h:], np.full(h, np.nan)]/v - 1)*100 for h in HOR}
    base = {h: np.nanmean(fwd[h]) for h in HOR}

    # heat: worst close-to-close drawdown in the 21d AFTER entry  (max adverse excursion)
    mae = []
    for t in ev:
        w = v[t:t+22]
        mae.append((w.min()/v[t]-1)*100 if len(w) > 3 else np.nan)
    mae = np.array(mae, float)

    # the 20-SMA RECLAIM filter (deep-value-reclaim's finding), per name
    # ⛔ FIXED 2026-07-31 (v1 was WRONG). v1 started the search at j=t, the TRIGGER DAY,
    # so a name 8% off a 63d high that was STILL ABOVE its 20-SMA logged "reclaimed, lag 0."
    # That filtered NOTHING -- rec% came back ~100% on 29 of 34 names, lag 0 on six.
    # deep-value-reclaim requires price BELOW the 20-SMA first, THEN a cross back above.
    # Events that never go below are EXCLUDED: there is no reclaim to filter on.
    rec_idx, rec_lag, no_setup = [], [], 0
    for t in ev:
        below = None
        for j in range(t, min(t+63, n)):
            if not np.isnan(sma20[j]) and v[j] < sma20[j]: below = j; break
        if below is None: no_setup += 1; continue
        for j in range(below+1, min(t+63, n)):
            if not np.isnan(sma20[j]) and v[j] > sma20[j]:
                rec_idx.append(j); rec_lag.append(j-t); break
    rec_idx = np.array(rec_idx, int)

    r = s.dropna().pct_change()
    out = dict(
        n=len(ev), per_yr=len(ev)/(n/252),
        vol=r.std()*np.sqrt(252)*100,
        med_dd=np.nanmedian([dd[t]*100 for t in ev]),
        mae=np.nanmedian(mae),
        rec_pct=len(rec_idx)/len(ev)*100, no_setup=no_setup, rec_lag=np.median(rec_lag) if rec_lag else np.nan)
    for h in HOR:
        x = fwd[h][ev]; x = x[~np.isnan(x)]
        out[f'e{h}'] = x.mean()-base[h] if len(x) >= 5 else np.nan
        if len(rec_idx):
            y = fwd[h][rec_idx]; y = y[~np.isnan(y)]
            out[f'r{h}'] = y.mean()-base[h] if len(y) >= 5 else np.nan
        else: out[f'r{h}'] = np.nan
    return out

rows = {}
for t in UNIV:
    if t in px.columns:
        a = analyse(px[t])
        if a: rows[t] = a
R = pd.DataFrame(rows).T
if R.empty: raise SystemExit('no names qualified')

# COMPOSITE: opportunity RATE x payoff EDGE x reclaim hit-rate.
# Deliberately NOT the raw forward return -- that just ranks high-drift names.
R['score'] = (R['per_yr'].clip(0,12)/12) * R['r21'].fillna(R['e21']).clip(-5,15) * (R['rec_pct']/100)
R = R.sort_values('score', ascending=False)

print('='*118)
print(f'  MOVEMENT-CAPTURE SCREEN — {len(R)} names | dip = >={THRESH:.0%} off a {LOOKBACK}d high | '
      f'{COOL}d cooloff | since {START}')
print('  EDGE = forward return MINUS that name\'s own base rate. Only EDGE means anything.')
print('='*118)
print(f'  {"tkr":<6}{"dips/yr":>8}{"n":>4}{"vol%":>6}{"medDip":>8}{"HEAT":>7} | '
      f'{"e5":>6}{"e10":>6}{"e21":>7}{"e63":>7} | {"rec%":>6}{"lag":>5}{"r21":>7}{"r63":>7} | {"score":>6}')
print('  ' + '-'*114)
for t, x in R.iterrows():
    f = lambda k: f"{x[k]:>+6.1f}" if pd.notna(x[k]) else f"{'--':>6}"
    print(f'  {t:<6}{x["per_yr"]:>8.1f}{int(x["n"]):>4}{x["vol"]:>6.0f}{x["med_dd"]:>8.1f}{x["mae"]:>7.1f} | '
          f'{f("e5")}{f("e10")}{f("e21"):>7}{f("e63"):>7} | {x["rec_pct"]:>5.0f}%{x["rec_lag"]:>5.0f}'
          f'{f("r21"):>7}{f("r63"):>7} | {x["score"]:>6.2f}')

print('\n  COLUMNS')
print('   dips/yr  how often it hands you an 8% entry      = your OPPORTUNITY RATE')
print('   medDip   median depth AT the trigger              = is "8%" really 8% for this name?')
print('   HEAT     median worst drawdown in the NEXT 21d    = the pain you must sit through')
print('   e*       EDGE after the dip, no filter')
print('   rec%     goes BELOW the 20-SMA then RECLAIMS it within 63d; lag = median days')
print('            ⛔ v1 was BROKEN here: it counted "never went below" as a reclaim, so')
print('               rec% came back ~100% on 29 of 34 names. FIXED — events with no')
print('               below-SMA setup are now EXCLUDED. If rec% is STILL near 100 for a')
print('               name, that name simply rarely loses its 20-SMA on an 8% dip — which')
print('               is itself a finding about which dips are shallow.')
print('   r*       EDGE measured FROM THE RECLAIM  <- deep-value-reclaim\'s tested filter')
print('   score    opportunity rate x r21 edge x reclaim rate. NOT raw return -- that would')
print('            just rank whichever name drifted up most.')
print('\n  ⚠️ READ THIS BEFORE TRADING IT')
print('   1. SURVIVORSHIP: yfinance shows today\'s survivors. Names that died are ABSENT.')
print('      Every dip-buy number here is FLATTERED. The neoclouds especially -- short history,')
print('      and the ones that failed are not in the sample.')
print('   2. r* > e* is the WHOLE POINT. If the reclaim filter does not beat the naive dip')
print('      on a name, do not use the filter on that name -- and probably do not trade its dips.')
print('   3. HEAT is the position-sizing input, not a curiosity. If median HEAT is -12%, a')
print('      $1,037 position sits through ~-$124 BEFORE the thesis gets a chance. Size for HEAT,')
print('      not for the entry price.')
print('   4. 63d windows overlap -> t-stats optimistic. Read the RANKING, never one cell.')
print('   5. Short-history names (IREN/CRWV/NBIS/RNW/CRCL/ARM/GFS) have few events and wide')
print('      error bars. Treat a high score there as a HYPOTHESIS, not a finding.')
print('='*118)
