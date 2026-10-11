# Vol divergence: where the options market disagrees with the vault's expression

One idea: for every name the vault has a view on, compare what the OPTIONS market charges (30-day implied
volatility, iv30) with how the stock has actually MOVED (realized volatility, rv20/rv60) — then ask whether
the vault's expressed view is cheap or expensive to own. Cheap vol + a vault view + a dated catalyst = buy
the option; rich vol + a vault view = own shares or sell premium; rich vol + no catalyst = the market is
paying for an event that keeps not arriving. Built 2026-10-04 on Jake's ask ("volatility vs real prices").
Related: [[earnings-implied-moves]] (the print-specific version) · [[where-the-edge-is]] (the vol risk
premium) · [[data-sourcing-playbook]] (IV/RV rules) · [[market-fragility]] (index vol vs correlation) ·
[[money-board]] · [[flag-board]] · [[forest]].

> Firewall: DATA = the snapshot (dated, sourced). THESIS = which side of the vol the vault's view sits on.

## DATA (observed) — snapshot as of the 2026-10-02 close
*Sources: CBOE delayed quotes (`cdn.cboe.com/api/global/delayed_quotes/options/<TK>.json`, keyless; iv30 =
CBOE's 30-day implied, straddle = ATM bid/ask mid for the named expiry) · realized vol = close-to-close
log returns from Yahoo daily bars via `tools/tape.py`, annualized (rv20 = 20 sessions, rv60 = 60) · full
table `raw/2026-10-04-iv-vs-rv-snapshot.csv` (49 names). Index gauges 10/2 close: VIX 15.31 · VIX9D 12.06 ·
VIX3M 18.01 · VVIX 87.0 · SKEW 144.9 · OVX 51.0 · MOVE 107.29 · GVZ 23.2.*

| name | px | iv30 | rv20 | rv60 | iv−rv20 | iv/rv60 | straddle through | vault view (10/4) |
|---|---|---|---|---|---|---|---|---|
| SPY | 769.64 | 12.4 | 10.3 | 11.1 | +2 | 1.12 | Fri 10/9 ±1.15% | hedge (745P ACTUAL); THE LOOP IF met |
| QQQ | 749.55 | 18.7 | 15.0 | 18.7 | +4 | 1.00 | Fri 10/9 ±1.72% | "match the hedge to the leaders" (10/2) |
| TLT | 77.53 | 15.6 | 10.3 | 10.0 | +5 | 1.56 | 10/9 ±1.59% · 10/14 ±2.08% | BEAR 1 |
| LEN | 80.33 | 41.4 | 39.5 | 35.2 | +2 | 1.18 | 10/9 ±5.0% · 10/16 ±6.6% | BEAR 2 (heaviest on the board) |
| DHI | 135.00 | 39.0 | 27.0 | 32.2 | +12 | 1.21 | 10/16 ±5.15% | BEAR (with LEN) |
| PARR | 84.80 | 62.8 | 39.6 | 62.3 | +23 | 1.01 | 10/16 ±8.55% | BULL 1; ACTUAL long + short $80C |
| DINO | 113.36 | 55.3 | 37.8 | 37.7 | +17.5 | 1.47 | 10/16 ±8.56% | BULL 2 |
| VLO | 406.30 | 50.7 | 38.3 | 33.8 | +12 | 1.50 | 10/9 ±5.3% · 10/16 ±7.5% | BULL 1 (grade 9, frozen) |
| MPC | 422.33 | 48.7 | 37.0 | 35.3 | +12 | 1.38 | 10/16 ±7.15% | BULL 1 (grade 9, frozen) |
| PBF | 80.97 | 71.5 | 60.6 | 67.3 | +11 | 1.06 | 10/16 ±10.9% | BULL 1 |
| DHT | 23.68 | 55.8 | 35.7 | 36.6 | +20 | 1.53 | 10/16 ±8.66% | BULL 1 (flag fired 10/4) |
| FRO | 51.43 ⚠️ CBOE snapshot stale — Yahoo 10/2 close 52.74 (money-board 10/4 9:00pm) | 49.4 | 38.4 | 38.5 | +11 | 1.28 | 10/16 ±8.2% | BULL 1 (10/4) |
| UAL | 112.25 | 53.1 | 34.4 | 37.9 | +19 | 1.40 | 10/9 ±6.8% | BEAR 1 (tanker mirror) |
| BNO | 63.10 | 53.5 | 45.2 | 51.0 | +8 | 1.05 | 10/9 ±5.0% · 10/16 ±8.0% | bear 0.5 / bull 0.5 → net 0 |
| RTX | 184.95 | 30.5 | 12.3 | 23.2 | +18 | 1.31 | 10/16 ±3.65% | bull 1 (SM-6) vs primes bear 0.5 |
| LMT | 506.98 | 30.1 | 18.0 | 30.5 | +12 | 0.99 | 10/16 ±4.35% | bull 0.5 / bear 0.5 |
| KTOS | 43.20 | 57.4 | 28.2 | 54.7 | +29 | 1.05 | 10/16 ±8.45% | flat 0.5 |
| AVAV | 140.90 | 55.0 | 45.8 | 59.1 | +9 | 0.93 | 10/16 ±8.1% | flat 0.5 |
| ONDS | 7.29 | 64.0 | 35.3 | 77.6 | +29 | 0.82 | 10/16 ±10.2% | bull 1 |
| LTRX | 7.22 | 80.9 | 48.2 | 64.4 | +33 | 1.26 | 10/16 ±10.7% | bull 1 / bear 1 |
| MU | 1,069.18 | 48.8 | 50.8 | 75.2 | −2 | 0.65 | 10/9 ±4.9% · 10/14 ±6.3% | BULL (💰 #1, 9/23) |
| NVDA | 234.22 | 29.0 | 24.8 | 38.5 | +4 | 0.75 | 10/9 ±2.9% | bull 1 (9/23) / bear 0.5 (9/30) |
| AVGO | 355.10 | 35.2 | 33.1 | 38.0 | +2 | 0.93 | 10/9 ±3.7% | nets 0; CDS test >131.6 thru 10/9 |
| ORCL | 142.37 | 52.1 | 46.6 | 55.7 | +5.5 | 0.93 | 10/16 ±7.3% | bear 1 (PAPER short) |
| CRWV | 89.40 | 69.9 | 69.6 | 97.4 | +0.3 | 0.72 | 10/16 ±10.3% | BEAR 1 (CDS 849.8) |
| NBIS | 242.98 | 74.2 | 64.8 | 126.0 | +9 | 0.59 | 10/16 ±10.9% | BULL 1 (new fleet) |
| IREN | 41.70 | 72.0 | 58.8 | 104.3 | +13 | 0.69 | 10/16 ±10.7% | bear 0.5 |
| META | 727.65 | 42.2 | 55.2 | 47.2 | −13 | 0.89 | 10/9 ±3.6% | flat 0.5 |
| GOOGL | 343.25 | 34.7 | 26.1 | 34.9 | +9 | 0.99 | 10/9 ±2.9% | bull 0.5 |
| MSFT | 517.19 | 32.1 | 22.2 | 38.4 | +10 | 0.84 | 10/9 ±2.6% | bull 0.5 |
| AMZN | 251.39 | 38.2 | 21.4 | 40.3 | +17 | 0.95 | 10/9 ±2.8% | flat 0.5 |
| CEG | 258.80 | 44.1 | 41.6 | 36.2 | +2.5 | 1.22 | 10/16 ±6.6% | flat 0.5 / bull 0.5 |
| VST | 143.96 | 45.4 | 31.0 | 40.0 | +14 | 1.13 | 10/16 ±7.05% | flat 0.5 / bull 0.5 |
| TLN | 320.50 | 52.2 | 45.8 | 50.7 | +6 | 1.03 | 10/16 ±8.1% | flat 0.5 |
| BE | 287.22 | 79.4 | 90.0 | 106.8 | −11 | 0.74 | 10/16 ±10.4% | bear 1 (9/24) / bull 0.5 (9/26) |
| OKLO | 35.97 | 65.1 | 69.7 | 82.1 | −5 | 0.79 | 10/16 ±9.7% | bear 0.5 |
| HYG | 76.91 | 7.5 | 3.9 | 3.7 | +3.6 | 2.02 | 10/16 ±1.1% | BEAR 2 |
| KRE | 70.78 | 25.1 | 14.4 | 15.5 | +11 | 1.62 | 10/16 ±4.1% | bull 0.5 / bear 0.5 |
| GLD | 380.14 | 20.6 | 21.3 | 24.9 | −1 | 0.83 | 10/9 ±2.0% | NR ("referee, not hedge") |
| CCJ | 85.69 | 45.7 | 27.6 | 41.4 | +18 | 1.10 | 10/16 ±6.4% | lean bull (existing fleet + fuel) |
| EWZ | 38.19 | 60.3 | 22.2 | 23.3 | +38 | 2.59 | 10/9 ±7.6% | NR (election 10/4) |

- **Term structure:** VIX9D 12.1 < VIX 15.3 < VIX3M 18.0 — the index prices the auction week (10/6-10/8) as
  nothing; the SPY straddle through Friday is ±1.15%.
- **MOVE/VIX ≈ 7.0** (vault 9/25: 76-79th percentile; median 5.32) — rates vol stressed, equity vol asleep.
- **ICC CDS 10/2:** CRWV 849.8 · ORCL 247.0 · AVGO 130.8 · META 100.2 · NVDA 85.4 · MSFT 51.6 (`tools/icc_cds.py`).
- ⚠️ Perimeters: iv30 is CBOE's blended 30-day number; rv is close-to-close (no gaps intraday); a straddle
  mid on thin names (LTRX, ONDS, SWMR) carries wide spreads; CBOE quotes are delayed, taken after Friday's close.

## THESIS (interpretation, NOT fact)
- **(analysis) Where the vault's view is CHEAP to own — implied below realized, or far below the stress the
  vault measures elsewhere:**
  1. **Index puts (SPY/QQQ).** The vault's most corroborated stress read (MOVE 107, CDX IG 50→60, ICE IG 86 /
     HY 324 / CCC 1,215 through the registered thresholds, THE LOOP's IF met 10/2) against VIX 15 and record-low
     correlation (COR1M ~7.5). This is the board's own 9/25 line — "own the cheap index hedge rather than press
     index shorts" — and the 10/2 refinement: the leaders (QQQ) are the matching hedge. **It is a hedge that
     needs VIOLENCE, not direction:** ~60% of a shock's payoff is the vol leg ([[dip-buying-base-rates]] L93-106).
  2. **MU.** iv30 48.8 vs rv60 75 (0.65) — the only large AI name where implied sits below realized; the
     vault's #1 cumulative bull; [[earnings-implied-moves]]: MU realized MORE than implied in 3 of 4 prints;
     Samsung prelim (~10/7-10/14) and TSMC September sales (~10/10) inside the window.
  3. **CRWV puts.** iv 70 ≈ rv20 70 but rv60 97 — the vault's strongest bear (CDS 849.8, ~40-45% implied
     default; the ~36-point book-vs-recontract gap lands on equity) is not expensive to own; but no dated
     catalyst inside 10/5-10/16 (next raise undated; CME curve TBA) and the tape keeps bidding it (+10.7% 1m).
     *(same day, later)* The first dated observable is now on file: DDTL 5.0 amortisation begins Nov-2026 and the Q3 10-Q (early Nov) shows it — match a CRWV put's expiry to mid-November or later ([[ai-financing-fragility]] 10/4 🗓️).
  4. **META** is the cheapest vol in the table (42 vs 55) — and the vault has no view strong enough (flat 0.5).
     *(same day, later)* A dated stack now attaches — Watermelon (October target, reported) + Q3 (~10/28, inferred): direction still a coin flip on the vault's record, magnitude likely ⇒ a small Nov-20 strangle is the vol-consistent shape, not a call ([[compression-thesis]] 10/4 🍉).
- **(analysis) Where the vault's view is RICH to own — shares or sold premium, not bought options:**
  - **Refiners** (PARR +23, DINO +17.5, VLO/MPC +12 over realized): the sold PARR $80 call is on the right side
    of this; DINO/VLO adds belong in shares with the +3/−3 bracket. The market is paying for the China/ban
    binary the vault already carries as flags.
  - **Tankers** (DHT +20, FRO +11; iv/rv60 1.5): the war premium is priced into freight AND into the options;
    shares with the bracket, or a covered call to collect it.
  - **TLT** (1.56× 60-day realized) and **HYG** (2.0×): the rates and credit bears are EXPENSIVE through their
    own ETFs' options — LEN puts (iv ≈ rv) are the fair-priced expression of the same rates view.
  - **Defense/drones** (KTOS +29, ONDS +29, RTX +18 over realized): the OPPOSITE divergence — options priced
    for an event that keeps not arriving while the names stop moving (XAR −22% from 8/14 against a 243×
    budget line). Buy nothing optional there; the cause of the slide is ⬜.
- **(analysis) The single largest price-vs-expression gap on the board is the index:** credit and rates
  price the AI-financing stress the vault has documented; equity options price nothing. Either credit snaps
  back after issuance (the vault's registered risk) or correlation jumps and the index put pays. The base
  rates argue for humility: the VIX-priced option wrapper loses ~29% of premium on average and 57% expire
  worthless (n=375, 1975-2026, [[momentum-extrapolation-backtest]]); VIX episodes under 30 days have never
  preceded a bear (0/14, [[fear-duration]]); "rotation regime = the worst environment for an index put"
  ([[precedent-bid]]). ⇒ hedge, not bet; size it as insurance.
- **Rules carried (not new):** buy options only when IV/RV < ~1.0 with a dated catalyst and an expiry past it;
  IV/RV > ~1.5 = rich; never buy straddles into events or war commodities ([[data-sourcing-playbook]],
  [[retail-edge]]); a short-dated put on a "flashing" STATE dies to theta — name the DATE ([[_calibration]]).

## 📌 OPEN
- ⬜ re-pull the snapshot after the auctions (10/8 close) — does MOVE/VIX converge, and from which side?
- ⬜ COR1M/COR3M print (CBOE implied correlation) — the "off switch" is a jump above ~0.4-0.5.
- ⬜ IV percentile ranks (the table has levels, not ranks); CBOE `iv30_change` fields were zero on the weekend pull.
- ⬜ the first week of CME H100 futures open interest (readout for CRWV/NBIS), launch TBA.

**Links:** [[money-board]] · [[flag-board]] · [[forest]] · [[earnings-implied-moves]] · [[market-fragility]] · [[rates-board]] · [[portfolio-state]]

- *(⛔ scored 2026-10-05 ~8:20am PDT — Brazil first round Sun 10/4: Bolsonaro 47.0% vs Lula 45.2%, runoff Oct 25; EWZ 43.12 at 7:58am PT = **+12.9%** vs Fri 38.19; ZH 10/5 lists Brazilian ADRs +6 to +15% pre-market, `raw/2026-10-05-zh-scan-0800.md`)* **THE TABLE CALLED EWZ "THE RICHEST VOL ON THE BOARD" (iv30 60 vs realized 22; Oct-9 straddle ±7.6%). THE EVENT MOVED 1.7× THE STRADDLE IN ONE SESSION. THE FRAME WAS WRONG FOR A BINARY: implied-vs-REALIZED-HISTORY says nothing about an election whose outcome distribution is bimodal — the right comparison was implied move vs the plausible outcome gap (a Bolsonaro lead vs a Lula lead ≈ a 20%+ swing in the index), and on that test 7.6% was CHEAP.** Lesson filed to [[_calibration]] shape: for dated binaries, rank vol against the outcome gap, not against trailing realized; "rich" needs a denominator that contains the event. Names on the table with a dated binary inside their window and the same exposure: PSKY (financing close 10/6), KTOS/AVAV (budget), MU (Samsung prelim) — re-rank before the next menu. No position was taken (NR), so the error cost nothing but is logged as a MISS of the table's own stated purpose.
