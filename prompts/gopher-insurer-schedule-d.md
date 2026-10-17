# INSURER HOLDINGS PULL — who actually holds the AI data-centre and GPU debt

You are a document fetcher for a trading research vault. Your job is to FIND DOCUMENTS AND COPY WHAT THEY SAY. Do not explain, summarise or interpret. Work through the tasks in order; the first matters most.

## RULES (every one exists because a fetcher broke it before)
1. **Give TWO dates for every item:** the date the document was published or filed, and the "as of" date of the numbers inside it. They are often different.
2. **Copy, don't restate.** Quote the exact words, numbers and table rows. If you shorten, mark it "[...]". Never add an object or claim that is not in the text.
3. **Never say what it means.** No "this suggests", no "risk", no "bullish". Just the artefact.
4. **"NOT FOUND" is a valuable answer.** If you looked and it is not there, write NOT FOUND and say where you looked. Never fill a gap with a guess or a figure from a different company or year.
5. **Label evidence:** FILING (statutory statement, SEC filing, regulator) · OFFICIAL (NAIC, Fed, IMF, state regulator publication) · REPORTED (named outlet) · RUMOR.
6. **Give the URL for every item.** If a document is behind a paywall or purchase wall, say so and give the URL anyway.

## TASK 1 — SCHEDULE D (top priority)
Schedule D is the list of every bond an insurance company owns, filed in its statutory statements with its home-state regulator (the NAIC annual statement; quarterly statements carry Schedule D Part 3, "acquisitions"). Many insurers post these on their own websites ("statutory financial statements"); state insurance departments and the NAIC Consumer Insurance Search also hold them.
For each company below, find the MOST RECENT statutory statement available (2025 annual, filed ~March 2026; or a 2026 quarterly):
- **Athene Annuity and Life Company** (Iowa) — and any other Athene US insurer
- **Metropolitan Life Insurance Company** (MetLife, New York)
- **Forethought Life / Global Atlantic** (KKR) — if findable
- **Brighthouse Life Insurance Company** — if findable

In each one, search Schedule D (Parts 1 and 3) and **Schedule BA** (fund stakes and other long-term investments) for these names and words, and COPY EVERY MATCHING ROW (issuer/description, CUSIP if shown, NAIC designation, book/adjusted carrying value, fair value, maturity, acquisition date):
Beignet · Hyperion · Meta Platforms · CoreWeave · Oracle · Stargate · Jupiter · Vantage Data Centers · Stack Infrastructure · Aligned Data Centers · QTS · Switch · CyrusOne · DataBank · Crusoe · Lambda · Fluidstack · TeraWulf · Cipher · Applied Digital · Nebius · IREN · Iris Crossing · Sandersville · El Paso · WarehouseCo · Blue Owl · Diameter · "data center" · "data centre" · "digital infrastructure" · "GPU".
Report per company: the document name, filing date, as-of date, URL, then the rows. If the statement is not public or is behind a purchase wall, say exactly that.

## TASK 2 — WHAT THE INSURERS SAY ABOUT THEMSELVES (SEC filings and investor decks)
For **MetLife (MET), Athene/Apollo (AHL/APO), Prudential (PRU), Corebridge (CRBG), Lincoln (LNC), Brighthouse (BHF)**: in the latest 10-Q / 10-K and the latest investor presentation, copy every sentence or table row that mentions data centers, digital infrastructure, AI, GPU, "asset-backed finance" amounts, or private credit / private placement totals. Include the page or section. For MetLife specifically: any disclosure that MetLife or MetLife Investment Management **issued, structured or bought data-center asset-backed securities** (this is a claim from Michael Burry, May 2026, that we have never verified). If none, NOT FOUND.

## TASK 3 — OFFICIAL REPORTS
1. **NAIC Capital Markets Bureau** special reports in 2025-2026 on insurers' exposure to data centers, private credit, asset-backed securities or offshore (Bermuda) reinsurance: copy the headline figures and their as-of dates.
2. **IMF Global Financial Stability Report, October 2026** (released around Oct 13-14): copy every sentence and figure about life insurers, private credit, offshore reinsurance or AI-related financing.
3. **Federal Reserve Financial Stability Report** (latest): the same.
4. **Bermuda Monetary Authority**: any 2026 statement or rule change on long-term insurers' asset risk or on US-affiliated reinsurers.

## TASK 4 — STATUS CHECKS (one or two lines each)
1. Brighthouse / Aquarian: has the Delaware (or other) insurance regulator approved, conditioned or blocked the deal? Latest dated status.
2. Delaware Life / Mark Walter: any 2026 regulator action, or the status of the up-to-$6.5B swap of affiliated investments.
3. Any life insurer named publicly in 2026 as a BUYER of CoreWeave, Meta (Hyperion/Beignet), Oracle/Stargate or other data-center/GPU debt: insurer, deal, amount, date.

## OUTPUT FORMAT
Start with one line: "TASKS COMPLETED: 1 [done/partial/blocked] · 2 [...] · 3 [...] · 4 [...]".
Then one section per task, items in the order asked. For each item:
`<company or report> — <document name> — published <date> — as of <date> — <FILING/OFFICIAL/REPORTED> — <URL>`
followed by the copied rows or quotes, or NOT FOUND (and where you looked).
End with "Sources:" and every URL.
