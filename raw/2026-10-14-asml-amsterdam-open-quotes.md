# ASML — first European prices after the Q3 print, Wed 2026-10-14 (pulled ~00:08–00:11 PDT = 09:08–09:11 CEST)

Source pulls, verbatim fields. Amsterdam (Euronext) opened 09:00 CEST = 00:00 PDT.

## Euronext Amsterdam — NOT OBSERVED
- Yahoo ASML.AS chart API (07:08–07:10 UTC): regularMarketTime 2026-10-13 15:38:32 UTC, price 1509.6, **0 bars for 10/14** (delayed feed not yet populated).
- Yahoo quote page via WebFetch: "As of October 13 at 5:38:32 PM GMT+2" — 1,509.60, −66.20 (−4.20%), prev close 1,575.80.
- live.euronext.com ajax endpoints: encrypted payload ({"ct": ...}); not readable.

## Tradegate Exchange (Berlin; EUR; live order book) — tradegate.de/orderbuch.php?isin=NL0010273215
- 07:09:54 UTC: Bid 1,539.20 / Ask 1,540.20 · High 1,547.40 · Low 1,470.00 · Last 1,540.20 · Change +0.33% · Turnover 20,208 TEUR · 13,483 shares · avg 1,498.813
- 07:10:26 UTC: Bid 1,538.20 / Ask 1,539.00 · High 1,547.40 · Low 1,470.00 · Last 1,538.00 · Change +0.18% · 20,267 TEUR · 13,521 shares · avg 1,498.927
- Header test: 1,540.20 ÷ 1.0033 = 1,535.13; 1,538.00 ÷ 1.0018 = 1,535.24 ⇒ Tradegate's "Change" is vs ITS OWN prior last (~1,535, its 22:00 CEST Tuesday print, after US hours), NOT Amsterdam's 1,509.60 close.
- Peers 07:10 UTC: ASM International last 836.20 (+0.43% Tradegate) · BESI 174.20 (+0.09%) · Infineon 56.86 (+0.67%).

## Börse Frankfurt API (api.boerse-frankfurt.de/v1/data/...)
- XFRA (Frankfurt floor): 24 fixings 08:00–08:58:48 CEST, day low 1,489.6, high 1,506, last 1,506 (08:58:48 CEST); prev close 1,524.8. Quote 07:09:48 UTC: bid 1,537.4 / ask 1,542.2.
- XETR: stale — status "Retail Early/Late", last 1,500.4 at 06:22:36 UTC, 2 shares traded; box timestamp frozen ~06:54 UTC. Not used.

## FX
- Yahoo EURUSD=X 1.1207 at 07:10:25 UTC.

## News (Google News RSS, pubDate GMT)
- 05:56 ad-hoc-news.de: "ASML reports EUR 11.70 billion in Q3 sales: stock pre-market at EUR 1,493.10"
- 06:11 Yahoo Finance: "ASML Raises Sales Forecast For A Third Time, But Q3 Revenue Miss Sends Stock Lower: Earnings Selloff Spreads To MU, SNDK, INTC"
- 06:27 Investing.com: "Earnings call transcript: ASML tops Q3 2026 estimates but shares fall"
- 06:51 Financial Times: "AI demand to exceed supply for 2 more years, says ASML"
- 07:03 XTB: "ASML disappoints on revenue but delivers stronger profits and raises guidance"
