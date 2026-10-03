#!/usr/bin/env python3
"""THE 3% BOARD — which names can move >=3% tomorrow, and does a +3% limit / stop bracket pay on them.

Jake's spec (2026-10-02 ~9:15am PT): "a list of >=3% stocks... concentrate shares, limit sell at ~+3%,
with stop loss... the stock will either go, or not, either way I need to be disciplined to exit,
reassess and try again."

Two modes, both token-free (Yahoo daily bars via tools/tape.py's _fetch):

  python3 tools/three_pct_board.py                 # the DAILY LIST: reach rates, trend, volume
  python3 tools/three_pct_board.py --backtest      # the bracket rule on the same universe, 2y
  python3 tools/three_pct_board.py --tickers MU,PARR,DHT   # override the universe

DAILY LIST COLUMNS (last 60 sessions unless noted):
  up3   % of days the intraday HIGH reached open x 1.03   <- what a resting +3% limit sell needs
  dn2   % of days the intraday LOW reached open x 0.98    <- how often a -2% stop gets touched
  dn3   % of days the intraday LOW reached open x 0.97
  skew  up3 - dn3 — SYMMETRIC reach (+3 vs -3): positive = the tape has been reaching UP more than down.
        (up3 - dn2 is NOT used: a -2% stop is nearer than a +3% target, so it reads negative by construction.)
  atr%  14-day average true range / price
  trend price vs 20- and 50-day average ( ++ above both, -- below both )
  rvol  today's volume / 20-day average (on a live session, partial day reads LOW)

The script ranks; it does not know CATALYSTS. The catalyst + vault-lean column is added in session
from the money board (rule 16d) — the list is the mechanical half.

BACKTEST (daily bars, so the order of high/low inside a day is UNKNOWN):
  entry at the OPEN of day t; target +3%; stop -s; max hold H days, else exit at the close.
  A day that touches BOTH target and stop is counted as a STOP (conservative) and tallied.
  A gap through the stop exits at the OPEN (worse than -s); a gap through the target exits at the OPEN.
  No commissions (Fidelity $0), no slippage, no idle-cash yield. Trades overlap across days.
"""
import sys, statistics, argparse
from datetime import datetime, timezone

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from tape import _fetch  # noqa: E402

UNIVERSE = (
    # AI complex / semis / memory
    "NVDA,AMD,AVGO,MU,TSM,ARM,MRVL,ANET,SMCI,DELL,ORCL,CRWV,PLTR,"
    # megacaps
    "META,AMZN,GOOGL,MSFT,AAPL,TSLA,NFLX,"
    # power / nuclear
    "VST,CEG,TLN,OKLO,NNE,"
    # refiners / tankers / energy
    "PARR,VLO,MPC,PSX,PBF,DINO,DHT,FRO,"
    # rates / housing / airlines / other vault names
    "LEN,UAL,LLY,NOW,COIN,HOOD,MSTR"
).split(",")


def bars(ticker, rng="2y"):
    d = _fetch(ticker, rng)
    q = d["indicators"]["quote"][0]
    out = []
    for t, o, h, l, c, v in zip(d["timestamp"], q["open"], q["high"], q["low"], q["close"], q["volume"]):
        if None in (o, h, l, c) or o <= 0:
            continue
        out.append((datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%d"), o, h, l, c, v or 0))
    return out


def daily_row(tk, b, win=60):
    b60 = b[-win:]
    up3 = sum(1 for _, o, h, l, c, v in b60 if h >= o * 1.03) / len(b60)
    dn2 = sum(1 for _, o, h, l, c, v in b60 if l <= o * 0.98) / len(b60)
    dn3 = sum(1 for _, o, h, l, c, v in b60 if l <= o * 0.97) / len(b60)
    trs = []
    for i in range(len(b) - 14, len(b)):
        pc = b[i - 1][4]
        _, o, h, l, c, v = b[i]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    px = b[-1][4]
    atr = sum(trs) / len(trs) / px
    ma20 = sum(x[4] for x in b[-20:]) / 20
    ma50 = sum(x[4] for x in b[-50:]) / 50
    trend = ("+" if px > ma20 else "-") + ("+" if px > ma50 else "-")
    vol20 = sum(x[5] for x in b[-21:-1]) / 20 or 1
    rvol = b[-1][5] / vol20
    return dict(tk=tk, px=px, up3=up3, dn2=dn2, dn3=dn3, skew=up3 - dn3, atr=atr, trend=trend, rvol=rvol, date=b[-1][0])


def bracket(b, i, tgt=0.03, stop=0.02, hold=3):
    """Trade entered at the open of bar i. Returns (return, outcome, both_touched_flag)."""
    e = b[i][1]
    T, S = e * (1 + tgt), e * (1 - stop)
    for k in range(i, min(i + hold, len(b))):
        _, o, h, l, c, v = b[k]
        if k > i:  # gaps on later days
            if o <= S:
                return o / e - 1, "gapstop", False
            if o >= T:
                return o / e - 1, "gapwin", False
        hitT, hitS = h >= T, l <= S
        if hitT and hitS:
            return -stop, "stop", True
        if hitT:
            return tgt, "win", False
        if hitS:
            return -stop, "stop", False
    last = min(i + hold, len(b)) - 1
    return b[last][4] / e - 1, "timeout", False


def backtest(data, tgt, stop, hold, since=None, filt=None):
    rets, outs, amb = [], {}, 0
    for tk, b in data.items():
        for i in range(60, len(b) - hold):
            if since and b[i][0] < since:
                continue
            if filt and not filt(b, i):
                continue
            r, o, a = bracket(b, i, tgt, stop, hold)
            rets.append(r)
            outs[o] = outs.get(o, 0) + 1
            amb += a
    n = len(rets)
    if not n:
        return None
    wins = outs.get("win", 0) + outs.get("gapwin", 0)
    losses = outs.get("stop", 0) + outs.get("gapstop", 0)
    return dict(n=n, mean=statistics.mean(rets), win=wins / n, loss=losses / n,
                to=outs.get("timeout", 0) / n, amb=amb / n)


def f_atr3(b, i):  # yesterday's 14d ATR% >= 3%
    trs = [max(b[k][2] - b[k][3], abs(b[k][2] - b[k - 1][4]), abs(b[k][3] - b[k - 1][4])) for k in range(i - 14, i)]
    return sum(trs) / 14 / b[i - 1][4] >= 0.03


def f_uptrend(b, i):  # yesterday's close above its 20d and 50d average
    c = b[i - 1][4]
    return c > sum(x[4] for x in b[i - 20:i]) / 20 and c > sum(x[4] for x in b[i - 50:i]) / 50


def f_downtrend(b, i):
    c = b[i - 1][4]
    return c < sum(x[4] for x in b[i - 20:i]) / 20 and c < sum(x[4] for x in b[i - 50:i]) / 50


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tickers")
    ap.add_argument("--backtest", action="store_true")
    a = ap.parse_args()
    tks = a.tickers.split(",") if a.tickers else UNIVERSE
    data = {}
    for tk in tks:
        try:
            data[tk] = bars(tk, "2y" if a.backtest else "6mo")
        except Exception as ex:
            print(f"  {tk}: fetch failed ({ex})", file=sys.stderr)

    if not a.backtest:
        rows = sorted((daily_row(tk, b) for tk, b in data.items() if len(b) >= 60),
                      key=lambda r: (r["up3"] >= 0.25, r["skew"]), reverse=True)
        print(f"THE 3% BOARD — last bar {rows[0]['date'] if rows else '?'} — 60-session reach rates\n")
        print(f"{'ticker':7}{'price':>9}{'up3':>7}{'dn3':>7}{'skew':>7}{'dn2':>7}{'atr%':>7}  trend {'rvol':>6}")
        for r in rows:
            print(f"{r['tk']:7}{r['px']:>9.2f}{r['up3']:>7.0%}{r['dn3']:>7.0%}{r['skew']:>+7.0%}{r['dn2']:>7.0%}"
                  f"{r['atr']:>7.1%}  {r['trend']:5}{r['rvol']:>6.2f}")
        print("\nsorted: names reaching +3% on >=25% of days first, then by skew. up3/dn3 = HIGH/LOW reached "
              "open +/-3% · dn2 = a -2% stop touched · catalyst/lean added in session")
        return

    print(f"BRACKET BACKTEST — {len(data)} names, 2y daily bars, entry at the open\n")
    since6 = sorted(b[-126][0] for b in data.values() if len(b) > 126)[0]
    print(f"{'rule':34}{'n':>7}{'win':>7}{'stop':>7}{'t/o':>6}{'both':>6}{'mean/trade':>12}")
    for stop in (0.02, 0.03):
        for hold in (1, 3, 5):
            for label, filt, since in (("all days", None, None),
                                       ("ATR>=3%", f_atr3, None),
                                       ("uptrend (>20&50dma)", f_uptrend, None),
                                       ("downtrend (<20&50dma)", f_downtrend, None),
                                       ("all days, last 6mo", None, since6)):
                r = backtest(data, 0.03, stop, hold, since, filt)
                if r:
                    name = f"+3/-{stop*100:.0f} hold{hold} {label}"
                    print(f"{name:34}{r['n']:>7}{r['win']:>7.0%}{r['loss']:>7.0%}{r['to']:>6.0%}"
                          f"{r['amb']:>6.0%}{r['mean']:>+12.2%}")
        print()
    print("breakeven win rate (no timeouts): -2 stop = 40% · -3 stop = 50%. "
          "'both' = days touching target AND stop, scored as stops.")


if __name__ == "__main__":
    main()
