#!/usr/bin/env python3
"""THE DAILY MENU — the vault's flags, ordered by when they can fire (rule 16e, Jake 2026-10-02).

Jake's spec: "daily at open we run the vault against prior days flags. We set a daily 'menu'. Stock
for that day and concise reasoning on why we're watching and the precise prediction that would need
to be made to catch that catalyst… then I can choose the one or two I find most compelling."

  python3 tools/menu.py              # LIVE flags from wiki/flag-board.md, nearest date first,
                                     # + the previous menu's predictions (grade them first)
  python3 tools/menu.py --days 10    # horizon for "dated" flags (default 10 calendar days)
  python3 tools/menu.py --new        # scaffold menu/<today Pacific>.md (does not overwrite)

Token-free. It only ORDERS the board; the menu's reasoning and the precise predictions are written in
session, from the board entries and the overnight inbound (librarian first).
"""
import re, sys, argparse, pathlib
from datetime import datetime, date, timedelta
from zoneinfo import ZoneInfo

ROOT = pathlib.Path(__file__).resolve().parent.parent
BOARD = ROOT / "wiki" / "flag-board.md"
MENUS = ROOT / "menu"


def today_pt():
    return datetime.now(ZoneInfo("America/Los_Angeles")).date()


def parse_board():
    text = BOARD.read_text()
    body = text.split("## FLAGS", 1)[1] if "## FLAGS" in text else text
    flags = []
    for blk in re.split(r"\n### ", body)[1:]:
        name = blk.split("\n", 1)[0].strip()
        field = {}
        for m in re.finditer(r"- \*\*([^:*]+):\*\*\s*(.*)", blk):
            field[m.group(1).strip()] = m.group(2).strip()
        when = field.get("When", "")
        dates = sorted(date.fromisoformat(d) for d in re.findall(r"\d{4}-\d{2}-\d{2}", when))
        flags.append(dict(name=name, when=when, dates=dates,
                          status=field.get("Status", ""), lean=field.get("Lean", ""),
                          green=field.get("🟢 IF", ""), red=field.get("🔴 IF", "")))
    return flags


def prior_menu(today):
    if not MENUS.exists():
        return None
    files = sorted(p for p in MENUS.glob("20??-??-??.md") if p.stem < today.isoformat())
    return files[-1] if files else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=10)
    ap.add_argument("--new", action="store_true")
    a = ap.parse_args()
    t = today_pt()
    horizon = t + timedelta(days=a.days)

    prev = prior_menu(t)
    print(f"DAILY MENU INPUTS — {t} (Pacific)\n")
    if prev:
        print(f"① GRADE FIRST — the previous menu: menu/{prev.name}")
        for line in prev.read_text().splitlines():
            if line.startswith("- **Prediction") or line.startswith("**Prediction"):
                print("   " + line[:220])
        print()

    live = [f for f in parse_board() if f["status"].upper().startswith("LIVE")]
    due = [f for f in live if any(t <= d <= horizon for d in f["dates"])]
    past = [f for f in live if f["dates"] and all(d < t for d in f["dates"])]
    windows = [f for f in live if f not in due and f not in past]
    due.sort(key=lambda f: min(d for d in f["dates"] if d >= t))

    print(f"② DATED — fires by {horizon}:")
    for f in due:
        nxt = min(d for d in f["dates"] if d >= t)
        print(f"   {nxt}  {f['name'][:70]}\n              lean: {f['lean'][:110]}")
    print("\n③ WINDOWS / undated (menu only if overnight news moved them):")
    for f in windows:
        print(f"   ····  {f['name'][:70]}")
    if past:
        print("\n⚠️ STALE — every date has passed but status is still LIVE (flip or re-date):")
        for f in past:
            print(f"   {f['dates'][-1]}  {f['name'][:70]}")

    if a.new:
        MENUS.mkdir(exist_ok=True)
        out = MENUS / f"{t.isoformat()}.md"
        if out.exists():
            print(f"\n{out.relative_to(ROOT)} exists — not overwritten.")
            return
        lines = [f"# Menu — {t.strftime('%a %Y-%m-%d')} (built ~__:__ PT)",
                 "", "*Drawn from [[flag-board]]. Each item: the names · why the vault is watching · the "
                 "precise prediction that catches the catalyst · when. Jake picks one or two. Registered "
                 "at build time; graded in the NEXT menu, never edited here.*", ""]
        if prev:
            lines += [f"## Graded from menu/{prev.name}", "- ", ""]
        lines += ["## On the menu", ""]
        for f in due:
            lines += [f"### {f['name']}", "- **Why watching:** ", "- **Prediction:** ", f"- **When:** {f['when']}", ""]
        lines += ["## Not on the menu today (and why)", "- ", ""]
        out.write_text("\n".join(lines) + "\n")
        print(f"\nscaffolded {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
