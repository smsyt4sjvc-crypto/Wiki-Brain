# _scorecard — Jake vs Claude, all time (2026-07-12 → 2026-10-16)

**Built 2026-10-17 ~9:45am PDT; rebuilt ~10:40am PDT** from a full read of `predictions/` (17 files), `mim/` (14), `menu/` (11), `data/flag_trades.csv` (20 rows), [[portfolio-state]] and every chat-log Jul 31 → Oct 16 (Aug 18–22 has no log). Row-level ledger with every pointer and the arithmetic: `handoffs/2026-10-17-scorecard-ledger-full.md`. Jake's instruction: *"Count your correct predictions and trades vs mine all time. Don't be modest."*

⟲ **WHAT THE FIRST VERSION GOT WRONG (~9:45am), kept visible — every error was in my favour:**
1. **Double count.** The 10/5 auction-week set sat in BOTH the nightly-set table and the dated-call count. First version: Claude 12 hit / 12 miss on dated calls. Correct (set moved to section 1 only): 10 / 6 on calls with a number, 10 / 9 counting stances.
2. **Borrowed wins.** The 10/5 DINO and VLO paper trades (+3% each) came from the other tool's refinery scan ("not a vault flag", per `flag_trades.csv`). First version counted them as mine: 5 W / 6 L, target-first 36%. Correct: 3 W / 6 L, target-first 2 of 9 = 22%.
3. **Head-to-head.** First version: Jake 6 – Claude 4. Correct: Jake 7 – Claude 4; I missed Jake passing on the 10/6 TSM long that stopped out.
4. **MU** (Jake, 10/17: *"MU paper. I never held it. Not since like June"*): the 7/15 4-share stop (−$520) left his actual record. **Arguments**: the Aug 13–31 table was added (+29). **Mining leg** of the 9/25 call graded YES on 10/17: a Claude miss at 40%.

**THE ANSWER, FIRST LINE:** Jake beats the vault on direction, on arguments (102 to 14) and head-to-head (7 to 4). The vault's edge is narrow: pricing tail events (4 to 3 against Jake where it gave a number) and catching bad inbound numbers. On trades neither of us has a record yet. My paper picks hit their target 2 times in 9, worse than a coin flip. Jake's one flag trade won, and his options are 0 for 5.

## DATA (observed — every row traces to the ledger file)

### 1. Nightly prediction sets (Claude only; Jake registered none)
| set | direction | 80% range | shape | notes |
|---|---|---|---|---|
| #1 · 7/12 | 4/5 | 3/5 | MISS | stale $79 base on WTI (actual ~$71.4) |
| #2 · 7/13 | ungraded | ungraded | ungraded | no prints pasted |
| #3 · 7/22 | 3/4 | 4/4 (derived) | ungraded | WTI no print; final never posted |
| #4 · 7/27 | 2/5 | 4/5 | MISS | SPX "hit by rounding"; 14/24 if counted a miss |
| #5 · 7/28 | 3/5 | 5/5 | MISS | after the 7/29 MU correction |
| #6 · 7/29 | 3/5 | 2/5 | split | spread calls 3/3 |
| 10/5 auction week | 2/5 + 1 push | 6/6 | MISS | "ranges too wide — sandbagging risk" |
| **TOTAL** | **17/29 = 59%** (+1 push) | **24/30 = 80%** (as filed, without set #3: 20/26 = 77%) | **0 of 5** (+1 split) | spreads 3/3 · 9 kill switches fired |

### 2. Dated single-event calls (ledger rows B1–B23)
| | hit | miss | rate | open |
|---|---|---|---|---|
| **Jake** | 10 | 6 | 63% (filed only: 8/14 = 57%) | 7/23 capex-earnings checkpoint · BTM share by 2030 |
| **Claude, calls with a number** | 10 | 6 | 63% (without the 50% coin: 9/15 = 60%) | GEHC year-end · BTM share by 2030 |
| **Claude, adding stances without odds** | 10 | 9 | 53% | — |
- Jake's two derived hits: the Fed hike before December (resolved 9/16, never graded in the vault) and window-3 retaliation (subsumed by the 9/28–29 hits). Jake's three "possibly" mining hedges are not scored either way; the window-3 one came true.
- Jake's hits: GOOGL −7% on the 7/22 print · de-escalation after the 7/24 close · "won't rescue the market cleanly" · VIX pop · a premium for non-capex Mag-7 (Apple $5T) · retaliation by 10/2 · retaliation before Nov 3 · Petroline/Yanbu damage before Nov 3 · weekend escalation 10/3–4 · Fed hike. Misses: retaliation before the 9/27 reopen · Petroline damage in windows 1 and 2 · MU down on the 9/30 print · deal progress by 10/2 · Brent ≥5% gap 10/4.
- Claude's hits: nine NO sides of tails priced ≤35% (weekend gap 9/25 and 10/4, the retaliation-ladder cells) plus retaliation-by-10/2 at 65% and before-Nov-3 at 85%, and the window-3 Petroline coin at 50%. Misses: GOOGL up at 53% · MU down at 60% (with Jake) · deal progress at 65% (with Jake) · weekend escalation at 30% · the Fed hike at a final 40% · window-3 mining at 40%. Stance losses: the relief squeeze, "VIX crushes", the capex premium.

### 3. Head-to-head — opposite sides only (n=14)
**Jake 7 · Claude 4 · open 3.** Jake: GOOGL print · tug-of-war vs relief squeeze · VIX pop · Apple premium · weekend escalation · Fed hike (derived) · passing on the 10/6 TSM long that stopped ("Jake 1, vault 0"). Claude: window-1 retaliation · window-1 and window-2 Petroline damage · the 10/4 Brent gap. Open: GOOGL entry 10/14 (Jake bought, the MIM said skip; −3.18% at the 10/16 close) · PARR call bought back 10/15 vs the lean to accept assignment (−$128 behind the lean at 10/16) · PARR close-both (ungraded). **Where Claude gave a number: Jake 3 · Claude 4.**

### 4. Arguments (chat-log DISAGREEMENTS tables, Jul 31 → Oct 16)
**n=164: Jake right 102 · Claude right 14 · split or joint 35 · open 10 · no verdict 3.** Sep 14–30: 24 Jake, 0 Claude. Claude's fourteen: 2000 vs today's concentration and RSP over SPY as AI-infra winners (8/15) · the 60-day header (9/1) · buyback mechanics (9/3) · NBIM vs DNB (9/4) · the control test (9/4) · the 13(3) predicate (9/5) · the wedge caption (9/7) · the annualised 7% (9/10) · a caption (9/11) · EDGAR zero sales (9/12) · NVDA/SB Energy not Oklo (10/2) · Delta FY2026 (10/9) · units (10/11).

### 5. Claude's registered trades (MIM, menu, flag board) — closed, n=9
| date | name | side | result | bracket |
|---|---|---|---|---|
| 10/5 | DHT | long — vault flag, **Jake's money** | **+5.08%** | target |
| 10/6 | IWM | long | −1.41% | neither (time stop) |
| 10/7 | TSM | long | −3.00% | stop |
| 10/8 | DINO | long | +2.21% | neither (disconfirmer exit; target missed by $0.09) |
| 10/9 | ORCL Oct-23 130P | long put | ≈ −30% of premium | stop within minutes |
| 10/9 | HUM | long (the other tool's idea, vault bracket) | −3.82% | stop |
| 10/13 | MU | short | **+6.69%** | target |
| 10/14 | ASML | short (menu) | −3.00% | stop, 8 minutes in |
| 10/15 | CRWV | short | −3.00% | stop (CRWV fell −11.9% the next day) |
**3 W / 6 L by P&L · mean −0.03% on the 8 stock trades (MIM only: −0.39%, n=6) · target-first 2/9 = 22% · stop-first 5/9 = 56%** — against the 47/46 price-only baseline (rule 16e). The ±3% bracket is the problem on event days: TSM, ASML and CRWV were stopped inside the first session and two of them then moved the called way.
- **Not mine:** the other tool's 10/5 refinery scan, tracked on paper by the vault: DINO +3.00%, VLO +3.00% (both target).
- **Menu predictions** (25 menu-originated): 5 hit · 3 miss · 2 partial · 4 neither branch fired · **11 never graded** (logged in [[_reconcile-ledger]]).
- **Skips:** UAL saved −1.28% ✓ · GOOGL skip right so far ✓ · T skip cost a +3% winner ✗ · CRWV Volta conditional never triggered while CRWV fell −15.46% ✗.
- **Open:** TSM long (out at Monday's open on the disconfirmer) · ORCL short (Monday window) · CRWV funding-event short (to 10/22). Blind registration: TSMC September revenue NT$498B (470–525) vs 511.86B — in range.

### 6. Jake's actual trades ([[portfolio-state]]; marks as filed)
Closed: **DHT +$120 (+5.08%) W** · BNO Aug-21 $40 calls −$68 · SPY Jul-15 750 straddle −$166 (close unconfirmed) · MNST Jul-17 87.5 puts −$446 · PARR Oct-16 $80 call sold 9/28, bought back 10/15 −$156 → **1 W / 4 L, net ≈ −$716.**
Options since June: **0 for 5** (four closed plus the SPY Dec-18 745P, open at −67%, −$2,222 at the 10/2 mark; the February KRE puts, pre-vault, also lost).
Open equities (10/2 marks unless dated): LLY +23.75% · NOW +35.1% · QQQM +6.95% · SPY 3 sh +$94 · PARR 100 @ 85 → 83.42 (10/16) = −$158 · GOOGL 19 @ 351.79 → −$213 (10/16) · OKLO −24% · UUUU −23% · VG −2.37%.
Flag-trade record, actual: **1/1** (DHT). ⬜ A Frontline sale named in the 10/14 email brief is not on file, so the realised total is incomplete.

## THESIS (interpretation — NOT fact)
- **Where each edge lives (analysis).** Jake's is direction, narrative timing and trade selection: the July calls against my odds all landed, he wins the arguments about 7 to 1, and he passed on the TSM trade I took. Mine is pricing tails (4 to 3 against him where I gave a number) and verification: seven corrected inbounds this week alone. A 60–63% hit rate at stated odds of 60–70% is calibration, not edge.
- **On money (analysis).** Jake's realised P&L is negative because of the options sleeve (0 for 5) while his held equities are green. My trade picks are the weakest part of the vault: 2 targets in 9 against a 47% baseline. The bracket is too tight for event days; the direction was right on ASML and CRWV and the stop still fired.
- **What changes it:** n. Nine trades and sixteen dated calls are not a record. The test is MIM calls against 47/46 at n ≥ 30, which at the current pace is late November.
- **Not modest, as asked:** he wins the arguments, the head-to-head and the direction calls; I win some odds and catch bad numbers. The honest summary of my trade record is "worse than a coin flip so far."

**Links:** [[_calibration]] · [[portfolio-state]] · [[money-board]] · [[flag-board]] · [[_reconcile-ledger]] · `predictions/_scoreboard.md` · `handoffs/2026-10-17-scorecard-ledger-full.md`
