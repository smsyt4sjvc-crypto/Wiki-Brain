#!/usr/bin/env python3
"""
fragility.py -- reads data/fragility/series/*.csv, scores each indicator against
ITS OWN history, and prints the dashboard. Also writes latest.json for the HTML
generator.

SCORING PHILOSOPHY (this is the part that can be wrong, so it is stated)
-----------------------------------------------------------------------
NO ABSOLUTE THRESHOLDS. Jake's own rule for swap spreads -- "don't use an
arbitrary X bps = crisis, regulation and issuance move the equilibrium" --
is applied to EVERY series here. Each indicator is scored two ways against
its own trailing 3 years:

  LEVEL   percentile rank of today's value
  RATE    percentile rank of the trailing 20-observation CHANGE

Status combines them, and RATE is weighted to fire first, because Jake's
transmission chain is a statement about SEQUENCE, not about levels.

  critical  level >=95th AND rate >=80th      (high and still accelerating)
  serious   level >=90th OR  rate >=95th
  warning   level >=75th OR  rate >=85th
  calm      otherwise

INVERTED series (bank C&I loans, deposits) are scored on 13-observation
percent change only, flipped -- for those, CONTRACTION is the stress.

STALENESS IS A FIRST-CLASS OUTPUT. A weekly series is not late at 6 days;
a daily series is late at 6 days. Each row carries its own expected cadence
and says so. A stale number that looks calm is the most dangerous cell on
any dashboard.
"""
import csv, json, os, sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(ROOT, "data", "fragility")
SER  = os.path.join(OUT, "series")

# key: (label, chart#, stage, unit, scale, cadence_days, inverted, note)
IND = {
 "ccc_oas":   ("CCC & lower OAS",              1, 1, "bp",   100, 4,  0, "the weakest borrowers"),
 "hy_oas":    ("High-yield OAS",               1, 1, "bp",   100, 4,  0, "general junk conditions"),
 "ccc_hy_gap":("CCC minus HY quality gap",     1, 1, "bp",   100, 4,  0, "CCC breaking underneath the index"),
 "bbb_oas":   ("BBB OAS",                      2, 2, "bp",   100, 4,  0, "junk problem -> corporate problem"),
 "ig_oas":    ("Investment-grade OAS",         2, 2, "bp",   100, 4,  0, "systemic corporate repricing"),
 "cp_spread": ("A2/P2 minus AA CP 90d",        8, 3, "bp",     1, 4,  0, "short-term unsecured corporate money"),
 "move":      ("MOVE index",                   4, 4, "pts",    1, 5,  0, "implied Treasury vol -- AGENT-FETCHED, not in the cron"),
 "rvol10":    ("10Y realized vol",             4, 4, "bp ann", 1, 4,  0, "realized, not implied -- the cron-safe leg"),
 "dgs30":     ("30Y Treasury yield",           4, 4, "%",      1, 4,  0, "dangerous when rising WITH vol"),
 "pd_ust":    ("Dealer UST net position",      9, 5, "$mm",    1, 10, 0, "are dealers getting stuffed"),
 "repo_fin":  ("Dealer UST repo financing",    9, 5, "$mm",    1, 10, 0, "dealers funding their own inventory"),
 "rev_repo":  ("Dealer UST reverse repo",      9, 5, "$mm",    1, 10, 0, "cash lent out against collateral"),
 "pd_ftd":    ("Dealer UST fails to deliver",  9, 5, "$mm",    1, 10, 0, "settlement plumbing"),
 "pd_ftr":    ("Dealer UST fails to receive",  9, 5, "$mm",    1, 10, 0, "settlement plumbing"),
 "sofr_iorb": ("SOFR minus IORB",              7, 6, "bp",     1, 4,  0, "overnight secured funding"),
 "repo_ops":  ("Fed repo ops accepted",        7, 6, "$B",     1, 4,  0, "SRF take-up = plumbing tightening"),
 "ci_all":    ("H.8 C&I loans, all banks",    10, 7, "$B",     1, 10, 1, "contraction is the stress here"),
 "ci_large":  ("H.8 C&I loans, LARGE banks",  10, 7, "$B",     1, 10, 1, "DERIVED: domestic minus small, both NSA"),
 "ci_small":  ("H.8 C&I loans, SMALL banks",  10, 7, "$B",     1, 10, 1, "NSA -- the SA series died in 2018"),
 "cre_all":   ("H.8 CRE loans, all banks",    10, 7, "$B",     1, 10, 1, "commercial real estate"),
 "cre_large": ("H.8 CRE loans, LARGE banks",  10, 7, "$B",     1, 10, 1, "commercial real estate"),
 "cre_small": ("H.8 CRE loans, SMALL banks",  10, 7, "$B",     1, 10, 1, "67% of ALL CRE sits at small banks"),
 "dep_large": ("H.8 deposits, LARGE banks",   10, 7, "$B",     1, 10, 1, "funding base"),
 "dep_small": ("H.8 deposits, SMALL banks",   10, 7, "$B",     1, 10, 1, "deposit flight shows up here first"),
 "vix":       ("VIX",                          0, 0, "pts",    1, 4,  0, "context only -- not a chain stage"),
}
STAGES = {
 1: "Low-quality credit (CCC/HY)",
 2: "Investment grade (BBB/IG)",
 3: "Corporate short-term funding (CP)",
 4: "Rates volatility / the collateral",
 5: "Dealers & Treasury absorption",
 6: "Repo & money-market plumbing",
 7: "Bank credit channel",
}
# Series whose LEVEL trends structurally -- a level percentile on these is an
# artifact of the trend, not a stress reading. The 30Y sits at the 99th
# percentile of 3 years because yields ROSE, not because today is stressed;
# dealer positions sit high because ISSUANCE is high. For these, status comes
# from RATE OF CHANGE ONLY. This is Jake's own swap-spread rule generalised:
# no arbitrary level threshold, watch for dislocation from the recent range.
DETREND = {"dgs30", "pd_ust", "pd_ftd", "pd_ftr", "repo_fin", "rev_repo"}

# Series that RESTATE another series rather than adding evidence. The CCC-minus-HY
# gap is arithmetic on ccc_oas and hy_oas -- counting it as a third lit indicator
# in stage 1 would be counting CCC twice. Excluded from the corroboration count,
# still shown, still scored.
REDUNDANT = {"ccc_hy_gap": ("ccc_oas", "hy_oas")}

RANK = {"calm": 0, "warning": 1, "serious": 2, "critical": 3}
ICON = {"calm": "OK", "warning": "!", "serious": "!!", "critical": "!!!"}

def load(key):
    p = os.path.join(SER, f"{key}.csv")
    if not os.path.exists(p): return []
    out = []
    with open(p) as fh:
        for r in csv.DictReader(fh):
            try: out.append((r["date"], float(r["value"])))
            except (ValueError, TypeError): pass
    return out

def pctrank(xs, v):
    if not xs: return None
    return 100.0 * sum(1 for x in xs if x <= v) / len(xs)

def score(key, s):
    label, chart, stage, unit, scale, cadence, inv, note = IND[key]
    if len(s) < 30: return None
    cut = (date.today() - timedelta(days=365 * 3)).isoformat()
    hist = [(d, v) for d, v in s if d >= cut] or s
    vals = [v * scale for _, v in hist]
    last_d, last_v = s[-1][0], s[-1][1] * scale

    def chg(n):
        return (last_v - s[-1-n][1] * scale) if len(s) > n else None
    d1, d5, d20 = chg(1), chg(5), chg(20)

    if inv:
        # stress = CONTRACTION. Score 13-obs % change, flipped.
        pc = [100.0*(hist[i][1]-hist[i-13][1])/abs(hist[i-13][1])
              for i in range(13, len(hist)) if hist[i-13][1]]
        cur = (100.0*(s[-1][1]-s[-14][1])/abs(s[-14][1])) if len(s) > 14 and s[-14][1] else None
        lvl_p = None
        rate_p = (100 - pctrank(pc, cur)) if cur is not None else None
    else:
        lvl_p = pctrank(vals, last_v)
        ch = [vals[i]-vals[i-20] for i in range(20, len(vals))]
        rate_p = pctrank(ch, d20) if d20 is not None else None

    st = "calm"
    R = rate_p or 0
    if key in DETREND or inv:
        L = None                       # level says nothing; rate is the signal
        if   R >= 97: st = "critical"
        elif R >= 90: st = "serious"
        elif R >= 80: st = "warning"
    else:
        L = lvl_p or 0
        if   L >= 95 and R >= 80: st = "critical"
        elif L >= 90 or  R >= 95: st = "serious"
        elif L >= 75 or  R >= 85: st = "warning"

    age = (date.today() - datetime.strptime(last_d, "%Y-%m-%d").date()).days
    return {"key": key, "label": label, "chart": chart, "stage": stage,
            "unit": unit, "note": note, "inverted": bool(inv),
            "date": last_d, "value": round(last_v, 4),
            "d1": d1 and round(d1, 3), "d5": d5 and round(d5, 3),
            "d20": d20 and round(d20, 3),
            "level_pct": (None if (key in DETREND or inv) else
                          (lvl_p and round(lvl_p, 1))),
            "detrended": key in DETREND or bool(inv),
            "rate_pct": rate_p and round(rate_p, 1),
            "status": st, "n": len(s), "age_days": age,
            "redundant": key in REDUNDANT,
            "stale": age > cadence,
            "spark": [round(v, 4) for v in vals[-120:]]}

def cds_panel():
    """The 11th panel: ICE Clear Credit single-name 5Y CDS.

    ⛔ SCORED DIFFERENTLY FROM EVERY OTHER ROW, ON PURPOSE. ICE publishes ONE
    clearing date and licenses the history, so the vault accumulates forward from
    2026-08-22. There is no 3-year window to rank against and there will not be
    one for years. Faking a percentile here would be the exact sin this dashboard
    was built to avoid, so these are LEVELS, and the panel says how much history
    it actually has."""
    path = os.path.join(OUT, "cds_panel.csv")
    if not os.path.exists(path):
        return None
    rows = list(csv.DictReader(open(path)))
    if not rows:
        return None
    dates = sorted({r["date"] for r in rows})
    latest = [r for r in rows if r["date"] == dates[-1]]
    hist = {}
    for r in rows:
        hist.setdefault(r["ticker"], []).append((r["date"], float(r["spread_bp"])))
    names = []
    for r in sorted(latest, key=lambda x: -float(x["spread_bp"])):
        h = sorted(hist[r["ticker"]])
        prev = h[-2][1] if len(h) > 1 else None
        names.append({
            "ticker": r["ticker"], "issuer": r["issuer"],
            "spread_bp": float(r["spread_bp"]), "price": float(r["price"]),
            "coupon_bp": int(r["coupon_bp"]), "maturity": r["maturity"],
            "chg": (round(float(r["spread_bp"]) - prev, 1) if prev is not None else None),
            "hy_convention": int(r["coupon_bp"]) == 500,
            "spark": [v for _, v in h][-120:],
        })
    sp = sorted(n["spread_bp"] for n in names)
    med = sp[len(sp)//2] if len(sp) % 2 else (sp[len(sp)//2-1] + sp[len(sp)//2]) / 2
    return {"date": dates[-1], "days_of_history": len(dates), "names": names,
            "median_bp": round(med, 1),
            "dispersion": round(max(sp) / min(sp), 1) if min(sp) else None,
            # Jake's spec: "number making 3-month highs". Needs 3 months.
            "three_month_highs": (sum(1 for n in names
                                      if n["spread_bp"] >= max(n["spark"]))
                                  if len(dates) >= 60 else None),
            "maturity": names[0]["maturity"]}


def main():
    rows = [r for r in (score(k, load(k)) for k in IND) if r]
    meta = {}
    mp = os.path.join(OUT, "raw_meta.json")
    if os.path.exists(mp): meta = json.load(open(mp))

    # ladder: worst status per chain stage
    # ⚠️ COUNT BIAS: a worst-of-stage rule makes a stage with 8 series far more
    # likely to light than a stage with 1, purely from having more chances. The
    # math is left alone -- the fix is to SHOW how many of the stage's series are
    # lit, so "1 of 8" is never read as "the stage is lit". CORROBORATED means two
    # or more NON-REDUNDANT series in that stage agree.
    ladder = []
    for sn in sorted(STAGES):
        rs = [r for r in rows if r["stage"] == sn]
        indep = [r for r in rs if not r["redundant"]]
        worst = max((r["status"] for r in rs), key=lambda x: RANK[x]) if rs else "calm"
        n_lit = sum(1 for r in indep if RANK[r["status"]] >= 1)
        ladder.append({"stage": sn, "name": STAGES[sn], "status": worst,
                       "n": len(rs), "n_indep": len(indep), "n_lit": n_lit,
                       "corroborated": n_lit >= 2, "lit": RANK[worst] >= 1})

    lit  = [l for l in ladder if l["lit"]]
    corr = [l for l in lit if l["corroborated"]]
    if not lit:
        verdict = "NO STAGE LIT -- no evidence of a credit crack in the public data."
    elif len(lit) == 1:
        c = ("corroborated by %d of its %d independent series"
             % (lit[0]["n_lit"], lit[0]["n_indep"])) if lit[0]["corroborated"] else \
            ("on a SINGLE series of %d -- weak" % lit[0]["n_indep"])
        verdict = (f"ONE STAGE LIT (stage {lit[0]['stage']}: {lit[0]['name']}, {c}). "
                   "Localised repricing, not a chain.")
    else:
        verdict = (f"{len(lit)} STAGES LIT ({len(corr)} corroborated): " +
                   " -> ".join(str(l["stage"]) for l in lit) +
                   ". Check whether they lit IN ORDER -- sequence is the signal.")

    panel = cds_panel()
    payload = {"cds": panel, "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
               "verdict": verdict, "ladder": ladder, "rows": rows,
               "gaps": meta.get("gaps", []), "feed_errors": meta.get("errors", []),
               "stages": STAGES}
    with open(os.path.join(OUT, "latest.json"), "w") as fh:
        json.dump(payload, fh, indent=1)

    # ---- terminal view
    W = 96
    print("=" * W)
    print("  CREDIT / DEBT FRAGILITY DASHBOARD".ljust(70) + payload["generated"][:16])
    print("=" * W)
    print("\n  TRANSMISSION LADDER  (stress migrates downward; SEQUENCE is the signal)")
    print("  n/N lit = independent series in that stage at warning or worse."
          "  * = corroborated (2+)")
    for l in ladder:
        bar = "#" * RANK[l["status"]] if RANK[l["status"]] else "."
        mark = "*" if l["corroborated"] else (" " if l["lit"] else " ")
        print(f"   {l['stage']}  [{bar:<3}] {ICON[l['status']]:<4}"
              f" {l['name']:<38} {l['n_lit']}/{l['n_indep']} lit{mark}")
    print(f"\n  >> {verdict}\n")
    print(f"  {'indicator':<30}{'value':>11} {'unit':<8}{'chg1p':>10}{'chg20p':>11}"
          f"{'lvl%':>6}{'rate%':>7}  status")
    print("  (chg is in OBSERVATIONS not days -- weekly series: 1p = 1 week)")
    print("  " + "-" * (W - 4))
    cur = None
    for r in sorted(rows, key=lambda x: (x["stage"] or 99, -RANK[x["status"]])):
        if r["stage"] != cur:
            cur = r["stage"]
            print(f"  -- stage {cur}: {STAGES.get(cur,'context')}")
        f = lambda v: ("--" if v is None else (f"{v:+,.0f}" if abs(v) >= 1000 else f"{v:+,.2f}"))
        lvl = "  -" if r["level_pct"] is None else f"{r['level_pct']:.0f}"
        flag = "  STALE" if r["stale"] else ""
        print(f"  {r['label']:<30}{r['value']:>11,.2f} {r['unit']:<8}"
              f"{f(r['d1']):>10}{f(r['d20']):>11}"
              f"{lvl:>6}"
              f"{(r['rate_pct'] if r['rate_pct'] is not None else 0):>7.0f}"
              f"  {ICON[r['status']]:<4}{r['status']}{flag}")
    if panel:
        print(f"\n  ⬜ AI-COMPLEX SINGLE-NAME CDS (ICE Clear Credit, {panel['date']}) "
              f"-- LEVELS ONLY, {panel['days_of_history']} day(s) of history")
        print(f"  {'ticker':<8}{'issuer':<24}{'spread':>9}{'chg':>8}   note")
        print("  " + "-" * 60)
        for n in panel["names"]:
            c = "--" if n["chg"] is None else f"{n['chg']:+.1f}"
            note = "HY convention (no 100bp contract)" if n["hy_convention"] else ""
            print(f"  {n['ticker']:<8}{n['issuer']:<24}{n['spread_bp']:>9.1f}{c:>8}   {note}")
        tmh = ("insufficient history" if panel["three_month_highs"] is None
               else f"{panel['three_month_highs']}")
        print(f"\n  MEDIAN {panel['median_bp']}bp  ·  dispersion {panel['dispersion']}x  "
              f"·  3-month highs: {tmh}")
        print(f"  ⚠️ Spreads are MODELLED from ICE points-upfront prices, not quoted. "
              f"Maturity {panel['maturity']} rolls on the next IMM date.")

    if payload["gaps"]:
        print(f"\n  KNOWN GAPS -- these charts are NOT in the data above:")
        for g in payload["gaps"]:
            print(f"   [{g['status']}] chart {g['chart']}: {g['name']}")
    if payload["feed_errors"]:
        print(f"\n  FEED ERRORS: {[e['key'] for e in payload['feed_errors']]}")
    print()

if __name__ == "__main__":
    main()
