# ============================================================================
#  OIL ASYMMETRY — "Brent goes down much quicker now than it rises" (Jake, 8/2)
#
#  THE CLAIM: the rockets-and-feathers asymmetry has INVERTED — crude now falls
#  faster than it rises — and the cause is political pressure.
#
#  ⛔ WHY THE STATED MECHANISM CANNOT BE RIGHT, AND WHY THE CLAIM STILL MIGHT BE:
#  Rockets-and-feathers is a RETAIL phenomenon. It requires an INTERMEDIARY
#  holding a margin (the station) who can adjust slowly on the way down. BRENT
#  FUTURES HAVE NO SUCH INTERMEDIARY — a persistent directional asymmetry in a
#  deep two-way futures market is an arbitrage, and no president has a lever on
#  ICE. So the mechanism does not transfer.
#
#  BUT THREE OTHER MECHANISMS WOULD PRODUCE THE SAME OBSERVATION, and this cell
#  is built to separate them:
#   [A] NEWS-FLOW ASYMMETRY. De-escalation is ANNOUNCED — discrete, timed,
#       droppable into a closed market. Escalation is DISCOVERED — a tanker is
#       hit, UKMTO reports, confirmation trickles out intraday.
#       ⇒ ANNOUNCED EVENTS GAP. DISCOVERED EVENTS GRIND.
#       ⇒ TESTABLE: down-moves should be disproportionately OVERNIGHT GAPS,
#         up-moves disproportionately INTRADAY. This is the sharpest test here
#         and it needs no assumption about anyone's motives.
#   [B] OPTION-VALUE DECAY. A war premium is a tail bid. Building a tail is
#       gradual (probability and severity both drift); REMOVING one is discrete
#       (the attack is cancelled). Option value collapses faster than it accretes.
#       ⇒ produces the same asymmetry with NO political input at all.
#   [C] POLITICAL PRESSURE on the price itself. The vault's registered read is
#       "with the SPR EMPTY, jawboning Iran is the cheapest suppression tool
#       left" (demand-destruction L70). ⇒ if [C] is doing the work and not [A],
#       the asymmetry should appear in INTRADAY returns too, not just gaps.
#
#  ⚠️ AND THE NULL, BECAUSE THIS VAULT KILLED A 500-NAME SCREEN FOR SKIPPING ONE:
#  daily returns are roughly symmetric under a random walk. ANY measured
#  asymmetry needs a null before it is a finding. Here the null is a SIGN-FLIP
#  permutation: randomly flip the sign of each day's return and recompute the
#  statistic. That preserves the magnitude distribution exactly and destroys only
#  the up/down ASSIGNMENT — which is precisely the thing being claimed.
#  ⇒ IF THE REAL STATISTIC SITS INSIDE THE SIGN-FLIP NULL, THERE IS NO ASYMMETRY.
# ============================================================================
import subprocess, sys
try:
    import yfinance as yf; import pandas as pd; import numpy as np
except Exception:
    subprocess.run([sys.executable,'-m','pip','install','-q','yfinance','pandas'])
    import yfinance as yf; import pandas as pd; import numpy as np

TICKERS   = {'BZ=F':'Brent', 'CL=F':'WTI'}
START     = '2023-01-01'
WAR_START = '2026-02-28'      # Operation Epic Fury (Windward timeline)
NSHUF     = 2000
SEED      = 20260802
rng = np.random.default_rng(SEED)

print('downloading Brent + WTI daily OHLC...')
raw = yf.download(list(TICKERS), start=START, auto_adjust=False, progress=False,
                  threads=True, group_by='ticker')

def series(t):
    d = raw[t][['Open','Close']].dropna()
    d['prev']  = d['Close'].shift(1)
    d = d.dropna()
    d['tot']   = d['Close']/d['prev'] - 1        # close-to-close
    d['gap']   = d['Open'] /d['prev'] - 1        # OVERNIGHT — where announced news lands
    d['intra'] = d['Close']/d['Open']  - 1       # SESSION  — where discovered news lands
    return d

def asym(x):
    """mean |down| minus mean |up|. POSITIVE = down-moves are BIGGER = Jake's claim."""
    up, dn = x[x > 0], x[x < 0]
    if len(up) < 5 or len(dn) < 5: return np.nan
    return np.abs(dn).mean() - up.mean()

def signflip_p(x, stat):
    """null: keep the magnitudes, randomise the SIGNS. p = P(null >= real)."""
    a = np.abs(x); n = 0
    for _ in range(NSHUF):
        s = a * rng.choice([-1.0, 1.0], size=len(a))
        v = asym(s)
        if np.isfinite(v) and v >= stat: n += 1
    return (n + 1)/(NSHUF + 1)

for tk, name in TICKERS.items():
    try: d = series(tk)
    except Exception as e:
        print(f'\n{name}: FETCH FAILED ({type(e).__name__}) — no result, do not infer'); continue
    pre = d[d.index <  pd.Timestamp(WAR_START)]
    war = d[d.index >= pd.Timestamp(WAR_START)]
    print('\n' + '='*90)
    print(f'  {name}   pre-war n={len(pre)}   war n={len(war)}   (split {WAR_START})')
    print('='*90)
    print(f'  {"window":<10}{"leg":<8}{"n_up":>6}{"n_dn":>6}{"mean|up|%":>11}{"mean|dn|%":>11}'
          f'{"ASYM pp":>9}{"p(null)":>9}   read')
    for lab, dd in (('PRE-WAR', pre), ('WAR', war)):
        for leg in ('tot','gap','intra'):
            x = dd[leg].to_numpy(float); x = x[np.isfinite(x)]
            a = asym(x)
            if not np.isfinite(a):
                print(f'  {lab:<10}{leg:<8}  insufficient data'); continue
            up, dn = x[x>0], x[x<0]
            p = signflip_p(x, a)
            tag = ('DOWN BIGGER' if p <= 0.05 else
                   'up bigger' if p >= 0.95 else 'SYMMETRIC — no asymmetry')
            print(f'  {lab:<10}{leg:<8}{len(up):>6}{len(dn):>6}{up.mean()*100:>11.3f}'
                  f'{np.abs(dn).mean()*100:>11.3f}{a*100:>9.3f}{p:>9.3f}   {tag}')

    # ---- THE SHARP TEST: where do the BIGGEST moves live, overnight or intraday?
    print(f'\n  ── [A] ANNOUNCED-vs-DISCOVERED: are big DOWN moves GAPS and big UP moves INTRADAY?')
    for lab, dd in (('PRE-WAR', pre), ('WAR', war)):
        if len(dd) < 30: continue
        k = max(5, len(dd)//20)                                  # top 5% of |close-to-close|
        big = dd.reindex(dd['tot'].abs().sort_values(ascending=False).index[:k])
        bd, bu = big[big['tot'] < 0], big[big['tot'] > 0]
        def share(g):
            if not len(g): return np.nan
            return (g['gap'].abs()/(g['gap'].abs()+g['intra'].abs())).mean()*100
        print(f'     {lab:<9} biggest {k} moves: {len(bd)} down / {len(bu)} up   '
              f'GAP-share of move — down {share(bd):5.1f}%   up {share(bu):5.1f}%')
    print(f'     ⇒ [A] PREDICTS: in the WAR window, DOWN gap-share MATERIALLY ABOVE UP gap-share.')
    print(f'       If both are similar, the asymmetry (if any) is NOT announcement-timing.')

print('\n' + '='*90)
print('  ⚠️ HOW TO READ THIS')
print('   1. p is a SIGN-FLIP null: magnitudes held fixed, up/down assignment randomised.')
print('      It tests EXACTLY the claim and nothing else. p>0.05 ⇒ NO measured asymmetry, full stop.')
print('   2. A "war window" of a few months is a SMALL sample and it overlaps ONE regime.')
print('      Even a significant result here is ONE episode, not a law. Do not generalise it.')
print('   3. [A] vs [B] vs [C]: gap-loaded DOWN moves ⇒ [A] news timing. Asymmetry present in')
print('      INTRADAY too ⇒ [C] price pressure. Neither ⇒ [B] option decay, or nothing.')
print('   4. ⛔ TODAY IS ONE OBSERVATION. A -6.7% Sunday gap is a data point, not a pattern.')
print('      This vault killed a 500-name screen for reading structure into a sample like that.')
print('='*90)
