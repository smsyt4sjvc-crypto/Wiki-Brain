#!/usr/bin/env python3
"""
curve_exposure.py — WHERE ON THE CURVE DOES EACH AI BORROWER NEED MONEY NEXT (Jake, 2026-09-23).

⭐ THE POINT: a company's EXISTING fixed-rate bonds do not cost it more when yields rise — the rate is
locked. The pain lands where it must borrow NEXT: debt maturing soon (refinancing), planned new deals,
and floating-rate loans (reprice at once). So an auction result should mark the names whose NEXT money
sits at that tenor — a 5Y/7Y tail hits CoreWeave's refinancing; it barely touches Meta.

⚠️ YELLOW FLAG (Jake's addition): BACKSTOP STRUCTURES — debt the name does not owe, but guarantees,
backstops or underwrites via an RVG (Google → TeraWulf's 7.75% 2030 notes; Meta → Beignet; Oracle →
Jupiter's floating loans; NVIDIA → neocloud capacity). "Not their debt per se, and maybe never will be,
but scrutinized as if it is to a degree" — and it is typically SHORTER, HIGHER-YIELD paper than the
backstopper's own bonds. It marks at half weight.

Buckets: FRONT = due within 2 years (+ floating) · BELLY = years 3-5 · LONG = after year 5.
Auction → bucket: 2Y/3Y → FRONT · 5Y/7Y → BELLY · 10Y → LONG (BELLY secondary) · 20Y/30Y → LONG.
Source: SEC XBRL debt-maturity tags (companyconcept API, free) + data/money/curve_overlays.csv.

Usage:
    python3 tools/curve_exposure.py                          # the exposure table
    python3 tools/curve_exposure.py --auction 7Y --tail 1.8  # proposed money-board marks (tail > 0.5bp = BEAR)
    python3 tools/curve_exposure.py --auction 7Y --tail -1.0 # stop-through (< -0.5bp) = BULL
    ... --write                                             # append the proposed marks to data/money/marks.csv
"""
import argparse, csv, json, os, sys, urllib.request
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVER = os.path.join(ROOT, "data", "money", "curve_overlays.csv")
MARKS = os.path.join(ROOT, "data", "money", "marks.csv")
UA = {"User-Agent": "research-vault 7bm4q6x5sm@privaterelay.appleid.com"}
ISSUERS = {"ORCL": 1341439, "META": 1326801, "CRWV": 1769628, "MSFT": 789019, "GOOGL": 1652044,
           "AMZN": 1018724, "NVDA": 1045810, "AVGO": 1730168, "TSLA": 1318605, "DELL": 1571996,
           "AMD": 2488, "INTC": 50863, "WULF": 1083301, "CIFR": 1819989}
P = "LongTermDebtMaturitiesRepaymentsOfPrincipal"
TAGS = [("y1", P + "InNextTwelveMonths"), ("y2", P + "InYearTwo"), ("y3", P + "InYearThree"),
        ("y4", P + "InYearFour"), ("y5", P + "InYearFive"), ("after5", P + "AfterYearFive")]
AUCTION = {"2Y": ("FRONT", None), "3Y": ("FRONT", None), "5Y": ("BELLY", "FRONT"),
           "7Y": ("BELLY", None), "10Y": ("LONG", "BELLY"), "20Y": ("LONG", None), "30Y": ("LONG", None)}


def series(cik, tag):
    url = f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{tag}.json"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=25) as fh:
            u = json.load(fh)["units"]["USD"]
        out = {}
        for z in sorted(u, key=lambda z: z.get("filed", "")):
            out[z["end"]] = z["val"] / 1e9          # last-filed value per period end wins
        return out
    except Exception:
        return {}


def mktcap(tk):
    url = f"https://api.nasdaq.com/api/quote/{tk}/summary?assetclass=stocks"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=25) as fh:
            return float(json.load(fh)["data"]["summaryData"]["MarketCap"]["value"].replace(",", "")) / 1e9
    except Exception:
        return None


# ⭐ v2 (same night): maturities due inside 2 years must be REFINANCED — and a borrower refinances at the
# tenor it normally ISSUES at, not the tenor it is maturing from. Fortress IG issues long (10-30y);
# crossover issues belly+long; high-yield issues belly (5-7y). Beyond-2-year maturities are shown but do
# not mark (outside the 120-day window). Floating debt reprices off SHORT rates (FRONT) immediately.
ISSUE = {"MSFT": "LONG", "GOOGL": "LONG", "AMZN": "LONG", "META": "LONG", "NVDA": "LONG", "AVGO": "LONG",
         "AMD": "BELLY+LONG", "ORCL": "BELLY+LONG", "DELL": "BELLY+LONG", "INTC": "BELLY+LONG",
         "TSLA": "BELLY", "CRWV": "BELLY", "WULF": "BELLY", "CIFR": "BELLY"}


def profile(tk, cik):
    S = {k: series(cik, tag) for k, tag in TAGS}
    if not S["y1"]:
        return {"tk": tk, "tot": 0}
    end = max(S["y1"])                              # as-of = latest period with a next-12-month figure
    v, mixed = {}, False
    for k in S:
        if end in S[k]:
            v[k] = S[k][end]
        else:
            prior = [e for e in S[k] if e <= end]
            v[k] = S[k][max(prior)] if prior else 0.0
            mixed = mixed or bool(prior)
    front, belly, lng = v["y1"] + v["y2"], v["y3"] + v["y4"] + v["y5"], v["after5"]
    return {"tk": tk, "front": front, "belly": belly, "long": lng, "tot": front + belly + lng,
            "end": end, "mixed": mixed, "stale": end < "2025-06-30", "issue": ISSUE.get(tk, "LONG"),
            "cap": mktcap(tk)}


def overlays():
    return list(csv.DictReader(open(OVER))) if os.path.exists(OVER) else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--auction")
    ap.add_argument("--tail", type=float, help="bp vs when-issued; + = tail (weak), - = stop-through (strong)")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--date", default=date.today().isoformat())
    a = ap.parse_args()

    profs = [profile(t, c) for t, c in ISSUERS.items()]
    ov = overlays()
    print("WHERE EACH BORROWER NEEDS MONEY NEXT — scheduled debt maturities ($B, SEC XBRL) + overlays\n")
    print(f"{'name':6} {'due<=2y':>8} {'3-5y':>6} {'>5y':>6}  {'refi% cap':>9}  issues-at   as-of")
    for p in profs:
        if not p["tot"]:
            print(f"{p['tk']:6} — no XBRL maturity table —"); continue
        rc = f"{100*p['front']/p['cap']:8.1f}%" if p["cap"] else "      n/a"
        flag = " STALE" if p["stale"] else (" *mixed" if p["mixed"] else "")
        print(f"{p['tk']:6} {p['front']:8.1f} {p['belly']:6.1f} {p['long']:6.1f}  {rc}  {p['issue']:10}  {p['end']}{flag}")
    print("\nOVERLAYS (floating · new issues · ⚠️ YELLOW = backstop/guarantee/RVG — not their debt, scrutinized as if it were):")
    for o in ov:
        fl = "⚠️ YELLOW" if o["flag"] == "YELLOW" else "        "
        print(f"  {fl} {o['exposed']:5} {o['bucket']:7} ${float(o['amount_B']):6.1f}B  {o['kind']:9} {o['counterparty']}")

    if not a.auction:
        return
    if a.tail is None or abs(a.tail) < 0.5:
        print(f"\n{a.auction}: |tail| < 0.5bp = CLEAN — no marks."); return
    col = "bear" if a.tail > 0 else "bull"
    prim_b, sec_b = AUCTION[a.auction]
    ev = f"{a.auction} auction {'tail' if a.tail > 0 else 'stop-through'} {a.tail:+.1f}bp -> curve exposure"
    # EXPOSURE at this auction's bucket ($B): refinancing need (due <=2y) if the name ISSUES at this bucket
    # + overlays at this bucket (YELLOW backstops count HALF — not their debt, scrutinized as if it were;
    # floating debt counts at FRONT). MATERIALITY = exposure / market cap: >=10% -> w 1.0 · 2-10% -> 0.5.
    buckets = [b for b in (prim_b, sec_b) if b]
    caps = {p["tk"]: p.get("cap") for p in profs}
    expo, why = {}, {}
    for p in profs:
        if p["tot"] and not p["stale"] and any(b in p["issue"] for b in buckets):
            expo[p["tk"]] = expo.get(p["tk"], 0) + p["front"]
            why.setdefault(p["tk"], []).append(f"refi ${p['front']:.1f}B due<=2y, issues {p['issue']}")
    for o in ov:
        ob = "FRONT" if o["kind"] == "floating" else o["bucket"]
        if ob in buckets and float(o["amount_B"]) > 0:
            amt = float(o["amount_B"]) * (0.5 if o["flag"] == "YELLOW" else 1.0)
            expo[o["exposed"]] = expo.get(o["exposed"], 0) + amt
            why.setdefault(o["exposed"], []).append(("⚠️" if o["flag"] == "YELLOW" else "") + o["counterparty"])
    print(f"\nPROPOSED MARKS — {ev}: {col.upper()}  (materiality = exposure ÷ market cap)")
    rows = []
    for tk, amt in sorted(expo.items(), key=lambda z: -(z[1] / (caps.get(z[0]) or mktcap(z[0]) or 1e9))):
        cap = caps.get(tk) or mktcap(tk)
        m = amt / cap if cap else 0
        w = 1.0 if m >= 0.10 else 0.5 if m >= 0.02 else 0
        tag = f"w={w}" if w else "no mark (<2%)"
        print(f"  {tk:6} ${amt:6.1f}B = {100*m:5.1f}% of cap  {col if w else '':4} {tag:14} [{'; '.join(why[tk])}]")
        if w:
            rows.append((a.date, tk, col, w, "TLT", ev, "tools/curve_exposure.py"))
    if a.write:
        with open(MARKS, "a", newline="") as f:
            csv.writer(f).writerows(rows)
        print(f"  → {len(rows)} marks appended to data/money/marks.csv")


if __name__ == "__main__":
    main()
