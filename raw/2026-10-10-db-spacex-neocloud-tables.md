# Deutsche Bank "Got compute?" tables (via ZH) + ZH rate-card chart — Jake's screenshots, 2026-10-10 ~2:50pm PDT

Files: `2026-10-10-db-spacex-neocloud-deals-fig2.png` · `2026-10-10-db-spacex-compute-capacity-fig1.png` · `2026-10-10-zh-rate-card-chart.png`. Jake: "Spacex X as neocloud and compute curve".

## Figure 2: Neocloud deals (Source: Company reports, Deutsche Bank Research) — transcribed; grey cells = DB estimates
| Customer | Chip | GPUs (000) | $/hr | Revenue ($m, 8,760h) | MW | $m/MW |
|---|---|---|---|---|---|---|
| #1 | H100 | 150 | 3.50 | 4,599 | 195 | |
| #1 | H200 | 50 | 4.81 | 2,107 | 50 | |
| #1 | GB200 | 125 | 7.55 | 8,267 | 235 | |
| #1 total | | 325 | 5.26 | 14,973 | 480 | 31 |
| Google | GB300 | 110 | 11.46 | 11,040 | 220 | 50 |
| Reflection AI | GB300 | 18 | 11.74 | 1,800 | 35 | 51 |
| #2 | GB300 | 110 (est) | 13.90 (est) | 13,394 | 220 (est) | 61 |
| #3 | GB300 | 110 (est) | 13.80 (est) | 13,298 | 220 (est) | 60 |
| Total | | | | 54,504 | | |

Arithmetic check (Claude): every revenue cell = GPUs × $/hr × 8,760 (Reflection reproduces at ~17.5k GPUs, shown rounded to 18); total 54,505; MW total 1,175 ⇒ $46.4B/GW blended. kW per GPU: H100 1.30 · H200 1.00 · GB200 1.88 · GB300 2.00 (DB's MW allocation; IT vs facility ⬜).
**Customer #1 = Anthropic** per the SEC free-writing prospectus already on file (`ai-capex-cycle:L3920`, 10/8): "$1.25 billion per month through May 2029", ~325,000 GPUs on Colossus I/II ⇒ $15.0B/yr vs DB 14,973. Google: "$920 million per month from October 2026 through June 2029" ⇒ $11.04B/yr vs DB 11,040. CFO (9/10): ~$1.11B/month from 12/1 ≈ $13.3B/yr ≈ DB #2/#3.

## Figure 1: Compute capacity (Source: Company reports, Deutsche Bank Research, X post from Elon Musk)
| Site | GPUs | MW |
|---|---|---|
| Colossus I Phase 1 | 100k H100 | 130 |
| Colossus I Phase 2 | 50k H100 + 50k H200 + 30k GB200 | 170 |
| Colossus I total | 230k | 300 |
| Colossus II Phase 1 | 110k GB200 | 210 |
| Colossus II Phase 2 | 110k GB300 | 220 |
| Colossus II Phase 3 | 220k GB300 | 440 |
| Colossus II Phase 4 | 110k GB300 | 220 |
| Minihard (grey) | 220k GB300 | 440 |
| Phase 5 (grey) | 220k GB300 | 440 |
| Phase 6 (grey) | 220k GB300 | (blank; total implies 440) |
| Colossus II total | 1,210k | 2,410 |
| Overall | 1,440k | 2,710 |

Check: Colossus II listed MW sum 1,970; the 2,410 total implies Phase 6 = 440. Unshaded (Colossus I + II phases 1–4) = 1,390 MW ≈ Goldman's 1.4 GW (2Q26).

## ZH chart "Spot Is Four Times The Hurdle"
Neocloud short-term (NBIS, CRWV, SpaceX) $40–50bn · SpaceX hosting deals (DB est.) $31–61bn by deal ($40–45bn blended; footnote: $54.5bn run-rate on 1.2–1.4 GW) · long-term hosting (IREN, NBIS, SpaceX LT) $20–44bn · frontier-lab token revenue potential (JPM) $20–40bn (vs $10bn 2025) · hyperscaler revenue needed for 15% ROIC (Goldman) $11.6bn base · Street-implied SpaceX non-hosting 2027–28 $8–13bn.
