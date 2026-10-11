# The AI money map — financing in / out, by layer (big picture)

*Opened 2026-10-10 ~6:55pm PDT (filed under rule 22c) on Jake's ask: "put together a clear financing in/out structure on the profitability of the AI rollout. Big picture." Built only from figures already filed; every number carries its pointer and perimeter. ⛔ **VENDOR CONFLICT: MAXIMAL** — Anthropic appears in layer 2 and this vault runs on Anthropic's model; its figures are stated as numbers only, with no view on the company.*

**WHY THIS MATTERS (plain English):** only one kind of money enters the AI build from outside: what end users (companies, consumers) pay. Every other flow is either one layer paying the next (one layer's revenue is the next one's cost) or money borrowed or raised from investors. Today the outside money is a fraction of what is being spent, and the gap is filled by equity, debt and the chip makers financing their own customers. The money question is who gets paid in cash now and who is carrying the bill if the outside money doesn't grow fast enough.

Links: [[ai-financing-fragility]] · [[hyperscaler-credit]] · [[mw-dollar]] · [[ai-capex-cycle]] · [[transmission-chain]] · [[money-board]] · [[reflection-ai]] · [[power-scarcity-equities]]

## DATA — the layers (outside money enters at the top; borrowed capital enters at the bottom)

| # | Layer | Money IN (from whom) | Money OUT (to whom) | Profitable now? | Gap funded by |
|---|---|---|---|---|---|
| 1 | **End users** (enterprises, consumers) | — (the only outside money) | Labs and clouds | n/a | Their own budgets |
  ⟲ SUPERSEDED 2026-10-11 → ai-money-map.md:L74 — layer 1 is not all outside money: 1a truly outside / 1b big tech buying rivals' models (self-liquidating; Meta >$105M/28d, halving) / 1c investor-funded AI-natives and labs (recycled venture money)
| 2 | **AI labs** (OpenAI, Anthropic, xAI inside SpaceX) | End-user revenue | Compute rent to clouds and neoclouds; talent | **No** | Equity rounds; partner borrowing |
| 3 | **Clouds and neoclouds** (AWS, Azure, GCP, Oracle; SpaceX, CoreWeave, Nebius, IREN) | Rent from labs and enterprises | Capex to chip makers, power, buildings | Renting: yes, at today's rates. Own AI use: unresolved | Operating cash, bonds, leases, SPVs, guarantees |
| 4 | **Chip makers** (NVIDIA, Broadcom, TSMC, memory, optics) | Capex, booked at shipment | Wafers, memory and, increasingly, financing back to customers | **Yes** | Cash flow; now also guarantees and receivables |
| 5 | **Power and physical** (utilities, generation, grid gear, copper, construction) | Builders' capex and power contracts | Fuel, equipment, labour | **Yes** (paid upfront or contracted) | n/a |
| 6 | **Lenders and capital markets** (private credit, banks, insurers, bonds) | Coupons and fees | Loans to layers 2–3 (and 5) | Yes, until defaults | Their own funding |

**Layer 1 — the outside money (all REPORTED or measured as noted):**
- Top three labs ~**$100B** run-rate in July; need **$180–200B** by year-end "to keep the AI trade intact" (Gerstner, via GS TMT, mixed gross/net) · GS Portfolio Strategy: the market "now needs evidence of" ~**$300B** a year of AI revenue · both via ZH 10/10 (`ai-financing-fragility` 10/10 3:00pm).
- Concentration: top 10% of customers = **99.5%** of model-serving spend, 99% of neocloud spend (Apollo 9/24, `metered-compute:L3651`).
- Price vs volume: Vercel July tokens +59%, price −13.6%, spend +37% (`mw-dollar`).

**Layer 2 — the labs:**
- OpenAI annualized revenue **~$50B** at end-September vs ~$70B circulating (FT 10/8; Bloomberg: a projection off a shorter period) (`ai-financing-fragility` 10/8).
- Anthropic (draft prospectus via Reuters, REPORTED; vendor conflict): 2025 revenue ~**$4.59B**, compute/infrastructure **$7.33B**, operating loss ~**$8.06B**, commitments "up to **$518B**" (`ai-financing-fragility` 9/29 close addendum).
- Compute bills on file: Anthropic → SpaceX **$1.25B a month** to May 2029 (SEC filing, `ai-capex-cycle:L3920`) · Jefferies estimate: the two labs ≈ **45% of GCP, 25% of Azure, 6% → 12–18% of AWS** (`ai-financing-fragility` 10/10 6:40pm).
- Funding: SoftBank borrowing **$10B + €1B at an indicated 9–10%** for its OpenAI installment (`ai-financing-fragility:L8649`).

**Layer 3 — clouds and neoclouds:**
- **Spend:** GS: **$1,726B** of AI compute capex in CY26–27 by GOOGL, MSFT, AMZN, META, ORCL, SPCX at $42.4B/GW ⇒ 40.7 GW ≈ **~$863B a year** (`hyperscaler-credit:L658`).
- **What it must earn:** **$1.42T** of AI revenue over 2028–30 (≈ **$473B a year**) = **$11.6B per GW-year** for a 15% ROIC (same).
- **What renting earns today:** short-term **$40–50B/GW-year**, multi-year **$20–25B** (NBIS, CRWV, IREN, SpaceX disclosures via GS) · SpaceX ~**$54.5B** run-rate on ~1.2 GW contracted (DB est.), ramping, on 90-day termination terms · SpaceX Q2 RECOGNIZED new-cloud revenue **$4.57–6.40M per nameplate MW-year** (MW- noncanonical diagnostic) (`ai-financing-fragility` 10/10 3:00–3:45pm; `mw-dollar` 10/10).
- **How it is funded, off the income statement:** Meta Hyperion **$46.0B** maximum exposure; **$279B** uncommenced leases (different perimeter) · Oracle RPO **$638B** (OpenAI ~$300B/5yr, reported); Jupiter ~**$18B** of loans indicated at 89–91c · SpaceX ~**$40B** chip-collateralized SPV (reported); Valor failed-sale-leaseback **$13.3B** · CoreWeave 5Y CDS **904** (10/9).

**Layer 4 — chip makers:**
- **In:** NVIDIA Q2 Data Center **$89.0B** · Broadcom Q3 AI semis **$16.7B** · TSMC Q3 ~**US$46.7B** (record).
- **Out, back to customers:** NVIDIA PORTS guarantee cap **$105B** (contingent, phased from FY2029), **$36B** of AI-cloud service commitments, equity into customers (Poolside $1B + $6B licence/hire; Reflection talks 10/10) · Broadcom **2 × $21B** senior tranches it partly backstops (SOFR+150/187.5, to 9/2033), ~**$29B** XPV lease backstop, **$126.8B** purchase commitments (mostly inventory).
- **The strain:** NVIDIA DSO **45 → 60 days**; operating cash flow **$50.3B → $24.1B** q/q (extended IG terms; not default) (`mw-dollar` 10/10).

**Layer 5 — power and physical:** Google–Constellation 3,590 MW uprates · Amazon–Calvert Cliffs 20-year · Bloom–Nebius **$1.04M per guaranteed MW-year** · constraint: the Texas pause (ERCOT audit 12/10), Jupiter's permit stay · copper LME $14,689/t near the record (`power-scarcity-equities`, `nuclear`, `new-economy-regime` 10/10).

**Layer 6 — the price of the money (10/8–10/9):** 10Y **5.24%**, 30Y **5.60%** · HY OAS **309**, CCC **1,252** (3-year wide) · ORCL 5Y CDS **255–261** (record zone) · CRWV **904** · Broadcom-backed senior at SOFR+150–187.5 · Apollo/Athene in all three of the week's chip-debt deals (`rates-board`, `ai-financing-fragility`).

## DATA — the loops on file (why "AI revenue" overstates the outside money)
- **Vendor → customer → vendor:** NVIDIA equity → Reflection/Poolside → rent to SpaceX/Nebius → NVIDIA GPUs (`reflection-ai` 10/10).
- **Guarantee loop:** vendor guarantees the customer's debt (PORTS; Broadcom's $42B senior) → lenders lend → the customer buys the vendor's chips.
- **The stack double-count:** one end-user dollar → lab revenue (gross) → cloud revenue → neocloud hosting revenue → chip-maker revenue. Summing "AI revenue" across layers counts it several times (GS Johnstone, ZH 10/10).

## THESIS (analysis — NOT fact)
1. **The scale gap.** ~$100B (July) to $180–200B (year-end target) of lab run-rate on the outside vs ~$863B a year of AI compute capex by six builders, with ~$473B a year required in 2028–30 for a 15% return: **end demand has to grow ~2.5× from the year-end target to reach the hurdle**, before any scarcity premium. ⚠️ Different perimeters (three labs' run-rate vs six builders' required revenue); use as scale, not as an identity.
2. **The core mismatch is DURATION, not today's profit.** Revenue is short (90-day hosting terms; lab revenue sustained by the next funding round). Liabilities are long (SPVs to 2029–2033, 20-year leases, guarantees phased from FY2029). Today's rents (2–4× the hurdle) are a scarcity price for capacity billing NOW, and should not be capitalised into 2028 project economics (Jake's MW- framing, `mw-dollar` 10/10 4:00pm).
3. **Who is paid in cash now:** chip makers (booked at shipment), power and grid suppliers, copper, and owners of energized capacity renting at spot.
4. **Who carries the bill if outside money slows**, in order of exposure: (a) the labs' equity holders; (b) the levered middle with short-lease revenue and long debt (Oracle, CoreWeave and other neoclouds, chip-collateralized SPVs); (c) their lenders (private credit, insurers); (d) the chip makers through guarantees, receivables and inventory commitments; (e) the hyperscalers, whose balance sheets absorb it but whose cloud growth is concentrated (GCP ~45% two labs, estimate).
5. **The transmission:** a funding slowdown at layer 2 shows up first as lease cancellations or repricing at layer 3, then as wider spreads at layer 6, then as order deferrals at layer 4 (`transmission-chain`; Jake's 10/7 stretchy-demand branch).

## MONEY — the money board already leans this way (net marks, 10/10 tally)
- **Levered middle and guarantor, bottom:** ORCL −14.2 · CRWV −11.5 · IREN −4.0 · AVGO −2.5.
- **Paid-now layers, positive:** ETN +3.5 · CEG +2.0 · PWR +2.0 · VST +1.5 · TLN +1.5 · GEV +1.0 · TSM +2.0 · MU +2.0 · NVDA 0 (paid now, but guaranteeing) · FCX +1.5.
- **Jake's ACTUAL book on this map:** CEG / VST / TLN (layer 5, paid now) · SPY 745 put (the accident hedge: the vault's 10/9 read that index puts are the cheap hedge, COR1M 7.05, VIX 7th percentile).

## 📌 THE DATED TESTS (each says whether the gap is closing or widening)
- **Wed 10/14 ~11pm PT:** TSMC Q3 wafers (layer 4 volume; ≤ +3.9% q/q = slowing).
- **Late October:** hyperscaler Q3: capex guides, any >10% customer, cloud backlog (layers 3 and 1).
- **~10/31:** Google's GPU-delivery deadline at SpaceX · **12/1:** the unnamed ~$1.11B-a-month SpaceX contract starts · **12/31:** Google's 90-day exit right opens.
- **November:** CoreWeave Q3 10-Q and the DDTL amortisation start · NVIDIA Q3 (DSO 60 → ?).
- **12/10:** ERCOT audit (layer 5 constraint).
- **Any time:** OpenAI round terms; a hosting lease cancelled or repriced; a short-term deal below $40B/GW or a term deal below $20B; ORCL CDS above 260 / CRWV above 950; CCC wider.

## Sources
All figures above are filed with primaries or labelled REPORTED in the linked notes; the 10/10 filings: `raw/2026-10-10-zh-neocloud-rents-four-times-hurdle.md`, `raw/2026-10-10-db-spacex-neocloud-tables.md`, `raw/2026-10-10-x-zh-nvidia-reflection-ft.md`, `raw/2026-10-10-zh-jefferies-openai-anthropic-share-of-cloud.md`; MW- read 10/10 (`mw-dollar`).

## 2026-10-10 ~7:15pm PDT — ⟲ CORRECTION (Jake: "Aren't you skipping the part where the AI labs themselves are also a huge portion of 'end user'? Aren't they the heaviest users of each others' models?")
  ⟲ EXTENDS ai-money-map.md:L53 (2026-10-11) — the ~$100B lab run-rate overstates outside money (1b/1c are inside the complex) ⇒ the ~2.5× gap is a floor [old entry stays LIVE]
  ⟲ SUPERSEDES ai-money-map.md:L13 — layer 1 is not all outside money: 1a truly outside / 1b big tech buying rivals' models (self-liquidating; Meta >$105M/28d, halving) / 1c investor-funded AI-natives and labs (recycled venture money)
*(⛔ VENDOR CONFLICT: MAXIMAL — the examples are big-tech purchases of Anthropic's and OpenAI's products; numbers only, no view on either company.)* **Layer 1 is not all outside money. It holds three kinds of buyer, and only the first is money from outside the AI complex.** The vault already held this (`metered-compute:L3654`, 9/24: "the heavy spenders are largely AI labs and VC-funded AI-natives ⇒ a meaningful share of 'AI revenue' is venture money recycled"); the 6:55pm map dropped it.
- **1a — truly outside:** businesses outside tech and consumers, paying from non-AI income. Includes enterprise usage resold through the clouds (Microsoft's customer-facing Anthropic consumption ≥$2B a year, REPORTED). ⬜ no source sizes this slice.
- **1b — big tech buying rivals' models:** real cash from ad and cloud profits, but spent inside the AI complex, and **self-liquidating**: it lasts until the buyer's own model catches up. **DATA (REPORTED, `compression-thesis:L3728`):** Meta spent >$105M on Claude Code in one 28-day period; its April usage was 60.2T tokens in 30 days across 85,000+ employees, ~$900M at list prices (list ≠ billed); Meta is now halving Claude Code users and restricting Codex, citing "distillation hygiene," while it builds MetaCode/Muse Code. Microsoft cancelled internal Claude Code licenses (May; `ai-capex-cycle:L416`) and cut its internal Claude projection by a third.
- **1c — investor-funded AI companies:** AI-native startups (Cursor and the coding-agent layer) and labs paying labs, funded by venture rounds. Cursor is now inside the SpaceX complex (option deal, April), runs on Anthropic/Grok models beneath its own, and loses OpenAI access 11/12 (forest 8/28 row). Private credit and venture capital are the same risk appetite (`ai-financing-fragility:L5678`).
- **And the money runs both ways between the same few firms:** the labs are ~45% of GCP and ~25% of Azure (Jefferies estimate) while big tech buys the labs' models. Part of "AI revenue" on BOTH sides is the complex trading with itself.
- **⬜ What the vault does NOT have:** a measured share of any lab's revenue that comes from other labs or big tech. "Heaviest users of each other's models" is consistent with the Meta figures (among the largest single-customer numbers on file) but is not measured.
- **THESIS (analysis):** (1) **The outside money is smaller than the ~$100B lab run-rate,** so the ~2.5× scale gap (thesis 1 above) is a floor, not a midpoint. (2) **Inter-lab demand is the most fragile slice:** each big buyer is also building the substitute (Meta's MetaCode, Microsoft in-house), and distillation means buying a rival's output can be a step toward replacing it. When the buyer catches up, that revenue turns into competition. (3) **The test is the mix, not the total:** watch for any lab disclosure of revenue by customer type (the Anthropic prospectus, when it is on EDGAR; vendor conflict), and for 1b buyers cutting usage (Meta's MetaCode rollout; the Cursor/OpenAI cutoff 11/12).
- **MONEY:** no new marks (the Meta usage cut was marked META BULL 0.5 on 10/5). The correction strengthens the map's existing lean: the layers paid in cash now (power, grid, chip makers' shipments) over the layers whose revenue depends on the complex funding itself.
