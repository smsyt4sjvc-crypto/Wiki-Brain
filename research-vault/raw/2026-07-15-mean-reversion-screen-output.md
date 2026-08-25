# Mean-reversion / index-support screen — Stage 1 output (2026-07-15 ~4:10pm PT)

Source: `research-vault/tools/mean_reversion_screener.ipynb`, S&P 100 universe, 2y lookback,
Jake ran on Colab. Criteria: range 1.5-3.5% / autocorr<0 & Hurst<0.5 / half-life 2-40d /
R²-to-SPY>0.35 / worst-day>-15%.

## Full-profile names (passes = 5)
| ticker | range% | autocorr | hurst | half-life | R²-SPY | worst-day |
|--------|--------|----------|-------|-----------|--------|-----------|
| BLK  | 1.96 | -0.029 | 0.441 | 33.5 | 0.469 | -7.7  |
| MET  | 1.91 | -0.061 | 0.386 | 23.4 | 0.403 | -9.0  |
| META | 2.47 | -0.041 | 0.429 | 30.4 | 0.398 | -11.3 |
| QCOM | 2.78 | -0.098 | 0.497 | 20.1 | 0.377 | -11.5 |

## Key rows (context)
- 4-pass financials cluster: MS, EMR, AXP, JPM, USB, GE, ITW (high R² + reverting).
- Staples/utilities knocked to 3 (or fewer) SOLELY on R²≈0: MCD(4, R²0.023), PG(3, 0.004),
  SO(3, 0.002), DUK(3, 0.009), KO(2, 0.001), PEP(3, 0.002), CL(3, 0.000).
- Mega-cap compounders scored low on POSITIVE autocorr (trending): AAPL +0.021 (hl 473),
  MSFT +0.030, GOOGL +0.038 (hl NaN) — read as trenders, not reverters.
- NVDA 3 passes but FAILED crash (-17%), hl 102 = high-beta lone-wolf, excluded.
- Bottom (1 pass) = the wild crashers: INTC (4.6% range, -26%), TSLA (-15%), AMD (-17%),
  UNH (-22%), INTU (-20%).
