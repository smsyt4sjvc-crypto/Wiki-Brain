# ═══════════════════════════════════════════════════════════════════════════
#  CEPI TRACKER v2 — the running E/C ratio, now a SERIES
#  Capex → Earnings → Price Intensity, instrumented.   v1 2026-08-07 (Jake's spec)
#  v2 2026-08-07 ~5:05pm PDT — 11 company-quarters loaded from the SEC line-item digest.
#
#  Paste into Colab and run. Zero dependencies. Add ONE BLOCK per company-quarter
#  as earnings land — the series builds itself.
#
#  FIVE RATIOS. The fifth was forced by the data on first load.
#   C/R   = capex / revenue ............. intensity (SPCX 2.35x vs MSFT ~0.4x)
#   E/C   = net income / capex .......... Jake's ask. GAAP profit per $ of capex.
#   OCF/C = operating cash flow / capex . THE LINE THAT MATTERS. <1.00 = NOT self-funding.
#   DA/C  = D&A / capex ................. the CATCH-UP ratio, where D&A = DEPRECIATION AND
#                                         AMORTIZATION: the non-cash accounting charge for
#                                         assets bought in PAST years. (The cash itself left
#                                         at capex; D&A just spreads that cost over the years
#                                         the asset is used.) DA/C therefore compares what is
#                                         being SPENT now against what is being EXPENSED now.
#                                         Near 0 = the capex wave has not hit the P&L yet.
#                                         Toward 1.0 = steady state, it has.
#   CQ    = (OCF − NI) / D&A ............ ★ CASH QUALITY. Normally ≥1.0: cash flow should
#                                         exceed earnings by AT LEAST depreciation. Below
#                                         1.0 = something non-cash is inflating earnings.
#                                         NEGATIVE = earnings exceed cash generation
#                                         outright. This is the ratio that catches
#                                         mark-to-market gains on equity stakes.
#
#  ⚠️ THE TRAP E/C ALONE WALKS INTO: earnings are AFTER depreciation, so as the
#  2024-26 wave starts depreciating, E/C falls for TWO reasons at once (capex up AND
#  earnings down). DA/C is what separates them. Never read E/C without it.
#
#  ⚠️ THE SECOND TRAP — FINANCE LEASES. Headline "capex" from a press release often
#  EXCLUDES finance-lease additions, which is where a lot of AI infrastructure sits.
#  This cell tracks them SEPARATELY and reports both headline and TRUE capex, because
#  the difference decides the self-funding verdict outright. (Do not merge the fields.)
#
#  ⚠️ THE THIRD TRAP — FISCAL vs CALENDAR. Oracle's fiscal quarters (Dec-Feb, Mar-May)
#  do NOT map to calendar quarters. `cal_ok=False` filers are EXCLUDED from the
#  calendar aggregate and reported on their own line. A silent mix would corrupt the series.
# ═══════════════════════════════════════════════════════════════════════════

# ── DATA ───────────────────────────────────────────────────────────────────
# $ MILLIONS, per QUARTER. None = not disclosed (the cell reports coverage).
# fl = finance-lease additions, stated SEPARATELY from headline capex.
# cal_ok = does the fiscal period map cleanly onto the calendar quarter?
# grp = "HYPER" (the five-name complex the GS chart tracks) or "OTHER".
# Source: SEC line-item digest 2026-08-07 (10-Q / 10-K / earnings releases).
FILINGS = [
    # ── MICROSOFT ── FY ends Jun 30. FY26Q3 = cal Q1, FY26Q4 = cal Q2.
    dict(tkr="MSFT", q="2026Q1", grp="HYPER", cal_ok=True,
         rev=82886, capex=30876, fl=4700, ni=31778, ocf=46679, da=10167,
         src="FY26Q3 financials 4/29; D&A = CF line 'Depreciation, amortization, and other'; RPO 627,000; prior-period CF RECAST not restated"),
    dict(tkr="MSFT", q="2026Q2", grp="HYPER", cal_ok=True,
         rev=90007, capex=35802, fl=5600, ni=35766, ocf=55441, da=11022,
         src="FY26Q4 financials 7/29; RPO 678,000; ⚠️ eff. 2026-07-01 datacenter/office lives 15→25y (NOT servers/network) — flatters cal-Q3 onward"),

    # ── ALPHABET ──
    dict(tkr="GOOGL", q="2026Q1", grp="HYPER", cal_ok=True,
         rev=109896, capex=35674, fl=211, ni=62578, ocf=45790, da=6482,
         src="10-Q 4/29-30; ⚠️ D&A = depreciation ONLY, amortization not disclosed on CF stmt (DA/C understated); backlog 467,600"),
    dict(tkr="GOOGL", q="2026Q2", grp="HYPER", cal_ok=True,
         rev=119796, capex=44924, fl=691, ni=112193, ocf=39069, da=7104,
         src="10-Q 7/22-23; ⚠️ D&A = depreciation ONLY; backlog 519,500 (Cloud 513,900)"),

    # ── AMAZON ──
    dict(tkr="AMZN", q="2026Q1", grp="HYPER", cal_ok=True,
         rev=181519, capex=44203, fl=1565, ni=30255, ocf=26032, da=18945,
         src="10-Q 4/30; ⚠️ D&A line includes PP&E + capitalized content + operating-lease assets (DA/C OVERstated); purch. oblig. 103,768"),
    dict(tkr="AMZN", q="2026Q2", grp="HYPER", cal_ok=True,
         rev=200606, capex=54208, fl=563, ni=62647, ocf=45387, da=19988,
         src="10-Q 7/31; ⚠️ D&A line includes content + lease assets; purch. oblig. 130,065"),

    # ── META ── finance leases NOT disclosed ⇒ true capex UNDERSTATED ⇒ its OCF/C is a CEILING.
    dict(tkr="META", q="2026Q1", grp="HYPER", cal_ok=True,
         rev=56311, capex=18997, fl=None, ni=26773, ocf=32226, da=5999,
         src="10-Q 4/29-30; finance leases NOT DISCLOSED; contractual commitments 237,670"),
    dict(tkr="META", q="2026Q2", grp="HYPER", cal_ok=True,
         rev=60801, capex=30116, fl=None, ni=15848, ocf=31862, da=6356,
         src="10-Q 7/29; finance leases NOT DISCLOSED; contractual commitments 349,310 (+47% QoQ)"),

    # ── ORACLE ── FY ends May 31. ⚠️ FISCAL ≠ CALENDAR, and nearly every line is DERIVED
    #    by period subtraction (9M − 6M, FY − 9M). Excluded from the calendar aggregate.
    dict(tkr="ORCL", q="2026Q1", grp="HYPER", cal_ok=False,
         rev=17190, capex=18635, fl=None, ni=3721, ocf=7151, da=2566,
         src="FY26Q3 = Dec1'25-Feb28'26, NOT cal Q1. capex/ocf/da all DERIVED 9M−6M. 10-Q 3/11 + 12/11; RPO 552,600"),
    dict(tkr="ORCL", q="2026Q2", grp="HYPER", cal_ok=False,
         rev=19184, capex=16493, fl=1527, ni=4304, ocf=14620, da=2847,
         src="FY26Q4 = Mar1-May31'26, NOT cal Q2. capex/fl/ocf/da all DERIVED FY−9M. 10-K + Q4 release 6/10-22; RPO 638,000"),

    # ── SPACEX ── not part of the GS five-name complex; tracked separately.
    dict(tkr="SPCX", q="2026Q2", grp="OTHER", cal_ok=True,
         rev=7814, capex=18369, fl=None, ni=-541, ocf=2419, da=2848,
         src="segment table 8/4 (ZH-confirmed to the dollar) + 10-Q 8/4; OCF DERIVED 6M−Q1; adj EBITDA 3,538, op income −143"),
]

# Independent AGGREGATE cross-check: GS/FactSet combined FCF for META+MSFT+GOOGL+AMZN+ORCL
# ($bn/qtr, chart-read 8/6 — approximate). Combined FCF < 0  ⟺  combined OCF/C < 1.00.
GS_COMBINED_FCF_BN = {"2024Q2": 104, "2026Q1": 57, "2026Q3E": -20, "2027E": -25, "2029Q3E": 122}

ORDER = ["C/R", "E/C", "OCF/C", "DA/C", "CQ"]

# ── ENGINE ─────────────────────────────────────────────────────────────────
def r(a, b):
    """Ratio with None-safety. Returns None if either side is missing or denom is 0."""
    if a is None or b is None or b == 0:
        return None
    return a / b

def fmt(x, w=8, dp=2):
    return ("—".rjust(w) if x is None else f"{x:,.{dp}f}".rjust(w))

def true_capex(f):
    """Headline capex + finance-lease additions. If leases are undisclosed, this is a FLOOR."""
    if f["capex"] is None:
        return None, False
    if f["fl"] is None:
        return f["capex"], False          # floor — leases unknown
    return f["capex"] + f["fl"], True

def ratios(f, use_true=True):
    c = true_capex(f)[0] if use_true else f["capex"]
    ocf, ni, da = f["ocf"], f["ni"], f["da"]
    cq = None
    if ocf is not None and ni is not None and da not in (None, 0):
        cq = (ocf - ni) / da
    return {"C/R": r(c, f["rev"]), "E/C": r(ni, c), "OCF/C": r(ocf, c),
            "DA/C": r(da, c), "CQ": cq}

print("=" * 96)
print("  CEPI TRACKER v2 — E/C, the self-funding line, and the cash-quality screen".center(96))
print("  D&A = depreciation and amortization · OCF = operating cash flow · C = capex".center(96))
print("=" * 96)

if not FILINGS:
    print("\n  No filings loaded.\n")
else:
    # ── PER-FILING (on TRUE capex: headline + finance leases) ──
    print("\n  PER FILING — ratios computed on TRUE capex (headline + finance leases)")
    print(f"\n{'TKR':<7}{'QUARTER':<10}" + "".join(k.rjust(8) for k in ORDER)
          + "   COV  FLAGS")
    print("-" * 96)
    for f in sorted(FILINGS, key=lambda x: (x["q"], x["tkr"])):
        R = ratios(f)
        have = sum(1 for k in ORDER if R[k] is not None)
        flags = []
        if not f["cal_ok"]:
            flags.append("⚠️FISCAL≠CAL")
        if f["fl"] is None:
            flags.append("leases n/d→capex is a FLOOR")
        if R["OCF/C"] is not None and R["OCF/C"] < 1.0:
            flags.append("NOT self-funding")
        if R["CQ"] is not None and R["CQ"] < 0:
            flags.append("★NI > cash generation")
        print(f"{f['tkr']:<7}{f['q']:<10}" + "".join(fmt(R[k]) for k in ORDER)
              + f"   {have}/5  " + "; ".join(flags))
    print("-" * 96)

    # ── THE FINANCE-LEASE CORRECTION — how much the headline understates ──
    print("\n  THE FINANCE-LEASE CORRECTION (why the two numbers are kept apart)")
    print(f"\n{'TKR':<7}{'QUARTER':<10}{'headline':>11}{'+leases':>10}{'= TRUE':>11}"
          f"{'OCF/C hdln':>12}{'OCF/C true':>12}   verdict flips?")
    print("-" * 96)
    for f in sorted(FILINGS, key=lambda x: (x["q"], x["tkr"])):
        if f["fl"] is None or f["capex"] is None:
            continue
        h, t = f["capex"], f["capex"] + f["fl"]
        oh, ot = r(f["ocf"], h), r(f["ocf"], t)
        flip = ""
        if oh is not None and ot is not None:
            flip = "★ YES — crosses 1.00" if (oh >= 1.0 > ot) else ("no" if oh >= 1.0 else "already <1.00")
        print(f"{f['tkr']:<7}{f['q']:<10}{h:>11,}{f['fl']:>10,}{t:>11,}"
              + fmt(oh, 12) + fmt(ot, 12) + "   " + flip)
    print("-" * 96)

    # ── DOLLAR-WEIGHTED AGGREGATE, BY QUARTER ──
    def aggregate(rows, label):
        def pair(num_key, use_true=True):
            """Sum numerator and capex ONLY over filings that have both — no mixed baskets."""
            ok = []
            for f in rows:
                c = true_capex(f)[0] if use_true else f["capex"]
                if f[num_key] is not None and c is not None:
                    ok.append((f[num_key], c))
            if not ok:
                return None, 0
            return sum(a for a, _ in ok) / sum(c for _, c in ok), len(ok)

        cr_ok = [f for f in rows if f["rev"] is not None and true_capex(f)[0] is not None]
        cr = (r(sum(true_capex(f)[0] for f in cr_ok), sum(f["rev"] for f in cr_ok))
              if cr_ok else None)
        ec,  n_ec  = pair("ni")
        ocf, n_ocf = pair("ocf")
        da,  n_da  = pair("da")
        cq_ok = [f for f in rows if None not in (f["ocf"], f["ni"], f["da"])]
        cq = (sum(f["ocf"] - f["ni"] for f in cq_ok) / sum(f["da"] for f in cq_ok)
              if cq_ok and sum(f["da"] for f in cq_ok) else None)
        print(f"{label:<34}" + fmt(cr) + fmt(ec) + fmt(ocf) + fmt(da) + fmt(cq)
              + f"   {len(cr_ok)}/{n_ec}/{n_ocf}/{n_da}/{len(cq_ok)} of {len(rows)}")
        return ocf

    print("\n  DOLLAR-WEIGHTED AGGREGATE (sum the dollars, then divide — not an average of ratios)")
    print("  Calendar-aligned filers only. Fiscal≠calendar filers reported separately below.")
    print(f"\n{'BASKET':<34}" + "".join(k.rjust(8) for k in ORDER) + "   n covered")
    print("-" * 96)
    verdicts = {}
    for q in sorted({f["q"] for f in FILINGS}):
        hyper = [f for f in FILINGS if f["q"] == q and f["grp"] == "HYPER" and f["cal_ok"]]
        if hyper:
            verdicts[q] = aggregate(hyper, f"{q}  hyperscalers (cal-aligned)")
        off = [f for f in FILINGS if f["q"] == q and not f["cal_ok"]]
        if off:
            aggregate(off, f"{q}  ⚠️ fiscal≠calendar (ORCL)")
        oth = [f for f in FILINGS if f["q"] == q and f["grp"] == "OTHER"]
        if oth:
            aggregate(oth, f"{q}  other ({', '.join(f['tkr'] for f in oth)})")
    print("-" * 96)

    # ── THE SELF-FUNDING VERDICT ──
    print("\n  ⭐ THE SELF-FUNDING LINE — OCF/C vs 1.00, calendar-aligned hyperscalers")
    for q in sorted(verdicts):
        v = verdicts[q]
        if v is None:
            continue
        state = "BELOW 1.00 — the complex is NOT self-funding its buildout" if v < 1.0 \
                else "above 1.00 — still self-funded out of the business"
        print(f"    {q}   OCF/C = {v:,.3f}   → {state}")
    print("\n    Note: META's finance leases are NOT DISCLOSED, so true capex is a FLOOR and")
    print("    the aggregate OCF/C above is a CEILING. The real number is at or below it.")

    # ── DIFFUSION — an aggregate can cross while most names do not. Count them. ──
    print("\n  ⭐ DIFFUSION — how many names are individually below 1.00?")
    print("     (an aggregate is one number; it hides whether this is broad or concentrated)")
    for q in sorted({f["q"] for f in FILINGS}):
        rows = [f for f in FILINGS if f["q"] == q and f["grp"] == "HYPER"
                and f["ocf"] is not None and true_capex(f)[0]]
        if not rows:
            continue
        vals = sorted(((f["tkr"], f["ocf"] / true_capex(f)[0]) for f in rows), key=lambda x: x[1])
        below = [v for v in vals if v[1] < 1.0]
        above = [v for v in vals if v[1] >= 1.0]
        print(f"    {q}   BELOW {len(below)}/{len(rows)}: "
              + ", ".join(f"{t} {v:.2f}" for t, v in below)
              + "   |   above: " + ", ".join(f"{t} {v:.2f}" for t, v in reversed(above)))

    # ── QoQ ATTRIBUTION — WHICH BLADE MOVED? falling cash and rising capex are
    #    not the same problem and do not resolve the same way. ──
    qs = sorted({f["q"] for f in FILINGS})
    if len(qs) >= 2:
        qa, qb = qs[-2], qs[-1]
        print(f"\n  ⭐ QoQ ATTRIBUTION {qa} → {qb} — which blade moved?")
        print("     capex step-up = a SPENDING CHOICE (reversible in a quarter)")
        print("     OCF decline   = a CASH problem (not reversible by decision)")
        print(f"\n{'TKR':<7}{'OCF/C '+qa:>12}{'OCF/C '+qb:>12}{'Δ':>8}{'OCF Δ%':>10}{'capex Δ%':>11}   driver")
        print("-" * 96)
        for t in sorted({f["tkr"] for f in FILINGS if f["grp"] == "HYPER"}):
            a = [f for f in FILINGS if f["tkr"] == t and f["q"] == qa]
            b = [f for f in FILINGS if f["tkr"] == t and f["q"] == qb]
            if not (a and b):
                continue
            a, b = a[0], b[0]
            ca, cb = true_capex(a)[0], true_capex(b)[0]
            if None in (ca, cb, a["ocf"], b["ocf"]) or not (ca and a["ocf"]):
                continue
            r1, r2 = a["ocf"] / ca, b["ocf"] / cb
            do, dc = (b["ocf"] / a["ocf"] - 1) * 100, (cb / ca - 1) * 100
            drv = ("★ BOTH blades" if do < -5 and dc > 15 else
                   "OCF decline"   if do < -5 else
                   "capex step-up" if dc > 15 and do <= 15 else
                   "OCF recovery"  if do > 15 else "flat")
            if r2 > r1 and drv == "capex step-up":
                drv += " (outgrown by OCF)"
            print(f"{t:<7}{r1:>12.2f}{r2:>12.2f}{r2-r1:>+8.2f}{do:>+9.1f}%{dc:>+10.1f}%   {drv}")
        print("-" * 96)

    # ── REPORTED vs CASH EARNINGS AGAINST CAPEX ──
    #    "Do earnings exceed capex?" has two answers and they disagree. Print both,
    #    and print the basket with the biggest non-cash contributor REMOVED, because
    #    an aggregate answer that one name produces is not an answer about the group.
    print("\n  ⭐ DO EARNINGS EXCEED CAPEX? — reported vs cash, and the concentration test")
    print("     cash earnings = OCF − D&A.  ⚠️ a PROXY: in a buildout D&A lags the asset base,")
    print("     so the eventual depreciation charge is LARGER and this proxy is GENEROUS.")

    def basket(rows, label):
        rows = [f for f in rows if None not in (f["ni"], f["ocf"], f["da"]) and true_capex(f)[0]]
        if not rows:
            return
        NI = sum(f["ni"] for f in rows); DA = sum(f["da"] for f in rows)
        OCF = sum(f["ocf"] for f in rows); C = sum(true_capex(f)[0] for f in rows)
        short = NI + DA - OCF
        print(f"{label:<30}{NI/C:>10.2f}{(OCF-DA)/C:>10.2f}{OCF/C:>9.2f}{short:>15,}{short/NI*100:>7.0f}%")

    # who is the biggest non-cash contributor? (largest NI − OCF gap, latest quarter)
    qs = sorted({f["q"] for f in FILINGS})
    hyp = [f for f in FILINGS if f["grp"] == "HYPER" and f["cal_ok"]]
    latest = [f for f in hyp if f["q"] == qs[-1] and None not in (f["ni"], f["ocf"])]
    worst = max(latest, key=lambda f: f["ni"] - f["ocf"])["tkr"] if latest else None

    print(f"\n{'BASKET':<30}{'rep E/C':>10}{'cash E/C':>10}{'OCF/C':>9}{'non-cash gap':>15}{'of NI':>8}")
    print("-" * 96)
    for q in qs:
        basket([f for f in hyp if f["q"] == q], f"{q}  all cal-aligned")
        if worst:
            basket([f for f in hyp if f["q"] == q and f["tkr"] != worst], f"{q}  ex-{worst}")
    print("-" * 96)
    if worst:
        print(f"    If 'rep E/C' crosses 1.00 between the two rows, the answer to \"do earnings")
        print(f"    exceed capex\" is a statement about {worst}, not about the group.")

    # ── ROBUSTNESS: how much of the conclusion rests on the LEAST-VERIFIED number? ──
    #    A conclusion that inverts on one unconfirmed datapoint is not a conclusion yet.
    #    Set `stress` below to re-run the headline with a suspect figure replaced.
    STRESS = dict(tkr="GOOGL", q=qs[-1], field="ni", alt_note="~30% net margin (sector-normal)",
                  alt=lambda f: int(f["rev"] * 0.30))
    tgt = [f for f in hyp if f["tkr"] == STRESS["tkr"] and f["q"] == STRESS["q"]]
    if tgt and tgt[0]["rev"]:
        print(f"\n  ⭐ ROBUSTNESS — does the answer survive if {STRESS['tkr']} {STRESS['q']} "
              f"{STRESS['field']} is wrong?")
        rows = [f for f in hyp if f["q"] == STRESS["q"]]
        for lab, override in [("as digested", None), (STRESS["alt_note"], STRESS["alt"](tgt[0]))]:
            NI = sum((override if (override is not None and f["tkr"] == STRESS["tkr"]) else f[STRESS["field"]])
                     for f in rows)
            DA = sum(f["da"] for f in rows); OCF = sum(f["ocf"] for f in rows)
            C = sum(true_capex(f)[0] for f in rows)
            print(f"    {lab:<34} rep E/C {NI/C:>5.2f}   gap {NI/C-(OCF-DA)/C:>5.2f}   "
                  f"wedge {NI+DA-OCF:>10,} ({(NI+DA-OCF)/NI*100:>3.0f}% of NI)")
        print("    If the two rows disagree on the SIGN or the verdict, the headline is")
        print("    unconfirmed — quote it with the caveat, not as a finding.")

    # ── THE CASH-QUALITY SCREEN ──
    print("\n  ⭐ CASH-QUALITY SCREEN — CQ = (OCF − NI) / D&A")
    print("     ≥1.0 = normal (cash flow exceeds earnings by at least depreciation)")
    print("     <1.0 = something non-cash is inflating earnings")
    print("     <0   = earnings EXCEED cash generation outright")
    print(f"\n{'TKR':<7}{'QUARTER':<10}{'net income':>13}{'op cash flow':>14}{'OCF − NI':>12}{'D&A':>10}{'CQ':>9}")
    print("-" * 96)
    for f in sorted(FILINGS, key=lambda x: (ratios(x)["CQ"] if ratios(x)["CQ"] is not None else 99)):
        cq = ratios(f)["CQ"]
        if cq is None:
            continue
        mark = "  ★" if cq < 0 else ("  ⚠️" if cq < 1.0 else "")
        print(f"{f['tkr']:<7}{f['q']:<10}{f['ni']:>13,}{f['ocf']:>14,}{f['ocf']-f['ni']:>12,}"
              f"{f['da']:>10,}{cq:>9,.2f}{mark}")
    print("-" * 96)

    # ── WHAT IS MISSING ──
    print("\n  🚩 MISSING LINE ITEMS (each closes one cell above)")
    gaps = {}
    for f in FILINGS:
        for k, label in [("rev", "revenue"), ("capex", "capex (CF stmt)"), ("fl", "finance leases"),
                         ("ni", "net income"), ("ocf", "operating cash flow"), ("da", "D&A")]:
            if f[k] is None:
                gaps.setdefault(f"{f['tkr']} {f['q']}", []).append(label)
    if gaps:
        for who, items in gaps.items():
            print(f"    {who:<16} → " + ", ".join(items))
    else:
        print("    none — full coverage.")

print("\n" + "=" * 96)
print("  READING IT")
print("=" * 96)
print("""
  OCF/C = 1.00  is THE THRESHOLD. Above it the buildout is self-funded out of the
                business. Below it, every marginal dollar comes from a bond desk or
                a share sale — the state the vault documented on 8/6 (Google's first
                negative-FCF quarter since its 2004 IPO; Alphabet's $25B jumbo bond
                drawing $115B of demand; the GS chart of all five going negative).

  E/C  falling  is ambiguous ALONE. Decompose it:
                  DA/C rising  → the old capex is hitting the P&L (mechanical, expected)
                  DA/C flat    → earnings are deteriorating for a REAL reason
                That distinction is the difference between a depreciation wave and
                a demand problem, and E/C alone cannot see it.

  CQ            is the one that catches earnings quality. A capital-intensive company
                should generate MORE cash than accounting profit, by roughly D&A.
                When it generates LESS — CQ below 1.0, or negative — the earnings
                contain something that is not cash. Mark-to-market gains on private
                equity stakes are the current example.

  C/R           intensity. Vault comparators: SPCX 2.35x · ORCL ~1.0x · MSFT ~0.7x.

  ⚠️ THE THREE THINGS THAT WOULD CHANGE THE VERDICT AND ARE NOT YET IN HAND:
     1. META finance leases — undisclosed. Would push true capex UP and OCF/C DOWN.
     2. ORCL on a calendar basis — its fiscal quarters genuinely do not align; the
        numbers here are period-subtraction derivations, not disclosed quarterlies.
     3. MSFT's 15→25y building-life extension, effective 2026-07-01 — it lands in
        calendar Q3, lowers depreciation, and RAISES reported earnings without any
        change in cash. Watch E/C rise while OCF/C does not.
""")
print("  GS/FactSet combined-FCF cross-check ($bn/qtr, chart-read — sign is what matters):")
for k, v in GS_COMBINED_FCF_BN.items():
    print(f"    {k:<9} {v:>6}   {'← COMBINED NEGATIVE (OCF/C < 1.00 across the complex)' if v < 0 else ''}")
print("=" * 96)
