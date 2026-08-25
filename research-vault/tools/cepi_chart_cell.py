# ═══════════════════════════════════════════════════════════════════════════
#  CEPI CHART CELL — the four panels worth looking at
#  Built 2026-08-07. Paste into Colab BELOW cepi_tracker_cell.py and run.
#  (If run standalone it falls back to an inline copy of the data.)
#
#  matplotlib only — pre-installed in Colab, nothing to pip install.
#
#  Q1 is blue and Q2 is orange in EVERY panel. The colour follows the QUARTER,
#  never the rank, so nothing repaints when a name is added or dropped.
#
#  D&A = depreciation and amortization · OCF = operating cash flow · C = capex
# ═══════════════════════════════════════════════════════════════════════════
import matplotlib
matplotlib.use("Agg")                      # Colab: drop this line to display inline
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

try:
    FILINGS
except NameError:                          # standalone fallback
    FILINGS = [
        dict(tkr="MSFT",  q="2026Q1", grp="HYPER", cal_ok=True,  rev=82886,  capex=30876, fl=4700, ni=31778,  ocf=46679, da=10167),
        dict(tkr="MSFT",  q="2026Q2", grp="HYPER", cal_ok=True,  rev=90007,  capex=35802, fl=5600, ni=35766,  ocf=55441, da=11022),
        dict(tkr="GOOGL", q="2026Q1", grp="HYPER", cal_ok=True,  rev=109896, capex=35674, fl=211,  ni=62578,  ocf=45790, da=6482),
        dict(tkr="GOOGL", q="2026Q2", grp="HYPER", cal_ok=True,  rev=119796, capex=44924, fl=691,  ni=112193, ocf=39069, da=7104),
        dict(tkr="AMZN",  q="2026Q1", grp="HYPER", cal_ok=True,  rev=181519, capex=44203, fl=1565, ni=30255,  ocf=26032, da=18945),
        dict(tkr="AMZN",  q="2026Q2", grp="HYPER", cal_ok=True,  rev=200606, capex=54208, fl=563,  ni=62647,  ocf=45387, da=19988),
        dict(tkr="META",  q="2026Q1", grp="HYPER", cal_ok=True,  rev=56311,  capex=18997, fl=None, ni=26773,  ocf=32226, da=5999),
        dict(tkr="META",  q="2026Q2", grp="HYPER", cal_ok=True,  rev=60801,  capex=30116, fl=None, ni=15848,  ocf=31862, da=6356),
        dict(tkr="ORCL",  q="2026Q1", grp="HYPER", cal_ok=False, rev=17190,  capex=18635, fl=None, ni=3721,   ocf=7151,  da=2566),
        dict(tkr="ORCL",  q="2026Q2", grp="HYPER", cal_ok=False, rev=19184,  capex=16493, fl=1527, ni=4304,   ocf=14620, da=2847),
        dict(tkr="SPCX",  q="2026Q2", grp="OTHER", cal_ok=True,  rev=7814,   capex=18369, fl=None, ni=-541,   ocf=2419,  da=2848),
    ]

# ── palette (validated categorical slots 1 & 2) ────────────────────────────
Q1C, Q2C = "#2a78d6", "#eb6834"            # blue / orange
INK, MUTED, RULE = "#0b0b0b", "#52514e", "#c9c8c3"
BAD = "#e34948"

NAMES = ["MSFT", "GOOGL", "AMZN", "META", "ORCL"]
QS = ["2026Q1", "2026Q2"]
tc  = lambda f: f["capex"] + (f["fl"] or 0)
get = lambda t, q: next((f for f in FILINGS if f["tkr"] == t and f["q"] == q), None)

plt.rcParams.update({
    "font.size": 11, "axes.titlesize": 12.5, "axes.labelsize": 10.5,
    "axes.edgecolor": RULE, "axes.linewidth": 0.8, "text.color": INK,
    "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
    "xtick.major.size": 0, "ytick.major.size": 0, "figure.facecolor": "white",
    "axes.facecolor": "white",
})

fig, ax = plt.subplots(2, 2, figsize=(13, 11))
fig.suptitle("CEPI tracker — calendar 2026 Q1 vs Q2, on true capex (incl. finance leases)",
             fontsize=15, fontweight="bold", y=0.975)
fig.text(0.5, 0.945, "D&A = depreciation and amortization  ·  OCF = operating cash flow  ·  C = capex",
         ha="center", fontsize=10, color=MUTED)

def grouped(a, metric, title, sub, thresh=None, thresh_lbl=None, names=NAMES):
    w, xs = 0.38, range(len(names))
    for i, q in enumerate(QS):
        vals = [metric(get(t, q)) if get(t, q) else 0 for t in names]
        pos = [x + (i - 0.5) * w for x in xs]
        b = a.bar(pos, vals, w * 0.92, label=q, color=[Q1C, Q2C][i], zorder=3)
        a.bar_label(b, fmt="%.2f", padding=2, fontsize=9, color=MUTED)
    if thresh is not None:
        a.axhline(thresh, color=BAD, lw=1.6, ls="--", zorder=4)
        a.text(len(names) - 0.55, thresh - 0.03, thresh_lbl, va="top", ha="right",
               fontsize=10, color=BAD, fontweight="bold")
    a.set_xticks(list(xs)); a.set_xticklabels(names, fontsize=11, color=INK)
    a.set_title(title, loc="left", fontweight="bold", pad=30)
    a.text(0, 1.045, sub, transform=a.transAxes, fontsize=9.5, color=MUTED)
    a.grid(axis="y", color=RULE, lw=0.6, alpha=0.6, zorder=0)
    a.set_axisbelow(True)
    for s in ("top", "right", "left"):
        a.spines[s].set_visible(False)

# ── 1. the self-funding line ──
grouped(ax[0][0], lambda f: f["ocf"] / tc(f),
        "Is the buildout funded out of the business?",
        "OCF / capex. Below 1.00 the marginal dollar comes from a bond desk.",
        thresh=1.0, thresh_lbl="1.00")
ax[0][0].legend(frameon=False, loc="upper left", bbox_to_anchor=(0, -0.09), ncol=2, fontsize=10)

# ── 2. the concentration test ──
def basket(q, ex=None):
    R = [f for f in FILINGS if f["q"] == q and f["grp"] == "HYPER" and f["cal_ok"] and f["tkr"] != ex]
    NI, DA = sum(f["ni"] for f in R), sum(f["da"] for f in R)
    OCF, C = sum(f["ocf"] for f in R), sum(tc(f) for f in R)
    return NI / C, (OCF - DA) / C

a = ax[0][1]
labels = ["all four\nreported", "all four\ncash", "ex-GOOGL\nreported", "ex-GOOGL\ncash"]
w, xs = 0.38, range(4)
for i, q in enumerate(QS):
    r_all, c_all = basket(q); r_ex, c_ex = basket(q, "GOOGL")
    vals = [r_all, c_all, r_ex, c_ex]
    pos = [x + (i - 0.5) * w for x in xs]
    b = a.bar(pos, vals, w * 0.92, label=q, color=[Q1C, Q2C][i], zorder=3)
    a.bar_label(b, fmt="%.2f", padding=2, fontsize=9, color=MUTED)
a.axhline(1.0, color=BAD, lw=1.6, ls="--", zorder=4)
a.text(3.45, 1.02, "1.00", va="bottom", ha="right", fontsize=9.5, color=BAD, fontweight="bold")
a.set_xticks(list(xs)); a.set_xticklabels(labels, fontsize=9.5, color=INK)
a.set_title("Do earnings exceed capex? Two answers, and one name", loc="left",
            fontweight="bold", pad=30)
a.text(0, 1.045, "Reported says yes. Cash (OCF − D&A) says no. Drop one name and the yes goes.",
       transform=a.transAxes, fontsize=9.5, color=MUTED)
a.grid(axis="y", color=RULE, lw=0.6, alpha=0.6, zorder=0); a.set_axisbelow(True)
for s in ("top", "right", "left"):
    a.spines[s].set_visible(False)

# ── 3. the quadrant map ──
a = ax[1][0]
XLO = -3.6
for t in NAMES + ["SPCX"]:
    f = get(t, "2026Q2")
    if not f:
        continue
    cq, oc = (f["ocf"] - f["ni"]) / f["da"], f["ocf"] / tc(f)
    clipped = cq < XLO
    x = XLO + 0.18 if clipped else cq
    a.scatter(x, oc, s=150, color=BAD if (cq < 0 and oc < 1) else Q1C,
              zorder=5, edgecolor="white", linewidth=2, marker="<" if clipped else "o")
    off = {"GOOGL": (14, -26), "AMZN": (12, 10), "MSFT": (12, 6),
           "META": (12, 6), "ORCL": (12, 6), "SPCX": (12, 6)}.get(t, (12, 6))
    a.annotate(f"{t}\nCQ {cq:.1f} — off scale".replace("-", "\u2212") if clipped else t,
               (x, oc), textcoords="offset points", xytext=off,
               fontsize=10, fontweight="bold", color=INK, linespacing=1.5)
a.axhline(1.0, color=RULE, lw=1.2, zorder=1); a.axvline(1.0, color=RULE, lw=1.2, zorder=1)
a.set_xlim(XLO, 5.0); a.set_ylim(-0.05, 2.0)
a.text(0.985, 0.03, "cash quality below normal  ↓ + not self-funding ←", transform=a.transAxes,
       ha="right", fontsize=9, color=BAD, style="italic")
a.set_xlabel("CQ  =  (OCF − net income) / D&A        →  1.0 = normal")
a.set_ylabel("OCF / capex        →  1.0 = self-funding")
a.set_title("Where each name sits — calendar Q2 2026", loc="left", fontweight="bold", pad=30)
a.text(0, 1.045, "Bottom-left is the bad quadrant: outspending cash, on earnings that aren't cash.",
       transform=a.transAxes, fontsize=9.5, color=MUTED)
a.grid(color=RULE, lw=0.6, alpha=0.45, zorder=0); a.set_axisbelow(True)
for s in ("top", "right"):
    a.spines[s].set_visible(False)

# ── 4. the catch-up gap ──
grouped(ax[1][1], lambda f: f["da"] / tc(f),
        "The bill that hasn't arrived yet",
        "D&A / capex. Falling = depreciation dropping further behind capex.")
ax[1][1].legend(frameon=False, loc="upper left", bbox_to_anchor=(0, -0.09), ncol=2, fontsize=10)
ax[1][1].yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.2f}"))

fig.text(0.5, 0.012,
         "⚠️  ORCL's fiscal quarters (Dec–Feb, Mar–May) do NOT align to calendar quarters and its lines are period-subtraction derivations.  "
         "META's finance leases are undisclosed, so its capex is a floor.  GOOGL Q2 net income is unverified against the primary 10-Q.",
         ha="center", fontsize=8.5, color=MUTED, style="italic")

plt.tight_layout(rect=[0, 0.028, 1, 0.935])
plt.savefig("cepi_panels.png", dpi=125, bbox_inches="tight", facecolor="white")
print("saved cepi_panels.png")
# In Colab, replace the two lines above with:  plt.show()
