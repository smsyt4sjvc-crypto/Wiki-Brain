# WHERE'S THE MONEY — the money board (rule 16d)

**Adopted 2026-09-23 (Jake: "Where should the money be… I don't care if it's autos, retail,
consumer staples, energy, ect. I care about money.").** Replaces the 1-10 number of rule 16c;
[[grades]] is frozen as history. Daily top 5 → [[forest]]. Links: [[rates-board]] ·
[[war/war-board]] · [[oil-value-chain]] · [[demand-destruction]] · [[ai-financing-fragility]].

## HOW IT WORKS
  ⟲ SUPERSEDES grades.md:L1 — rule 16d (9/23): the 1-10 number retired; bear/flat/bull marks x sensitivity replace it; this ledger frozen as history
- **Three columns per name — BEAR · FLAT · BULL.** Every data input drops a mark in one column
  for EVERY name it implicates, any sector, held or not. Each mark carries date + pointer.
- **Weights = the evidence ladder (rule 9):** **2** MEASURED (auction, filing, print) · **1**
  confirmed event · **0.5** REPORTED / talks-stage. **A lagged echo of an already-marked shock
  takes the lower weight (anti-double-count).** FLAT = an input that touches the name both ways.
- **Marks expire after 120 days** (the 16c window). The `5d` column = net marks added in the last
  week (momentum).
- **Ranking: score = (bull − bear) × |sensitivity|**, sensitivity = the name's % move on a
  1-sigma day of the driver behind its heaviest marks, 60 sessions. **Top 5 by |score| — longs
  AND shorts, direction labelled.**
- **Drivers (ETF proxies):** TLT rates · BNO Brent · BWET tanker freight · SOXX semis · SPY market.
- **Ledger:** `data/money/marks.csv` · **tool:** `python3 tools/money_board.py` (zero-token;
  Nasdaq historical prices).
- **Cadence: run at the close, IN SESSION — Jake's closing-scan paste is the trigger.** No
  cron/Routine exists or may be created without his explicit same-conversation yes (rule 15).

### ⛔ TWO DESIGN FINDINGS FROM THE FIRST RUN (2026-09-23) — built into the tool
- **Raw beta is not comparable across drivers.** TLT's low variance handed every volatile name a
  beta of ~2 to it (ORCL 1.99, CVNA 2.08). ⇒ **score on beta × driver sigma (% per 1σ day) and
  print CORRELATION; |corr| < 0.2 is flagged "weak link."**
- **Tankers trade on FREIGHT, not crude:** FRO/DHT/INSW/STNG/TRMD vs BNO corr 0.08-0.18; vs BWET
  0.32-0.58. ⇒ **the driver must be what the name actually trades on, not what the story says.**

### ⭐ CUMULATIVE, NOT DAILY (Jake, 2026-09-23 3:48pm: "The rankings are accumulative not daily")
- The ranking is the **running 120-day sum of marks**, not the day's inputs. **Backfilled 9/23 from the frozen 16c
  ledger** so September's record counts: grade **9 → +3 bull · 8 → +2 · 7 → +1 · 6 → FLAT 1 · 5 → −1 bear · 4 → −2 ·
  ≤3 → −3**, each dated to its grade date (so it expires on schedule); 50 names; pointer = the grades.md row.
- **The registered book** (`data/money/book.csv`) is scored at every close: `python3 tools/money_board.py --book`.

## THE IMPLICATION MAP (THESIS — analysis; the tape's correlation column validates or kills each link)
*Event class → who it implicates, both directions, any sector. Grows with every new event type.*
- **SHIPPING / CHOKEPOINT CONSTRAINED (Hormuz, Red Sea):** BULL crude tankers FRO/DHT/INSW ·
  product tankers STNG/TRMD · US refiners VLO/MPC (freight wedge) · US Gulf petchem DOW/LYB (ethane
  vs Asian naphtha). BEAR airlines UAL/DAL · cruise CCL/RCL. ⬜ import-heavy retail (freight cost).
- **TREASURY AUCTION TAILS / REAL-RATE SHOCK:** BEAR homebuilders DHI/LEN · mortgage RKT ·
  subprime auto CVNA · levered AI periphery ORCL/CRWV · DC REITs DLR/EQIX · small caps IWM.
  BULL (theory) life insurers MET/PRU · SCHW — ⚠️ **tape corr ≈ 0 on 9/23: weak links.**
- **AUCTION CLEARS WITH NO TAIL / YIELDS FALL:** the mirror — the BEAR list above becomes the BULL list.
- **IG SPREADS TIGHTEN (flatten):** BULL AI-periphery issuers ORCL/CRWV · private-credit managers
  APO/BX/ARES/OWL · issuance-dependent capex chain. **IG WIDENS:** the mirror.
- **US DIESEL EXPORT BAN:** BEAR VLO/MPC/PSX/PBF (the cap). BULL domestic diesel users ODFL/JBHT
  ⭐ *(9/23 ~7:55pm, second-order, CONDITIONAL — mark only if the ban FIRES)*: BULL **MUSA** (retail margin — wins flat or partial, waiver or not) · **KEX** (Jones Act barges — ONLY under a flat ban; a waiver erases it) · **GLP** (storage contango + NE retail) · partly priced SUN/CASY/BP/SHEL · BEAR **DAR** (renewable-diesel margin). → [[demand-destruction]] ban #4 addendum.
- **REMOTE-ACCESS LOOPHOLE CLOSES (chips rented offshore by Chinese firms):** BEAR neoclouds with offshore Chinese tenants (Nscale pre-IPO; ⬜ others) + their lenders · WATCH NVDA (back-door demand + capacity backstop) · the IPO-window channel: a stalled neocloud IPO → BEAR CRWV/NBIS/IREN equity. → [[ai-financing-fragility]] 9/23 Nscale.
- **STATE PERMIT HALT / MORATORIUM (Texas 9/21):** BEAR developers + neoclouds with builds in the state (IREN/CIFR/WULF in TX) · BEAR the state's load-growth generators (VST/CEG in ERCOT) · BEAR tenants with unbuilt commitments there (ORCL/Abilene) · orders slip for on-site power (GEV/BE/CAT) · BULL energized, permitted capacity anywhere. → [[buildout-bottleneck-map]] 9/24.
  (weak corr to Brent). Europe's crack up (not investable here).
- **CHINA LOCALIZATION STEP (survey → guidance → ban):** BEAR AVGO/NVDA/AMD; domestic winners
  (Huawei/H3C) not US-listed.
- **HOT PMIs + INPUT COSTS:** BULL industrials CAT/ETN. BEAR staples/discount-retail margins
  PG/KO/DG/TGT (⚠️ corr ≈ 0 to SPY — these are defensive; they move on their own margins).
- **HYPERSCALER GUARANTEE / BACKSTOP:** BULL developer-lenders APO · TPU chain AVGO. FLAT GOOGL
  (TPU volume vs contingent liability).

## DAILY LOG

## 2026-09-23 ~3:30pm PDT — 💰 FIRST RUN: THE RATE SHOCK OWNS THE BOARD — HOMEBUILDERS AND AIRLINES SHORT, ETN THE ONE LONG
  ⟲ SUPERSEDES forest.md:L200 — rule 16d: the money board's longs+shorts replace the rotation basket (kept as history)
  ⟲ SUPERSEDES forest.md:L186 — rule 16d: the daily money-board top 5 replaces the confidence basket (kept as history)
**DATA (tool run; 44 marks · 39 names · 8 inputs):**
- **Inputs marked:** 5Y RED + real-rate shock (2) · Hormuz strike + VLCC ~2× record (2) · freight
  wedge (2) · diesel-ban rehearsal (1) · flash PMIs 58.4 (2) · MBA 7.12% (1, echo) ·
  Anthropic/Stream (0.5, reported; vendor conflict named) · SASAC Broadcom (0.5, reported).
- **💰 TOP 5 (score = net × % per 1σ driver day):**
  1. **DHI BEAR** — net −3 · +1.26%/1σ TLT (corr +0.59) · score −3.77
  2. **LEN BEAR** — net −3 · +1.21%/1σ TLT (corr +0.53) · score −3.64
  3. **UAL BEAR** — net −2 · −1.71%/1σ BNO (corr −0.73) · score −3.42
  4. **ETN BULL** — net +2 · +1.58%/1σ SPY (corr +0.53) · score +3.16
  5. **CCL BEAR** — net −2 · −1.48%/1σ BNO (corr −0.71) · score −2.96
  *Next: DOW/LYB bull 2.88/2.84 · DHT bull ~2.9 (BWET) · CAT bull 2.73 · DAL bear 2.62.*
- **Day-0 consistency (regular session, Nasdaq, 4:00pm ET): DHI −2.78% · LEN −1.84% · UAL −3.90%
  · CCL −2.13% · ETN −0.76%. ⇒ 4 of 5 moved the marked direction; ETN (bull) fell.**
  ⚠️ **NOT a forecast test — the marks were made AFTER the moves. The forward test starts tomorrow.**

**THESIS (analysis):**
- **The day's money was in the RATE channel and the FUEL channel, not the AI channel.** The two
  AI inputs were reported-rung (0.5) and AVGO netted to zero (TPU bull vs SASAC bear).
- **The weak links are the finding:** KRE, MET, PRU, SCHW, PG, TGT, DG carry marks but ~0
  correlation to their drivers over 60 sessions ⇒ **in this regime the "obvious" rate and margin
  trades in financials and staples are not where the money moves.**

**📌 REGISTERED:** 🔴 9/24 close = the first FORWARD test of this top 5 · the 7Y auction, ICE 9/23
OAS, SoftBank pricing and the Xi readout are tomorrow's inputs · ⬜ pointers into chat-log update
when the pending entries file.

### Addendum 2026-09-23 ~4:00pm PDT — **RERUN AFTER THE AFTERNOON INPUTS (58 marks · 46 names): ORCL AND DHT ENTER, ETN AND CCL DROP OUT.**
- **New marks:** ICE CDS 12/12 wider → BEAR ORCL/CRWV (w=1, TLT) · AVGO CDS +6.8 → BEAR AVGO (w=1, SOXX) · Rezaei Gulf-airport threat → BEAR UAL/BA, BULL RTX/LMT/NOC (w=0.5) · Rezaei 4-5 day Hormuz ultimatum → BULL FRO/DHT/INSW (w=0.5, BWET) · truce extension (REPORTED) → BULL AAPL/TSLA/NKE (w=0.5).
- **💰 TOP 5 (9/23 close, final):** 1. **UAL BEAR** −4.27 (BNO, corr −0.73) · 2. **DHI BEAR** −3.77 (TLT, +0.59) · 3. **LEN BEAR** −3.64 (TLT, +0.53) · 4. **ORCL BEAR** −3.63 (TLT, corr +0.35) · 5. **DHT BULL** +3.60 (BWET, +0.58). *Out: ETN +3.16 · CCL −2.96.*
- **THESIS:** the board now reads **short the rate channel (homebuilders, ORCL) and the fuel channel (airlines), long freight (DHT)** — every name in it has |corr| ≥ 0.35 to its driver. **Forward test: the 9/24 close.** AVGO nets −1 (TPU +0.5 · SASAC −0.5 · CDS −1).

## 📒 REGISTERED BOOK — 2026-09-23 (Y'd 3:54pm; Jake: "top overall stocks to be holding right now with target returns and exit strategy aimed at maximum volatility, momentum and event harvesting")
**RULES:** stop = one weekly σ (σd20 × √5), CLOSING basis · half off at T1, stop → breakeven, trail one weekly σ · **the event exit overrides price.** Entries = 9/23 regular-session closes (Nasdaq). Sizing is Jake's.

| | name | entry | stop | T1 / T2 | vol · momentum · event | event exit |
|---|---|---|---|---|---|---|
| L1 | **DINO** | 106.11 | 100.4 (−5.4%) | 116.6 (+10%, high retest) / 123 (+16%) | σd 2.4% · 3M +62%, +11% vs 50DMA · grade 8 · INLAND = least export-ban exposure | flat ban fires Fri 9/25 → out |
| L2 | **DHT** | 21.28 | 20.00 (−6.0%) | 23.27 (+9%) / 25.1 (+18%) | σd 2.7% · +9% vs 50DMA · freight corr 0.58 · VLCC ~2× record | verified Hormuz transits resume → out |
| L3 | **MU** | 1,071.88 | 995 (−7.2%) | 1,160 (+8%) / 1,214 (+13%, prior high) | σd 3.2% · 1M +13% · grade 8 · earnings 9/30 | sell into the print (by 9/30 close) |
| S1 | **UAL** | 110.72 | 116.7 (+5.4%) | 99.6 (−10%) / 94.1 (−15%) | σd 2.4% · corr −0.73 to Brent · Gulf-airport threat | Hormuz reopening → cover |
| S2 | **ORCL** | 144.56 | 154.5 (+6.9%) | 130.1 (−10%) / 118.5 (−18%) | σd 3.1% · −40% off high · CDS 224 | SoftBank inside guidance AND IG OAS flat 9/24 → cover |
| S3 | **LEN** | 81.53 | 86.1 (+5.6%) | 75.0 (−8%) / 70.1 (−14%) | σd 2.5% · rate channel corr +0.53 | 7Y no tail AND 10Y < 5.0 close → cover |

*Alternates: VLO (grade 9, full ban exposure) · FRO (σd 2.9%, −11% off high) · CRWV short (σd 4.4%, but corr 0.16 = weak link, squeeze risk).*
**⛔ THE BOOK IS TWO BETS, NOT SIX:** DINO + DHT + UAL-short = **"Hormuz stays shut"** (a verified reopening hits all three — long tankers / short airlines is NOT a hedge); ORCL + LEN shorts = **"real rates stay high"** (a clean 7Y + 10Y < 5.0 hits both); MU is the only independent leg. Both clusters are tested within days (7Y 9/24 · ban 9/25 · Rezaei ~9/27-28) — by design.
**⚠️ Evidence limits:** marks ledger started 9/23; the stop/target rules are vol-scaled conventions, NOT back-tested; no forward score yet.
**📌 SCORED AT EVERY CLOSE** (`--book`) — hits, stops and event exits logged here, losers as loudly as winners.

### 2026-09-23 ~4:00pm PDT — 💰 FIRST CUMULATIVE RUN (grades backfill + 9/23 inputs; 108 marks) — **THE MECHANICAL BOARD AND THE REGISTERED BOOK DISAGREE, AND THE DISAGREEMENT IS INFORMATIVE**
- **DATA — TOP 10 (cumulative):** 1. **MU BULL** +8.72 (SOXX, corr +0.86) · 2. CRWV BEAR −6.48 (TLT, corr +0.16 ⚠️ weak link) · 3. **RGTI BEAR** −6.46 (SPY, +0.64) · 4. **QBTS BEAR** −6.42 (SPY, +0.57) · 5. **DELL BULL** +6.35 (SOXX, +0.61) · 6. **ORCL BEAR** −6.04 (TLT, +0.35) · 7. TSLA BEAR −5.83 · 8. OKLO BEAR −5.24 · 9. ETN BULL +4.74 · 10. TSM BULL +4.64 (SOXX, +0.90). Book names outside the top 10: UAL −4.27 · LEN −3.64 · DHT +3.60 · MPC +2.95 · VLO +2.79 · **DINO +1.38.** No prices: EWY, SBE.
- **THESIS (analysis):** (1) **⛔ THIRD DRIVER MIS-SPECIFICATION — REFINERS TRADE ON THE CRACK, NOT CRUDE** (VLO/MPC/DINO vs BNO corr 0.27-0.33; the vault's own 9/17 quadrant-one rule: *"track VLO/MPC/PSX vs cracks not crude"*). **The refiners are under-scored by construction; no free crack ETF exists (CRAK is a refiner basket = self-referential) ⬜.** (2) **High-β speculative bears (RGTI/QBTS/OKLO) rank on 3-week-old grades with ZERO fresh inputs** — the 120-day window holds them at full weight. (3) The book was built on EVENT PROXIMITY; the score has no event term. ⇒ **MU and ORCL are where board and book agree.**
**📌 PROPOSED (not adopted — rule 22):** time-decay on marks (half-life ~20 sessions) · an event-proximity term · a crack driver for refiners.

## 2026-09-23 ~5:10pm PDT — 🧭 CURVE EXPOSURE + ⚠️ YELLOW BACKSTOP FLAGS (Jake: "a flag on which bonds that particular hyperscaler is more exposed to… a yellow flag for backstop structures")
- **Tool:** `tools/curve_exposure.py` (SEC XBRL maturity tables, free) + `data/money/curve_overlays.csv` (floating debt, new issues, and ⚠️ YELLOW backstops/guarantees/RVGs with pointers). **An auction result → proposed marks** on the names whose NEXT money sits at that tenor, weighted by **refinancing need ÷ market cap** (≥10% → w 1.0 · 2-10% → 0.5 · <2% → none). Tail → BEAR, stop-through → BULL, |tail| < 0.5bp → no marks. Default is print-only; `--write` appends.
- **Model (v2, fixed on the first run):** maturities due ≤2y are refinanced at the tenor the name ISSUES at (fortress IG long · crossover belly+long · HY belly); floating reprices at FRONT; YELLOW overlays count half. v1 marked TSLA/CIFR full-weight and CRWV half on the 5Y — backwards — because it used the tenor debt matures FROM and ignored size.
- **DATA — debt due ≤2y ÷ market cap:** **CRWV $10.6B = 22.1%** · CIFR 6.7% · **ORCL $17.4B = 4.0%** (+ ⚠️ Jupiter $18B floating, ⚠️ $3.3B lessor guarantee maturing Sep-26) · DELL 2.3% · INTC 1.0% · AMZN 0.4% · AVGO 0.3% · META 0.2% · MSFT 0.2% · GOOGL 0.1%. NVDA: no XBRL maturity table. WULF: stale XBRL.
- **Back-test on 9/23's 5Y (+3.2bp), NOT written (the rate shock is already marked — anti-double-count):** CRWV bear w=1.0 (27.5% of cap incl. the floating DDTL) · CIFR / ORCL / DELL bear w=0.5 · GOOGL's backstops = 0.5% of cap → no mark.
- **THESIS (analysis):** **the same auction is very different money by name — the belly failure is a CoreWeave event, an Oracle event at half strength, and a non-event for the fortress five.** The yellow flags matter to the BACKSTOPPED (the startups' paper at ~7.75-10%), not to the backstopper's equity. **First live use: tomorrow's $44B 7Y.**

## 2026-09-24 close — 📒 **THE BOOK'S FIRST SCORED CLOSE: +0.9% AVERAGE, 4 OF 6 IN FAVOUR, NOTHING NEAR A STOP — AND THE ORCL COVER RULE IS HALF-FIRED.**
- **DATA (`--book`, 9/24 closes):** DINO 105.79 (−0.30%) · DHT 21.68 (+1.88%) · MU 1,080.53 (+0.81%) · UAL short 111.19 (−0.42%) · **ORCL short 139.54 (+3.47%)** · LEN short 81.47 (+0.07%) ⇒ equal-weight **+0.92%**. All live; no stop within reach.
- **⚖️ ORCL EVENT EXIT:** rule = "SoftBank prices inside guidance AND IG OAS flat on 9/24." **SoftBank half FIRED (priced at/inside the tight end); the IG half = ICE's 9/24 print (published 9/25).** But Jupiter's force-majeure notice is NEW Oracle-specific bear news the rule did not anticipate. **Proposal (Jake's call on size): if IG is flat, cover HALF per the rule, hold half for Jupiter.**
- **LEN:** barely moved (+0.07%) through a +22bp two-day 10Y — homebuilders are NOT tracking the rate shock this week; watch. Cover rule not met.
- **New marks:** ORCL bear w=1 (Jupiter force majeure) · AAPL/TSLA/NKE bull +0.5 (truce CONFIRMED — upgrade). 7Y curve marks (half strength) and the Safavi threat marks filed earlier today.

### 2026-09-24 ~8:05pm PDT — ⚖️ **ORCL: JAKE HOLDS THE FULL SHORT — A DELIBERATE OVERRIDE OF THE REGISTERED HALF-COVER RULE.**
- **The rule** (registered 9/23): cover if SoftBank prices inside guidance AND IG OAS is flat on 9/24. SoftBank half FIRED; the IG half = ICE 9/24 (published 9/25).
- **Jake's call (8:03pm): HOLD, whatever ICE shows.** **Reason on record:** the rule was built on SECTOR credit fear easing; the new risk is ORACLE-SPECIFIC and outside its logic — Jupiter's carry cost (Oracle pays up to 3 yrs for possibly dark capacity; FT) + the Texas permit freeze (Abilene's later phases).
- **Scoring note:** from here the ORCL leg is scored as an override — if it gives back gains after ICE prints flat, that is logged against the override, not the rule. The stop (154.5, closing basis) still governs.

### 2026-09-25 (Y'd) — ✔ CORRECTION TO THE ORCL "OVERRIDE": THE RULE WOULD NOT HAVE FIRED.
- The cover rule required IG OAS **FLAT on 9/24**. ICE 9/24: **IG 79 (+2)** ⇒ the IG half did NOT fire ⇒ the registered rule would not have covered. **Jake's HOLD is rule-consistent; the ORCL leg is scored on the rule, not as an override** (the 9/24 override note stands as the record of intent). ORCL CDS 228 (+13 since 9/22).
- New marks: AVGO bear 0.5 (CDS +10 in two days) · DINO/VLO/MPC bull 0.5 (Russia keeps diesel home; US swing supplier).
