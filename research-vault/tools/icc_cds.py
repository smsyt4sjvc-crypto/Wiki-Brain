#!/usr/bin/env python3
"""
icc_cds.py -- ICE Clear Credit daily 5Y single-name CDS settlement prices.

THE SOURCE (Jake's lead, 2026-08-22). ICE publishes end-of-day cleared settlement
levels free to the public. The page renders client-side, but a probe on a GitHub
runner caught the request it makes, and that endpoint is a plain keyless JSON GET
that works from anywhere:

    https://www.ice.com/api/cds-settlement-prices/icc-single-names

This closes the vault's single most valuable gap. Single-name CDS is where
AI-complex stress appears FIRST, and it had no other free source -- every prior
mark came from Jake pasting a chart.

⛔⛔ THE CATCH THAT MATTERS MOST: `eodPrice` IS A PRICE, NOT A SPREAD.
These are standardised-coupon contracts quoted points-upfront. A price ABOVE 100
means the fair spread is BELOW the fixed coupon. Reading 99.07 as "99bp" would be
error class 5 (instrument mismatch) and would be wrong by an order of magnitude.
We convert, and the conversion is a MODEL -- see convert() for its assumptions.

⚠️ NO HISTORY. The endpoint returns ONE clearing date. History cannot be
backfilled at any price (ICE licenses it), so the vault accumulates forward from
2026-08-22. Percentile scoring against a 3-year window is therefore IMPOSSIBLE
for these rows for years. They are reported as LEVELS with an explicit "no
baseline" marker -- never faked into a percentile.

⚠️ THE MATURITY ROLLS. Today every contract reads 2031-06-20. On the IMM roll
(Mar 20 / Sep 20) the on-the-run 5Y jumps to the next maturity and the price
series discontinues for reasons that are not credit. Next roll: ~2026-09-20.
The stored maturity column is what makes that detectable -- do not drop it.
"""
import csv, json, math, os, subprocess, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "data", "fragility")
URL  = "https://www.ice.com/api/cds-settlement-prices/icc-single-names"

# ICE's own names, which are neither tickers nor tidy. "Oracle Cop" is ICE's
# typo, not ours. Matching on these exact strings is deliberate: a fuzzy match
# would silently pick up a different issuer after any ICE rename.
NAMES = {
    "BROINC":  ("AVGO",  "Broadcom"),
    "NVIDIA":  ("NVDA",  "Nvidia"),
    "ORCLE":   ("ORCL",  "Oracle"),
    "METAPL":  ("META",  "Meta Platforms"),
    "ALPHINC": ("GOOGL", "Alphabet"),
    "AMZN":    ("AMZN",  "Amazon"),
    "MSFT":    ("MSFT",  "Microsoft"),
    "COREWEI": ("CRWV",  "CoreWeave"),
    "AMD":     ("AMD",   "Advanced Micro Devices"),
    "INTC":    ("INTC",  "Intel"),
    "DELLN":   ("DELL",  "Dell"),
    "TESLINC": ("TSLA",  "Tesla"),
}

RECOVERY = 0.40      # ISDA standard for senior unsecured corporates
RISK_FREE = 0.040    # flat. See the honest-bounds note in convert().


def get(url, tries=3, timeout=60):
    """curl, no User-Agent -- same transport rule as fragility_feed.py."""
    last = None
    for i in range(tries):
        try:
            r = subprocess.run(["curl", "-sS", "--fail", "--http1.1",
                                "-m", str(timeout), url], capture_output=True)
            if r.returncode == 0 and r.stdout:
                return r.stdout
            last = RuntimeError(f"curl rc={r.returncode} {r.stderr.decode()[:160]}")
        except Exception as e:
            last = e
        time.sleep(3 * (i + 1))
    raise last


def rpv01(spread, T, recovery=RECOVERY, r=RISK_FREE, freq=4):
    """Risky annuity under a flat hazard rate implied by the spread itself."""
    h = spread / (1.0 - recovery)
    n = max(1, int(round(T * freq)))
    dt = 1.0 / freq
    return sum(dt * math.exp(-r * (i * dt)) * math.exp(-h * (i * dt))
               for i in range(1, n + 1))


def convert(price, coupon, T):
    """Points-upfront -> par spread, in basis points.

    upfront_fraction = (100 - price)/100 = (spread - coupon) * RPV01(spread)
    Solved by fixed-point iteration; RPV01 depends on the spread being solved
    for, so it converges rather than closes.

    ⚠️ THIS IS A MODEL, NOT A QUOTE. It assumes a flat hazard rate, 40% recovery,
    a flat 4.0% risk-free curve, and quarterly premiums. Real ISDA pricing uses
    the live swap curve and the actual accrual schedule. Cross-checked against
    seven independently-sourced vault marks and lands within a few bp -- good
    enough to TRACK, not to quote as a dealer level.
    """
    uf = (100.0 - price) / 100.0
    s = coupon                                  # seed at the fixed coupon
    for _ in range(60):
        a = rpv01(s, T)
        new = coupon + uf / a
        if new <= 1e-6:                         # keep the hazard rate sane
            new = 1e-6
        if abs(new - s) < 1e-9:
            s = new
            break
        s = new
    return s * 1e4


def year_frac(clearing_date, maturity):
    from datetime import date
    y1, m1, d1 = map(int, clearing_date.split("-"))
    y2, m2, d2 = map(int, maturity.split("-"))
    return max(0.25, (date(y2, m2, d2) - date(y1, m1, d1)).days / 365.25)


def main():
    rows = json.loads(get(URL))
    out = []
    for r in rows:
        parts = r["instrumentName"].split(".")
        if len(parts) < 6:
            continue
        tkr, tier, ccy, doc, cpn, mat = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
        if tkr not in NAMES or ccy != "USD" or tier != "SNRFOR":
            continue
        price = float(r["eodPrice"])
        coupon = int(cpn) / 1e4
        T = year_frac(r["clearingDate"], mat)
        out.append({
            "date": r["clearingDate"], "ticker": NAMES[tkr][0], "issuer": NAMES[tkr][1],
            "ice_name": r["name"], "instrument": r["instrumentName"],
            "coupon_bp": int(cpn), "maturity": mat, "price": price,
            "spread_bp": round(convert(price, coupon, T), 1),
        })

    # One contract per issuer: the 100bp (IG convention) unless the name only
    # clears at 500bp, which is itself a signal -- ICE treats it as high yield.
    best = {}
    for r in out:
        k = r["ticker"]
        if k not in best or r["coupon_bp"] < best[k]["coupon_bp"]:
            best[k] = r
    panel = sorted(best.values(), key=lambda x: -x["spread_bp"])

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, "cds_panel.csv")
    cols = ["date", "ticker", "issuer", "coupon_bp", "maturity", "price", "spread_bp"]
    seen = set()
    if os.path.exists(path):
        with open(path) as fh:
            for row in csv.DictReader(fh):
                seen.add((row["date"], row["ticker"]))
    new = [r for r in panel if (r["date"], r["ticker"]) not in seen]
    with open(path, "a" if seen else "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        if not seen:
            w.writeheader()
        w.writerows(new)

    med = sorted(r["spread_bp"] for r in panel)
    med = med[len(med) // 2] if len(med) % 2 else (med[len(med)//2 - 1] + med[len(med)//2]) / 2
    print(f"ICE Clear Credit, clearing date {panel[0]['date']} -- {len(panel)} names, "
          f"{len(new)} new rows appended\n")
    print(f"  {'ticker':<7}{'issuer':<24}{'cpn':>5}{'price':>10}{'spread':>9}")
    print("  " + "-" * 54)
    for r in panel:
        flag = "  <- HY convention (no 100bp contract)" if r["coupon_bp"] == 500 else ""
        print(f"  {r['ticker']:<7}{r['issuer']:<24}{r['coupon_bp']:>5}"
              f"{r['price']:>10.4f}{r['spread_bp']:>9.1f}{flag}")
    print(f"\n  MEDIAN SPREAD: {med:.1f}bp   ·   maturity {panel[0]['maturity']} "
          f"(rolls on the next IMM date)")


if __name__ == "__main__":
    main()
