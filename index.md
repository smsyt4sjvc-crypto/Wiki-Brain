# Vault Index — the map (read after CLAUDE.md)

Table of contents for the `wiki/`. Read `CLAUDE.md` first (identity + rules), then this (what exists + where).
55 notes, 178 raw sources, 69 tools. Last built: 2026-08-12. Regenerate when notes are added/renamed.
(+ `wiki/war/` containment added 2026-07-23: war-board / war-confirmed / war-rhetoric — the scannable war index.)

> Two domains, two brains: THIS vault = markets research. The **trading system** is a SEPARATE repo
> (`Alpaca-Claude`) with its own `CLAUDE.md` — staged in `trading-system/` (one domain per vault).

## 🔗 THE SPINE — read the stage order before anything AI-complex
- [[transmission-chain]] — **Treasuries → hyperscaler CDS/spreads → funding appetite → capex
  commitments → supplier orders.** Which stage is a shock sitting on, and has it propagated?
  Merged 5-stage running log: `wiki/_timelines/_chain.md` (544 entries, 2026-05-22 →).
- [[etched-inference-challenger]] — **stage 5, challenger side** (created 2026-08-18). Etched $5B→$21B
  in 8 months, Jane Street as customer AND lead investor, no MLPerf. Router key `INF-ASIC`.
- [[hyperscaler-credit]] — **stage 2**, created 2026-08-18. NVDA 5Y CDS ~40 → 80bp since late May.

## ⏱ THE GATES (`wiki/_timelines/`) — READ THE GATE BEFORE THE NOTE
**29 merged per-thread chronologies, oldest → newest, auto-generated.** When an inbound matches a
thread, its gate file is the entry point: the whole thread in order across every note that carries it,
so a March entry lands on an August paste. The router prints the path on every match.
`war-oil.md` (222 entries, opens 2026-03-13) · `financing.md` · `rates.md` · `capex.md` · `memory.md` …
**Every note also carries its own ⏱ TIMELINE block under the H1.** Regenerate both with
`python3 tools/timeline_header.py --all --threads`. Never hand-edit; edit the entry and rebuild.

## ⭐ Read-first / meta
- [[_persona]] — response contract (how to engage Jake: no pandering, peer not cheerleader)
- [[_calibration]] — the pushback filter (argue the side he's under-weighting)
- [[_origin-assessment]] — the first-message ChatGPT profile of Jake, graded against months of reality
- [[_assumption-filters]] — pre-flight for any load-bearing thesis (Goodhart/Hanlon/Occam/Chesterton + narrative-tiers)
- [[data-sourcing-playbook]] — offload heavy fetching, keep the chat lean
- [[thesis-radar]] — the confirmation loop: isolated ecosystem scouts → filings verification → convergence-only reconciliation. Cycle 1: 2026-08-09.

## 🧭 The thesis spine (start here)
1. [[consumption-vs-investment-crux]] — THE top question: did post-COVID borrowing build or drink?
2. [[new-economy-regime]] — the macro-database read (Fed Trap / debasement in the series)
3. [[market-fragility]] — the top-level regime read (narrow-market STATE, timed by triggers)
4. [[ai-capex-cycle]] → [[cepi]] — the fragility's fundamental driver (Capex→Earnings→Price Intensity)
5. [[power-not-petroleum]] → [[demand-destruction]] — the energy rotation / oil
- [[physical-ai-hardware-stack]] — the ACTUATOR/REDUCER layer only (Harmonic Drive, Nabtesco; Japan-concentrated = a queue, not a weapon). ⚠️ The magnet/rare-earth layer is NOT here — it lives in [[buildout-bottleneck-map]] L632+ (8/4 Bernstein) and L689 (8/8 policy).
6. [[fragility-engine]] — the code that scores it all into one number
6b. [[memory-regime-question]] — dip vs cliff vs revolving demand: THE question for the MU position (opened 7/28)
7. [[portfolio-state]] — the running truth of the book (+ account constraints)

## 🤖 AI capex / compression / financing
- [[ai-capex-cycle]] — the buildout cycle
- [[compression-thesis]] — Jake's positive spine: how the AI-capex corner resolves (input-deflation heal; the razor)
- [[ai-financing-fragility]] — the debt leg (private credit → the funding squeeze; the tripwire)
- [[reflection-ai]] — the "American open-weight champion" (Nvidia-backed, private, pre-product; circular-financing instance)
- [[metered-compute]] — Jake's structural-demand thesis (geometric agentic token consumption = the DEMAND side; shortage-not-glut) + the settlement toll
- [[content-toll]] — the crawler unbundling: content becoming a PRICED AI input (Google Zero, Cloudflare 9/15, the search/training bundle as the source of leverage)
- [[agentic-payments]] — the AI payment layer (x402/MPP; own the stablecoin float + COIN toll, not the alt coins)
- [[ai-infra-allocation-map]] — the names, sorted
- [[buildout-bottleneck-map]] — the next unrepriced layer
- [[cepi]] — Capex → Earnings → Price Intensity
- [[trade-down-landing-pads]] — who catches the falling customer
- [[concentration]] — concentration & breadth
- [[ai-evaluation-framework]] — **EO 14409 / "covered frontier model" — a DATED LEDGER, not a read.**
  The framework was reported complete 2026-08-03 and is UNPUBLISHED. **DATA accumulates; THESIS does not,
  until the text is public.**
- [[danger-disclosure-playbook]] — the "our model escapes/hacks" announcement genre: one move, three
  payoffs (capability projection / liability cover / gates-not-brakes) + the grading rubric. Conflict-flagged.

## ⚡ Power / energy / oil
- [[europe-energy-crunch]] — **European gas + the Rhine, and the gas-to-oil channel into the diesel crack**
  (created 2026-08-18, closing the `war-board:531` "no European gas instrument" gap). Router key `EUROGAS`.
- [[power-not-petroleum]] — the core energy-rotation thesis
- [[power-scarcity-equities]] — the three tiers (and the bottleneck≠hedge correction)
- [[nuclear]] — the AI-power sleeve
- [[demand-destruction]] — oil / war THESIS + marker framework (the reasoning; war EVENTS moved to `wiki/war/`)
- [[high-confidence-basket]] — ⭐ THE AUDITED ≤10 BASKET (2026-08-24): 10 names (VLO filled slot 10 on Jake's catch, 8/24 ~9:10pm), every exclusion on a vault-filed finding
- [[oil-value-chain]] — where the oil money goes by layer (own the crack + the toll, not the barrel)
- [[civilian-infra-strike-log]] — dated ledger, both sides: non-military / civilian-impact strikes (power/water/telecom)

## ⚔️ War containment (`wiki/war/` — the scannable Iran-war index; flags 🔴/🟠/🟡/⚪)
- [[war-board]] — THE ONE SCREEN: live marker board, triggers, current status, flag legend + logging rule (open first)
- [[war-confirmed]] — confirmed-event ledger (official/neutral/data), one flag each
- [[war-rhetoric]] — rhetoric/verbal ledger (threats/claims/doctrines), one flag each
- (Scan for market-relevant war items: grep `MARKER-MOVED\|SHOULD-MOVE` across `wiki/war/`.)

## 📉 Rates / curve / credit spreads
- [[rates-board]] — **THE routing target for any rates inbound** (added 2026-08-17). Level, August
  refunding internals (30Y stop 5.216%, bid dispersion 33.6bp), the FOUR-ROUTE long-end conclusion,
  and the open items. **The argument in full still lives in [[new-economy-regime]]; this is the board.**
  ⬜ Corporate IG/HY as a macro series is the thinnest leg — flagged inside.

## 🩻 Fragility / regime / breadth
- [[market-fragility]] — the regime read
- [[fragility-engine]] — "the brain" (the score)
- [[new-economy-regime]] — the macro-DB read
- [[detachment-bid]] — the standing bull vector
- [[precedent-bid]] — **bull vector #2 (Jake, 8/4/26 personal note): AI compressed the learning curve →
  precedent-on-demand + instant control = taught dip-buying = the V-shaped "resilience."** Counterpart to detachment-bid.
- [[bull-bear-ledger]] — the whole debate, counted honestly (+ the mechanical-bid & VRP studies)
- [[buying-at-highs]] — the ATH framework
- [[ath-clustering]] — do all-time-high clustering/spacing/droughts predict?
- [[fear-duration]] — does how LONG the market stays afraid predict bear vs recovery?
- [[rotation-stickiness]] — when a tech→defensive rotation persists vs snaps back
  · 2026-08-12 quarterly regime gauge: trend-follow + buy-hold win on Sharpe; vol-harvest DEAD (−0.4%/3y); nothing predicts Q+1 (best candidate family-wise p=0.128)

## 💰 Where the edge is (→ the trading system)
- [[how-to-get-paid]] — the four buckets, and which one is Jake's (keystone)
- [[where-the-edge-is]] — get PAID to bear risk, don't predict (keystone; the VRP verdict lives here)
- [[seeing-vs-predicting]] — see WHERE (free) vs predict DIRECTION (~0); movement predicts MAGNITUDE not sign (capstone)
- [[defense-not-offense]] — the Tudor Jones discipline anchor (the behavioral half: survival, not prediction)
- [[trading-maxims]] — the sticky one-liners, each mapped to a validated law/study (Buffett, PTJ)
- [[retail-edge]] — retail-edge doctrine ("most successful retail system for straight ROI?")

## 🪙 Gold / debasement / flows
- [[gold-flows]] — central-bank vs ETF-tourist flows (the debasement referee)
- [[live-flow-trackers]] — MOSO + RVOL (free)
- [[structural-pull-log]] — weekly positioning/filings baseline

## 🔬 Studies / screens / synthesis
- [[growth-ignition-anatomy]] — the starts of 3x runs dissected vs control (capitulation not breakout; RSI 28/below-200SMA/relvol 121%; 200-SMA reclaim day ~44; base rate 18% vs 10%)
- [[deep-value-reclaim]] — Jake's screen: furthest under 200-SMA + reclaimed 20-SMA (21% CAGR but survivorship-flattered, worse Sharpe than SPY; the 20-day filter is the finding)
- [[dip-buying-base-rates]] — the ruler for adding on weakness (war down-day + weekend base rates + ATH-drawdown ruler; SPY/QQQ)
- [[balance-sheet-board]] — ⭐ THE SHEETS BRANCH (Jake 8/10): mag7+ORCL+AVGO+SPCX on-sheet vs off-sheet vs CDS, 2023→ (EDGAR ledger cell; ~$356B stake web; spenders already net-negative)
- [[who-gets-paid-12m]] — the next-12-months synthesis
- [[cluster-shortlist-workup]] — E-path workup on the 15 names
- [[quiet-health-screen]] — value × health × no-story
- [[durable-value-backtest]] — ⛔ the point-in-time test of that screen; the durability measure was an inverted GROWTH filter (7/7 dates). Jake's hypothesis UNTESTED, not disproven. What survives: cheapness itself lost 2017-2026.
- [[runner-anatomy]] — what 200%+ 12-mo runners looked like at ignition
- [[weekly-momentum]] — NDX top-5 weekly winners: carry, duration, threshold
- [[median-line-dip]] — the median/LAD line as a dip trigger (wins 1-3mo, loses 12mo; test-run result)
- [[momentum-extrapolation-backtest]] — Jake's trailing-3-mo-trend-as-forecast via option breakevens, 1995-2026 (hit 27.5%, slope +0.02; only the drift bucket survives; GFC the lone paying era)

## 📜 Process / policy
- [[ioss-proposal]] — iOSS policy project (Jake's)
- [[data-sourcing-playbook]] — (also under meta)
- [[colab-archive-audit]] — the Drive Colab folder read + graded (50 files): what the vault already had, the 4-bug hiccup taxonomy, `tools/`=code vs Drive=runs
- [[quarterly-regime-gauge]] — which archetype fits the quarter (structural metrics, not hand-tuned rules) + does Q predict Q+1

## 🛠 Tools (`tools/`, 69 files — run in Colab, token-free)
Edge/premium: `vol_risk_premium.ipynb`, `vol_risk_premium_decay.ipynb`, `passive_bid_fingerprint.ipynb`,
`mechanical_bid_patterns.ipynb`, `first_of_month_options.ipynb`, `momentum_through_first.ipynb`,
`body_momentum_carry.ipynb`, `sma_20_50_regime_backtest.ipynb`, `memory_intraday_close.ipynb`,
`broad_value_screen.ipynb` (S&P-1500 two-stage value screen, recovered 8/12 — NOT the same tool as `cluster_hunter.ipynb`), `csp_screen.ipynb` (the laws as filters, recovered 8/12),
`median_line_dip_study.ipynb` (straight LAD/median trend vs SMA/%-off-high/rolling-median as a dip trigger),
`median_fan_drawdown.ipynb` (10/5/2y median-line fan; drawdown-depth ruler + acceleration),
`momentum_extrapolation_backtest_cell.py` (trailing 3-mo trend extrapolated via solved option breakevens, CBOE SPX + FRED VIX, 375 trades 1995-2026),
`growth_ignition_anatomy.ipynb` (maps every >=3x-in-3y S&P run since 2015, dissects ignition anatomy vs control + base-rate cell),
`deep_value_reclaim.ipynb` (Jake's deep-value screen backtest: furthest-under-200-SMA + above-20-SMA, monthly rebalance vs SPY + today's-picks cell — survivorship caveat baked into the header),
`sector_brain.ipynb` (sectors as a firing correlation network; animation + running record for rotation/stress),
`financial_gravity.ipynb` (tests 'SPX / Fed balance sheet is flat since 2008' — FRED + yfinance, QE vs QT split),
`sec_hyperscaler_scanner.ipynb` (pulls real SEC EDGAR XBRL + full-text search, no key/token — hyperscaler
earnings-quality dashboard [depreciation-schedule test, off-B/S purchase commitments, unrealized-equity-gain
catcher, FCF proxy] + secondaries fundamentals [MU/AMD/INTC/AVGO/NVDA/TSM] + ad-hoc keyword search across
filings — the Schedule-D-style "find the receipt" tool, operationalizes [[ai-financing-fragility]]).
Screens/scanners: `insider_trading_scanner.ipynb`, `vault_headline_scanner.ipynb`, `mean_reversion_screener.ipynb`,
`spy_weekly_poc_scan.ipynb`, `power_equipment_screen.ipynb`, `sp500_health_screen.py`, `cluster_hunter.ipynb`,
`ignition_filter.py`, `runner_anatomy.py`, `follow_the_money.ipynb`, `structural_pulls.py`, `flow_trackers.py`,
`monday_flows.py`, `top10_band_test.py`, `weekly_stack.ipynb`, `cluster_backtest.ipynb`, `insider_pull.py`.
Tape/regime cells (2026-07): `vault_headline_collector.ipynb` (capture-EVERYTHING RSS collector, no keyword gate
→ CSV), `sp500_full_sweep_cell.py` (whole-index sorted mover sweep; browser-UA + GitHub-CSV fallback for the
Wikipedia 403), `pyramid_tape_cell.py` (prices all four layers of the server/electrical cascade — is capital
rotating DOWN the pyramid or OUT?), `crude_curve_cell.py` (9-month WTI/Brent calendar spreads — the
physical-shortage arbiter that inverted the Hormuz absorption hypothesis),
**`vix_term_structure_cell.py`** (CALM-or-COILED: VIX9D/VIX with 12-month percentile, VIX/VIX3M backwardation,
realised index-vs-component vol to test whether a low VIX is just dispersion arithmetic, and the variance risk
premium — built 7/28 as the falsifiable test of a Jake-vs-Claude disagreement; see [[market-fragility]]),
`asia_stress_cell.py` (reads Korea/Japan/Taiwan by TRANSMISSION CHANNEL — FX, credit proxy, memory complex —
rather than by equity beta; prints the prior-session BASE next to every 1d% and flags dropped bars, both fixes
forced by measured artifact errors on 7/28), **`acute_scanner_cell.py`** (the acute scanner: 10-hour window,
~40 vault-derived keywords, index + Mag-7 + memory priced independently, headlines gated by keyword and tiered
financial-wire → networks/Google → fast-and-opinionated. **Every hit prints a `->` line naming the vault note
its keyword came FROM**, because a hit is evidence for or against a named thesis, not news — an unrouted hit is
a skipped relevance check).

**`glp1-wardrobe-cycle.md`** — Jake's GLP-1 apparel question, worked: the weight-loss-indication map
(MA/NJ/DE/NH/VT) is NOT the total-GLP-1 map (KY/WV/MS/LA), and it runs ANTI-correlated to early school
starts. What survives is transitional sizing (off-price + resale) and a timing variable that is the
GLP-1 new-start curve lagged two quarters, not the school calendar.

## 🎯 Predictions (`predictions/`) — the calibration engine
Nightly point + 80% range + direction + kill-switch for the core five; graded next session → `_scoreboard.md`.

## 📁 Trading system (`trading-system/` → transplants to repo `Alpaca-Claude`)
`constitution.md` (constraints→vehicle→laws→roadmap), `CLAUDE.md` (the 8 laws), `README.md`,
`alpaca_connection_test.ipynb`, `.gitignore`, `.env.example`. Separate domain, own brain.

### ★★★ STANDING POSITIONS — read these before the threads that feed them
- **OPTIMUS / MAGNETS / PHYSICAL AI → [[buildout-bottleneck-map]] `:L1241` (2026-08-22).** Canonical. Supersedes the 8/21 supplier map and its whole ORDERS layer. Earlier Optimus entries are history, not state.
