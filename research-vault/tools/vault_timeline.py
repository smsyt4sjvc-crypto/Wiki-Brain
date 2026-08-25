#!/usr/bin/env python3
# ============================================================================
#  VAULT TIMELINE — the vault as a CHRONOLOGY, not a pile.  (Jake, 2026-07-31)
#
#  THE ANSWER TO "is there a way without checking each time": THERE ALREADY WAS.
#  Git has stamped every line of this vault since day one. `git blame` gives the
#  exact commit time of any line. Nobody was reading it. This surfaces it.
#
#  WHAT IT DOES
#   1. Finds every dated entry header across wiki/ (the HAND-TYPED date).
#   2. Gets the GIT commit time of that exact line (the VERIFIED date).
#   3. Sorts the whole vault by GIT time -- one chronology across all notes.
#   4. ⚠️ FLAGS MISMATCHES. The vault's timestamp rule exists because I got the
#      clock wrong TWICE in one weekend. Git can catch that automatically instead
#      of relying on me to remember to run `date -u`.
#
#  WHY GIT TIME IS THE AUTHORITY AND THE HEADER IS NOT: the header is what I
#  TYPED; the commit is what HAPPENED. When they disagree, the header is wrong.
#  (One caveat, stated: a note WRITTEN about an EARLIER event legitimately has an
#  older header than its commit -- backfills. Those are flagged as BACKFILL, not
#  as errors, when the header PREDATES the commit. The dangerous direction is a
#  header from the FUTURE, or one that drifts days from its commit.)
#
#  USAGE
#    python3 tools/vault_timeline.py                 # last 40 entries, vault-wide
#    python3 tools/vault_timeline.py --days 3        # everything since 3 days ago
#    python3 tools/vault_timeline.py --check         # ONLY the mismatches
#    python3 tools/vault_timeline.py --file wiki/war/war-board.md
# ============================================================================
import subprocess, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATE_HDR = re.compile(r'^#{2,6}\s*.*?(\d{4}-\d{2}-\d{2})')

def sh(args):
    try:
        return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=60).stdout
    except Exception:
        return ''

def md_files(only=None):
    if only: return [only]
    out = []
    for dp, _, fn in os.walk(os.path.join(ROOT, 'wiki')):
        for f in fn:
            if f.endswith('.md'):
                out.append(os.path.relpath(os.path.join(dp, f), ROOT))
    return sorted(out)

def blame_dates(rel):
    """line-number -> (commit-date, sha) for one file, in ONE git call."""
    raw = sh(['git', 'blame', '--date=format:%Y-%m-%d %H:%M', '-l', '--', rel])
    out = {}
    for i, line in enumerate(raw.split('\n'), 1):
        m = re.match(r'^\^?([0-9a-f]{7,40})\s+.*?\((.*?)\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\s+\d+\)', line)
        if m: out[i] = (m.group(3), m.group(1)[:8])
    return out

def collect(only=None):
    rows = []
    for rel in md_files(only):
        try: lines = open(os.path.join(ROOT, rel), encoding='utf-8').read().split('\n')
        except Exception: continue
        bd = blame_dates(rel)
        for i, l in enumerate(lines, 1):
            m = DATE_HDR.match(l)
            if not m: continue
            hdr = m.group(1)
            git_dt, sha = bd.get(i, ('(uncommitted)', '--------'))
            title = re.sub(r'\s+', ' ', l.strip().lstrip('# ').replace('**', ''))
            rows.append(dict(file=rel, line=i, hdr=hdr, git=git_dt, sha=sha, title=title))
    rows.sort(key=lambda r: (r['git'], r['file'], r['line']))
    return rows

def classify(r):
    if r['git'].startswith('('): return 'UNCOMMITTED'
    gd = r['git'][:10]
    if r['hdr'] == gd: return 'OK'
    # ── TIMEZONE CROSSING, not a backfill. ──────────────────────────────────
    # First run flagged 216 entries as "BACKFILL +1d". They are not backfills:
    # a header stamped "~10:35pm PT" commits at ~05:35 UTC the NEXT calendar day.
    # PT is UTC-7/8, so any evening-PT header lands one UTC day later BY DESIGN.
    # Flagging that as a discrepancy would train me to ignore the whole report --
    # a check that cries wolf 216 times is worse than no check.
    if re.search(r'\b(PT|PDT|PST)\b', r['title']):
        try:
            if (datetime.date.fromisoformat(gd) -
                datetime.date.fromisoformat(r['hdr'])).days == 1 and r['git'][11:13] < '09':
                return 'OK'
        except Exception:
            pass
    try:
        d = (datetime.date.fromisoformat(gd) - datetime.date.fromisoformat(r['hdr'])).days
    except Exception:
        return 'UNPARSEABLE'
    if d > 0:  return f'BACKFILL +{d}d'      # header older than commit: legitimate
    return f'⚠️ FUTURE {-d}d'                # header AHEAD of commit: clock error

def main():
    a = sys.argv[1:]
    only = a[a.index('--file')+1] if '--file' in a else None
    rows = collect(only)
    days = int(a[a.index('--days')+1]) if '--days' in a else None
    if days:
        cut = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        rows = [r for r in rows if r['git'][:10] >= cut]
    if '--check' in a:
        bad = [r for r in rows if classify(r) not in ('OK', 'UNCOMMITTED')]
        print('=' * 100)
        print(f'  HEADER vs GIT MISMATCHES  ({len(bad)} of {len(rows)} dated entries)')
        print('  BACKFILL = header older than commit = a note written about an EARLIER event. Legitimate.')
        print('  ⚠️ FUTURE = header AHEAD of its own commit = a CLOCK ERROR. That is the one to fix.')
        print('=' * 100)
        for r in bad:
            print(f'  [{classify(r):<14}] hdr {r["hdr"]}  git {r["git"]}  {r["file"]}:L{r["line"]}')
            print(f'                   {r["title"][:88]}')
        if not bad: print('  none.')
        return
    n = 40 if not (days or only) else len(rows)
    show = rows[-n:]
    print('=' * 100)
    print(f'  VAULT TIMELINE — {len(rows)} dated entries, sorted by GIT commit time (the authority)')
    print(f'  showing {len(show)}. Git time is what HAPPENED; the header is what I TYPED.')
    print('=' * 100)
    last = None
    for r in show:
        d = r['git'][:10]
        if d != last:
            print(f'\n  ── {d} ' + '─' * 60); last = d
        st = classify(r)
        tag = '' if st in ('OK', 'UNCOMMITTED') else f' [{st}]'
        print(f'    {r["git"][11:]}  {r["sha"]}  {r["file"].replace("wiki/",""):<34} L{r["line"]:<5}{tag}')
        print(f'              {r["title"][:84]}')
    print('\n' + '=' * 100)
    print('  git blame gives this per-LINE for free. `--check` shows only clock mismatches.')
    print('=' * 100)

if __name__ == '__main__':
    try: main()
    except BrokenPipeError:
        try: sys.stdout.close()
        except Exception: pass
