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
