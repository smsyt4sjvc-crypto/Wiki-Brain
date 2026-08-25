#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
#  CURVE — the Treasury par curve as a SPREAD series, from the primary source.
#  (Jake, 2026-08-18: "Build it")
#
#  WHY: rates-board carried LEVELS only. A "bear steepening" claim is about a
#  SPREAD, so every steepening claim was someone else's chart. This builds
#  2s10s / 2s30s / 5s30s / 10s30s from Treasury.gov daily par yields (1990→),
#  and CLASSIFIES the daily regime so "bear steepening" stops being a vibe:
#
#      Δlong > 0 and Δshort > 0 and Δlong > Δshort   -> BEAR STEEPENING
#      Δlong < 0 and Δshort < 0 and Δlong < Δshort   -> BULL STEEPENING
#      Δlong > 0 and Δshort > 0 and Δlong < Δshort   -> BEAR FLATTENING
#      Δlong < 0 and Δshort < 0 and Δlong > Δshort   -> BULL FLATTENING
#      (mixed signs -> TWIST)
#
#  ⚠️ SOURCE DISCIPLINE: Treasury.gov daily par yield curve is the PRIMARY.
#  TVC/TradingView and vendor summaries are not. The 8/18 30Y print was
#  confirmed against this file before the vault trusted the decimal.
#
#  USAGE
#    python3 tools/curve.py                     # current levels + spreads + regime
#    python3 tools/curve.py --episodes          # distinct bear-steepening episodes
#    python3 tools/curve.py --window 60         # change the smoothing window (days)
# ═══════════════════════════════════════════════════════════════════════════
import os, sys, csv, datetime as dt

SP = os.environ.get('TSY_DIR') or '/tmp/claude-0/-home-user-INMA-/94323c36-2246-5405-881a-07e84a3f61c5/scratchpad/tsy'
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load():
    rows = {}
    for fn in sorted(os.listdir(SP)):
        if not fn.endswith('.csv'):
            continue
        with open(os.path.join(SP, fn), newline='', errors='replace') as fh:
            for r in csv.DictReader(fh):
                d = r.get('Date')
                if not d:
                    continue
                try:
                    date = dt.datetime.strptime(d.strip(), '%m/%d/%Y').date()
                except ValueError:
                    continue
                def g(k):
                    v = (r.get(k) or '').strip()
                    try:
                        return float(v)
                    except ValueError:
                        return None
                rows[date] = {'2': g('2 Yr'), '5': g('5 Yr'), '10': g('10 Yr'), '30': g('30 Yr')}
    return [(d, rows[d]) for d in sorted(rows)]


def spreads(rows):
    out = []
    for d, v in rows:
        if v['2'] is None:
            continue
        s = {'date': d, '2': v['2'], '10': v['10'], '30': v['30'], '5': v['5']}
        s['2s10s'] = (v['10'] - v['2']) * 100 if v['10'] is not None else None
        s['2s30s'] = (v['30'] - v['2']) * 100 if v['30'] is not None else None
        s['5s30s'] = (v['30'] - v['5']) * 100 if (v['30'] is not None and v['5'] is not None) else None
        out.append(s)
    return out


def regime(dl, ds):
    """dl = change in the LONG yield, ds = change in the SHORT yield (both in bp)."""
    if dl > 0 and ds > 0:
        return 'BEAR STEEPENING' if dl > ds else 'BEAR FLATTENING'
    if dl < 0 and ds < 0:
        return 'BULL STEEPENING' if dl < ds else 'BULL FLATTENING'
    return 'TWIST'


def episodes(S, win=60, min_steep=25, min_rise=25, gap=90):
    """A bear-steepening EPISODE: over a `win`-day window the long yield ROSE by at least
    `min_rise` bp, the short yield also rose, and the 2s30s spread WIDENED by at least
    `min_steep` bp. Consecutive qualifying days within `gap` days collapse into one episode.
    ⇒ Thresholds are stated, so the sample is REPRODUCIBLE — which is precisely what the
    '4 episodes since 1962' claim never supplied."""
    idx = {i: s for i, s in enumerate(S)}
    hits = []
    for i in range(win, len(S)):
        a, b = idx[i - win], idx[i]
        if None in (a['2s30s'], b['2s30s'], a['30'], b['30']):
            continue
        d30 = (b['30'] - a['30']) * 100
        d2 = (b['2'] - a['2']) * 100
        dsp = b['2s30s'] - a['2s30s']
        if d30 >= min_rise and d2 > 0 and dsp >= min_steep:
            hits.append(b['date'])
    eps, cur = [], []
    for d in hits:
        if cur and (d - cur[-1]).days > gap:
            eps.append((cur[0], cur[-1])); cur = []
        cur.append(d)
    if cur:
        eps.append((cur[0], cur[-1]))
    return eps


def main():
    a = sys.argv[1:]
    win = int(a[a.index('--window') + 1]) if '--window' in a else 60
    S = spreads(load())
    if not S:
        print('  no data — set TSY_DIR or re-download Treasury CSVs'); return
    last = S[-1]
    print(f"  TREASURY PAR CURVE — PRIMARY SOURCE (treasury.gov). {len(S):,} trading days "
          f"{S[0]['date']} → {last['date']}\n")
    print(f"  LATEST {last['date']}:  2Y {last['2']:.2f}  5Y {last['5']:.2f}  "
          f"10Y {last['10']:.2f}  30Y {last['30']:.2f}")
    print(f"    2s10s {last['2s10s']:+.0f}bp    2s30s {last['2s30s']:+.0f}bp    5s30s {last['5s30s']:+.0f}bp")
    for lbl, n in (('1 week', 5), ('1 month', 21), ('3 months', 63), ('6 months', 126)):
        if len(S) > n and S[-1 - n]['2s30s'] is not None:
            p = S[-1 - n]
            d30 = (last['30'] - p['30']) * 100; d2 = (last['2'] - p['2']) * 100
            print(f"    {lbl:<9} 2s30s {p['2s30s']:+7.0f} → {last['2s30s']:+.0f}  "
                  f"({last['2s30s'] - p['2s30s']:+.0f}bp)   30Y {d30:+6.1f}bp  2Y {d2:+6.1f}bp"
                  f"   ⇒ {regime(d30, d2)}")
    hist = [s['2s30s'] for s in S if s['2s30s'] is not None]
    pct = sum(1 for v in hist if v < last['2s30s']) / len(hist) * 100
    print(f"\n    2s30s percentile since {S[0]['date'].year}: {pct:.0f}th  "
          f"(min {min(hist):+.0f} / max {max(hist):+.0f})")
    if '--episodes' in a:
        eps = episodes(S, win=win)
        print(f"\n  BEAR-STEEPENING EPISODES — stated rule: over {win} trading days the 30Y rose ≥25bp,")
        print(f"  the 2Y also rose, and 2s30s widened ≥25bp. Episodes ≥90 days apart are distinct.")
        print(f"  ⇒ {len(eps)} DISTINCT EPISODES since {S[0]['date'].year} (data starts 1990):\n")
        for s, e in eps:
            print(f"     {s} → {e}   ({(e - s).days:>4}d)")


if __name__ == '__main__':
    main()
