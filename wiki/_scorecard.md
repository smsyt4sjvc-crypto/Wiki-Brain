# _scorecard — Jake vs Claude, all time (2026-07-12 → 2026-10-16)

**Built 2026-10-17 ~9:45am PDT** from a full read of `predictions/` (17 files), `mim/` (14), `menu/` (11), `data/flag_trades.csv` (20 rows), [[portfolio-state]] and the chat-logs Jul 31 → Oct 16 (the Aug 13–31 disagreement table is missing: that reader died on a rate limit). Row-level ledger with every pointer: `handoffs/2026-10-17-scorecard-ledger-full.md`. Jake's instruction: *"Count your correct predictions and trades vs mine all time. Don't be modest."* The numbers are stated as they fall.

**THE ANSWER, FIRST LINE:** Jake beats the vault on direction and on arguments (7 : 1 when we disagreed). The vault beats Jake on odds for tail events and on bracketed paper trades. On real money, Jake's only flag trade won and every options trade he has made since June has lost.

## DATA (observed — every row traces to the ledger file)

### 1. Nightly prediction sets (Claude only)
Set #2 (7/13) was never graded (no prints pasted). Set #3 WTI had no print.

| set | direction | 80% range | shape | notes |
|---|---|---|---|---|
| #1 · 7/12 | 4/5 | 3/5 | MISS | stale $79 base on WTI (actual ~$71.4); MU "double miss" |
| #3 · 7/22 | 3/4 | 4/4 | ungraded | derived from the GOOGL-print grade |
| #4 · 7/27 | 2/5 | 4/5 | MISS | SPX "hit by rounding", thesis fail |
| #5 · 7/28 | 3/5 | 5/5 | MISS | 5/5 after the 7/29 MU correction |
| #6 · 7/29 | 3/5 | 2/5 | SPLIT (0.5) | spread calls 3/3 |
| 10/5 auction week | 2/5 + 1 push | 6/6 | MISS (2 of 3 legs) | "ranges too wide — sandbagging risk" |
| **TOTAL** | **17/29 = 59%** (July alone 15/24 = 63%) | **24/30 = 80%** (July alone 18/24 = 75%) | **0.5/5** | spreads 3/3 |

Direction is coin-flip territory. Range coverage sits on the 80% target. Shape calls (how the day trades) fail almost every time.

### 2. Dated single-event calls (`predictions/*.md` + `_scoreboard.md`, rows B1–B31 in the ledger)
**Jake: 10 HIT / 6 MISS = 63%** (n=16 scored; three "possibly" hedges not scored; three open). Two hits are derived, not filed: Fed hike before December (resolved YES 9/16) and window-3 any-retaliation (subsumed by the 9/28–29 hits). Filed-only: 8/6.
- Hits: GOOGL −7% on the 7/22 print (exact); de-escalation after the 7/24 close (Reuters Sun 7/26); "won't rescue the market cleanly" (7/23); VIX pop against Claude's "VIX crushes" (7/23); a premium for non-capex Mag-7 (7/27 → Apple $5T 7/28); retaliation by 10/2 (four UKMTO hits 9/28–29); retaliation before Nov 3; Petroline/Yanbu damage before Nov 3 (Khurais 10/4); weekend escalation 10/3–4 (UKMTO tanker hits); Fed hike before December.
- Misses: retaliation before the 9/27 reopen; Petroline damage in windows 1 and 2; MU down on the 9/30 print (+3.03%); deal progress by 10/2; Brent ≥5% gap at the 10/4 reopen (+0.33%).

**Claude: 12 HIT / 12 MISS / 1 PUSH = 50%** (n=24 at the ≥50% rule; the window-3 Petroline call was priced at exactly 50% and counts as a hit under the rule — zero edge). Nine of the twelve hits are the NO side of tail events priced at ≤35% (the retaliation ladder, mining, the weekend gap twice); two are YES at 65% and 85%; one is the coin.
- Misses: the four July directional calls against Jake (GOOGL 53% up; relief squeeze; VIX crush; "capex premium"); MU down at 60% (wrong with Jake); deal progress at 65%; weekend escalation at 30% (Jake right); Fed hike at a final 40% (Jake right); SPY/QQQ/DHT direction on 10/6; the auction-week shape.

**Head-to-head (both took a side, n=15): Jake 6 · Claude 4 · both right 3 · both wrong 2.** Claude's four: window-1 retaliation, window-1 and window-2 Petroline, the 10/4 gap. Jake's six: GOOGL, the tug-of-war, VIX, Apple, weekend escalation, the Fed hike.

### 3. Arguments (chat-log DISAGREEMENTS tables, Jul 31 → Oct 16; Aug 13–31 missing)
**n=133 logged: Jake right 84 · Claude right 12 · split or joint 30 · open 7.** Sep 14–30 alone: 23 Jake, 0 Claude, 6 split. Claude's twelve: the 60-day header (9/1), buyback mechanics (9/3), NBIM vs DNB (9/4), the control test (9/4), the 13(3) predicate (9/5), the wedge caption (9/7), the annualised 7% (9/10), a caption (9/11), EDGAR zero sales (9/12), NVDA/SB Energy not Oklo (10/2), Delta FY2026 (10/9), units (10/11).

### 4. Claude's registered trades (MIM / menu; PAPER unless marked) — closed, n=11
| date | name | side | result | bracket |
|---|---|---|---|---|
| 10/5 | DHT | long, **ACTUAL** | **+5.08%** | target (limit 24.80 filled 10/8) |
| 10/5 | DINO | long | +3.00% | target (gopher scan, vault bracket) |
| 10/5 | VLO | long | +3.00% | target |
| 10/6 | IWM | long | −1.41% | neither (time stop 10/12); prediction FAILED |
| 10/7 | TSM | long | −3.00% | stop (revenue leg passed, price leg failed) |
| 10/8 | DINO | long | +2.21% | neither (disconfirmer exit; target missed by $0.09) |
| 10/9 | ORCL Oct-23 130P | long put | ≈ −30% of premium | stock stop within minutes |
| 10/9 | HUM | long | −3.82% | stop 10/13 |
| 10/13 | MU | short | **+6.69%** | target (gap-down follow, n=40 study) |
| 10/14 | ASML | short | −3.00% | stop, 8 minutes after the open |
| 10/15 | CRWV | short | −3.00% | stop 8:03am; CRWV then fell −11.9% the next day |

By P&L: **5 W / 6 L**, mean **+0.58% per trade** on the ten equity trades (option excluded). Strict bracket test: **target-first 4/11 = 36% · stop-first 5/11 = 45% · neither 2** — **below the 47/46 price-only baseline** (rule 16e), n=11.
Skips: UAL skip saved −1.28% ✓ · GOOGL skip right (shadow stop hit 10/15) ✓ · T skip cost a +3% winner ✗ · CRWV 10/15 conditional never triggered while the shadow fell −15.46% ✗ (the month's biggest miss, by rule).
Open: TSM long (fired 421.22 10/16; exits at Monday's open on the disconfirmer) · ORCL short Call 1 (Monday window) · CRWV Call 2 (to 10/22).
Statement calls: MIM 10/5 and 10/6 statements RIGHT; TSMC September blind estimate NT$498B vs actual 511.86B (inside the 470–525 range; P(≥483)=70% hit; P(>514.8)=30% → no, hit).

### 5. Jake's actual trades ([[portfolio-state]]; Fidelity listing 10/2; marks as filed)
Closed: **DHT +$120 (+5.08%) W** · BNO Aug-21 $40 calls −$68 · SPY Jul-15 750 straddle −$166 (−25%) · MU 4 sh −$520 (−13%, stop 7/15) · MNST Jul-17 87.5 puts −$446 (−87%) · PARR Oct-16 $80 call sold 9/28, bought back 10/15: −$156. → **1 W / 5 L, net ≈ −$1,236.**
Options since June: **0 for 5** closed or marked (BNO calls, SPY straddle, MNST puts, PARR call; the SPY Dec-18 745P open at −67%, −$2,222 at the 10/2 mark; the February KRE puts, pre-vault, also lost to theta).
Open equities (10/2 marks unless dated): LLY +23.75% · NOW +35.1% · QQQM +6.95% · SPY 3 sh +$94 · PARR 100 @ 85 → 83.42 (10/16) = −$158 · GOOGL 19 @ 351.79 → −$213 (10/16) · OKLO −24% · UUUU −23% · VG −2.37%.
Flag-trade record, ACTUAL (rule 16e): **1/1** (DHT).

### 6. The biggest single calls, each way
- Jake: GOOGL −7% exact (7/22) · the VIX pop (7/23) · the Fed hike before December (7/30 → 9/16) · weekend escalation (10/1 → 10/3).
- Claude: the weekend-gap UNDER (9/25 and 10/1, n=2) · the retaliation odds ladder (7 of 9 NO sides) · the MU short +6.69% · the week's verifications rather than predictions (Brent "$112" never printed, the AI diesel table, Goldman net vs gross leverage).

## THESIS (interpretation — NOT fact)
- **Where each edge lives (analysis).** Jake's is direction and narrative timing: the four July calls against my odds all landed, and he wins the arguments 7 : 1. Mine is pricing the tails and taking the NO side of consensus: a 50% hit rate *at the stated odds* is calibration, not edge; the edge shows only in the no-gap pattern (n=2) and the retaliation ladder.
- **On money (analysis).** Jake's realised P&L is negative because of the options sleeve, 0 for 5, while his held equities are green and his one flag trade won. My paper trades are net positive by P&L but **below the 47/46 bracket baseline**: ±3% brackets are too tight for event days (ASML, CRWV and TSM were all stopped inside the first session).
- **What changes it:** n. Eleven paper trades and sixteen dated calls are not a record. The 120-day window will hold ~60 trades by January; the test is whether MIM calls beat 47/46 at n ≥ 30.
- **Not modest, as asked:** I lose the arguments and win the odds; he wins the arguments and loses the options. The vault's value so far has been verification — seven corrected inbounds this week — more than prediction.

**Links:** [[_calibration]] · [[portfolio-state]] · [[money-board]] · [[flag-board]] · [[_reconcile-ledger]] · `predictions/_scoreboard.md` · `handoffs/2026-10-17-scorecard-ledger-full.md`
