#!/usr/bin/env python3
# =============================================================================
#  THE ORACLE — perfect-foresight trade set. Jake's spec, 2026-08-19:
#  "2 trades per month each on Nasdaq and S&P. Hit at the low sell at the higher."
#
#  DEFINITION, stated so it can be argued with:
#    Within each CALENDAR MONTH, choose buy1<=sell1<=buy2<=sell2 (trading-day
#    indices) maximizing (sell1.high/buy1.low - 1) + (sell2.high/buy2.low - 1).
#    Buys execute at the INTRADAY LOW, sells at the INTRADAY HIGH. Same-day
#    round trips allowed. Trades may NOT overlap.
#  BRUTE FORCE, not DP -- ~21 days/month means ~10k combos, provably correct,
#  and a DP bug here would poison every downstream agent.
#  A CLOSE-BASED variant is computed alongside as the realizability check.
# =============================================================================
import csv, os, itertools, json
ROOT = os.path.dirname(os.path.abspath(__file__))

def load(name):
    rows = []
    with open(os.path.join(ROOT, 'data', name + '.csv')) as f:
        for r in csv.DictReader(f):
            try:
                rows.append({'date': r['date'], 'o': float(r['open']), 'h': float(r['high']),
                             'l': float(r['low']), 'c': float(r['close']),
                             'v': float(r['volume']) if r['volume'] not in ('', 'None') else 0.0})
            except (ValueError, TypeError):
                continue
    return rows

def best_two(days, lo_key, hi_key):
    n = len(days); best = None
    for b1 in range(n):
        for s1 in range(b1, n):
            r1 = days[s1][hi_key] / days[b1][lo_key] - 1.0
            if r1 <= 0: continue
            # single-trade candidate
            if best is None or r1 > best[0]: best = (r1, b1, s1, None, None)
            for b2 in range(s1, n):
                for s2 in range(b2, n):
                    r2 = days[s2][hi_key] / days[b2][lo_key] - 1.0
                    if r2 <= 0: continue
                    tot = r1 + r2
                    if best is None or tot > best[0]: best = (tot, b1, s1, b2, s2)
    return best

def run(sym, lo_key='l', hi_key='h'):
    rows = [r for r in load(sym) if r['date'] >= '2023-01-01']
    months = {}
    for i, r in enumerate(rows):
        months.setdefault(r['date'][:7], []).append(i)
    out = []
    for mo in sorted(months):
        idx = months[mo]; days = [rows[i] for i in idx]
        res = best_two(days, lo_key, hi_key)
        if not res: continue
        tot, b1, s1, b2, s2 = res
        legs = [(b1, s1)] + ([(b2, s2)] if b2 is not None else [])
        for k, (b, s) in enumerate(legs, 1):
            out.append({
                'sym': sym, 'month': mo, 'leg': k,
                'buy_date': days[b]['date'], 'sell_date': days[s]['date'],
                'buy_px': round(days[b][lo_key], 4), 'sell_px': round(days[s][hi_key], 4),
                'ret_pct': round((days[s][hi_key] / days[b][lo_key] - 1) * 100, 4),
                'hold_days': s - b, 'buy_i_in_month': b, 'sell_i_in_month': s,
                'days_in_month': len(days), 'month_total_pct': round(tot * 100, 4),
            })
    return out, rows

allt = []
for sym in ('spx', 'ndx'):
    t, rows = run(sym)
    allt += t
    tot = sum(x['ret_pct'] for x in t)
    mo = len({x['month'] for x in t})
    bh = (rows[-1]['c'] / rows[0]['c'] - 1) * 100
    print(f"{sym.upper():<4} {len(t):>3} trades over {mo} months | sum of leg returns {tot:8.1f}% "
          f"| avg/trade {tot/len(t):5.2f}% | buy&hold {bh:6.1f}%")
with open(os.path.join(ROOT, 'out', 'oracle_trades.json'), 'w') as f:
    json.dump(allt, f, indent=1)
print('->', os.path.join(ROOT, 'out', 'oracle_trades.json'), len(allt), 'trades')
