# HANDOFF — 2026-08-08 ~7:35am PDT — PRICING, BACKLOGS AND CONTRACTED SUPPLY FOR THE PHYSICAL-AI STACK

Jake: *"We need to see where pricing, backlogs and contracted supply is for the physical AI stack."*

**Why this fetch and not another sell-side note.** The vault now holds two bank notes and ~$3bn of policy
announcements on the magnet chokepoint ([[buildout-bottleneck-map]] 8/4 + 8/8). **Every number in both is
an ANNOUNCEMENT** — capacity forecasts, targets, commitments. The evidence ladder says the next rung is
MEASURED, and for a supply chain that means exactly three things: **what it costs, how long the queue is,
and what is actually contracted.** Backlogs in particular are published, auditable, and available now.

⚠️ **THE FOUR TRAPS THIS PROMPT IS BUILT AROUND** — each one has produced a wrong number in some vault
thread before, and each is a place where a plausible answer can be quietly incomparable:
1. **THERE IS NO SINGLE "MAGNET PRICE."** Chinese *domestic* NdPr oxide, Chinese *export* price, ex-China
   spot, and *long-term contract* price are four different series that diverged after the 2025 export
   controls. An answer that gives one number without saying which is unusable.
2. **JAPANESE FISCAL YEARS END MARCH 31.** Harmonic Drive and Nabtesco report on a fiscal calendar that does
   not align to calendar quarters — the same trap that would have corrupted the CEPI series (MSFT June 30,
   Oracle May 31). Every backlog figure must state its fiscal period explicitly.
3. **"CONTRACTED" IS FOUR DIFFERENT COMMITMENTS.** Memorandum of understanding (MOU) / letter of intent
   (LOI) / binding offtake / take-or-pay are not the same object, and only the last two are supply.
4. **⭐ PRICE FLOORS BREAK THE PRICE SIGNAL.** US government arrangements in this sector have included
   *price floors* on neodymium-praseodymium (NdPr). **Where a floor exists, the observed price is a policy
   number, not a market-clearing one** — and reading it as a shortage signal would be a category error.

**FIRST-USE:** NdFeB = neodymium-iron-boron (the permanent-magnet alloy) · NdPr = neodymium-praseodymium
oxide (the key feedstock) · Dy/Tb = dysprosium/terbium (heavy rare earths for heat resistance) ·
MGOe = mega-gauss-oersted (magnetic energy product, the performance metric) · ASP = average selling price ·
FID = final investment decision · TSE = Tokyo Stock Exchange.

---

## THE PROMPT

> Pull **current, sourced, dated** figures. Return plain tables. **No estimates, no commentary.** If a
> number is not public, write **NOT DISCLOSED**. If you are deriving or converting anything, say so on that
> line. **Every row needs a source and an as-of date.**
>
> ### PART 1 — PRICING (the four-series problem)
> For **NdPr oxide**, **dysprosium oxide**, **terbium oxide**, and **finished NdFeB magnets**, give the
> **latest price and the price 12 months ago**, and **state explicitly which series each is**:
> - (a) China domestic spot · (b) China export · (c) ex-China / rest-of-world spot · (d) long-term contract
>
> State the **currency and the unit** (USD/kg vs RMB/tonne — do not silently convert). Name the price
> assessor (Asian Metal, Shanghai Metals Market, Fastmarkets, Argus, or other).
>
> **Also: does any US government price floor or offtake currently apply to NdPr or NdFeB — and if so, at
> what level, for which company, and since when?** This one matters more than the spot print.
>
> ### PART 2 — BACKLOGS AND LEAD TIMES (the measurable queue)
> For each company: **order backlog, order intake, book-to-bill, and quoted lead time**, most recent
> reported period **and** the year-ago comparison.
> - **Harmonic Drive Systems** (TSE 6324) — precision reducers
> - **Nabtesco** (TSE 6268) — precision reducers
> - **MP Materials** (NYSE: MP) — mining/refining/magnets
> - **Lynas Rare Earths** (ASX: LYC)
> - **Vacuumschmelze**, **Noveon**, **Vulcan Elements**, **Niron Magnetics** — if any disclose
>
> **⚠️ For the two Japanese names, state the fiscal period explicitly** (e.g. "FY2026 Q1 = Apr–Jun 2026").
> Do not map Japanese fiscal quarters onto calendar quarters silently.
>
> ### PART 3 — CONTRACTED SUPPLY (classify every item)
> List announced magnet/rare-earth supply agreements from **Jan 2025 to now** with a Western buyer or
> government, and for each give: **counterparties · tonnes/yr · start year · duration · and the COMMITMENT
> CLASS — MOU / LOI / binding offtake / take-or-pay.** Flag which have reached **FID** and which have
> **commissioned physical capacity** versus being announcements only.
>
> Specifically include, with current status: the **~$750M Vulcan Elements + ReElement Technologies**
> arrangement (targeting 10,000 t/yr) and the **Niron Magnetics** Department of War awards.
>
> ### PART 4 — THE ACTUATOR LAYER (thinner data — say so if it is not public)
> - Humanoid **actuator ASP**, and the **reducer share** of actuator cost
> - Any disclosed **humanoid production/delivery numbers for 2025 and 2026 to date** — units, by company
> - Any **rare-earth-free magnet** performance disclosure: **MGOe versus NdFeB**, and delivered tonnage
>
> ### FORMAT
> `item | series/class | latest value + date | year-ago value | source (publication + date)`
>
> **Flag explicitly:** any figure that is a company target rather than a reported actual; any series
> discontinued or redefined in the last 18 months; and any case where Chinese export licensing makes a
> quoted price non-comparable to the prior year.

---

## WHAT EACH PART SETTLES IN THE VAULT
| part | closes |
|---|---|
| 1 — pricing | whether the chokepoint is **binding now** or **anticipated**. Announcements do not move prices; scarcity does. |
| 1 — price floors | ⭐ whether the price signal is even readable, or is a policy artifact |
| 2 — backlogs | **the cheapest falsifiable test in the whole thread.** A real reducer constraint shows up as book-to-bill and lead times in public filings **today**, not in a 2030 forecast |
| 3 — contracted | converts the 8/8 policy entry from ANNOUNCED to FID/COMMISSIONED on the vault's own ladder |
| 4 — actuators | the 30-50% bill-of-materials claim, and registered test #2 (rare-earth-free magnets obsoleting rather than relieving the NdFeB thesis) |

**Then:** paste the digest back and say "ingest." It lands in [[buildout-bottleneck-map]] (magnets/policy)
and [[physical-ai-hardware-stack]] (actuators/reducers), and it should resolve or sharpen registered
tests 1-4 in the 8/8 entry.
