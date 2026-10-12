# "84% of S&P 500 stocks are now trading at least -10% below their all-time highs" — Jake's paste 2026-10-11 ~8:25pm PDT + replication

## Paste (aggregator "BREAKING" format)
> BREAKING: 84% of S&P 500 stocks are now trading at least -10% below their all-time highs.
> Real Estate leads the drawdown, with 97% of stocks down at least -10%, followed by Materials at 96%, Utilities at 94%, and Consumer Discretionary at 92%.
> By comparison, Energy has held up relatively better, with 62% of stocks more than -10% below their all-time highs, followed by Healthcare at 70% and Information Technology at 72%.
> Furthermore, 59% of S&P 500 stocks are down at least -20% from their highs, 41% are down more than -30%, and 17% are down more than -50%.
> Meanwhile, the S&P 500 is just 0.2% from its all-time high set on Tuesday.
> A few names are carrying the entire stock market.

## Replication (yfinance, 503 current members from Wikipedia, as of Fri 10/9 close; run ~8:30pm PDT 10/11)
| bucket | post | PRICE vs intraday ATH | PRICE vs closing ATH | DIVIDEND-ADJUSTED vs closing ATH |
|---|---|---|---|---|
| ≥10% below | 84% | **83.3%** | 81.3% | 79.1% |
| ≥20% below | 59% | **58.3%** | 56.5% | 48.5% |
| ≥30% below | 41% | **42.5%** | 41.4% | 33.2% |
| ≥50% below | 17% | **17.5%** | 16.9% | 13.3% |
Median member: −25.8% from its intraday ATH (price).
Sectors, ≥10% below (price vs intraday ATH; post in brackets): Real Estate 96.7 [97] · Utilities 93.5 [94] · Materials 91.7 [96] · Consumer Staples 91.2 [—] · Consumer Discretionary 89.4 [92] · Industrials 88.0 · Financials 86.8 · Communication Services 86.4 · Information Technology 72.0 [72] · Health Care 70.0 [70] · Energy 57.1 [62] (Energy n=21, so one name ≈ 4.8 points).
S&P 500: last close 7,811.54 (10/9) · record close 7,818.93 Tue 10/6 (−0.09%) · intraday record 7,844.52 (10/6, −0.42%). Post's "0.2%" sits between the two.

## % of members above their own 200-day average (dividend-adjusted closes, current members)
2025-12-31 62.1 · 2026-03-31 49.5 · 6/30 62.3 · 7/31 68.7 · 8/14 75.2 · 8/18 72.2 · 8/31 69.0 · 9/15 57.2 · **9/30 42.4 (2026 low)** · 10/2 45.8 · **10/6 50.2** · 10/9 50.0. 2026 high 75.6 (8/19).
**S&P record closes since August with the reading on the day:** 8/4 7,736.52 (72.9%) · 8/7 7,757.64 (74.1%) · **8/13 7,798.99 (75.4%)** · **10/6 7,818.93 (50.2%)**.
By sector now (% above 200-day): Health Care 76.7 · IT 73.3 · Energy 71.4 · Financials 53.9 · Staples 48.5 · Industrials 43.2 · Discretionary 34.0 · Comm Services 31.8 · Materials 29.2 · Real Estate 23.3 · Utilities 16.1.
⚠️ Current members only (survivorship); Rubner's 8/14 reading was 72% on his own method vs 75.2% here — compare within one method.
Per-name file: `data/breadth/2026-10-09.csv` · tool: `tools/breadth_divergence.py`.
