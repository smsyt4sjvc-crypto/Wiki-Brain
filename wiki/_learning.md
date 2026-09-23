# LEARNING NOTE — the concepts, in plain English

**Started 2026-09-23 (Jake: "so that I understand it, and can reference back to it later").** One entry per
concept, written once, in plain English: **what it is · why it matters · where we met it.** When a board or a
reply uses one of these words, this is the lookup. Rule 22b in `CLAUDE.md`. Links: [[rates-board]] ·
[[hyperscaler-credit]] · [[money-board]] · [[forest]].

## TREASURY AUCTIONS (how the government borrows)
- **Auction.** Treasury sells new bonds on a schedule (2Y, 5Y, 7Y, 10Y, 20Y, 30Y). Buyers bid the yield they
  will accept; the lowest yields fill first. **Why it matters:** it's the one moment you see REAL demand for
  government debt at a price, not just traders marking screens. *(Met: all September; the 5Y failed 9/23.)*
- **When-issued (WI) yield.** The yield the new bond trades at in the grey market just BEFORE the auction —
  the market's guess at where it will clear.
- **Tail.** When the auction clears at a HIGHER yield than the WI (sold cheaper than expected). **A tail =
  buyers demanded an extra discount = weak demand.** The 9/23 5Y tailed 3.2bp, 2nd-biggest ever. The opposite
  (clearing below WI) is a **stop-through** = strong demand.
- **Concession.** The market cheapening the bond in the hours/days BEFORE the auction to attract buyers. Usually
  a big concession means a clean auction. **9/23 was the exception:** 15bp of concession AND a tail — buyers
  still wanted more. That's why it was alarming.
- **Bid-to-cover.** Dollars bid ÷ dollars sold. 2.5x = $2.50 of demand per $1 of bonds. Lower = thinner demand
  (9/23: 2.21x, lowest since 2018).
- **Indirects / directs / dealers.** Who bought. **Indirects** = bids through banks, largely foreign central
  banks and big funds (⚠️ not literally "foreigners" — Jake's correction). **Directs** = domestic institutions
  bidding themselves. **Dealers** = the big banks REQUIRED to bid, who take whatever's left. **High dealer share =
  nobody else wanted it.** (9/23: dealers 15.8%, highest since 2024.)
- **The belly.** The middle of the curve, ~3Y to 7Y. **Why it matters:** companies (including AI borrowers)
  price their loans off this part — trouble here reaches corporate borrowing fastest.
- **WAM (weighted average maturity).** How long, on average, the government's debt lasts before it must be
  re-borrowed. **Shortening WAM** = borrowing more with short bills, less with long bonds. Cheap when rates are
  falling, **expensive when the Fed is hiking** — the debt re-prices faster. *(Jake's question, 9/23.)*
- **Buyback.** Treasury buying back old bonds (often to improve trading, or to reshape maturities). **It does not
  reduce what the government has to borrow** — the bonds bought back are replaced with new ones.

## YIELDS (what a bond's return is made of)
- **Nominal yield = real yield + breakeven inflation** (rule 20). The 10Y at 5.11% is the nominal.
- **Real yield.** The return AFTER inflation, measured by TIPS (inflation-protected Treasuries). **High real
  yields = money is genuinely expensive** — bad for long-duration assets (growth stocks, data-centre projects,
  housing). 9/23: the 10Y real hit 2.76%, highest since 2007 outside the Lehman panic.
- **Breakeven.** Nominal minus real = what the market expects inflation to average. **If yields rise on
  breakevens, it's an inflation scare; if they rise on reals, it's a cost-of-money / Fed / growth story.** 9/23
  was almost all real.
- **Term premium.** The extra yield investors demand just for locking money up long. It rises when people doubt
  the long-run fiscal or inflation picture.
- **Basis point (bp).** 1/100th of a percent. 5.11% → 5.26% is +15bp.

## CREDIT (how risky a company's debt looks)
- **Credit spread.** Extra yield a company pays over Treasuries for being riskier. Wider = more fear.
- **IG / HY / BBB / CCC.** Ratings buckets. **Investment grade (IG)** = safer (AAA down to BBB); **high yield
  (HY, "junk")** = BB and below; **CCC** = near-distressed. BBB is the edge of IG — the first IG names to crack.
- **OAS (option-adjusted spread).** The standard way indexes quote a spread. "IG OAS 77" = IG companies pay 0.77%
  over Treasuries. The number to watch for whether the rate shock reaches corporate credit.
- **CDS (credit default swap).** Insurance against a company defaulting; the price is in bp per year. **ORCL CDS
  224 = $2.24M a year to insure $100M of Oracle debt.** Rising CDS = the market paying more for protection.
  9/23: all 12 AI names wider. Read the CHANGE, not the level (our levels are a model conversion).
- **G-spread.** A bond's yield minus the Treasury yield at the same maturity — the simplest spread.
- **SPV (special-purpose vehicle).** A separate company set up to own a project and borrow against it (e.g.
  Beignet, which owns Meta's Hyperion data centre). The question is always: **does the market price the SPV as
  the parent (Meta) or as the project alone?** The gap between them (the "basis") tells you.
- **Clearing yield.** The rate the riskier AI borrowers actually have to pay to get money: **~9-10% right now**
  (CoreWeave, SoftBank, SB Energy, Digital Drive).

## OIL (the war trade)
- **Crack spread.** Refined-product price (diesel, gasoline) minus crude price = the refiner's margin. **Refiners
  make money on the crack, not on crude** — that's why VLO/MPC can rise when oil falls.
- **Brent vs WTI.** Brent = seaborne global oil (priced in the North Sea); WTI = US inland oil (Cushing, OK).
  **The spread between them widens when SEA routes are disrupted** (Hormuz) — a direct gauge of the war premium.
- **Tanker rates.** What it costs per day to rent a supertanker. Hormuz risk pushed Gulf rates to ~2× the old
  record; tanker stocks (DHT/FRO) trade on these, not on oil prices.
- **Export ban.** A US ban on diesel exports would trap diesel at home (US prices fall, Europe's soar) — good for
  US drivers, bad for refiners that export. That's the "policy cap" on the refiner trade.

## VOLATILITY & THE MONEY BOARD
- **VIX / MOVE.** The market's expected volatility for stocks (VIX) and for Treasury yields (MOVE), priced from
  options. Low = calm expected. 9/23: both low even though yields moved hard.
- **Implied vs realized volatility.** Implied = what options price in; realized = what actually happens. When
  realized >> implied (a "3-sigma day" on a calm MOVE), options are too cheap.
- **Correlation (COR1M).** How much stocks move together. Record LOW now ⇒ stocks offset each other ⇒ the index
  stays calm while single names swing. That's why VIX can "sleep" through a bond rout.
- **Contango.** Later-dated futures priced above near-dated. Holding long VIX in contango bleeds money daily
  while you wait.
- **Beta / sensitivity.** How much a stock moves when its driver moves. On the money board: **% move per one
  typical (1-sigma) day of the driver** — so UAL moves ~1.7% opposite a normal Brent day.
- **Sigma (σ).** One standard deviation — a "typical" move. A **weekly σ** = daily σ × √5. **The book's stops sit
  one weekly σ away**: far enough to survive normal noise, close enough to cap a wrong call.
- **Momentum / event harvesting.** Ride what's already moving (momentum) into a DATED catalyst (an auction, an
  earnings date, a deadline) and exit on the event (harvesting), rather than holding and hoping.
