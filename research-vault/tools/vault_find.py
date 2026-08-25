#!/usr/bin/env python3
"""
VAULT FIND — the "folder" for any entity, materialised on demand.

Jake, 2026-08-11: "Can we create folders and a search function like a typical OS? If I upload
meta earnings you search 'meta' and the folder comes up? Easier than scanning?"

YES to the outcome. NO to folders as the mechanism, and the reason is structural:

  A FILE LIVES IN EXACTLY ONE FOLDER. AN ENTITY APPEARS IN MANY THREADS.

META's story is spread across ai-capex-cycle (the 7/29 earnings crash), ai-financing-fragility
(the BlackRock JV moving capex off balance sheet), cepi (FCF ~zero), compression-thesis (open
source strategy), market-fragility (today's tape), portfolio-state (basket weight). A physical
wiki/meta/ folder forces a choice: fragment the THREADS, or duplicate the entries. Both are
worse than what the vault has, because the vault's value is the cross-thread synthesis — the
threads ARE the product, and entities cut across them.

So: keep one-idea-per-file on disk, and generate the entity view on demand. A virtual folder
beats a real one here precisely because an entry can appear in several at once.

    python3 tools/vault_find.py META
    python3 tools/vault_find.py "data centre" --days 30
    python3 tools/vault_find.py MU --raw
"""
import re, sys, argparse, subprocess, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
WIKI, RAW = ROOT / "wiki", ROOT / "raw"
DATED = re.compile(r"(20\d{2})-(\d{2})-(\d{2})")

def grep(term, path):
    try:
        r = subprocess.run(["grep", "-rn", "--include=*.md", "-iF", term, str(path)],
                           capture_output=True, text=True, timeout=90)
        return r.stdout.splitlines()
    except Exception:
        return []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("term")
    ap.add_argument("--days", type=int, default=0, help="only entries dated within N days of the newest")
    ap.add_argument("--max", type=int, default=12, help="entries shown per section")
    ap.add_argument("--raw", action="store_true", help="also list matching raw/ artifacts")
    a = ap.parse_args()

    hits = grep(a.term, WIKI)
    if not hits:
        print(f"  no wiki mention of {a.term!r}. That is INFORMATION: either genuinely new")
        print(f"  territory (open a note) or the term is spelled differently here. It is never")
        print(f"  evidence the vault is silent — try a synonym before concluding anything.")
        return

    per_file = collections.Counter()
    dated, corrections, standing, flags = [], [], [], []
    for h in hits:
        try:
            f, ln, body = h.split(":", 2)
        except ValueError:
            continue
        name = str(pathlib.Path(f).relative_to(WIKI))
        per_file[name] += 1
        rec = (DATED.search(body).group(0) if DATED.search(body) else "", name, ln, body.strip())
        if body.lstrip().startswith("#") and rec[0]:
            dated.append(rec)
        if "⛔" in body:
            corrections.append(rec)
        if "★★★" in body:
            standing.append(rec)
        if "🚩" in body or "⬜" in body:
            flags.append(rec)

    print("=" * 96)
    print(f'  VAULT FIND — "{a.term}"     {len(hits)} mentions across {len(per_file)} notes')
    print("=" * 96)

    print("\n  📂 WHERE IT LIVES  (this IS the folder — ranked by weight of coverage)")
    for name, n in per_file.most_common(10):
        bar = "█" * min(int(n / max(1, per_file.most_common(1)[0][1]) * 30), 30)
        print(f"     {n:>4}  {name:<38} {bar}")

    def section(title, rows, note=""):
        if not rows:
            return
        rows = sorted(rows, key=lambda r: r[0], reverse=True)
        if a.days and rows and rows[0][0]:
            newest = rows[0][0]
            rows = [r for r in rows if r[0] and _within(r[0], newest, a.days)]
        print(f"\n  {title}  {note}")
        for d, name, ln, body in rows[:a.max]:
            stamp = d or "  (undated) "
            print(f"     {stamp}  {name}:{ln}")
            print(f"                  {body[:104]}")

    def _within(d, newest, days):
        try:
            from datetime import date
            a_ = date(*map(int, d.split("-"))); b_ = date(*map(int, newest.split("-")))
            return (b_ - a_).days <= days
        except Exception:
            return True

    globals()["_within"] = _within
    section("📅 DATED ENTRIES (newest first)", dated)
    section("⛔ CORRECTIONS", corrections, "— arguments already CLOSED. Do not re-derive.")
    section("★★★ STANDING CONCLUSIONS", standing, "— do not re-argue.")
    section("🚩 OPEN FLAGS / ⬜ NOT-KNOWN", flags, "— test new data against these.")

    if a.raw:
        names = [p.name for p in RAW.iterdir() if a.term.lower() in p.name.lower()]
        print(f"\n  🗃️  RAW ARTIFACTS matching the name ({len(names)}):")
        for n in sorted(names)[-15:]:
            print(f"     {n}")
        if not names:
            print("     none by FILENAME — raw/ is 178 flat files and names are inconsistent.")

    print("\n" + "=" * 96)
    print("  WHY THIS IS A VIEW AND NOT A FOLDER: a file lives in one folder; an entity appears")
    print("  in many threads. Generating the view keeps one-idea-per-file on disk AND lets the")
    print("  same entry show up under every entity it touches. Moving files would also break")
    print("  every [[wiki-link]] and all 67 vault_amend pointers.")
    print("=" * 96)

if __name__ == "__main__":
    main()
