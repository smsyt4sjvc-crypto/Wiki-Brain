# Business Vault — operating instructions

This folder is the second brain for the business (window/exterior contracting). Plain markdown,
git-persisted, Obsidian-compatible. Sibling to `research-vault/` (markets) — same architecture.

## Layout
- `raw/`  — evidence locker: customer call notes, supplier quotes, competitor flyers, permits, photos,
  invoices-as-context. Dated, verbatim, never edited.
- `wiki/` — one idea per file, cross-linked with [[links]]: pricing-model, lead-sources, supplier notes
  (one per supplier), objection-handling, competitor-map, install-process, warranty-policy, seasonal-demand.
- `tools/` — anything runnable that worked once (estimate logic, quote calculators).
- `wiki/pipeline-state.md` — THE canonical current truth: active bids, jobs in progress, AR, committed
  material orders. Only what is ACTUALLY true — no aspirational entries.

## Commands (say these in chat)
- **"ingest this"** (+ any fragment: voicemail summary, supplier email, flyer photo) → file to raw/,
  distill into the right wiki note(s), cross-link, commit+push SAME TURN.
- **"what do we know about X"** → answer from the vault, citing note files.
- **"update pipeline"** → edit pipeline-state.md.
- **"what's stale"** → list notes old enough to re-check (prices, supplier terms).

## THE FIREWALL — data vs interpretation (non-negotiable)
Every note splits into:
- `## DATA (observed)` — what happened, verbatim, dated, sourced: "bid $8,400; customer chose competitor 6/14."
- `## THESIS (interpretation — NOT fact)` — the read: "we lost on price" — labeled opinion until verified.
Rules: numbers never appear in THESIS as settled; opinions never appear in DATA. Wrong reads STAY in the
note marked ⚠️ CORRECTION (struck through, not deleted) — the vault remembers its mistakes.

## Disciplines
1. Date + source every DATA line. 2. One idea per file. 3. Claims, not prose — bullet the number and the
source, kill adjectives. 4. Commit + push EVERY change, same turn (containers die; the repo survives).
5. Audit pipeline-state whenever real money moves.

## Load first
- [[_persona]] — how to respond (build it: no pandering, applicable-first, concede fast, ignore typos).
- [[_calibration]] — the owner's known business biases, so pushback is tuned not generic. (Fill honestly:
  e.g., underbidding when cash is tight? saying yes to bad-fit jobs in slow months? Name them here.)
