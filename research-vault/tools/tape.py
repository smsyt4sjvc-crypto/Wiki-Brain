#!/usr/bin/env python3
"""
tape.py — the ONLY sanctioned way this vault pulls a quote.

⛔ WHY THIS FILE EXISTS. On 2026-08-14 I published a market table to Jake and filed
it to the vault with EVERY SIGN WRONG:

        filed          actual (vs the prior session's close)
   5Y    -8bp           +3bp
  10Y    -4bp           +5bp
  30Y     0bp           +6bp
  S&P  +0.45%         -0.13%
  VIX  -5.43%         -0.82%

One bug produced all of it. I used the Yahoo chart API's `meta.chartPreviousClose`
as "yesterday's close." IT IS NOT. It is the close immediately BEFORE THE REQUESTED
RANGE WINDOW — so it is range-dependent and almost never the prior session:

    range=5d   -> chartPreviousClose = 7757.64   (the close ~5 sessions back)
    range=10d  -> chartPreviousClose = 7600.50   (the close ~10 sessions back)
    actual prior session close (Thu 8/13)       = 7798.99

The failure was SILENT and DIRECTIONALLY PLAUSIBLE — a rally instead of a selloff on
a weak data day — which is the worst kind. It was caught only because Jake sent a
screenshot of his Fidelity app showing -0.14% while I had told him +0.45%.

⇒ THE RULE: the prior close is a value in the CLOSE ARRAY, never a value in `meta`.
   Read the series. Take the last COMPLETED session. That is the only reference.

Usage:
    python3 tools/tape.py ^GSPC ^IXIC ^RUT ^VIX ^FVX ^TNX ^TYX XRT
    from tape import quote;  q = quote("^GSPC")
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone

UA = {"User-Agent": "Mozilla/5.0"}
YIELD_TICKERS = {"^FVX", "^TNX", "^TYX", "^IRX"}   # quoted in percent -> report bp


def _fetch(ticker, rng="1mo"):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?range={rng}&interval=1d")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as fh:
        return json.load(fh)["chart"]["result"][0]


def quote(ticker, rng="1mo"):
    """Return a dict with the live price and the LAST COMPLETED SESSION's close.

    Never touches meta.chartPreviousClose. The prior close is read out of the
    close array, and today's own bar is excluded by date, not by position --
    excluding by position (rows[-2]) breaks before the open, when today has no bar.
    """
    d = _fetch(ticker, rng)
    stamps = d["timestamp"]
    closes = d["indicators"]["quote"][0]["close"]
    rows = [(datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d"), c)
            for t, c in zip(stamps, closes) if c is not None]
    if len(rows) < 2:
        raise RuntimeError(f"{ticker}: need >=2 sessions, got {len(rows)}")

    live = d["meta"]["regularMarketPrice"]
    today = datetime.fromtimestamp(
        d["meta"].get("regularMarketTime", stamps[-1]), timezone.utc
    ).strftime("%Y-%m-%d")

    prior = [(dt, c) for dt, c in rows if dt < today]
    if not prior:                      # pre-open: the last bar IS the prior session
        prior = rows[:-1] or rows
    prior_date, prior_close = prior[-1]

    is_yield = ticker.upper() in YIELD_TICKERS
    return {
        "ticker": ticker,
        "live": live,
        "prior_close": prior_close,
        "prior_date": prior_date,
        "chg": live - prior_close,
        "chg_pct": (live - prior_close) / prior_close * 100.0,
        "chg_bp": (live - prior_close) * 100.0 if is_yield else None,
        "is_yield": is_yield,
        "stale_meta": d["meta"].get("chartPreviousClose"),   # kept ONLY to show the trap
    }


def main(tickers):
    print(f"{'ticker':<10}{'live':>11}{'prior close':>13}{'date':>12}"
          f"{'change':>12}{'⚠️ meta':>12}")
    print("-" * 70)
    for t in tickers:
        try:
            q = quote(t)
        except Exception as exc:                       # noqa: BLE001
            print(f"{t:<10}  FAIL  {exc}")
            continue
        move = (f"{q['chg_bp']:+.0f}bp" if q["is_yield"]
                else f"{q['chg_pct']:+.2f}%")
        stale = q["stale_meta"]
        print(f"{t:<10}{q['live']:>11.2f}{q['prior_close']:>13.2f}"
              f"{q['prior_date']:>12}{move:>12}"
              f"{(f'{stale:.2f}' if stale is not None else '-'):>12}")
    print("-" * 70)
    print("  ⚠️ the right-hand column is meta.chartPreviousClose — the value that")
    print("     caused the 2026-08-14 error. It is shown ONLY so the gap is visible.")
    print("     Never compute a change from it.")


if __name__ == "__main__":
    args = sys.argv[1:] or ["^GSPC", "^IXIC", "^RUT", "^VIX", "^FVX", "^TNX", "^TYX"]
    main(args)
