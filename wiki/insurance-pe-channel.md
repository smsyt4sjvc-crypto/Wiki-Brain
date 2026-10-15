# THE INSURANCE / PRIVATE-CREDIT CHANNEL — who lends the AI buildout its long money

*Hub note, built 2026-10-14 ~7:45pm PDT (Jake: "We should have extensive notes on insurers/ABS/PE/apollo/Metlife ect…" + "Heretics/bezzle/burry").*
**The vault already held this channel: 241 insurer mentions in 25 notes, Apollo 194/21, private credit 154/17,
BDC 89/7, Bermuda 60/9, Athene 47/6. It was scattered, it had no hub, and the router could not see it (map gap #27,
fixed the same turn). This note is the INDEX: one line per finding, each pointing to the entry that holds it.
Nothing primary lives here — read the pointer before quoting.** AFF = [[ai-financing-fragility]].

**WHY THIS MATTERS (plain English):** a data centre is built with short money and must be refinanced with long
money. The biggest pool of long money is life-insurance and annuity premiums. Private-equity firms (Apollo, KKR,
Blackstone, Brookfield) bought or built life insurers to get that money, then send part of the risk to lightly
regulated Bermuda reinsurers, which can hold riskier paper with less capital. **So a retiree's annuity can end up
funding a GPU cluster that is obsolete before the annuity pays out.** If the chips hold their value and the tenants pay,
everyone is paid. If both fail together, the loss travels: equity → credit funds → insurers → state guaranty funds
and annuity holders.

## THE CHAIN (Jake's frame since 7/3, AFF:L285; transmission-chain stage 3)
retiree annuity / life premiums → PE-owned insurers (Athene/Apollo · Global Atlantic/KKR …) → Bermuda captive
reinsurers → private-credit vehicles, SPVs and asset-backed securities (ABS) → data-centre and GPU debt.
**Stage-3 state on the spine: RATIONING** ([[transmission-chain]] `:L40`, `:L124`).

## DATA (observed — as the pointed-to entry records it; firewall applies there)
**Size and ownership**
- PE insurance footprint: Apollo **$374B (51% of AUM)**, KKR **$247B (40%)**, Blackstone 20%, Brookfield 16% (Drall & Granato, AFF:L1223, 7/24).
- Chicago Fed: **$849B** of private credit on life-insurer balance sheets (2024) = ~14% of assets; PE-owned insurers drove the rise (as briefed, AFF:L7826, 8/30).
- Burry Part III (5/22): **200+ Bermuda captives since 2023, 36 PE-affiliated**; MetLife issues data-centre ABS (15-19yr lease income) to match annuities and cedes the rest to its Bermuda captive; two Bermuda-parent insurers borrowing from the Federal Home Loan Banks (FHLB); Morgan Stanley: PE/insurance private credit must fund **~$800B of $2.9T by 2028**; Ropes & Gray **$275B** permanent-loan takeout (AFF:L315-336; primary `raw/2026-05-22-burry-heretics-guide-part-3.md`).
- Apollo: US data-centre securitisations **$81.4B since 2018** ($18B in 1H26) (AFF:L8589, 9/19).

**The insurer filings actually read**
- ⭐ **Athene 10-Q (EDGAR primary, 10/8):** guarantees **15%** of an Apollo fund's (WarehouseCo) purchase obligation on the **$35B Broadcom/Anthropic** compute deal; pays only if the fund defaults; ends by 2028; 35% reimbursed by a third party; "not probable of payment"; vault ceiling ~**$3.41B ≈ 9.8% of Athene's $34.8B equity** (assets $472.9B) (AFF:L8865).
- That is the ONLY insurer filing read. (CoreWeave's 10-Q was read on the borrower side.)

**Private-credit funds (BDCs) and redemptions**
- Q2 tender data: **$15.6B requested / $5.9B paid = 37.8% payout** (AFF:L3334, 8/4).
- OBDC non-accruals **2.8% at cost** (from 2.0%) (AFF:L3526, 8/6).
- ⛔ The 7/30 redemption table is undated/stale: do not use it until it is dated (AFF ~7/30 correction).
- NY Fed review of >$1.5T of bank loans to nonbank lenders (Semafor, REPORTED); YTD to 10/6: **OWL −41.0 · KKR −29.6 · ARES −28.8 · BX −28.8 · APO −21.1 · BXSL −11.6 · BIZD −14.5 vs SPY +14.2** (AFF:L8856).

**Deals and prices (the channel at work)**
- CoreWeave's **$8.5B** GPU-collateralised deal rated **A3 (Moody's) / A(low) (DBRS)**, tied to a Meta contract (AFF:L279; FT 10/14 AFF:L9029).
- Meta Hyperion / Beignet **$27.29B 6.581% 2049, A+, PIMCO ~$18B anchor**; price drift is rates, not credit (AFF:L8675).
- Project Jupiter **$18B loan quoted 89-91**, syndication stalled (AFF:L8610, 9/20).
- Volta GPU tranche, best efforts at **11.21-11.75%** (AFF ~L8995, 10/13).
- Insurers as named buyers: Vantage $2B revolver with ~12 insurance/institutional investors (9/19); Nippon Life plans **$13B** for US data-centre financing (a PLAN, AFF:L8607); Samsung Life/Fire into KKR's Helix (9/29).
- FT 10/14: CoreWeave wants investment-grade GPU debt sold to life insurers; McBee: insurers' capital "is unlimited… all the money in the world that sits in the insurance tranche" (AFF 10/14 6:45am + 7:45pm).

**The Brighthouse / Walter thread (8/25)**
- WSJ: ~$20B Delaware Life/Clear Spring investments into Mark Walter's other firms under federal/SEC scrutiny; **BHF −20% since late July**; Aquarian's $4.1B deal for Brighthouse with walk-away rights if Delaware changes captive treatment (AFF:L7494-7536). In raw only, not yet filed: Delaware Life to swap up to **$6.5B** of affiliated investments (`raw/2026-08-18-smtc-macro-feed-verification.txt:225-227`); 13 Japanese lifers ~¥30.9T (~$200B) unrealised bond losses (`:231`).

## THESIS (interpretation — NOT fact; whose read is named)
- **Burry (5/22), with his own hedges:** the STRUCTURE is subprime-shaped ("the exact structure of the RMBS I shorted"), the SCALE is not there yet ("the DC ABS market is small now — the Meta deal was almost the sum total"). He calls it a canary, not a called event. **The risk activates on a CORRELATION EVENT:** residual-value guarantees fail when every data centre of a vintage reprices together (Moody's) (AFF:L322, L332-335).
- **The bezzle (Burry, after Galbraith):** "the market is capitalizing the most expensive phase of AI adoption as if it were normal." Insurance money is the longest-dated buyer: **15-19-year paper against data centres obsolete in under 10 years and GPUs in a few** ([[ai-capex-cycle]] `:L404`). *(analysis, 10/14)* CoreWeave asking for "unlimited" insurance money = the bezzle seeking its longest-dated funder.
- **Jake (7/24), Minsky / fire suppression:** "not blowing up is the higher risk" — the absence of losses validates the strategy, so exposure grows; the honest test is to **measure the fuel load, not predict the fire** (AFF:L1302-1307).
- **Shape (analysis):** a slow bleed, not a Lehman weekend; pain migrates equity → credit → retiree (AFF:L301).
- **Firewall (analysis, 7/24):** that AI paper sits on insurer balance sheets is INFERRED, not seen (AFF:L1253). Still true except Athene's guarantee.
- **Sponsors exit the RISK, not the business:** they keep the fees and sell the residual; but KKR and Apollo keep duration inside captive insurers (AFF:L7844).
- Private credit is "long BOTH sides of the AI event" (AFF:L3861).
- **10/8 (analysis):** Athene's disclosed link is limited; in a failed raise ~85% of the unpaid obligation stays with Broadcom, so the listed expression is AVGO, not APO (AFF:L8865).
- **10/14 (analysis, the CoreWeave read):** a rated tranche rides the CUSTOMER's contract plus the GPUs as collateral; the insurers are under-paid for both failing together. ⟲ That is Burry's correlation event (AFF:L322) — re-derived on 10/14 without citing it.

## THE MONEY — where it moves, and the instruments
- **If the channel holds** (raises clear, rated deals place with named insurers): the cost of money for neoclouds drops from ~11-15% toward single digits → CRWV/NBIS equity relief; fees to APO/KKR/BX/OWL.
- **If it cracks** (a co-signed raise fails, a correlation event, a captive-capital ruling): third-party capital marks down — **KKR · APO · BX · OWL · BLK · BIZD**, then NVDA ([[forest]] ⚡ 10/1 co-signed-raise branch, `forest:L189`); insurers with PE-owned books next; **BHF** is the daily-priced instrument on Delaware's captive ruling (AFF:L7529).
- **What the tape already says:** the alt managers are down 21-41% YTD while the S&P is up ~14% (to 10/6). The managers' equity has priced a lot; the insurers (MET, PRU) have not been tested in the vault.
- **Marks on file** (`data/money/marks.csv`): MET bull 2 · PRU bull 2 (9/23, real-rate shock; flagged weak links) · APO bull 0.5 / bear 0.5 · KKR bull 0.5 · OWL bear 0.5 ×2 · ARES bear 0.5 · BXSL bear 0.5 · BX bear 0.5 · BLK bull 1. None for BHF, CRBG, LNC, BN, BIZD.

## 🔴 OPEN — registered and never closed
- 🔴 **GOPHER SENT 2026-10-14 ~8:00pm (Jake: "Let's send the gopher"):** `prompts/gopher-insurer-schedule-d.md` — Task 1 Schedule D/BA rows (Athene · MetLife · Global Atlantic · Brighthouse) · Task 2 insurer SEC/deck disclosures (MET · AHL/APO · PRU · CRBG · LNC · BHF; MetLife data-centre ABS claim) · Task 3 NAIC CMB · IMF GFSR Oct 2026 · Fed FSR · BMA · Task 4 Brighthouse/Aquarian, Delaware Life, named insurer buyers. **On return: grade it against the gopher regression suite FIRST (both dates · verbatim · no interpretation; `data-sourcing-playbook:L715-720`), then ingest.**
- 🚩🚩🚩 **Schedule D pull** (an insurer's public statutory holdings list), "the highest-value item on the board" since **7/24** (AFF:L1254). **Never done.**
- 🚩🚩🚩 Delaware's decision on Brighthouse/Aquarian: no outcome filed since 8/30.
- 🔴 BHF + APO daily scan roster, proposed 8/25 — Jake never said yes or no.
- 🔴 The co-signed raise test (① clean / ② bigger guarantee / ③ fails even co-signed) — ungraded; Volta's outcome unknown at the 10/14 close.
- 🔴 An investment-grade-rated CoreWeave deal placed with NAMED insurers (who, what spread).
- ⬜ Athene Q3 10-Q (~early Nov): the funded share, the 35% reimburser · Q3 BDC tender data · NAIC / Bermuda Monetary Authority captive actions · Nippon plan → committed vehicles.

## GAPS — what the vault does NOT have
- **MetLife: 4 mentions — Burry's one claim (repeated three times) and a history line on mutual vs PE ownership (AFF:L1271). No filing, no size for its data-centre ABS, no price.** Prudential: one passing line. **Corebridge and Lincoln: zero.** Global Atlantic: as-briefed only.
- No Blue Owl, Blackstone, KKR, Ares or Brookfield filing read. No data-centre ABS spread quantified. FHLB: one source. IMF financial stability report: mentioned, never read.

→ [[ai-financing-fragility]] · [[transmission-chain]] · [[hyperscaler-credit]] · [[balance-sheet-board]] · [[forest]] · [[money-board]] · [[ai-capex-cycle]]
