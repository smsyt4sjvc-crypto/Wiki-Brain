# Subagent verification digest — IDC server tracker, TrendForce Weekly Radar 004, Fatima & Li arXiv:2610.05502 (fetched 2026-10-09 ~8:45am PT)
Checks the other tool's items 1, 4, 5 (`raw/2026-10-09-other-tool-ai-infra-research-5-reads.md`) against primaries.

## IDC — CONFIRMED; the annual-total conflict is REAL
Sources: IDC "Servers Market Insights" https://www.idc.com/promo/servers/ ("Updated: October 9, 2026"); IDC press release Sep 10, 2026 "Worldwide Server Market Revenue Hits Record $166.3 Billion in the Second Quarter of 2026…" (full text via https://www.emsnow.com/idc-posts-worldwide-server-market-revenue-for-q2-2026/). Basis: IDC Worldwide Quarterly Server Tracker, all servers, vendor revenue.
- Q2'26 revenue $166.3B ($166,319.2M) vs $109.4B Q2'25 = +52.0% YoY. Unit shipments +15.4% YoY. Absolute unit count: NOT FOUND.
- Subsets: non-x86 $74.4B (+146.0%, 44.8% share); x86 $91.9B (+16.1%); GPU-accelerated $87.4B (+28.1%, 52.6% share); other accelerated $27.5B (+237.6%).
- GPU-server ASP $118.6K → $170.2K (+43.6%) with GPU-server UNITS −10.8% YoY. Non-accelerated ASP $9.8K → $13.0K (+33.5%) with units +16.7%.
- Insights-page narrative: "IDC forecasts 2026 vendor revenue of $685.1 billion, up 54% from 2025… full-year shipments are expected to rise only about 12%." 28.4% CAGR to 2030, $1.58T.
- Insights-page table: 2025 $453,533M; 2026 $701,592M (+54.7%); 2027 $1,020,760M (+45.5%). 2026 split: non-x86 $311,904M (+101.3%), x86 $389,688M (+30.5%).
- CONFLICT: narrative $685.1B vs table $701.6B ($16.5B gap). On the table's 2025 base $685.1B = +51.1%, not 54%; $701.6B = +54.7% (matches "54%"). Table-implied 2026 revenue per unit: 1.547/1.12 − 1 = +38%.
- Earlier snapshot of the same page (Q1, via search index): 2026 total $646,998M (+42.7%). March 2026 press report (InfotechLead 3/13): $565.9B (+24.3%). The forecast was raised twice.
- Q2 revenue per unit: 1.52/1.154 − 1 = +31.7%.

## TrendForce — CONFIRMED (table is an image, read directly)
Source: "Weekly Radar 004: DRAM Tightness Is Becoming an Enterprise SSD Constraint", Oct 5, 2026 — https://insights.trendforce.com/p/weekly-radar-004 (Substack newsletter, not a trendforce.com press release).
Oct 5 (status, current lead time, balanced benchmark): CPU Tight 25–30w vs 16–20w · GPU Balanced 30–40w vs 30–40w · DRAM Very Tight 20w vs 8w · NAND (eSSD) Tight 16w vs 8w · HDD Very Tight 50w vs 16w · ABF Very Tight 48–56w vs 12w · MLCC Tight 35w vs 12w.
- GPU quick take: "Blackwell series will remain the main shipping platform through 2026… Rubin… system-level testing and validation issues persist, with volumes expected to ramp gradually from 4Q26 or 1Q27."
- eSSD: "The DRAM shortage is constraining some NAND suppliers' ability to support enterprise SSD solutions. As a result, enterprise SSDs are expected to remain undersupplied through 2026." (constraint = DRAM specifically)
- HDD: Toshiba expansion "will take at least 12 to 24 months… unlikely to improve before late 2027."
- Prior weeks: Sep 14 GPU 20–30w/20–30w, MLCC 30w, others identical · Sep 21 GPU 30–40w/30–40w (benchmark re-based in lockstep), MLCC 32w · Sep 28 CPU added 25–30w/16–20w, MLCC 32w · Oct 5 only MLCC moved (35w). DRAM / eSSD / HDD / ABF flat four straight weeks.

## Fatima & Li — CONFIRMED (preprint)
"Unlocking AI Data Center Interconnection Capacity Through Coordinated Grid and Data Center Flexibility" — Rida Fatima, Xingpeng Li (University of Houston). arXiv:2610.05502 [eess.SY], v1 2026-10-04 20:17 UTC, 23 pp. Preprint, no journal ref. https://arxiv.org/abs/2610.05502
- Network: 116-bus model derived from IEEE 123-node feeder; constrained connection at bus 60; day-ahead MISOCP.
- Bus 60 (training / inference / mixed): BASE 10.5–10.6 MW · grid-side (CVR + network topology reconfiguration) +42.5–45.0% (14.9–15.4 MW), nearly all from topology reconfiguration, CVR ~0 · DC flexibility alone (workload shifting + UPS) +2.1–5.4% · coordinated +45.9–50.8% (15.3–16.0 MW; 16.0 inference case hits the UPS reserve ceiling).
- Location-dependent: bus 35 no grid-side gain; bus 90 BASE ≈ GRID ≈ 14.8 MW. Combined adverse condition: FULL capacity −3.4%.
