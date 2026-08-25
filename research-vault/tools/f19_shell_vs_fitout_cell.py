#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════════════════════
#  F19 — SHELL vs FIT-OUT: dating the buildout with a SERIES instead of an adjective   [v3]
#
#  The flag (ai-capex-cycle.md:L2076, registered 2026-08-05): "If the shells were built
#  2024-25 and 2026 is the fill, data-center CONSTRUCTION should be DECELERATING while
#  equipment and semiconductor ORDERS ACCELERATE. A clean divergence DATES the buildout."
#  It carried a caveat — "⚠️ verify the series exists and is broken out." IT DOES.
#
#  ⛔ v3 REWRITE. v1/v2 pulled from FRED and every series timed out, including NEWORDER and
#  AMTMNO which unquestionably exist — so the IDs were never the problem, FRED was. The
#  Census API now returns "Missing Key" and DBnomics 404s on its series endpoints. But the
#  CENSUS C30 SPREADSHEET IS SERVED DIRECTLY, no key, no auth, and it is the ORIGINAL source
#  FRED was only mirroring. This cell reads it. VERIFIED WORKING 2026-08-11.
#
#  DATA CENTER IS ITS OWN COLUMN (col 9), monthly, seasonally adjusted, back to 2014.
#
#  ⚠️ TWO PARSING TRAPS, both hit and fixed during the build — left documented because they
#  silently produce WRONG NUMBERS rather than errors:
#    1. The header row has DUPLICATE labels, so name-based column lookup misaligns. Index
#       columns POSITIONALLY.
#    2. Dates are "Jun-26" / "Jan-93" — a naive "20"+yy turns 1993 into 2093, and after
#       sorting, .iloc[-1] returns 1990s data. Two-digit years >= 50 are 19xx.
#
#  COMPLETE CELL — paste whole into Colab and run. Tier 0: free, keyless, no tokens.
# ═══════════════════════════════════════════════════════════════════════════════════════════
try:
    import openpyxl  # noqa: F401
except ImportError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "openpyxl"], check=False)

import io, re, urllib.request, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

warnings.filterwarnings("ignore")

# ═════════════════════════════════ CONFIG ═══════════════════════════════════════════════════
START  = "2014-01-01"   # data centres are only broken out from 2014
SMOOTH = 3              # months of smoothing on growth lines (C30 is noisy and revised hard)
# ════════════════════════════════════════════════════════════════════════════════════════════

C30 = "https://www.census.gov/construction/c30/xls/privsatime.xlsx"
UA  = {"User-Agent": "Mozilla/5.0"}
MON = "JanFebMarAprMayJunJulAugSepOctNovDec"
COLS = {1: "Total private", 5: "Nonresidential", 7: "Office (total)",
        8: "Office: general", 9: "DATA CENTER", 11: "Commercial", 60: "Manufacturing"}

def parse_month(s):
    m = re.match(r"([A-Za-z]{3})-(\d{2})", str(s))
    if not m:
        return None
    yy = int(m.group(2))
    return pd.Timestamp(1900 + yy if yy >= 50 else 2000 + yy, MON.find(m.group(1)) // 3 + 1, 1)

print("=" * 94)
print("  F19 — SHELL vs FIT-OUT.  Source: Census C30, Value of Private Construction Put in")
print("  Place, seasonally adjusted annual rate. Direct from census.gov — no API key.")
print("=" * 94)

raw = urllib.request.urlopen(urllib.request.Request(C30, headers=UA), timeout=90).read()
df = pd.read_excel(io.BytesIO(raw), header=None)

# locate the table: header row is the one whose col0 == "Date"; data runs to the last Mon-YY
hdr_row = next(i for i in range(20) if str(df.iloc[i, 0]).strip() == "Date")
labels = [str(x).replace("\n", " ").replace("_x000D_", "").strip() for x in df.iloc[hdr_row]]
body = df.iloc[hdr_row + 1:].copy()
body["dt"] = body[0].map(parse_month)
body = body.dropna(subset=["dt"]).set_index("dt").sort_index()
print(f"  parsed {len(body)} monthly rows, {body.index[0].date()} → {body.index[-1].date()}")
print(f"  column 9 header reads: {labels[9]!r}   ← the flag's 'verify it is broken out'")
if "data cent" not in labels[9].lower():
    raise SystemExit(f"⛔ column 9 is {labels[9]!r}, not the data-centre line. Census changed the "
                     f"layout — find the right column index before trusting anything below.")

S = {name: pd.to_numeric(body[i], errors="coerce").dropna() for i, name in COLS.items()}
S = {k: v[v.index >= START] for k, v in S.items() if len(v[v.index >= START]) > 24}
DC = S["DATA CENTER"]

# ── integrity check: the subcategories must reconcile to the parent
last = DC.index[-1]
recon = S["Office: general"].get(last, np.nan) + DC.iloc[-1]
print(f"  ✓ reconciliation {last.strftime('%b-%y')}: data centre {DC.iloc[-1]/1000:.1f}B + general "
      f"office {S['Office: general'].get(last, np.nan)/1000:.1f}B = {recon/1000:.1f}B "
      f"vs Office total {S['Office (total)'].get(last, np.nan)/1000:.1f}B (difference = financial)")

def yoy(s):
    return (s / s.shift(12) - 1) * 100
def ann(s, m):
    return ((s / s.shift(m)) ** (12 / m) - 1) * 100

print("\n" + "=" * 94)
print("  THE SHELL LEG — is data-centre construction DECELERATING (fit-out) or not (shell)?")
print("=" * 94)
print(f"  {'month':<9}{'$B SAAR':>10}{'YoY':>9}{'3m ann':>9}{'6m ann':>9}")
for t in DC.index[-10:]:
    print(f"  {t.strftime('%b-%y'):<9}{DC[t]/1000:>10.1f}{yoy(DC).get(t, np.nan):>8.1f}%"
          f"{ann(DC,3).get(t, np.nan):>8.1f}%{ann(DC,6).get(t, np.nan):>8.1f}%")

g_now, g_6ago = yoy(DC).iloc[-1], yoy(DC).iloc[-7]
a3, a6 = ann(DC, 3).iloc[-1], ann(DC, 6).iloc[-1]
peak_is_now = DC.idxmax() == DC.index[-1]
print(f"\n  peak to date: ${DC.max()/1000:.1f}B in {DC.idxmax().strftime('%b-%y')}"
      f"{'  ← THE LATEST PRINT IS THE PEAK' if peak_is_now else ''}")

verdict = ("SHELL PHASE, STILL ACCELERATING — construction is not rolling over"
           if a3 > g_now and g_now > 0 else
           "SHELL PHASE, steady" if g_now > 5 else
           "DECELERATING — consistent with fit-out taking over" if g_now < g_6ago else "flat")
print(f"\n  ⇒ CONSTRUCTION LEG READS: {verdict}")
print(f"     YoY {g_now:+.1f}% (vs {g_6ago:+.1f}% six months ago) · 3m ann {a3:+.1f}% · 6m ann {a6:+.1f}%")
print(f"     3m ann ABOVE YoY ⇒ accelerating into the latest print."
      if a3 > g_now else "     3m ann BELOW YoY ⇒ losing momentum.")

# ── the contrast that makes it a finding rather than a number
print("\n" + "=" * 94)
print("  THE CONTRAST — is this a construction boom, or ONLY a data-centre boom?")
print("=" * 94)
print(f"  {'series':<20}{'6m ago':>10}{'latest':>10}{'change':>10}")
for name in ["DATA CENTER", "Office: general", "Office (total)", "Commercial",
             "Manufacturing", "Nonresidential", "Total private"]:
    if name not in S or len(S[name]) < 7:
        continue
    s = S[name]
    print(f"  {name:<20}{s.iloc[-7]/1000:>9.1f}B{s.iloc[-1]/1000:>9.1f}B"
          f"{(s.iloc[-1]/s.iloc[-7]-1)*100:>+9.1f}%")
share_now = DC.iloc[-1] / S["Office (total)"].iloc[-1] * 100
back = DC.index[-1] - pd.DateOffset(years=3)
share_3y = (DC[back] / S["Office (total)"][back] * 100) if back in DC.index else np.nan
print(f"\n  ⇒ data centres are {share_now:.0f}% of private office construction "
      f"(was {share_3y:.0f}% three years ago)")

# ═══════════════════════════════════ CHARTS ═════════════════════════════════════════════════
plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": .25,
                     "axes.spines.top": False, "axes.spines.right": False})
fig, ax = plt.subplots(3, 1, figsize=(12, 11), dpi=110)

ax[0].plot(DC.index, DC / 1000, lw=2.6, color="#b45309", label="DATA CENTER")
for n, c in [("Office: general", "#6b7280"), ("Commercial", "#9ca3af")]:
    if n in S:
        ax[0].plot(S[n].index, S[n] / 1000, lw=1.5, ls="--", color=c, label=n)
ax[0].set_title("Private construction put in place, $B SAAR — data centre vs the rest of office",
                fontsize=12.5, weight="bold", loc="left")
ax[0].legend(frameon=False, fontsize=9.5); ax[0].set_ylabel("$B SAAR")

g = yoy(DC).rolling(SMOOTH).mean()
ax[1].plot(g.index, g.values, lw=2.5, color="#b45309", label=f"data centre ({g_now:+.0f}% YoY)")
if "Office: general" in S:
    gg = yoy(S["Office: general"]).rolling(SMOOTH).mean()
    ax[1].plot(gg.index, gg.values, lw=1.6, ls="--", color="#6b7280", label="office ex-data-centre")
ax[1].axhline(0, color="#111", lw=.9)
ax[1].yaxis.set_major_formatter(mtick.PercentFormatter())
ax[1].set_title(f"YoY growth ({SMOOTH}m smoothed) — THE F19 TEST: is the shell leg rolling over?",
                fontsize=12.5, weight="bold", loc="left")
ax[1].legend(frameon=False, fontsize=9.5)

sh = (DC / S["Office (total)"].reindex(DC.index) * 100).dropna()
ax[2].plot(sh.index, sh.values, lw=2.5, color="#7c3aed")
ax[2].fill_between(sh.index, sh.values, 0, color="#7c3aed", alpha=.12)
ax[2].yaxis.set_major_formatter(mtick.PercentFormatter())
ax[2].set_title("data centres as a share of ALL private office construction",
                fontsize=12.5, weight="bold", loc="left")
plt.tight_layout(); plt.show()

print("\n" + "=" * 94)
print("  READING NOTES — what this does and does NOT establish")
print("  · IT KILLS THE ADJECTIVE, which was the point. 'Adolescence' and 'late-cycle' are both")
print("    unfalsifiable; this is a monthly series with a revision policy.")
print("  · IT IS A FLOW OF CAPEX, NOT A MEASURE OF RETURNS. Accelerating construction against")
print("    decelerating revenue per unit of compute is precisely the fragility case, not its")
print("    refutation. Pair it with CEPI before drawing any conclusion about equities.")
print("  · CONSTRUCTION PEAKS LATE. Telecom capex peaked in 2000-01; the equities topped in")
print("    March 2000. An accelerating flow times nothing — same rule, applied to the bull side.")
print("  · NOMINAL. Part of the growth is input-cost inflation the vault has logged (5-25% PCB")
print("    assembly, 15-45% bare boards). Real volume growth is SMALLER than these lines.")
print("  · ⚠️ REVISIONS: the last print is preliminary (p) and the two before it are revised (r).")
print("    The 3m-annualised figure leans hardest on the least settled data. The YoY and 6m")
print("    figures use settled months and are the ones to trust.")
print("=" * 94)
