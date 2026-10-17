# _reconcile-ledger — what the vault holds twice, and which copy is live

**Built 2026-10-17 ~9:45am PDT** from the vault-wide read Jake ordered on 10/16 (*"Read the vault in its entirety… No more missing things or glazing over information that should be reconciled as new"*). Thirty Sonnet readers digested all 92 notes and the chat-logs Jul 31 → Oct 16 and flagged **802 reconcile rows**, archived in full with pointers at `handoffs/2026-10-17-reconcile-gaps-full.md`. This note is the curated head: the conflicts that change a number someone could quote, what was fixed, and what still needs a decision.

**Method.** Each reader flagged four classes: **(a)** two lines that contradict with no ⟲ marker · **(b)** a ⬜ open item later answered but never closed · **(c)** a grade or result living in one place and not carried to the lines that asked · **(d)** duplicates and drifted pointers.

## DATA (observed)

**Rows by note (802):** rates-board 68 · war-board 58 · market-fragility 51 · ai-financing-fragility 50 · ai-capex-cycle 42 · compression-thesis 42 · metered-compute 42 · demand-destruction 41 · new-economy-regime 38 · oil-value-chain 38 · buildout-bottleneck-map 19 · balance-sheet-board 17 · every other note ≤14.

### Fixed this turn (2026-10-17)
1. **SPR level** — [[war/war-board]] L2199 "3.05MM barrels" superseded by L2533 (298.7M bbl, 43-year low, EIA). `vault_amend` marker written.
2. **Treasury buyback cap** — [[rates-board]] L3294 "$2.0B, NOT $6BN" (9/10 9:20am) superseded by L3971 (Fiscal Data primary: the 9/10 10–20Y operation was capped at $6.0B and accepted $5.187B; $2.0B was the May–Aug schedule). Marker written.
3. **GOOGL position size** — [[forest]] 10/14 branch line now reads 19 sh @ 351.79 avg (was 14 @ 353.50).
4. **grades.md header** — now states that rule 16d retired the 1–10 number on 9/23 and the ledger is frozen as history (it still read as live).
5. **Bloom Energy "not on the roster"** — already self-corrected inside [[buildout-bottleneck-map]] L1919 (`grades.md:49` had BE at 6 since 9/2); no new fix.
6. **The thread map** — the structural fix for "missing things": 58 threads / 7,535 terms (was 34 / 1,424). Every term verified to occur in `wiki/`. See `index.md` → THREADS.

### Open — needs Jake's word, or a read of both lines
- [[memory-regime-question]] L59 / L727 / L798 / L1199 "MU 28% of the book" vs [[portfolio-state]] (MU stopped out 7/15; none held since). **Paper book or real book?** → Jake.
- [[demand-destruction]] L4608 "$6.44 (9/28) = NEW RECORD" vs the $6.52–6.53 record on 9/22 (EIA vs AAA series, unflagged). The 8/19 SPR-clock "tracking" grade (L3939) vs the September draw slowdown (L4600).
- [[oil-value-chain]] 9/10 "Hormuz never carried much distillate" vs the IEA 4.93 mb/d products figure and Goldman's "products at half" in the same note · 8/26 β written −0.405 where 8/23 has +0.405 · kill-switch firing count n=3 vs n=4 (the summit readout double-counted) · China export-halt status conflicts across L3030–3036, L3068, L3252.
- [[war/war-board]] Rezaei: L2118 "second-in-command" vs L2177 "replaces the top security official" — one Reuters story, two readings.
- [[compression-thesis]] L3674 / L3676: ORCL bull 0.5 and bear 0.5 the same day, both live — net zero mark.
- [[metered-compute]]: "EXTENDS" used where the old line was withdrawn (L3672/L3683, L3705/L3707) · the Oct-5 CME launch test superseded in one of four lines · the two-speed barbell struck at L3456 with no marker on the 8/31 and 9/1 lines · IREN and CRWV grades moved without a driver · Silicon Data proprietary-index test open since 9/3.
- [[ai-capex-cycle]]: MU grade 8 → 7 with no logged move.
- **Dated items with no result on file:** FERC IRAS ruling (due ~10/12) · Suncatcher (10/1) · Tuike (10/14) · the Sept-18 Korea MOU outcome · the 31-name grade tranche "awaiting Jake" · the UMich 1Y *prior* needed to grade menu 10/9 #1.
- **Window-3 mining (Jake's 9/25 call, open to Nov 3):** candidates on file — IRGC "southern Strait is mined" and AlHadath "Houthis planted sea mines" (both 10/9, war-board L5487). Grade on Jake's ruling or at the window close.
- **Rule 21(c)** proposed at war-board L4730 ("flagging a vintage is not discounting it") — still awaiting Jake's word.

### Pointer drift — a tool finding, not a content one
- ⟲ markers written before the ⏱ TIMELINE blocks were inserted point ~100–270 lines above their targets in the big notes. `vault_amend.py --check` tests that a target **line exists**, not that it is the right line, so drift is invisible to it: 367 pointers "OK", 9 "UNPARSEABLE" (hand-written markers in prose). **The marker TEXT is the durable part.** ⬜ A text-anchored re-check (match the `why` string at the target) would catch drift; not built.
- Stale auto-TIMELINE blocks (portfolio-state ended 9/9, memory-regime-question 9/21, forest empty, nuclear/grades/_calibration) — regenerated this turn by `timeline_header.py --all`.
- Readers that died before writing (rate limit 10/17 ~2am PT): ai-financing-fragility L6101–9122, chat-log Aug 13–31 disagreements, `raw/` inventory. Vocabulary for the financing slice was pulled by a proper-noun sweep instead; the other two are ⬜.

## THESIS (interpretation — NOT fact)
- Four of the five classes are one defect: **the vault appends faster than it amends.** Rule 22c already requires the supersede in the same turn; the missing half was retrieval — the librarian could not surface the older line because the map could not reach it. The map is the fix for the second half; the ledger above is the backlog from before it.
- The honest count: two numbers were wrong in a way someone could have quoted (SPR, buyback cap). The rest are unmarked supersessions and uncarried grades — expensive to re-derive, not wrong.

**Links:** [[_scorecard]] · [[_calibration]] · [[forest]] · `tools/vault_amend.py` · `tools/acute_scanner_cell.py` (THREAD MAP)
