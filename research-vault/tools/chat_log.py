#!/usr/bin/env python3
"""
CHAT LOG — dated, running conversational state. Jake's spec, 2026-08-01:
"a branch for chat context that's summarized and logged daily, then read each day to keep the
 conversation going through any chat compaction. Just each calendar day."

WHY THIS IS NOT THE WIKI. wiki/ holds CONCLUSIONS — what we decided, firewalled into DATA and
THESIS. This holds what the wiki structurally CANNOT: the conversation's STATE. What was asked
and never answered. What I was in the middle of. Which corrections happened and what caused
them. A conclusion survives compaction because it is a file; an OPEN QUESTION does not, because
nobody writes a note titled "the thing Jake asked three times that I keep not answering."

⛔ THE FAILURE THIS EXISTS TO FIX, observed in the session that created it: across one long
   session I broke STEP ZERO four times, contradicted my own vault four times, and had to
   re-derive my own registered prediction because I could not remember whether it said 30% or
   50%. Every one of those is a STATE failure, not a knowledge failure. The knowledge was on
   disk the whole time.

USAGE (run at session start, and after any compaction):
    python3 tools/chat_log.py              # RESUME BRIEF: today + the prior 2 days
    python3 tools/chat_log.py --open       # ONLY the open items, across the last 14 days
    python3 tools/chat_log.py --new        # scaffold today's file if missing
    python3 tools/chat_log.py --stale 3    # open items carried >3 days -- the nag list
    python3 tools/chat_log.py --days 5     # widen the resume brief
"""
import sys, os, re, subprocess
from datetime import date, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR  = os.path.join(ROOT, 'chat-log')
OPEN_MARK, CORR_MARK = '🔴', '⛔'

TEMPLATE = """# CHAT LOG — {d} ({wd})
**Read this FIRST after any compaction.** Conversational STATE, not conclusions — conclusions
live in `wiki/`. Never restate a note here; point at it.

## SESSION SHAPE
<!-- times PT · what came in · what thread it touched -->

## 🔴 OPEN — asked, owed, or blocked
<!-- THE HIGHEST-VALUE SECTION. Anything Jake asked that is not answered. Carry forward
     unresolved items from the prior day VERBATIM with their original date, so the age shows. -->

## ⛔ CORRECTIONS MADE TODAY
<!-- with the CAUSE, so the pattern is visible across days rather than per-incident -->

## ★ CONCLUSIONS REACHED
<!-- pointers only: -> wiki/<file>.md:L<n>. If it is not worth a wiki note it is not a conclusion. -->

## ↩ CONTINUITY CHECK vs PRIOR DAY
<!-- did anything today CONTRADICT yesterday? that is the question this file exists to answer -->

## 📌 STATE AT SESSION END
<!-- what I was in the middle of, so the next session resumes instead of restarting -->
"""

def path(d): return os.path.join(DIR, f'{d.isoformat()}.md')
def existing():
    if not os.path.isdir(DIR): return []
    fs = [f for f in os.listdir(DIR) if re.fullmatch(r'\d{4}-\d{2}-\d{2}\.md', f)]
    return sorted(fs, reverse=True)

def today():
    """container clock is UTC; the vault runs on Jake's PACIFIC day. TZ rule, standing."""
    try:
        s = subprocess.run(['date', '+%Y-%m-%d'], capture_output=True, text=True,
                           env={**os.environ, 'TZ': 'America/Los_Angeles'}).stdout.strip()
        return date.fromisoformat(s)
    except Exception:
        return date.today()

def scaffold(d):
    os.makedirs(DIR, exist_ok=True)
    p = path(d)
    if os.path.exists(p):
        print(f'  exists: chat-log/{d.isoformat()}.md'); return p
    open(p, 'w').write(TEMPLATE.format(d=d.isoformat(), wd=d.strftime('%A')))
    print(f'  created: chat-log/{d.isoformat()}.md'); return p

def lines_under(txt, mark):
    """collect bullet lines that carry a mark, with their line numbers"""
    out = []
    for i, ln in enumerate(txt.splitlines(), 1):
        if mark in ln and ln.lstrip().startswith(('-', '*', '1.', '2.', '3.')):
            out.append((i, ln.strip()))
    return out

def show_open(days=14, stale=None):
    fs = existing()[:days]
    if not fs:
        print('  no chat-log files yet. run --new'); return
    print('=' * 92)
    print(f'  🔴 OPEN ITEMS across the last {len(fs)} logged day(s)'
          + (f'   [STALE FILTER: carried > {stale} day(s)]' if stale else ''))
    print('=' * 92)
    t, n = today(), 0
    for f in fs:
        d = date.fromisoformat(f[:-3])
        age = (t - d).days
        if stale is not None and age <= stale: continue
        items = lines_under(open(os.path.join(DIR, f)).read(), OPEN_MARK)
        if not items: continue
        print(f'\n  ── {f[:-3]}  ({age}d ago)')
        for ln, txt in items:
            print(f'     chat-log/{f}:{ln}  {txt[:150]}')
            n += 1
    print(f'\n  {n} open item(s).')
    if stale is None:
        print('  ⚠️ An item that survives many days is either genuinely blocked or being AVOIDED.')
        print('     `--stale 3` separates the two. Say which one it is; do not let it just sit.')
    print('=' * 92)

def resume(days=3):
    fs = existing()
    if not fs:
        print('  no chat-log files yet. run --new'); return
    print('=' * 92)
    print('  📖 RESUME BRIEF — read before answering anything after a compaction')
    print('=' * 92)
    for f in fs[:days]:
        p = os.path.join(DIR, f)
        print(f'\n{"─"*92}\n  chat-log/{f}\n{"─"*92}')
        print(open(p).read().rstrip())
    print('\n' + '=' * 92)
    print('  ⇒ Then run `python3 tools/vault_router.py` on the inbound (STEP ZERO). This file gives')
    print('    you the CONVERSATION; the router gives you the VAULT. Neither substitutes for the other.')
    print('=' * 92)

if __name__ == '__main__':
    a = sys.argv[1:]
    if '--new' in a:
        scaffold(today())
    elif '--open' in a:
        show_open()
    elif '--stale' in a:
        i = a.index('--stale')
        show_open(stale=int(a[i+1]) if len(a) > i+1 and a[i+1].isdigit() else 3)
    else:
        d = 3
        if '--days' in a:
            i = a.index('--days')
            if len(a) > i+1 and a[i+1].isdigit(): d = int(a[i+1])
        resume(d)
