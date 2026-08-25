# data/ — datasets for the brain

Drop CSVs / spreadsheets here (e.g. the macro database). Then in any chat say
**"ingest the macro data"** and I'll pull it from the repo and write the interpreting
wiki note (facts as DATA, the regime read as THESIS).

## Stored
- `jake-bishop-project-memory.csv` — CANONICAL. Full trading-project memory (profile, comm
  style, 11-vector convergence stack, 4-basket + Tier A/B/C portfolio, positions, hedges,
  principles, tools, open decisions). Supersedes earlier partial `portfolio-state` guesses.
  Dated 2026-06-30. Full reconciliation into `wiki/portfolio-state.md` still pending.

## Stored (macro)
- `macro_2019_present.csv` — LIVE, monthly 2019→2026-06, 28 cols (Fed rate, WALCL, M2, RRP,
  debt, debt/GDP, CPI/core-CPI/PCE/core-PCE + YoY, breakevens, 3m/2y/10y + curve, unemployment,
  real GDP, S&P, VIX, dollar, WTI, HY OAS, real fed funds). Pulled via the **Colab** cell (NOT
  ChatGPT — its sandbox returned stale 2024 data). Sanity-checked: SP500 2026-06 = 7,499.36.
  ⚠️ `fed_assets_pct_gdp` column is bad (= WALCL raw, not divided by GDP) — ignore it.
  Refresh monthly by re-running the Colab cell + overwrite. Read: `wiki/new-economy-regime.md`.
- `postcovid_2022.csv` — monthly 2022-01→2026-05: CPI, energy CPI, median nominal + real weekly
  wage (`LEU0252881500Q`/`LES1252881600Q`, quarterly), unemployment rate + median duration
  (`UEMPMED`), JOLTS hires/quits/layoffs (`JTSHIR/JTSQUR/JTSLDR`). Re-baselined to 2022 to strip
  the front-loaded wage jump. Chart: `raw/postcovid-2022-wages-labor.jpeg`.
  NOTE: BLS weekly-wage FRED IDs need the **Q** suffix (bare IDs 404).
