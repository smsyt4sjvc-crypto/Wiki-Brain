#!/usr/bin/env python3
# ============================================================================
#  VAULT ROUTER — the vault-FIRST step, made mechanical.
#
#  WHY THIS EXISTS (2026-07-31, Jake's spec):
#  On 7/30 I filed a rule: "before arguing any position on a dated event this
#  vault has logged, OPEN THE ENTRY." I broke it THREE TIMES the next day --
#  searched the web instead of the vault on the Anthropic blacklist, missed that
#  Hammack had made the data-centre-inflation argument a month before Kashkari,
#  and answered the cement question from a chart instead of the cell I had just
#  built. A rule that only fires when remembered is an INTENTION. This is the
#  WORKFLOW STEP that replaces it.
#
#  USAGE (run BEFORE analysing any paste; costs one local call, no network):
#      python3 tools/vault_router.py <<'EOF'
#      ...paste the inbound text here...
#      EOF
#  Or:  python3 tools/vault_router.py --rebuild      (writes wiki/_router.md)
#
#  WHAT IT RETURNS, and why these four things:
#    ⛔ CORRECTIONS  — what I already got WRONG on this thread. Highest value:
#                      these are the exact re-derivations that waste the session.
#    ★★★ CONCLUSIONS — load-bearing findings already reached. Do not re-argue.
#    🚩 OPEN FLAGS   — the unresolved questions, so new data gets tested against
#                      the question it might ANSWER.
#    📅 RECENT       — the last dated entries, so I know what is already logged.
#  Every line carries FILE:LINE. The brief is an INDEX, not a replacement --
#  it tells me WHERE to read, and reading the entry is still the job.
#
#  THREAD MAP is PARSED FROM acute_scanner_cell.py so there is exactly ONE
#  keyword map in this vault and it cannot drift.
# ============================================================================
import re, sys, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCANNER = os.path.join(ROOT, 'tools', 'acute_scanner_cell.py')

def parse_scanner_maps():
    """Single source of truth: the sentinel-delimited THREAD MAP block in the scanner,
    executed as REAL PYTHON — not regex-scraped. (The 8/8 parser bug class: an apostrophe
    in an in-list comment broke quote pairing and keywords silently parsed as commas.
    exec of the actual block makes comments safe by construction.)"""
    try:
        src = open(SCANNER, encoding='utf-8').read()
    except Exception:
        return {}, {}
    m = re.search(r'THREAD MAP BEGIN.*?\n(.*?)# ═+ THREAD MAP END', src, re.S)
    if not m:
        return {}, {}
    ns = {}
    try:
        exec(compile(m.group(1), '<thread-map>', 'exec'), {}, ns)
    except Exception as e:
        print(f'  !! THREAD MAP FAILED TO PARSE: {e} — fix acute_scanner_cell.py before trusting output')
        return {}, {}
    return ns.get('THREADS', {}), ns.get('ROUTE', {})

THREADS, ROUTE = parse_scanner_maps()

# Router-only threads the SCANNER does not need (it reads wires; this reads Jake).
THREADS.update({
 'PORTFOLIO': ['position','basket','cost basis','avg cost','shares owned','qty','portfolio',
               'holdings','bought','sold','my book','watchlist','rebalance','target weight'],
 'OPTIONS':   ['put','call','strike price','expiry','expiration','delta','vega','theta','implied vol',
               'iv','premium','contract','breakeven','otm','itm','assignment'],
 'NUCLEAR':   ['nuclear','reactor','smr','uranium','enrichment','fuel cycle','nrc','oklo',
               'nuscale','kairos','holtec','spent fuel'],
 'CALIBRATION':['you said','you were wrong','earlier you','contradict','you told me',
               'in the vault','already','superseded'],
})
ROUTE.update({
 'PORTFOLIO': 'portfolio-state / ai-infra-allocation-map',
 'OPTIONS':   'options-reference-natenberg / portfolio-state',
 'NUCLEAR':   'nuclear / power-not-petroleum / buildout-bottleneck-map',
 'CALIBRATION':'_calibration / _persona',
})

# thread -> concrete files (ROUTE strings are prose; this resolves them to paths)
def files_for(thread):
    hint = ROUTE.get(thread, '')
    out = []
    for tok in re.split(r'[/;,]', hint):
        tok = tok.strip().split('(')[0].strip()
        if not tok: continue
        for cand in (f'wiki/{tok}.md', f'wiki/war/{tok}.md',
                     f'wiki/{tok.replace(" ", "-")}.md'):
            p = os.path.join(ROOT, cand)
            if os.path.exists(p) and p not in out: out.append(p)
    return out

# ⟲ FIRST, deliberately. The amendment trail is the thing Jake asked the vault to
# express: "back in March we thought X, but instead Y." A retired claim that still
# READS as live is worse than no claim -- it is how "political escalation is MAXED"
# got cited nine hours after being retired. Show what changed BEFORE what stands.
MARKS = [('⟲ SUPERSEDED', 'AMENDED / RETIRED — what we thought THEN vs now. READ FIRST.'),
         ('⛔', 'CORRECTIONS ALREADY MADE — do NOT re-derive'),
         ('★★★', 'STANDING CONCLUSIONS — do NOT re-argue'),
         ('🚩', 'OPEN FLAGS — test new data against these')]
DATE = re.compile(r'^#{2,6}\s*.*?(\d{4}-\d{2}-\d{2})')

def brief(paths, per_mark=6, recent=5):
    for p in paths:
        rel = os.path.relpath(p, ROOT)
        try: lines = open(p, encoding='utf-8').read().split('\n')
        except Exception: continue
        print(f'\n  ── {rel}  ({len(lines):,} lines)')
        dated = [(i+1, l) for i, l in enumerate(lines) if DATE.match(l)]
        if dated:
            print(f'     📅 RECENT ENTRIES (newest {recent} of {len(dated)}):')
            for ln, l in dated[-recent:]:
                print(f'        L{ln:<6} {l.strip().lstrip("#").strip()[:96]}')
        for mark, label in MARKS:
            hits = [(i+1, l) for i, l in enumerate(lines) if mark in l]
            if not hits: continue
            print(f'     {mark} {label}  ({len(hits)} total, newest {min(per_mark,len(hits))}):')
            for ln, l in hits[-per_mark:]:
                txt = re.sub(r'\s+', ' ', l.strip().lstrip('-*# ')).replace('**', '')
                # SUPERSESSION CHECK. Without this the router hands back RETIRED
                # conclusions as live -- which is exactly how "political escalation is
                # MAXED" got cited nine hours after being retired (7/31).
                nxt = lines[ln] if ln < len(lines) else ''
                if '⟲ SUPERSEDED' in nxt:
                    tgt = re.search(r'→\s*(\S+)', nxt)
                    print(f'        L{ln:<6} ⟲ RETIRED → {tgt.group(1) if tgt else "?"}  |  {txt[:66]}')
                    print(f'        {"":<7} ⟲ DO NOT CITE. {re.sub(chr(10)," ",nxt.strip())[:96]}')
                else:
                    print(f'        L{ln:<6} {txt[:104]}')

def main():
    if '--rebuild' in sys.argv:
        print('rebuild mode: run per-thread briefs into wiki/_router.md yourself if wanted')
    text = '' if sys.stdin.isatty() else sys.stdin.read()
    low = text.lower()
    # WORD-BOUNDARY match. Substring matching gave a false positive on the first live
    # test: war "strikes" tagged the OPTIONS thread via "strike". Same defect class the
    # scanner already fixed with its STRICT set -- fixed here before it was trusted.
    def n_hits(kws):
        n = 0
        for k in kws:
            pat = r'\b' + re.escape(k) + (r'\b' if len(k) <= 4 else r'\w{0,3}\b')
            if re.search(pat, low): n += 1
        return n
    hits = {t: n_hits(kw) for t, kw in THREADS.items()}
    hits = {t: c for t, c in hits.items() if c}
    print('=' * 92)
    print('  VAULT PRE-BRIEF — READ BEFORE ANALYSING THE PASTE')
    print('=' * 92)
    if not text.strip():
        print('  (no input on stdin — pipe the paste in)')
    if not hits:
        print('  NO THREAD MATCHED. That is itself information: either genuinely new')
        print('  territory (open a note) or the keyword map has a gap (fix acute_scanner_cell.py).')
        print('  ⚠️ Do NOT proceed as though the vault is silent until you have checked by hand.')
        return
    order = sorted(hits, key=lambda t: -hits[t])
    print('  matched threads: ' + ', '.join(
        f'{t}({hits[t]})' + ('*' if hits[t] == 1 else '') for t in order))
    if any(hits[t] == 1 for t in order):
        print('  * = SINGLE-keyword match. Weak signal, kept for recall — verify it is not a')
        print('    homonym before trusting it (war "strikes" once tagged OPTIONS via "strike").')
    for t in order:
        fs = files_for(t)
        print(f'\n{"="*92}\n  THREAD: {t}   ->  {ROUTE.get(t,"(unrouted)")}')
        # ⏱ THE GATE (Jake, 2026-08-17): "when a new 'Iran' piece is uploaded … the gate you
        # enter brings you from the start." The merged, committed timeline for this thread is
        # a FILE, not a printout — point at it and read it before the per-note brief below.
        _slug = __import__('re').sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
        _gate = os.path.join(ROOT, 'wiki', '_timelines', f'{_slug}.md')
        if os.path.exists(_gate):
            _n = sum(1 for l in open(_gate, errors='replace') if l.startswith('- `2'))
            print(f'  ⏱ GATE — READ FIRST, WHOLE THREAD OLDEST→NEWEST: wiki/_timelines/{_slug}.md '
                  f'({_n} dated entries)')
        if not fs:
            print('  ⚠️ no file resolved — ROUTE hint does not map to a path. Fix the map.')
        brief(fs)
    print('\n' + '=' * 92)
    print('  THE RULE THIS ENFORCES: the web knows what HAPPENED. Only the vault knows')
    print('  what Jake and I already CONCLUDED about it — including the calls already graded.')
    print('  If a ⛔ line above touches the paste, that argument is CLOSED. Open the entry.')
    print('=' * 92)

if __name__ == '__main__':
    try:
        main()
    except BrokenPipeError:
        try: sys.stdout.close()
        except Exception: pass
