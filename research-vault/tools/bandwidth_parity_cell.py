#!/usr/bin/env python3
# ==============================================================================
#  BANDWIDTH-PARITY TEST — what unit does the GPU rental market actually price?
#  Built 2026-08-12 ~10:45pm PDT. Paste the whole cell into Colab and run.
#
#  WHY THIS EXISTS
#  ---------------
#  On 8/12 I found, from THREE chips, that GPU rental prices track MEMORY
#  BANDWIDTH far more tightly than they track FLOPS (floating-point operations
#  per second):
#        $/(GB/s)-hour spread across A100 / H100 / B200 ......  12%
#        $/TFLOP-hour  spread across the same three .........  86%
#  and that the A100's $1.29 index price sits within 1% of its bandwidth-parity
#  price against a B200.
#
#  ⛔ THAT RESULT IS NOT YET EVIDENCE. n=3, I chose the rate points, and
#     bandwidth was the THIRD metric I tried. That is a multiple-comparisons
#     problem — the same trap as the monotone sweep in the pre-earnings study,
#     where a tightening axis concentrated the sample and manufactured a signal.
#     A conclusion found on the third try needs a bigger sample BEFORE it is
#     load-bearing. This cell is that sample.
#
#  WHAT IT DOES
#  ------------
#  For every SKU (stock-keeping unit — a specific chip model) it computes price
#  per unit of each candidate metric, then asks which metric makes price most
#  CONSTANT across the fleet. Two independent scorers, because either alone can
#  mislead:
#     1. CV  = coefficient of variation of price-per-unit (lower = better unit)
#     2. R^2 of log(price) ~ log(metric)  (higher = better explanatory variable)
#  It also runs a LEAVE-ONE-OUT check, because with a small n a single SKU can
#  carry the whole result.
#
#  ⚠️ SPECS ARE HARD-CODED AND VERIFIABLE. RATES ARE NOT — edit RATES below with
#     whatever source you trust. The specs are published datasheet numbers; the
#     rates are the soft input and they are where this test can be gamed.
# ==============================================================================

import math

# ------------------------------------------------------------------ 1. SPECS
# name: (FP16 dense TFLOPS, best low-precision TOPS/TFLOPS, HBM/GDDR GB/s, TDP watts, HBM GB)
# TFLOPS = trillion floating-point operations per second (dense, no sparsity).
# Low-precision column is the chip's BEST inference format: INT8 (8-bit integer)
# for Ampere, FP8 for Hopper/Ada, FP4 for Blackwell. Comparing across formats is
# a real apples-to-oranges problem — that is why it is a SEPARATE column, and why
# a chip with no FP4 is not penalised twice.
SPECS = {
    "V100 SXM2 32GB":  (  125,     0,   900,  300,  32),
    "A10 24GB":        (  125,   250,   600,  150,  24),
    "L4 24GB":         (  121,   242,   300,   72,  24),
    "A100 40GB SXM":   (  312,   624,  1555,  400,  40),
    "A100 80GB SXM":   (  312,   624,  2039,  400,  80),
    "A100 80GB PCIe":  (  312,   624,  1935,  300,  80),
    "L40S 48GB":       (  362,   733,   864,  350,  48),
    "H100 PCIe 80GB":  (  756,  1513,  2000,  350,  80),
    "H100 SXM 80GB":   (989.5,  1979,  3350,  700,  80),
    "H200 SXM 141GB":  (989.5,  1979,  4800,  700, 141),
    "MI300X 192GB":    ( 1307,  2615,  5300,  750, 192),
    "B200 180GB":      ( 2250,  9000,  8000, 1000, 180),
}

# ------------------------------------------------------------- 2. RATES ⚠️ EDIT
# $/GPU-hour. SOURCED = I pulled it 8/12 and it is in the vault. PLACEHOLDER =
# a plausible market number I did NOT verify — replace before trusting output.
# Delete any line you cannot source; the test is stronger with 8 real rows than
# 12 rows where 4 are invented.
RATES = {
    "A100 80GB SXM":   (1.29, "SOURCED  Silicon Data A100 index SDA100RT, 8/12"),
    "H100 SXM 80GB":   (2.35, "SOURCED  independent tracker, Mar-2026"),
    "B200 180GB":      (5.00, "PLACEHOLDER  mid of a wide quoted range"),
    "A100 80GB PCIe":  (1.19, "SOURCED  CoreWeave published pricing, 8/12"),
    "H100 PCIe 80GB":  (1.99, "PLACEHOLDER"),
    "H200 SXM 141GB":  (3.10, "PLACEHOLDER"),
    "L40S 48GB":       (1.10, "PLACEHOLDER"),
    "L4 24GB":         (0.43, "PLACEHOLDER"),
    "A10 24GB":        (0.75, "PLACEHOLDER"),
    "MI300X 192GB":    (2.20, "PLACEHOLDER"),
    "V100 SXM2 32GB":  (0.55, "PLACEHOLDER"),
}

# --------------------------------------------------------------- 3. THE TEST
METRICS = [
    ("MEMORY BANDWIDTH",   lambda s: s[2],            "GB/s"),
    ("FP16 COMPUTE",       lambda s: s[0],            "TFLOPS"),
    ("LOW-PRECISION",      lambda s: s[1],            "TOPS"),
    ("POWER (TDP)",        lambda s: s[3],            "watts"),
    ("MEMORY CAPACITY",    lambda s: s[4],            "GB"),
    ("BANDWIDTH x CAPACITY", lambda s: s[2]*s[4]/1e3, "GB/s*TB"),
]

def stats(xs):
    n = len(xs); m = sum(xs)/n
    sd = math.sqrt(sum((x-m)**2 for x in xs)/(n-1)) if n > 1 else 0.0
    return m, sd, (sd/m if m else float("nan"))

def loglog_r2(xs, ys):
    """R^2 of log(y) ~ log(x). Returns (r2, slope). Log-log because a doubling
    of bandwidth costing double is a CONSTANT unit price — that is linear in
    logs, not in levels."""
    pts = [(math.log(x), math.log(y)) for x, y in zip(xs, ys) if x > 0 and y > 0]
    n = len(pts)
    if n < 3: return float("nan"), float("nan")
    mx = sum(p[0] for p in pts)/n; my = sum(p[1] for p in pts)/n
    sxy = sum((p[0]-mx)*(p[1]-my) for p in pts)
    sxx = sum((p[0]-mx)**2 for p in pts)
    if sxx == 0: return float("nan"), float("nan")
    slope = sxy/sxx
    syy = sum((p[1]-my)**2 for p in pts)
    return (sxy**2/(sxx*syy) if syy else float("nan")), slope

def run(rows, label, verbose=True):
    names = list(rows)
    px    = [RATES[n][0] for n in names]
    out   = []
    for mname, getter, unit in METRICS:
        vals = [getter(SPECS[n]) for n in names]
        keep = [(p, v) for p, v in zip(px, vals) if v > 0]
        if len(keep) < 3:
            continue
        per  = [p/v for p, v in keep]
        _, _, cv = stats(per)
        r2, slope = loglog_r2([v for _, v in keep], [p for p, _ in keep])
        out.append((cv, r2, slope, mname, unit, len(keep)))
    out.sort(key=lambda r: r[0])
    if verbose:
        print(f"\n{label}")
        print("-"*78)
        print(f"  {'unit of account':<22}{'n':>3}{'CV of $/unit':>14}{'R^2 log-log':>13}{'slope':>8}")
        for cv, r2, slope, mname, unit, n in out:
            flag = "  <-- BEST" if (cv, r2, slope, mname, unit, n) == out[0] else ""
            print(f"  {mname:<22}{n:>3}{cv:>13.1%}{r2:>13.3f}{slope:>8.2f}{flag}")
    return out

def main():
    rows = {n: v for n, v in RATES.items() if n in SPECS}
    print("="*78)
    print("  BANDWIDTH-PARITY TEST — which unit does the rental market price?")
    print("="*78)
    ph = [n for n in rows if RATES[n][1].startswith("PLACEHOLDER")]
    print(f"  {len(rows)} SKUs priced.  ⚠️ {len(ph)} of them use PLACEHOLDER rates:")
    print(f"     {', '.join(ph) if ph else '(none)'}")
    print("  ⛔ Every PLACEHOLDER is a number I invented. Replace them or delete the row.")
    print("     A clean result built on invented rates is a clean result about my priors.")

    print("\n  PRICE PER UNIT, BY SKU")
    print("-"*78)
    print(f"  {'SKU':<18}{'$/hr':>7}{'$/(GB/s)k':>11}{'$/TFLOP':>10}{'$/kW':>8}{'$/GB':>8}")
    for n in sorted(rows, key=lambda k: SPECS[k][2]):
        s, p = SPECS[n], RATES[n][0]
        print(f"  {n:<18}{p:>7.2f}{p/s[2]*1000:>11.3f}{p/s[0]*1000:>10.3f}"
              f"{p/s[3]*1000:>8.2f}{p/s[4]:>8.3f}")

    full = run(rows, "ALL SKUs — lower CV and higher R^2 both favour the true unit")

    # ---- LEAVE-ONE-OUT: with a small n, one SKU can carry the whole answer.
    print("\n\n  LEAVE-ONE-OUT — does the winner survive dropping any single SKU?")
    print("-"*78)
    winners = {}
    for drop in rows:
        sub = {k: v for k, v in rows.items() if k != drop}
        if len(sub) < 4: continue
        res = run(sub, "", verbose=False)
        if res:
            w = res[0][3]
            winners[w] = winners.get(w, 0) + 1
            print(f"  drop {drop:<20} -> winner: {w:<22} CV {res[0][0]:>6.1%}")
    print("-"*78)
    if winners:
        top, cnt = max(winners.items(), key=lambda kv: kv[1])
        tot = sum(winners.values())
        print(f"  {top} wins {cnt}/{tot} leave-one-out runs.")
        if cnt < tot:
            print(f"  ⚠️ NOT UNANIMOUS — the answer depends on which SKU is in the sample.")
            print(f"     Others that won: {', '.join(k for k in winners if k != top)}")

    # ---- THE VERDICT, stated so it cannot be over-read.
    print("\n" + "="*78)
    if full:
        best_cv, best_r2, _, best_name, _, n = full[0]
        second_cv = full[1][0] if len(full) > 1 else float("inf")
        print(f"  BEST UNIT: {best_name}   (CV {best_cv:.1%}, R^2 {best_r2:.3f}, n={n})")
        print(f"  Runner-up CV {second_cv:.1%} -> separation {second_cv/best_cv:.1f}x")
        if second_cv/best_cv < 1.5:
            print("  ⛔ SEPARATION UNDER 1.5x = NOT A RESULT. Two metrics explain price")
            print("     about equally well, which is what you expect when they are")
            print("     correlated with each other (bandwidth and FLOPS both scale with")
            print("     die size). Do NOT report a winner.")
        elif n < 8:
            print("  ⚠️ n < 8. Directional only. The 8/12 finding was n=3 and that was")
            print("     never enough to conclude from.")
        else:
            print("  ★ Separation is real at this sample size. THIS IS STILL NOT CAUSAL:")
            print("     bandwidth may be a PROXY for whatever actually sets price")
            print("     (die area, HBM stack count, vendor list-price policy).")
    print("\n  ⬜ THE FALSIFIER THIS WAS BUILT TO RUN, from ai-financing-fragility 8/12:")
    print("     if GPUs price on bandwidth, $/(GB/s)-hour should be flat across SKUs")
    print("     AND BACK THROUGH TIME. This cell tests the cross-section only.")
    print("     The TIME leg needs historical rates and is the harder, better test —")
    print("     a cross-section can be flat because vendors COPY each other's pricing.")
    print("="*78)

main()
