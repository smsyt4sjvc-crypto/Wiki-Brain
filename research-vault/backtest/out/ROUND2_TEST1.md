# ROUND-2 TEST #1 — ⛔ THE ROUND-1 HEADLINE IS DEAD. IT WAS MY OWN WINDOW.

**The question, registered as round 2's #1 because it could invalidate the headline:** was the month-edge
rhythm a real flow phenomenon, or an artifact of defining the oracle on CALENDAR MONTHS?

**THE TEST:** re-run the identical 2-trade oracle on windows offset by 7, 14 and 21 calendar days, then
measure leg-2 sells against BOTH boundaries — the (arbitrary) WINDOW end, and the CALENDAR month end.

## RESULT — unambiguous
| offset | sym | leg-2 sells at **WINDOW**-end | leg-2 sells at **CALENDAR month**-end |
|---|---|---|---|
| **0** | SPX | **61.4%** | **61.4%** |
| **7** | SPX | **63.6%** | **6.8%** |
| **14** | SPX | **50.0%** | **0.0%** |
| **21** | SPX | **40.9%** | **0.0%** |
| **0** | NDX | **59.1%** | **59.1%** |
| **7** | NDX | **59.1%** | **9.1%** |
| **14** | NDX | **56.8%** | **4.5%** |
| **21** | NDX | **50.0%** | **0.0%** |
**Base rate, last-2-trading-days-of-calendar-month: 88/907 = 9.7%.** n=44 windows per cell.

## ⛔ VERDICT: ARTIFACT
- **The concentration FOLLOWS THE ARBITRARY WINDOW BOUNDARY and does not follow the calendar.**
- **Calendar-month-end clustering collapses from ~60% to 0-9% the moment the window is shifted — i.e. TO
  THE BASE RATE, and at offset 7 SPX prints 6.8%, BELOW it.** ⇒ **There is not even a residual month-end
  effect. It is zero.**
- **Leg-1 buys at window-START behave the same way: 56.8% → 45.5% → 38.6% → 31.8%.** Follows the window.
- ⇒ **★★★ "LEG-2 SELLS CLUSTER IN THE LAST TWO TRADING DAYS OF THE MONTH, 6.2× BASE" WAS A STATEMENT
  ABOUT MY CODE, NOT ABOUT THE MARKET.** **A 2-trade-per-window optimiser puts the second sell near the
  end of whatever window you hand it. That is arithmetic.**

## ⚠️ AND THE VERIFIER'S 20,000-SIM NULL WAS CORRECT BUT AIMED AT THE WRONG TARGET
Round 1's adversarial verifier simulated the **ordering constraint** (buy1≤sell1≤buy2≤sell2) and correctly
found it predicts only 33.6% against the observed 60.2%, p=0.0000. **That test was right and it passed.**
**It simply never asked whether the WINDOW BOUNDARY — a separate feature of the construction — produced
the rest.** ⇒ **A null that models one part of your construction cannot clear the parts it does not model.**
🚩 **Standing lesson: when a finding depends on a boundary you chose, MOVE THE BOUNDARY. No amount of
in-boundary simulation substitutes.**

## ✅ WHAT SURVIVES ROUND 1 — and note WHERE the survivors came from
**Everything that survives was measured on `daily_panel.csv` with NO ORACLE CONTACT, so no window can
contaminate it:**
- **RSI14 < 25 → forward 5d mean +2.04% (n=37, 81.1% positive) vs all-days +0.48% (n=1,807, 61.3%).**
  Stable in all four years. **UNAFFECTED.**
- **`is_20d_low` → P(oracle buy) 35.97%, lift 3.91×** — a panel base rate. **UNAFFECTED.**
- **All the NEGATIVE findings** (VIX is 78-84% prior-return, credit residual 1.06×, rates ≤10bp
  within-year, day-of-week dead, opex confounded at r=−0.97, seasonality underpowered at n=44).
  **UNAFFECTED.**
- **⚠️ NEEDS RE-TESTING AT OFFSET: `consec_up_days ≥ 5 → zero oracle buys`.** It is oracle-conditioned.
  The mechanism is not obviously window-dependent, but that is an argument, not a measurement.

## ⇒ THE REAL CONCLUSION OF THE WHOLE EXERCISE SO FAR
**THE ORACLE'S CALENDAR STRUCTURE TAUGHT US NOTHING. THE PANEL BASE RATES TAUGHT US EVERYTHING.**
**The perfect-foresight trade set was useful as a QUESTION GENERATOR and worthless as an ANSWER —
every finding that survived came from the 1,817-row unconditioned panel sitting next to it.**
