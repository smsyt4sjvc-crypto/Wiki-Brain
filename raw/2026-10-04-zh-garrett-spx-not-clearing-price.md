# ZH — "Correlated With Almost Nothing But Itself": Goldman's Top Derivs Trader Says S&P Is No Longer The Clearing Price For Risk
Jake's paste (headline only), Sun 2026-10-04 ~8:30pm PT. Published 2026-10-04 23:16 ET. Paywalled ("pro subs") after the opener;
the Brian Garrett "Weekend Prep" note itself is NOT read — only the lines below are DATA.
URL: https://www.zerohedge.com/markets/correlated-almost-nothing-itself-goldmans-top-derivs-trader-says-sp-no-longer-clearing

## Visible text (verbatim)
For most of modern market history, the S&P 500 did one job: it was the place where every other risk – rates, oil, credit, the consumer – eventually got priced. But according to Goldman's top derivatives trader, it has quietly quit that job.
"This week made it even more clear that SPX spot is no longer behaving like the clearing price for risk," Goldman derivatives guru Brian Garrett, writes in his latest Weekend Prep note (available to pro subs here), adding that correlations "across almost everything have broken down" vs the S&P, which "seems to be increasingly correlated with almost nothing but itself" – and even then, he notes, "it's a stretch eq weight vs mkt cap."
Correlated With Nothing (Not Even Itself)

[cut: "Sign Up For ZH Premium"]

## The vault's tape test (Yahoo daily closes via tools/tape.py, 2y window, through Fri 2026-10-02 close; computed ~8:35pm PT)
Rolling 20-day correlation of SPY daily log returns vs each pair; "pct" = where the latest 20d reading sits in the 2y
history of 20d readings (excluding the latest window).

| pair | tk | 10d | 20d | 2y median | 2y min | pct |
|---|---|---|---|---|---|---|
| equal-weight | RSP | 0.73 | 0.79 | 0.80 | 0.29 | 45 |
| small caps | IWM | 0.75 | 0.75 | 0.84 | 0.49 | 14 |
| financials | XLF | 0.51 | 0.55 | 0.67 | −0.07 | 28 |
| 20Y+ Treasuries | TLT | 0.82 | 0.63 | 0.23 | −0.70 | 93 |
| HY credit | HYG | 0.83 | 0.68 | 0.72 | 0.19 | 40 |
| Brent | BNO | −0.53 | −0.56 | −0.03 | −0.81 | 20 |
| gold | GLD | 0.38 | 0.47 | 0.18 | −0.74 | 79 |
| Nasdaq-100 | QQQ | 0.94 | 0.92 | 0.94 | 0.75 | 22 |
| semis | SOXX | 0.91 | 0.63 | 0.78 | 0.17 | 13 |

Drift, 20 sessions to 10/2: SPY −0.46% · RSP −4.69% (5 sessions: SPY −0.22% · RSP −0.65%).
Week of 9/28–10/2, daily %: SPY −0.74 / −0.18 / −0.21 / +0.18 / +0.74 · RSP −0.65 / −0.11 / −0.71 / +0.47 / +0.35 ·
TLT −0.88 / −0.50 / −0.58 / −0.09 / −0.30 · BNO +1.14 / −2.62 / +2.28 / +4.76 / +0.24 · HYG −0.41 / −0.23 / −0.19 / −0.40 / +0.01.
VIX 15.31 (10/2) · VIX3M 18.01 · VVIX 87.02 (from 92.01). COR1M/COR3M: CBOE index endpoint 403, Yahoo has no symbol — ⬜ (last on file 7.59, 9/22).
