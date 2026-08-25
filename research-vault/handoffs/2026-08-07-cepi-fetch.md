# HANDOFF — 2026-08-07 ~2:55pm PDT — THE 60 NUMBERS THAT TURN `cepi_tracker_cell.py` INTO A SERIES

Paste the block below into ChatGPT / Perplexity / Gemini (whichever browses best). Paste the digest
back and say "ingest." Tier 1 alone makes the tracker work; Tier 2 makes it a trend.

⚠️ **THE TWO TRAPS THIS PROMPT IS BUILT AROUND:** (1) **finance leases** — headline capex often
excludes them and that is where AI infrastructure hides (the vault caught a $132B gap this way);
(2) **fiscal-vs-calendar quarters** — MSFT's FY ends June 30 and ORCL's ends May 31, so their fiscal
quarters do NOT align with calendar quarters. A silent mismatch would corrupt the whole series.

---

## THE PROMPT

> You are pulling exact line items from SEC filings (10-Q / 10-K / earnings releases). Return a plain
> table. **No commentary, no estimates.** If a number is not disclosed, write **NOT DISCLOSED**. If you
> are inferring or deriving anything, say so on that line.
>
> **COMPANIES:** Microsoft (MSFT), Alphabet (GOOGL), Amazon (AMZN), Meta (META), Oracle (ORCL).
>
> **PERIODS — report by CALENDAR QUARTER:**
> - **TIER 1 (do these first):** calendar **2026 Q1** and **2026 Q2**
> - **TIER 2 (if you can):** calendar **2025 Q3** and **2025 Q4**
>
> **⚠️ FISCAL-YEAR WARNING — this matters and I need you to be explicit:** Microsoft's fiscal year ends
> June 30 and Oracle's ends May 31, so their fiscal quarters do not match calendar quarters. **For every
> row, state which fiscal period you used** (e.g. "MSFT FY2026 Q4 = calendar Q2 2026" or "ORCL FY2026 Q4
> = Mar–May 2026, does not align with calendar Q2"). Do not silently map one to the other.
>
> **SIX LINE ITEMS PER COMPANY PER QUARTER, all in $ millions, QUARTERLY (not year-to-date, not TTM):**
> 1. **Total revenue**
> 2. **Capital expenditures** — the cash flow statement line ("purchases of property and equipment" or
>    equivalent). **AND SEPARATELY: finance-lease additions / assets acquired under finance leases** for
>    the same quarter (usually in the leases footnote or supplemental cash-flow disclosure). **Report
>    these as two distinct numbers — do not combine them.**
> 3. **Net income (GAAP)**
> 4. **Net cash provided by operating activities**
> 5. **Depreciation and amortization** (cash flow statement)
> 6. **If disclosed:** total purchase commitments / remaining performance obligations, and any stated
>    change in useful-life assumptions for servers or network equipment.
>
> **Also, separately, for SpaceX (SPCX) calendar Q2 2026:** net income (GAAP), net cash from operating
> activities, and depreciation & amortization. *(I already have revenue $7,814M, capex $18,369M,
> adjusted EBITDA $3,538M, operating income −$143M — I need the three missing lines.)*
>
> **FORMAT — one row per company-quarter:**
> `TICKER | CALENDAR QTR | fiscal period used | revenue | capex | finance leases | net income | operating cash flow | D&A | source (filing + date)`
>
> **Flag explicitly if:** any company changed depreciable-life assumptions during these periods, or
> restated a prior quarter.

---

## WHAT EACH NUMBER UNLOCKS IN THE CELL
| line item | fills |
|---|---|
| revenue + capex | **C/R** (intensity) — the only ratio currently populated |
| net income + capex | **E/C** — Jake's ask |
| operating cash flow + capex | **OCF/C** — the self-funding threshold at 1.00 |
| D&A + capex | **DA/C** — the catch-up ratio that keeps E/C from lying |
| finance leases | corrects capex upward; the vault's $196.6B-vs-$329.1B trap |
| useful-life changes | the single cheapest way to flatter earnings — worth catching |

**Then:** add one `dict(...)` line per company-quarter to `FILINGS` in `tools/cepi_tracker_cell.py`
and re-run. The series builds itself.
