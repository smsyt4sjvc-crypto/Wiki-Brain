# ORACLE BACKTEST — ROUND 1 SYNTHESIS (2026-08-19)
6 lenses · 70+ hypotheses each · every finding adversarially re-derived by an independent verifier
told to refute it. **15 survived · 32 killed · 36 dead ends · 53 agents · 3.28M tokens.**

## ⛔ THE METHOD CORRECTION THAT APPLIES TO EVERY NUMBER BELOW
**The effective sample is ~95–99, NOT 176.** Verifiers measured it: SPX and NDX share the **identical buy
date in 71/88 (80.7%)** of (month, leg) pairs and the identical sell date in 57/88 (64.8%). Intra-class
correlation across calendar features **ICC = 0.852**, design effect 1.85. Macro columns (VIX, HYG, yields,
DXY) are **byte-identical across the two symbols** on all 907 shared dates — so any macro claim computed on
176 rows is double-counting and must be deduped to ~98 unique buy dates / 910 unique panel dates.
**Every lift below is stated on the corrected basis where the verifier supplied one.**

## ★★★★★★ HEADLINE — THE ORACLE'S STRUCTURE IS CALENDAR, NOT INDICATOR
**Perfect entries did not cluster on an oscillator. They clustered on a twice-monthly RHYTHM.**
Median trading-day-in-month, n=88 per leg-side:
**leg1 BUY day 2.0 → leg1 SELL day 8.5 → leg2 BUY day 13.0 → leg2 SELL day 19.5.**
- **leg-2 sells land in the LAST TWO trading days of the month 53/88 = 60.2%** against a **9.686% base
  rate ⇒ 6.22×.** Pooled across both legs 55/176 = 31.25% ⇒ 3.23×.
- **leg-1 sells are 2/88 = 2.3% — BELOW base rate.** The two legs have opposite calendar signatures.
- **leg-1 buys in the first two trading days 50/88 = 56.8%.**
- ⛔ **AND IT SURVIVES THE RIGHT NULL, WHICH IS THE PART THAT MATTERS.** The ordering constraint
  buy1≤sell1≤buy2≤sell2 mechanically pushes leg1 early and leg2 late — so the verifier simulated it.
  **20,000 order-statistic sims predict leg1-buy start-TOM 33.7% and leg2-sell end-TOM 33.6%. Observed:
  56.8% and 60.2%. P(null ≥ observed) = 0.0000.** ⇒ **The month-edge concentration is roughly DOUBLE what
  the construction alone forces.**
- **⭐ AND THERE IS A MID-MONTH HOLE.** Trading days 6, 10 and 16 hold **2, 0 and 1 buys** against ~8.5
  expected each. The verifier corrected the original agent's dismissal: **P(a given mid-month cell is
  empty) makes this a ~1-in-300 family-wise event — it IS remarkable**, and the agent's own arithmetic
  (off by ~125×) had argued the opposite of its conclusion.

## ✅ THE ONE GENUINELY TRADEABLE, NON-TAUTOLOGICAL FINDING
Measured on **daily_panel.csv with NO oracle contact at all** — so selection-on-outcome cannot explain it:
| condition | n | fwd 5d mean | % positive |
|---|---|---|---|
| **all days** | 1,807 | **+0.48%** | 61.3% |
| RSI14 30–40 | 202 | +0.88% | — |
| **RSI14 < 30** | 84 | **+1.82%** | **72.6%** |
| **RSI14 < 25** | 37 | **+2.04%** | **81.1%** |
**Excess +1.16 to +1.56pp = 3.4×–4.3× the unconditional mean.** **Stable in every single year:
2023 +1.74 · 2024 +1.98 · 2025 +1.67 · 2026 +2.31.** ⚠️ **n=37 at the RSI<25 cut. That is ~9 events per
year and it is the binding limitation.**

## ⛔ …AND THE FINDING THAT IMMEDIATELY DEMOTES IT
**RSI is mostly a re-encoding of "price is at a local low," and the price primitive is better:**
- **P(oracle buy | is_20d_low) = 50/139 = 35.97%, lift 3.91×** (7.65% of all days).
- **P(oracle buy | RSI<30) = 25/84 = 29.8%, lift 3.24×.**
- ⇒ **Inside the 20-day-low stratum, RSI<30 gives 40.7% vs RSI≥30 32.5% — the standalone 3.24× lift
  collapses to 1.25×.** ⇒ **Use `is_20d_low`. RSI adds ~a quarter on top of it, not a multiple.**
- ⚠️ **The verifier WITHDREW the deep-drawdown sub-claim as a Simpson-style artifact** — the apparent
  1.75× residual was `is_20d_low` re-entering through the back door.
- ⚠️ **Recall is the real problem: only 15.0% of oracle buys were RSI<30 days.** High precision, low
  recall. **This finds a minority of the good entries, not most of them.**

## ✅ THE STRONGEST *NEGATIVE* RULE — where perfect entries essentially never happen
- **`consec_up_days ≥ 5`: 114 panel days, ZERO oracle buys.**
- The wider exclusion zone covers **21.4% of all days and holds 4 of 167 buy-days: P = 1.03% vs a 9.19%
  base ⇒ lift 0.11×.** Expected 35.8, observed 4. ⇒ **Excluding it costs you 2.4% of the buys and removes
  a fifth of the calendar.** **A negative rule with n=114 and zero exceptions is worth more than most
  positive ones.**

## ⛔ WHAT DIED, AND THESE MATTER AS MUCH AS THE SURVIVORS
- **VIX — 78–84% of its apparent edge is just "price already fell."** Raw lifts vix_chg5d>+3 **2.70×**,
  vix>20 1.82×, vix_pctile>80 2.02× — after controlling for the prior 5-day return they fall to **1.29×,
  1.13×, 1.23×.** ⭐ **And the killer: at oracle buys the VIX percentile averages 0.758 versus 0.857 at
  the naive "lowest low of the month" day — VIX is LOWER at the good entries than at the obvious ones.**
- **CREDIT (HYG) — dead on the residual.** 65.3% of unique buy dates had HYG falling 5d vs 45.9% base
  (1.42×), but **equity-conditioned residual lift = 1.06 (z=0.79).** Credit adds nothing beyond equity.
- **RATES AND THE CURVE — dead at trade-timing resolution.** Pooled 2s10s at buys median −12.5bp vs panel
  +10.0bp looks big, but **within-year the maximum gap across all 7 tenors and both curve measures is
  10.0bp**, and **year-mixing explains ~40% of the pooled gap.** ⇒ **Rates set the regime; they do not
  time the entry.**
- **DAY OF WEEK — dead.** Net {Mon +15, Tue −2, Wed +2, Thu −9, Fri −6}; ex-turn-of-month lifts 0.92 and
  1.15; **cluster-robust z all below 1.5.** The "Monday" tilt decays monotonically by year:
  **62.5% → 52.1% → 43.8% → 34.4%.**
- **OPEX — dead AND confounded by construction.** Holding-day rate 32.68% vs 31.98% base = **1.02×**, and
  **Spearman(days_to_opex, tday_in_month) = −0.972** ⇒ "opex week" IS mid-month. Not a separate variable.
- **SEASONALITY — UNDERPOWERED, not absent.** Effective n is **44 months, not 88** (SPX/NDX
  month_total_pct correlate **+0.966**). **Detection floor ≈ 5.5pp; month-of-year F = 0.929.**
  ⇒ **44 months cannot resolve a month-of-year effect. This is a sample-size verdict, not a market verdict.**

## 📌 WHAT ROUND 2 MUST ASK
1. **🚩🚩🚩 Is the month-edge rhythm a REAL flow phenomenon or an artifact of monthly bucketing?**
   **The test: re-run the oracle on windows offset by ±7 and ±14 days.** If the edge concentration follows
   the arbitrary window boundary, it is my definition. If it stays on calendar month-ends, it is flows.
   **This is the single most important open question and it invalidates or promotes the headline.**
2. **🚩🚩🚩 THE EVENT CALENDAR — still the biggest data gap.** FOMC, CPI, NFP, opex-quarterly. "Fed" is
   currently reachable only through yields, and yields tested dead. **Fetchable from federalreserve.gov.**
3. **🚩🚩 Does `is_20d_low` + `NOT consec_up_days≥5` beat buy-and-hold OUT OF SAMPLE?** Everything above is
   in-sample description. **Nothing here has been traded, and I have not run it.**
4. **🚩🚩 Sell-side signature.** Round 1 was buy-heavy. **What marks the exits beyond "end of month"?**
5. **🚩 Intraday.** 13% of trades are same-day low→high. **Daily bars cannot say whether those are real.**

## ⚠️ THE HONEST FRAME
**This is a description of what perfect hindsight looked like, not a strategy.** The strongest result
(month-edge rhythm) may be an artifact of how I defined the month. The most tradeable result (RSI<25 →
+2.04% fwd 5d) has n=37 and finds only 15% of the good entries. **Everything macro — VIX, credit, rates —
tested as a proxy for price, not as information beyond it.**
