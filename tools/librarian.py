#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
#  THE LIBRARIAN — the single ingest gate.        Built 2026-08-08 (Jake's spec:
#  "a librarian that fetches things — there's errors every time we upload")
#
#  ONE COMMAND, run on EVERY inbound before any analysis:
#
#      python3 tools/librarian.py <<'EOF'
#      <the pasted text, or the extracted text of an upload>
#      EOF
#
#  It replaces the old multi-step STEP ZERO with SEVEN checks in one call:
#    1. CLOCK      — verified PDT + UTC printed first (the timestamp rule, baked in)
#    1b. COLLISION — ⭐ added 2026-08-17. Figures in the inbound that ALREADY APPEAR in wiki/,
#                    oldest first. RUNS BEFORE THE ROUTER ON PURPOSE: on 8/17 the router's
#                    brief ran 1,350 lines and the checks that mattered sat at line 1,359 —
#                    which is how they get skipped. Most important check, first position.
#    1c. ANCHOR    — ⭐ added 2026-08-17. Per ENTITY: what number has the vault already
#                    committed to, and WHEN did it first say so.
#                    ⇒ BOTH EXIST BECAUSE THE ROUTER RANKS BY RECENCY INSIDE A NOTE.
#                    ai-financing-fragility.md is 6,500 lines / 160 entries; "newest 5" is 3%.
#                    On 8/17 the vault had held ">$500B total incl. chips" for the Ohio campus
#                    since 7/26 (:1163). Nothing surfaced it, a denominator was re-derived,
#                    and the resulting headline entry was superseded 30 minutes later.
#    2. ROUTER     — the thread-map brief (⟲ trail, ⛔ corrections, ★★★, 🚩 flags)
#    3. SWEEP      — full-text scan of wiki/ for the inbound's DISTINCTIVE TOKENS,
#                    independent of the keyword map. Files the sweep finds that the
#                    router did NOT are flagged as VOCABULARY-GAP candidates.
#                    ⭐ This is the check that does not depend on anyone having
#                    predicted the vocabulary. It is why the librarian exists.
#    4. DUPE CHECK — the inbound's tokens vs raw/ + handoffs/ filenames (60 days).
#                    (Would have caught the 8/8 duplicate: the 8/4 Bernstein PDF
#                    was sitting in raw/ under 'bernstein…magnet-chokepoint'.)
#    5. OPEN ITEMS — today's + recent 🔴 open list, so what is OWED is in view.
#
#  THE BRIEF IS AN INDEX, NOT A SUBSTITUTE: if a line touches the inbound, OPEN
#  THE ENTRY. For document uploads / multi-thread dumps, the sanctioned escalation
#  is a librarian SUBAGENT that reads every surfaced entry in full and reports
#  back — spawned per-inbound inside the session (no standing daemon; see CLAUDE.md §0).
# ═══════════════════════════════════════════════════════════════════════════
import os, re, sys, subprocess, time
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI, RAW, HAND = (os.path.join(ROOT, d) for d in ('wiki', 'raw', 'handoffs'))

STOP = set('''the and for that with this from have been will was were are is not you your can could
would should about into over under more most than then them they their there here when where what
which while these those been being other after before between during against each such only also
just like some very much many said says new all but has had its per our out one two three per cent
percent billion million trillion year years month months week weeks day days today yesterday
tomorrow report reports reported according breaking news update market markets stock stocks price
prices company companies group total pace record levels level high low higher lower first second
third last next now still even both same source sources chart data'''.split())

def clock():
    pdt = subprocess.run(['date', '+%Y-%m-%d %I:%M%p %Z'], env={**os.environ, 'TZ': 'America/Los_Angeles'},
                         capture_output=True, text=True).stdout.strip()
    utc = subprocess.run(['date', '-u', '+%Y-%m-%d %H:%M UTC'], capture_output=True, text=True).stdout.strip()
    return pdt, utc

def distinctive_tokens(text, cap=45):
    """Tokens likely to be ENTITIES or MEASURES: originally-capitalised words, all-caps
    ticker-like strings, hyphenated terms, and 2-grams of capitalised words."""
    toks = Counter()
    words = re.findall(r"[A-Za-z][A-Za-z0-9&./-]{1,}", text)
    for i, w in enumerate(words):
        lw = w.lower().strip('.-/')
        if len(lw) < 3 or lw in STOP:
            continue
        cap_like = w[0].isupper() or w.isupper() or '-' in w
        if not cap_like:
            continue
        toks[lw] += 1
        if i + 1 < len(words) and words[i+1][:1].isupper():
            nx = words[i+1].lower().strip('.-/')
            if nx not in STOP and len(nx) >= 3:
                toks[f"{lw} {nx}"] += 1
    # prefer bigrams and repeated tokens; drop bare fragments of kept bigrams
    ranked = sorted(toks.items(), key=lambda kv: (-(' ' in kv[0]), -kv[1], kv[0]))
    return [t for t, _ in ranked[:cap]]

def sweep(tokens):
    """Grep each token across wiki/*.md, then keep only DISCRIMINATING tokens:
    a token found in more than ~35% of notes (china, america, market…) identifies
    nothing and is dropped before scoring. Per-file DISTINCT-token counts follow."""
    n_notes = sum(1 for _, _, fs in os.walk(WIKI) for x in fs if x.endswith('.md')) or 1
    ubiq_bar = max(4, int(n_notes * 0.35))
    tok_files, dropped = {}, []
    for tok in tokens:
        pat = re.escape(tok).replace(r'\ ', r'[\s-]+')
        try:
            out = subprocess.run(['grep', '-ril', '-E', pat, WIKI], capture_output=True, text=True, timeout=20).stdout
        except subprocess.TimeoutExpired:
            continue
        fs = [f for f in out.strip().split('\n') if f]
        if len(fs) > ubiq_bar:
            dropped.append(tok); continue
        tok_files[tok] = fs
    hits = {}
    for tok, fs in tok_files.items():
        for f in fs:
            hits.setdefault(os.path.relpath(f, ROOT), set()).add(tok)
    return {f: s for f, s in hits.items() if len(s) >= 2}, dropped

MAG_RE = re.compile(r"""(?xi)
    (?:\$\s?\d[\d,]*(?:\.\d+)?\s*(?:trillion|billion|million|bn|[btm])\b)   # $105B, $2 trillion
  | (?:\b\d[\d,]*(?:\.\d+)?\s*(?:gw|mw|gigawatt|megawatt)s?\b)              # 10GW, 800MW
  | (?:\b\d+(?:\.\d+)?\s*(?:bp|bps|basis points?)\b)                        # 33.6bp
  | (?:\b\d+(?:\.\d+)?\s?%)                                                 # 25%, 19.2%
  | (?:\$?\s?\d[\d,]*(?:\.\d+)?\s*(?:/|\s?per\s?)                             # ⭐ PRICE PER UNIT --
       (?:bbl|barrel|gal|gallon|mmbtu|mwh|kwh|therm|ton|tonne|mt|lb|oz)s?\b)   #   $66.26/bbl, 78.62/bbl
  | (?:\$\s?\d[\d,]*\.\d{2}\b)                                              # ⭐ BARE DOLLARS+CENTS: $87.06
""")
# ⛔ ADDED 2026-08-23 AFTER THE GATE MISSED A COLLISION IT EXISTED TO CATCH.
# Jake pasted "3-2-1 crack spread: $66.26/bbl, RBN's latest reading from Aug. 21."
# The vault had committed 66.26 as the AUG 20 3-2-1 twenty minutes earlier
# (oil-value-chain:L1803). The gate reported "no figure in this inbound matches one
# already on file" -- because the ORIGINAL MAG_RE only saw $NNN B/M/T, GW/MW, bp and %.
# ⇒ THE ENTIRE COMMODITY THREAD TRADES IN $/bbl AND WAS INVISIBLE TO THE COLLISION CHECK.
# That is the exact miss the check was built to prevent (error class 1: a LABEL -- "Aug 21" --
# trusted over the DATA). Caught by hand this time. It should not need to be.
DATE_RE = re.compile(r'(20\d\d-\d\d-\d\d)')
MAX_ANCHOR_HITS = 60   # above this a token is vocabulary, not an entity (calibrated 8/17)
# Generic market/status vocabulary that arrives CAPITALISED and therefore looks like an entity.
# Observed 8/17 polluting the anchor from a verification brief's own status legend and
# signal table ("CONFIRMED", "PARTIAL", "Bullish", "Net signal"). Extend as new ones appear —
# this list is a calibration record, same discipline as the thread map's gap history.
ANCHOR_STOP = set('''bullish bearish confirmed unconfirmed partial commentary duplicate aggregate
verification status legend theme signal sources source method summary executive brief feed item
route street index equity net gross yoy mom qoq consensus estimate estimates target targets
january february march april may june july august september october november december
monday tuesday wednesday thursday friday weekly monthly quarterly annual
bullishness risk risks live provisional treat exact separate major minor broad narrow'''.split())

def hot_tokens(text, window=220):
    """Tokens sitting NEAR a magnitude in the INBOUND. These are the ones where a ratio,
    share or denominator is about to be computed — so they are the ones worth anchoring.
    (On 8/17 'ohio' ranked too low to be picked by frequency alone, and 'ohio' was the
    entity whose denominator the vault already held.)"""
    hot = set()
    for m in MAG_RE.finditer(text):
        seg = text[max(0, m.start() - window): m.end() + window]
        for w in re.findall(r"[A-Z][A-Za-z0-9&./-]{2,}", seg):
            lw = w.lower().strip('.-/')
            if lw not in STOP and lw not in ANCHOR_STOP and len(lw) >= 4:
                hot.add(lw)
    return hot

def norm_mag(m):
    """'$500B' / '$500 billion' / '>$500bn' -> '500b'.  '10GW' -> '10gw'.  '25 %' -> '25%'."""
    t = m.lower().replace(',', '').replace(' ', '').lstrip('$')
    t = re.sub(r'(trillion|^t$|t$)', 't', t) if t.endswith(('trillion', 't')) else t
    t = t.replace('trillion', 't').replace('billion', 'b').replace('bn', 'b').replace('million', 'm')
    t = t.replace('gigawatts', 'gw').replace('gigawatt', 'gw').replace('megawatts', 'mw').replace('megawatt', 'mw')
    t = re.sub(r'(basis points?|bps)$', 'bp', t)
    t = re.sub(r'\.0+([a-z%]*)$', r'\1', t)
    return t

def collisions(text, rows_all, max_out=8, per_mag=3):
    """⭐⭐ MAGNITUDE COLLISION — the sharpest form of the anchor, and the one that would
    have caught the 8/17 error directly.

    The inbound carried '$500B'. The vault had carried '>$500B total incl. chips' for the
    Ohio campus since 7/26 (ai-financing-fragility:1162). Nothing surfaced it, so the
    denominator was re-derived and came out wrong. ⇒ MATCH ON THE NUMBER ITSELF, not on
    the topic: when a figure in the inbound already appears in wiki/, that is the single
    highest-value line to read before doing any arithmetic with it.
    """
    want = {}
    for m in MAG_RE.finditer(text):
        want.setdefault(norm_mag(m.group(0)), m.group(0))
    if not want:
        return []
    out = []
    for key, shown in want.items():
        if len(key) < 3 or key.endswith('%') and len(key) <= 3:
            continue                     # bare '5%' collides with everything; needs a subject
        hits = []
        for d, f, i, ln, low in rows_all:
            for m2 in MAG_RE.finditer(low):
                if norm_mag(m2.group(0)) == key:
                    hits.append((d, f, i, ln)); break
        # ⛔ NO UPPER CAP ON MONEY/POWER. Calibrated 8/17: '$500B' carries 103 lines and an
        # earlier version dropped it at >40 — killing the single collision that mattered.
        # A figure the vault repeats constantly is MORE load-bearing, not less; we just show
        # its oldest and newest rather than all of them.
        # Bare PERCENTAGES are the exception: '3.1%' collides with unrelated tables, so a
        # percentage only earns a slot if it is rare enough to be about something specific.
        is_pct = key.endswith('%')
        if hits and (len(hits) <= 8 if is_pct else True):
            hits.sort(key=lambda r: r[0])
            out.append((shown, len(hits), hits))
    out.sort(key=lambda x: (x[0].endswith('%'), -x[1]))
    out = out[:max_out]
    # DE-CLUSTER: two hits 4 lines apart in one note are one statement, not two. Keep the
    # first of each cluster so the slots go to DIFFERENT statements. (8/17: the $500B
    # collision spent both its oldest slots on :692 and :696 — adjacent lines, same entry.)
    final = []
    for rank, (shown, n, hits) in enumerate(out):
        seen, keep = {}, []
        for h in hits:
            d, f, i, ln = h
            if any(f == pf and abs(i - pi) < 12 for pf, pi in seen.items()):
                continue
            seen[f] = i
            keep.append(h)
        # the TOP collision gets a wide window; a wide, load-bearing figure deserves the room.
        width = 7 if rank == 0 else per_mag
        pick = keep[:width - 1] + ([keep[-1]] if len(keep) >= width else [])
        final.append((shown, n, pick))
    return final


TENOR = re.compile(r'\b(\d{1,2})\s*[-]?\s*(?:y|yr|year)\b', re.I)

def measure_tokens(text, thread, vocab, cap=5):
    """The measure names to draw a MOVEMENT track for. Taken from the inbound itself
    (intersected with the thread's own vocabulary) plus any tenor it mentions, so a
    '10-year Treasury yield' inbound tracks 10y even though the map spells it differently."""
    low = text.lower()
    toks = [k for k in vocab if len(k) > 3 and k in low and ' ' not in k]
    for n in set(TENOR.findall(text)):
        toks.append(f'{n}y')
    seen, out = set(), []
    for t in toks:
        if t not in seen:
            seen.add(t); out.append(t)
    return out[:cap]

def _mag_lines():
    """One pass over wiki/: every line carrying a magnitude, tagged with the date of the
    dated header it sits under. Built once, then matched against candidate tokens."""
    out = []
    paths = []
    for dp, dns, fns in os.walk(WIKI):        # wiki/ HAS SUBDIRS (wiki/war/) -- listdir misses them
        # ⛔ EXCLUDE _timelines/. Those files are AUTO-GENERATED SUMMARIES that quote entry headers
        # verbatim, so counting them makes the vault collide with its own summary of itself.
        # Same failure class as the TIMELINE:BEGIN/END block, different scope -- caught 8/18 when
        # a $500B collision returned _timelines/_chain.md instead of the source entry.
        dns[:] = [d for d in dns if d != '_timelines']
        paths += [os.path.join(dp, f) for f in fns if f.endswith('.md')]
    for path in sorted(paths):
        fn = os.path.relpath(path, WIKI)
        cur = ''
        try:
            lines = open(path, errors='replace').read().split('\n')
        except OSError:
            continue
        in_tl = False
        for i, ln in enumerate(lines, 1):
            # ⛔ SKIP THE AUTO-GENERATED TIMELINE BLOCK. It quotes entry headers verbatim,
            # so every figure in it would double-count as a fresh vault statement and the
            # collision check would start matching the vault's own summary of itself.
            if 'TIMELINE:BEGIN' in ln:
                in_tl = True; continue
            if 'TIMELINE:END' in ln:
                in_tl = False; continue
            if in_tl:
                continue
            if ln.startswith('#'):
                m = DATE_RE.search(ln)
                if m:
                    cur = m.group(1)
            if MAG_RE.search(ln):
                out.append((cur or '0000-00-00', f'wiki/{fn}', i, ln.strip(), ln.lower()))
    return out

def anchors(text, ubiq=(), rows_all=None, per_entity=3, max_entities=8):
    """⭐ THE PRIOR-STATEMENT ANCHOR — added 2026-08-17 after the $420B error.

    THE FAILURE IT FIXES: the router ranks entries by RECENCY inside a matched note.
    ai-financing-fragility.md is 6,500 lines / 160 entries; 'newest 5' is 3% of it. On
    2026-08-17 the vault had held '>$500B total incl. chips' for the Ohio campus since
    7/26 at :1162 — three weeks old, so nothing surfaced it, and a denominator was DERIVED
    that the vault already owned. Cost: a wrong headline entry, superseded 30 min later.

    ⇒ CANDIDATES ARE THE TOKENS SITTING NEXT TO A NUMBER IN THE INBOUND — those are the
    ones a ratio is about to be computed for. For each, show vault lines pairing that
    entity WITH A MAGNITUDE, OLDEST FIRST. Recency is the router's job; this answers the
    other question: what has the vault already committed to for this thing, and when first?
    ⚠️ Ranked by SPAN (oldest→newest gap), because an entity the vault has carried a number
    on for weeks is exactly where a fresh derivation is most likely to contradict it.
    """
    cands = [t for t in hot_tokens(text) if t not in set(ubiq)]
    rows_all = rows_all if rows_all is not None else _mag_lines()
    idx = {}
    for tok in cands:
        pat = re.compile(rf'\b{re.escape(tok)}\b')
        hits = [r for r in rows_all if tok in r[4] and pat.search(r[4])]
        # ⚠️ HIT-COUNT IS THE ENTITY DISCRIMINATOR, measured 8/17 on this vault:
        #   ohio 23 · cxmt 26 · nvidia 42 · openai 52   ← entities the vault holds numbers on
        #   index 125 · july 105 · equity 100           ← vocabulary, identifies nothing
        # Above the ceiling the token is a word, not a subject. Below 1 there is nothing to anchor.
        if hits and len(hits) <= MAX_ANCHOR_HITS:
            idx[tok] = sorted(hits, key=lambda r: r[0])
    def span_days(rows):
        ds = sorted(d for d, *_ in rows if d != '0000-00-00')
        if len(ds) < 2:
            return 0
        from datetime import date
        a, b = (date(*map(int, x.split('-'))) for x in (ds[0], ds[-1]))
        return (b - a).days
    # rank by SPAN first: an entity the vault has carried a number on for weeks is exactly
    # where a fresh derivation is most likely to contradict something already committed.
    scored = sorted(idx.items(), key=lambda kv: (-span_days(kv[1]), -len(kv[1])))[:max_entities]
    out = []
    for tok, rows in scored:
        pick = rows[:per_entity - 1] + ([rows[-1]] if len(rows) >= per_entity else [])
        out.append((tok, len(rows), [(d, f, i, ln) for d, f, i, ln, _ in pick]))
    return out

def dupes(tokens, days=60):
    now, out = time.time(), []
    for d in (RAW, HAND):
        if not os.path.isdir(d):
            continue
        for fn in os.listdir(d):
            p = os.path.join(d, fn)
            if now - os.path.getmtime(p) > days * 86400:
                continue
            base = fn.lower()
            m = [t for t in tokens if ' ' not in t and (t in base or t.rstrip('s') in base)]
            if len(m) >= 2:
                out.append((os.path.relpath(p, ROOT), m))
    return sorted(out, key=lambda x: -len(x[1]))[:8]

def main():
    text = sys.stdin.read()
    if not text.strip():
        print('usage: python3 tools/librarian.py <<EOF ... EOF'); return
    pdt, utc = clock()
    W = 92
    print('═' * W)
    print('  📚 LIBRARIAN — the ingest gate. Run BEFORE analysis, on every inbound.'.ljust(W))
    print(f'  🕐 VERIFIED CLOCK: {pdt}   ({utc}) — stamp entries from THIS, not from vibes.')
    print('═' * W)

    rows_all = _mag_lines()
    C = collisions(text, rows_all)
    print('\n' + '─' * W)
    print('  ⚠️  MAGNITUDE COLLISION — figures in this inbound that ALREADY APPEAR in wiki/')
    print('     ⛔ READ THESE FIRST. A number the vault has already stated is a number you must')
    print('        not re-derive. (8/17: the inbound said $500B; the vault had held ">$500B total')
    print('        incl. chips" for the Ohio campus since 7/26. Missing it cost a wrong entry.)')
    if not C:
        print('     no figure in this inbound matches one already on file.')
    for shown, n, rows in C:
        print(f'     ── {shown}   ({n} line(s) in wiki/ carry this figure)')
        for d, f, i, ln in rows:
            print(f'        {d}  {f}:{i}')
            print(f'          {ln[:150]}')

    A = anchors(text, ubiq=(), rows_all=rows_all)
    print('\n' + '─' * W)
    print('  ⚓ PRIOR-STATEMENT ANCHOR — what number has the vault ALREADY committed to, and WHEN FIRST?')
    print('     ⛔ Read this BEFORE deriving any denominator, ratio or share from the inbound.')
    print('     (OLDEST first — the router shows newest. The 8/17 $420B error was an oldest-line miss.)')
    if not A:
        print('     no entity in this inbound is paired with a magnitude anywhere in wiki/.')
    for tok, n, rows in A:
        print(f'     ── {tok.upper()}  ({n} magnitude-bearing lines in wiki/)')
        for d, f, i, ln in rows:
            print(f'        {d}  {f}:{i}')
            print(f'          {ln[:150]}')

    # 1d. THREAD ARC — the running history, oldest → newest (Jake, 8/17)
    try:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        import thread_arc as TA
        from vault_router import THREADS, ROUTE  # noqa: F401
    except Exception as _e:
        TA = None
        print(f'\n  (thread arc could not load: {_e})')
    if TA is not None:
        try:
            pre = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'vault_router.py')],
                                 input=text, capture_output=True, text=True, timeout=120).stdout
            mline = next((l for l in pre.split('\n') if 'matched threads:' in l), '')
            names = re.findall(r'([A-Z][A-Z0-9/_-]+)\((\d+)\)', mline)
            top = [n for n, c in sorted(names, key=lambda x: -int(x[1])) if int(c) >= 2][:2]
            print('\n' + '─' * W)
            print('  📈 THREAD ARC — the running history, BEGINNING → NOW, for the top matched threads.')
            print('     Jake, 8/17: "walk you sequentially forward from the beginning to the new upload…')
            print('     by reading the totality from beginning to current, the upload is immediately in')
            print('     perspective." ⇒ READ THE INBOUND AS THE NEXT TICK, not as a standalone fact.')
            if not top:
                print('     (no thread matched strongly enough to arc)')
            shown = []
            for th in top:
                from vault_router import THREADS as _T
                paths = TA.notes_for_thread(th)
                # RATES and FED both route to new-economy-regime + market-fragility, so the
                # second arc was printing the same 40 lines again. Skip a thread whose notes
                # are already covered — the arc is about the MOVEMENT, not the label.
                if any(set(paths) <= set(prev) for prev in shown):
                    print(f'    (arc for {th} skipped — same notes as a thread already shown)')
                    continue
                shown.append(paths)
                mt = measure_tokens(text, th, _T.get(th, []))
                for ln in TA.render(th, paths, mt):
                    print('  ' + ln)
                print()
        except Exception as e:
            print(f'     (thread arc unavailable: {e})')

    # 2. router brief (thread map)
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'vault_router.py')],
                       input=text, capture_output=True, text=True, timeout=120)
    print(r.stdout.rstrip())
    routed = set(re.findall(r'wiki/[\w/-]+\.md', r.stdout))
    router_strong = bool(re.search(r'matched threads:.*?\((?:[2-9]|\d\d+)\)', r.stdout))

    # 3. map-independent full-text sweep
    toks = distinctive_tokens(text)
    S, ubiq = sweep(toks)
    print('\n' + '─' * W)
    print('  🔎 FULL-TEXT SWEEP (map-independent) — DISCRIMINATING entity/measure tokens per note')
    if ubiq:
        print(f'     (dropped as ubiquitous, matching >35% of notes: {", ".join(ubiq[:10])})')
    if not S:
        print('     no multi-token hits. If the router ALSO matched nothing, this may be genuinely')
        print('     new territory — open a note, and add the vocabulary to the thread map.')
    for f, sset in sorted(S.items(), key=lambda kv: -len(kv[1]))[:10]:
        # cross-links are NORMAL — the gap warning is reserved for a sweep that finds a
        # note the map could not reach at all (router silent/weak) or an overwhelming hit.
        gap = (f not in routed) and not router_strong
        flag = '   ⚠️ MAP COULD NOT REACH THIS — vocabulary gap, add tokens to the thread map' if gap else ''
        print(f'     {len(sset):>2}  {f}{flag}')
        print(f'         tokens: {", ".join(sorted(sset)[:8])}')

    # 3b. PRIOR-STATEMENT ANCHOR — oldest committed numbers, not newest entries
    wide = [t for t in distinctive_tokens(text, cap=120) if t not in ubiq]
    hotset = hot_tokens(text)
    # 4. raw/ + handoffs/ dupe check
    D = dupes([t for t in toks if ' ' not in t])
    print('\n' + '─' * W)
    print('  🗃️  ARTIFACT DUPE CHECK (raw/ + handoffs/, 60 days) — has this been archived before?')
    if not D:
        print('     nothing similar on file.')
    for p, m in D:
        print(f'     ≈ {p}   (matched: {", ".join(m)})')
        print('       → if this inbound is ABOUT the same object, the vault already has an entry. FIND IT.')

    # 5. open items
    print('\n' + '─' * W)
    print('  🔴 OPEN ITEMS this inbound might close (chat_log --open, tail):')
    try:
        o = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'chat_log.py'), '--open'],
                           capture_output=True, text=True, timeout=30).stdout
        tail = [l for l in o.split('\n') if l.strip()][-14:]
        print('\n'.join('     ' + l for l in tail))
    except Exception as e:
        print(f'     (chat_log unavailable: {e})')

    print('═' * W)
    print('  THE BRIEF IS AN INDEX, NOT A SUBSTITUTE. If a line touches the inbound, OPEN THE ENTRY.')
    print('  Uploads / multi-thread dumps → spawn the librarian SUBAGENT to read entries in full.')
    print('═' * W)

if __name__ == '__main__':
    main()
