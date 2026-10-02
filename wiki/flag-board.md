# 🚩 Flag board — the vault's standing IF → THEN per stock

*Opened 2026-10-02 ~10:00am PDT on Jake's spec (rule 16e). One block per stock or stock group. The
daily menu (`menu/YYYY-MM-DD.md`, one file per trading day) is drawn from this board each morning at the open.*

**WHY THIS EXISTS (Jake, 10/2):** *"I want the vault's opinion since I built it… the narratives should
give stocks a green flag if xx happens… if it's a timed event, or a window… I haven't spent a year
building this vault to just run a scanner and guess."* **The 10/2 backtest is the reason in numbers:**
a +3% limit / −3% stop on 40 vault names over 2 years, picked on price alone, hit the target 47% and
the stop 46% (n≈17,400, `tools/three_pct_board.py --backtest`) — a coin flip. **Any edge has to come
from the vault's conditions, not from the tape.**

**HOW IT IS USED**
- **Each block = THESIS (interpretation), not data.** Every line points to the board entry that holds
  the evidence. Nothing primary lives here (same rule as [[forest]]).
- **🟢 / 🔴 IF lines are PRECISE and CHECKABLE:** a named event, a named source that confirms it, and a
  date or a window. "Escalation" is not a trigger; "a UKMTO-confirmed strike Sat-Sun" is.
- **When a trigger prints, the status line flips** (🟢 FIRED / 🔴 FIRED / ✖ EXPIRED) with the date and a
  pointer — the old text stays (rule 4).
- **Execution is Jake's** (sizing, entry). His stated discipline: shares, limit sell ~+3%, stop ~−3%,
  out within ~5 days either way. The flag is the WHY and the WHEN; the bracket is the EXIT.
- **ACTUAL vs PAPER:** a block that touches Jake's real holdings says so ([[portfolio-state]]).
- **Prune** a block when its narrative resolves; move the history to its board.

**Format** (`tools/menu.py` reads these field names — keep them):
`### NAME` · `Lean` · `Watching` · `🟢 IF` · `🔴 IF` · `When` (YYYY-MM-DD dates, or "window") ·
`Read it on` · `Pointer` · `Status`

## FLAGS

### 🛢️ REFINERS — PARR (ACTUAL: 100 sh + short Oct-16 $80 call) · VLO · MPC · DINO · PBF
- **Lean:** FLAT — the shortage is structural (China halt, Russia ban, Gulf product flows) but governments are now actively capping it.
- **Watching:** China halted fuel exports "until further notice" (10/1); G7 confirmed up to 100M bbl of emergency oil + diesel over four months (10/2); Trump cooled on a US diesel export ban (10/1).
- **🟢 IF:** Beijing does NOT restore fuel-export permits in the week after its 10/7 holiday (no quota/permit news by Fri 10/9) AND no US export-ban order ⇒ the crack holds or rebuilds from ~95.6 (10/2).
- **🔴 IF:** (a) China restores fuel-export permits/quotas; or (b) a US diesel export-ban order (traps diesel at home — the vault map marks VLO/MPC/PSX/PBF BEAR); or (c) a windfall tax / price-cap proposal with a sponsor.
- **When:** 2026-10-08 · 2026-10-09 · 2026-10-16 (PARR call expiry)
- **Read it on:** China MOFCOM/NDRC export-quota reports · the diesel crack (10/2 ~95.6; 9/30 peak ~109.5) · any Oval Office ban language.
- **Pointer:** [[oil-value-chain]] 10/1 3:10pm (China release valve) · [[demand-destruction]] ban clock + 10/2 G7 · [[money-board]] (US diesel export ban row) · [[portfolio-state]] 10/2.
- **Status:** LIVE

### 🚢 TANKERS — DHT · FRO (mirror: UAL BEAR)
- **Lean:** BULL (DHT bull 1 on [[money-board]]).
- **Watching:** Jake's registered call — deal talk Friday, escalation over the weekend (`predictions/2026-10-01-deal-then-weekend-escalation.md`: (b) Claude ≈30%, (c) Brent ≥±5% gap ≈25%, up ≈18 / down ≈7); Fars-claimed VLCC hit 10/1 still unconfirmed.
- **🟢 IF:** kinetic action Sat 10/3 → Sun 10/4 6pm ET confirmed by UKMTO / a target government / CENTCOM, OR UKMTO confirms the 10/1 Fars-claimed hit ⇒ Brent December gaps up at the Sunday 3pm PT reopen.
- **🔴 IF:** a dated US-Iran meeting (Muscat / Doha / Islamabad) or a framework announced by an official ⇒ the war premium comes out; UAL is the mirror (🟢 on a deal).
- **When:** 2026-10-04 (3pm PT reopen) · window to end-November (the post-midterm strike window)
- **Read it on:** UKMTO advisories · CENTCOM · Brent December vs Friday settle at the reopen.
- **Pointer:** [[war/war-board]] 10/1 12:40pm 🚢 + 10/2 addendum · [[forest]] ⚡ Fujairah + post-midterm window.
- **Status:** LIVE

### 🏠 HOMEBUILDERS / LONG BONDS — LEN · DHI · TLT · (ACTUAL: SPY 745 put Dec-18)
- **Lean:** BEAR on LEN/DHI (9/23 top-5); the vault's standing read is that the long end will not rally (five tests passed, incl. the 10/2 post-payrolls round trip).
- **Watching:** next week's Treasury auctions after a squeeze that fully reversed in three hours (10Y 5.16 → 5.26 on 10/2).
- **🟢 IF:** the 10-year auction (Wed 10/7) stops THROUGH the when-issued yield (no tail) AND the 10Y closes below ~5.15 ⇒ LEN/DHI and TLT bid (the BEAR list becomes the BULL list).
- **🔴 IF:** the 10Y or 30Y auction tails AND the 10Y closes at or above ~5.30 ⇒ LEN/DHI lower; the SPY put (ACTUAL) gains.
- **When:** 2026-10-06 (3Y) · 2026-10-07 (10Y) · 2026-10-08 (30Y) — results 10am PT
- **Read it on:** Treasury auction results (high yield vs when-issued, bid-to-cover, indirects) · rule-20 split of the day's move.
- **Pointer:** [[rates-board]] 10/1 🔁 round trip + 10/2 💥 squeeze · [[money-board]] (auction-tail row).
- **Status:** LIVE

### 🔌 AVGO — the $60B for Anthropic chips
- **Lean:** FLAT 0.5 ([[money-board]] 10/2). *Vendor conflict: this vault runs on Anthropic's model; Anthropic is the end customer.*
- **Watching:** Broadcom amassing $60B ($42B senior + $18B subordinated; Blackstone ~$9B) to fund chips for Anthropic. Its 5.2% 2035 notes at 92.3 (~6.53% yield) — ~80% of their fall since June is Treasury rates (+88bp of +111bp), ~20bp is Broadcom credit; spread ~127bp ≈ 5Y CDS 130.8 (10/1).
- **🟢 IF:** the senior $42B is placed with outside lenders with NO Broadcom guarantee/recourse AND the 5Y CDS holds at or below ~131 ⇒ a funded order book = revenue.
- **🔴 IF:** the structure carries a Broadcom guarantee / residual-value support, OR the 5Y CDS closes above 131.6 (the panel high, 9/28) ⇒ Broadcom is lending against its own sales.
- **When:** 2026-10-02 (ICE settle tonight — Jake: "CDS gonna fly") · window: the raise's pricing (date ⬜) · AVGO FQ4 earnings (December, date ⬜)
- **Read it on:** `tools/icc_cds.py` (manual) · term sheets / lender lists.
- **Pointer:** [[ai-financing-fragility]] 10/1 ⚖️ referee + 10/2 Amazon SPV / Broadcom addendum · chat-log 10/2 ~9:40am (bond decomposition).
- **Status:** LIVE

### 🧠 MU — memory pricing vs the first buyer pushback
- **Lean:** BULL (money-board #1 cumulative, 9/23) — with a fresh WARNING: TrendForce has Nvidia evaluating 8-high HBM on Rubin Ultra to cut cost (less memory per GPU because of price). MU at new lows despite blowout earnings (Jake 10/1: "everything now in the price").
- **🟢 IF:** Samsung's Q3 preliminary operating profit beats consensus (Q2 was ₩89.4T, released 7/7) OR TSMC's September revenue prints above August's NT$514.8B ⇒ the cycle is still being paid.
- **🔴 IF:** Nvidia or a supplier confirms 8-high HBM on Rubin Ultra (load cut), OR distributor backorders reopen (the vault's MU reversal trigger).
- **When:** window 2026-10-07 → 2026-10-14 (Samsung prelim; date ⬜ — last year Oct 14, Q2 this year Jul 7) · ~2026-10-10 (TSMC monthly revenue, date ⬜)
- **Read it on:** Samsung IR pre-earnings guidance · TSMC monthly revenue release · DigiKey stock/backorder columns.
- **Pointer:** [[memory-regime-question]] · [[ai-capex-cycle]] (TSMC monthly) · chat-log 10/2 ~9:00am (HBM 8-Hi).
- **Status:** LIVE

### 🧾 CRWV · ORCL · NVDA — the co-signed raise test
- **Lean:** BEAR CRWV/ORCL (credit); NVDA/AVGO exposed as co-signers.
- **Watching:** Paramount's record junk deal broke in a day (CDS 432); the next AI-cloud raises: CRWV refinancing, Fluidstack $50B, Nebius, Lambda, Amazon's $8B chip sale-leaseback SPV, Broadcom's $60B. ICE 5Y CDS 10/1: CRWV 855.5 · ORCL 247.5 · NVDA 86.8.
- **🟢 IF:** a raise clears at normal terms WITHOUT a larger residual-value guarantee or backstop than the last one ⇒ CRWV/ORCL relief.
- **🔴 IF:** a raise needs a BIGGER RVG/backstop (Jake's example: "raising our backstop to 30% from 25%") or fails to clear ⇒ risk has moved onto NVDA/AVGO/GOOGL contingents — the last rung.
- **When:** window (no dated raise yet)
- **Read it on:** term sheets · `tools/icc_cds.py`.
- **Pointer:** [[ai-financing-fragility]] 10/1 ⚖️ (co-signed raise test, Jake's thesis) · [[forest]] ⚡ co-signed raise test · [[hyperscaler-credit]].
- **Status:** LIVE

### ⚡ POWER — CEG · VST · TLN (ACTUAL: small CEG, VST, TLN)
- **Lean:** FLAT 0.5 (PJM's fix delayed; scarcity preserved) · CEG bull 0.5 (AMZN Calvert Cliffs).
- **Watching:** FERC ruling on PJM's Interim Resource Adequacy Service.
- **🟢 IF / 🔴 IF:** ⬜ direction NOT settled on file — a delayed fix preserves scarcity pricing (🟢 generators) but delays the $555 bid (🔴). **Not menu-ready until the direction is argued.**
- **When:** 2026-10-12 (FERC, by)
- **Read it on:** FERC order · PJM filing.
- **Pointer:** [[buildout-bottleneck-map]] 9/30 ⚡ PJM entry.
- **Status:** LIVE (watch only)

### 🏗️ HYPERSCALER EARNINGS — NVDA · AVGO · MU (suppliers) vs the long end
- **Lean:** —
- **Watching:** Goldman's capex path $1.2T 2027 (+54%) → $1.4T 2028 (+12%); suppliers are paid on capex GROWTH, depreciation rides on the STOCK.
- **🟢 IF:** 2027 capex guides land above ~$1.2T ⇒ supplier orders (NVDA/AVGO/MU).
- **🔴 IF:** the same raise ⇒ more IG issuance ⇒ the long end cheapens (the vault's projection channel) — 🟢 for the SPY put (ACTUAL); a capex CUT ⇒ 🔴 suppliers.
- **When:** window late October (dates ⬜)
- **Read it on:** earnings releases / calls.
- **Pointer:** [[rates-board]] (capex-guidance → long-end channel) · chat-log 10/2 ~9:00am (GS capex).
- **Status:** LIVE (window)

## Links
[[forest]] · [[money-board]] · `menu/` · [[portfolio-state]] · [[retail-edge]] (bracket tests 7/15 + 10/2)
