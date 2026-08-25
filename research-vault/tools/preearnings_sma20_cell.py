#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════════════════════════
#  PRE-EARNINGS 20-SMA SUPPRESSION STUDY — Jake's spec, 2026-08-12
#
#  THE IDEA (his words): "check companies that trade below (even daily low if it closes above) the
#  20 SMA at least 70% of the 45 trading days leading up to earnings. If after 30 days from the
#  45 day mark (15 days before earnings) it's traded under 70% we buy it then and through earnings.
#  Only in our 2nd order universe and if implied volatility is elevated. Sweep the volatility
#  threshold from normal to high so we can see results without rejecting too many."
#
#  FORMALISED:
#    · MEASURE window  = trading days [E−45, E−15)   ← 30 bars, ends the day we decide
#    · DAY CONDITION   = Low < SMA20  (a TOUCH counts even if the close is back above — his spec)
#    · TRIGGER         = suppressed_fraction ≥ 70%   (swept 50→90, because a fixed 70 is a guess)
#    · ENTRY           = close of E−15               (the last bar of the measure window)
#    · EXIT            = close of E+1                (through the print; E+0/E+3/E+5 also reported)
#    · UNIVERSE        = the 23-name 2nd-order basket, wiki/ai-infra-allocation-map.md:L161
#    · VOL GATE        = swept, and n IS PRINTED AT EVERY LEVEL so the rejection cost is visible
#
#  ⛔ THE ONE THING YOU MUST READ BEFORE TRUSTING A NUMBER — THE IV SUBSTITUTION.
#     There is NO free source of HISTORICAL implied volatility. yfinance serves the CURRENT option
#     chain only. So a backtest gated on "IV was elevated back then" cannot be built at tier 0.
#     What this cell does instead, explicitly:
#       · BACKTEST  gates on REALISED-vol percentile (20d RV ranked in its own trailing 252d).
#       · LIVE SCREEN gates on ATM IV ÷ RV20 from the real chain — "are options rich vs what this
#         stock actually does", which is the better reading of "elevated" anyway.
#     ⚠️ RV IS NOT IV. The gap between them IS the volatility risk premium — an entire vault thread
#     ([[bull-bear-ledger]] VRP studies). RV says what the stock DID; IV says what the market EXPECTS.
#     For a LONG-SHARES trade through a print, "expected big move" is the intended signal, and that is
#     the half RV cannot see. Treat every backtest row below as the RV-proxy version of the idea.
#
#  ⚠️ AND THE STRUCTURAL LIMIT, STATED UP FRONT: there is NO HOLDOUT here, and two thresholds are
#     swept. Any single best cell in these tables is selected by the same data that scored it. The
#     durable output is the SHAPE across the sweep + the CONTROL legs, never the best cell.
#
#  COMPLETE CELL — paste whole into Colab and run. Token-free (yfinance only, no keys).
# ═══════════════════════════════════════════════════════════════════════════════════════════════════
import warnings, time, math
warnings.filterwarnings("ignore")
try:
    import yfinance as yf
except ImportError:
    import sys, subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "yfinance"])
    import yfinance as yf
import numpy as np, pandas as pd

# ═══════════════════════════ CONFIG ═══════════════════════════════════════════════════════════════
# The 2nd-order capex basket — wiki/ai-infra-allocation-map.md:L161 (Jake's 7/31 construction).
# ⚠️ EWY is DROPPED: it is an ETF and has no earnings date, so it cannot enter an earnings study.
UNIVERSE = ["NVDA","AVGO","TSM","INTC","AMD","MU","GFS","ARM",      # compute silicon 35.5%
            "IREN","CRWV","NBIS",                                    # neocloud 13.5%
            "AMAT","LRCX",                                           # semicap 9.0%
            "COHR","LITE",                                           # optical 8.5%
            "QRVO","SWKS",                                           # RF/handset 7.0%
            "ORCL","TXN","RNW","RIVN","MP"]                          # + hyperscaler/analog/power/EV/materials

LOOKBACK_START = 45      # window opens this many trading days before earnings
ENTRY_OFFSET   = 15      # window closes / we enter this many trading days before earnings
SMA_LEN        = 20
# ⛔⛔ JAKE, 2026-08-12: "wouldn't being under the 20 SMA for that many days imply the volatility on
#     its own — if it's flat, the SMA would catch up to it." HE IS RIGHT ABOUT THE MECHANISM, and it
#     is the single most important thing to know before reading any number this cell prints.
#
#       Low < SMA20   rearranges to   (Close − SMA20) < (Close − Low)
#                                     displacement above the mean  <  own intraday range
#
#     Both sides scale with volatility, so the condition is NOT a clean trend reading.
#
#  SIMULATED, 400 independent paths per cell, one 30-bar window each (2026-08-12):
#
#     metric            flat/20vol  flat/80vol   down−40%   up+50%   |  separation (down − up)
#     LOW<SMA  (spec)       62%        66%       73% / 70%  51% / 60% |  +21 pts @35vol, +9 @80vol
#     CLOSE<SMA             51%        54%       62% / 58%  39% / 49% |  +22 pts @35vol, +10 @80vol
#     (Close−SMA)/σ       −0.12      −0.54      −0.95 /−0.86 +0.65/−0.14| −1.60σ @35, −0.72σ @80
#
#  ⇒ THREE CONCLUSIONS, INCLUDING ONE THAT CORRECTS MY OWN FIRST READ:
#   1. **THE FLAT-STOCK PROBLEM IS REAL.** In the limiting case Jake describes — a perfectly constant
#      close — SMA20 converges to that price and the LOW is beneath it **100% of days**. In practice a
#      driftless stock reads **62-66%**, which sits uncomfortably close to a 70% gate: on 30 bars the
#      standard error is ~9 points, so **a flat name clears 70% a large share of the time by chance.**
#      The gate has weak SPECIFICITY, and that is his point landing.
#   2. **⛔ BUT SWITCHING TO CLOSE<SMA DOES NOT FIX DISCRIMINATION — I OVERSTATED THAT.** Touch and
#      close separate downtrend from uptrend **almost identically** (+21 vs +22 pts). What close has
#      is a **lower, interpretable null (~51% vs ~62%)**. So the metric is not the error — **THE
#      THRESHOLD IS.** 70% is a sensible gate on TOUCH (≈ the downtrend mean) and far too strict on
#      CLOSE, where the downtrend mean is only ~58-62%. **A threshold is meaningless without its null.**
#   3. **⚠️ THE VOL GATE HALVES THE SIGNAL, AND THIS IS THE REAL DESIGN CONFLICT.** Separation falls
#      from ~21 pts at 35% vol to ~9 pts at 80% vol, for EVERY metric. **The high-IV names the second
#      filter is meant to select are precisely the names where the first filter stops working.**
#      Expect the sweep's high-vol cells to be noise even where n survives. That is not a bug to fix —
#      it is the honest shape of the idea, and it is why the sweep exists.
#
# All three metrics are computed and swept side by side, each against its OWN null, so the original
# spec stays visible and gradeable instead of being quietly overwritten.
METRIC = "touch"   # "touch" = Jake's spec (null ~62%) | "close" (null ~51%) | "z" (null ~0σ)
TOUCH_MODE = (METRIC == "touch")   # the live screen reads the same switch
INCLUDE_ENTRY_BAR = False
YEARS          = 6       # price history to pull
EXIT_OFFSETS   = [0, 1, 3, 5]   # trading days after the earnings date; 1 is the headline
SUPPRESS_SWEEP = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95]  # extended UP: the flat-stock null is
                                                       # ~62% on touch, so 70% is only +8 pts
                                                       # above neutral. 85-95% is where a touch
                                                       # gate becomes genuinely selective.
VOL_SWEEP      = [0.0, 0.20, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]   # RV-percentile floor; 0 = no gate
BENCH          = "SPY"
PAUSE          = 0.4     # be polite to Yahoo; raise if you get rate-limited
# ══════════════════════════════════════════════════════════════════════════════════════════════════

def flat(df):
    """yf.download returns MultiIndex columns for some calls and not others. This is the single
    most common breakage in this whole notebook folder — 4 of the archived notebooks die on it."""
    if isinstance(df.columns, pd.MultiIndex):
        df = df.copy(); df.columns = df.columns.get_level_values(0)
    return df

def load_px(tkr, years=YEARS):
    try:
        df = yf.download(tkr, period=f"{years}y", interval="1d",
                         auto_adjust=True, progress=False, threads=False)
    except Exception as e:
        return None, f"download failed: {type(e).__name__}"
    if df is None or len(df) == 0:
        return None, "no rows returned"
    df = flat(df).dropna(subset=["Close"])
    if len(df) < 300:
        return None, f"only {len(df)} bars"
    df["SMA20"] = df["Close"].rolling(SMA_LEN).mean()
    r = df["Close"].pct_change()
    df["RV20"] = r.rolling(20).std() * math.sqrt(252)
    df["SD20"] = r.rolling(20).std() * df["Close"]   # 1σ in PRICE units, for the z-metric
    # RV percentile = where today's 20d realised vol sits in its OWN trailing year. Self-referential
    # on purpose: "elevated for THIS name", not elevated vs the market.
    df["RVpct"] = df["RV20"].rolling(252).rank(pct=True)
    return df, None

def load_earnings(tkr):
    """Past earnings dates. yfinance coverage is SHALLOW and uneven — this is the binding constraint
    on sample size, so the coverage is reported rather than hidden."""
    try:
        ed = yf.Ticker(tkr).get_earnings_dates(limit=60)
    except Exception as e:
        return [], f"{type(e).__name__}"
    if ed is None or len(ed) == 0:
        return [], "none returned"
    idx = pd.to_datetime(ed.index)
    try: idx = idx.tz_localize(None)
    except Exception:
        try: idx = idx.tz_convert(None)
        except Exception: pass
    today = pd.Timestamp.today().normalize()
    return sorted([d.normalize() for d in idx if d.normalize() < today]), None

# Null baselines from the 2026-08-12 simulation — printed alongside every gate so a threshold is
# always read against NEUTRAL rather than against zero. A gate below its own null selects nothing.
# Simulated nulls (driftless stock, 400 paths). A gate is only meaningful RELATIVE to these.
NULLS = {"touch": 0.62, "close": 0.51, "z": 0.0}
DOWN_MEAN = {"touch": 0.73, "close": 0.62, "z": -0.95}   # what a −40%/yr drifter reads

def window_metrics(df, i_e):
    """All three suppression metrics over the MEASURE window.
    Window = [i_e-45, i_e-15) → exactly 30 bars, ending on the entry bar (exclusive).
      touch = frac(Low   < SMA20)   — Jake's spec. Null 65%, and vol-blind at high vol.
      close = frac(Close < SMA20)   — null 52%, ~2σ discrimination at a 70% gate.
      z     = mean (Close − SMA20)/σ20 — scale-free; uses DEPTH, not just sign, so it does not
              throw away the difference between grazing the mean and sitting 3σ under it."""
    lo = i_e - LOOKBACK_START
    hi = i_e - ENTRY_OFFSET + (1 if INCLUDE_ENTRY_BAR else 0)
    if lo < SMA_LEN + 1 or hi <= lo:
        return None
    w = df.iloc[lo:hi]
    if w["SMA20"].isna().any() or w["SD20"].isna().any() or (w["SD20"] <= 0).any():
        return None
    return dict(touch=float((w["Low"] < w["SMA20"]).mean()),
                close=float((w["Close"] < w["SMA20"]).mean()),
                z=float(((w["Close"] - w["SMA20"]) / w["SD20"]).mean()),
                nbars=len(w))

def build_events():
    rows, notes = [], []
    bench, berr = load_px(BENCH)
    if berr:
        raise SystemExit(f"⛔ {BENCH} failed ({berr}) — no benchmark leg means no interpretable result.")
    print(f"  {'ticker':<7}{'bars':>7}{'earnings':>10}{'usable':>8}   note")
    print("  " + "-" * 74)
    for t in UNIVERSE:
        df, err = load_px(t)
        time.sleep(PAUSE)
        if err:
            print(f"  {t:<7}{'—':>7}{'—':>10}{'—':>8}   ⛔ {err}"); notes.append((t, err)); continue
        eds, eerr = load_earnings(t)
        time.sleep(PAUSE)
        if eerr or not eds:
            print(f"  {t:<7}{len(df):>7}{'—':>10}{'—':>8}   ⛔ earnings: {eerr or 'empty'}")
            notes.append((t, f"earnings {eerr}")); continue
        used = 0
        for e in eds:
            pos = df.index.searchsorted(e)
            if pos <= 0 or pos >= len(df): continue
            i_e = int(pos)
            m = window_metrics(df, i_e)
            if m is None: continue
            i_entry = i_e - ENTRY_OFFSET
            if i_entry < 0 or i_e + max(EXIT_OFFSETS) >= len(df): continue
            entry_px = float(df["Close"].iloc[i_entry])
            rvp = df["RVpct"].iloc[i_entry]
            rvp = float(rvp) if pd.notna(rvp) else np.nan
            rec = dict(ticker=t, edate=df.index[i_e], entry_date=df.index[i_entry],
                       frac=m[METRIC], f_touch=m["touch"], f_close=m["close"], f_z=m["z"],
                       rvpct=rvp, entry=entry_px)
            for k in EXIT_OFFSETS:
                px = float(df["Close"].iloc[i_e + k])
                rec[f"ret_{k}"] = px / entry_px - 1.0
                # benchmark over the IDENTICAL calendar span — the leg the archived backtests omit
                try:
                    b0 = float(bench["Close"].asof(df.index[i_entry]))
                    b1 = float(bench["Close"].asof(df.index[i_e + k]))
                    rec[f"spy_{k}"] = b1 / b0 - 1.0
                except Exception:
                    rec[f"spy_{k}"] = np.nan
                rec[f"alpha_{k}"] = rec[f"ret_{k}"] - rec[f"spy_{k}"]
            rows.append(rec); used += 1
        print(f"  {t:<7}{len(df):>7}{len(eds):>10}{used:>8}")
    return pd.DataFrame(rows), notes

def stat_block(d, k=1, ctrl=None):
    if len(d) == 0: return None
    r, a = d[f"ret_{k}"], d[f"alpha_{k}"]
    out = dict(n=len(d), win=(r > 0).mean(), mean=r.mean(), med=r.median(),
               amean=a.mean(), amed=a.median(), beat=(a > 0).mean(), sd=r.std())
    # ⛔ 8/12 GAP THIS CLOSES: v1 printed a t-stat for the headline trigger ONLY, so every GATED
    # cell — the ones that look best — went out with no significance attached at all.
    out["t"] = float("nan")
    if ctrl is not None and len(ctrl) > 1 and len(d) > 1:
        cr = ctrl[f"ret_{k}"]
        se = math.sqrt(r.var()/len(r) + cr.var()/len(cr))
        if se > 0: out["t"] = (r.mean() - cr.mean()) / se
    return out

def line(lab, s):
    if s is None or s["n"] == 0:
        return f"  {lab:<26}{'—  no events':>12}"
    t = s.get("t", float("nan"))
    tf = "  t —" if (t != t) else f"  t{t:>+5.2f}{'' if abs(t) >= 2 else ' ·noise'}"
    return (f"  {lab:<24}{s['n']:>5}  win {s['win']:>5.0%}  mean {s['mean']:>+7.2%}  "
            f"α {s['amean']:>+7.2%}  beat {s['beat']:>4.0%}{tf}")

print("=" * 100)
print("  PRE-EARNINGS 20-SMA SUPPRESSION — 2nd-order basket")
print(f"  measure [E−{LOOKBACK_START}, E−{ENTRY_OFFSET}) = {LOOKBACK_START-ENTRY_OFFSET} bars · "
      f"{'LOW touches' if TOUCH_MODE else 'CLOSE below'} SMA{SMA_LEN} · enter E−{ENTRY_OFFSET} close")
print("=" * 100)
print("\n  COVERAGE — read this before any result. Thin coverage is the binding constraint.\n")
ev, notes = build_events()

if len(ev) == 0:
    raise SystemExit("\n⛔ No usable events. Almost always yfinance earnings coverage — check the ⛔ rows.")

print(f"\n  → {len(ev)} usable earnings events across {ev.ticker.nunique()} names, "
      f"{ev.edate.min().date()} → {ev.edate.max().date()}")

# ── the suppression distribution: is 70% rare, or is it most of the sample?
print("\n" + "=" * 100)
print("  WHERE DOES THE 70% BAR ACTUALLY SIT? (distribution of the suppressed fraction)")
print("=" * 100)
print(f"  ACTIVE METRIC = {METRIC!r}   simulated null (zero-drift stock) = "
      f"{NULLS[METRIC]:.0%}" if METRIC != "z" else f"  ACTIVE METRIC = 'z'   null = 0.00σ")
print("  ⛔ READ EVERY GATE AGAINST ITS NULL, NOT AGAINST ZERO. Simulated, 400 paths, 30-bar window:")
print("        metric        flat(null)   −40%/yr   +50%/yr    SE on 30 bars")
print("        touch            62%         73%       51%          ~9 pts")
print("        close            51%         62%       39%          ~9 pts")
print("     ⇒ on TOUCH a 70% gate is only +8 pts above flat — barely 1 SE, so flat names leak through.")
print("     ⇒ on CLOSE a 70% gate sits ABOVE the downtrend mean (62%) and is far too strict.")
print("     ⇒ SEPARATION HALVES AT HIGH VOL (21 pts @35vol → 9 pts @80vol) FOR BOTH. The vol gate")
print("        selects exactly the names where this metric stops working — read those cells sceptically.")
for lab, col in [("touch  Low<SMA", "f_touch"), ("close  Close<SMA", "f_close")]:
    q = ev[col].quantile([.1,.25,.5,.75,.9])
    print(f"\n  {lab:<18} deciles: " + "  ".join(f"p{int(k*100)}={v:.0%}" for k, v in q.items()))
    for th in SUPPRESS_SWEEP:
        n = int((ev[col] >= th).sum())
        print(f"     ≥{th:.0%}: {n:>4} events ({n/len(ev):>4.0%})  {'█'*int(40*n/len(ev))}")
qz = ev["f_z"].quantile([.1,.25,.5,.75,.9])
print(f"\n  z      (Close−SMA)/σ deciles: " + "  ".join(f"p{int(k*100)}={v:+.2f}" for k, v in qz.items()))
print("     (more negative = deeper under the mean in its OWN volatility units)")

# ── the headline table: BOTH sweeps, with n printed everywhere
print("\n" + "=" * 100)
print(f"  THE SWEEP — entry E−{ENTRY_OFFSET} → exit E+1.  n IS SHOWN AT EVERY CELL ON PURPOSE:")
print("  a gate that rejects its way to a good number is the failure mode, not the result.")
print("=" * 100)
CTRL = ev[ev["frac"] < 0.70]     # the not-triggered control, fixed, for every cell's t-stat
print("  every t is vs the NOT-TRIGGERED control (<70%). |t|<2 is tagged ·noise.\n")
for th in SUPPRESS_SWEEP:
    trig = ev[ev["frac"] >= th]
    print(f"\n  ── {METRIC} ≥ {th:.0%}   ({len(trig)} events before the vol gate)"        + (f"   [null {NULLS[METRIC]:.0%}]" if METRIC != "z" else ""))
    if len(trig) == 0:
        print("     none"); continue
    for vg in VOL_SWEEP:
        sub = trig if vg == 0 else trig[trig["rvpct"] >= vg]
        lab = "no vol gate" if vg == 0 else f"RV pctile ≥ {vg:.0%}"
        print(line(lab, stat_block(sub, 1, CTRL)))

# ── THE CONTROLS. Without these the table above is unreadable.
print("\n" + "=" * 100)
print("  CONTROL LEGS — the comparison the result actually needs")
print("=" * 100)
base = ev[ev["frac"] < 0.70]
trig70 = ev[ev["frac"] >= 0.70]
print(line("ALL events (universe)", stat_block(ev, 1)))
print(line("TRIGGERED (≥70%)", stat_block(trig70, 1)))
print(line("NOT triggered (<70%)", stat_block(base, 1)))
if len(trig70) > 1 and len(base) > 1:
    d = trig70["ret_1"].mean() - base["ret_1"].mean()
    sp = math.sqrt(trig70["ret_1"].var()/len(trig70) + base["ret_1"].var()/len(base))
    print(f"\n  triggered − not-triggered = {d:+.2%}   t ≈ {d/sp if sp else float('nan'):+.2f}")
    print("  ⚠️ |t| < 2 on a sample this size is noise. Say so out loud rather than reading the sign.")

# ── holding-horizon shape
print("\n" + "=" * 100)
print("  HOLD HORIZON — is 'through earnings' the right exit, or is the move before/after the print?")
print("=" * 100)
for k in EXIT_OFFSETS:
    s = stat_block(trig70, k)
    print(line(f"triggered ≥70%, exit E+{k}", s))

# ── ⛔ THE DECOMPOSITION THE 8/12 RUN MADE ESSENTIAL: pre-announcement DRIFT vs the EVENT itself.
# Jake's thesis is "buy it then and THROUGH earnings" — the print is meant to be the catalyst. The
# first run said otherwise: α was +3.07% by E+0 and +2.80% by E+1, i.e. the print gave BACK 0.27pp.
# If that holds, this is a pre-earnings drift trade and the announcement is uncompensated variance.
print("\n" + "=" * 100)
print("  DRIFT vs EVENT — does the PRINT pay, or is the move already in before it?")
print("=" * 100)
for th in [0.70, 0.80, 0.90]:
    for vg in [0.0, 0.60, 0.70]:
        sub = ev[ev["frac"] >= th]
        if vg: sub = sub[sub["rvpct"] >= vg]
        if len(sub) < 5: continue
        pre = sub["alpha_0"].mean()                      # entry → E+0, before most prints
        evn = sub["alpha_1"].mean() - sub["alpha_0"].mean()   # the announcement itself
        post = sub["alpha_5"].mean() - sub["alpha_1"].mean()  # E+1 → E+5
        gate = "no vol gate" if vg == 0 else f"RV≥{vg:.0%}"
        print(f"  supp≥{th:.0%} · {gate:<12} n={len(sub):>4}   "
              f"PRE-drift α {pre:>+6.2%}   PRINT α {evn:>+6.2%}   POST α {post:>+6.2%}")
print("  ⇒ if PRINT is ~0 or negative, the earnings event is RISK WITHOUT RETURN and the exit")
print("     belongs at E+0, not after. That converts the idea into a 15-day pre-drift trade.")

# ── ⛔ THE REGIME TEST. 2020-2026 in AI/semis is ONE tape. If the effect is only 2023-24, it is the era.
print("\n" + "=" * 100)
print("  BY YEAR — is this a setup, or is it the 2023-24 AI tape wearing a setup's clothes?")
print("=" * 100)
# ⛔ v2 BUG, CAUGHT ON THE v2 RUN: this panel tested the UNGATED trigger — and the ungated
# suppression gate is INERT (α is flat at +2.3→+3.1% across the 50-90% band, because the metric's
# own null is 62%). So v2's by-year table was measuring the leg that does nothing, and its verdict
# ("positive in 3 of 6 years") was a verdict on the wrong thing. The gated cell is what must be
# tested by year, because the gated cell is the only thing that showed an effect.
ev["yr"] = ev["edate"].dt.year
for glab, gsupp, gvol in [("TRIGGER ONLY  (supp≥70%, no vol gate)", 0.70, 0.0),
                          ("VOL GATE ONLY (supp≥50% × RV≥60%)",     0.50, 0.60),
                          ("BOTH          (supp≥70% × RV≥60%)",     0.70, 0.60)]:
    print(f"\n  ── {glab}")
    print(f"  {'year':<7}{'ALL n':>7}{'ALL α':>9}{'sel n':>7}{'sel α':>9}{'win':>7}   marginal α")
    print("  " + "-" * 70)
    pos = neg = 0
    for y in sorted(ev["yr"].unique()):
        a = ev[ev["yr"] == y]
        t = a[a["frac"] >= gsupp]
        if gvol: t = t[t["rvpct"] >= gvol]
        if len(a) < 10:            # 2020 has n=3 — do not let a 1-event year vote
            print(f"  {y:<7}{len(a):>7}{a['alpha_1'].mean():>9.2%}{len(t):>7}"
                  f"{'—':>9}{'—':>7}   (n too small)")
            continue
        ta = t["alpha_1"].mean() if len(t) else float("nan")
        tw = (t["ret_1"] > 0).mean() if len(t) else float("nan")
        marg = ta - a["alpha_1"].mean() if len(t) else float("nan")
        if marg == marg:
            pos += marg > 0; neg += marg <= 0
        print(f"  {y:<7}{len(a):>7}{a['alpha_1'].mean():>9.2%}{len(t):>7}"
              f"{ta:>9.2%}{tw:>7.0%}   {marg:>+7.2%}")
    print(f"     → marginal α positive in {pos} of {pos+neg} scoreable years")
print("\n  ⇒ THE MARGINAL COLUMN IS THE ONLY ONE THAT MATTERS — how much the selection adds OVER")
print("     the universe's own base rate THAT YEAR. Compare the three blocks: if BOTH beats")
print("     TRIGGER-ONLY in most years, the interaction is real; if all three wander together,")
print("     the whole thing is the tape. A leg that is positive in ≤3 of 6 years is regime-bound.")

# ── per-name, so one ticker's run cannot masquerade as an effect
print("\n" + "=" * 100)
print("  PER-NAME (triggered ≥70%) — concentration check")
print("=" * 100)
if len(trig70):
    g = trig70.groupby("ticker")["ret_1"].agg(["count","mean","median"]).sort_values("mean", ascending=False)
    for t, r in g.iterrows():
        print(f"     {t:<7} n={int(r['count']):>3}  mean {r['mean']:>+7.2%}  med {r['median']:>+7.2%}")
    top = g["mean"].idxmax()
    ex = trig70[trig70.ticker != top]
    print(f"\n  drop the best name ({top}): " + (line("", stat_block(ex, 1)).strip() or "—"))
    print("  If the effect dies when one name leaves, it was that name — not the setup.")

# ── LIVE SCREEN, with REAL implied vol (the thing the backtest could not use)
print("\n" + "=" * 100)
print("  LIVE — who is in the setup NOW, with ACTUAL implied vol from the chain")
print("  ⛔ READ ABSOLUTE IV, NOT IV/RV, FOR THIS TRADE. Buying shares into a print, the thesis is")
print("  'the market expects a big move' — that is absolute IV. IV/RV is the option-SELLER's gauge")
print("  and it mislabels a name that just moved hard (high RV drags the ratio down while IV is")
print("  objectively elevated). IV/RV < 0.75 is flagged as 'the move already happened', not 'cheap'.")
print("=" * 100)
def atm_iv(tkr, spot):
    try:
        tk = yf.Ticker(tkr); exps = tk.options
        if not exps: return np.nan, None
        exp = exps[0]
        for e in exps:   # first expiry at least a week out
            if (pd.Timestamp(e) - pd.Timestamp.today()).days >= 7: exp = e; break
        ch = tk.option_chain(exp)
        cs = ch.calls.dropna(subset=["impliedVolatility"])
        if len(cs) == 0: return np.nan, exp
        k = (cs["strike"] - spot).abs().idxmin()
        return float(cs.loc[k, "impliedVolatility"]), exp
    except Exception:
        return np.nan, None

print(f"  {'tkr':<6}{'days→ER':>9}{'suppress%':>11}{'RVpct':>8}{'RV20':>8}{'ATM IV':>9}{'IV/RV':>8}  status")
print("  " + "-" * 84)
for t in UNIVERSE:
    df, err = load_px(t, years=2)
    if err: continue
    eds, _ = load_earnings(t)
    try:
        nxt = yf.Ticker(t).calendar
        nd = None
        if isinstance(nxt, dict) and nxt.get("Earnings Date"):
            nd = pd.Timestamp(sorted(nxt["Earnings Date"])[0])
        elif hasattr(nxt, "loc") and "Earnings Date" in getattr(nxt, "index", []):
            nd = pd.Timestamp(nxt.loc["Earnings Date"][0])
    except Exception:
        nd = None
    time.sleep(PAUSE)
    if nd is None: continue
    dte = int(np.busday_count(pd.Timestamp.today().date(), nd.date()))
    if not (0 < dte <= LOOKBACK_START): continue
    i_e = len(df) + dte                      # projected bar index of the print
    lo, hi = i_e - LOOKBACK_START, min(len(df), i_e - ENTRY_OFFSET)
    lo = max(lo, 0)
    if hi <= lo: continue
    w = df.iloc[lo:hi]
    below = (w["Low"] < w["SMA20"]) if TOUCH_MODE else (w["Close"] < w["SMA20"])
    frac = float(below.mean())
    spot = float(df["Close"].iloc[-1]); rv = float(df["RV20"].iloc[-1])
    rvp = df["RVpct"].iloc[-1]; rvp = float(rvp) if pd.notna(rvp) else np.nan
    iv, _ = atm_iv(t, spot); time.sleep(PAUSE)
    ratio = iv / rv if (rv and not np.isnan(iv)) else np.nan
    # ⛔ CORRECTED 8/12 AFTER THE FIRST LIVE RUN. v1 tagged every setup "IV not rich" when IV/RV<1
    # and that is the WRONG GAUGE FOR THIS TRADE. IREN printed ATM IV 85% — enormous in absolute
    # terms — but IV/RV 0.52 only because its REALISED vol was 164% after a huge move. IV/RV is the
    # OPTION-SELLER's question (are options dear vs what the stock does). Jake is buying SHARES and
    # wants "the market expects a big move" — that is ABSOLUTE IV, and IV/RV<1 actively mislabels it.
    st = "SETUP" if frac >= 0.70 else ("watch" if frac >= 0.55 else "")
    if st == "SETUP":
        if not np.isnan(iv) and iv >= 0.60:   st += "  ·IV HIGH (abs)"
        elif not np.isnan(iv) and iv <= 0.30: st += "  ·IV low (abs)"
        if not np.isnan(ratio) and ratio < 0.75:
            st += "  ·RV>>IV: the move already happened"
    print(f"  {t:<6}{dte:>9}{frac:>10.0%}{rvp:>8.0%}{rv:>8.0%}"
          f"{(f'{iv:.0%}' if not np.isnan(iv) else '—'):>9}"
          f"{(f'{ratio:.2f}' if not np.isnan(ratio) else '—'):>8}  {st}")
    if dte > ENTRY_OFFSET:
        print(f"         ↑ window still OPEN — decision bar is E−{ENTRY_OFFSET}, "
              f"{dte-ENTRY_OFFSET} trading days away. This % can still move.")

print("\n" + "=" * 100)
print("  HOW TO READ THIS — the limits, stated so they are not rediscovered later")
print("  · NO HOLDOUT, TWO SWEPT AXES. The best cell in the sweep was chosen by the data that scored")
print("    it. Read the SHAPE (does it improve monotonically with the gate?) and the CONTROL legs.")
print("    A gate that only looks good at one threshold with n=6 is a coincidence with a label.")
print("  · THE BACKTEST'S VOL GATE IS REALISED VOL, NOT IMPLIED. There is no free historical IV.")
print("    RV says what the stock DID; IV says what the market EXPECTS — and 'expects a big move' is")
print("    the actual thesis. The live table above is the only place real IV appears.")
print("  · SURVIVORSHIP: the universe is today's basket. Every name survived to today by construction.")
print("  · THE SETUP IS NEARLY A DOWNTREND DEFINITION. 'Below its 20-SMA 70% of 30 days' selects")
print("    beaten-down names almost tautologically, so this tests ONE specific claim: that the")
print("    earnings print reverses them. The not-triggered control is what separates the two.")
print("  · EARNINGS COVERAGE from yfinance is shallow and uneven; several names here IPO'd recently")
print("    (CRWV, NBIS, ARM, IREN). Sample size, not signal strength, is the binding constraint.")
print("=" * 100)
