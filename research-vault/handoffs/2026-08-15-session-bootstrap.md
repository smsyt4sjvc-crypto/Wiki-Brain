# SESSION BOOTSTRAP — paste this at the top of a new chat
> ⟲ **SUPERSEDED 2026-08-17 → `handoffs/2026-08-17-session-bootstrap.md`.** Two heavy sessions have
> landed since (the durable-value backtest, the August refunding, the WSJ $3T piece, Jake's flip to
> cautiously bullish, the refiner strip). **Use the 8/17 file. This one is kept for the trail.**

*Built 2026-08-14 ~11:58pm PDT, at the end of a very heavy two-day session (8/13–8/14).*
*⚠️ It is nearly a new calendar day — the next session must run `chat_log.py --new` before writing anything.*

---

## THE PASTE-IN BLOCK

> You're my markets research partner. The vault is at `/home/user/INMA-/research-vault/` on branch
> `claude/sp500-intraday-low-timing-53fi7s`.
>
> **Bootstrap, in this order, before you answer anything:**
> 1. Read `CLAUDE.md` — the rulebook. §0 is the checklist; it wins over anything you think you remember.
> 2. `python3 tools/chat_log.py` — the resume brief (today + prior 2 days). This is the conversation state.
> 3. Read `handoffs/2026-08-15-session-bootstrap.md` — this file. It has what the last session learned.
> 4. On my first paste, run the ingest gate BEFORE analysing:
>    `python3 tools/librarian.py <<'EOF' … EOF`
>
> **Non-negotiables I care about most, in order:**
> - **No pandering.** Argue the side I'm under-weighting. Concede fast when I'm right. You're my only error-check.
> - **Descriptive, not advisory.** No trade recommendations. Sizing is mine.
> - **Nothing automated that could charge me** — no crons, Routines, or background jobs without my yes in
>   that same conversation. Subagents inside a session I started are fine.
> - **Complete code cells only.** I'm on an iPhone; I can't edit inside Colab.
> - **Every turn: file → link → chat-log → commit → push.**

---

## WHAT THE LAST SESSION SHIPPED (don't re-derive these)

**`tools/tape.py` — NEW AND MANDATORY.** The only sanctioned way to pull a quote.
```
python3 tools/tape.py ^GSPC ^IXIC ^RUT ^VIX ^FVX ^TNX ^TYX XRT
```
It exists because on 8/14 I published a market table with **every sign wrong**. `meta.chartPreviousClose`
from the Yahoo chart API is **the close before the requested RANGE window**, not the prior session — it is
range-dependent (`5d`→7,757.64 · `10d`→7,600.50 · `1mo`→7,543.59 · true prior close 7,798.99, same ticker,
same second). **Any inline Yahoo pull that computes a change from `meta` is a defect.**

**Thread-map gaps patched:** #25a (plain-English capability-curve vocabulary — the map had
`recursive self-improvement` but not "learning from its own research") · #25b (plain-English credit
vocabulary — had `residual value` but not "duration of the loan") · **#26, the worst one: there was ZERO
consumer vocabulary. No `retail sales`, no `control group`, no `michigan`. A new CONSUMER thread now exists.**
**The class of gap: the map was keyed to how SOURCES write, not how Jake writes.**

---

## THE CORRECTIONS FROM 8/13–8/14 — do not re-make these

| what | the error |
|---|---|
| **Market table, 8/14 7:45am** | Every % and sign wrong. Stale baseline (`chartPreviousClose`). |
| **July retail sales** | I sized the Prime Day effect off GS's −0.2pp guess. **Prime Day 2026 moved to JUNE 23–26; Walmart and Target too; no July event at all.** BofA modelled it and forecast core −0.4% — it printed −0.4%. |
| **Michigan 51.0** | Not near a record. **Record is 44.8, set May 2026.** July was a 5.7pt spike; August gave back 4.2 and sits above Apr/May/Jun. Chicago Fed Letter 521 (Jun-2026): sentiment↔real-PCE correlation fell from 0.69 to ~zero. |
| **Jane Street $15B** | I rejected it using **2024 revenue ($20.5B)**. Actual: 2025 $39.6B, 2026 YTD >$40B post-loss, ~$55B equity. It's real. |
| **The refiner strip** | I offered the collapsing deferred strip as the counterargument. `oil-value-chain:689` already had it: **the low strip IS the trade.** |

**⛔ NAMED ERROR CLASS, twice in one day: STALE REFERENCE VALUE.** Correct numerator, wrong baseline, both
directionally plausible enough to pass a smell test. **Source the denominator; don't recall it.**

**And the meta-lesson: §0.6 exists and I ran `crosscheck.py` zero times.** The librarian gates the door;
nothing gates the window — numbers I generate myself. On 8/14 the gate that caught the error was Jake
sending a screenshot of his phone.

---

## WHERE THE THREADS ACTUALLY STAND

**AI FINANCING — re-aimed.** The CRWV debt ladder came back (10-Q filed 8/12): **$35.55B gross, ~3.22yr
weighted-average LIFE, amortising, 53% secured — and the collateral is NOT hardware.** MD&A verbatim:
*"collateralized with the assets underlying the contributed contracts AND the pledged contractual cash
flows, generally from investment grade counterparties."* DDTL 4.0 is rated **A3/A(low) — investment grade.**
⇒ **The deciding comparison is TENOR vs CONTRACT TERM, not tenor vs generation clock.** The live fragility is
**cash-flow coverage** (debt +64.5% in six months, interest +61% QoQ to ~$3.6B annualised), **not collateral value.**

**The depreciation finding.** NVDA went **"two-year rhythm" (May-2022) → "one-year rhythm" (Huang, Jun-2024)**
while every major operator *lengthened* server life to ~6 years (MSFT/GOOGL 4→6, +$3.7B and +$3.0B of
earnings respectively). **Generations carried on the books went 2.0 → 6.0.** **AWS already went the other way**
— shortened a subset 6→5 eff. 1/1/25, −$677M net income, citing "the increased pace of technology development."

**The circularity has two independent instances now.** NVDA: sets the cadence · writes the RVG · holds equity
in the borrowers ($3.4B→$42.3B) · **markets the paper** (the $500B was a *response to stalled dealmaking*, per
the 8/14 wire — "a round figure with no obvious provenance"). Jane Street: **$1B equity into CoreWeave + $6B
committed to spend on its cloud**, and holds **6.01% of CRWV** ($2.93BN, +212%).

**REFINERS — Jake's thesis, and it survived four axes of testing.** Physical premises measured-confirmed via
EIA; 24 of 24 estimate-revision windows positive; three of four crack-beta labels confirmed. **"The deferred
strip is too low" and "FY27 consensus is too low" are ONE BET IN TWO INSTRUMENTS** (`oil-value-chain:689`).
**Do not offer the low strip back as a disconfirmer.** A real disconfirmer is a *dated physical or policy
event*, not a state or a curve shape.

**MACRO.** The 30Y is priced by **term premium and fiscal supply**, not the growth outlook — established by
real/breakeven decomposition 8/13 and re-confirmed 8/14 when the whole curve sold off on a weak retail print.

---

## OPEN ITEMS, PRIORITISED

**Tier 1 — housekeeping that protects everything else**
1. 🔴 **AUDIT PASS on every large round number filed in the last 30 days.** Standing since the SPR was wrong
   by 100× in the vault. **Now extended: also audit every entry quoting a same-day % change from a Yahoo pull**
   (`ai-infra-allocation-map`, `oil-value-chain`, `new-economy-regime`, `market-fragility`,
   `colab-archive-audit`, `bull-bear-ledger` — the 52-week screens read the close array and are fine).

**Tier 2 — the load-bearing unknowns**
2. 🚩🚩🚩 **CRWV weighted-average remaining CONTRACT term**, against the ~3.22yr debt life. Everything in the
   financing thread now hangs on this one number. Sources: RPO/revenue-recognition notes, backlog duration.
3. 🚩🚩🚩 **The next useful-life SHORTENING** at MSFT/GOOGL/META/ORCL/CRWV. New #1 leading indicator, and it's
   a quarterly filing line, not a price.
4. 🚩🚩 **13G/A amendments on CRWV (6.01%) / SMCI (7.61%) / BE (5.05%)** since 7/1 — the legally-compelled,
   dated falsifier for Reuters' "closed a significant portion of exposure."
5. 🚩🚩 **What did Citadel PAY** for Situational Awareness's book? A single buyer taking a levered AI book is
   the cleanest mark-to-market on the complex that exists.

**Tier 3 — the refiner fetches (the discipline Jake needs is these, not doubt)**
6. **EIA distillate inventories vs the 5-yr band** · **12-month deferred crack, weekly** · **refiner equity vs
   crack, rolling 20-session correlation** · **Chinese refined-product exports, monthly.**
7. **FY27 consensus EPS monthly** — baseline VLO 27.72 · MPC 32.97 · PSX 20.58 · PBF 9.19 · DINO 9.55 · PARR 13.23.
8. **Does Russia re-impose a product export ban, and on what date?** The trigger; the queues are the warning.

**Tier 4 — registered and cold**
9. **August retail sales (~Sep 15)** — clean calendar both sides, so it's the whole consumer test.
10. **State PUC / utility interconnection criteria** (VA/Dominion, OH/AEP, TX/ERCOT, GA/Georgia Power) — does
    any add a compute-per-MW test? Needs no legislature; ~12-month object.
11. **MEMORY IS THE EVIDENCE GAP** — nothing fetched. DRAM/HBM contract prices; is "stabilised" a top or a pause?
12. **Real GPU rental rates for 8–12 SKUs** — `tools/bandwidth_parity_cell.py` is built but 8 of 11 rates are
    placeholders I invented.
13. **Re-fetch the Bloomberg Russian diesel-export figure (80,000 b/d) from primary text** — highest
    quotability × lowest verification.

---

## THE CAPTURE TEST — apply it to every "physical constraint" thesis

*Who is SHORT the scarce thing at market price?* Power failed this for a year while being right. Refiners
pass it — they're long the scarce thing. Run it before scoring any scarcity story as bullish.
