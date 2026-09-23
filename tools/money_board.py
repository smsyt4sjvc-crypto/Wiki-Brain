#!/usr/bin/env python3
"""
money_board.py — "WHERE'S THE MONEY" (rule 16d, adopted 2026-09-23, Jake's spec).

Every data input drops a weighted mark in one of three columns (bear / flat / bull)
for EVERY name it implicates, any sector. Marks live in data/money/marks.csv and
expire after 120 days. This script tallies them, computes each name's 60-session beta
to the driver of its heaviest marks, and ranks by  score = (bull - bear) x |sensitivity|, where sensitivity = the name's
% move on a 1-sigma day of its driver (beta x driver sigma).
The top 5 by |score| (longs AND shorts) is the daily "where's the money" list.

Weights (evidence ladder): 2 = MEASURED (auction, filing, print) · 1 = confirmed
event · 0.5 = REPORTED / talks-stage. A lagged echo of an already-marked shock
gets the lower weight (anti-double-count).

Drivers (ETF proxies): TLT = rates (10Y) · BNO = Brent · BWET = tanker freight · SOXX = semis
· SPY = market. ⚠️ Tankers trade on FREIGHT, not crude: vs BNO corr ~0.1, vs BWET 0.3-0.6
(found on the first run, 9/23) — pick the driver the name actually trades on.
Prices: Nasdaq historical API (works from the container; Yahoo is rate-limited).

Usage:
    python3 tools/money_board.py                 # tally + betas + top 5, as of today
    python3 tools/money_board.py --asof 2026-09-23 --top 5
    python3 tools/money_board.py --no-beta       # tally only, no network
"""
import argparse, csv, json, math, os, sys, urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKS = os.path.join(ROOT, "data", "money", "marks.csv")
EXPIRY_DAYS, MOMENTUM_DAYS, BETA_N = 120, 7, 60
ETFS = {"TLT", "BNO", "SOXX", "SPY", "BWET", "KRE", "IWM", "XLU", "XRT", "USO", "GLD"}
UA = {"User-Agent": "Mozilla/5.0"}


def load_marks(asof):
    out = []
    with open(MARKS) as fh:
        for r in csv.DictReader(fh):
            d = datetime.strptime(r["date"], "%Y-%m-%d").date()
            if d <= asof and (asof - d).days < EXPIRY_DAYS:
                r["_d"], r["weight"] = d, float(r["weight"])
                out.append(r)
    return out


def closes(tk):
    ac = "etf" if tk in ETFS else "stocks"
    frm = (date.today() - timedelta(days=130)).isoformat()
    url = (f"https://api.nasdaq.com/api/quote/{tk}/historical?assetclass={ac}"
           f"&fromdate={frm}&limit=200")
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as fh:
        rows = json.load(fh)["data"]["tradesTable"]["rows"]
    px = {}
    for r in rows:
        d = datetime.strptime(r["date"], "%m/%d/%Y").date()
        px[d] = float(r["close"].replace("$", "").replace(",", ""))
    return px


def beta(a, b):
    ds = sorted(set(a) & set(b))[-(BETA_N + 1):]
    ra = [a[ds[i]] / a[ds[i - 1]] - 1 for i in range(1, len(ds))]
    rb = [b[ds[i]] / b[ds[i - 1]] - 1 for i in range(1, len(ds))]
    if len(ra) < 20:
        return None
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra)
    vb = sum((y - mb) ** 2 for y in rb)
    if not va or not vb:
        return None
    # SENSITIVITY = beta x sigma(driver) = the name's % move on a 1-sigma driver day.
    # Raw beta is NOT comparable across drivers (TLT's low variance inflates every
    # volatile name's beta to it — found on the first run, 9/23). corr is returned
    # so a weak relationship is visible instead of hiding inside a big beta.
    b = cov / vb
    sd_b = math.sqrt(vb / (len(rb) - 1))
    return {"beta": b, "sens": 100 * b * sd_b, "corr": cov / math.sqrt(va * vb)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default=date.today().isoformat())
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--no-beta", action="store_true")
    ap.add_argument("--book", action="store_true", help="score the registered book(s) in data/money/book.csv")
    a = ap.parse_args()
    asof = datetime.strptime(a.asof, "%Y-%m-%d").date()
    if a.book:
        return score_book()
    marks = load_marks(asof)

    tal = defaultdict(lambda: {"bull": 0.0, "flat": 0.0, "bear": 0.0, "mom": 0.0,
                               "drv": defaultdict(float), "n": 0})
    for m in marks:
        t = tal[m["ticker"]]
        t[m["col"]] += m["weight"]
        t["n"] += 1
        t["drv"][m["driver"]] += m["weight"]
        if (asof - m["_d"]).days < MOMENTUM_DAYS:
            t["mom"] += {"bull": 1, "bear": -1}.get(m["col"], 0) * m["weight"]

    cache = {}
    def px(tk):
        if tk not in cache:
            try:
                cache[tk] = closes(tk)
            except Exception as e:
                cache[tk] = None
                print(f"  ⚠️ no prices for {tk}: {e}", file=sys.stderr)
        return cache[tk]

    rows = []
    for tk, t in tal.items():
        tot = t["bull"] + t["flat"] + t["bear"]
        net = t["bull"] - t["bear"]
        drv = max(t["drv"], key=t["drv"].get)
        b = None
        if not a.no_beta:
            p, q = px(tk), px(drv)
            if p and q:
                b = beta(p, q)
        score = net * abs(b["sens"]) if b else None
        rows.append((tk, t, tot, net, net / tot if tot else 0, drv, b, score))

    print(f"WHERE'S THE MONEY — as of {asof} · {len(marks)} live marks · {len(rows)} names\n")
    print(f"{'name':6} {'bear':>5} {'flat':>5} {'bull':>5} {'net':>5} {'skew':>6} {'5d':>5}"
          f" {'drv':>5} {'sens%':>6} {'corr':>5} {'score':>6}")
    key = lambda r: -(abs(r[7]) if r[7] is not None else abs(r[3]) * 0.001)
    for tk, t, tot, net, sk, drv, b, sc in sorted(rows, key=key):
        bs = f"{b['sens']:6.2f} {b['corr']:+5.2f}" if b else "   n/a   n/a"
        ss = f"{sc:6.2f}" if sc is not None else "   n/a"
        print(f"{tk:6} {t['bear']:5.1f} {t['flat']:5.1f} {t['bull']:5.1f} {net:+5.1f}"
              f" {sk:+6.2f} {t['mom']:+5.1f} {drv:>5} {bs} {ss}")
    ranked = [r for r in sorted(rows, key=key) if r[7] is not None and r[3] != 0][:a.top]
    print(f"\n💰 TOP {a.top} (score = net marks × |% move per 1σ driver day|; ⚠️ |corr|<0.2 = weak link):")
    for i, (tk, t, tot, net, sk, drv, b, sc) in enumerate(ranked, 1):
        side = "BULL" if net > 0 else "BEAR"
        flag = "  ⚠️ weak link" if abs(b["corr"]) < 0.2 else ""
        print(f"  {i}. {tk:6} {side}  net {net:+.1f}  {b['sens']:+.2f}%/1σ {drv} (corr {b['corr']:+.2f})  score {sc:+.2f}{flag}")


def last_close(tk):
    ac = "etf" if tk in ETFS else "stocks"
    url = f"https://api.nasdaq.com/api/quote/{tk}/info?assetclass={ac}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as fh:
        d = json.load(fh)["data"]
    s = d.get("secondaryData") or d["primaryData"]   # secondaryData = REGULAR-session close after hours
    return float(s["lastSalePrice"].replace("$", "").replace(",", ""))


def score_book():
    """Score each open position vs its registered stop / T1 / T2 (closing basis).
    Event exits are NOT automatic — they are printed so the close review checks them."""
    path = os.path.join(ROOT, "data", "money", "book.csv")
    print("REGISTERED BOOK — stop = one weekly sigma (closing basis) · half off at T1, then stop to breakeven\n")
    for r in csv.DictReader(open(path)):
        if r["status"] != "open":
            continue
        e, st, t1, t2 = (float(r[k]) for k in ("entry", "stop", "t1", "t2"))
        try:
            px = last_close(r["ticker"])
        except Exception as ex:
            print(f"  {r['ticker']:5} ⚠️ no quote: {ex}"); continue
        sgn = 1 if r["side"] == "long" else -1
        pnl = sgn * (px / e - 1) * 100
        hit = ("STOPPED" if sgn * (px - st) <= 0 else "T2 ✔" if sgn * (px - t2) >= 0
               else "T1 ✔ (stop→BE)" if sgn * (px - t1) >= 0 else "live")
        print(f"  {r['ticker']:5} {r['side']:5} entry {e:>9.2f}  now {px:>9.2f}  {pnl:+6.2f}%  "
              f"stop {st} · T1 {t1} · T2 {t2}  [{hit}]\n        event exit: {r['event_exit']}")


if __name__ == "__main__":
    main()
