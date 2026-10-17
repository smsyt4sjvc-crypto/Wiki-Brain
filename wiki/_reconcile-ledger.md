# _reconcile-ledger — what the vault holds twice, and which copy is live

**Built 2026-10-17 ~9:45am PDT; updated ~10:45am** from the vault-wide read Jake ordered on 10/16 (*"Read the vault in its entirety… No more missing things or glazing over information that should be reconciled as new"*). Thirty Sonnet readers digested all 92 notes and the chat-logs Jul 31 → Oct 16 and flagged **1,026 reconcile rows** across all 92 notes, archived in full with pointers at `handoffs/2026-10-17-reconcile-gaps-full.md`. *(First version ~9:45am said 802: nine readers had stopped early on a rate limit; all finished by ~10:45am.)* This note is the curated head: the conflicts that change a number someone could quote, what was fixed, and what still needs a decision.

**Method.** Each reader flagged four classes: **(a)** two lines that contradict with no ⟲ marker · **(b)** a ⬜ open item later answered but never closed · **(c)** a grade or result living in one place and not carried to the lines that asked · **(d)** duplicates and drifted pointers.

## DATA (observed)

**Rows by note (1,026):** rates-board 68 · ai-financing-fragility 66 · war-board 58 · market-fragility 51 · ai-capex-cycle 42 · compression-thesis 42 · metered-compute 42 · demand-destruction 41 · new-economy-regime 38 · oil-value-chain 38 · buildout-bottleneck-map 19 · balance-sheet-board 17 · every other note ≤14.

### Fixed this turn (2026-10-17)
1. **SPR level** — [[war/war-board]] L2199 "3.05MM barrels" superseded by L2533 (298.7M bbl, 43-year low, EIA). `vault_amend` marker written.
2. **Treasury buyback cap** — [[rates-board]] L3294 "$2.0B, NOT $6BN" (9/10 9:20am) superseded by L3971 (Fiscal Data primary: the 9/10 10–20Y operation was capped at $6.0B and accepted $5.187B; $2.0B was the May–Aug schedule). Marker written.
3. **GOOGL position size** — [[forest]] 10/14 branch line now reads 19 sh @ 351.79 avg (was 14 @ 353.50).
4. **grades.md header** — now states that rule 16d retired the 1–10 number on 9/23 and the ledger is frozen as history (it still read as live).
5. **Bloom Energy "not on the roster"** — already self-corrected inside [[buildout-bottleneck-map]] L1919 (`grades.md:49` had BE at 6 since 9/2); no new fix.
7. **MU was paper** (Jake, 10/17) — [[portfolio-state]] L355 (the 7/15 4-share stop) and [[memory-regime-question]] L59 / L728 / L800 / L1202 ("MU 28% of the book") superseded → [[portfolio-state]] 10/17 ~10:05am.
8. **Jake's 9/25 mining leg** — graded YES (IRGC mine claims 10/10–10/17); `predictions/_scoreboard.md` + [[war/war-board]] 10/17 ~10:00am.
9. **Jake's Fed-hike call** (7/30) — never graded; resolved YES on the 9/16 hike; graded in `_scoreboard.md`. Same file: the L222 "2 of 3" slip noted (1 of 3).
10. **`flag_trades.csv` row 13** (CRWV Volta conditional) — was still CONDITIONAL; now NOT TRIGGERED, as the 10/14 MIM graded it.
11. **[[money-board]] L301** — a supersede marker pointed at itself; now points at the correction line L302.
6. **The thread map** — the structural fix for "missing things": 58 threads / 7,922 terms (was 34 / 1,424). Every term verified to occur in `wiki/`. See `index.md` → THREADS.
12. **`raw/` inventory** (`handoffs/2026-10-17-raw-inventory.md`): 900 files, 899 reachable by at least one term. Empty captures: `cisa-aa26-251a-distillation.txt` (Access Denied) and `openai-an-alien-mind.txt` (JS wall); three 10/1 `zh-*.txt` files hold only a headline; `avgo_clean.txt` and both Oklo FERC text layers are garbled. Superseded pairs: the reuters-ship-fuel stub vs -FULL, the ai-supremacy preview vs full paste, zh-firmus-ipo-cut vs its update.

### Open — needs Jake's word, or a read of both lines
- [[demand-destruction]] L4608 "$6.44 (9/28) = NEW RECORD" vs the $6.52–6.53 record on 9/22 (EIA vs AAA series, unflagged). The 8/19 SPR-clock "tracking" grade (L3939) vs the September draw slowdown (L4600).
- [[oil-value-chain]] 9/10 "Hormuz never carried much distillate" vs the IEA 4.93 mb/d products figure and Goldman's "products at half" in the same note · 8/26 β written −0.405 where 8/23 has +0.405 · kill-switch firing count n=3 vs n=4 (the summit readout double-counted) · China export-halt status conflicts across L3030–3036, L3068, L3252.
- [[war/war-board]] Rezaei: L2118 "second-in-command" vs L2177 "replaces the top security official" — one Reuters story, two readings.
- [[compression-thesis]] L3674 / L3676: ORCL bull 0.5 and bear 0.5 the same day, both live — net zero mark.
- [[metered-compute]]: "EXTENDS" used where the old line was withdrawn (L3672/L3683, L3705/L3707) · the Oct-5 CME launch test superseded in one of four lines · the two-speed barbell struck at L3456 with no marker on the 8/31 and 9/1 lines · IREN and CRWV grades moved without a driver · Silicon Data proprietary-index test open since 9/3.
- [[ai-capex-cycle]]: MU grade 8 → 7 with no logged move.
- **Dated items with no result on file:** FERC IRAS ruling (due ~10/12) · Suncatcher (10/1) · Tuike (10/14) · the Sept-18 Korea MOU outcome · the 31-name grade tranche "awaiting Jake" · the UMich 1Y *prior* needed to grade menu 10/9 #1.
- **From the readers that finished late (10/17):** [[bull-bear-ledger]] says body_momentum_carry both ran (L258–274) and never ran (L321–328) · [[transmission-chain]] stage table never rewritten for stages 4b/4c · [[financing-fragility-gauge]] calls single-name CDS a GAP at L127/L282 though L129 closed it 8/22, and its CURRENT READING block is frozen at 8/20 · [[europe-energy-crunch]] 9/14 re-quotes the 12.2× TTF/HH ratio the 9/10 entry retired · [[dip-buying-base-rates]] 34-name findings and the "$226 edge" not marked after the permutation test killed the screen · [[gold-flows]] Dec-2026 whale bet strike $20k vs $15k · [[war/war-confirmed]] says "newest on top" but runs ascending, carries three conflicting blockade tallies and has no entry after 7/28 · [[data-sourcing-playbook]] FRED-down entries superseded 130 lines later with no marker on the originals.
- **Dated checks that passed with no result on file:** [[flag-board]] — every flag dated ≤10/16 (FERC IRAS 10/12, the 10/7–8 auctions, IEA OMR 10/15, the TSM fade, PARR expiry) has no recorded flip · NOAA 10/8 · Panama canal slots 10/15 · Cloudflare 9/15 · ADT/GPK/ADSK earnings · **11 of 25 menu predictions never graded** (list in the scorecard ledger, section D).
- **Book records missing:** a Frontline sale named in the 10/14 email brief is not in [[portfolio-state]] · the 7/31 GOOGL 355/375 call spread is still "unconfirmed" and Tier 1 does not permit spreads · set #2 (7/13) was never graded.
- **Rule 21(c)** proposed at war-board L4730 ("flagging a vintage is not discounting it") — still awaiting Jake's word.

### Pointer drift — a tool finding, not a content one
- ⟲ markers written before the ⏱ TIMELINE blocks were inserted point ~100–270 lines above their targets in the big notes. `vault_amend.py --check` tests that a target **line exists**, not that it is the right line, so drift is invisible to it: 367 pointers "OK", 9 "UNPARSEABLE" (hand-written markers in prose). **The marker TEXT is the durable part.** ⬜ A text-anchored re-check (match the `why` string at the target) would catch drift; not built.
- Stale auto-TIMELINE blocks (portfolio-state ended 9/9, memory-regime-question 9/21, forest empty, nuclear/grades/_calibration) — regenerated this turn by `timeline_header.py --all`.
- ⟲ **Corrected 10/17 ~10:45am:** the first version said three readers had died. Eleven had stopped early on the rate limit, nine with partial digests (groups A1, A2, B1, B2, C and credit missing 2–19 notes each). All were resumed on Jake's word and finished; the map and this ledger were rebuilt from the complete set. The `raw/` inventory is folded in when it lands.

## THESIS (interpretation — NOT fact)
- Four of the five classes are one defect: **the vault appends faster than it amends.** Rule 22c already requires the supersede in the same turn; the missing half was retrieval — the librarian could not surface the older line because the map could not reach it. The map is the fix for the second half; the ledger above is the backlog from before it.
- The honest count: two numbers were wrong in a way someone could have quoted (SPR, buyback cap). The rest are unmarked supersessions and uncarried grades — expensive to re-derive, not wrong.

**Links:** [[_scorecard]] · [[_calibration]] · [[forest]] · `tools/vault_amend.py` · `tools/acute_scanner_cell.py` (THREAD MAP)
