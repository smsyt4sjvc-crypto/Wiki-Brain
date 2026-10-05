#!/usr/bin/env python3
"""MIM — MONEY IN THE MORNING (rule 16f, Jake 2026-10-05: "New section after close every day: MIM.
Money in the morning. We run a material scan at 9:00 PM Pacific time, round out the day's news —
bond close, macro, market, business news, etc. — scan ZH and decide if there's anywhere worth
putting money at the open in the morning.")

  python3 tools/mim.py            # INPUTS: ZH headlines since the US close · tape (book, flag names,
                                  #   core five) · today's chat-log shape · flags due in ≤3 days ·
                                  #   the previous MIM's calls (grade them first)
  python3 tools/mim.py --new      # scaffold mim/<today Pacific>.md (does not overwrite)
  python3 tools/mim.py --since 13 # ZH headlines since HH (Pacific) — default 13 (the US close)

Token-free fetch. The READ, the "where money goes" call and the precise prediction are written in
session (librarian first on anything material). Runs IN SESSION when Jake opens at ~9pm PT — never
as a cron/Routine (rule 15).
"""
import re, sys, json, html, argparse, pathlib, subprocess, email.utils
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
PT = ZoneInfo("America/Los_Angeles")
sys.path.insert(0, str(ROOT / "tools"))

BOOK = ["SPY", "QQQ", "PARR", "DHT", "CEG", "VST", "TLN", "VG"]
CORE = ["CL=F", "BZ=F", "SPY", "QQQ", "SOXX", "MU", "^TNX", "^TYX", "^VIX", "TLT", "HYG", "IWM", "RSP", "DX-Y.NYB", "GLD"]
FLAGS = ["FRO", "NAT", "BWET", "BNO", "VLO", "MPC", "DINO", "PBF", "LEN", "DHI", "UAL", "AVGO", "CRWV", "META", "INTC", "TSM", "EWZ", "PSKY"]
UA = "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1"


def now_pt():
    return datetime.now(PT)


def zh_headlines(since_hour):
    """Feedburner RSS (lags) + the homepage listing; returns [(pt_time_or_None, title, path)]."""
    out = []
    try:
        xml = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0", "--max-time", "30",
                              "https://feeds.feedburner.com/zerohedge/feed"], capture_output=True, text=True).stdout
        for it in re.findall(r"<item>(.*?)</item>", xml, re.S):
            t = re.search(r"<title>(.*?)</title>", it, re.S); l = re.search(r"<link>(.*?)</link>", it, re.S)
            d = re.search(r"<pubDate>(.*?)</pubDate>", it, re.S)
            if not (t and l):
                continue
            title = html.unescape(re.sub(r"<!\[CDATA\[|\]\]>", "", t.group(1))).strip()
            dt = email.utils.parsedate_to_datetime(d.group(1)).astimezone(PT) if d else None
            out.append((dt, title, l.group(1).strip().replace("https://www.zerohedge.com", "")))
    except Exception as e:
        print(f"  (rss failed: {e})")
    try:
        page = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "30", "https://www.zerohedge.com/"],
                              capture_output=True, text=True).stdout
        seen = {p for _, _, p in out}
        for m in re.finditer(r'href="(/(?:markets|geopolitical|energy|economics|political|military|ai|commodities|news)/[^"#?]+)"[^>]*>([^<]{15,160})<', page):
            path, title = m.group(1), html.unescape(m.group(2)).strip()
            if path not in seen and title:
                seen.add(path); out.append((None, title, path))
    except Exception as e:
        print(f"  (homepage failed: {e})")
    cutoff = now_pt().replace(hour=since_hour, minute=0, second=0, microsecond=0)
    dated = [x for x in out if x[0] and x[0] >= cutoff]
    undated = [x for x in out if x[0] is None]
    dated.sort(key=lambda x: x[0], reverse=True)
    return dated, undated


def tape(tickers):
    import tape as T
    rows = []
    for tk in tickers:
        try:
            r = T._fetch(tk, "5d"); m = r["meta"]; q = r["indicators"]["quote"][0]
            c = [x for x in q["close"] if x]
            px = m.get("regularMarketPrice") or c[-1]
            prev = c[-2] if len(c) > 1 else None
            rows.append((tk, px, (px / prev - 1) * 100 if prev else None,
                         datetime.fromtimestamp(m.get("regularMarketTime", 0), tz=timezone.utc).astimezone(PT).strftime("%H:%M")))
        except Exception:
            rows.append((tk, None, None, ""))
    return rows


def flags_due(days=3):
    sys.path.insert(0, str(ROOT / "tools"))
    import menu as M
    t = now_pt().date(); horizon = t + timedelta(days=days)
    live = [f for f in M.parse_board() if f["status"].upper().startswith("LIVE")]
    due = [f for f in live if any(t <= d <= horizon for d in f["dates"])]
    due.sort(key=lambda f: min(d for d in f["dates"] if d >= t))
    return due


def prior_mim(today):
    d = ROOT / "mim"
    files = sorted(p for p in d.glob("20??-??-??.md") if p.stem < today.isoformat()) if d.exists() else []
    return files[-1] if files else None


def chat_shape(today):
    p = ROOT / "chat-log" / f"{today.isoformat()}.md"
    if not p.exists():
        return []
    txt = p.read_text()
    sec = txt.split("## SESSION SHAPE", 1)[1].split("\n## ", 1)[0] if "## SESSION SHAPE" in txt else ""
    return [l[:160] for l in sec.splitlines() if l.startswith("- ")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", action="store_true")
    ap.add_argument("--since", type=int, default=13)
    ap.add_argument("--out", help="write the scaffold here instead of mim/ (testing)")
    a = ap.parse_args()
    n = now_pt(); t = n.date()
    print(f"MIM INPUTS — {n:%Y-%m-%d %H:%M %Z}  (Money In the Morning; decide where money goes at the open)\n")

    prev = prior_mim(t)
    if prev:
        print(f"① GRADE FIRST — the previous MIM: mim/{prev.name}")
        for line in prev.read_text().splitlines():
            if line.startswith("- **Call") or line.startswith("- **Prediction"):
                print("   " + line[:220])
        print()

    print("② THE DAY AS FILED (chat-log SESSION SHAPE):")
    for l in chat_shape(t)[-14:]:
        print("   " + l)
    print()

    print("③ TAPE (last · % vs prior close · PT time):")
    for grp, tks in (("book", BOOK), ("core", CORE), ("flags", FLAGS)):
        rows = tape(tks)
        print(f"   {grp}: " + " · ".join(f"{tk} {px:.2f} ({chg:+.1f}%)" if px and chg is not None else f"{tk} n/a" for tk, px, chg, _ in rows))
    print()

    due = flags_due()
    print("④ FLAGS DUE IN ≤3 DAYS (from wiki/flag-board.md):")
    for f in due:
        nxt = min(d for d in f["dates"] if d >= t)
        print(f"   {nxt}  {f['name'][:70]}\n              🟢 {f['green'][:120]}\n              🔴 {f['red'][:120]}")
    print()

    dated, undated = zh_headlines(a.since)
    print(f"⑤ ZH SINCE {a.since:02d}:00 PT (RSS, dated):")
    for dt, title, path in dated[:30]:
        print(f"   {dt:%H:%M}  {title[:110]}  {path}")
    print(f"   + homepage items without a timestamp ({len(undated)}):")
    for _, title, path in undated[:25]:
        print(f"          {title[:110]}  {path}")
    print("\n⑥ WRITE THE MIM: round-out (bonds · close · macro · market · business) → ZH read → THE CALL"
          " (name · side · entry · limit ~+3% · stop ~−3% · the precise prediction · when) or NO TRADE, with the"
          " disconfirmer named. Librarian on anything material. Filed → chat-log → commit → push.")

    if a.new or a.out:
        path = pathlib.Path(a.out) if a.out else ROOT / "mim" / f"{t.isoformat()}.md"
        if path.exists() and not a.out:
            print(f"\n(exists — not overwritten) {path}")
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"# MIM — Money In the Morning — {t:%a %Y-%m-%d} (built ~{n:%-I:%M%p} PT; for the {(t + timedelta(days=1)):%a %m/%d} open)",
                 "", "*Rule 16f. The 9pm round-out of the day, the ZH scan, and the decision: is there anywhere worth putting money at the open? Registered at build; graded in the next MIM; never edited. Book lines name ACTUAL or PAPER.*",
                 "", "## Graded from the previous MIM", "- (none / grade each call: level hit? mechanism fired?)",
                 "", "## Round-out of the day", "- **Bonds:** ", "- **Close:** ", "- **Macro:** ", "- **Market internals:** ", "- **Business:** ", "- **War / oil:** ",
                 "", "## ZH since the close (material only)", "- ",
                 "", "## THE BOOK tonight", "- ",
                 "", "## 💰 WHERE MONEY GOES AT THE OPEN", "- **Call 1:** NAME · side · entry ≤ · limit (+3%) · stop (−3%) · out by · **Prediction:** … · **Disconfirmer:** …",
                 "- **NO TRADE if:** ", "", "## Not tonight (and why)", "- ", ""]
        path.write_text("\n".join(lines))
        print(f"\nscaffold → {path}")


if __name__ == "__main__":
    main()
