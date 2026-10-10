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
- **Watching:** *(10/4)* Zelensky vows MORE strikes on Russian refineries; Houthis claim a hit on Aramco's ~130k b/d Riyadh refinery (unconfirmed) — supply-side 🟢 pressure ([[oil-value-chain]] 10/4) · China halted fuel exports "until further notice" (10/1); G7 confirmed up to 100M bbl of emergency oil + diesel over four months (10/2); Trump cooled on a US diesel export ban (10/1). · *(10/4 eve)* Aramco cut November Asia OSPs $3-5 (widest discount since 2020) and raised Europe +$3 — the price-war tail's first datum; December OSP (~Nov 5) is the test ([[oil-value-chain]] 10/4 🏷️).
- **🟢 IF:** Beijing does NOT restore fuel-export permits in the week after its 10/7 holiday (no quota/permit news by Fri 10/9) AND no US export-ban order ⇒ the crack holds or rebuilds from ~95.6 (10/2).
- **🔴 IF:** (a) China restores fuel-export permits/quotas; or (b) a US diesel export-ban order (traps diesel at home — the vault map marks VLO/MPC/PSX/PBF BEAR); or (c) a windfall tax / price-cap proposal with a sponsor.
- **⟲ 10/2 ~1:03pm PT:** **(b) effectively RESOLVED** — Trump: "we were never going to do diesel export ban" (ZH squawk, 2 min after the close), the day the G7 release was confirmed ⇒ the ban was leverage, now disowned. The live refiner flag is (a) China after 10/7. → [[demand-destruction]] 10/2.
- **When:** 2026-10-08 · 2026-10-09 · 2026-10-16 (PARR call expiry)
- **Read it on:** China MOFCOM/NDRC export-quota reports · the diesel crack (10/2 ~95.6; 9/30 peak ~109.5) · any Oval Office ban language.
- **Pointer:** [[oil-value-chain]] 10/1 3:10pm (China release valve) · [[demand-destruction]] ban clock + 10/2 G7 · [[money-board]] (US diesel export ban row) · [[portfolio-state]] 10/2.
- **🔴 (a) FIRED 2026-10-09 (REPORTED):** Reuters 10/8 8:28pm PT, four trade sources: China to resume October fuel exports after its holiday pause (traders est. ~3.7M tonnes, per the other tool). The DINO pick exited at the open (120.00, +2.21%) by its rule. PARR (ACTUAL, short $80C to 10/16) unchanged. Confirm on MOFCOM/NDRC quota news. → menu/2026-10-09.md.
- **🔴 (d) ADDED + FIRED 2026-10-09 ~11:48am PT (REPORTED):** Trump–Putin Russian diesel deal (300k t now, 500k t Nov, 1M t after, 3M t 'based on the condition of their refineries'; US purchases authorized to 4/7/2027). Heating oil −2.7%, PARR −6.0%, VLO −2.2%, DINO flat. Physical volume capped by refinery damage (`oil-value-chain:L2980`); the slower, real version is an energy truce. → [[oil-value-chain]] 10/9 12:45pm.
- **↳ 10/10 ~11:10am:** OFAC GL 135 verified (primary; US imports authorized to 4/7/2027; EU/UK sanctions unchanged). Novak's ceiling is **3 Mt PER MONTH (~0.74 mb/d)** once refineries recover, not a one-off 3 Mt, so the bear case is bigger IF the strikes stop. Kyiv's answer: "we will burn refineries" (FT), and the Yug Rusi export terminal in Rostov burned overnight (governor-confirmed fire). ⇒ the 🔴 stays live but unrealised: the deciding input is a truce, and there is none. Marks net flat on 10/10 (BEAR 0.5 coercion, BULL 0.5 refusal). → [[oil-value-chain]] 10/10 11:10am.
- **Status:** LIVE

### 🧩 THE INTEGRATION SEAT — NOW (Jake's layer-4 thesis) · DDOG · NET
- **Lean:** BULL NOW (0.5) · FLAT DDOG/NET (priced) — [[commoditization-layer]] 10/5.
- **Watching:** the seat-to-consumption conversion at the un-run workflow/data layer vs the "AI eats seats" discount (NOW −29% from high; ADSK −35%; INTU −59%); Schneider–PTC 42% premium as a floor datum.
- **🟢 IF:** NOW's Q3 (late Oct) shows Now Assist ACV on track for ≥$1.5B AND Control Tower customers up again AND no seat-count decline disclosed ⇒ NOW +3% inside 5 sessions; a second strategic bid for a data-owning software name ⇒ the floor is general (ADSK/ANSS read-across).
- **🔴 IF:** NOW discloses seat erosion or cuts the Now Assist target; or a hyperscaler ships native evals/observability that names DDOG's seat ⇒ NOW −3% first / DDOG −3%.
- **When:** NOW Q3 ~2026-10-22 (⬜ confirm) · peers' tape this week · Oct 30 (OpenAI allowance expiry — the rotation seat's churn window).
- **Pointer:** [[commoditization-layer]] · [[metered-compute]] L617 (7/25 routing thread) · [[compression-thesis]] 10/5.
- **Status:** LIVE

### 🚢 TANKERS — DHT · FRO (mirror: UAL BEAR)
- **Lean:** BULL (DHT bull 1 on [[money-board]]).
- **Watching:** Jake's registered call — deal talk Friday, escalation over the weekend (`predictions/2026-10-01-deal-then-weekend-escalation.md`: (b) Claude ≈30%, (c) Brent ≥±5% gap ≈25%, up ≈18 / down ≈7); Fars-claimed VLCC hit 10/1 still unconfirmed.
- **🟢 IF:** kinetic action Sat 10/3 → Sun 10/4 6pm ET confirmed by UKMTO / a target government / CENTCOM, OR UKMTO confirms the 10/1 Fars-claimed hit ⇒ Brent December gaps up at the Sunday 3pm PT reopen.
- **🔴 IF:** a dated US-Iran meeting (Muscat / Doha / Islamabad) or a framework announced by an official ⇒ the war premium comes out; UAL is the mirror (🟢 on a deal). *(added 10/2 ~10:05am)* A SIGNED deal — the outcome Trump's "sign the deal or it won't exist" (10/1) is pushing for before Nov 3.
- **🟢 IF (added 10/2 ~10:05am):** a DATED US strike announcement before Nov 3 — it would break the vault's after-midterms read (third carrier on station end-November) and pull the oil premium forward.
- **🟢 IF (added 10/2 ~1:20pm):** a Saudi ground offensive along Yemen's Red Sea coast is confirmed LAUNCHED (Reuters 10/2: options being prepared) — Bab el-Mandeb is the outlet of the Saudi Hormuz bypass for Asia-bound Yanbu barrels; two chokepoints under pressure at once = longer voyages + war-risk pay. *(Two-sided over months: a successful offensive would make the bypass safer.)*
- **✅ 10/5 ~8:50am — FLAG TRADE TAKEN (ACTUAL):** DHT long 23.60, limit 24.80, stop ⬜ (rule 22.89), out ~Fri 10/9. First row of `data/flag_trades.csv`. Graded against this flag in the next menu ([[portfolio-state]] 10/5).
- **📉 10/5 8:10am tape:** DHT printed 24.98 pre-/at the open (through the +3% level) on the AFP "pipeline stopped" headline, then round-tripped to 23.22 on Bloomberg "flowing"; BNO never moved; BWET 901 → 875. Tickets did NOT fill as written (limit ≤23.80, open 24.90). Headlines are being sold; a measured Yanbu outage is what would re-bid it ([[money-board]] 10/5 8:10am).
- **✈️🛰️ 10/5 ~9:55am:** Houthis declare ALL Saudi airspace unsafe for airlines (HOCC, verified); IRGC turned a tanker back at the Strait by radio (UKMTO); UKMTO 155-26 logs the 10/3 crude-tanker hit time-late; Rubio expelled Iran's NY diplomats (the 🔴 moved AWAY); Iraq chartering a VLCC + Suezmax to run Hormuz itself. Yemeni-govt claims Bab al-Mandeb "cleared" (unverified) — if the coast is secured the RED SEA leg of the premium comes out while Hormuz stays administered: two-sided for DHT ([[war/war-board]] 10/5 9:55am).
- **🛢️ 10/5 ~8:20am:** Petroline pumping station at Khurais hit Sun 10/4 (AFP source: "stopped again"; Bloomberg/Reuters: flowing) — the bypass INLET hit while its OUTLET is fought over; BNO −1% regardless. 🔴 Yanbu loadings this week settle it ([[war/war-board]] 10/5 8:20am).
- **✅ 10/6 ~6:30am — the bypass is FLOWING (minister: 5.8 mb/d — flow CLOSED; Yanbu LOADINGS still ⬜, see 6:40am).** Energy minister (Bahrain, Tue AM): East-West pipeline at 5.8 mb/d; restarted 5–6 days after the 9/10 hit. Yemen govt says the coast up to Mocha is retaken (claim; Houthis deny). Brent Dec −2.1% pre-market, FRO −1.5%, DHT flat at 23.82 (ACTUAL, limit 24.80, stop ⬜/22.89). The 🔴 side (premium out via the Red Sea) is in motion; the 🟢 now rests on Hormuz strikes continuing (Windward: near-daily). → war-board 10/6 6:30am.
- **⚡ 10/6 ~2:00pm — FREIGHT UP, STOCKS DOWN (Jake: "ships being hit has to affect shipping rates?"):** tanker freight futures (BWET) **+6.7% today, +28.4% in 5 sessions, +72.6% in a month** to 949.5, while DHT −1.3% / FRO −1.8% / TNK −2.1%. Over 60 sessions DHT moves with BWET at **+0.60** and with crude (BNO) at only **+0.12** — the stock's real driver rose while the stock traded the Red Sea/crude relief. Dry-bulk freight (BDRY) −0.3% today, −13.5% in a month: the Black Sea cargo-ship hits have NOT moved bulk rates. Cause of today's BWET jump ⬜ not attributed (BWET holds VLCC/Suezmax futures; not a Black Sea route). → money-board DHT BULL 1 (measured freight; offsets the 6:30am BEAR 0.5).

- **📡 10/5 (Windward, data as of 10/4):** eight merchant vessels struck in Hormuz since 9/28 (four in 10/1–10/4; LR2 Lipsi disabled 10/4) while transits rose to 13; crude outflow 9.17M bbl on 10/3 from 13.15M; Bab el-Mandeb near-miss 10/4 16:50 UTC, unclaimed. Tape 7:52am: DHT 23.29 (−1.7%), tickets PAPER-filled, stops open ([[war/war-board]] 10/5 8:05am).
- **✔ FIRED 2026-10-04 ~4:30pm PT (the first 🟢):** UKMTO-reported strikes Sat 10/3 (crude tanker, 4 nm E of Oman) and Sun 10/4 (tanker in Hormuz, engine room) — part (b) MET; Brent December reopened +0.3% (no gap); freight Gulf→China $1.2M/day (ZH). Third carrier now reported due END-OCTOBER (TWZ: a relief, not necessarily a third). → [[war/war-board]] 10/4 ⚖️.
- **✔ FIRED 2026-10-04 ~10:30am PT:** Alimi ordered all Yemeni forces into active combat operations Sun 10/4 (his X post + Bloomberg), with Saudi air cover (Reuters 10/2) — about five days ahead of the ~10/9 window. Houthis CLAIM a missile/drone hit on Aramco Riyadh Sat 10/3 (fire observed; coalition: "misleading"; unconfirmed ⇒ part (b) NOT met on the letter yet). → [[war/war-board]] 10/4 🇾🇪.
- **When:** 2026-10-04 (3pm PT reopen) · Mon 2026-10-05: the Mecca-pact (MJDA) committee meets in Riyadh — Fidan/Güler/Bayraktaroğlu + Saudi/Pakistani officials, Iran's Houthi-engagement suggestion on the agenda (Turkish MFA 10/4; ✔ closes the 10/2 ⬜; NOT a US-Iran meeting, 🔴 unfired — [[war/war-board]] 10/4 8:35pm) · **Saudi offensive launch window: "within a week to after the US midterms" (Axios via JPost 10/2) ≈ 2026-10-09 → mid-November** · window to end-November (the post-midterm strike window)
- **⚠️ (10/2 ~5:05pm):** the Houthis exempt all ships EXCEPT Saudi ones (9/11) — a Saudi offensive is the likeliest event to end that exemption ⇒ watch for a Houthi statement widening targets.
- **⚠️ Grading note (10/2):** UKMTO keeps issuing "time-late" reports (gCaptain Dispatch 120) — a weekend strike can surface days later ⇒ grade the weekend call provisionally at the reopen, finally ~Wed 10/7.
- **Read it on:** UKMTO advisories · CENTCOM · Brent December vs Friday settle at the reopen.
- **Pointer:** [[war/war-board]] 10/1 12:40pm 🚢 + 10/2 addendum · [[forest]] ⚡ Fujairah + post-midterm window.
- **Status:** LIVE

### 🏠 HOMEBUILDERS / LONG BONDS / SMALL CAPS — LEN · DHI · TLT · IWM · (ACTUAL: SPY 745 put Dec-18)
- **Added 10/2 ~1:20pm — IWM rides the same flag:** small caps need rates to fall (more floating-rate debt, more unprofitable firms — general, ⬜ current %). Tape 10/2: IWM −4.4% over a month and −7.8% from its 3-month high while QQQ sat AT its high.
- **Lean:** BEAR on LEN/DHI (9/23 top-5); the vault's standing read is that the long end will not rally (five tests passed, incl. the 10/2 post-payrolls round trip).
- **Watching:** next week's Treasury auctions after a squeeze that fully reversed in three hours (10Y 5.16 → 5.26 on 10/2). · *(10/4 eve)* Hartnett's cascade triggers: IXG (global financials) < $125 and MOVE > 125 — IXG 126.43, MOVE 107 on 10/2; neither fired.
- **🟢 IF:** the 10-year auction (Wed 10/7) stops THROUGH the when-issued yield (no tail) AND the 10Y closes below ~5.15 ⇒ LEN/DHI and TLT bid (the BEAR list becomes the BULL list).
- **🔴 IF:** the 10Y or 30Y auction tails AND the 10Y closes at or above ~5.30 ⇒ LEN/DHI lower; the SPY put (ACTUAL) gains.
- **🐭 10/5 ~10:00am — IWM, two-sided (Jake's thesis):** 🟢 IF the post-payrolls SPEAKERS — Williams (Tue), Logan (Wed), Musalem (Thu) — read "pause/assess" (⟲ 10:05am, Jake: the minutes are from the 9/16 HIKE meeting, before the jobs data — stale by construction, expected hawkish, not a 🔴 on their own) AND HY OAS < 310 AND the 10Y auction stops through ⇒ IWM +3% inside the week (floating-rate relief + credit). 🔴 IF the minutes read "more tightening" and the 10Y tails ⇒ IWM −3% first. A CUT is not on the table (CME Oct 28: cut 0-1%, hike ~20%; 86bp of hikes priced over 12m) — the dovish surprise available is a pause ([[rates-board]] 10/5 10:00am).
- **⚠️ 10/5 7:52am PT:** LEN −4.9% (75.93) on a Hunterbrook SHORT REPORT (Lennar–Millrose transactions), not rates; 10Y 5.32 / 30Y 5.67 before any auction; ISM services prices 74.0 (highest since Jul-2022). The level in the menu printed for the wrong reason — grade accordingly ([[rates-board]] 10/5 8:05am).
- **When:** 2026-10-06 (3Y) · 2026-10-07 (10Y) · 2026-10-08 (30Y) — results 10am PT
- **Read it on:** Treasury auction results (high yield vs when-issued, bid-to-cover, indirects) · rule-20 split of the day's move.
- **Pointer:** [[rates-board]] 10/1 🔁 round trip + 10/2 💥 squeeze · [[money-board]] (auction-tail row).
- **Status:** LIVE

### 🛡️ DEFENSE — RTX · LMT · NOC (small caps: KTOS · AVAV · ONDS)
- **Lean:** BULL — RTX bull 1 (SM-6 $24.4B multiyear confirmed 10/1) · LMT/NOC 0.5.
- **Watching:** interceptor burn — Patriot batteries and interceptors pulled from other commands to guard Saudi oil and Qatari gas (Axios via ZH, 10/2); Trump concedes some munitions are "a little bit lower" (TIME, 10/1).
- **🟢 IF:** US strikes resume (any date) OR an emergency/supplemental munitions appropriation is introduced with a sponsor OR another multiyear interceptor award (PAC-3 = LMT; SM-3/SM-6 = RTX).
- **🔴 IF:** a SIGNED US-Iran deal — the restock urgency fades; limited, because multiyear contracts are already locked.
- **When:** window — through the post-midterm strike window (late November)
- **Read it on:** DoD daily contract announcements · appropriations bills · CENTCOM.
- **Pointer:** [[war/war-board]] 9/25 (munitions dwindling) + 10/2 🛡️ addendum · [[money-board]] RTX 10/2.
- **Status:** LIVE (window)

### ⛽ JUPITER — BE · ORCL (Oracle's 2.45 GW New Mexico campus)
- **Lean:** BEAR (BE bear 1 · ORCL bear, 9/24).
- **Watching:** Oracle's force-majeure notice to the developer (Blue Owl); the gas pipeline slipped to Feb 1, 2027; the fuel cells still need a state air-quality permit.
- **🟢 IF:** New Mexico's environment department GRANTS the air-quality permit for the Bloom fuel-cell system by Nov 23 ⇒ the last permit block clears (pipeline due Feb 1) — BE relief, Oracle's schedule claim gains credibility.
- **🔴 IF:** the permit is DENIED or DELAYED past Nov 23 ⇒ the site's power path slips again; hardware orders tied to it slip (Barclays 9/24: hardware is bought ~2-3 months before go-live) — BE and ORCL down; NVDA/AMD order timing.
- **When:** 2026-11-23 (permit deadline) · 2027-02-01 (pipeline in service)
- **Read it on:** New Mexico Environment Department air-quality bureau · Oracle/Blue Owl statements.
- **Pointer:** [[buildout-bottleneck-map]] 10/2 🔩 · [[ai-financing-fragility]] 9/24 (Barclays, five Oracle sites).
- **Status:** LIVE

### 🛸 ONDS — Ondas (drones + counter-drone)
- **Lean:** BULL 1 (9/26: a $46.1M Air Force ULTRA modification — material to its size) — but the drone group is FLAT and the autonomy money is going to insiders/private firms (new-economy-regime 10/1).
- **Watching:** *(10/3)* private Neros won $100M for 14,000 attack drones (Drone Dominance Gauntlet II) — the drone money keeps going to private firms ([[new-economy-regime]] 10/4) · ONDS 7.22 (10/2), −26% from its 3-month high; ~41% of the float short; history of cash burn and new-share issuance; ZH promotes it (class 8).
- **🟢 IF:** another OBLIGATED award large relative to its size (≥ ~$25M), OR Congress funds the FY27 drone/counter-drone lines with listed-vendor programs.
- **🔴 IF:** an equity raise — an at-the-market program or offering filing (the history: dilution follows rallies; it gaps straight through a stop).
- **When:** window — FY27 appropriations (date ⬜) · DoD daily contract announcements.
- **Read it on:** DoD contracts page · SEC filings (S-3, 424B, ATM).
- **Pointer:** [[war/war-board]] 9/26 (ULTRA award) · [[new-economy-regime]] 10/1 (Meridian/AutoWarCom addenda).
- **Status:** LIVE (window)

### 🔌 AVGO — the $60B for Anthropic chips
- **Lean:** FLAT 0.5 ([[money-board]] 10/2). *Vendor conflict: this vault runs on Anthropic's model; Anthropic is the end customer.*
- **Watching:** Broadcom amassing $60B ($42B senior + $18B subordinated; Blackstone ~$9B) to fund chips for Anthropic. Its 5.2% 2035 notes at 92.3 (~6.53% yield) — ~80% of their fall since June is Treasury rates (+88bp of +111bp), ~20bp is Broadcom credit; spread ~127bp ≈ 5Y CDS 130.8 (10/1).
- **🟢 IF:** the senior $42B is placed with outside lenders with NO Broadcom guarantee/recourse AND the 5Y CDS holds at or below ~131 ⇒ a funded order book = revenue.
- **🔴 IF:** the structure carries a Broadcom guarantee / residual-value support, OR the 5Y CDS closes above 131.6 (the panel high, 9/28) ⇒ Broadcom is lending against its own sales.
- **When:** 2026-10-02 (ICE settle tonight — Jake: "CDS gonna fly") · window: the raise's pricing (date ⬜) · AVGO FQ4 earnings (December, date ⬜)
- **Read it on:** `tools/icc_cds.py` (manual) · term sheets / lender lists.
- **Pointer:** [[ai-financing-fragility]] 10/1 ⚖️ referee + 10/2 Amazon SPV / Broadcom addendum · chat-log 10/2 ~9:40am (bond decomposition).
- **Status:** 🔴 FIRED (CDS leg) at the 2026-10-07 ICE settle: Broadcom 5Y CDS 133.5 > 131.6, same 2031-12-20 maturity (10/6: 128.8), the first close above the 9/28 panel high, the day the second $50B+ Broadcom customer-financing package was reported. Recorded 10/8 ~8:45am (missed at the 8:10am filing). The guarantee leg: the original $35B carries Broadcom ~$30B senior-tranche residual support (FT 8/4, REPORTED); terms of the $60B ⬜. Athene 10-Q (8/10): in a failed raise Broadcom carries ~85% of the unpaid purchase obligation → [[ai-financing-fragility]] 10/8 8:45am. · **2026-10-09 ~8:30am: the GUARANTEE leg fires too (REPORTED: IFR 10/9 "backstopped by Broadcom", FT 10/5 "Broadcom-supported"): two $21B senior tranches at SOFR+187.5/+150bp, both maturing 9/30/2033; partial guarantee, size ⬜; the $18B junior has no Broadcom guarantee → [[ai-financing-fragility]] 10/9 8:30am.**

### 🧠 MU — memory pricing vs the first buyer pushback
- **🔴 IF (added 10/5 close):** a named hyperscaler or neocloud DEFERS rack deployment for lack of power (MS: ~33 GW / 34% net shortfall through 2028; memory/optics bear the timing) ⇒ MU −3% first; the 9/30 deposits/SCAs cushion revenue, not the multiple ([[buildout-bottleneck-map]] 10/5 close).
- **Lean:** BULL (money-board #1 cumulative, 9/23) — with a fresh WARNING: TrendForce has Nvidia evaluating 8-high HBM on Rubin Ultra to cut cost (less memory per GPU because of price). MU at new lows despite blowout earnings (Jake 10/1: "everything now in the price").
- **🟢 IF:** Samsung's Q3 preliminary operating profit beats consensus (Q2 was ₩89.4T, released 7/7) OR TSMC's September revenue prints above August's NT$514.8B ⇒ the cycle is still being paid. · ⟶ 10/7 ~3:55pm PT: Samsung prelim ₩107.4T vs ₩108.67T est (reported; consensus range ₩105.4–108.7T) = IN LINE, Samsung leg NOT fired; TSMC leg tonight. ⟶ 10/8 1:30am: TSMC Sept NT$511.86B (−0.6% m/m) < 514.8 ⇒ TSMC leg NOT fired. Both 🟢 legs missed this window.
- **🔴 IF:** Nvidia or a supplier confirms 8-high HBM on Rubin Ultra (load cut), OR distributor backorders reopen (the vault's MU reversal trigger).
- **🔴 IF (added 10/7 pm):** DRAM contract prices stop rising (TrendForce or Samsung/Hynix quarterly ASP flat or down q/q) ⇒ MU −3% first. Micron's DRAM price growth already slowed from +mid-60s% to +high-teens% q/q in FQ4'26 while bits grew only mid-single-digits, so revenue is price-led and the sign of the next price change is the hinge. → memory-regime-question 10/7 1:00pm.
- **🔴 IF (added 10/7):** Micron's Taoyuan union calls a strike (mandate won 10/7: 1,994 of 2,012 votes; no date) OR Micron concedes a permanent profit share (the ask: 15% of operating profit) after its Oct 8–9 board ⇒ MU −3% first. A strike's price benefit goes to Samsung/Hynix, not MU. → memory-regime-question 10/7.
- **🔴 IF (added 10/6):** Samsung or SK Hynix announces a DRAM/HBM capacity step-up on the Toshiba-HDD pattern (a rival's supply answer to the shortage) ⇒ MU −3% first — on 10/6 Toshiba's HDD doubling + the TDK heads bid took STX −9% / WDC −7% while MU held flat (memory-regime-question 10/6 11:55am).
- **When:** window 2026-10-07 → 2026-10-14 (Samsung prelim; date ⬜ — last year Oct 14, Q2 this year Jul 7) · ~2026-10-10 (TSMC monthly revenue, date ⬜) ✔ 10/6 ~10:55pm: TSMC calendar = **Thu 2026-10-08** (Taipei; time ⬜). Q3 guide math: Sept ≥ NT$464B = guide midpoint, ≥ NT$483B = top; this 🟢 bar (> NT$514.8B) is above both — mim/2026-10-06.md Call 1 · ✔ 10/7 ~10:25am (TSMC IR, quarterly-results page): **Q3 earnings conference Thu 2026-10-15, 14:00 Taipei = Wed 10/14 ~11:00pm PT**; quiet period Oct 5–14. The TSM PAPER trade (out by Tue 10/13 close) exits BEFORE it.
- **Read it on:** Samsung IR pre-earnings guidance · TSMC monthly revenue release · DigiKey stock/backorder columns.
- **Pointer:** [[memory-regime-question]] · [[ai-capex-cycle]] (TSMC monthly) · chat-log 10/2 ~9:00am (HBM 8-Hi).
- **Status:** LIVE

### 🧾 CRWV · ORCL · NVDA — the co-signed raise test
- **Lean:** BEAR CRWV/ORCL (credit); NVDA/AVGO exposed as co-signers.
- **Watching:** Paramount's record junk deal broke in a day (CDS 432); the next AI-cloud raises: CRWV refinancing, Fluidstack $50B, Nebius, Lambda, Amazon's $8B chip sale-leaseback SPV, Broadcom's $60B. ICE 5Y CDS 10/1: CRWV 855.5 · ORCL 247.5 · NVDA 86.8.
- **🟢 IF:** a raise clears at normal terms WITHOUT a larger residual-value guarantee or backstop than the last one ⇒ CRWV/ORCL relief.
- **🔴 IF:** a raise needs a BIGGER RVG/backstop (Jake's example: "raising our backstop to 30% from 25%") or fails to clear ⇒ risk has moved onto NVDA/AVGO/GOOGL contingents — the last rung.
- **When:** 2026-11-01 → 2026-11-15 (CRWV Q3 10-Q: DDTL 5.0 amortisation began Nov-2026, first instalment + drawn balance; 393/355 MW delivery vs schedule) · Dec-2026 (DDTL 5.5 draw window closes; OEM repayments start) · 2027 ($6.2B principal) — [[ai-financing-fragility]] 10/4 🗓️ · the raise itself still undated
- **Read it on:** term sheets · `tools/icc_cds.py`.
- **Pointer:** [[ai-financing-fragility]] 10/1 ⚖️ (co-signed raise test, Jake's thesis) · [[forest]] ⚡ co-signed raise test · [[hyperscaler-credit]].
- **Status:** LIVE

### 🛩️ LTRX — Lantronix (drone compute supplier) · (mirror: SWMR, a listed customer)
- **Lean:** FLAT (initialised 10/4: BULL 1 on measured unmanned revenue / BEAR 1 on dilution — the ATM is live at today's price).
- **Watching:** $7.19 (10/2) = the May offering price (≈$7.19) and the ATM average (≈$7.24), with ~$17M ATM left; +36% since 9/8 while ONDS/RCAT fell; CEO bought 15K at $5.18 on 9/9.
- **🟢 IF:** Q1 FY27 revenue ≥ $32M (the guide's top half, $31-33M) AND unmanned revenue ≥ ~$5M in the quarter (the run-rate for the top of the FY27 range, ~$20-28M) or management raises the FY27 unmanned share above 15-20% ⇒ the ~52x multiple compresses on growth.
- **🔴 IF:** the Q1 10-Q shows the ATM was used after 6/30 (share count above 46.71M by more than plan grants) or a new offering · unmanned flat-to-down quarter on quarter · another large legacy customer drops out.
- **When:** 2026-11-03 (annual meeting: +1.8M plan shares) · Q1 FY27 report ≈ early November (date ⬜; last year 11/6)
- **Read it on:** the Q1 release and 10-Q (EDGAR) · Form 4s · 424B5 filings.
- **Pointer:** [[lantronix]] 10/4.
- **Status:** LIVE

### 🧮 COMPUTE FUTURES — CRWV · NBIS · IREN (readout; the futures are not tradeable at level 1)
- **Lean:** SPLIT by vintage (9/23): NBIS bull · CRWV bear.
- **Watching:** CME/NYMEX Silicon Data H100 and B200 rental-index futures (730 GPU-hours, monthly to 36 months; launch TBA, NOT 10/5); the H100 neocloud index ~$2.75 (FT chart, early Oct), off its Aug high, last print turning up.
- **🟢 IF:** the H100 curve prices later months ABOVE the spot index (the market expects rents to rise) with real open interest in week one ⇒ neocloud revenue support; NBIS first.
- **🔴 IF:** later months BELOW spot (the market prices the old-vintage decline) or the H100 index falls below ~115 on the 9/23 rebased scale ⇒ H100-heavy fleets (CRWV) and GPU-backed lenders marked down.
- **When:** launch TBA — CME's revised notice drops the 10/5 date (Jake, 10/4); CFTC review extended 9/21 ("Approval Pending (90)") ⇒ a decision ~early-mid November (start date ⬜) · first week of trading
- **Read it on:** CME/NYMEX settlements + open interest · Silicon Data index.
- **Pointer:** [[metered-compute]] 9/15 + 10/4 🧮 · [[ai-financing-fragility]] 9/23 (vintage split).
- **10/9 ~7:10pm (WSJ, full text):** H100 1-year rentals +60% y/y (SemiAnalysis; a term rate, not the index) · clouds demand multiyear deals with up to 30% upfront, sometimes guarantors · over-contracting as a hedge, and startups RESELLING leftover capacity = the double-ordering tell. The resale supply hits this index first → [[ai-capex-cycle]] 10/9 7:10pm.
- **10/9 note:** Multicoin publishes the investment case for compute futures, financing and capacity-transfer markets (via TLDR). Class 8: an investor in the theme. Its point cuts both ways: hedgeable compute makes contracted capacity look normal, AND transparent prices make inflated rental economics harder to hide.
- **Status:** LIVE

### ⚡ POWER — CEG · VST · TLN (ACTUAL: small CEG, VST, TLN)
- **Lean:** FLAT 0.5 (PJM's fix delayed; scarcity preserved) · CEG bull 0.5 (AMZN Calvert Cliffs).
- **Watching:** FERC ruling on PJM's Interim Resource Adequacy Service.
- **🟢 IF (argued 10/4):** FERC approves IRAS curtail-first by 10/12 ⇒ behind-the-meter becomes the default for new large loads — BE / CAT / GEV (turbines) up, hyperscaler $/MW up; connected-fleet premium (VST/CEG/TLN) holds.
- **🔴 IF:** FERC rejects or suspends IRAS too ⇒ the queue freezes harder; the $555 backstop stays unpriced into 2027 (PJM pulled it 10/4, launch TBD) — generators keep scarcity pricing but lose the dated bid; data-center-dependent names (ORCL Jupiter-class, CRWV) lose a power path.
- **When:** 2026-10-12 (FERC, by)
- **Read it on:** FERC order · PJM filing.
- **Pointer:** [[buildout-bottleneck-map]] 9/30 ⚡ PJM entry.
- **Texas leg (added 2026-10-08):** 🔴 TCEQ's Oct 19 update extends the freeze, or ERCOT's Dec 10 audit narrows eligibility ⇒ VST's Texas data-center contracting slips into 2027 · 🟢 the freeze lifts on pay-your-own-way terms ⇒ the Texas queue restarts (behind-the-meter gear first: GEV / CAT / BE). → [[buildout-bottleneck-map]] 10/8 7:40pm.
- **10/9 note:** DOE is pressing PJM on ratepayer protections from large-load costs (Utility Dive 10/8). The pressure runs toward data centers paying more and grid-first curtailment, the IRAS direction. FERC's ruling by 10/12 is still the test.
- **Status:** LIVE (watch only)

### 🍉 META — Watermelon + Q3 (the cheapest options in the vault's table)
- **Lean:** FLAT 0.5 (10/1) — attention seller wins from token compression vs capex-burner sold on spending (−8.3% on 7/29); CDS 100.2 through 100.
- **Watching:** Watermelon (next frontier model, ~10× Muse Spark compute; October target REPORTED, benchmarks undisclosed) · Q3 ~10/28 AMC (inferred, not confirmed) · Muse Spark open weights "soon". Options: iv30 42 vs realized 55/47 — IV/RV <1 with a dated stack; skew flat; Nov-20 ATM straddle ±11.7%.
- **🟢 IF:** Watermelon ships with DISCLOSED benchmarks at or above GPT-5.5 parity AND the Q3 revenue guide ≥ consensus ⇒ META above the Nov-20 call breakeven (~+12% from 728 at the 800 strike).
- **🔴 IF:** the 7/29 pattern — Q3 capex guide raised with the revenue guide short, or Watermelon slips past October with no date ⇒ META −8% that session (the put wing).
- **When:** October (Watermelon, no hard date) · ~2026-10-28 (Q3, inferred) · Nov-20 expiry captures both.
- **Read it on:** Meta newsroom / Zuckerberg · Meta IR (date confirmation) · CBOE META chain (iv vs the 55/47 realized).
- **Pointer:** [[compression-thesis]] 10/4 🍉 · [[vol-divergence]] · [[cepi]] (Q3 mark give-back).
- **Status:** LIVE

### 🏗️ HYPERSCALER EARNINGS — NVDA · AVGO · MU (suppliers) vs the long end
- **Lean:** —
- **Watching:** Goldman's capex path $1.2T 2027 (+54%) → $1.4T 2028 (+12%); suppliers are paid on capex GROWTH, depreciation rides on the STOCK.
- **🟢 IF:** 2027 capex guides land above ~$1.2T ⇒ supplier orders (NVDA/AVGO/MU).
- **🔴 IF:** the same raise ⇒ more IG issuance ⇒ the long end cheapens (the vault's projection channel) — 🟢 for the SPY put (ACTUAL); a capex CUT ⇒ 🔴 suppliers.
- **When:** window late October (dates ⬜)
- **Read it on:** earnings releases / calls.
- **Pointer:** [[rates-board]] (capex-guidance → long-end channel) · chat-log 10/2 ~9:00am (GS capex).
- **Status:** LIVE (window)

### 📱 AGENT DEVICE — SPCX · TSLA (vs AAPL · GOOGL · QCOM) — Jake's hardware watch (set 2026-10-08 ~6:40pm)
- **Lean:** — (watch only; NR as a grade until a device has a date)
- **Watching:** a handheld that runs on SpaceX's stack — Grok as the interface, SpaceX's rented compute behind it, Starlink Mobile as the radio — and syncs with the car (Grok Bot + Connectors already run in Teslas since 9/22). Device silicon would be Tesla's own (AI5 at Samsung's Texas fab, trial production 9/17; Terafab later), NOT Nvidia: Nvidia makes no phone chip (its smallest is the N1X laptop chip with MediaTek). The ~$40B Nvidia purchase (REPORTED loan talks, not filed) is cloud GPUs for Colossus.
- **🟢 IF:** SpaceX or Tesla names a device (any form factor) with its own cellular/Starlink link and Grok as the OS, with a date — confirmed on a primary (SpaceX CMS updates feed, an 8-K, or an earnings call) ⇒ SPCX BULL; AAPL / GOOGL BEAR (the app-store and search tolls); QCOM BEAR; Samsung foundry BULL (AI5/AI6).
- **🔴 IF:** both Q3 calls pass with no device and the Starlink Mobile date slips past end-2027 ⇒ the watch waits. Separate 🔴 for SPCX's backend: Google's GPU-delivery grace ends ~10/31 (terminate or pro-rate) and its 90-day exit right opens 12/31.
- **When:** Tesla Q3 results + call **Wed 10/21, 2:30pm PT** (8-K) · SpaceX Q3 call (date ⬜) · Meta Muse Charm in December (the first rival specimen).
- **Read it on:** SpaceX `content.spacex.com/api/spacex-website/updates` · EDGAR 8-Ks (SpaceX CIK 1181412, Tesla CIK 1318605) · the calls.
- **Pointer:** [[compression-thesis]] 9/23 + 10/8 6:25–6:40pm · [[ai-capex-cycle]] 10/8 6:25pm (the compute contracts) · `raw/2026-10-08-agent-device-hardware-checks.md`.
- **Status:** LIVE (watch)

### 🔬 ASML — Q3 print Tue 10/13 ~10pm PT (07:00 Amsterdam 10/14) (set 2026-10-09 ~10:40am)
- **Lean:** FLAT 0.5 with a slight down tilt ([[money-board]] 10/9 10:40am). Straddle fairly priced (±6.1% to Fri; event ~±4.2%) ⇒ no volatility edge.
- **Watching:** the forward language, since ASML no longer publishes bookings: 2027 low-NA EUV coverage, the 2028 +30% capacity "investigation", the FY €43–45B guide (requires a record Q4 ≈ €13–16B), China (~20% of 2026 sales).
- **🟢 IF:** the release or call moves 2028 +30% from "investigating" to planned AND holds or raises FY2026 €43–45B (ASML release/call, 10/14) ⇒ ASML +3% first; read-across AMAT/LRCX/KLAC up, MU (memory capex intact).
- **🔴 IF:** any walk-back of 2027 coverage, a FY guide cut or a Q4 implied below ~€13B, or China demand flagged lower (same sources) ⇒ ASML −3% first (the Q1/Q2-2025 "beat and sold" pattern).
- **When:** Tue 10/13 ~10pm PT release; the US session Wed 10/14 opens 6:30am PT, one hour after CPI (5:30am PT); TSMC Q3 results/call Wed night PT. The Oct-16 options carry all three.
- **Read it on:** asml.com press release + IR presentation; the investor call transcript; Cboe delayed chain (`cdn.cboe.com/api/global/delayed_quotes/options/ASML.json`).
- **Pointer:** [[earnings-implied-moves]] 10/9 10:40am · `raw/2026-10-09-asml-q3-2026-earnings-trade-report.txt`.
- **Status:** LIVE (dated 10/13–10/14)

### 🔬 TSM — Q3 print Wed 10/14 ~11pm PT (2am ET); the US reaction Thu 10/15 (set 2026-10-09 ~10:45am)
- **Lean:** the FADE after a gap up (Jake's side; [[_calibration]] 10/8). No straddle ahead of the print.
- **Watching:** the opening gap Thursday vs Wednesday's close; Q3 wafer shipments q/q vs +3.9% (`ai-capex-cycle:L3963`); revenue per wafer; Q4 guide; capex vs $60–64B; HPC share vs 66%.
- **🟢 IF (for the fade):** TSM opens Thursday ABOVE Wednesday's close AND Q3 wafers grew ≤ +3.9% q/q (TSMC management report / call) ⇒ TSM closes Friday below Thursday's open (6 of 6 after gap-ups, 2024–26; mean −2.9%) — Oct-23 ATM put at the open, out at +3% against or Friday's close.
- **🔴 IF:** wafers > +3.9% q/q with a raised capex range or a wafer-growth Q4 guide ⇒ do not fade; or TSM gaps DOWN ⇒ no trade (2 of 2 gap-downs were mixed).
- **When:** ASML Tue 10/13 ~10pm PT · CPI Wed 10/14 5:30am PT · TSMC release + call Wed 10/14 ~11pm PT · entry Thu 10/15 6:30am PT open · exit Fri 10/16 close.
- **Read it on:** investor.tsmc.com (management report: wafer shipments, 12-inch equivalent) · the call · Cboe delayed chain (`cdn.cboe.com/api/global/delayed_quotes/options/TSM.json`).
- **Pointer:** [[earnings-implied-moves]] 10/9 10:45am · [[ai-capex-cycle]] `:L3866` (wafer series), `:L3955` (Jake's thesis) · `raw/2026-10-09-tsmc-q3-2026-earnings-trade-report.txt`.
- **Status:** LIVE (dated 10/15–10/16)

## Links
[[forest]] · [[money-board]] · `menu/` · [[portfolio-state]] · [[retail-edge]] (bracket tests 7/15 + 10/2)
