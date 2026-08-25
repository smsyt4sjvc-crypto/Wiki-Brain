#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════════════════
#  BASKET INDEX — chart a basket of holdings as if it were ONE ETF
#  Jake's spec 2026-08-11: "a chart for these baskets as if it's an etf or singular chart."
#
#  Source: two "Basket details" screenshots per basket (paste-time 2026-08-11 ~7:50am PDT).
#  Each holding carries CURRENT % (what it has drifted to) and TARGET % (the policy weight).
#  Both baskets' CURRENT weights sum to 100.0 → the screenshots captured every holding.
#
#  WHAT IT DOES
#    1. Prints the DRIFT table (current vs target) — needs NO market data, so it works even
#       if the fetch fails. The drift IS information: it says what has run and what has lagged.
#    2. Fetches daily adjusted closes, builds each basket into a single index series, and
#       charts it against SOXX / SPY / QQQ.
#    3. Handles the IPO problem honestly: names with no history yet (CRWV Mar-2025,
#       NBIS, ALAB, ARM...) are EXCLUDED on dates before they list and the remaining weights
#       are renormalised — with a COVERAGE panel underneath showing what fraction of the
#       basket is actually live on each date. No silent truncation.
#
#  COMPLETE CELL — paste the whole thing into Colab and run. Edit only the CONFIG block.
# ═══════════════════════════════════════════════════════════════════════════════════════════
try:
    import yfinance  # noqa: F401
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yfinance"], check=False)

import io, warnings, urllib.request
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

warnings.filterwarnings("ignore")

# ═══════════════════════ CONFIG — the only lines you need to touch ═════════════════════════
START     = "2023-01-01"   # history start. "2021-01-01" for more; earlier = more names missing
WEIGHTS   = "target"       # "target" = the policy weights (what the basket rebalances TO)
                           # "current" = today's drifted weights
REBAL     = "M"            # "M" monthly · "Q" quarterly · "W" weekly · None = buy-and-hold drift
BENCH     = ["SOXX", "SPY", "QQQ"]
LOG_SCALE = False          # True if the range gets too wide to read
# ═══════════════════════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────────────────────
#  THE BASKETS.  ticker: (current %, target %)
#  Read off the 2026-08-11 screenshots. ⚠️ MTSI's target was cut off by the screen edge —
#  1.10 is DERIVED as the residual (the other 23 targets sum to 98.90). Flagged, not read.
# ───────────────────────────────────────────────────────────────────────────────────────────
BASKETS = {
    "BASKET 1 — semis / hardware": {
        "NVDA": (8.36, 7.80), "MU":   (7.65, 8.00), "AVGO": (7.35, 7.10), "AMD":  (7.32, 8.00),
        "DELL": (5.87, 6.00), "INTC": (5.77, 5.70), "AMAT": (5.10, 5.20), "KLAC": (4.93, 4.70),
        "MRVL": (4.59, 4.60), "TSM":  (4.48, 4.40), "LRCX": (4.34, 4.30), "TXN":  (4.06, 4.00),
        "ADI":  (3.99, 3.80), "NXPI": (3.67, 3.60), "MPWR": (3.14, 3.20), "QCOM": (3.10, 3.00),
        "TER":  (2.63, 2.80), "ALAB": (2.48, 2.80), "MCHP": (2.43, 2.30), "CRDO": (2.31, 2.20),
        "ASML": (2.00, 2.30), "ON":   (1.93, 1.90), "ASX":  (1.25, 1.20), "MTSI": (1.24, 1.10),
    },
    "BASKET 2 — AI buildout, full stack": {
        "NVDA": (7.12, 7.00), "ORCL": (5.13, 5.00), "QRVO": (5.00, 5.00), "AVGO": (5.00, 5.00),
        "INTC": (4.98, 5.00), "TSM":  (4.90, 5.00), "CRWV": (4.86, 4.50), "TXN":  (4.85, 5.00),
        "COHR": (4.82, 4.50), "AMAT": (4.79, 5.00), "AMD":  (4.66, 5.00), "RNW":  (4.60, 4.50),
        "IREN": (4.54, 4.50), "EWY":  (4.44, 4.50), "RIVN": (4.44, 4.50), "MU":   (4.31, 4.50),
        "NBIS": (4.30, 4.50), "LITE": (4.07, 4.00), "LRCX": (3.88, 4.00), "MP":   (3.37, 3.00),
        "SWKS": (2.02, 2.00), "ARM":  (2.00, 2.00), "GFS":  (1.93, 2.00),
    },
}
DERIVED = {("BASKET 1 — semis / hardware", "MTSI")}   # target not legible; residual-derived

COLORS = {"BASKET 1 — semis / hardware": "#2563eb", "BASKET 2 — AI buildout, full stack": "#dc2626"}
BCOLORS = {"SOXX": "#6b7280", "SPY": "#9ca3af", "QQQ": "#a78bfa"}

# ═══════════════════════════ 1. DRIFT TABLE (no market data needed) ═════════════════════════
print("=" * 92)
print("  CURRENT vs TARGET — the drift already tells you what has run and what has lagged")
print("=" * 92)
for bname, holdings in BASKETS.items():
    cur = pd.Series({k: v[0] for k, v in holdings.items()})
    tgt = pd.Series({k: v[1] for k, v in holdings.items()})
    d = (cur - tgt).sort_values(ascending=False)
    print(f"\n── {bname}   ({len(holdings)} names · current sums {cur.sum():.2f}% · "
          f"target sums {tgt.sum():.2f}%)")
    print(f"   {'ticker':<8}{'current':>9}{'target':>9}{'drift':>9}   {'':<3}")
    for t in d.index:
        flag = "  ⚠️ target derived" if (bname, t) in DERIVED else ""
        bar = "█" * int(min(abs(d[t]) / 0.1, 12))
        side = "over" if d[t] > 0 else ("under" if d[t] < 0 else "flat")
        print(f"   {t:<8}{cur[t]:>8.2f}%{tgt[t]:>8.2f}%{d[t]:>+8.2f}%   {bar:<12} {side}{flag}")
    print(f"   ⇒ largest overweight vs policy: {d.index[0]} {d.iloc[0]:+.2f}%  ·  "
          f"largest underweight: {d.index[-1]} {d.iloc[-1]:+.2f}%")
    print(f"   ⇒ total absolute drift: {d.abs().sum():.2f}% "
          f"(one-way turnover to snap back ≈ {d.abs().sum()/2:.2f}%)")

# ═══════════════════════════════════ 2. PRICE FETCH ═════════════════════════════════════════
ALL = sorted({t for h in BASKETS.values() for t in h} | set(BENCH))
print("\n" + "=" * 92)
print(f"  FETCHING {len(ALL)} tickers from {START} …")
print("=" * 92)

def fetch_yf(tickers, start):
    import yfinance as yf
    df = yf.download(tickers, start=start, auto_adjust=True, progress=False,
                     group_by="column", threads=True)
    if isinstance(df.columns, pd.MultiIndex):
        df = df["Close"]
    return df.dropna(how="all")

def fetch_stooq(ticker, start):
    """Fallback, one ticker at a time. Stooq serves US equities as <sym>.us."""
    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode()
    if "Date" not in raw[:64]:
        raise ValueError("no data")
    s = pd.read_csv(io.StringIO(raw), parse_dates=["Date"]).set_index("Date")["Close"]
    return s[s.index >= pd.Timestamp(start)]

px = pd.DataFrame()
try:
    px = fetch_yf(ALL, START)
    print(f"  yfinance OK — {px.shape[1]} series, {px.shape[0]} rows")
except Exception as e:
    print(f"  !! yfinance failed ({e}) — falling back to stooq, one ticker at a time")

missing = [t for t in ALL if t not in px.columns or px[t].dropna().empty]
if missing:
    print(f"  filling {len(missing)} via stooq: {', '.join(missing)}")
    for t in missing:
        try:
            px[t] = fetch_stooq(t, START)
        except Exception as e:
            print(f"     ✗ {t}: {e}")

px = px.reindex(columns=[c for c in ALL if c in px.columns]).sort_index()
px = px[~px.index.duplicated(keep="last")]
dead = [c for c in px.columns if px[c].dropna().empty]
if dead:
    print(f"  ⚠️ NO DATA AT ALL for: {', '.join(dead)} — dropped, weights renormalised")
    px = px.drop(columns=dead)
px = px.ffill()          # once a name starts, carry it over holidays/gaps

print(f"\n  first date per name (blank history = listed later than {START}):")
firsts = px.apply(lambda c: c.first_valid_index())
late = firsts[firsts > firsts.min() + pd.Timedelta(days=5)].sort_values()
if len(late):
    for t, d0 in late.items():
        print(f"     {t:<6} first close {d0.date()}")
else:
    print("     all names have history back to the start date")

# ══════════════════════════════════ 3. INDEX CONSTRUCTION ═══════════════════════════════════
def build_index(prices, weights, rebal="M"):
    """Basket → one series, normalised to 100. Names not yet listed are excluded and the
    remaining weights renormalised on each rebalance. Returns (index, coverage_fraction)."""
    cols = [c for c in weights.index if c in prices.columns]
    p = prices[cols].copy()
    w0 = weights[cols] / weights[cols].sum()
    live = p.notna()
    rets = p.pct_change().fillna(0.0)

    if rebal:
        per = p.index.to_period(rebal)
        rb = set(pd.Series(p.index, index=per).groupby(level=0).first().values)
    else:
        rb = {p.index[0]}
    rb.add(p.index[0])

    vals, lvl, cov = None, [], []
    for d in p.index:
        mask = live.loc[d]
        wl = (w0 * mask)
        s = wl.sum()
        if s <= 0:                       # nothing listed yet
            lvl.append(np.nan); cov.append(0.0); continue
        if vals is None:
            vals = wl / s
        else:
            # ORDER MATTERS: mark to market FIRST, then rebalance at the new total.
            # Rebalancing before applying the day's return silently drops that day —
            # ~24 lost days/yr on a monthly schedule (caught by the flat-growth unit test,
            # where a rebalance must be a no-op and any drift from exact is the bug).
            vals = vals * (1.0 + rets.loc[d])
            if d in rb:
                vals = wl / s * vals.sum()
        lvl.append(vals.sum()); cov.append(float(s))

    idx = pd.Series(lvl, index=p.index).dropna()
    idx = idx / idx.iloc[0] * 100.0
    return idx, pd.Series(cov, index=p.index).reindex(idx.index)

def stats(idx, bench=None):
    r = idx.pct_change().dropna()
    yrs = (idx.index[-1] - idx.index[0]).days / 365.25
    tot = idx.iloc[-1] / idx.iloc[0] - 1
    cagr = (idx.iloc[-1] / idx.iloc[0]) ** (1 / yrs) - 1 if yrs > 0 else np.nan
    vol = r.std() * np.sqrt(252)
    dd = (idx / idx.cummax() - 1).min()
    out = {"total": tot, "cagr": cagr, "vol": vol, "ret/vol": cagr / vol if vol else np.nan,
           "maxDD": dd, "best": r.max(), "worst": r.min()}
    if bench is not None:
        b = bench.pct_change().reindex(r.index).dropna()
        rr = r.reindex(b.index)
        out["beta"] = float(np.cov(rr, b)[0, 1] / np.var(b)) if len(b) > 20 else np.nan
    return out

wkey = 0 if WEIGHTS == "current" else 1
series, covers = {}, {}
for bname, holdings in BASKETS.items():
    w = pd.Series({k: v[wkey] for k, v in holdings.items()})
    series[bname], covers[bname] = build_index(px, w, REBAL)

bench_px = {b: px[b].dropna() for b in BENCH if b in px.columns}
bench_ix = {b: s / s.iloc[0] * 100.0 for b, s in bench_px.items()}
spy = bench_px.get("SPY")

print("\n" + "=" * 92)
print(f"  PERFORMANCE — {WEIGHTS.upper()} weights, "
      f"{'buy-and-hold (no rebalance)' if not REBAL else f'rebalanced {REBAL}'}, "
      f"{series[list(series)[0]].index[0].date()} → {series[list(series)[0]].index[-1].date()}")
print("=" * 92)
hdr = f"  {'':<38}{'total':>9}{'CAGR':>9}{'vol':>8}{'ret/vol':>9}{'maxDD':>9}{'beta':>7}"
print(hdr); print("  " + "─" * 88)
rows = list(series.items()) + [(f"[bench] {b}", s) for b, s in bench_ix.items()]
for nm, s in rows:
    st = stats(s, spy)
    print(f"  {nm:<38}{st['total']:>8.1%}{st['cagr']:>9.1%}{st['vol']:>8.1%}"
          f"{st['ret/vol']:>9.2f}{st['maxDD']:>9.1%}{st.get('beta', np.nan):>7.2f}")

# ═════════════════════════════════ 4. PER-NAME CONTRIBUTION ═════════════════════════════════
print("\n" + "=" * 92)
print("  PER-NAME: total return over the window × policy weight")
print("  ⚠️ APPROXIMATE for a rebalanced index — it is the static-weight decomposition, so it")
print("     will not sum exactly to the basket return. Read the ORDERING, not the decimals.")
print("=" * 92)
for bname, holdings in BASKETS.items():
    w = pd.Series({k: v[wkey] for k, v in holdings.items()})
    cols = [c for c in w.index if c in px.columns]
    w = w[cols] / w[cols].sum()
    idx0 = series[bname].index[0]
    tr = {}
    for t in cols:
        s = px[t].dropna()
        s = s[s.index >= idx0]
        if len(s) > 1:
            tr[t] = s.iloc[-1] / s.iloc[0] - 1
    tr = pd.Series(tr)
    contrib = (w[tr.index] * tr).sort_values(ascending=False)
    print(f"\n── {bname}")
    print(f"   {'ticker':<8}{'weight':>8}{'return':>10}{'contrib':>10}   {'from':<12}")
    for t in contrib.index:
        s0 = px[t].dropna()
        s0 = s0[s0.index >= idx0]
        late_tag = str(s0.index[0].date()) if s0.index[0] > idx0 + pd.Timedelta(days=5) else ""
        print(f"   {t:<8}{w[t]:>7.1%}{tr[t]:>10.1%}{contrib[t]:>10.1%}   {late_tag:<12}")
    print(f"   Σ static-weight contribution: {contrib.sum():+.1%}   "
          f"(basket actual: {series[bname].iloc[-1]/100-1:+.1%})")

# ═══════════════════════════════════════ 5. CHARTS ══════════════════════════════════════════
plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.25,
                     "axes.spines.top": False, "axes.spines.right": False})

fig = plt.figure(figsize=(12, 8.5), dpi=110)
gs = fig.add_gridspec(3, 1, height_ratios=[3.0, 0.85, 1.5], hspace=0.32)

ax = fig.add_subplot(gs[0])
for bname, s in series.items():
    ax.plot(s.index, s.values, lw=2.6, color=COLORS[bname],
            label=f"{bname}  ({s.iloc[-1]/100-1:+.0%})")
for b, s in bench_ix.items():
    ax.plot(s.index, s.values, lw=1.3, ls="--", color=BCOLORS.get(b, "#999"),
            label=f"{b}  ({s.iloc[-1]/100-1:+.0%})")
ax.axhline(100, color="#111", lw=0.8, alpha=0.5)
if LOG_SCALE:
    ax.set_yscale("log")
ax.set_title(f"Each basket as ONE index — {WEIGHTS} weights, "
             f"{'buy & hold' if not REBAL else f'{REBAL} rebalance'}   (start = 100)",
             fontsize=13, weight="bold", loc="left")
ax.set_ylabel("index (start = 100)")
ax.legend(frameon=False, fontsize=9.5, loc="upper left")

axc = fig.add_subplot(gs[1], sharex=ax)
for bname, c in covers.items():
    axc.plot(c.index, c.values * 100, lw=1.8, color=COLORS[bname])
axc.set_ylim(0, 105)
axc.yaxis.set_major_formatter(mtick.PercentFormatter())
axc.set_ylabel("coverage", fontsize=9.5)
axc.set_title("share of basket weight actually listed on each date "
              "— below 100% the index is a renormalised SUBSET",
              fontsize=9.5, loc="left", color="#666")

axd = fig.add_subplot(gs[2], sharex=ax)
for bname, s in series.items():
    dd = (s / s.cummax() - 1) * 100
    axd.plot(dd.index, dd.values, lw=1.9, color=COLORS[bname])
    axd.fill_between(dd.index, dd.values, 0, color=COLORS[bname], alpha=0.12)
for b, s in bench_ix.items():
    if b == "SOXX":
        dd = (s / s.cummax() - 1) * 100
        axd.plot(dd.index, dd.values, lw=1.1, ls="--", color="#6b7280", label="SOXX")
        axd.legend(frameon=False, fontsize=9)
axd.yaxis.set_major_formatter(mtick.PercentFormatter())
axd.set_ylabel("drawdown")
axd.set_title("drawdown from running peak", fontsize=9.5, loc="left", color="#666")
plt.show()

# relative strength — the pair trade view
fig2, axr = plt.subplots(2, 1, figsize=(12, 6.2), dpi=110, sharex=True)
names = list(series)
if "SOXX" in bench_ix:
    for bname in names:
        rel = (series[bname] / bench_ix["SOXX"].reindex(series[bname].index).ffill())
        rel = rel / rel.iloc[0] * 100
        axr[0].plot(rel.index, rel.values, lw=2.2, color=COLORS[bname], label=bname)
    axr[0].axhline(100, color="#111", lw=0.8, alpha=0.5)
    axr[0].set_title("each basket RELATIVE to SOXX (rising = beating the sector)",
                     fontsize=11.5, weight="bold", loc="left")
    axr[0].legend(frameon=False, fontsize=9.5)
    axr[0].set_ylabel("ratio (start = 100)")
if len(names) == 2:
    a, b = series[names[0]], series[names[1]]
    common = a.index.intersection(b.index)
    ratio = (a[common] / b[common]); ratio = ratio / ratio.iloc[0] * 100
    axr[1].plot(ratio.index, ratio.values, lw=2.2, color="#059669")
    axr[1].axhline(100, color="#111", lw=0.8, alpha=0.5)
    axr[1].set_title(f"{names[0]}  ÷  {names[1]}   "
                     f"(rising = semis basket beating the buildout basket)",
                     fontsize=11.5, weight="bold", loc="left")
    axr[1].set_ylabel("ratio (start = 100)")
plt.tight_layout(); plt.show()

print("\n" + "=" * 92)
print("  READING NOTES")
print("  · COVERAGE is the honest part. Basket 2 holds CRWV (listed 2025) and NBIS — before")
print("    those dates the red line is a SUBSET of the basket, not the basket. Any comparison")
print("    that spans a coverage step is comparing two different portfolios.")
print("  · Rebalancing is an assumption, not an observation. The screenshots show CURRENT vs")
print("    TARGET, i.e. the basket HAS drifted — so the true history sits between REBAL='M'")
print("    and REBAL=None. Run it both ways; the gap is the rebalancing effect.")
print("  · This is a price index. No dividends beyond what auto-adjust captures, no fees,")
print("    no slippage, no tax. It is not a statement about what the account actually did.")
print("=" * 92)
