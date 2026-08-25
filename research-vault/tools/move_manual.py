#!/usr/bin/env python3
"""
move_manual.py -- append a hand-fetched MOVE reading into the dashboard.

WHY THIS EXISTS. Every automated route to the MOVE index is blocked from a
datacentre IP: Yahoo 429s from this container AND from GitHub runners, CNBC 403s,
WSJ 401s, Nasdaq does not carry it, Stooq is JS-gated, and FRED's VXTYN was
discontinued in May 2020. MOVE is ICE BofA proprietary and has no free feed.

⭐ BUT WebFetch REACHES IT. WebFetch is a different fetcher, not this container's
curl, and Yahoo's quote page answers it. So the usual operator of this tool is
CLAUDE, in-session, not Jake -- verified 2026-08-22 against three stored values
(Aug 20 = 73.18 and Aug 19 = 71.26 both matched the CSV exactly).

⛔ WHAT THIS DOES NOT FIX: the weekday GitHub Action cannot call WebFetch. MOVE
is therefore a LIVE ROW THAT THE CRON CANNOT REFRESH, and it will lag on any day
Claude is not asked. The STALE flag is the honest signal that it did. A pasted
reading from Jake's phone (a residential IP) remains a valid second route.

USAGE
    python3 tools/move_manual.py 2026-08-21 73.40
    python3 tools/move_manual.py --from-paste "MOVE 73.40"       # date = today
    python3 tools/move_manual.py --status                        # what's missing

⚠️ A HAND-ENTERED ROW IS STILL DATA AND IS TREATED AS SUCH: it lands in the same
CSV as every fetched series and is scored identically. The provenance column is
what keeps that honest -- never silently mix it with a machine pull.
"""
import csv, os, sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SER  = os.path.join(ROOT, "data", "fragility", "series")
CSV  = os.path.join(SER, "move.csv")
PROV = os.path.join(ROOT, "data", "fragility", "move_provenance.csv")


def load():
    if not os.path.exists(CSV):
        return {}
    out = {}
    with open(CSV) as fh:
        for r in csv.DictReader(fh):
            try:
                out[r["date"]] = float(r["value"])
            except (ValueError, KeyError, TypeError):
                pass
    return out


def save(rows):
    os.makedirs(SER, exist_ok=True)
    with open(CSV, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "value"])
        w.writerows(sorted((d, round(v, 6)) for d, v in rows.items()))


def note_provenance(d, v):
    new = not os.path.exists(PROV)
    with open(PROV, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["date", "value", "entered_utc", "source"])
        w.writerow([d, v, datetime.utcnow().isoformat(timespec="seconds"), "manual"])


def status():
    rows = load()
    if not rows:
        print("move.csv is empty.")
        return
    last = max(rows)
    ld = datetime.strptime(last, "%Y-%m-%d").date()
    gap = (date.today() - ld).days
    print(f"MOVE last value : {rows[last]:.2f} on {last}  ({gap} days old)")
    missing = []
    d = ld + timedelta(days=1)
    while d < date.today():
        if d.weekday() < 5:
            missing.append(d.isoformat())
        d += timedelta(days=1)
    if missing:
        print(f"MISSING weekdays ({len(missing)}): {', '.join(missing[-10:])}")
        print("\nEach one is a row that cannot be recovered later -- MOVE has no "
              "history endpoint at any price.")
    else:
        print("No missing weekdays.")


def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__)
        return
    if a[0] == "--status":
        status()
        return

    if a[0] == "--from-paste":
        txt = " ".join(a[1:])
        # A date in the paste ALWAYS wins over "today". Quote widgets label a
        # stale close "today" -- Google printed "+0.22 (0.30%) today" beside a
        # quote stamped Aug 21 while it was Aug 22. Same failure class as the
        # MRNA header on 8/19: a field that does not belong to its neighbour.
        import re
        m = re.search(r"(\d{4}-\d{2}-\d{2})", txt)
        nums = [t for t in txt.replace(",", " ").split()
                if t.replace(".", "", 1).replace("-", "", 1).isdigit()
                and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", t)]
        if not nums:
            sys.exit(f"no number found in: {txt!r}")
        v = float(nums[-1])
        if m:
            d = m.group(1)
        else:
            d = date.today().isoformat()
            print(f"⚠️ No date in the paste -- assuming {d}. If this came off a "
                  f"quote page, USE ITS TIMESTAMP, not the word 'today'.")
    else:
        if len(a) < 2:
            sys.exit("usage: move_manual.py YYYY-MM-DD VALUE")
        d, v = a[0], float(a[1])
        datetime.strptime(d, "%Y-%m-%d")           # validate or raise

    dt = datetime.strptime(d, "%Y-%m-%d").date()
    if dt.weekday() >= 5:
        sys.exit(f"⛔ {d} is a {dt.strftime('%A')} -- the market was CLOSED and MOVE "
                 f"has no print. A quote page saying 'today' on a weekend is showing "
                 f"the LAST CLOSE. Use that session's date "
                 f"({(dt - timedelta(days=dt.weekday() - 4)).isoformat()}), not today's.")
    if dt > date.today():
        sys.exit(f"⛔ {d} is in the future.")

    if not (20 <= v <= 300):
        sys.exit(f"⛔ {v} is outside any plausible MOVE range (20-300). "
                 "Refusing -- check you did not paste a price or a percent.")

    rows = load()
    prev = rows.get(d)
    rows[d] = v
    save(rows)
    note_provenance(d, v)
    if prev is not None and abs(prev - v) > 1e-9:
        print(f"⚠️ OVERWROTE {d}: {prev:.2f} -> {v:.2f}")
    print(f"✅ MOVE {v:.2f} recorded for {d}  ({len(rows)} rows total)")
    print("\nNow run:  python3 tools/fragility.py")


if __name__ == "__main__":
    main()
