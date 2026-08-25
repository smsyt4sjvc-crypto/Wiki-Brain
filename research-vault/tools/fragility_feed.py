#!/usr/bin/env python3
"""
fragility_feed.py — pulls the credit/debt fragility dashboard series from
FREE, KEYLESS sources and writes them into the vault as CSV + a latest.json.

WHY IT IS BUILT THIS WAY
------------------------
The data is COMMITTED INTO THE REPO as plain CSV/JSON. It is deliberately NOT
fetched by JavaScript in the browser, because a page that fetches client-side
is EMPTY to an agent reading it (WebFetch renders markdown; it does not execute
JS). Baking the numbers into the artifacts at build time is what makes the same
dashboard readable by a person AND by Claude.

SOURCES (all keyless, all verified reachable 2026-08-22)
  fredgraph.csv   — the FRED *API* is key-gated; the public graph CSV is not.
  markets.newyorkfed.org/api  — SOFR, repo ops, primary-dealer positions & fails.
  treasurydirect.gov/TA_WS    — auction results.
  query2.finance.yahoo.com    — ^MOVE (needs a UA header).

KNOWN GAPS — see GAPS at the bottom of latest.json. Do not paper over them.
"""
import csv, io, json, os, re, subprocess, sys, time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "data", "fragility")
SER  = os.path.join(OUT, "series")
# ⚠️ USER-AGENT IS LOAD-BEARING AND THE RULE IS PER-SOURCE.
#   FRED bot-protects on UA: NO User-Agent -> 200 in ~200ms; a custom UA ->
#   HTTP/2 INTERNAL_ERROR; a browser UA -> hangs until timeout. Send NOTHING.
#   Yahoo is the opposite: no UA -> HTTP 429; it needs a browser-ish UA.
#   This is why the vault previously concluded "FRED is blocked from the
#   container." FRED was never blocked. The User-Agent was the block.
UA_BROWSER = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126"

def get(url, tries=4, timeout=45, ua=None):
    """Transport is CURL, not urllib, and that is deliberate.

    In the agent container all egress goes through a local CONNECT proxy;
    urllib times out against it while curl (which honours the proxy env vars
    and the CA bundle) succeeds. --http1.1 is required: FRED over HTTP/2
    through the proxy dies with "stream not closed cleanly" (INTERNAL_ERROR).
    On a GitHub Actions runner there is no proxy
    and curl behaves identically -- so one transport covers both environments.
    """
    last = None
    for i in range(tries):
        try:
            r = subprocess.run(
                ["curl", "-sS", "--fail", "--http1.1", "-m", str(timeout)]
                + (["-A", ua] if ua else []) + [url],
                capture_output=True)
            if r.returncode == 0 and r.stdout:
                return r.stdout
            last = RuntimeError(
                f"curl rc={r.returncode} {r.stderr.decode()[:160].strip()}")
        except Exception as e:
            last = e
        time.sleep(5 * (i + 1) ** 2)   # 5s, 20s, 45s -- Yahoo 429s need real backoff
    raise last


# ---------------------------------------------------------------- fetchers
def fred(series_id, start="2018-01-01"):
    """FRED public graph CSV. Returns [(date, float)] with '.' gaps dropped."""
    raw = get(f"https://fred.stlouisfed.org/graph/fredgraph.csv"
              f"?id={series_id}&cosd={start}").decode()
    rows = list(csv.reader(io.StringIO(raw)))
    if not rows or "observation_date" not in rows[0][0]:
        raise ValueError(f"{series_id}: not a FRED csv")
    out = []
    for d, v in (r for r in rows[1:] if len(r) >= 2):
        try:
            out.append((d, float(v)))
        except ValueError:
            pass                      # FRED writes '.' for missing
    return out

def nyfed_pd(keyid):
    j = json.loads(get(f"https://markets.newyorkfed.org/api/pd/get/{keyid}.json"))
    out = []
    for r in j["pd"]["timeseries"]:
        try:
            out.append((r["asofdate"], float(r["value"])))
        except (TypeError, ValueError):
            pass                      # NY Fed writes null / '*' for suppressed
    return out

def yahoo(symbol):
    j = json.loads(get(f"https://query2.finance.yahoo.com/v8/finance/chart/"
                       f"{symbol}?range=5y&interval=1d", ua=UA_BROWSER))
    res = j["chart"]["result"][0]
    ts  = res["timestamp"]
    cl  = res["indicators"]["quote"][0]["close"]
    return [(datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d"), float(c))
            for t, c in zip(ts, cl) if c is not None]

def treasury_auctions(n=250):
    j = json.loads(get("https://www.treasurydirect.gov/TA_WS/securities/auctioned"
                       f"?format=json&pagesize={n}"))
    keep = []
    for a in j:
        if a.get("securityType") not in ("Note", "Bond"):
            continue
        term = (a.get("securityTerm") or "")
        if not re.match(r"^(9-Year|10-Year|19-Year|20-Year|29-Year|30-Year)", term):
            continue
        def f(k):
            try:    return float(a.get(k) or "")
            except ValueError: return None
        keep.append({
            "date": (a.get("auctionDate") or "")[:10],
            "term": term,
            "cusip": a.get("cusip"),
            "high_yield":  f("highYield"),
            "bid_to_cover": f("bidToCoverRatio"),
            "indirect":  f("indirectBidderAccepted"),
            "direct":    f("directBidderAccepted"),
            "dealer":    f("primaryDealerAccepted"),
            "offering":  f("offeringAmount"),
        })
    keep.sort(key=lambda x: x["date"])
    return keep

def nyfed_repo_ops(n=60):
    j = json.loads(get("https://markets.newyorkfed.org/api/rp/repo/all/results/"
                       f"last/{n}.json"))
    out = []
    for o in j["repo"]["operations"]:
        tot = o.get("totalAmtAccepted")
        if tot is None:
            continue
        out.append((o.get("operationDate", "")[:10], float(tot) / 1e9))
    out.sort()
    return out

# ------------------------------------------------------- derived series
def align(a, b):
    """Inner-join two [(date,val)] series on date."""
    db = dict(b)
    return [(d, va, db[d]) for d, va in a if d in db]

def diff(a, b, scale=1.0):
    return [(d, (va - vb) * scale) for d, va, vb in align(a, b)]

def realized_vol(s, win=20, ann=252):
    """Annualized stdev of DAILY YIELD CHANGES, in basis points.
    A MOVE PROXY, NOT MOVE: MOVE is IMPLIED vol on Treasury options.
    This is REALIZED vol of the cash yield. They diverge exactly when it
    matters most — implied leads. Labelled as a proxy everywhere it appears."""
    out = []
    ch = [(s[i][0], (s[i][1] - s[i-1][1]) * 100.0) for i in range(1, len(s))]
    for i in range(win, len(ch)):
        w = [c for _, c in ch[i-win:i]]
        m = sum(w) / len(w)
        var = sum((x - m) ** 2 for x in w) / (len(w) - 1)
        out.append((ch[i][0], (var ** 0.5) * (ann ** 0.5)))
    return out

# ------------------------------------------------------------ the spec
# stage = position on Jake's transmission chain. This is what the ladder reads.
SPEC = [
    # key,            label,                       stage, panel, kind, arg
    ("ccc_oas",   "CCC & lower OAS",                1, 1, "fred", "BAMLH0A3HYC"),
    ("hy_oas",    "High-yield OAS",                 1, 1, "fred", "BAMLH0A0HYM2"),
    ("ccc_hy_gap","CCC minus HY (quality gap)",     1, 1, "derived", None),
    ("bbb_oas",   "BBB OAS",                        2, 2, "fred", "BAMLC0A4CBBB"),
    ("ig_oas",    "Investment-grade OAS",           2, 2, "fred", "BAMLC0A0CM"),
    ("cp_spread", "A2/P2 minus AA CP, 90d",         3, 8, "derived", None),
    ("rvol10",    "10Y realized vol (MOVE proxy)",  4, 4, "derived", None),
    ("dgs30",     "30Y Treasury yield",             4, 4, "fred", "DGS30"),
    ("sofr_iorb", "SOFR minus IORB",                6, 7, "derived", None),
    ("repo_ops",  "Fed repo ops accepted ($B)",     6, 7, "nyfed_repo", None),
    ("pd_ust",   "Dealer UST net position",        5, 9, "nyfed_pd", "PDPOSGST-TOT"),
    ("repo_fin", "Dealer UST repo financing",      5, 9, "nyfed_pd", "PDSORA-UTSETTOT"),
    ("rev_repo", "Dealer UST reverse repo",        5, 9, "nyfed_pd", "PDSIRRA-UTSETTOT"),
    ("pd_ftd",   "Dealer UST fails to deliver",    5, 9, "nyfed_pd", "PDFTD-USTET"),
    ("pd_ftr",   "Dealer UST fails to receive",    5, 9, "nyfed_pd", "PDFTR-USTET"),
    ("ci_all",   "H.8 C&I loans, all banks",       7, 10, "fred", "TOTCI"),
    ("ci_large", "H.8 C&I loans, LARGE banks",     7, 10, "derived", None),
    ("ci_small", "H.8 C&I loans, SMALL banks",     7, 10, "fred", "CILSCBW027NBOG"),
    ("cre_all",  "H.8 CRE loans, all banks",       7, 10, "fred", "CREACBW027SBOG"),
    ("cre_large","H.8 CRE loans, LARGE banks",     7, 10, "fred", "CRELCBW027SBOG"),
    ("cre_small","H.8 CRE loans, SMALL banks",     7, 10, "fred", "CRESCBW027SBOG"),
    ("dep_large","H.8 deposits, LARGE banks",      7, 10, "fred", "DPSLCBW027SBOG"),
    ("dep_small","H.8 deposits, SMALL banks",      7, 10, "fred", "DPSSCBW027SBOG"),
    ("vix",       "VIX (context, not a stage)",     0, 0, "fred", "VIXCLS"),
]
# indicators where FALLING is the stress direction
INVERTED = {"ci_all", "ci_large", "ci_small", "cre_all", "cre_large",
            "cre_small", "dep_large", "dep_small"}

GAPS = [
    {"chart": 4,  "name": "MOVE index — AGENT-FETCHED, NOT IN THE CRON",
     "why": "Every curl route 429s/403s from a datacentre IP (Yahoo from both "
            "this container AND GitHub runners, CNBC, WSJ; Stooq is JS-gated; "
            "FRED's VXTYN died in May 2020). But WebFetch DOES reach Yahoo's "
            "quote page — it is a different fetcher, not this container's curl. "
            "So MOVE is a LIVE ROW that Claude refreshes in-session via "
            "tools/move_manual.py, and the weekday cron CANNOT refresh it. "
            "Expect it to lag on any day Claude was not asked. The STALE flag "
            "is the honest signal that it did.",
     "status": "LIVE — but agent-refreshed, never cron-refreshed"},
    {"chart": 3,  "name": "CDX IG / CDX HY",
     "why": "Markit/S&P proprietary. No free feed exists. The ICE cash-bond OAS "
            "series (charts 1-2) answer the same question more slowly.",
     "status": "UNOBTAINABLE FREE"},
    {"chart": 6,  "name": "10Y/30Y swap spreads",
     "why": "FRED's DSWP10/DSWP30 were discontinued in 2016 (they return 2000-era "
            "data). Live swap rates are vendor-gated.",
     "status": "UNOBTAINABLE FREE — vault fetch stays open"},
    {"chart": 11, "name": "Single-name 5Y CDS — CLOSED 2026-08-22",
     "why": "SOLVED via ICE Clear Credit's free daily settlement prices "
            "(tools/icc_cds.py). All 12 AI-complex names clear, CoreWeave "
            "included. Two remaining limits, both real: the published number is "
            "a points-upfront PRICE that must be MODELLED into a spread, and ICE "
            "serves only one clearing date — history is licensed, so the vault "
            "accumulates forward from 2026-08-22 and cannot percentile-score "
            "these rows for years.",
     "status": "CLOSED — levels only, no baseline yet"},
]

def main():
    os.makedirs(SER, exist_ok=True)
    data, errors = {}, []

    for key, label, stage, panel, kind, arg in SPEC:
        if kind == "derived":
            continue
        try:
            if   kind == "fred":       s = fred(arg)
            elif kind == "yahoo":      s = yahoo(arg)
            elif kind == "nyfed_pd":   s = nyfed_pd(arg)
            elif kind == "nyfed_repo": s = nyfed_repo_ops()
            else: continue
            if not s:
                raise ValueError("empty series")
            data[key] = s
            print(f"  ok   {key:<12} {len(s):>5} pts  last {s[-1][0]} = {s[-1][1]:,.4g}")
        except Exception as e:
            errors.append({"key": key, "error": f"{type(e).__name__}: {e}"})
            print(f"  FAIL {key:<12} {type(e).__name__}: {e}", file=sys.stderr)

    # derived — each guarded so one missing input does not kill the run
    try: data["ccc_hy_gap"] = diff(data["ccc_oas"], data["hy_oas"])
    except Exception as e: errors.append({"key": "ccc_hy_gap", "error": str(e)})
    try:
        a2p2 = fred("RIFSPPNA2P2D90NB"); aa = fred("RIFSPPNAAD90NB")
        data["cp_spread"] = diff(a2p2, aa, 100.0)          # pct -> bp
    except Exception as e: errors.append({"key": "cp_spread", "error": str(e)})
    try:
        sofr = fred("SOFR"); iorb = fred("IORB")
        data["sofr_iorb"] = diff(sofr, iorb, 100.0)        # pct -> bp
    except Exception as e: errors.append({"key": "sofr_iorb", "error": str(e)})
    try:
        # ⚠️ CILDCBW027NBOG is DOMESTICALLY CHARTERED (all sizes), NOT "large" --
        # the arithmetic proves it: domestic 2,306 vs small 735 vs all-banks
        # 2,933. Large domestic is unpublished, so it is DERIVED as domestic
        # minus small. Both legs are NSA on purpose: the seasonally-adjusted
        # small-bank series was discontinued in 2018, and differencing an SA
        # series against an NSA one would be an instrument mismatch.
        dom = fred("CILDCBW027NBOG"); sml = fred("CILSCBW027NBOG")
        data["ci_large"] = [(d, a - b) for d, a, b in align(dom, sml)]
    except Exception as e: errors.append({"key": "ci_large", "error": str(e)})
    try: data["rvol10"] = realized_vol(fred("DGS10"))
    except Exception as e: errors.append({"key": "rvol10", "error": str(e)})

    # MERGE, never replace. A 429 on one source must not erase that series'
    # history, and daily merging accumulates history past any API's window.
    for k, s in data.items():
        path = os.path.join(SER, f"{k}.csv")
        merged = {}
        if os.path.exists(path):
            with open(path) as fh:
                for row in csv.DictReader(fh):
                    try: merged[row["date"]] = round(float(row["value"]), 6)
                    except (ValueError, KeyError, TypeError): pass
        before = len(merged)
        # ⚠️ ROUND ON WRITE. Derived series (realized vol) are computed, not
        # fetched, and a different CPU/Python build lands 1 ulp away: the runner
        # writes 53.1512241776136 where this container writes 53.15122417761359.
        # Same number to any meaning we care about -- but repr() differs, so git
        # sees ~1,450 changed lines every time the machine alternates, and the
        # real changes drown in it. 6 decimals is far past any series' precision
        # here and makes a diff mean something again.
        merged.update({d: round(v, 6) for d, v in s})   # today's pull wins
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["date", "value"])
            w.writerows(sorted(merged.items()))
        if len(merged) > before and before:
            print(f"       {k}: +{len(merged)-before} new rows (now {len(merged)})")

    auctions = []
    try:
        auctions = treasury_auctions()
        with open(os.path.join(OUT, "auctions.json"), "w") as fh:
            json.dump(auctions, fh, indent=1)
        print(f"  ok   auctions     {len(auctions)} long-end results")
    except Exception as e:
        errors.append({"key": "auctions", "error": str(e)})
        print(f"  FAIL auctions    {e}", file=sys.stderr)

    meta = {k: {"label": l, "stage": st, "panel": p}
            for k, l, st, p, _, _ in SPEC}
    with open(os.path.join(OUT, "raw_meta.json"), "w") as fh:
        json.dump({"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "meta": meta, "inverted": sorted(INVERTED),
                   "errors": errors, "gaps": GAPS,
                   "auction_count": len(auctions)}, fh, indent=1)
    print(f"\n  {len(data)} series -> {SER}")
    if errors:
        print(f"  {len(errors)} FAILED: {[e['key'] for e in errors]}", file=sys.stderr)

if __name__ == "__main__":
    main()
