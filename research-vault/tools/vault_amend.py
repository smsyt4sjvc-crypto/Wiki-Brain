#!/usr/bin/env python3
# ============================================================================
#  VAULT AMEND — supersession, so the vault has STATE and not just a LOG.
#
#  WHY (2026-07-31, Jake's spec: "learn new information AND amend old
#  information… so it's easy to go 'back in March we thought X, but instead Y'"):
#  The vault is APPEND-ONLY. Every entry is `cat >>`. A retired conclusion sits
#  in the file with exactly the same authority as a live one. That failed TWICE
#  tonight: I cited "political escalation is MAXED" nine hours after retiring it,
#  and trigger (a)'s "$120-147" still reads as current in the status block after
#  being re-sized 700 lines later.
#
#  WHY NOT JUST EDIT THE OLD LINE: CLAUDE.md rule 4 — wrong calls stay VISIBLE.
#  The calibration value of this vault is that the errors are readable. So:
#  markers, not deletions. The old text survives; its STATUS becomes explicit.
#
#  CONVENTION (bidirectional, so it is traversable from either end):
#    at the OLD line:  ⟲ SUPERSEDED 2026-07-31 → war-board.md:L745  (one-line why)
#    at the NEW entry: ⟲ SUPERSEDES war-board.md:L21
#  => reading the March claim, you SEE it was amended and where to go.
#     Reading tonight's, you see what it retired. That is the "brain" behaviour.
#
#  USAGE
#    python3 tools/vault_amend.py --supersede wiki/war/war-board.md:21 \
#            --by wiki/war/war-board.md:745 --why "band is Abqaiq-only; Kharg is 1.5mb/d"
#    python3 tools/vault_amend.py --check          # every pointer resolves?
#    python3 tools/vault_amend.py --stale wiki/war/war-board.md   # never-revisited ★★★
# ============================================================================
import sys, os, re, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK_OLD, MARK_NEW = '⟲ SUPERSEDED', '⟲ SUPERSEDES'

def rd(p): return open(os.path.join(ROOT, p), encoding='utf-8').read().split('\n')
def wr(p, L): open(os.path.join(ROOT, p), 'w', encoding='utf-8').write('\n'.join(L))
def loc(s):
    f, _, l = s.rpartition(':')
    return f, int(l.lstrip('L'))

def supersede(old, new, why, today):
    of, ol = loc(old); nf, nl = loc(new)
    O = rd(of)
    if ol < 1 or ol > len(O): sys.exit(f'ERROR: {of} has {len(O)} lines, asked for L{ol}')
    if MARK_OLD in O[ol-1]:
        print(f'  already marked: {of}:L{ol}'); return
    indent = re.match(r'\s*', O[ol-1]).group(0)
    O.insert(ol, f'{indent}  {MARK_OLD} {today} → {os.path.basename(nf)}:L{nl} — {why}')
    wr(of, O)
    N = rd(nf)
    # the new entry moved down by one if it is in the same file BELOW the insert
    if nf == of and nl >= ol: nl += 1
    if nl <= len(N) and MARK_NEW not in N[nl-1]:
        ind2 = re.match(r'\s*', N[nl-1]).group(0)
        N.insert(nl, f'{ind2}  {MARK_NEW} {os.path.basename(of)}:L{ol} — {why}')
        wr(nf, N)
    print(f'  ⟲ {of}:L{ol}  SUPERSEDED BY  {nf}:L{nl}')
    print(f'    why: {why}')

def extends(old, new, why, today):
    """The NON-retiring link — added 2026-08-08 after --supersede was misapplied to a
    live entry (market-fragility L575). THE TEST: does the old line become WRONG?
    YES -> --supersede.  NO, it merely becomes less complete -> --extends.
    Writes a marker at the NEW entry only; the old entry stays clean (it is still live)."""
    of, ol = loc(old); nf, nl = loc(new)
    N = rd(nf)
    if nl < 1 or nl > len(N): sys.exit(f'ERROR: {nf} has {len(N)} lines, asked for L{nl}')
    if '⟲ EXTENDS' in N[nl-1] or (nl < len(N) and '⟲ EXTENDS' in N[nl]):
        print(f'  already marked: {nf}:L{nl}'); return
    ind = re.match(r'\s*', N[nl-1]).group(0)
    N.insert(nl, f'{ind}  ⟲ EXTENDS {os.path.basename(of)}:L{ol} ({today}) — {why} [old entry stays LIVE]')
    wr(nf, N)
    print(f'  ⟲ {nf}:L{nl}  EXTENDS  {of}:L{ol}   (no supersession; both live)')
    print(f'    why: {why}')

def walk():
    for dp, _, fn in os.walk(os.path.join(ROOT, 'wiki')):
        for f in fn:
            if f.endswith('.md'):
                yield os.path.relpath(os.path.join(dp, f), ROOT)

def check():
    print('=' * 84); print('  SUPERSESSION LEDGER — every ⟲ pointer in the vault'); print('=' * 84)
    n = bad = 0
    for rel in sorted(walk()):
        for i, l in enumerate(rd(rel)):
            if MARK_OLD not in l and MARK_NEW not in l: continue
            n += 1
            m = re.search(r'→?\s*([\w\-\.]+\.md):L(\d+)', l)
            tgt = 'UNPARSEABLE'
            if m:
                cands = [r for r in walk() if os.path.basename(r) == m.group(1)]
                tgt = 'OK' if cands and int(m.group(2)) <= len(rd(cands[0])) else 'DANGLING'
            if tgt != 'OK': bad += 1
            kind = 'OLD→' if MARK_OLD in l else 'NEW←'
            print(f'  [{tgt:<11}] {kind} {rel}:L{i+1}')
            print(f'                {re.sub(chr(10)," ",l.strip())[:100]}')
    print(f'\n  {n} pointers, {bad} broken.')
    if bad: print('  ⚠️ DANGLING pointers mean line numbers drifted — re-run after edits.')
    print('  ⚠️ Line numbers move when a file is appended to. This ledger is a POINTER')
    print('     check, not a guarantee; the marker TEXT is the durable part.')
    print('=' * 84)

def stale(rel, keep=12):
    L = rd(rel)
    hits = [(i+1, l) for i, l in enumerate(L) if '★★★' in l and MARK_OLD not in L[min(i+1,len(L)-1)]]
    print('=' * 84)
    print(f'  UNREVISITED ★★★ CONCLUSIONS — {rel}  ({len(hits)} never marked superseded)')
    print('  These read as LIVE. Each is a standing claim nothing has amended.')
    print('  ⚠️ Not necessarily wrong — but the OLDEST are the ones most likely to be stale.')
    print('=' * 84)
    for ln, l in hits[:keep]:
        txt = re.sub(r'\s+', ' ', l.strip().lstrip('-*# ')).replace('**', '')
        print(f'  L{ln:<6} {txt[:100]}')
    if len(hits) > keep: print(f'  … {len(hits)-keep} more')

if __name__ == '__main__':
    a = sys.argv[1:]
    today = os.environ.get('VAULT_DATE') or datetime.date.today().isoformat()
    if '--check' in a: check()
    elif '--stale' in a: stale(a[a.index('--stale')+1])
    elif '--supersede' in a:
        supersede(a[a.index('--supersede')+1], a[a.index('--by')+1],
                  a[a.index('--why')+1] if '--why' in a else '(no reason given)', today)
    elif '--extends' in a:
        extends(a[a.index('--extends')+1], a[a.index('--by')+1],
                a[a.index('--why')+1] if '--why' in a else '(no reason given)', today)
    else:
        print(__doc__ or 'see header')
        print('  --supersede OLD_F:L --by NEW_F:L --why "..."   (old conclusion becomes WRONG)')
        print('  --extends   OLD_F:L --by NEW_F:L --why "..."   (old stays LIVE; new adds to it)')
        print('  --check  |  --stale F')
        print('  THE TEST: does the old line become WRONG? yes=supersede, no=extends.')
