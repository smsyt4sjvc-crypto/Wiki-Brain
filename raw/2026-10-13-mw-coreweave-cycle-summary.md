# Jake's paste — MW- CoreWeave cycle summary (2026-10-13 ~9:05am PT); MW- commit d8f5eff (2026-10-13 08:53 PT)

Speaking of Coreweave….

Published the CoreWeave cycle to MW-.

* Strongest finding: recent 3–6 month contracts were signed near $40M annualized revenue per MW of power required for the related clusters. The read is currently tight, but short-dated—useful for pricing, not durable fleet yield.
* PUE: not_disclosed; no defensible low/base/high range. The earlier generic PUE/utilization sensitivity was retired.
* Revenue/MW: canonical compute revenue per effective utilized IT MW remains blank. Missing inputs are compute-only revenue, IT-versus-facility power boundary, dated IT-MW activations, matched PUE, and physical utilization. Q2's noncanonical all-cloud timing ceiling is $6.87M–$10.30M per reported active-power MW-year.
* Financing: $4.2B of 2.875% converts improved liquidity, but $566.2M funded capped calls. Separately, one undelivered 393MW site carries maximum contractual rent of $14.7B over 16 years, illustrating the long-duration funding risk.
* Workbook rebuilt and validated; remote review and handoff verified.

Verified commit d8f5eff

9PM HANDOFF

Current pricing contradicts a blanket neocloud-glut thesis, but the short contract duration creates rollover risk. Recheck the unidentified $40M/MW cohort, the 393MW/355MW lease deliveries, and any disclosure that finally defines CoreWeave's power boundary or operational PUE.

---
Verified (Claude, ~9:30am PT): commit d8f5eff exists on MW- main ("Review CoreWeave pricing, leases, and MW economics (2026-10-13)"); every figure above matches `research/companies/coreweave/2026-10-13.json` and its formula checks ($2.575B×4 = $10.3B; $10.3B ÷ [1.5, 1.0] GW = $6.87–10.30M; $640M ÷ $2.575B = 24.85%; $4.137B − $0.5662B = $3.5708B; $4.2B × 2.875% = $120.75M). Filed → wiki/mw-dollar.md 10/13.
