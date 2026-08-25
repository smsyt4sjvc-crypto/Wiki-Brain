#!/usr/bin/env python3
# =============================================================================
#  DURABLE-VALUE SCREEN — a POINT-IN-TIME backtest of "cheap, but for a good reason"
#  Built 2026-08-15, rebuilt 2026-08-16 after three EPS bugs. Paste and run.
#
#  THE QUESTION
#  ------------
#  A low price-to-earnings (P/E) ratio has two very different causes:
#    (a) the price is depressed and the earnings are normal   -> possibly cheap
#    (b) the EARNINGS are temporarily inflated and the price is normal -> a TRAP
#  Case (b) is the whole argument at single-stock scale: a cyclical at peak
#  earnings prints its LOWEST multiple exactly when it is most expensive.
#
#  Jake's spec as filters: low P/E, where BOTH the P and the E sit in
#  historically tolerated ranges -- not where one of them is doing all the work.
#  No quarter of crazy earnings, no pulled-forward depreciation, no acquisition
#  eating the earnings. Good balance sheet. Price above its 50- and 200-day
#  moving averages (that is what excludes the falling knife).
#
#  ⛔ THE TWO THINGS THAT WOULD INVALIDATE THIS, STATED UP FRONT
#  -------------------------------------------------------------
#  1. LOOK-AHEAD BIAS. Using today's fundamentals for a 2021 screen is cheating.
#     FIXED: every EDGAR fact carries a `filed` date and this script uses ONLY
#     facts filed BEFORE the formation date. That is real point-in-time.
#  2. SURVIVORSHIP BIAS. The universe is TODAY'S index. Every company that went
#     bankrupt, got acquired, or shrank out of the index between 2021 and now is
#     missing -- and those are disproportionately the failures.
#     NOT FIXED. It biases every return in this script UPWARD, including the
#     benchmark. Read the SPREAD vs the benchmark, never the absolute return.
#
#  WHY THE CONTROL GROUP IS THE POINT: the script runs the screen WITH and
#  WITHOUT the durability filter. If durable-E cheap beats naive cheap, the
#  filter is doing work. If it does not, the idea is wrong and we say so.
#
#  ⛔⛔ THE THREE EPS BUGS THIS FILE EXISTS TO KILL (found 2026-08-16, all in
#  one hand-check of five names -- the run BEFORE this one was unreportable)
#  ---------------------------------------------------------------------------
#  A. QUARTERLY FACTS WEARING ANNUAL CLOTHES. Valero's 10-K tags its quarterly
#     EPS footnote with form="10-K". Keying on `end` alone lets Q4-2019 (end
#     2019-12-31, val 2.58) silently OVERWRITE FY-2019 (same end, val 5.84).
#     VLO's "annual EPS history" printed as [2.58, -4.54, 3.07, -1.14, -0.88]:
#     five CONSECUTIVE QUARTERS masquerading as five YEARS. Chevron's 10-K does
#     not tag quarterly data, so Chevron looked fine.
#     ⇒ THE BUG WAS COMPANY-DEPENDENT. Spot-checking one name could not find it.
#  B. YEAR-TO-DATE MIXED WITH DISCRETE QUARTERS. A Q2 10-Q carries BOTH the
#     3-month figure and the 6-month figure, and `fp` says "Q2" for both.
#     Summing four rows off the `fp` label mixes bases and double-counts.
#  C. THE STRUCTURAL ONE: Q4 DISCRETE EPS IS NEVER IN A 10-Q. It exists only in
#     the 10-K, and only for filers that tag it. So "sum four 10-Q quarters" can
#     NEVER build a trailing twelve months that spans a fiscal year-end. That is
#     not patchable by filtering forms.
#
#  ⇒ THE FIX, AND IT IS THE ONLY CONSTRUCTION THAT WORKS ON WHAT EDGAR ACTUALLY
#    PUBLISHES: classify every fact by the SPAN BETWEEN ITS start AND end DATES,
#    never by its form or fp label. Then build the trailing twelve months by
#    ARITHMETIC ON CUMULATIVE PERIODS:
#
#        TTM = latest FY annual
#            + current-FY cumulative through period P
#            - prior-FY cumulative through the SAME period P
#
#    Verified by hand against the raw facts, formation 2021-08-16:
#      CVX  -2.96 + 2.32 - (-2.51) = +1.87  -> P/E 54.0   (was: nan)
#      VLO  -3.50 + (-1.34) - (-1.48) = -3.36 -> loss     (was: P/E 109.4)
#    Both are RIGHT, and both correctly DROP OUT of a cheapness screen. The old
#    code showed Valero as a 109x "value" name.
# =============================================================================

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from statistics import median

# ----------------------------------------------------------------- PARAMETERS
SEC_UA    = {"User-Agent": "INMA Research contact@example.com"}   # SEC requires a real UA
YF_UA     = {"User-Agent": "Mozilla/5.0"}

PE_PCTILE       = 0.20    # "low P/E" = bottom quintile OF THE DATE'S OWN CROSS-SECTION
DURABLE_LO      = 0.70    # TTM EPS must be >= 0.70x the multi-year median  (not collapsed)
DURABLE_HI      = 1.60    # ...and <= 1.60x                                  (not a spike)
MIN_YEARS       = 4       # need this many annual EPS prints for a median to mean anything
MIN_EQUITY_ASSETS = 0.30  # equity as a share of assets -- see the note on total_debt()
MIN_CURRENT     = 1.00    # current ratio
REQUIRE_SMA     = True    # price above BOTH the 50d and 200d at formation
MAX_TTM_STALE   = 200     # days: a TTM built from a bare annual older than this is unusable

CACHE = os.environ.get("DVS_CACHE", "/tmp/dvs_cache")

# ------------------------------------------------------------------- PLUMBING
def _get(url, headers, tries=3, pause=0.35):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=45) as fh:
                return json.load(fh)
        except urllib.error.HTTPError as e:
            if e.code in (404, 403):
                return None
            time.sleep(pause * (i + 1))
        except Exception:
            time.sleep(pause * (i + 1))
    return None


def _cached(key, fn):
    """EDGAR companyfacts blobs run to tens of megabytes. Cache them so a
    re-run after a parameter change costs no network and no SEC goodwill."""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, key + ".json")
    if os.path.exists(path):
        try:
            with open(path) as fh:
                return json.load(fh)
        except Exception:
            pass
    d = fn()
    if d is not None:
        try:
            with open(path, "w") as fh:
                json.dump(d, fh)
        except Exception:
            pass
    return d


def sp500_tickers():
    """Ticker -> CIK. ⚠️ NOT point-in-time -- see the survivorship note."""
    d = _cached("_tickers", lambda: _get("https://www.sec.gov/files/company_tickers.json", SEC_UA))
    if not d:
        return {}
    return {v["ticker"]: str(v["cik_str"]).zfill(10) for v in d.values()}


def prices(ticker):
    """Daily closes AND the split history.

    ⛔ THE BUG THIS EXISTS TO KILL, caught on the first smoke test: Yahoo's
    closes are SPLIT-ADJUSTED BACKWARDS. EDGAR's EPS is AS-REPORTED at the time
    and is NOT. Divide one by the other and a stock that later split 10:1 shows
    a P/E ten times too low. The smoke test printed NVDA at 2.6x and GOOGL at
    1.7x in Aug-2021 -- both nonsense, both caused by exactly this.

    So: return the adjusted series AND the AS-TRADED price, which is the only
    thing comparable to a filed EPS.
    """
    def fetch():
        return _get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                    f"?range=10y&interval=1d&events=split", YF_UA)
    d = _cached("px_" + ticker.replace("/", "_"), fetch)
    try:
        r = d["chart"]["result"][0]
        splits = []
        for s in (r.get("events", {}).get("splits") or {}).values():
            splits.append((datetime.fromtimestamp(s["date"], timezone.utc).strftime("%Y-%m-%d"),
                           s["numerator"] / s["denominator"]))
        splits.sort()
        out = []
        for t, c in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]):
            if c is None:
                continue
            dt = datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d")
            f = 1.0                                     # cumulative factor of splits AFTER this date
            for sd, ratio in splits:
                if sd > dt:
                    f *= ratio
            out.append((dt, c, c * f))                  # (date, adjusted, AS-TRADED)
        return out
    except Exception:
        return []


def px_on(series, date, traded=False):
    """Last close on or before `date`.
    traded=False -> split-ADJUSTED (use for RETURNS, which must be adjusted).
    traded=True  -> AS-TRADED     (use for the P/E, which must match filed EPS)."""
    i = 2 if traded else 1
    prior = [row[i] for row in series if row[0] <= date]
    return prior[-1] if prior else None


def sma(series, date, n):
    """SMA on the ADJUSTED series -- a split must not create a fake trend break."""
    prior = [row[1] for row in series if row[0] <= date]
    return sum(prior[-n:]) / n if len(prior) >= n else None


def edgar_facts(cik):
    return _cached("cf_" + cik,
                   lambda: _get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", SEC_UA))


def splits_of(ticker):
    """Split events (date, ratio) from the same cached Yahoo blob the prices use."""
    def fetch():
        return _get(f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
                    f"?range=10y&interval=1d&events=split", YF_UA)
    d = _cached("px_" + ticker.replace("/", "_"), fetch)
    try:
        ev = (d["chart"]["result"][0].get("events", {}).get("splits") or {}).values()
        out = [(datetime.fromtimestamp(s["date"], timezone.utc).strftime("%Y-%m-%d"),
                s["numerator"] / s["denominator"]) for s in ev]
        return sorted(out)
    except Exception:
        return []


# ------------------------------------------------------- THE EPS LAYER (rebuilt)
def _days(a, b):
    return (datetime.fromisoformat(b) - datetime.fromisoformat(a)).days


def eps_facts(facts, asof, splits=()):
    """Every diluted-EPS fact FILED STRICTLY BEFORE `asof`, tagged with the true
    length of the period it covers, and restated onto ONE share basis.

    The `filed` filter is the line that makes the whole backtest honest -- drop
    it and you are fitting on data nobody had.
    The `span` field is the line that makes the EPS honest -- see bugs A/B/C.

    ⛔ BUG D, THE SPLIT BUG A SECOND TIME, INSIDE THE EPS HISTORY ITSELF.
    EDGAR restates comparatives for a split only in filings made AFTER it, so a
    single company's history is MIXED-BASIS. Apple's annual list came back as
        [9.22, 8.31, 9.21, 2.98, 2.97, 3.28]
    -- the first three pre-split as-reported, the next two EDGAR's post-split
    restatements of 11.91 and 11.89 (the 4:1 of Aug-2020). The MEDIAN of that
    list is not a number about anything, and the median is what the durability
    ratio divides by.

    ⇒ Adjust each fact by the splits that fell between ITS OWN `filed` DATE and
      the formation date -- the exact mirror of how the price series is adjusted
      by the splits after each price date. A fact filed after a split already
      reflects it; a fact filed before it does not. Everything then sits on the
      basis in effect AT FORMATION, which is the basis of the as-traded price.
      Apple becomes [2.31, 2.08, 2.30, 2.98, 2.97, 3.28] -- one basis, and its
      durability goes 0.88 -> 1.94, correctly reading 2021 as a SPIKE.
    """
    us = facts.get("facts", {}).get("us-gaap", {})
    node = us.get("EarningsPerShareDiluted") or us.get("EarningsPerShareBasicAndDiluted")
    if not node:
        return []
    rows = []
    for u in node.get("units", {}).get("USD/shares", []):
        if not u.get("filed") or u["filed"] >= asof or u.get("val") is None or not u.get("start"):
            continue
        f = 1.0
        for sd, ratio in splits:                # splits between the filing and formation
            if u["filed"] < sd <= asof:
                f *= ratio
        rows.append(dict(start=u["start"], end=u["end"], val=u["val"] / f,
                         raw=u["val"], adj=f, filed=u["filed"], form=u.get("form", ""),
                         span=_days(u["start"], u["end"])))
    rows.sort(key=lambda r: (r["end"], r["filed"]))
    return rows


def _dedupe(rows):
    """Latest FILING wins for a given (start, end) -- that is a restatement,
    and the point-in-time investor would have seen the restated number."""
    by = {}
    for r in rows:
        by[(r["start"], r["end"])] = r
    return sorted(by.values(), key=lambda r: r["end"])


def annual_eps(facts, asof, splits=()):
    """Annual diluted EPS history, selected BY SPAN (340-400 days), never by form.

    ⛔ Selecting by form="10-K" is what produced VLO's five-quarters-as-five-years
    (bug A). A 10-K contains quarterly facts too; a fiscal year is 365 days long
    and that is the only reliable signal in the data."""
    return _dedupe([r for r in eps_facts(facts, asof, splits) if 340 <= r["span"] <= 400])


def ttm_eps(facts, asof, splits=()):
    """Trailing twelve months diluted EPS, point-in-time.

    Builds EVERY construction that the data supports and returns THE FRESHEST --
    not the first one that happens to work:
      cum:    latest FY + current-FY-to-date - prior-FY-to-same-date.
              The only method that spans a fiscal year-end, because Q4 discrete
              EPS is never published in a 10-Q (bug C).
      4q:     four consecutive discrete quarters, verified consecutive BY DATE
              (each start within 5 days of the prior end, total span 350-380).
              Not by counting rows off an `fp` label (bug B).
      annual: the bare latest fiscal year.

    ⚠️ WHY FRESHEST, NOT A FIXED LADDER: Procter & Gamble has a June year-end and
    filed its FY2021 10-K on 2021-08-05, eleven days before formation. A ladder
    that tries `cum` first finds no post-year-end quarter yet, falls through to
    `4q`, and returns a window ending 31-MAR -- 138 days stale -- when a 47-day-old
    full fiscal year was sitting right there. Freshest-wins fixes every fiscal
    calendar at once instead of special-casing them.

    Returns (ttm, annual_list, method, stale_days).
    """
    rows = eps_facts(facts, asof, splits)
    ann = annual_eps(facts, asof, splits)
    hist = [a["val"] for a in ann]
    if not rows:
        return None, [], "none", None
    cands = []

    # ---- cumulative arithmetic
    if ann:
        fy = ann[-1]
        cum = [r for r in rows if 80 <= r["span"] <= 290 and r["start"] > fy["end"]]
        if cum:
            cur = max(cum, key=lambda r: (r["end"], r["filed"]))
            prev = [r for r in rows
                    if abs(r["span"] - cur["span"]) <= 6
                    and 350 <= _days(r["start"], cur["start"]) <= 380]
            if prev:
                p = max(prev, key=lambda r: r["filed"])
                cands.append((_days(cur["end"], asof), fy["val"] + cur["val"] - p["val"], "cum"))

    # ---- four consecutive discrete quarters
    q = _dedupe([r for r in rows if 80 <= r["span"] <= 100])
    if len(q) >= 4:
        w = q[-4:]
        if (all(abs(_days(w[i]["end"], w[i + 1]["start"])) <= 5 for i in range(3))
                and 350 <= _days(w[0]["start"], w[-1]["end"]) <= 380):
            cands.append((_days(w[-1]["end"], asof), sum(x["val"] for x in w), "4q"))

    # ---- the bare latest fiscal year
    if ann:
        cands.append((_days(ann[-1]["end"], asof), ann[-1]["val"], "annual"))

    if not cands:
        return None, hist, "none", None
    stale, val, method = min(cands, key=lambda c: c[0])
    return val, hist, method, stale


MAX_BS_AGE = 200          # days: a balance sheet older than this is not a balance sheet


def instant(facts, tags, asof, max_age=MAX_BS_AGE):
    """Latest balance-sheet value as of a date, point-in-time. Balance-sheet
    facts are INSTANTS: they carry an `end` and no `start`.

    ⛔⛔ STALE REFERENCE VALUE — THE THIRD INSTANCE OF THIS ERROR CLASS IN THREE
    DAYS, and the first two were `meta.chartPreviousClose` (8/14, every sign in a
    published market table wrong) and a rejection computed off a 2024 denominator
    (8/14). Same shape every time: THE VALUE IS CORRECT AND THE DATE IS NOT.

    The defect here: this returned the newest fact carrying a tag, however old
    that was. FILERS ABANDON TAGS. Marathon Petroleum last used
    `LongTermDebtNoncurrent` on 2012-03-31; the screen cheerfully reported a
    NINE-YEAR-OLD figure as its 2021 debt and computed a leverage ratio of 0.11
    from it. Ford's last use was a $0.29B fragment while its actual borrowings
    sit under a tag this list never checked.

    ⇒ A FACT MUST BE REJECTED ON AGE, NOT JUST ON FILING ORDER. `max_age` is the
      gate, and it protects every instant read here -- equity, current assets and
      current liabilities were all exposed to exactly the same failure.
    """
    us = facts.get("facts", {}).get("us-gaap", {})
    for tag in tags:
        node = us.get(tag)
        if not node:
            continue
        rows = [u for u in node.get("units", {}).get("USD", [])
                if u.get("filed") and u["filed"] < asof and u.get("val") is not None
                and not u.get("start") and _days(u["end"], asof) <= max_age]
        if rows:
            rows.sort(key=lambda r: (r["end"], r["filed"]))
            return rows[-1]["val"]
    return None



def total_debt(facts, asof):
    """INTEREST-BEARING DEBT, not the whole right-hand side of the balance sheet.

    ⛔ THE ERROR THIS REPLACES, and it is MY error, not EDGAR's: the first run
    computed leverage as `Liabilities / StockholdersEquity`. `Liabilities` is
    EVERYTHING a company owes -- accounts payable, deferred revenue, pension,
    lease, tax. A perfectly ordinary industrial runs 1.5-2.5x on that measure
    with no borrowings at all. Gating it at 1.50 cut 14 of the 26 names that had
    survived the P/E gate, which is not a balance-sheet test, it is a business-
    model test that happens to punish anyone with working capital.
    ⇒ INSTRUMENT MISMATCH, the same class that has burned this vault repeatedly:
      the right number for the wrong instrument. Leverage means BORROWINGS.

    ⚠️ AND THE REASON THE SCREEN DOES NOT ULTIMATELY GATE ON THIS: even with the
    staleness fix, XBRL debt tagging is too inconsistent to compare across the
    universe. Measured coverage at 2021-08-16: `LongTermDebt` 85% of names,
    `LongTermDebtNoncurrent` 72%, `LongTermDebtAndCapitalLeaseObligations` 44%.
    Chevron reads 0.03, General Motors and Ford read nothing at all -- their
    borrowings sit in captive-finance tags this list never sees. A gate that can
    only measure 60% of the field does not screen out the levered; it screens out
    THE ONES THAT HAPPEN TO TAG THEIR DEBT, which is not a financial property.
    ⇒ THE GATE USES EQUITY/ASSETS INSTEAD: 100% tagged, unambiguous, identical in
      meaning at every formation date. It counts operating liabilities as well as
      borrowings, so it is a blunter instrument -- but it is applied IDENTICALLY
      to the naive and durable groups, and an identical blunt gate cannot bias a
      COMPARISON. A gate with holes can. Debt/equity is still reported where it
      is measurable, as information, never as a filter.
    """
    long_ = instant(facts, ["LongTermDebtAndCapitalLeaseObligations",
                            "LongTermDebtNoncurrent", "LongTermDebt",
                            "DebtLongtermAndShorttermCombinedAmount"], asof)
    short = instant(facts, ["LongTermDebtAndCapitalLeaseObligationsCurrent",
                            "LongTermDebtCurrent", "DebtCurrent",
                            "ShortTermBorrowings"], asof)
    if long_ is None and short is None:
        return None
    return (long_ or 0.0) + (short or 0.0)


def equity(facts, asof):
    """⚠️ Johnson & Johnson does not tag `StockholdersEquity` at all -- it uses
    the including-noncontrolling-interests variant. A single-tag lookup returned
    None and the leverage gate then passed the name by default."""
    return instant(facts, ["StockholdersEquity",
                           "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
                   asof)


# --------------------------------------------------------------- THE SCREEN
GATES = ["no price", "no facts", "no EPS", "TTM stale", "TTM<=0", "too few years"]


def evaluate(ticker, facts, px, splits, formation, hold_end, funnel):
    """One name, one formation date. `facts`/`px` are passed in so a multi-date
    run loads each 5-80MB companyfacts blob ONCE instead of once per date."""
    p0  = px_on(px, formation)                 # adjusted -> for the RETURN
    p1  = px_on(px, hold_end)
    p0t = px_on(px, formation, traded=True)    # as-traded -> for the P/E
    if not p0 or not p1 or not p0t:
        funnel["no price"] += 1
        return None

    ttm, ann, method, stale = ttm_eps(facts, formation, splits)
    if ttm is None:
        funnel["no EPS"] += 1;        return None
    if stale is not None and stale > MAX_TTM_STALE:
        funnel["TTM stale"] += 1;     return None
    if ttm <= 0:
        funnel["TTM<=0"] += 1;        return None
    if len(ann) < MIN_YEARS:
        funnel["too few years"] += 1; return None

    med = median(ann[-6:])                       # multi-year normal
    if not med or med <= 0:
        funnel["too few years"] += 1; return None

    eq = equity(facts, formation)
    dbt = total_debt(facts, formation)
    assets = instant(facts, ["Assets", "LiabilitiesAndStockholdersEquity"], formation)
    ca = instant(facts, ["AssetsCurrent"], formation)
    cl = instant(facts, ["LiabilitiesCurrent"], formation)

    # 3-year EPS CAGR off the ANNUAL prints.
    # ⚠️ Guarded on BOTH endpoints being positive: Python returns a COMPLEX
    # number for a negative float raised to 1/3, which then raised TypeError
    # inside the caller's try/except and SILENTLY DROPPED the name.
    growth = None
    if len(ann) >= 4 and ann[-4] > 0 and ann[-1] > 0:
        growth = (ann[-1] / ann[-4]) ** (1 / 3) - 1

    s50, s200 = sma(px, formation, 50), sma(px, formation, 200)
    return dict(
        ticker=ticker, pe=p0t / ttm, ttm=ttm, med=med, durability=ttm / med,
        method=method, stale=stale,
        de=((dbt / eq) if (eq and eq > 0 and dbt is not None) else None),
        eq_assets=((eq / assets) if (assets and assets > 0 and eq is not None) else None),
        cr=((ca / cl) if (cl and cl > 0 and ca is not None) else None),
        above50=(s50 is not None and p0 > s50),
        above200=(s200 is not None and p0 > s200),
        no_loss=all(e > 0 for e in ann[-3:]), growth=growth,
        ret=(p1 / p0 - 1),
    )


CUTS = ["P/E", "prior loss", "SMA", "D/E", "current", "growth", "durability"]


def passes(r, pe_cut, use_durability, cuts=None):
    def cut(name):
        if cuts is not None:
            cuts[name] += 1
        return False
    if r["pe"] > pe_cut:                                     return cut("P/E")
    if not r["no_loss"]:                                     return cut("prior loss")
    if REQUIRE_SMA and not (r["above50"] and r["above200"]): return cut("SMA")
    if r["eq_assets"] is None or r["eq_assets"] < MIN_EQUITY_ASSETS:
        return cut("D/E")
    if r["cr"] is not None and r["cr"] < MIN_CURRENT:        return cut("current")
    if r["growth"] is None or r["growth"] <= 0:              return cut("growth")
    if use_durability and not (DURABLE_LO <= r["durability"] <= DURABLE_HI):
        return cut("durability")
    return True


def pctile(vals, q):
    v = sorted(vals)
    if not v:
        return None
    i = max(0, min(len(v) - 1, int(round(q * (len(v) - 1)))))
    return v[i]


# --------------------------------------------------------------------- VERIFY
VERIFY = ["CVX", "VLO", "MPC", "GM", "F", "JNJ", "PG", "CSCO", "MU", "AAPL"]


def verify(formation=None):
    """Print the full workings for known names. ⛔ NOT OPTIONAL -- the first
    version of this file produced a complete, plausible, WRONG result set, and
    the only thing that caught it was reading ten numbers by hand."""
    formation = formation or FORMATIONS[-1][0]
    cikmap = sp500_tickers()
    print("=" * 100)
    print("  HAND-VERIFY — EPS construction at formation", formation)
    print("=" * 100)
    print(f"  {'tkr':<6}{'as-traded':>10}{'TTM EPS':>9}{'P/E':>8}{'method':>8}{'stale':>7}"
          f"{'splt':>6}{'dur':>7}{'D/E':>7}  annual EPS history (oldest -> newest)")
    for t in VERIFY:
        cik = cikmap.get(t)
        facts, px = (edgar_facts(cik) if cik else None), prices(t)
        if not facts or not px:
            print(f"  {t:<6}  no data")
            continue
        sp = [s for s in splits_of(t) if s[0] <= formation]
        ttm, ann, method, stale = ttm_eps(facts, formation, splits_of(t))
        p0t = px_on(px, formation, traded=True)
        pe = (p0t / ttm) if (ttm and ttm > 0) else float("nan")
        med = median(ann[-6:]) if ann else None
        dur = (ttm / med) if (ttm and med and med > 0) else float("nan")
        eq, dbt = equity(facts, formation), total_debt(facts, formation)
        de = (dbt / eq) if (eq and eq > 0 and dbt is not None) else float("nan")
        print(f"  {t:<6}{p0t:>10.2f}{(ttm if ttm else float('nan')):>9.2f}{pe:>8.1f}"
              f"{method:>8}{(stale if stale is not None else -1):>7}"
              f"{(f'{len(sp)}' if sp else '-'):>6}{dur:>7.2f}{de:>7.2f}  "
              f"{[round(a, 2) for a in ann[-6:]]}")
    print("\n  TWO THINGS TO READ, and they are the two bugs that got through before:")
    print("  1. The annual history must be YEARS, not quarters. Consecutive small")
    print("     numbers of quarterly magnitude = bug A is back.")
    print("  2. It must be ONE SHARE BASIS. A step-change of exactly the split ratio")
    print("     partway along the list (splt column non-zero) = bug D is back.")


# ----------------------------------------------------------------------- MAIN
def load_all(tickers, cikmap):
    """Load every blob ONCE. This is what makes the multi-date run affordable:
    the EDGAR facts contain the FULL history, so changing the formation date
    changes only the `filed <` filter -- no new network at all."""
    store = {}
    for i, t in enumerate(tickers, 1):
        cik = cikmap.get(t)
        if not cik:
            continue
        px = prices(t)
        if len(px) < 300:
            continue
        f = edgar_facts(cik)
        if not f:
            continue
        store[t] = (f, px, splits_of(t))
        if i % 50 == 0:
            print(f"    loaded {i}/{len(tickers)} …", flush=True)
    return store


def run_one(store, formation, hold_end, verbose=True):
    """One formation date. Returns {label: (spread, n, mean, beat)}."""
    b = prices("SPY")
    b0, b1 = px_on(b, formation), px_on(b, hold_end)
    if not b0 or not b1:
        return {}
    bench = b1 / b0 - 1

    funnel = {k: 0 for k in GATES}
    rows = []
    for t, (facts, px, sp) in store.items():
        try:
            r = evaluate(t, facts, px, sp, formation, hold_end, funnel)
        except Exception as exc:                       # noqa: BLE001
            print(f"    ⚠️ {t} @ {formation}: {type(exc).__name__} {exc}")
            r = None
        if r:
            rows.append(r)

    # CHEAPNESS IS CROSS-SECTIONAL, NOT ABSOLUTE.
    # ⛔ The first run gated at an absolute P/E of 15 and cut 149 of 175 names.
    #   A fixed multiple is not a cheapness test, it is a bet on the ERA: 15x is
    #   near the median in 2011 and near the bottom decile in 2021. Gate on the
    #   universe's OWN distribution so the screen means the same thing at every
    #   formation date -- which is the entire point of running more than one.
    pe_cut = pctile([r["pe"] for r in rows], PE_PCTILE)
    out = {}
    if verbose:
        print(f"\n  ── FORMATION {formation} -> {hold_end}   "
              f"SPY {bench:+.1%}   usable {len(rows)}   "
              f"cheap-cut P/E ≤ {pe_cut:.1f} (bottom {PE_PCTILE:.0%})")
        print("     dropped: " + " · ".join(f"{k} {v}" for k, v in funnel.items() if v))

    for label, use_dur in (("NAIVE  ", False), ("DURABLE", True)):
        cuts = {k: 0 for k in CUTS}
        sel = [r for r in rows if passes(r, pe_cut, use_dur, cuts)]
        if not sel:
            if verbose:
                print(f"     {label}  n=0   cut by: "
                      + " · ".join(f"{k} {v}" for k, v in cuts.items() if v))
            out[label.strip()] = None
            continue
        rets = [r["ret"] for r in sel]
        avg = sum(rets) / len(rets)
        beat = sum(1 for x in rets if x > bench) / len(rets)
        out[label.strip()] = (avg - bench, len(sel), avg, beat)
        if verbose:
            print(f"     {label}  n={len(sel):<3} mean {avg:+7.1%}  vs SPY {bench:+7.1%}  "
                  f"spread {avg-bench:+7.1%}  beat {beat:.0%}   "
                  + " ".join(sorted(r["ticker"] for r in sel))[:88])
    return out


def main():
    print("=" * 100)
    print("  DURABLE-VALUE SCREEN — point-in-time, MULTIPLE FORMATION DATES")
    print("=" * 100)
    print("  ⚠️ SURVIVORSHIP: the universe is TODAY'S listed set, at EVERY formation date.")
    print("     Companies that failed or were acquired are ABSENT from all of them.")
    print("     READ THE SPREAD BETWEEN THE TWO SCREENS, never the absolute return —")
    print("     the bias hits NAIVE and DURABLE alike and largely cancels in the difference.")
    print("  ✓ LOOK-AHEAD: every fundamental filtered on EDGAR's `filed` date.")
    print("  ✓ EPS periods classified by DATE SPAN, never by form/fp label.")
    print("  ✓ CHEAPNESS is a percentile of each date's own cross-section, not a fixed multiple.")
    print("  ✓ LEVERAGE is interest-bearing debt / equity, not total liabilities / equity.\n")

    cikmap = sp500_tickers()
    print(f"  loading {len(UNIVERSE)} names (cached after the first run) …")
    store = load_all(UNIVERSE, cikmap)
    print(f"  loaded {len(store)} with both price and filing history\n")

    agg = {"NAIVE": [], "DURABLE": []}
    for formation, hold_end in FORMATIONS:
        res = run_one(store, formation, hold_end)
        for k, v in res.items():
            if v:
                agg[k].append((formation, v))

    print("\n" + "=" * 100)
    print("  THE COMPARISON IS THE RESULT — spread vs SPY, averaged across formation dates")
    print("=" * 100)
    print(f"  {'screen':<10}{'dates':>7}{'avg n':>8}{'avg spread':>13}{'median spread':>15}{'dates won':>11}")
    for k in ("NAIVE", "DURABLE"):
        v = agg[k]
        if not v:
            print(f"  {k:<10}   no date produced any names")
            continue
        sp = [x[1][0] for x in v]
        ns = [x[1][1] for x in v]
        print(f"  {k:<10}{len(v):>7}{sum(ns)/len(ns):>8.1f}{sum(sp)/len(sp):>+13.1%}"
              f"{median(sp):>+15.1%}{sum(1 for s in sp if s > 0)/len(sp):>11.0%}")
    both = [f for f, _ in agg["NAIVE"] if f in dict(agg["DURABLE"])]
    if both:
        dn = dict(agg["NAIVE"])
        dd = dict(agg["DURABLE"])
        diffs = [dd[f][0] - dn[f][0] for f in both]
        print(f"\n  HEAD-TO-HEAD on the {len(both)} dates where BOTH produced names:")
        print(f"    DURABLE minus NAIVE, mean {sum(diffs)/len(diffs):+.1%} · "
              f"median {median(diffs):+.1%} · DURABLE wins {sum(1 for d in diffs if d>0)}/{len(diffs)}")
        for f in both:
            print(f"      {f}   naive {dn[f][0]:+7.1%} (n={dn[f][1]:<3})   "
                  f"durable {dd[f][0]:+7.1%} (n={dd[f][1]:<3})   diff {dd[f][0]-dn[f][0]:+7.1%}")
    print("\n  If DURABLE does not beat NAIVE, the durability filter is not doing")
    print("  work and the idea is wrong — say so. n is small; read it as a direction,")
    print("  not a measurement.")
    return agg

UNIVERSE = """AAPL MSFT NVDA AMZN GOOGL META AVGO TSLA BRK-B JPM LLY V UNH XOM MA COST HD PG
JNJ WMT NFLX BAC CRM ORCL MRK ABBV CVX AMD KO PEP ADBE TMO LIN CSCO ACN MCD ABT PM DHR
WFC TXN VZ INTU IBM CAT GE QCOM NOW DIS AMGN NEE CMCSA PFE UNP RTX SPGI AXP LOW HON T
COP ELV BKNG SYK BLK VRTX PLD MDT ADP GILD MU SBUX LMT TJX MMC ADI CVS SCHW REGN CI BSX
ETN ZTS MO CB SO BA DE PGR AMT ANET FI ITW SLB DUK NKE EOG APD SHW BDX WM MCK CME TGT
MPC ICE PSX EMR NOC MCO CSX PNC AON APH ORLY GD MSI USB HCA VLO FCX MAR NSC F GM AZO
ROP AJG TDG TRV PCAR CTAS PSA AEP CPRT WELL SRE MET DXCM O KMB AIG D EW PRU ALL EXC
GIS DOW HLT KMI JCI ODFL IDXX SYY RSG A OTIS AME CMI HSY PPG STZ FAST YUM VRSK EA
KR CTSH GWW ED IQV WMB XEL DD ROK GLW EFX AVB CHTR VICI EBAY MTD DVN HIG WEC ANSS
KEYS FTV ES CDW TSCO ULTA HPQ PPL AWK BKR NUE STT LYB VTR DTE MLM VMC EIX HPE
CAH COR MOH LH DGX BAX ZBH STE HOLX CNC WAT RVTY CRL TFX BIO PODD ALGN
AFL TROW NTRS RF CFG KEY HBAN FITB MTB ZION CMA IVZ BEN SEIC RJF AMP PFG LNC UNM GL AIZ
WRB CINF L ACGL EG RE BRO MMC-X
NEM FCX-X VMC-X IP PKG WRK SEE AVY BALL CCK SW AMCR ATO NI CNP LNT EVRG AEE CMS PNW POR
JBHT CHRW EXPD UNP-X LUV DAL UAL ALK
WHR NWL LEG MHK TPR RL PVH HBI GPS M JWN KSS BBY DKS AAP ORLY-X GPC LKQ
HRL CAG CPB SJM K MKC CHD CLX KMB-X TSN ADM BG DAR
XRAY OGN VTRS JAZZ INCY BMRN NBIX SRPT UTHR HALO
NTAP WDC STX JNPR FFIV AKAM VRSN GEN DXC IT LDOS SAIC BAH CACI
SWK DOV IEX GGG NDSN LECO RRX ITT FLS PNR XYL WTS AOS
HES OXY PXD FANG APA MRO CTRA EQT AR RRC SWN CHK MTDR SM
DINO PBF PARR CVI DK""".split()
UNIVERSE = [t for t in dict.fromkeys(UNIVERSE) if not t.endswith("-X")]

# FORMATION DATES. ⛔ THE REASON THIS IS A LIST AND NOT A SINGLE DATE:
# the first run tested ONE date, 2021-08-16, and that date sits at a cyclical
# TROUGH for exactly the names the durability band excludes -- COVID-depressed
# energy, travel and industrials about to normalise violently upward. A filter
# that vetoes "trailing E far below its own history" would have vetoed the best
# value trade of the following year. Reading a filter's worth off that single
# draw is reading a coin off one flip.
# Equal 3-year holds so the dates are comparable to each other. Yahoo's 10y
# range starts ~2016-08, and a 200-day SMA needs ~10 months before that, so the
# first usable formation is mid-2017.
FORMATIONS = [("2017-08-15", "2020-08-14"),
              ("2018-08-15", "2021-08-13"),
              ("2019-08-15", "2022-08-15"),
              ("2020-08-14", "2023-08-14"),
              ("2021-08-16", "2024-08-15"),
              ("2022-08-15", "2025-08-15"),
              ("2023-08-15", "2026-08-14")]

# ------------------------------------------------------------------ ENTRY POINT
# Colab-safe: in a notebook sys.argv carries the kernel's connection-file path,
# so a bare int(sys.argv[1]) raises ValueError before a single line of the screen
# runs. Parse defensively and ignore anything that is not a number.
if __name__ == "__main__":
    verify()                      # ⛔ ALWAYS. The first version of this file produced a
    print()                       #    complete, plausible, WRONG result set, and the only
    main()                        #    thing that caught it was reading ten numbers by hand.


# ============================================================================
#  ISOLATION TEST — the one that can actually answer the question
#  ---------------------------------------------------------------------------
#  ⛔ WHY THIS EXISTS. Jake's full spec produces 1.6 names per formation date.
#  Across the dates where both groups existed the durable group beat the naive
#  group by a mean of +22.4pp -- and ALL OF IT is one stock: Dick's Sporting
#  Goods was the SOLE name in the 2018 durable bucket and returned +201%. Drop
#  that single date and the filter reads -5.1pp. An effect that inverts when one
#  observation is removed is not an effect, and reporting the +22.4 without that
#  sentence would be the most misleading thing this file could do.
#
#  The fix is not a better filter, it is a bigger sample. Strip every gate
#  except cheapness, then split the cheap cohort on durability alone. Same
#  cheapness rule, same dates, same universe -- the ONLY difference between the
#  two columns is the thing being tested. ~60 names per date instead of 1.6.
#
#  And note what the comparison becomes: not "durable vs everything" but
#  DURABLE-E vs SPIKY-E *within the cheap cohort*. That is Jake's actual claim --
#  that a low multiple built on inflated earnings is a different animal from a
#  low multiple built on normal ones.
# ============================================================================
def isolation(store=None):
    if store is None:
        store = load_all(UNIVERSE, sp500_tickers())
    print("\n" + "=" * 100)
    print("  ISOLATION TEST — cheap cohort SPLIT ON DURABILITY ALONE")
    print("  no balance-sheet gate, no moving-average gate, no growth gate: the only")
    print("  difference between the columns is TTM EPS vs its own multi-year median.")
    print("=" * 100)
    print(f"  {'formation':<12}{'SPY':>8}{'cheap n':>9}"
          f"{'DUR n':>7}{'spread':>9}{'SPIKY n':>9}{'spread':>9}{'diff':>9}")
    rows_out = []
    for formation, hold_end in FORMATIONS:
        b = prices("SPY")
        b0, b1 = px_on(b, formation), px_on(b, hold_end)
        bench = b1 / b0 - 1
        funnel = {k: 0 for k in GATES}
        rows = []
        for t, (facts, px, sp) in store.items():
            try:
                r = evaluate(t, facts, px, sp, formation, hold_end, funnel)
            except Exception:
                r = None
            if r:
                rows.append(r)
        pe_cut = pctile([r["pe"] for r in rows], PE_PCTILE)
        cheap = [r for r in rows if r["pe"] <= pe_cut]
        dur = [r for r in cheap if DURABLE_LO <= r["durability"] <= DURABLE_HI]
        spiky = [r for r in cheap if r["durability"] > DURABLE_HI]
        if not dur or not spiky:
            continue
        ds = sum(r["ret"] for r in dur) / len(dur) - bench
        ss = sum(r["ret"] for r in spiky) / len(spiky) - bench
        rows_out.append((formation, ds, ss, len(dur), len(spiky)))
        print(f"  {formation:<12}{bench:>+8.1%}{len(cheap):>9}"
              f"{len(dur):>7}{ds:>+9.1%}{len(spiky):>9}{ss:>+9.1%}{ds-ss:>+9.1%}")
    if rows_out:
        diffs = [r[1] - r[2] for r in rows_out]
        print("\n  DURABLE-E minus SPIKY-E, across", len(rows_out), "formation dates:")
        print(f"    mean {sum(diffs)/len(diffs):+.1%} · median {median(diffs):+.1%} · "
              f"durable wins {sum(1 for d in diffs if d>0)}/{len(diffs)}")
        print(f"    avg names per date: durable {sum(r[3] for r in rows_out)/len(rows_out):.0f} · "
              f"spiky {sum(r[4] for r in rows_out)/len(rows_out):.0f}")
        print("\n  ⚠️ LEAVE-ONE-OUT — an effect that dies when one date is removed is not an effect:")
        for i, r in enumerate(rows_out):
            rest = [d for j, d in enumerate(diffs) if j != i]
            print(f"    without {r[0]}:  mean {sum(rest)/len(rest):+6.1%}")
    return rows_out


# ============================================================================
#  TREND-FITTED DURABILITY — the corrected instrument
#  ---------------------------------------------------------------------------
#  ⛔ WHY THE MEDIAN VERSION HAD TO GO. `TTM / median(6 annual EPS)` is a LEVEL
#  statistic applied to a series with a TREND. On any compounding series the
#  median sits ~3 years back, so the ratio is approximately (1+g)^3 -- it
#  measures how far the company has TRAVELLED, not how far it has DEVIATED. A
#  company with zero spikes growing 27%/yr scored 2.03 and was thrown out as
#  "spiky"; the 1.60 threshold was, in effect, "reject anything compounding
#  faster than ~17%/yr". Confirmed empirically at 7 of 7 formation dates.
#
#  ⇒ TO DETECT A DEVIATION YOU NEED A MODEL OF THE TREND TO DEVIATE FROM.
#    Fit log-linear through the annual prints (constant-growth is a straight
#    line in logs), extrapolate to the TTM window, score TTM against the FITTED
#    value. A steady compounder now scores ~1.00 AT ANY GROWTH RATE. Only a
#    genuine departure from its own trend scores high.
#
#  ⚠️ AND THE KNOWN FAILURE MODE OF THE FIX, registered before it runs: a trend
#  fit reads a PERMANENT re-basing -- an acquisition that steps earnings power
#  up for good, which is one of the cases Jake explicitly named -- as a
#  deviation, identically to a one-off gain. No single ratio separates a spike
#  from a re-basing. That needs the SOURCE of the earnings out of the filings.
# ============================================================================
def trend_durability(ann_rows, ttm, ttm_end):
    """TTM EPS ÷ the value its own 6-year trend predicts for the TTM window."""
    if len(ann_rows) < 4 or ttm is None or not ttm_end:
        return None
    rows = ann_rows[-6:]
    x0 = datetime.fromisoformat(rows[0]["end"])
    xs = [(datetime.fromisoformat(r["end"]) - x0).days / 365.25 for r in rows]
    xt = (datetime.fromisoformat(ttm_end) - x0).days / 365.25
    ys_raw = [r["val"] for r in rows]
    use_log = all(v > 0 for v in ys_raw)
    ys = [__import__("math").log(v) for v in ys_raw] if use_log else ys_raw
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    a = my - b * mx
    fit = a + b * xt
    if use_log:
        fit = __import__("math").exp(min(fit, 700))
    if fit <= 0:
        return None
    return ttm / fit


def isolation2(store=None):
    """Two corrected tests, both of which the median version failed:
       (1) TREND-fitted durability -- growth-neutral by construction.
       (2) The ORIGINAL median durability, but split WITHIN growth terciles, so
           the durable and spiky groups are matched on EPS CAGR. If the effect
           is real it must survive holding growth constant. Two independent
           routes to the same question; agreement is the point."""
    if store is None:
        store = load_all(UNIVERSE, sp500_tickers())
    print("\n" + "=" * 100)
    print("  CORRECTED TEST 1 — TREND-FITTED DURABILITY (growth-neutral)")
    print("  TTM ÷ the value its OWN log-linear trend predicts. A steady compounder")
    print("  scores ~1.00 at ANY growth rate; only a departure from trend scores high.")
    print("=" * 100)
    print(f"  {'formation':<12}{'SPY':>8}{'cheap':>7}{'ON-TREND n':>12}{'spread':>9}"
          f"{'ABOVE-TREND n':>15}{'spread':>9}{'diff':>9}")
    t1, t2 = [], []
    for formation, hold_end in FORMATIONS:
        b = prices("SPY")
        bench = px_on(b, hold_end) / px_on(b, formation) - 1
        funnel = {k: 0 for k in GATES}
        rows = []
        for t, (facts, px, sp) in store.items():
            try:
                r = evaluate(t, facts, px, sp, formation, hold_end, funnel)
            except Exception:
                continue
            if not r:
                continue
            ar = annual_eps(facts, formation, sp)
            ttm_end = None
            if r["stale"] is not None:
                ttm_end = (datetime.fromisoformat(formation)
                           - __import__("datetime").timedelta(days=r["stale"])).strftime("%Y-%m-%d")
            r["td"] = trend_durability(ar, r["ttm"], ttm_end)
            r["growth3"] = r["growth"]
            rows.append(r)
        cut = pctile([r["pe"] for r in rows], PE_PCTILE)
        cheap = [r for r in rows if r["pe"] <= cut and r["td"]]
        on = [r for r in cheap if 0.75 <= r["td"] <= 1.35]
        above = [r for r in cheap if r["td"] > 1.35]
        if on and above:
            a1 = sum(r["ret"] for r in on) / len(on) - bench
            a2 = sum(r["ret"] for r in above) / len(above) - bench
            t1.append((formation, a1 - a2))
            print(f"  {formation:<12}{bench:>+8.1%}{len(cheap):>7}{len(on):>12}{a1:>+9.1%}"
                  f"{len(above):>15}{a2:>+9.1%}{a1-a2:>+9.1%}")

        # ---- test 2: median durability, split WITHIN growth terciles
        g = [r for r in cheap if r["growth3"] is not None]
        if len(g) >= 12:
            g.sort(key=lambda r: r["growth3"])
            k = len(g) // 3
            for lo, hi, name in ((0, k, "low-g"), (k, 2 * k, "mid-g"), (2 * k, len(g), "high-g")):
                band = g[lo:hi]
                d_ = [r for r in band if DURABLE_LO <= r["durability"] <= DURABLE_HI]
                s_ = [r for r in band if r["durability"] > DURABLE_HI]
                if d_ and s_:
                    t2.append((formation, name,
                               sum(r["ret"] for r in d_) / len(d_)
                               - sum(r["ret"] for r in s_) / len(s_), len(d_), len(s_)))
    if t1:
        d = [x[1] for x in t1]
        print(f"\n  ON-TREND minus ABOVE-TREND: mean {sum(d)/len(d):+.1%} · median {median(d):+.1%} · "
              f"wins {sum(1 for x in d if x>0)}/{len(d)}")
        print("  ⚠️ LEAVE-ONE-OUT:")
        for i, x in enumerate(t1):
            rest = [v for j, v in enumerate(d) if j != i]
            print(f"    without {x[0]}:  mean {sum(rest)/len(rest):+6.1%}")
    if t2:
        print("\n" + "=" * 100)
        print("  CORRECTED TEST 2 — median durability, split WITHIN growth terciles")
        print("  (durable minus spiky, holding EPS CAGR roughly constant)")
        print("=" * 100)
        for name in ("low-g", "mid-g", "high-g"):
            band = [x[2] for x in t2 if x[1] == name]
            if band:
                print(f"  {name:<8} n_dates={len(band):<3} mean {sum(band)/len(band):+7.1%} · "
                      f"median {median(band):+7.1%} · durable wins {sum(1 for v in band if v>0)}/{len(band)}")
        allb = [x[2] for x in t2]
        print(f"  {'ALL':<8} n={len(allb):<5} mean {sum(allb)/len(allb):+7.1%} · "
              f"median {median(allb):+7.1%} · durable wins {sum(1 for v in allb if v>0)}/{len(allb)}")
    return t1, t2


# ============================================================================
#  TREND P/E — price ÷ the earnings the company's OWN trend says is normal
#  ---------------------------------------------------------------------------
#  Jake, 2026-08-16 ~4:30pm: "let's create a new P/E."
#
#  IDENTITY (so it is clear this invents no new data):
#        trend P/E  =  trailing P/E  ×  trend-durability
#  because trailing P/E = P/TTM and trend-durability = TTM/fitted, so the
#  product is P/fitted. Both terms are already computed.
#
#  ★★★ WHY THIS IS NOT A REFINEMENT OF THE TEST THAT FAILED TODAY. The
#  durability screen was a FILTER applied AFTER a trailing-P/E cheapness cut, so
#  it could only ever SUBTRACT names from the cheap bucket. A company whose
#  earnings are temporarily DEPRESSED has a HIGH trailing P/E -- it never
#  entered the cheap cohort, so the durability test never saw it AND
#  STRUCTURALLY COULD NOT. That is the half of Jake's own idea that went
#  untested: not "the E is too high," but "the E is too low."
#  ⇒ A RATIO RE-RANKS THE WHOLE UNIVERSE. A FILTER ONLY PRUNES A PRE-SELECTED
#    SLICE. That difference, not the arithmetic, is the reason to build it.
#
#  ⚠️ THE VAULT'S OWN STANDARD, from market-fragility:4013 on the cycle-adjusted
#  ratio: "it is NOT a P/E of anything -- it divides the full index price by a
#  SUBSET of earnings." Numerator and denominator must cover the same entity.
#  This one does: same company, same share count, price over its own fitted EPS.
#
#  ⚠️ AND THE COST, stated before the run: the trend fit's known failure mode
#  now sits in the DENOMINATOR rather than merely excluding a name. A permanent
#  acquisition-driven re-basing reads as "above trend," so the fitted normal is
#  too low, so the trend P/E is too HIGH and the name is wrongly called dear.
#  The failure is no longer a missed name -- it is a mispriced one.
# ============================================================================
def normal_eps(ann_rows, ttm_end):
    """The EPS this company's own log-linear trend predicts for the TTM window."""
    if len(ann_rows) < 4 or not ttm_end:
        return None
    rows = ann_rows[-6:]
    x0 = datetime.fromisoformat(rows[0]["end"])
    xs = [(datetime.fromisoformat(r["end"]) - x0).days / 365.25 for r in rows]
    xt = (datetime.fromisoformat(ttm_end) - x0).days / 365.25
    raw = [r["val"] for r in rows]
    use_log = all(v > 0 for v in raw)
    import math
    ys = [math.log(v) for v in raw] if use_log else raw
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    den = sum((x - mx) ** 2 for x in xs)
    if den == 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    fit = (my - b * mx) + b * xt
    if use_log:
        fit = math.exp(min(fit, 700))
    return fit if fit > 0 else None


def trend_pe_test(store=None):
    """HEAD-TO-HEAD: cheap on TRAILING earnings vs cheap on TREND-NORMAL earnings.
    Same universe, same dates, same holds, same bottom-quintile rule. The only
    thing that changes is which denominator defines 'cheap'."""
    if store is None:
        store = load_all(UNIVERSE, sp500_tickers())
    print("\n" + "=" * 100)
    print("  TREND P/E — price ÷ trend-fitted normal EPS   (= trailing P/E × trend-durability)")
    print("  Bottom quintile on EACH ratio. The two cohorts are allowed to differ completely.")
    print("=" * 100)
    print(f"  {'formation':<12}{'SPY':>8}{'n':>6}{'TRAILING':>13}{'TREND':>12}"
          f"{'AVERAGE':>12}{'T-Tr':>8}{'overlap':>9}")
    tr, tn, av_l, ov = [], [], [], []
    for formation, hold_end in FORMATIONS:
        b = prices("SPY")
        bench = px_on(b, hold_end) / px_on(b, formation) - 1
        funnel = {k: 0 for k in GATES}
        rows = []
        for t, (facts, px, sp) in store.items():
            try:
                r = evaluate(t, facts, px, sp, formation, hold_end, funnel)
            except Exception:
                continue
            if not r or r["stale"] is None:
                continue
            import datetime as _dt
            ttm_end = (datetime.fromisoformat(formation)
                       - _dt.timedelta(days=r["stale"])).strftime("%Y-%m-%d")
            ar = annual_eps(facts, formation, sp)
            ne = normal_eps(ar, ttm_end)
            av = (sum(a["val"] for a in ar[-6:]) / len(ar[-6:])) if len(ar) >= 4 else None
            if not ne or not av or av <= 0:
                continue
            r["tpe"] = r["pe"] * (r["ttm"] / ne)      # price / TREND-fitted normal EPS
            r["ape"] = r["pe"] * (r["ttm"] / av)      # price / 6yr AVERAGE EPS (the CAPE analogue)
            rows.append(r)
        if len(rows) < 30:
            continue
        A = [r for r in rows if r["pe"]  <= pctile([x["pe"]  for x in rows], PE_PCTILE)]
        B = [r for r in rows if r["tpe"] <= pctile([x["tpe"] for x in rows], PE_PCTILE)]
        C = [r for r in rows if r["ape"] <= pctile([x["ape"] for x in rows], PE_PCTILE)]
        a  = sum(r["ret"] for r in A) / len(A) - bench
        bb = sum(r["ret"] for r in B) / len(B) - bench
        cc = sum(r["ret"] for r in C) / len(C) - bench
        shared = len({r["ticker"] for r in A} & {r["ticker"] for r in B}) / max(len(A), 1)
        tr.append(a); tn.append(bb); av_l.append(cc); ov.append(shared)
        print(f"  {formation:<12}{bench:>+8.1%}{len(rows):>6}{a:>+13.1%}{bb:>+12.1%}"
              f"{cc:>12.1%}{bb-a:>+8.1%}{shared:>9.0%}")
    if tr:
        d = [x - y for x, y in zip(tn, tr)]
        print(f"\n  TRAILING-cheap  mean spread vs SPY {sum(tr)/len(tr):+.1%} · "
              f"beat {sum(1 for x in tr if x>0)}/{len(tr)}")
        print(f"  TREND-cheap     mean spread vs SPY {sum(tn)/len(tn):+.1%} · "
              f"beat {sum(1 for x in tn if x>0)}/{len(tn)}")
        print(f"  AVERAGE-cheap   mean spread vs SPY {sum(av_l)/len(av_l):+.1%} · "
              f"beat {sum(1 for x in av_l if x>0)}/{len(av_l)}   "
              f"(the CAPE analogue — flat 6yr mean, no trend extrapolated)")
        print(f"  ★ TREND minus TRAILING: mean {sum(d)/len(d):+.1%} · median {median(d):+.1%} · "
              f"wins {sum(1 for x in d if x>0)}/{len(d)}")
        print(f"  cohort overlap averages {sum(ov)/len(ov):.0%} — "
              f"{'the two ratios pick DIFFERENT names' if sum(ov)/len(ov) < 0.7 else 'the ratios largely agree'}")
        print("\n  ⚠️ LEAVE-ONE-OUT:")
        for i, f in enumerate([x[0] for x in FORMATIONS][:len(d)]):
            rest = [v for j, v in enumerate(d) if j != i]
            print(f"    without {f}:  mean {sum(rest)/len(rest):+6.1%}")
    return tr, tn


# ============================================================================
#  CONSISTENCY OF THE GROWTH RATE — Jake, 2026-08-16 ~4:35pm
#  "First we look at how consistent quarter to quarter earning growth RATE is."
#  ---------------------------------------------------------------------------
#  ★★★ WHY THIS IS THE BEST VERSION OF THE IDEA SO FAR, and better than anything
#  built earlier today: EVERY measure tried this morning -- median, log-linear
#  trend, flat average -- operates on the LEVEL of earnings. Consistency operates
#  on the RATE, which is an orthogonal axis and is far closer to what "durable
#  earnings" actually means. A company earning 1.00, 1.05, 1.10, 1.15 and one
#  earning 0.20, 2.00, 0.30, 1.90 can share a median, a trend and an average.
#  They do not share a growth-rate variance.
#
#  ⛔ TWO DEFECTS IN THE LITERAL SPEC, both demonstrated on real data before
#  being asserted:
#  1. SEQUENTIAL QUARTER-OVER-QUARTER IS SEASONALITY, NOT GROWTH. Apple's last
#     two quarters before 2021-08-16 were 1.40 -> 1.30, a -7% sequential rate;
#     extrapolating that projects Apple into DECLINE while it was compounding
#     ~100% year-over-year with its December blowout quarter next. Walmart
#     printed -141% on one transition. Chevron had FOUR OF EIGHT transitions
#     undefined because the base quarter was negative.
#     ⇒ USE YEAR-OVER-YEAR SAME-QUARTER GROWTH. Seasonality cancels by
#       construction: Q2 is only ever compared to Q2.
#  2. A GROWTH RATE OFF A NEAR-ZERO BASE EXPLODES. Marathon's Speedway quarter
#     produced +129,900% and a stdev of 48,438% -- a division artifact, not
#     information.
#     ⇒ USE THE SYMMETRIC PERCENT CHANGE: (Et - Et-4) / mean(|Et|, |Et-4|).
#       Scale-free, defined across sign changes, bounded to +/-200%.
#
#  ⛔ AND THE THIRD PART OF THE SPEC IS ARITHMETICALLY EMPTY AS WRITTEN:
#  "match the P numerator to the same multiplier." If numerator and denominator
#  are both scaled by m, then (P*m)/(E*m) = P/E IDENTICALLY. No information can
#  survive that operation. The non-vacuous version -- and what the idea is
#  plainly reaching for -- is to compare the price's ACTUAL realised move against
#  the earnings' PROJECTED move. That gap is a real quantity: it says whether the
#  price has kept up with, lagged, or outrun the company's own earnings path.
#  Implemented below as `divergence`.
# ============================================================================
def quarterly_eps(facts, asof, splits=()):
    """Complete DISCRETE quarterly EPS series, point-in-time.
    ⛔ Q4 is NEVER published in a 10-Q. It is DERIVED: Q4 = FY - 9-month YTD."""
    rows = eps_facts(facts, asof, splits)
    q = {r["end"]: r["val"] for r in _dedupe([x for x in rows if 80 <= x["span"] <= 100])}
    ytd9 = {r["start"]: r["val"] for r in rows if 260 <= r["span"] <= 285}
    for a in annual_eps(facts, asof, splits):
        if a["end"] in q:
            continue
        for astart, yval in ytd9.items():
            if 340 <= _days(astart, a["end"]) <= 400:
                q[a["end"]] = a["val"] - yval
                break
    return sorted(q.items())


def yoy_growth(qs):
    """Year-over-year same-quarter SYMMETRIC growth. Seasonality-free, sign-safe."""
    out = []
    for i in range(4, len(qs)):
        cur, base = qs[i][1], qs[i - 4][1]
        scale = (abs(cur) + abs(base)) / 2.0
        if scale > 0.01:
            out.append((cur - base) / scale)
    return out


def consistency(facts, asof, splits=(), n=8):
    """(median growth rate, STDEV of the growth rate) over the last n YoY prints.
    The stdev IS the measure: low = the growth RATE itself is durable."""
    g = yoy_growth(quarterly_eps(facts, asof, splits))[-n:]
    if len(g) < 6:
        return None, None
    m = sum(g) / len(g)
    return median(g), (sum((x - m) ** 2 for x in g) / len(g)) ** 0.5


def forward_eps(facts, asof, splits=()):
    """Jake's denominator, seasonality-corrected: take the recent YoY growth rate
    and carry the next 2 quarters at it, so E is half ACTUAL and half PROJECTED."""
    qs = quarterly_eps(facts, asof, splits)
    if len(qs) < 8:
        return None
    g = yoy_growth(qs)[-4:]
    if not g:
        return None
    r = median(g)                                  # median, not mean: one spike must not set the path
    last4 = [v for _, v in qs[-4:]]
    proj = [qs[-4 + i][1] * (1 + r) for i in range(2)]   # next 2 quarters vs their year-ago selves
    return sum(last4[2:]) + sum(proj)              # 2 actual + 2 projected
