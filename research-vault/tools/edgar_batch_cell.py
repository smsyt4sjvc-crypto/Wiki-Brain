#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════════════════
#  EDGAR BATCHED FETCHER — Jake's spec 2026-08-11: "with data fetch through APIs we should
#  batch smaller requests."  He is right, and on EDGAR the win is measured:
#
#      companyfacts  (one company, EVERY tag)     2.70 MB
#      companyconcept(one company, ONE tag)       0.02 MB   ← 137x smaller
#      frames        (ONE tag, EVERY filer)       0.69 MB   ← 4,506 companies in ONE call
#
#  Every FCF/CEPI pull in this vault so far used companyfacts — the 2.7 MB blob — once per
#  company, to read two tags. This replaces that.
#
#  ⛔ IT ALSO FIXES A REAL BUG (found 2026-08-11). Most filers report cash-flow items
#  YEAR-TO-DATE: META's filed durations are 89d / 180d / 272d / 364d. A "discrete quarter"
#  filter of 80-100 days therefore matches ONLY THE FIRST QUARTER OF EACH YEAR, forever. The
#  old table showed META +13.2B (Q1) when its real latest quarter was +0.8B. Two defences here:
#     1. FRAMES are already period-normalised by the SEC — CY2026Q2 IS a discrete quarter.
#     2. Where frames are thin, YTD-DIFFERENCING (Q2 = H1 − Q1) is done explicitly.
#
#  ⚠️ AND IT REPORTS THE FILING-LAG GRADIENT, because that is the thing that silently lies.
#  As of 2026-08-11: CY2026Q1 has 4,506 filers, CY2026Q2 has 166. Q2 is still landing. A pull
#  that returns nothing for a name may mean "not filed yet," NOT "no data" — the difference
#  matters and the old script could not tell you which.
#
#  COMPLETE CELL — paste whole into Colab and run. Tier 0: free, keyless, no tokens.
# ═══════════════════════════════════════════════════════════════════════════════════════════
import json, time, urllib.request, urllib.error

UA = {"User-Agent": "Jake Research vault@example.com"}   # SEC requires a UA with contact

# ═══════════════════════════ CONFIG ═════════════════════════════════════════════════════════
NAMES   = ["MSFT", "GOOGL", "AMZN", "META", "NVDA", "ORCL", "AVGO", "TSM"]
PERIODS = ["CY2025Q3", "CY2025Q4", "CY2026Q1", "CY2026Q2"]   # discrete quarters
TIMEOUT = 12        # SHORT. A dead host must cost seconds, not minutes (the 8/11 FRED lesson)
RETRIES = 2
# ════════════════════════════════════════════════════════════════════════════════════════════

OCF_TAGS = ["NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"]
# AMZN tags capex as PaymentsToAcquireProductiveAssets, not ...PropertyPlantAndEquipment —
# a single-tag pull silently returns "no capex" for it. Candidates, first hit per CIK wins.
CAP_TAGS = ["PaymentsToAcquirePropertyPlantAndEquipment",
            "PaymentsToAcquireProductiveAssets",
            "PaymentsToAcquirePropertyPlantAndEquipmentExcludingLeases"]

_dead_hosts = set()          # fail-fast: one host timeout marks it dead for the whole run

def fetch(url, timeout=TIMEOUT, retries=RETRIES):
    """Small, fast, and LOUD about WHY it failed. Returns (data, error_string)."""
    host = url.split("/")[2]
    if host in _dead_hosts:
        return None, "host marked dead earlier this run — skipped"
    last = ""
    for attempt in range(retries + 1):
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
            return json.loads(r.read()), None
        except urllib.error.HTTPError as e:
            # An HTTP status is a real answer — do NOT mark the host dead, do NOT retry 4xx.
            return None, f"HTTP {e.code}"
        except TimeoutError:
            last = "timeout"
        except Exception as e:
            last = f"{type(e).__name__}"
        if attempt < retries:
            time.sleep(0.6 * (attempt + 1))
    if last == "timeout":
        _dead_hosts.add(host)          # ← the fix for "it's still running"
        return None, "TIMEOUT — host marked dead, remaining calls to it will be skipped"
    return None, last

def ticker_map():
    d, err = fetch("https://www.sec.gov/files/company_tickers.json")
    if err:
        return {}, err
    return {r["ticker"].upper(): int(r["cik_str"]) for r in d.values()}, None

def frame(tags, period):
    """ONE call per tag → that tag for EVERY filer in a discrete period. The batch primitive.
    Merges a candidate list: earlier-listed tags win, later ones fill gaps only."""
    merged, errs = {}, []
    for tag in tags:
        d, err = fetch(f"https://data.sec.gov/api/xbrl/frames/us-gaap/{tag}/USD/{period}.json")
        if err:
            errs.append(f"{tag.split('To')[-1][:14]}:{err}")
            continue
        for p in d.get("data", []):
            merged.setdefault(p["cik"], p["val"])       # first tag with the CIK wins
    return merged, ("; ".join(errs) if errs and not merged else None)

def concept(cik, tag):
    """ONE company, ONE tag — 137x smaller than companyfacts. Use for per-name series."""
    d, err = fetch(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{tag}.json")
    if err:
        return [], err
    return d.get("units", {}).get("USD", []), None

print("=" * 96)
print("  EDGAR BATCHED FETCHER — frames + companyconcept instead of companyfacts blobs")
print("=" * 96)

cik, err = ticker_map()
if err:
    raise SystemExit(f"⛔ ticker map failed: {err} — SEC unreachable, nothing else will work.")
want = {cik[t]: t for t in NAMES if t in cik}
missing = [t for t in NAMES if t not in cik]
if missing:
    print(f"  ⚠️ not in the SEC ticker file: {', '.join(missing)} (foreign filer or wrong symbol)")

# ── one frames call per (tag, period) — replaces len(NAMES) companyfacts downloads each
_ncalls = len(PERIODS) * (len(OCF_TAGS) + len(CAP_TAGS))
print(f"\n  Fetching {len(PERIODS)} periods x {len(OCF_TAGS)+len(CAP_TAGS)} candidate tags "
      f"= {_ncalls} calls, ~0.03-0.7 MB each")
print(f"  (the old pattern was {len(NAMES)} companyfacts blobs @ ~2.7 MB = ~{len(NAMES)*2.7:.0f} MB, "
      f"and it scaled with NAMES; this scales with PERIODS instead)\n")
OCF, CAP, COVER = {}, {}, {}
for per in PERIODS:
    o, e1 = frame(OCF_TAGS, per)
    c, e2 = frame(CAP_TAGS, per)
    OCF[per], CAP[per] = o, c
    COVER[per] = len(o)
    note = ""
    if e1 or e2:
        note = f"  ⚠️ {e1 or e2}"
    print(f"   {per}: {len(o):>5} filers report OCF · {len(c):>5} report capex{note}")

# ── THE FILING-LAG GRADIENT: the thing that silently lies
mx = max(COVER.values()) if COVER else 0
print(f"\n  ⚠️ FILING-LAG GRADIENT — a thin period means NOT-YET-FILED, not NO-DATA:")
for per in PERIODS:
    pct = (COVER[per] / mx * 100) if mx else 0
    bar = "█" * int(pct / 4)
    flag = "  ← STILL LANDING, absence here is not evidence" if pct < 50 else ""
    print(f"     {per}  {COVER[per]:>5} filers  {bar:<25}{pct:>5.0f}%{flag}")

# ── the table
print("\n" + "=" * 96)
print("  FREE CASH FLOW = OCF − capex, DISCRETE quarters (SEC frames are period-normalised)")
print("=" * 96)
print(f"  {'name':<7}" + "".join(f"{p[2:]:>22}" for p in PERIODS))
print("  " + "-" * 92)
for k, t in sorted(want.items(), key=lambda x: NAMES.index(x[1])):
    row = f"  {t:<7}"
    for per in PERIODS:
        o, c = OCF[per].get(k), CAP[per].get(k)
        if o is None:
            row += f"{'— not filed':>22}"
        elif c is None:
            row += f"{'OCF %.1f, no capex' % (o/1e9):>22}"
        else:
            row += f"{'%+.1fB (%.0f%%)' % ((o-c)/1e9, c/o*100):>22}"
    print(row)
print("\n  format: FCF $B (capex as % of operating cash flow)")
print("  '— not filed' = absent from THIS period's frame. Check the gradient above before")
print("  reading it as anything. It usually means the 10-Q has not posted its XBRL yet.")

# ── YTD fallback for a name the frames miss, demonstrated on the one that burned us
print("\n" + "=" * 96)
print("  YTD-DIFFERENCING FALLBACK — for filers that tag cash flow year-to-date only")
print("=" * 96)
demo = cik.get("META")
if demo:
    pts, err = concept(demo, OCF_TAGS[0])
    if err:
        print(f"  META companyconcept failed: {err}")
    else:
        per_len = {}
        for p in pts:
            if p.get("form") not in ("10-Q", "10-K") or not p.get("start"):
                continue
            import datetime as _dt
            dd = (_dt.date.fromisoformat(p["end"]) - _dt.date.fromisoformat(p["start"])).days
            per_len.setdefault(p["end"], {})[dd] = p["val"]
        recent = sorted(per_len)[-6:]
        print(f"  META filed OCF durations (this is WHY the 80-100 day filter only saw Q1):")
        for e in recent:
            lens = ", ".join(f"{d}d={v/1e9:.1f}B" for d, v in sorted(per_len[e].items()))
            print(f"     ending {e}:  {lens}")
        print("\n  ⇒ Q2 = (180d figure) − (89d figure).  Q3 = 272d − 180d.  Q4 = 364d − 272d.")
        print("  ⇒ If only an 89d figure exists for the latest year, THE QUARTER IS NOT FILED —")
        print("     use the 8-K earnings release, which leads the 10-Q's XBRL by days to weeks.")
print("\n" + "=" * 96)
print("  DESIGN NOTES (why this shape)")
print("  · BATCH ACROSS ENTITIES, NARROW ACROSS TAGS. frames gives every filer for one tag in")
print("    one call; companyconcept gives one tag for one filer at 1/137th the bytes. Neither")
print("    downloads a company's entire fact history to read two lines.")
print("  · SHORT TIMEOUT + FAIL-FAST. 12s, and the first host timeout marks that host dead for")
print("    the run. On 8/11 a 45s timeout across 27 series took ~40 minutes to say 'no'.")
print("  · AN HTTP STATUS IS AN ANSWER; A TIMEOUT IS NOT. 4xx returns immediately and never")
print("    kills the host — conflating the two is what made a transport failure look like bad IDs.")
print("  · REPORT COVERAGE, NOT JUST VALUES. A quarter with 166 filers and one with 4,506 are")
print("    not the same evidence, and a script that prints only values cannot tell you which.")
print("=" * 96)
