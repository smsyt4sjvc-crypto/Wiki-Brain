#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
#  THREAD ARC — a thread as a RUNNING HISTORY, oldest → newest.  (Jake, 2026-08-17)
#
#  HIS SPEC, VERBATIM:
#    "When I upload something related to bond yields, when you fetch 'bonds' from the
#     vault, it should walk you sequentially forward from the beginning to the new upload.
#     A running history of the movement gives us immediate relevance … By reading the
#     totality summary of the file from beginning to current, the upload is immediately
#     in perspective."
#
#  WHY THIS IS A THIRD RETRIEVAL SHAPE, NOT A TWEAK. The vault already had two:
#    • ROUTER      — newest N entries in a matched note      (recency)
#    • COLLISION   — figures already stated, oldest first    (a number's first commitment)
#  Neither gives the ARC. The router hands you the last thing said; the arc hands you the
#  WHOLE MOVEMENT, in order, so a new print is read as the NEXT TICK of a series rather
#  than as a standalone fact. On 8/17 a "10Y at 4.71%" arrived with no way to see that the
#  vault had walked 3.685% → 4.073% → 5.216% (30Y auction) over the preceding weeks.
#
#  TWO VIEWS, and the second is the one his phrase "history of the MOVEMENT" points at:
#    1. ARC     — every dated entry across the thread's notes, ascending, one line each.
#                 Long threads are compressed BY MONTH, keeping the highest-salience
#                 entries (★/⛔/⭐ count) plus always the FIRST and the LAST.
#    2. SERIES  — for measure tokens (30y, 10y, crack, brent, soxx…), every dated
#                 VALUE the vault has recorded, ascending. This is the actual movement:
#                 a column of numbers with dates, not prose about numbers.
#
#  USAGE
#    python3 tools/thread_arc.py --thread RATES
#    python3 tools/thread_arc.py --thread WAR/OIL --tokens brent,crack
#    python3 tools/thread_arc.py --note wiki/rates-board.md --full
#  Imported by tools/librarian.py to print the arc for the top matched threads on ingest.
# ═══════════════════════════════════════════════════════════════════════════
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = os.path.join(ROOT, 'wiki')
sys.path.insert(0, os.path.join(ROOT, 'tools'))

DATE = re.compile(r'(20\d\d-\d\d-\d\d)')
VALUE = re.compile(r"""(?xi)
    (?:\$?\d[\d,]*(?:\.\d+)?\s*(?:trillion|billion|million|bn|[btm])\b)
  | (?:\b\d[\d,]*(?:\.\d+)?\s*(?:gw|mw)\b)
  | (?:\b\d+(?:\.\d+)?\s*(?:bp|bps)\b)
  | (?:\b\d+(?:\.\d+)?\s?%)
  | (?:\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b)
""")


def notes_for_thread(thread):
    """Resolve a thread name to its notes via the router's own ROUTE map (single source
    of truth), then fall back to any note whose name appears in the route string."""
    try:
        from vault_router import ROUTE
    except Exception:
        return []
    spec = ROUTE.get(thread, '')
    names = re.findall(r'[a-z0-9][a-z0-9-]{2,}', spec.lower())
    out, seen = [], set()
    for dp, dns, fns in os.walk(WIKI):
        dns[:] = [d for d in dns if d != '_timelines']   # never arc the auto-generated summaries
        for fn in fns:
            if not fn.endswith('.md'):
                continue
            stem = fn[:-3].lower()
            if stem in names and stem not in seen:
                seen.add(stem)
                out.append(os.path.join(dp, fn))
    return out


def salience(line):
    return line.count('★') + line.count('⭐') + 2 * line.count('⛔') + line.count('🚩')


def entries(paths, vocab=()):
    """Every dated entry header across the given notes, ascending by header date."""
    rows = []
    for p in paths:
        try:
            lines = open(p, errors='replace').read().split('\n')
        except OSError:
            continue
        rel = os.path.relpath(p, ROOT)
        in_tl = False
        for i, ln in enumerate(lines, 1):
            if 'TIMELINE:BEGIN' in ln: in_tl = True; continue      # skip the written block
            if 'TIMELINE:END' in ln: in_tl = False; continue
            if in_tl or not ln.startswith('#'):
                continue
            m = DATE.search(ln)
            if not m:
                continue
            txt = re.sub(r'^#+\s*', '', ln).strip()
            # ON-THREAD BIAS: RATES routes to market-fragility too, so a raw arc fills with
            # VIX/KOSPI headers. Entries whose header carries the thread's own vocabulary
            # survive compression first; the chronology itself is never reordered.
            bonus = 3 * sum(1 for k in vocab if k in txt.lower()) if vocab else 0
            rows.append((m.group(1), rel, i, txt, bonus))
    rows.sort(key=lambda r: (r[0], r[1], r[2]))
    return rows


def compress(rows, budget=46):
    """Keep the ARC readable without breaking the chronology. Groups by month and keeps
    the highest-salience entries in each, ALWAYS keeping the first and last overall —
    the two that define the movement. Marks what it dropped, per rule: no silent caps."""
    if len(rows) <= budget:
        return rows, 0
    by_month = {}
    for r in rows:
        by_month.setdefault(r[0][:7], []).append(r)
    months = sorted(by_month)
    per = max(1, budget // max(1, len(months)))
    keep = []
    for mo in months:
        grp = by_month[mo]
        top = sorted(grp, key=lambda r: -(salience(r[3]) + r[4]))[:per]
        keep.extend(sorted(top, key=lambda r: (r[0], r[1], r[2])))
    for edge in (rows[0], rows[-1]):
        if edge not in keep:
            keep.append(edge)
    keep = sorted(set(keep), key=lambda r: (r[0], r[1], r[2]))
    return keep, len(rows) - len(keep)


def series(paths, tokens, per_token=14):
    """⭐ THE MOVEMENT. For each measure token, every dated VALUE the vault recorded for
    it, ascending. One row per date (highest-salience line wins) so the output reads as a
    track, not as duplicate prose."""
    out = {}
    for p in paths:
        try:
            lines = open(p, errors='replace').read().split('\n')
        except OSError:
            continue
        rel, cur = os.path.relpath(p, ROOT), ''
        in_tl = False
        for i, ln in enumerate(lines, 1):
            if 'TIMELINE:BEGIN' in ln: in_tl = True; continue      # skip the written block
            if 'TIMELINE:END' in ln: in_tl = False; continue
            if in_tl:
                continue
            if ln.startswith('#'):
                m = DATE.search(ln)
                if m:
                    cur = m.group(1)
            low = ln.lower()
            for tok in tokens:
                m = re.search(rf'(?<![a-z0-9]){re.escape(tok)}(?![a-z0-9])', low)
                if not m:
                    continue
                # ⛔ TAKE THE VALUE ATTACHED TO THE TOKEN, not every number on the line.
                # First version printed "10Y  19.79 · 8.74% · 90.27 · 84.61" — those were
                # other numbers in the same sentence. A movement track that prints
                # unrelated numbers under a measure name is worse than no track.
                after = ln[m.end():m.end() + 70]
                before = ln[max(0, m.start() - 40):m.start()]
                vals = [v.strip() for v in VALUE.findall(after)][:2]
                if not vals:
                    vals = [v.strip() for v in VALUE.findall(before)][-1:]
                vals = [v for v in vals if v and not re.fullmatch(r'20\d\d|\d{1,2}', v)]
                if not vals:
                    continue
                out.setdefault(tok, {}).setdefault(cur or '0000-00-00', []).append(
                    (salience(ln), rel, i, ln.strip(), vals[:4]))
    tracks = {}
    for tok, bydate in out.items():
        rows = []
        for d in sorted(bydate):
            best = max(bydate[d], key=lambda x: x[0])
            rows.append((d, best[1], best[2], best[3], best[4]))
        if len(rows) >= 2:
            tracks[tok] = rows[-per_token:] if len(rows) > per_token else rows
    return tracks


def render(thread, paths, tokens=(), width=100, full=False):
    L = []
    if not paths:
        return [f'  (no notes resolved for thread {thread})']
    L.append(f'  📈 THREAD ARC — {thread}  →  ' + ', '.join(os.path.basename(p) for p in paths))
    try:
        from vault_router import THREADS
        vocab = [k for k in THREADS.get(thread, []) if len(k) > 3][:60]
    except Exception:
        vocab = []
    rows = entries(paths, vocab)
    if not rows:
        L.append('     (no dated entry headers in these notes)')
    else:
        kept, dropped = (rows, 0) if full else compress(rows)
        span = f'{rows[0][0]} → {rows[-1][0]}'
        L.append(f'     {len(rows)} dated entries, {span}. Reading ORDER IS THE POINT: '
                 'the inbound is the next tick.')
        if dropped:
            L.append(f'     ⚠️ {dropped} mid-thread entries compressed out (kept highest-salience '
                     'per month + first + last). --full for all.')
        cur_mo = None
        for d, f, i, txt, _b in kept:
            if d[:7] != cur_mo:
                cur_mo = d[:7]
                L.append(f'     ── {cur_mo} ' + '─' * 40)
            L.append(f'     {d}  {os.path.basename(f)}:{i}  {txt[:width]}')
    if tokens:
        tr = series(paths, tokens)
        if tr:
            L.append('')
            L.append('  📉 THE MOVEMENT — every dated value on file, ascending. '
                     'The inbound goes at the BOTTOM.')
        for tok, rows in sorted(tr.items(), key=lambda kv: -len(kv[1])):
            L.append(f'     ── {tok.upper()}  ({len(rows)} dated readings)')
            for d, f, i, ln, vals in rows:
                L.append(f'        {d}  {" · ".join(vals):<34}  {os.path.basename(f)}:{i}')
    return L


def main():
    a = sys.argv[1:]
    def opt(name, dflt=None):
        return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else dflt
    thread = opt('--thread')
    note = opt('--note')
    toks = [t.strip().lower() for t in (opt('--tokens') or '').split(',') if t.strip()]
    full = '--full' in a
    if note:
        paths, thread = [os.path.join(ROOT, note)], note
    elif thread:
        paths = notes_for_thread(thread)
    else:
        print(__doc__ or 'usage: thread_arc.py --thread RATES [--tokens 30y,10y] [--full]')
        return
    print('\n'.join(render(thread, paths, toks, full=full)))


if __name__ == '__main__':
    main()
