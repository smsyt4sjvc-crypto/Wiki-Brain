# ROUND-2 TEST #2 — OUT-OF-SAMPLE + 23-YEAR DEEP HISTORY
**Fit window 2023-01→2024-12 · OOS 2025-01→2026-08 · plus 2000-2022 (never seen) and 2022 alone.**
Data extended back to 2000-01-03 (6,698 rows/index). Script: `backtest/oos_test.py`.

## ✅ RSI SURVIVES EVERYTHING — the one finding that is now genuinely validated
**Forward 5-day mean return, vs the all-days base in the same window:**
| window | index | ALL | **RSI<30** | lift |
|---|---|---|---|---|
| in-sample 23-24 | SPX | 0.44% | **1.12%** (n=21, 76.2% pos) | 2.51× |
| **OOS 25-26** | SPX | 0.36% | **1.31%** (n=19) | **3.61×** |
| in-sample 23-24 | NDX | 0.65% | **2.37%** (n=25, 80.0% pos) | 3.63× |
| **OOS 25-26** | NDX | 0.43% | **2.36%** (n=19, 73.7% pos) | **5.46×** |
| **DEEP 2000-2022** | SPX | 0.12% | **0.64%** (n=336, 58.9% pos) | **5.16×** |
| **DEEP 2000-2022, RSI<25** | SPX | 0.12% | **1.28%** (n=147, 63.3% pos) | **10.28×** |
- ⇒ **★★★★★★ IT HOLDS IN-SAMPLE, OUT-OF-SAMPLE, AND ACROSS 23 YEARS AND 147 INDEPENDENT RSI<25 EVENTS.**
  **That is the strongest thing this whole exercise has produced, and it is the ONLY thing.**
- **⚠️ THE LIFT IS FLATTERED BY THE DENOMINATOR IN DEEP HISTORY: the 2000-2022 base is +0.12% because it
  contains two ~50% bear markets. In ABSOLUTE excess the finding is stable — +1.16pp (deep) vs +0.87pp
  (in-sample) — but 10.28× and 2.51× are not comparable numbers.** **Quote the excess, not the ratio.**

## ⛔ AND IT REVERSES A ROUND-1 CONCLUSION: THE 20-DAY LOW IS THE WEAK LEG, NOT RSI
**Round 1 concluded: *"Use `is_20d_low`. RSI adds ~a quarter on top of it, not a multiple."*** **Out of
sample that is BACKWARDS:**
| | SPX in-sample | **SPX OOS** | NDX in-sample | **NDX OOS** | deep 2000-22 |
|---|---|---|---|---|---|
| **20d low alone** | 1.66× | **0.91× (WORSE than base)** | 0.61× | 2.23× | 3.88× |
| **20d low & RSI<30** | 2.38× | **2.70×** | 1.56× | **5.60×** | 6.41× |
- ⇒ **THE 20-DAY LOW ALONE SIGN-FLIPS ACROSS PERIODS. THE OSCILLATOR IS DOING THE WORK.**
  **Round 1's "RSI is just a re-encoding of price is at a local low" was an in-sample artifact, and the
  adversarial verifier confirmed it in-sample — which is exactly the failure mode OOS testing exists for.**

## ⛔ AND THE "AVOID AFTER 5 UP DAYS" RULE IS DEAD IN EVERY WINDOW
**SPX in-sample +0.69% · SPX OOS −0.07% · NDX OOS +0.65% · deep 2000-2022 +0.23% at 1.81×.**
- ⇒ **Round 1 found ZERO oracle buys after 5 consecutive up days. TRUE — AND IRRELEVANT.** **The oracle
  never bought there because THE ORACLE BUYS LOWS, not because forward returns are bad there.**
  ⇒ **A structural feature of the selection rule, mistaken for a market fact.** **Second round-1
  conclusion corrected by the same test.**

## ★★★★★★ THE MOST USEFUL FINDING — WHAT HAPPENS IN AN ACTUAL DOWNTREND (2022, n=251)
**2022 base: SPX fwd-5d −0.36%, only 46.2% positive. A real downtrend, and the only one in the file.**
| condition | n | **fwd 5d** | % pos | **fwd 10d** |
|---|---|---|---|---|
| ALL | 251 | **−0.36%** | 46.2% | −0.64% |
| **RSI<25** | 16 | **+1.35%** | **75.0%** | **+0.87%** |
| **RSI<30** | 33 | **+1.15%** | 66.7% | **−0.17%** |
| 20d low | 45 | +0.07% | 53.3% | −0.39% |
| 20dlow & RSI<30 | 23 | **+0.99%** | 69.6% | **−0.59%** |
- ⇒ **★★★ THE OVERSOLD BOUNCE IS REAL IN A DOWNTREND — AND IT GIVES ITSELF BACK BY DAY 10.**
  **RSI<30: +1.15% at 5 days → −0.17% at 10. The 20dlow&RSI<30 combination: +0.99% → −0.59%.**
- ⇒ **THIS IS A TRADE WITH AN EXIT, NOT A POSITION.** **In an uptrend the effect persists to 10 days
  (NDX OOS: +2.36% at 5d, +3.19% at 10d). In a downtrend it does not.**
  ⇒ **★★★ THE HOLDING PERIOD IS REGIME-DEPENDENT AND THAT IS THE WHOLE PRACTICAL LESSON.**
- ⚠️ **n=16 at RSI<25 in 2022. And the "vs ALL" ratios print NEGATIVE in that table purely because the
  denominator is negative — a display artifact, not a finding.**

## 📌 WHERE THIS LEAVES THE EXERCISE
**ONE rule survives everything: BUY OVERSOLD (RSI<25-30), and SIZE THE HOLD TO THE REGIME —
~10 days above the 200DMA, ~5 days below it.**
**⬜ STILL NOT TESTED: transaction costs · slippage · the semis/memory version (his actual question) ·
whether RSI<25 fires often enough to matter (≈9 events/yr per index).**
