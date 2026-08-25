# ORACLE BACKTEST — agent brief (built 2026-08-19, Jake's spec)

## WHAT THE DATA IS
`backtest/out/oracle_trades.json` and `backtest/out/oracle_features.csv` — 176 PERFECT-FORESIGHT trades.
Rule: within each CALENDAR MONTH, the 2 non-overlapping pairs (buy1<=sell1<=buy2<=sell2) maximising
summed return. Buys fill at the INTRADAY LOW, sells at the INTRADAY HIGH. Same-day round trips allowed.
SPX + NDX, Jan-2023 -> Aug-2026, 44 months x 2 legs x 2 indices.
Result: SPX 355.1% sum-of-legs vs 101.6% buy&hold. NDX 491.6% vs 153.5%.
Median hold 5-5.5 trading days. 23 of 176 are same-day (13%).

`backtest/out/daily_panel.csv` — 1,817 daily rows (both indices, same window) with the SAME 60+ features.
**THIS IS THE DENOMINATOR. It is not optional.**

Columns: `B_*` = feature on the BUY date. `S_*` = feature on the SELL date. Same names in daily_panel
without the prefix. Includes: RSI14, %B, ATR%, dist from 20/50/200 DMA, 1/3/5/10/20d returns, drawdown
from 20/63/252d high, run-up from lows, 20d-low/high flags, volume vs 20d, realised vol, consecutive
up/down days, day-of-week, trading-day-in-month, days to opex, turn-of-month, quarter-end, VIX + 5d chg
+ 252d percentile, DXY/WTI/gold/HYG/TLT + 5d chg, Treasury par curve (3m,1y,2y,5y,10y,20y,30y) + 5d chg,
2s10s, 2s30s.

## THE FIVE RULES — a finding that breaks any of these is REJECTED
1. **EVERY claim carries: n, the BASE RATE from daily_panel.csv, and the LIFT.** "Oracle buys cluster at
   RSI<35" is worthless without "and X% of ALL days are RSI<35." State both numbers or do not state it.
2. **MULTIPLE COMPARISONS ARE GUARANTEED HERE.** 143 columns x 176 rows. Some feature will look
   spectacular by chance. Report effect SIZE and n, not p-values, and say plainly when a result could be
   one of many tested.
3. **THE SELECTION BIAS IS THE WHOLE DATASET AND MUST BE NAMED, NOT MANAGED.** These trades were chosen
   BECAUSE a rally followed. Any feature at a buy date is conditioned on that. So "oracle buys happen at
   low RSI" may only mean "rallies start from lows" — a tautology, not an edge.
4. **AN ORACLE IS A DESCRIPTION, NOT A STRATEGY.** If you propose a rule, you must state what the
   out-of-sample test would be and admit it has not been run.
5. **NO SILENT CAPS.** If you looked at 3 of 44 months or dropped rows, say so.

## KNOWN GAPS — do not fabricate these
- NO event calendar. FOMC, CPI, NFP, earnings dates are NOT in the data. If your angle needs them, say so.
- Same-day (hold=0) trades use the same bar's low and high — flag them where they matter.
- Treasury curve is forward-filled to the last available business day.
