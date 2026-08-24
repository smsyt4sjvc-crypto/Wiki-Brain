#!/usr/bin/env python3
"""
token_profile.py -- profile a Claude Code session's token consumption BY TASK TYPE.

WHY THIS EXISTS (Jake, 2026-08-23): "Token arbitrage. Knowing what tasks consume the
most tokens..." -- that first clause is the prerequisite for the whole gopher design,
and the vault could not measure it. `metered-compute:L2265` has carried "tokens per
task" as "the single most valuable missing series" since 2026-08-12, unfetched.

⭐ THE VAULT IS ITS OWN DATASET. The session transcript records per-turn `usage`, and
every tool call says what the turn was DOING. That is enough to bucket the spend.

⛔ WHAT THIS MEASURES AND WHAT IT DOES NOT.
  MEASURES: output tokens generated per turn, and the SIZE of material each tool
    returned into context (the thing a gopher would replace).
  DOES NOT MEASURE: the input token bill directly attributable to one task. Input is
    CUMULATIVE -- every turn re-submits the whole conversation -- so "input tokens for
    task X" is not a well-defined quantity. The carried-context multiplier below is the
    honest way to express that cost, and it is the one that dominates.

USAGE:  python3 tools/token_profile.py [path/to/session.jsonl]
"""
import json, sys, glob, re
from collections import defaultdict

CHARS_PER_TOK = 3.6   # conservative for mixed prose/code/JSON; used ONLY for tool-result
                      # material sizing, never for the usage numbers (those are exact).

def classify(cmd, tool):
    """Bucket a tool call by the KIND OF WORK it performs. Order matters: first match wins."""
    c = (cmd or "").lower()
    if tool in ("Read", "NotebookRead"):
        return "document reading"
    if tool == "Artifact":
        return "publishing"
    if tool in ("Edit", "Write"):
        return "writing (vault)"
    if tool in ("Grep", "Glob"):
        return "vault retrieval"
    if tool != "Bash":
        return "other tools"
    # --- Bash, classified by what the command actually does ---
    if any(k in c for k in ("librarian.py", "vault_find.py", "crosscheck.py",
                            "thread_arc.py", "vault_router.py", "chat_log.py")):
        return "vault retrieval"
    if "pdftext.py" in c or re.search(r"(cat|head|tail|sed -n).*(raw/|uploads/)", c):
        return "document reading"
    if re.search(r"(grep|sed -n|awk|wc).*(wiki/|chat-log/|CLAUDE\.md|index\.md|tools/)", c):
        return "vault retrieval"
    if "git commit" in c or "git push" in c or "git add" in c:
        return "commit + push"
    if any(k in c for k in ("timeline_header.py", "vault_amend.py")):
        return "writing (vault)"
    if "cat >>" in c or "cat >" in c or "<<'ENTRY'" in c or "<<'LOG'" in c:
        return "writing (vault)"
    if "curl" in c or "urllib" in c or "tape.py" in c or "newyorkfed" in c or "yahoo" in c:
        return "data fetch (Tier 0)"
    if c.strip().startswith("timeout") and "python3 - <<" in c:
        return "arithmetic / verification"
    if "python3 - <<" in c or "python3 -c" in c:
        return "arithmetic / verification"
    if "date" in c and len(c) < 90:
        return "clock / housekeeping"
    return "shell / housekeeping"

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else sorted(
        glob.glob("/root/.claude/projects/*/*.jsonl"), key=lambda p: p)[-1]

    out_by_cat   = defaultdict(int)   # output tokens attributed to the turn's dominant tool
    calls_by_cat = defaultdict(int)
    mat_by_cat   = defaultdict(int)   # chars of tool-result material returned INTO context
    tot_out = tot_in = tot_cache_r = tot_cache_w = 0
    turns = 0
    reasoning_out = 0                 # output on turns with NO tool call = pure prose/judgment
    pending = {}                      # tool_use_id -> category

    with open(path) as fh:
        for line in fh:
            try: d = json.loads(line)
            except Exception: continue
            m = d.get("message")
            if not isinstance(m, dict): continue
            content = m.get("content")
            role = m.get("role")

            if role == "assistant":
                u = m.get("usage") or {}
                o = u.get("output_tokens", 0) or 0
                tot_out += o
                tot_in += u.get("input_tokens", 0) or 0
                tot_cache_r += u.get("cache_read_input_tokens", 0) or 0
                tot_cache_w += u.get("cache_creation_input_tokens", 0) or 0
                turns += 1
                cats = []
                if isinstance(content, list):
                    for b in content:
                        if isinstance(b, dict) and b.get("type") == "tool_use":
                            inp = b.get("input") or {}
                            cmd = inp.get("command") or inp.get("pattern") or inp.get("file_path") or ""
                            cat = classify(cmd, b.get("name"))
                            cats.append(cat)
                            calls_by_cat[cat] += 1
                            pending[b.get("id")] = cat
                if cats:
                    share = o / len(cats)
                    for c in cats: out_by_cat[c] += share
                else:
                    reasoning_out += o

            elif role == "user" and isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "tool_result":
                        cat = pending.pop(b.get("tool_use_id"), "other tools")
                        cc = b.get("content")
                        n = len(cc) if isinstance(cc, str) else sum(
                            len(x.get("text", "")) for x in cc if isinstance(x, dict))
                        mat_by_cat[cat] += n

    print("=" * 88)
    print("  TOKEN PROFILE BY TASK TYPE".ljust(60) + f"{turns:>6} assistant turns")
    print("=" * 88)
    print(f"\n  EXACT, from the transcript's own usage records:")
    print(f"    output tokens generated      {tot_out:>12,}")
    print(f"    input tokens (uncached)      {tot_in:>12,}")
    print(f"    cache WRITE                  {tot_cache_w:>12,}")
    print(f"    cache READ  (carried context){tot_cache_r:>12,}")
    billed_in = tot_in + tot_cache_w + tot_cache_r
    print(f"    ----------------------------------------")
    print(f"    total input surface          {billed_in:>12,}")
    if tot_out:
        print(f"\n  ⭐ CARRIED-CONTEXT MULTIPLIER: {billed_in/tot_out:>.1f}x")
        print(f"     For every 1 token GENERATED, {billed_in/tot_out:.1f} tokens were SUBMITTED.")
        print(f"     {tot_cache_r/billed_in*100:.1f}% of the input surface is CACHE READ -- i.e. re-sent")
        print(f"     conversation, not new material. THAT is what a smaller context buys back.")

    rows = sorted(set(list(out_by_cat) + list(mat_by_cat)),
                  key=lambda k: -(out_by_cat.get(k, 0)))
    print(f"\n  {'task type':<28}{'calls':>7}{'output tok':>12}{'% out':>8}"
          f"{'material IN':>14}{'% mat':>8}")
    print("  " + "-" * 78)
    tot_mat = sum(mat_by_cat.values()) or 1
    tool_out = sum(out_by_cat.values()) or 1
    for k in rows:
        o = out_by_cat.get(k, 0); mt = mat_by_cat.get(k, 0)
        print(f"  {k:<28}{calls_by_cat.get(k,0):>7}{o:>12,.0f}{o/tool_out*100:>7.1f}%"
              f"{mt/CHARS_PER_TOK:>13,.0f}{mt/tot_mat*100:>7.1f}%")
    print("  " + "-" * 78)
    print(f"  {'REASONING (no tool call)':<28}{'':>7}{reasoning_out:>12,}"
          f"{reasoning_out/tot_out*100:>7.1f}%{'--':>13}")
    print(f"\n  (material IN = tokens of tool output that entered context, est. at "
          f"{CHARS_PER_TOK} chars/token)")

    DELEGABLE = {"document reading", "vault retrieval", "data fetch (Tier 0)",
                 "arithmetic / verification", "shell / housekeeping",
                 "clock / housekeeping", "commit + push"}
    dm = sum(mat_by_cat.get(k, 0) for k in DELEGABLE) / CHARS_PER_TOK
    do = sum(out_by_cat.get(k, 0) for k in DELEGABLE)
    print(f"\n  ⭐ DELEGABLE UNDER RULE 19 (extract/fetch/verify/housekeep, NOT judgment):")
    print(f"     {dm:>10,.0f} tokens of material ({dm/(tot_mat/CHARS_PER_TOK)*100:.1f}% of all material)")
    print(f"     {do:>10,.0f} output tokens      ({do/tool_out*100:.1f}% of tool-attributed output)")
    print(f"\n  ⛔ NOT DELEGABLE: cross-document reconciliation and writing are the "
          f"{100-do/tool_out*100:.1f}%")

if __name__ == "__main__":
    main()
