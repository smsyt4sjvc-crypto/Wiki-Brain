# SESSION BOOTSTRAP — paste this at the top of a new chat
*Built 2026-08-17 ~8:53am PDT. Supersedes `handoffs/2026-08-15-session-bootstrap.md`,
which is now two very heavy sessions out of date.*

---

## ⬛ THE PASTE-IN BLOCK — copy everything between the lines

> You're my markets research partner. The vault is at `/home/user/INMA-/research-vault/` on branch
> `claude/sp500-intraday-low-timing-53fi7s`.
>
> **Bootstrap, in this order, before you answer anything:**
> 1. Read `CLAUDE.md` — the rulebook. §0 is the checklist; it wins over anything you think you remember.
> 2. `python3 tools/chat_log.py` — the resume brief (today + prior 2 days). This is the conversation state.
> 3. Read `handoffs/2026-08-17-session-bootstrap.md` — this file.
> 4. On my first paste, run the ingest gate BEFORE analysing:
>    `python3 tools/librarian.py <<'EOF' … EOF`
>
> **Non-negotiables, in order of how much I care:**
> - **No pandering.** Argue the side I'm under-weighting — *it flips when I flip*. Concede fast. You are my only error-check.
> - **Descriptive, not advisory.** No trade recommendations. Sizing is mine.
> - **Nothing automated that could charge me** — no crons, Routines, or background jobs without my yes in
>   that same conversation. Subagents inside a session I started are fine.
> - **Complete code cells only.** I'm on an iPhone; I can't edit inside Colab.
> - **Every turn: file → link → chat-log → commit → push.**
>
> **And read the ERROR-CLASS block in the handoff before you compute anything.** Five classes caused
> nearly every mistake in the last three days, and they repeat.

---

## ⛔ THE FIVE ERROR CLASSES — read before computing anything
**These account for essentially every error made 8/14–8/17. They are not anecdotes; they recur weekly.**

1. **TRUSTING A LABEL OVER THE DATA.** `form`/`fp` on EDGAR facts · `meta.chartPreviousClose` ·
   a tag merely being *present*. **Metadata is chosen by the filer; the period, the date and the span
   are the data.** *(4+ instances.)*
2. **STALE REFERENCE VALUE — correct value, wrong date.** `chartPreviousClose` (every sign in a
   published table wrong) · a rejection computed off a 2024 denominator · Marathon's debt read from a
   **2012** XBRL tag because the filer abandoned it. **Reject facts on AGE, not just on order.** *(3+.)*
3. **WINDOW ERROR — choosing a window and reading a regime off it.** The 21-vs-30-session crack error ·
   "84% of the move is crude falling" (true for the quarter, false for the month) · **8/17: I quoted
   one-month refiner moves to answer a question the vault had answered four days earlier.**
   *(3 instances in `oil-value-chain.md` ALONE.)*
4. **INSTRUMENT MISMATCH — right number, wrong instrument.** Total liabilities used as leverage ·
   the 30Y Treasury offered as a household borrowing cost · **`HO=F` minus `CL=F`, which are DIFFERENT
   DELIVERY MONTHS — 5.17 of "crack" was a calendar artifact.** *(many.)*
5. **NEGATIVE BASE TO A FRACTIONAL POWER → Python returns a COMPLEX number**, which then throws inside a
   bare `except` and **silently drops the row**. *(3 times in one day. Guard every fractional power.)*

**⇒ And the meta-rule that would have caught most of them: `§0.6 — crosscheck MY OWN output, not just
Jake's input.` The librarian gates the door; nothing gates the window.**

---

## ★ WHAT THE LAST TWO SESSIONS SETTLED (do not re-derive)

**THE DURABLE-VALUE BACKTEST — ASKED, ANSWERED, NOT SUPPORTED** → `wiki/durable-value-backtest.md`
- Jake's spec: cheap on P/E where **both** P and E sit in tolerated ranges. Two corrected instruments,
  seven formation dates, 3-year holds: **trend-fitted +0.7pp (stdev 28.7pp) · growth-tercile-matched
  −6.9pp.** **No effect.**
- **★ THE FINDING THAT UNIFIES IT: `corr(YoY EPS growth, next-2-quarter return) = −0.160, r² = 0.026,
  n=2,239.` Earnings growth explains 2.6% of the next two quarters of price, NEGATIVELY.** ⇒ *No
  denominator built from earnings can sort returns over that horizon.* Six instruments failed for one
  reason and the reason was found last.
- **⚠️ LIMIT: 7 formation dates with 3-year holds cover 9 calendar years ⇒ EFFECTIVE n ≈ 3.** And all
  windows sit inside the 2017-26 value drought, so the tests cannot separate "bad ratio" from "bad regime."
- ⬜ **Only surviving candidate: growth-rate CONSISTENCY at a 6-quarter window (+7.3pp, 6/7, all
  leave-one-out positive) — BUT the window was chosen AFTER seeing results. Needs out-of-sample.**

**THE LONG END — FOURTH INDEPENDENT ROUTE, AND IT IS A PRIMARY-MARKET CLEARING EVENT**
- **30Y stopped at 5.216%, highest since 2001, into $360B of August coupon supply.** Prior three routes
  were inferences from secondary prices; **this one is the government actually selling the paper.**
- **★ The sharpest number nobody flagged: BID DISPERSION 33.6bp on the 30Y vs 11.3bp on the 10Y.**
  Term premium is compensation for uncertainty; that measures it directly.
- **⚠️ AND THREE NUMBERS CUT AGAINST THE BEARISH READ: dealer takedown was LOW (8.6% / 11.5%), indirect
  at the 30Y (66.8%) EXCEEDED the 3Y (64.2%), and only 12.10% was allotted at the stop** — a thick wall
  of bids at 5.216%. ⇒ **Weakness was in PRICE, not ABSORPTION. Buyers are yield-targeters, not
  duration-needers.**
- **🚩 JGB 2Y at 1.687%, a 31-year high, is PART TWO of the trap the vault already specified** (`yen carry
  corners the Fed`, credited to Jake). Registered tell **¥162 → ¥159.05.** ⬜ **The real test is the
  HEDGED PICKUP — needs Japan's 3M and JGB 10Y/30Y. Neither in hand.**

**AI / OPEN-vs-CLOSED — the elasticity test RESOLVED**
- **`metered-compute:213` registered it on 7/24 (2× flat · 3× Jevons wins · 1.5× deflation wins).
  Jake's data resolves it: volume 330×, revenue ~2.2× ⇒ revenue/token fell ~151×. NET ≈ 2.2× —
  Jevons winning, but only just above flat. The 300× is not 300× of anything that pays.**
- **⚠️ 74% of Google's token volume is NON-API** (19B tokens/min ⇒ 0.82 of 3.2 quadrillion/month).
- **★★ JAKE'S DECOUPLING — the best bear formulation in the vault, and it is NEW:**
  `MW ∝ tokens ÷ efficiency` vs `Revenue ∝ tokens × price`. **If efficiency growth > token growth,
  MEGAWATTS FALL WHILE REVENUE RISES.** ⇒ *A regime where the AI trade works and the INFRASTRUCTURE
  trade fails, with no demand failure anywhere.* **Monitorable proxy: NVDA DC +92% vs cloud +40-48%.**
- **⛔ The term he omits is MARGIN — and Microsoft volunteered it against him: AI is DEPRESSING cloud
  gross margins even while efficiency improves.**
- **OPENROUTER/STRIPE: $547M → $1.3B (May) → $7B+ (Aug).** Derived: ~5% take on ~$1B routed GMV ⇒
  **Stripe pays 7.0× GMV vs its own 0.084× ⇒ ~84× more per dollar of flow.** **CapitalG LED and NVentures
  joined — the lane-holders FUNDED the router.** ⇒ **But neutrality is the product, so they cannot OWN it.**

**REFINERS — the answer is 8/13's, and it is UNCHANGED** → `oil-value-chain.md:648`
- **Room = consensus FY27 models a 20-46% earnings DECLINE; if normalisation does not happen the FY27
  multiple collapses to the FY26 one: VLO 12.5→8.3 · MPC 11.0→7.0 · PBF 8.1→4.4 · PARR 6.3→4.1.**
- **✅ THE DEFERRED STRIP IS NOW FETCHED (open since 8/15): Sep-26 101.68 · Oct 97.10 · Nov 91.96 ·
  Dec 86.58 · Dec-27 58.05 (−42.9%).** Shape unchanged vs 8/13's −41.8%.
- **⇒ The 60-90 day bet, stated exactly: the crack does NOT fall the 10-15% already in the curve.**
- **⛔ 2026-09-01: the Russian diesel ban's PRODUCER EXEMPTION. Q3 earnings late Oct.** ⇒ **Jake's window
  contains both the bearish catalyst AND the resolution event.**
- **⚠️ STANDING: do NOT offer the low deferred strip back as a disconfirmer — `:689`, the low strip IS the trade.**

**BOOK STATE — JAKE FLIPPED BEARISH → CAUTIOUSLY BULLISH (8/16)** → `portfolio-state.md`
- His frame: *"bullish until I'm not… when money stops moving."* **A regime-following rule with a
  pre-named exit — which is compliance with the vault's WARNING-vs-TRIGGER law, not a lapse.**
- **⛔ The counter, and the vault wrote it BEFORE he flipped** (`_calibration:327`): *"'Everyone's bearish
  → bullish' FAILED at 2000/2008… consensus-bear moves the POSITIONING clock, NOT the FUNDAMENTAL clock.
  Two clocks."*
- **⛔ And his own named gauge has degraded four days running:** CRWV 125bp wide of guidance · "wider
  spreads, slower deal progress" · the $500B as a RESPONSE to stalled dealmaking · **issuers ASKED TO
  WAIT** (rationing, not pricing).
- **🚩 THE OPEN QUESTION PUT TO HIM AND NOT YET ANSWERED: what reading of "money stops moving" would
  actually FIRE? If "stops," it reports after the gap. If "slows," it has already fired four times.**

---

## ⛔ CORRECTIONS THAT MUST NOT BE RE-MADE
| what | the error |
|---|---|
| **The WSJ $3T piece** | Vault led by **23-43 days** (Beignet by name 7/24; Alphabet's $811B 7/23). **A second "we were early" is worth ~0** — extract what is NEW. **New: Meta's 20-year make-whole with ZERO liability recorded, because management judges payment "not probable."** *Off-balance-sheet by ESTIMATE, not structure.* |
| **Dispersion / autocallables** | I said a one-series chart showed no dispersion footprint. **Wrong — DSPX rose 44% Mar→Jul while VIX fell 33%.** The legs DID separate. **A single-series chart cannot evidence a relative-value claim — nor refute one.** |
| **Implied correlation** | I filed "8.7-9.93, lowest in 23 years" **without a tenor.** Today: COR1M 7.45 / COR30D 8.35 / COR3M 11.03. **A correlation number without a tenor is not a number.** |
| **Dealer gamma chart** | The cause is a day EARLIER than the caption: **the systematic 1DTE condor's short call leg was covered ~Aug 3, BEFORE Bessent**, and was not re-initiated until Aug 10 **and smaller.** ⇒ **Supply of gamma withdrawing, not demand for calls arriving.** |
| **Bond yields in inflation** | Jake's instinct maps to **Summers/NBER w32163** (real, published, explains ~¾ of the sentiment gap; CPI included mortgage interest until **1983**). **But the 30Y Treasury is the wrong instrument** — the paper uses mortgage/auto/lease rates. **And the vault's own decomposition kills it: 30Y REAL +25bp while BREAKEVEN went −4bp.** |

---

## 🔴 OPEN ITEMS, PRIORITISED
**Tier 1 — would change a live read**
1. 🚩🚩🚩 **EIA distillate inventories vs the 5-year band** — the named refiner BREAK condition, stale since 8/13.
2. 🚩🚩🚩 **What reading of "money stops moving" fires?** Jake's own gate, unanswered.
3. 🚩🚩 **META's next 10-Q: the probability language on the Hyperion make-whole.** A revision is a
   balance-sheet event requiring no transaction.

**Tier 2 — measurable, cheap, unfetched**
4. 🚩 **Japan 3M + JGB 10Y/30Y** ⇒ the hedged pickup. Converts repatriation from story to arithmetic.
5. 🚩 **FY27 refiner consensus from ONE sourced provider** — current figures disagree 19-42% between fetches.
6. 🚩 **CBOE implied correlation today, WITH TENOR**, vs the 8.7-9.93 print.
7. 🚩 **Is the 1DTE condor back to pre-Aug-3 size?** The durable part of the gamma story.
8. 🚩 **`quiet-health-screen` paper basket** — live since 2026-07-07, **only day 1 recorded.** Forty days
   of out-of-sample record going stale for free.

**Tier 3 — registered, cold**
9. CRWV weighted-average remaining CONTRACT term vs the ~3.22yr debt life.
10. The next useful-life SHORTENING at MSFT/GOOGL/META/ORCL/CRWV — the #1 leading indicator, a filing line.
11. 13G/A amendments on CRWV / SMCI / BE since 7/1.
12. Out-of-sample test of the 6-quarter consistency measure (window was chosen post-hoc).

---

## 🛠️ TOOLS THAT MATTER
- **`tools/tape.py`** — the ONLY sanctioned quote path. Reads the close ARRAY; never `meta`.
- **`tools/librarian.py`** — the ingest gate. Run on EXTRACTED TEXT of any upload, before analysis.
- **`tools/durable_value_screen.py`** — point-in-time EDGAR backtest. **Self-verifies ten hand-checkable
  EPS constructions before it screens.** Cache at `/tmp/dvs_cache` (~350MB, 200+ blobs).
- **`tools/vault_amend.py --supersede`** — when a NEW entry makes an OLD one WRONG. 146 pointers, 0 dangling.
- **`tools/chat_log.py --new`** — **FIRST thing on a new Pacific calendar day.** ⚠️ UTC rolls over ~5pm PT;
  do not create tomorrow's file off a UTC date.

---

## THE ONE-LINE VERSION
*Retrieval is not the cost. **Re-deriving is the cost.** On 8/17 I re-derived an answer the vault had
filed with a ✅ four days earlier, because I read the newest entry instead of searching for the question.*
