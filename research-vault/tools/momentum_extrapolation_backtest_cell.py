#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════════════
#  MOMENTUM-EXTRAPOLATION OPTION BACKTEST — Jake's spec, 2026-08-09:
#    "Take a rolling, trailing 3 month S&P return and extrapolate it forward 3 months.
#     If it's down buy a put so that the breakeven is the extrapolated number. Same for
#     a call if it's up. Straight line out 3 months as if that's where the S&P will be.
#     If it is, we break even. If it surpasses, make money. Roll forward a month at a
#     time. Start at the beginning of the dotcom boom."
#
#  THE CONSTRUCTION'S OWN ELEGANCE (falls out of the algebra, worth knowing going in):
#    breakeven is pinned AT the extrapolated target T, so
#      · HIT RATE  = P(index lands BEYOND its own trailing-trend line) — option-free truth
#        value of the momentum theory; identical under any volatility assumption.
#      · $ P&L per trade = (S_expiry − T) in the trade's direction, FLOORED at −premium.
#        The strategy is long (realized − extrapolated) with a paid-for floor.
#
#  DATA (all free, no keys; works in Colab AND any box with outbound HTTPS):
#    · SPX daily closes 1975→   CBOE   cdn.cboe.com SPX_History.csv   (primary source)
#    · VIX daily 1990→          FRED   VIXCLS
#    · 3-mo T-bill              FRED   DTB3
#  Pricing: Black-Scholes European w/ dividend yield (SPX-style). Two vol bases run in
#  one pass: [A] VIX at entry (market-priced vol incl. premium)  [B] trailing 63-day
#  realized (no vol premium — the cheap-options upper bound). Strike SOLVED per trade
#  so breakeven = target exactly. COMPLETE CELL — paste whole into Colab and run.
# ═══════════════════════════════════════════════════════════════════════════════════════
import io, os, math, urllib.request, ssl
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm
from scipy.optimize import brentq

# ── PARAMETERS ─────────────────────────────────────────────────────────────────────────
START_TRADES = "1995-01-01"   # "beginning of the dotcom boom" (S&P's 1995 melt-up year)
ROLL         = "MS"           # enter first trading day of each month
LOOKBACK_M   = 3              # trailing window, calendar months
HORIZON_M    = 3              # option tenor, calendar months
DIV_YLD      = 0.018          # flat S&P dividend yield for pricing (caveat printed)
VOL_ADJ_GRID = (0.85, 1.00, 1.15)   # sensitivity multipliers on VIX pricing vol
VOL_FLOOR    = 0.05
ERAS = [("BOOM 95-00","1994-12-15","2000-03-31"), ("BUST 00-02","2000-04-01","2002-09-30"),
        ("EXPANSION 02-07","2002-10-01","2007-09-30"), ("GFC 07-09","2007-10-01","2009-02-28"),
        ("QE BULL 09-19","2009-03-01","2019-12-31"), ("COVID 20-21","2020-01-01","2021-12-31"),
        ("BEAR 2022","2022-01-01","2022-12-31"), ("AI ERA 23-26","2023-01-01","2026-12-31")]

def fetch(url, fname):
    if os.path.exists(fname) and os.path.getsize(fname) > 1000:
        return open(fname, "rb").read()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        raw = urllib.request.urlopen(req, timeout=60).read()
    except ssl.SSLError:
        raw = urllib.request.urlopen(req, timeout=60,
                                     context=ssl._create_unverified_context()).read()
    open(fname, "wb").write(raw)
    return raw

def fred(series, fname):
    raw = fetch(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}", fname)
    df = pd.read_csv(io.BytesIO(raw))
    df.columns = ["date", "v"]
    df["date"] = pd.to_datetime(df["date"])
    df["v"] = pd.to_numeric(df["v"], errors="coerce")
    return df.set_index("date")["v"]

# ── LOAD ───────────────────────────────────────────────────────────────────────────────
spx_raw = fetch("https://cdn.cboe.com/api/global/us_indices/daily_prices/SPX_History.csv",
                "spx_cboe.csv")
spx = pd.read_csv(io.BytesIO(spx_raw))
spx.columns = [c.strip().lower() for c in spx.columns]
spx["date"] = pd.to_datetime(spx["date"], format="%m/%d/%Y")
px = spx.set_index("date")["spx"].astype(float).sort_index()
vix = fred("VIXCLS", "vixcls.csv")
rf  = fred("DTB3", "dtb3.csv")

D = pd.DataFrame({"px": px})
D["vix"] = vix.reindex(D.index).ffill() / 100.0
D["rf"]  = rf.reindex(D.index).ffill() / 100.0
D["rvol"] = np.log(D["px"]).diff().rolling(63).std() * math.sqrt(252)
idx = D.index

def nearest(ts):
    i = idx.searchsorted(ts)
    if i >= len(idx): return None
    if i > 0 and abs((idx[i-1] - ts).days) <= abs((idx[i] - ts).days): i -= 1
    return idx[i]

# ── PRICING + STRIKE SOLVER (breakeven pinned at target) ───────────────────────────────
def bs(S, K, T, r, q, sig, kind):
    sig = max(sig, VOL_FLOOR); srt = sig * math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sig * sig) * T) / srt
    d2 = d1 - srt
    if kind == "C":
        return S * math.exp(-q * T) * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S * math.exp(-q * T) * norm.cdf(-d1)

def solve_strike(S, T_yrs, r, q, sig, kind, target):
    g = (lambda K: K + bs(S, K, T_yrs, r, q, sig, "C") - target) if kind == "C" else \
        (lambda K: K - bs(S, K, T_yrs, r, q, sig, "P") - target)
    lo, hi = S * 1e-4, S * 10
    if g(lo) > 0 or g(hi) < 0:
        return None                       # target inside the carry no-solution corner
    K = brentq(g, lo, hi, xtol=1e-8 * S)
    return K

# ── BUILD TRADES ───────────────────────────────────────────────────────────────────────
first = max(pd.Timestamp(START_TRADES), idx[0] + pd.DateOffset(months=LOOKBACK_M))
entries = [nearest(ts) for ts in pd.date_range(first, idx[-1], freq=ROLL)]
entries = sorted({e for e in entries if e is not None})
rows, skipped_flat, skipped_corner = [], 0, 0
for e in entries:
    a = nearest(e - pd.DateOffset(months=LOOKBACK_M))
    x = nearest(e + pd.DateOffset(months=HORIZON_M))
    if a is None or x is None or a >= e or (idx[-1] - e).days < HORIZON_M * 29:
        continue
    S, Pa, Sx = D.at[e, "px"], D.at[a, "px"], D.at[x, "px"]
    R = S / Pa - 1.0
    if R == 0: skipped_flat += 1; continue
    kind = "C" if R > 0 else "P"
    tgt = S * (1.0 + R)
    T_yrs = (x - e).days / 365.25
    r = D.at[e, "rf"] if not np.isnan(D.at[e, "rf"]) else 0.04
    row = dict(entry=e, expiry=x, S=S, R=R, kind=kind, tgt=tgt, Sx=Sx, T=T_yrs,
               fwd=Sx / S - 1.0)
    ok = True
    for tag, sig in (("A", D.at[e, "vix"]), ("B", D.at[e, "rvol"])):
        if np.isnan(sig): ok = False; break
        K = solve_strike(S, T_yrs, r, DIV_YLD, sig, kind, tgt)
        if K is None: ok = False; break
        prem = bs(S, K, T_yrs, r, DIV_YLD, max(sig, VOL_FLOOR), kind)
        pay = max(Sx - K, 0.0) if kind == "C" else max(K - Sx, 0.0)
        row[f"K{tag}"], row[f"prem{tag}"], row[f"rop{tag}"] = K, prem, pay / prem - 1.0
    if not ok: skipped_corner += 1; continue
    for adj in VOL_ADJ_GRID:
        if adj == 1.0: row["ropA%d" % 100] = row["ropA"]; continue
        sig = D.at[e, "vix"] * adj
        K = solve_strike(S, T_yrs, r, DIV_YLD, sig, kind, tgt)
        if K is None: row["ropA%d" % int(adj * 100)] = np.nan; continue
        prem = bs(S, K, T_yrs, r, DIV_YLD, max(sig, VOL_FLOOR), kind)
        pay = max(Sx - K, 0.0) if kind == "C" else max(K - Sx, 0.0)
        row["ropA%d" % int(adj * 100)] = pay / prem - 1.0
    rows.append(row)
tr = pd.DataFrame(rows).set_index("entry").sort_index()
tr["hit"] = tr["ropA"] > 0            # ⟺ index landed beyond the extrapolated target
tr["gap"] = tr["fwd"] - tr["R"]       # realized 3-mo return minus extrapolated

# ── REPORT ─────────────────────────────────────────────────────────────────────────────
W = 96
def line(c="─"): print(c * W)
def block(label, d):
    if len(d) == 0: print(f"  {label:<18} —"); return
    tot = d["ropA"].sum(); hit = d["hit"].mean() * 100
    print(f"  {label:<18} n={len(d):>3}  hit {hit:5.1f}%  meanRoP {d['ropA'].mean()*100:+7.1f}%  "
          f"medRoP {d['ropA'].median()*100:+7.1f}%  Σ premiums-P&L {tot:+7.2f}x")
line("═"); print("  MOMENTUM-EXTRAPOLATION OPTION BACKTEST — trailing 3-mo trend as 3-mo forecast, "
                "breakeven pinned at the trend line")
print(f"  SPX daily (CBOE) {px.index[0].date()} → {px.index[-1].date()} · VIX (FRED) from "
      f"{vix.dropna().index[0].date()} · trades monthly {tr.index[0].date()} → {tr.index[-1].date()}")
print(f"  {len(tr)} trades ({int((tr.kind=='C').sum())} calls / {int((tr.kind=='P').sum())} puts) · "
      f"skipped: {skipped_corner} no-solution corner, {skipped_flat} flat · div yield {DIV_YLD:.1%} flat")
line("═")
print("  THE THEORY'S TRUTH VALUE (option-free — hit = index landed BEYOND its own trend line):")
print(f"    all trades: {tr['hit'].mean()*100:.1f}%   after UP 3-mo (calls): "
      f"{tr.loc[tr.kind=='C','hit'].mean()*100:.1f}%   after DOWN 3-mo (puts): "
      f"{tr.loc[tr.kind=='P','hit'].mean()*100:.1f}%")
sl, ic = np.polyfit(tr["R"], tr["fwd"], 1)
print(f"    forward-vs-trailing regression: slope {sl:+.3f} (corr {tr['R'].corr(tr['fwd']):+.3f}) "
      f"— 1.0 = trends continue as drawn; 0 = trailing tells you nothing  [overlap-inflated t-stats]")
print(f"    mean GAP (realized − extrapolated): all {tr['gap'].mean()*100:+.2f}pp · after up "
      f"{tr.loc[tr.kind=='C','gap'].mean()*100:+.2f}pp · after down {tr.loc[tr.kind=='P','gap'].mean()*100:+.2f}pp")
line()
print("  WHAT THE OPTION WRAPPER PAID (RoP = return on premium; total loss = −100%):")
for lab, d in (("ALL", tr), ("CALLS", tr[tr.kind == "C"]), ("PUTS", tr[tr.kind == "P"])):
    ppct = (d["premA"] / d["S"]).mean() * 100
    tl = (d["ropA"] <= -0.999).mean() * 100
    print(f"    [A VIX-priced]  {lab:<6} n={len(d):>3}  hit {d['hit'].mean()*100:5.1f}%  mean "
          f"{d['ropA'].mean()*100:+7.1f}%  median {d['ropA'].median()*100:+7.1f}%  Σ {d['ropA'].sum():+8.2f}x"
          f"  avg prem {ppct:4.1f}% of spot  wiped {tl:4.1f}%")
for lab, d in (("ALL", tr), ("CALLS", tr[tr.kind == "C"]), ("PUTS", tr[tr.kind == "P"])):
    print(f"    [B realized]    {lab:<6} n={len(d):>3}  hit {(d['ropB']>0).mean()*100:5.1f}%  mean "
          f"{d['ropB'].mean()*100:+7.1f}%  median {d['ropB'].median()*100:+7.1f}%  Σ {d['ropB'].sum():+8.2f}x")
line()
print("  BY ERA (mode A):")
for name, a, b in ERAS: block(name, tr.loc[a:b])
line()
print("  BY TRAILING-RETURN BUCKET (mode A) — where does the construction survive?")
for lo, hi in ((-1, -.10), (-.10, -.05), (-.05, 0), (0, .05), (.05, .10), (.10, 9)):
    d = tr[(tr.R > lo) & (tr.R <= hi)]
    block(f"trail {lo*100:+.0f}..{hi*100:+.0f}%", d)
line()
best = tr.nlargest(3, "ropA"); worst_dt = tr.loc[tr.ropA <= -0.999]
print("  TAILS: best trades " + " · ".join(f"{d.date()} {r.kind} {r.ropA*100:+.0f}%"
      for d, r in best.iterrows()))
print(f"  100%-losses cluster: " + ", ".join(str(y) for y in
      sorted(worst_dt.index.year.unique())[:12]) + (" …" if len(worst_dt.index.year.unique()) > 12 else ""))
print(f"  VIX-adj sensitivity (Σ RoP): " + "  ".join(
      f"×{a:.2f}: {tr['ropA%d' % int(a*100)].sum():+.1f}x" for a in VOL_ADJ_GRID))
pre = tr  # placeholder for pre-era comparison, computed below if data allows
line()
print("  CAVEATS (all directional, printed so the number isn't over-read):")
print("  · Flat-vol BS: real SPX PUTS carry post-'87 skew ABOVE VIX-flat → real put premiums richer")
print("    → put results here are KINDER than reality. OTM call IV sits BELOW VIX → call results")
print("    here are HARSHER than reality. Mode B (no vol premium at all) is the strategy's ceiling.")
print("  · No bid-ask/commissions (90s SPX spreads were wide); European exercise; flat 1.8% div yield.")
print("  · Overlapping monthly 3-mo windows → serial dependence; era Σ's are premium-units, not equity.")
print("  · Descriptive backtest. No recommendation. Sizing is Jake's.  [rule 7]")
line("═")

# ── CHART ──────────────────────────────────────────────────────────────────────────────
BLU, ORG, GRY = "#2a78d6", "#eb6834", "#8a8f98"
fig, ax = plt.subplots(2, 2, figsize=(13.5, 9.2), facecolor="white")
fig.suptitle("Momentum extrapolation via option breakevens — trailing 3-mo trend as the 3-mo forecast, 1995→2026",
             fontsize=12.5, fontweight="bold")
a = ax[0, 0]
cum = tr["ropA"].cumsum()
a.plot(cum.index, cum.values, color=BLU, lw=1.6)
a.axhline(0, color=GRY, lw=.7)
for name, s, e in ERAS[::2]:
    a.axvspan(pd.Timestamp(s), min(pd.Timestamp(e), cum.index[-1]), color=GRY, alpha=.08)
a.set_title("Cumulative P&L, premium units (mode A — VIX-priced)", fontsize=10)
a.set_ylabel("Σ return-on-premium (×)")
a = ax[0, 1]
c, p = tr[tr.kind == "C"], tr[tr.kind == "P"]
a.scatter(c["R"] * 100, c["fwd"] * 100, s=12, color=BLU, alpha=.55, label="after UP (call bought)")
a.scatter(p["R"] * 100, p["fwd"] * 100, s=12, color=ORG, alpha=.55, label="after DOWN (put bought)")
lim = np.array([-35, 35]); a.plot(lim, lim, color="#222", lw=1.1, ls="--", label="the extrapolation (45°)")
a.plot(lim, ic * 100 + sl * lim, color=GRY, lw=1.2, label=f"actual fit (slope {sl:+.2f})")
a.axhline(0, color=GRY, lw=.5); a.axvline(0, color=GRY, lw=.5)
a.set_xlim(lim); a.set_ylim(lim)
a.set_title("Next 3-mo return vs trailing 3-mo return — the theory in one picture", fontsize=10)
a.set_xlabel("trailing 3-mo %"); a.set_ylabel("next 3-mo %"); a.legend(fontsize=7.5, loc="upper left")
a = ax[1, 0]
a.vlines(c.index, 0, c["ropA"] * 100, color=BLU, lw=1.1, alpha=.8, label="calls")
a.vlines(p.index, 0, p["ropA"] * 100, color=ORG, lw=1.1, alpha=.8, label="puts")
a.axhline(0, color=GRY, lw=.7)
a.set_title("Per-trade return on premium (mode A)", fontsize=10)
a.set_ylabel("RoP %"); a.legend(fontsize=8)
a = ax[1, 1]
labs, hits, means = [], [], []
for lo, hi in ((-1, -.10), (-.10, -.05), (-.05, 0), (0, .05), (.05, .10), (.10, 9)):
    d = tr[(tr.R > lo) & (tr.R <= hi)]
    labs.append(f"{lo*100:+.0f}..{hi*100:+.0f}" if hi < 9 else ">+10")
    hits.append(d["hit"].mean() * 100 if len(d) else np.nan)
    means.append(d["ropA"].mean() * 100 if len(d) else np.nan)
x = np.arange(len(labs))
a.bar(x - .2, hits, .38, color=BLU, label="hit rate %")
a.bar(x + .2, means, .38, color=ORG, label="mean RoP %")
a.axhline(0, color=GRY, lw=.7)
a.set_xticks(x); a.set_xticklabels(labs, fontsize=8)
a.set_title("By trailing-return bucket: how often the line is reached, and what it paid", fontsize=10)
a.set_xlabel("trailing 3-mo return bucket (%)"); a.legend(fontsize=8)
for axx in ax.flat:
    axx.grid(alpha=.25, lw=.5)
    for s in ("top", "right"): axx.spines[s].set_visible(False)
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("momentum_extrapolation_backtest.png", dpi=150, bbox_inches="tight")
print("chart saved: momentum_extrapolation_backtest.png")
