# ============================================================================
#  AVWAP CROSS: DOES IT STAY BELOW, OR BOUNCE?   (Jake's question, 2026-07-30)
#
#  THIS IS A DIFFERENT TEST FROM THE LAST ONE. anchored_vwap_test_cell.py asked a
#  STATE question ("while below, what happens?"), which lumps day-1-below together
#  with day-200-below. This asks a TRANSITION question: on the day price CROSSES
#  below, what follows? Those can disagree, and the transition is the one that
#  matters when you are sitting at the line -- which SPY is, right now.
#
#  READ THIS BEFORE THE OUTPUT -- three traps, all handled.
#
#  (1) THE QUESTION HAS NO ANSWER WITHOUT A HORIZON. Over infinite time SPY
#      re-crosses everything, because it drifts up. Over one day it is a coin
#      flip. "Stays below or bounces" is ENTIRELY a function of the window you
#      pick => this cell SWEEPS horizons instead of choosing one.
#
#  (2) *** THE LINE MOVES. *** This is the subtle one and nobody tests it. A
#      "re-cross above the AVWAP" can happen WITHOUT PRICE RISING, because new
#      low-priced volume drags the AVWAP DOWN to meet price. That is not a
#      bounce, it is the level surrendering. => every re-cross is classified:
#      PRICE RECOVERED (close back above the cross-day close) vs LINE CAME DOWN.
#
#  (3) BASE RATE. SPY drifts up, so ANY condition shows positive forward returns
#      and ANY level gets recovered eventually. Everything is printed as EDGE
#      against the unconditional mean over the identical sample.
#
#  CONTROL: the identical test on a matched-window SMA cross. The previous cell
#  found AVWAP and SMA agree to ~0.01pp on the STATE question. Whether they agree
#  on the TRANSITION is an open question -- assumed nothing, measured it.
# ============================================================================
import subprocess, sys
try:
    import yfinance as yf
except Exception:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-q', 'yfinance']); import yfinance as yf
import numpy as np, pandas as pd

TICKER, START = 'SPY', '1995-01-01'
HOR   = [1, 3, 5, 10, 21, 63]
DD_TRIG = 0.05

df = yf.download(TICKER, start=START, progress=False, auto_adjust=False)
if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
df = df.dropna(subset=['Close', 'Volume'])
c  = df['Close'].to_numpy(float)
tp = ((df['High'] + df['Low'] + df['Close']) / 3).to_numpy(float)
v  = df['Volume'].to_numpy(float)
n  = len(c)
print(f'{TICKER}  {df.index[0].date()} -> {df.index[-1].date()}  {n:,} sessions')

def anch_ath():     rm = np.maximum.accumulate(c); return c >= rm - 1e-9
def anch_quarter(): q = df.index.to_period('Q');   return np.r_[True, q[1:] != q[:-1]]
def anch_trough():
    rm = np.maximum.accumulate(c); dd = c / rm - 1
    out = np.zeros(n, bool); i = 0
    while i < n:
        if dd[i] <= -DD_TRIG:
            j = i
            while j < n and dd[j] < 0: j += 1
            out[i + int(np.argmin(c[i:j]))] = True; i = j
        else: i += 1
    return out
ANCHORS = {'ATH': anch_ath(), 'quarter-start': anch_quarter(), f'-{DD_TRIG:.0%} trough': anch_trough()}

def last_idx(flags):
    idx = np.full(n, -1, int); last = -1
    for i in range(n):
        if flags[i]: last = i
        idx[i] = last
    return idx

def lines(flags):
    a = last_idx(flags)
    cpv = np.r_[0.0, np.cumsum(tp * v)]; cv = np.r_[0.0, np.cumsum(v)]; ctp = np.r_[0.0, np.cumsum(tp)]
    ar = np.arange(n); ok = a >= 0
    av = np.full(n, np.nan); sm = np.full(n, np.nan)
    den = cv[ar + 1] - cv[a]
    av[ok] = np.where(den[ok] > 0, (cpv[ar + 1] - cpv[a])[ok] / den[ok], np.nan)
    sm[ok] = (ctp[ar + 1] - ctp[a])[ok] / (ar - a + 1).astype(float)[ok]
    return av, sm, a

FR   = {h: (np.r_[c[h:], np.full(h, np.nan)] / c - 1) * 100 for h in HOR}
BASE = {h: np.nanmean(FR[h]) for h in HOR}
print('\nbase rates: ' + '  '.join(f'{h}d {BASE[h]:+.2f}%' for h in HOR))
print('EDGE = conditional minus unconditional, same sample.')

def analyse(line, label, anchor):
    below = c < line
    ok = ~np.isnan(line)
    cross = np.zeros(n, bool)
    cross[1:] = below[1:] & ~below[:-1] & ok[1:] & ok[:-1]
    ev = np.flatnonzero(cross)
    if len(ev) < 30:
        print(f'  {anchor:<15}{label:<7}  only {len(ev)} crosses'); return None

    # --- time until price closes back ABOVE the line, and WHY it happened
    recross, why_price = [], []
    for t in ev:
        k = -1
        for j in range(t + 1, n):
            if not np.isnan(line[j]) and c[j] > line[j]: k = j; break
        if k < 0: continue
        recross.append(k - t)
        why_price.append(c[k] > c[t])          # True = price recovered; False = line came down
    recross = np.array(recross); why_price = np.array(why_price)

    stay = {h: np.mean([np.all(below[t + 1:t + 1 + h]) for t in ev if t + h < n]) * 100 for h in HOR}
    frac = {h: np.mean([np.mean(below[t + 1:t + 1 + h]) for t in ev if t + h < n]) * 100 for h in HOR}
    cells_e, cells_s, cells_f = '', '', ''
    for h in HOR:
        x = FR[h][ev]; x = x[~np.isnan(x)]
        cells_e += f'{x.mean() - BASE[h]:>+9.2f}' if len(x) >= 30 else f'{"n/a":>9}'
        cells_s += f'{stay[h]:>8.0f}%'; cells_f += f'{frac[h]:>8.0f}%'
    print(f'  {anchor:<15}{label:<7}{len(ev):>6}  EDGE   {cells_e}')
    print(f'  {"":<15}{"":<7}{"":>6}  never re-crossed {cells_s}')
    print(f'  {"":<15}{"":<7}{"":>6}  %days below      {cells_f}')
    return ev, recross, why_price

print('\n' + '=' * 104)
print('  [A] THE CROSS EVENT — forward EDGE, and how much of the window is spent below')
print('=' * 104)
print(f'  {"anchor":<15}{"line":<7}{"n":>6}         ' + ''.join(f'{str(h)+"d":>9}' for h in HOR))
res = {}
for name, flags in ANCHORS.items():
    av, sm, a = lines(flags)
    for lab, L in (('AVWAP', av), ('SMA', sm)):
        r = analyse(L, lab, name)
        if r: res[(name, lab)] = r
    print()

print('=' * 104)
print('  [B] *** SURVIVAL: how long does "below" actually last? ***')
print('=' * 104)
print(f'  {"anchor":<15}{"line":<7}{"n":>6}{"median":>9}{"mean":>8}{"75th":>7}{"90th":>7}{"max":>7}'
      f'{"<=2d":>8}{"<=5d":>8}')
for (name, lab), (ev, rc, wp) in res.items():
    if len(rc) < 20: continue
    print(f'  {name:<15}{lab:<7}{len(rc):>6}{np.median(rc):>9.0f}{rc.mean():>8.1f}'
          f'{np.percentile(rc,75):>7.0f}{np.percentile(rc,90):>7.0f}{rc.max():>7.0f}'
          f'{(rc<=2).mean()*100:>7.0f}%{(rc<=5).mean()*100:>7.0f}%')
print('  If MEDIAN is small but MEAN and MAX are huge, the answer is neither "stays')
print('  below" nor "bounces" -- it is CHOP, with a fat tail where all the P&L lives.')

print('\n' + '=' * 104)
print('  [C] *** WHY DID IT RE-CROSS? price recovered, or the LINE came down to price? ***')
print('=' * 104)
print(f'  {"anchor":<15}{"line":<7}{"n":>6}{"price RECOVERED":>18}{"LINE came down":>17}')
for (name, lab), (ev, rc, wp) in res.items():
    if len(wp) < 20: continue
    print(f'  {name:<15}{lab:<7}{len(wp):>6}{wp.mean()*100:>17.0f}%{(1-wp.mean())*100:>16.0f}%')
print('  "LINE came down" = you got your re-cross WITHOUT price rising. For a long put')
print('  that is not a bounce -- the level surrendered and the signal evaporated.')

print('\n' + '=' * 104)
print('  [D] CONTEXT — does the cross matter more when the level was HELD LONGER?')
print('=' * 104)
for name, flags in ANCHORS.items():
    av, sm, a = lines(flags)
    if (name, 'AVWAP') not in res: continue
    ev = res[(name, 'AVWAP')][0]
    below = c < av
    run = np.zeros(n, int)
    for i in range(1, n):
        run[i] = 0 if (np.isnan(av[i]) or below[i]) else run[i-1] + 1
    held = np.array([run[t-1] for t in ev])
    med = np.median(held)
    print(f'  {name}  (median days held above before the cross: {med:.0f})')
    print(f'    {"bucket":<22}{"n":>6}   ' + ''.join(f'{str(h)+"d EDGE":>11}' for h in HOR))
    for lab2, m in (('held SHORT (<=med)', held <= med), ('held LONG  (>med)', held > med)):
        sub = ev[m]
        if len(sub) < 20: continue
        cells = ''
        for h in HOR:
            x = FR[h][sub]; x = x[~np.isnan(x)]
            cells += f'{x.mean()-BASE[h]:>+11.2f}' if len(x) >= 20 else f'{"n/a":>11}'
        print(f'    {lab2:<22}{len(sub):>6}   {cells}')
    print()

print('=' * 104)
print('  [E] LIVE')
print('=' * 104)
for name, flags in ANCHORS.items():
    av, sm, a = lines(flags)
    if np.isnan(av[-1]): continue
    below = c < av
    k = 0
    while k < n - 1 and below[n-1-k] == below[n-1]: k += 1
    print(f'  {name:<16}AVWAP {av[-1]:>8.2f}  close {c[-1]:>8.2f}  {(c[-1]/av[-1]-1)*100:>+6.2f}%'
          f'   {"BELOW" if below[-1] else "above"} for {k} session(s)')
print('\n  ~90 comparisons here -> expect ~4-5 to look significant on noise alone.')
print('  Read [B] and [C] FIRST: they are descriptive facts about the tape, not')
print('  conditional bets, so they do not suffer the multiple-testing problem.')
print('=' * 104)
