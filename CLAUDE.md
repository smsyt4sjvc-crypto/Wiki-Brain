# Research Vault — operating instructions

This folder is a **second brain**: a living, cross-linked wiki of market research.
It is plain markdown so it works in Obsidian (open this folder as a vault) *and*
survives in git (the repo is the persistence layer — the container is ephemeral).

## Layout
- `raw/`  — drop zone for sources: PDFs, transcripts, pasted commentary, screenshots, article text. Never edited, just stored. This is the evidence locker.
- `wiki/` — the notes I write and maintain. One idea per file. Cross-linked with `[[wiki-links]]`.
- `index.md` — the MAP: table of contents of the wiki, grouped by theme + the spine. Read it after this file to know what exists and where. **Keep it current** — regenerate/extend when notes are added or renamed (a stale map is worse than none).
- `chat-log/` — ONE FILE PER CALENDAR DAY: conversational state, open questions, corrections, continuity vs the prior day. Read FIRST after a compaction (STEP ZERO-C).
- `predictions/` — nightly calibration (point + range + kill-switch), graded next session → `_scoreboard.md`.
- `tools/` — token-free Colab notebooks/scripts (screens, scanners, backtests).
- `trading-system/` — the SEPARATE Alpaca-Claude project (its own `CLAUDE.md`/laws), staged here to transplant.
- `CLAUDE.md` — this file. How the vault runs.

## §0 — THE RULEBOOK (restated 2026-08-08, Jake's spec: "reorganize the vault… restate rules")
**Every standing rule, one place, one line each. Details and origin stories live in the sections below —
this block is the checklist. When a rule here conflicts with memory, THIS text wins.**

### THE INGEST PROTOCOL — every upload, every paste, no exceptions
```
python3 tools/librarian.py <<'EOF'
<the pasted text, or the EXTRACTED TEXT of the upload>
EOF
```
**ONE command replaces the old multi-step STEP ZERO.** It prints, in order: the **verified clock** ·
⭐ **the MAGNITUDE COLLISION + PRIOR-STATEMENT ANCHOR (added 8/17, printed FIRST and before the router
on purpose)** — every figure in the inbound that the vault has ALREADY stated, oldest first, and per
entity the number the vault first committed to and when. **⛔ READ THESE BEFORE COMPUTING ANY RATIO,
SHARE OR DENOMINATOR.** ·
⭐ **the THREAD ARC (added 8/17, Jake's spec)** — for the top matched threads, the RUNNING HISTORY
**oldest → newest**, plus a **MOVEMENT track**: every dated value the vault has recorded for the
measures the inbound names (30Y: 5.28 → 5.238 → 5.20 → 5.22 → **5.216% auction stop**).
**⇒ READ THE INBOUND AS THE NEXT TICK OF A SERIES, not as a standalone fact.** His words: *"walk you
sequentially forward from the beginning to the new upload… by reading the totality from beginning to
current, the upload is immediately in perspective."* Standalone: `python3 tools/thread_arc.py --thread
RATES --tokens 30y,10y [--full]`. ⚠️ **The movement track is grep-built: ~1 row in 3 catches a nearby
unrelated figure. Every row carries file:line — check before quoting one.** *(Origin: 8/17, the $420B error — the router ranks by RECENCY inside a note, so
a 6,500-line file shows its newest 3% and a three-week-old denominator the vault already owned never
surfaced.)* ·
⭐ **THE QUOTE-HEADER RECONCILIATION TEST (added 2026-08-19, Jake's catch: *"they never reconcile
because there's more than one setting"*).** **On ANY pasted chart screenshot, before quoting a single
figure from it: solve `prior = change_$ ÷ (pct ÷ 100)`, then test `price_shown − change_$ ≈ prior`.**
**If it fails, the three fields do NOT belong to the same session and NONE of them may be quoted as a
move.** *(2026-08-19 MRNA: header read "130.52 −1.50 (−2.33%)"; the pair solves to a 62.96 close off a
~64.46 prior — the PREVIOUS session, verbatim, while the price field had already refreshed to the
current one. Two different days in one header.)* **⇒ THE CANDLE GEOMETRY IS THE DATUM; THE HEADER IS A
SEPARATE QUOTE WIDGET AND IS NOT TRUSTED.** **Same failure class as `meta.chartPreviousClose`
(`market-fragility:L3492`) — a denominator that does not belong to its numerator, i.e. error class 2.**
**Never derive a % move from a screenshot: re-pull it with `tools/tape.py`.** ·
the **router brief** (⟲ trail → ⛔ corrections → ★★★ standing → 🚩 flags) · the **map-independent
full-text sweep** (catches vocabulary the map missed — flags "MAP COULD NOT REACH THIS" only when the
router failed) · the **artifact dupe check** against raw/ + handoffs/ (would have caught the 8/8
duplicate note) · the **🔴 open items** the inbound might close.
1. **Run it BEFORE analysis. On documents, run it on the EXTRACTED TEXT, not just the filename** —
   the 8/8 duplicate happened because a PDF was ingested without the gate.
2. **The brief is an INDEX, not a substitute: if a line touches the inbound, OPEN THE ENTRY.**
3. **Upload or multi-thread dump → spawn the LIBRARIAN SUBAGENT**: it reads every surfaced entry in
   full and reports prior state + corrections + flags the inbound might close, then the main session
   analyses. Spawned per-inbound INSIDE the session — **no standing daemon, no cron** (spending rule;
   and the container is ephemeral, so an "idle" agent cannot survive between sessions anyway).
4. **A NO MATCH from the router with sweep hits = a MAP GAP. Fix the map in the same turn** (three
   layers: concepts / entities / measures — see the THREAD MAP block in `tools/acute_scanner_cell.py`).
5. **DEBT / PRIVATE-CREDIT / VC / OFF-SHEET / EARNINGS inbounds cross-check BOTH SIDES OF THE PIPE**
   (Jake, 8/10): [[ai-financing-fragility]] = the FUNDING side (who holds/prices the paper — private
   credit → insurance → Bermuda) and [[balance-sheet-board]] = the ISSUER side (whose sheet, which
   vehicle). The router now prints BOTH briefs on any FINANCING/SHEETS/CAPEX match — read both before
   filing; file to ONE per the board's ⛔ routing rule, cross-link the other.

6. **⛔ CROSSCHECK MY OWN OUTPUT, NOT JUST JAKE'S INPUT** (Jake, 8/11: *"the vault is supposed to
   remember things better than I can"*). **The librarian gates the DOOR. Nothing gated the WINDOW —
   numbers I generate myself.** On 8/11 the vault held the right answer FOUR TIMES and I did not
   consult it (Hormuz blockade record · FRED transport-vs-naming · F19 run on one leg · META FCF).
   **Before citing ANY fresh data pull or stating any number:**
   ```
   python3 tools/crosscheck.py --claim "META FCF +13.2B"     # or pipe a whole table in
   ```
   It gates on ENTITY **and** METRIC and returns a dated READ LIST, newest first. **A disagreement is
   usually a different period or definition — and sometimes it is the fresh pull being wrong.**
   ⚠️ Its extracted-value column is noisy; **the LINE TEXT is the product, not the number.**

### ⛔ ERROR CLASS 8 — BEFORE READING A QUOTE, ASK WHO GAINS IF IT IS BELIEVED (added 2026-08-23)
**Classes 1-7 all interrogate the DATUM — the label, the reference value, the window, the instrument,
the arithmetic, the failed call, the exhausted tool. NONE interrogates the SPEAKER'S INTEREST.**
⛔ **On 8/23 a satirical post by the SPEAKER OF IRAN'S PARLIAMENT was read as a critique of IRAN. It
was mocking Trump. The tell was in the attribution line I already had: a sitting Speaker does not post
four-line satire attacking his own government's economic policy.** ⇒ **I read the CONTENT and ignored
the POSITION.** **⇒ THE GATE: name the speaker's office, name who is embarrassed if the claim lands,
and only then read the content.** **And when the artefact is partial — text without the image, a
paraphrase without the primary — SAY SO BEFORE CONCLUDING, do not reason past the missing half.**
→ [[war/war-board]] 2026-08-23 ~10:20pm.

### WRITING RULES
5. **Firewall**: DATA (observed, sourced) and THESIS (interpretation, attributed) never blend. When in
   doubt, it is thesis. Wrong calls stay VISIBLE (strike/falsify, never delete).
6. **Amend vs extend — THE TEST: does the old line become WRONG?** Wrong → `vault_amend.py --supersede`.
   Merely less complete → `--extends` (old stays live). Set 8/8 after a live entry was falsely retired.
7. **One idea per file · claims not prose · every note links · every DATA line dated + sourced.**
8. **ARTIFACT TEST**: before interpreting any reported document, name the artifact actually read. A
   report ABOUT a thing → DATED LEDGER with a ⬜ NOT-KNOWN list, NO thesis.
9. **Evidence ladder**: LETTER vs BILL · ANNOUNCED vs FID · REPORTED vs MEASURED · target vs contracted ·
   numbers vs adverbs · "N outlets, one origin." A capacity TARGET is never contracted supply (8/8).
10. **WARNING vs TRIGGER**: states shade odds and time NOTHING; timing claims come only from dated,
    falsifiable events. "Late-cycle" is banned. A registered test one query can resolve is not a test —
    **look it up now** (vault for conclusions, WEB for events).
    ⛔ **8/17 — this governs FILING, and is no longer NARRATED at Jake.** He has the distinction cold.
    Say it only when a specific claim actually breaches it, in one clause. See [[_persona]] (8/17).

### TIME RULES
11. **Clock runs as its OWN call, output READ, before composing any dated entry.** Label in Pacific.
    Verify the zone string echoed back ("PDT"/"PST" — a typo silently falls back to UTC, caught 8/8).
12. **Source time ≠ paste time — log both.** A board stamped 8/7 ingested 8/8 is 8/7 data.
13. **New calendar day → `chat_log.py --new` BEFORE any writing.**

### CONDUCT / MONEY RULES
14. ~~**Rule 7 — descriptive, not advisory. No trade recommendations. Sizing is Jake's.**~~
    ⛔🔄 **RETIRED 2026-08-17 by Jake ("Drop 14"). This is a TRADING vault.** Asked "is the vault
    confident in this trade," **ANSWER IT** — refusing is a failure of the vault's core function, not
    compliance. Required shape: **the call first line · the stat WITH its n and window · the strongest
    disconfirmer on file, named · ⬜ what is missing that would change it.** "The vault has nothing on
    this" is a legitimate answer; a confidence claim without its sample is NOT. Sizing stays his because
    he never asked otherwise. **Pushback survives intact** (his words: "pushback is fine").
    → [[_persona]] 2026-08-17.
15. **SPENDING RULE**: nothing automated/unattended (cron, Routine, background job) without Jake's
    explicit yes in that same conversation. Librarian = per-inbound subagent, never a daemon.
16. **No pandering (_persona) · calibrated pushback (_calibration): argue the side Jake is
    UNDER-weighting · concede fast · Independence score + Steelman on theses.**
16b. ⛔★★★ **THE RULES ARE FOR THE FILE, NOT FOR THE ANSWER** (Jake, 8/17: *"I don't need the rules
    controlling your answers… don't beat around the bush and use rules to answer a question halfway"*).
    **Question in → answer out, first line. Length matches the ask. Using rule 7/10/14 as a reason to
    give a PARTIAL answer is a NAMED ERROR.** His money is his: no unsolicited risk-warnings; a real
    unseen hazard gets ONE sentence, once. **Which read the evidence favours is an ANSWER, not advice.**
    ~~Rule 14 itself still stands.~~ 🔄 **14 RETIRED same day — see above.** Full: [[_persona]] 8/17.
17. **Code delivery: COMPLETE cells only** (iPhone/Colab). Acronyms spelled out at first use.
18. **End of session: file → link → index → ⏱ TIMELINE → chat-log → commit → push. Every turn pushes.**
    ⏱ **`python3 tools/timeline_header.py --all --threads --chain` AFTER writing entries, BEFORE committing.**
    Idempotent (compares the spine, not the stamp), so a no-op run costs nothing.
18d. 🔗★★★ **THE TRANSMISSION CHAIN IS THE SPINE** (Jake, 2026-08-18): **Treasuries → hyperscaler
    CDS/spreads → bank/private-credit appetite → hyperscaler capex commitments → AI supplier orders.**
    **A CAUSAL ORDER, not a topic list — each stage prices the one below it.** On any inbound that
    touches the AI complex, **say WHICH STAGE it lands on and whether the shock has PROPAGATED or
    DIED.** Spine: [[transmission-chain]]. Merged running log across all five stages, oldest first:
    **`wiki/_timelines/_chain.md`** (`tools/timeline_header.py --chain`). **File evidence to the STAGE
    note, never to the spine.** ⚠️ **The ordering is a HYPOTHESIS — no lead-lag test has been run.**
18c. ⏱★★★ **THE TIMELINE IS AN ARTIFACT, NOT A PRINTOUT** (Jake, 2026-08-17: *"I don't care about the
    output. I'll never go in there and read it. I want it archived… date stamping, and filing into a
    folder… so that when a new 'Iran' piece is uploaded, the gate you enter brings you from the start"*).
    **Two committed objects, both auto-generated:**
    **(a) Every note carries a ⏱ TIMELINE block under its H1** — the note from the start, in order,
    with line refs. **Opening the note IS reading the chronology.** Between `TIMELINE:BEGIN/END`
    sentinels; `librarian.py` and `thread_arc.py` SKIP the block (it quotes entries verbatim, so
    counting it would make the collision check match the vault's own summary of itself).
    **(b) `wiki/_timelines/<thread>.md` is THE GATE** — one merged chronology per thread across every
    note that carries it. The router prints its path on every match. **⇒ ON ANY INBOUND, READ THE GATE
    FILE START-TO-FINISH BEFORE RESPONDING.** That is what makes a March line land on an August paste:
    WAR/OIL opens at 2026-03-13, and nothing in it is ranked by recency.
    ⚠️ **Never hand-edit either object — edit the ENTRY, then regenerate.**
18b. ⛔★★★ **NO INBOUND IS OFF-TOPIC** (Jake, 8/17): *"everything I bring here — Iran war, political
    macro etc — is relevant to the macro economic environment on down to stock earnings reports and
    rumors."* **Carry every inbound DOWN THE CHAIN: macro → sector → earnings → tape.** Name the
    transmission path or say plainly it has none. Never file a war/politics/policy/rumor inbound as
    background colour.
18e. 🌲★★★ **THE FOREST VIEW** (Jake, 2026-08-25: *"concise summaries of what this detailed
    information means… what state is the market in right now, without getting consumed in
    details"*). **`wiki/forest.md` = the whole market in ONE SCREEN: STATE · HEADED · THE DAM
    (dated triggers) · DOWNSTREAM (placement shapes) · ⚡ BRANCHES · the BASKETS.** **Conclusions
    only, every line carries a pointer into a detail board; nothing primary lives there.**
    ⇒ **REFRESH IT whenever an entry CHANGES THE STATE — not on every entry — and answer any
    "where are we / what does it mean" question FROM it, at its altitude.** The detail boards are
    for filing; the forest is for answering.
    ⚡ **EXTENDED same night (Jake): any finding BIGGER THAN IMPLIED — or one HE catches — gets a
    ⚡ BRANCH in the forest THE SAME TURN it is filed: IF → THEN → INSTRUMENT, dated in, PRUNED
    when resolved ("if xxx does yyy that could send the stock soaring" must be VISIBLE, not buried
    in a board).** **The forest also holds the CONFIDENCE BASKET and the ROTATION-β BASKET, each
    line with `vault_find` keywords so the detail pulls in one command.** A branch that resolves
    moves to its board; the forest stays one scroll — prune before adding.
19. ⭐ **MEASURED 2026-08-23 — `python3 tools/token_profile.py` profiles a session's own transcript
    by task type. FIRST RUN, 1,813 turns: carried-context multiplier 246× · input = 91% of the bill ·
    the steady-state context IS the accumulated tool output (97%) · ⛔ THE SINK IS *VAULT RETRIEVAL*
    (49.6% of material), NOT document reading (8.6%) · 55.2% of output came from turns with NO tool
    call, which is the hard ceiling on any delegation.** ⇒ **Fix retrieval WIDTH before adding a
    cheaper model.** Full: [[metered-compute]] 8/23 ~8:30pm.
19. **DELEGATION TIERS (Jake, 8/10 — "sonnet fetches, fable interprets"): all fetch/chew work runs at
    the CHEAPEST capable tier.** Tier 0 = scripts/cells, ZERO tokens (EDGAR, FRED, CBOE, OpenRouter —
    any structured API; the sheets/CEPI/backtest pattern). Tier 1 = **Sonnet/Haiku SUBAGENTS spawned
    in-session** for UNSTRUCTURED chewing (long filings, transcripts, article batches, multi-source
    verification) — per-task, background, results return as compact digests; Fable never reads the
    raw haystack. Tier 2 = a sibling Sonnet CCR session bound to the repo, ON REQUEST only, for
    parallel batch work (segregation is by-convention — both sessions hold repo creds; hard isolation
    needs a GitHub branch-protection rule). Fable does INTERPRETATION and writing only. No standing
    fetcher daemons/schedules ever without explicit same-conversation approval (rule 15).

## ⛔ STEP ZERO — THE ROUTER (standing, set 2026-07-31 — Jake's spec, after 3 breaches in one day)

**BEFORE analysing ANY inbound paste — wire, chart, position screen, article, question — RUN THIS FIRST:**

```
python3 tools/librarian.py <<'EOF'          # ⟵ since 2026-08-08 the librarian IS step zero
<the pasted text>                            #    (router+sweep+dupe+open items in one call;
EOF                                          #     vault_router.py still works standalone)
```

**It costs one local call and no network.** It reads `wiki/` and returns, per matched thread:
**⛔ corrections already made** (the re-derivations that waste the session) · **★★★ standing conclusions**
(do not re-argue) · **🚩 open flags** (test the new data against the question it might ANSWER) ·
**📅 recent dated entries** — every line with `FILE:LINE`. **The brief is an INDEX, not a substitute:
if a line touches the paste, OPEN THE ENTRY.**

**WHY THIS IS A STEP AND NOT A RULE.** On 7/30 I filed a rule in `_calibration`: *"before arguing any position
on a dated event this vault has logged, OPEN THE ENTRY."* **I broke it three times the next day** — searched
the web instead of the vault on the Anthropic blacklist (four relevant entries existed); missed that **Hammack
made the data-centre-inflation argument a MONTH before Kashkari** and called the later one a discovery; and
answered the cement question **from a chart instead of the cell I had built 20 minutes earlier.**
**A rule that only fires when remembered is an INTENTION. A command in the workflow is a CONTROL.**

- **The thread map lives in ONE sentinel-delimited block in `tools/acute_scanner_cell.py`**, executed as
  real Python by the router (regex-scraping died 8/8 — an apostrophe in a comment silently ate keywords).
  **Three layers per thread: CONCEPTS / ENTITIES / MEASURES** — five gaps in one day (#13-#17) proved the
  original concept-only map could not see proper nouns or data vocabulary. Adding a thread = fill all three.
- **NO MATCH is information, not permission.** It means either genuinely new territory (open a note) or a gap
  in the keyword map (fix the scanner). **It never means the vault is silent.**
- **`(n)*` = single-keyword match = weak.** Kept for recall; verify it is not a homonym.
- **For a large multi-thread dump**, one sub-agent per thread to read its note in full is the sanctioned
  escalation (Jake, 7/31: *"even if each thread needs its own agent"*). The router is the cheap default;
  agents are for when the brief is not enough.
- **THE PRINCIPLE:** *the web knows what HAPPENED. Only the vault knows what Jake and I already CONCLUDED
  about it — including which calls were graded and which were wrong.* **Retrieval is not the cost. Re-deriving
  is the cost.**

## ⟲ STEP ZERO-B — AMEND, DON'T ONLY APPEND (standing, set 2026-07-31 — Jake's spec)

**"The vault should evolve like a brain: learn new information AND amend old information — so it's easy to
go 'back in March we thought X, but instead they did Y.'"**

**THE DEFECT THIS FIXES: the vault was APPEND-ONLY.** Every entry is `cat >>`, so a RETIRED conclusion sits
in the file with exactly the same authority as a live one. **That failed twice on 7/31 alone:** I cited
*"political escalation is MAXED"* nine hours after retiring it, and trigger (a)'s **$120-147** band still read
as current after being re-sized 700 lines below. **A log is not a memory. Memory has STATE.**

**WHY NOT EDIT THE OLD LINE:** rule 4 — **wrong calls stay VISIBLE.** The calibration value of this vault is
that the errors are readable. **So: markers, never deletions.** The old text survives; its STATUS becomes
explicit.

**WHENEVER A NEW ENTRY CHANGES AN OLD CONCLUSION, RECORD IT:**
```
python3 tools/vault_amend.py --supersede wiki/<file>.md:<OLD_LINE>         --by wiki/<file>.md:<NEW_LINE> --why "<one line: what changed>"
python3 tools/vault_amend.py --check              # all pointers resolve?
python3 tools/vault_amend.py --stale wiki/<file>.md   # ★★★ nothing has ever revisited
```
It writes **bidirectional** markers — `⟲ SUPERSEDED <date> → file:Lnn` at the old line, `⟲ SUPERSEDES
file:Lnn` at the new one — **so the trail is traversable from either end.** Read the March claim, see it was
amended and where to go. Read tonight's, see what it retired. **That is the "brain" behaviour.**

- **`vault_router.py` PRINTS THE ⟲ TRAIL FIRST, ABOVE ★★★ and ⛔.** A retired claim resurfacing as live is
  worse than no claim — it is the precise failure of 7/31. **The router now refuses to hand one back clean.**
- **AMEND ON: superseded conclusions · re-sized magnitudes · a status line the new entry contradicts · a
  trigger/kill-switch definition proven too narrow · any "I was wrong about X" that touches an EARLIER entry.**
  **NOT on: ordinary new information that merely ADDS.**
- **⚠️ LINE NUMBERS DRIFT when a file is appended to.** `--check` is a pointer check, not a guarantee; **the
  marker TEXT is the durable part.** Re-run `--check` after any session that appended heavily.
- **THE PRINCIPLE:** *appending is learning. Amending is understanding. A vault that only appends gets bigger,
  not smarter — and it will hand you its own retired conclusions with a straight face.*

## 📅 CHRONOLOGY — GIT IS ALREADY THE TIMESTAMP (standing, set 2026-07-31 — Jake's Q)

**Jake: "is there a way, without checking each time, to put a time and date filter on every inclusion…
so they're chronological instead of just a pile?"** **THERE ALREADY WAS, and I was not using it.**
**Git has stamped every line of this vault since day one.**

```
git blame --date=format:'%Y-%m-%d %H:%M' -L 21,23 -- wiki/war/war-board.md
  05dc57ac (2026-07-24 01:33) - (a) Export-terminal strike — … Brent $120-147
  3438cb4f (2026-07-31 22:27)     ⟲ SUPERSEDED → war-board.md:L748 — the band is ABQAIQ-only
```
**That IS "back in March we thought X, but instead Y" — verified, per-line, free, already in the repo.**

**`python3 tools/vault_timeline.py`** surfaces it: every dated entry across `wiki/`, **sorted by GIT commit
time (the authority) rather than by the header (what I typed)**, with mismatches classified.
`--days N` · `--file F` · `--check` (mismatches only).

- **THE HEADER IS WHAT I TYPED. THE COMMIT IS WHAT HAPPENED.** When they disagree, the header is wrong —
  **except for legitimate backfills, where a note about an EARLIER event correctly carries an older date.**
  **The dangerous direction is a header AHEAD of its own commit: that is a clock error.**
- **★ RESULT OF THE FIRST FULL RUN (862 dated entries): ZERO clock errors.** **The timestamp rule has been
  working.** 89 backfills, all legitimate — the two largest (**+144d**, **+43d**) are historical notes about
  past events, which is what a backfill should look like.
- **⚠️ AND A CALIBRATION FIX THE FIRST RUN FORCED: it flagged 216 entries as "BACKFILL +1d." They were not.**
  **A header stamped "~10:35pm PT" commits at ~05:35 UTC the NEXT calendar day — PT is UTC-7/8, so every
  evening-PT entry lands one UTC day later BY DESIGN.** **A check that cries wolf 216 times trains you to
  ignore it, which is worse than no check.** Now normalised; **237 flags → 89 real ones.**
- **⛔ NO GIT HOOK, AND THE DATA IS THE REASON.** A pre-commit validator would be machinery for a failure that
  **is not occurring** (0 errors in 862 entries). **Build the check, read the result, and let the result
  decide whether the machinery is warranted.** It was not. *(Revisit if `--check` ever shows a FUTURE flag.)*

## 📖 STEP ZERO-C — THE DAILY CHAT LOG (standing, set 2026-08-01 — Jake's spec)

**"A branch for chat context that's summarized and logged daily, then read each day to keep the
conversation going through any chat compaction. Just each calendar day."**

```
python3 tools/chat_log.py            # RESUME BRIEF — today + prior 2 days. RUN AFTER ANY COMPACTION.
python3 tools/chat_log.py --open     # only the 🔴 open items, last 14 days
python3 tools/chat_log.py --stale 3  # items carried >3 days — the nag list
python3 tools/chat_log.py --new      # scaffold today (Pacific date, per the timestamp rule)
```

**WHY THIS IS NOT THE WIKI, AND WHY THE ROUTER DOES NOT COVER IT.** `wiki/` holds CONCLUSIONS;
`vault_router.py` retrieves them by keyword. **Neither can hold the conversation's STATE** — what was
asked and never answered, what I was mid-argument on, which correction caused which. **A conclusion
survives compaction because it is a file. An OPEN QUESTION does not, because nobody writes a note
titled "the thing Jake asked three times that I keep not answering."**

**⛔ THE FAILURE IT FIXES, from the session that commissioned it:** in one long session I broke STEP
ZERO **four times**, contradicted my own vault **four times**, and had to re-read my own registered
prediction because I could not recall whether it said 30% or 50%. **Every one is a STATE failure, not
a knowledge failure — the knowledge was on disk throughout.** And the single most expensive item was
not a wrong answer: **it was a question Jake asked three times (the loss number on the options sleeve)
that I never answered, because nothing in the vault was shaped like an unanswered question.**

- **🔴 OPEN is the load-bearing section.** Carry unresolved items forward **VERBATIM with their
  ORIGINAL date**, so the AGE is visible. An item that survives days is either genuinely blocked or
  being **avoided** — `--stale` separates them. **Say which; do not let it sit.**
- **↩ THE CONTINUITY CHECK IS THE POINT OF THE DATING.** Each day, test today's claims against
  yesterday's. **When they conflict, that is a STEP ZERO-B amendment, not a note to self.**
- **Conclusions go in as POINTERS ONLY** (`→ wiki/<file>.md`). If it is not worth a wiki note, it is
  not a conclusion. **This file must never become a second, worse copy of the vault.**
- **Order of operations after a compaction: `chat_log.py` FIRST, then `vault_router.py` on the
  inbound.** The log gives you the CONVERSATION; the router gives you the VAULT. **Neither
  substitutes for the other, and the log is the one that tells you what you still owe.**

## Session flow (the compounding loop)
Start: read this file → **`chat_log.py` (STEP ZERO-C: what is still OPEN)** → **run STEP ZERO on the inbound** → `index.md` (the map) → the relevant spine notes. Work. End: file new knowledge into
`wiki/` (firewall-split), update any note touched, extend `index.md` if notes were added, commit + push. Every
session leaves the vault smarter for the next. (This is the Karpathy/Obsidian second-brain pattern — which the
vault already implements; we add the DATA/THESIS firewall + the predictions calibration loop on top.)

## Commands (say these in chat)
- **"ingest this"** (with a file in `raw/` or pasted text) → I read it, extract the claims, create or update the relevant `wiki/` note(s), add `[[links]]` to related notes, and record the source under a `## Sources` heading with the date.
- **"what do we know about X"** → I read across `wiki/` and answer from the vault, citing the note files.
- **"update portfolio"** → I edit `wiki/portfolio-state.md` with the new position/thesis change.
- **"what's stale"** → I list notes whose data/claims are old enough to re-check.

## THE FIREWALL — data vs thesis (non-negotiable)
**Observed data and interpretation must never be conflated.** Every note is split into
two clearly labelled sections and nothing crosses the line:

- `## DATA (observed)` — only things that are *measured*: numbers, dates, what a source
  literally said, what a data pull returned. Each line carries its source. If it can't be
  traced to a `raw/` file, a data pull, or a dated source, it does **not** go here.
- `## THESIS (interpretation — NOT fact)` — the read, the hypothesis, the "what it means."
  This is opinion until proven. It may be the user's thesis or mine; either way it is
  labelled interpretation and never stated as fact.

Rules of the firewall:
1. A number never appears in the THESIS section as if settled; an opinion never appears in
   the DATA section. When in doubt, it's thesis.
2. Attribute interpretation: mark whose read it is — `(user's thesis)` or `(analysis)`.
3. If data later confirms a thesis, the data line moves/updates under DATA with its new
   source; the thesis line stays labelled as the (now-supported) interpretation. Support ≠
   proof; note the strength of evidence, don't promote opinion to fact.
4. Predictions that were *wrong* stay in the note (struck through or in a `### Falsified`
   list), so the brain remembers what it got wrong instead of quietly deleting it.

## Ingest rules (how I write notes)
1. **One idea per file.** A note is a concept (`cepi.md`), a thesis (`power-not-petroleum.md`), or a state (`portfolio-state.md`) — not a dump.
2. **Firewall first** (above): DATA and THESIS sections, always, never blended.
3. **Claims, not prose.** Bullet the falsifiable claim + the number + the source. Kill adjectives.
4. **Always link.** Every note names the other notes it touches with `[[...]]`. That's what makes it a graph, not a pile.
5. **Date and source everything.** Every DATA line traces to a file in `raw/` or a dated pull. No orphan facts.
6. **Separate signal from artifact.** If a data pull is suspect (parsing error, stale filing, war-premium contamination), label it `⚠️ artifact` under DATA so it's never read as a clean signal later.
7. **Descriptive, not advisory.** Notes describe the market and the book. Sizing and execution are the user's. No trade recommendations.

## How to respond: no pandering (load first)
Before responding at all, load [[_persona]] — no pandering, peer not cheerleader, applicable-first,
ignore typos, concede fast when he's right. It's a safety mechanism (Claude is his only error-check),
not a style pref.

## Pushback is calibrated, not blanket
Before challenging any thesis, load [[_calibration]]. Pushback is tuned to Jake's bias map —
push hard on source-correlated / monotone-confirmed / thesis-as-fact claims; leave primary-source
convergence and execution discipline alone. Argue the side he's *under-weighting* (it flips).
Tag each thesis with an Independence score + a Steelman. Current standing bull = [[detachment-bid]].

## SPENDING RULE (standing, no exceptions)
**Nothing automated that could charge Jake beyond his Max subscription without his explicit approval first.**
Do NOT create scheduled Routines/crons, recurring background jobs, or anything that runs unattended and
consumes usage — even if it seems helpful — without asking and getting a yes in that same conversation.
One-off work inside a session he started is fine; standing automation is not. (Set 2026-07-07 after a daily
morning-scan Routine was created and then deleted at his request.)

## Heavy data pulls → offload
Before doing a big in-session fetch (PDF, long page, bulk tickers, walled site), use the
[[data-sourcing-playbook]]: hand the retrieval to Perplexity/Grok/Gemini/ChatGPT with the
ingest-ready prompt, then paste the compact digest back and "ingest" it. Keeps the chat lean.

## Current thesis spine (start here)
- [[consumption-vs-investment-crux]] — THE top question: did post-COVID borrowing build or drink? Sorts every vector.
- [[new-economy-regime]] — the macro DB read: Fed Trap / debasement in the actual series (M2, real rates, balance sheet).
- [[market-fragility]] — the top-level regime read (narrow-market STATE; timed by triggers, not the narrowness)
- [[ai-capex-cycle]] → [[cepi]] — the fragility's fundamental driver
- [[power-not-petroleum]] → [[demand-destruction]] — the energy rotation
- [[fragility-engine]] — the code that scores all of it into one number
- [[portfolio-state]] — the running truth of the book

## Code delivery rule (standing, set 2026-07-12)
Jake works from an iPhone — editing inside Colab cells is effectively impossible for him.
**Always deliver COMPLETE cells/notebooks, never partial patches or "replace lines X-Y" edits.**
Any fix = reprint the entire cell with the fix baked in. Larger tools → build the .ipynb and send
the file.

## Nightly prediction ritual (standing, set 2026-07-12)
Every night: a new dated file in `predictions/` — point + 80% range + direction confidence for the
core five (WTI, S&P, NASDAQ, SOXX, DRAM/MU) + shape call + named kill switch. Reasoning from logged
vault evidence only. NEVER edited after registration. Next session: grade the prior set against the
prints Jake pastes, update `predictions/_scoreboard.md` (direction hits, range coverage, notes).
Misses logged as loudly as hits — this is the calibration engine.

## The WARNING-vs-TRIGGER rule (standing, set 2026-07-14 — Jake's catch)
**"Late-cycle signature" is BANNED as a tag.** Most features tagged "late cycle" — narrow breadth,
high concentration, expensive valuation, retail FOMO, melt-up, high single-stock vol — are
BULL-MARKET features present through the ENTIRE up-leg. They describe a STATE, not a TIMING, and only
look "late cycle" in hindsight (narrow breadth "flashed" for YEARS in 1998–2000, 2015–2020, 2023–2025
while the market ran; Greenspan's 1996 "irrational exuberance" → market tripled). Calling them "late
cycle" in real-time smuggles in an unfalsifiable timing claim — the exact hindsight bias the vault
ingested a warning about (Roberts; Druckenmiller "valuation is not a catalyst").
- **WARNINGS (states):** unfalsifiable, persist for years; at EXTREMES they shift forward-drawdown
  ODDS slightly but time NOTHING. Label them as conditions ("the market's state", "a bull-market
  feature that persists until a trigger fires"). An extreme reading may be noted as an odds-shader,
  NEVER as a top-caller.
- **TRIGGERS (events):** what actually ENDS bull markets — a Fed tightening cycle, a credit/liquidity
  event, a funding-chain break, a capex cut. Dated, mechanical, FALSIFIABLE. Timing claims come ONLY
  from these.
- Rule: describe states as states; make timing claims only from dated falsifiable triggers. The
  [[bull-bear-ledger]] + Roberts scorecard already do this right ("states flashing" vs "top-markers
  not yet fired") — the rest of the vault must match, not sloppily tag things "late cycle."

## Acronym rule (standing, set 2026-07-13)
When using an acronym, write the full words with the acronym in parentheses after — e.g.
"weighted average cost of capital (WACC)" — at first use in a conversation, so the terms stick.
Jargon is a tax on the reader; pay it once, visibly.

## Timestamp rule (standing, set 2026-07-12 ~9:30pm PT — after two clock errors in one weekend)
Claude has no internal clock and MUST NOT infer time from conversation flow. Before writing any
dated/timed vault entry or making any market-hours claim:
1. Run `date -u` + `TZ="America/Los_Angeles" date` in the container (it has a real clock).
2. Label all entries in JAKE'S clock (Pacific), date + time: "2026-07-12 ~9:30pm PT".
3. Market-session math (crude 3pm PT Sun, equities 6:30am PT, closes, expiries) derives from the
   verified clock, never from vibes.
4. When ingesting pasted items, log the SOURCE's stated timestamp separately from paste-time.
5. Git commit timestamps (UTC, container clock) are the authoritative when-was-it-logged record;
   in-note labels are for human reading — keep both honest.
(Origin: "under 4 hours to the crude open" on a Sunday morning; then labeling 9pm PT entries
"~3am" by UTC drift. Both Jake catches.)
6. Jake's uploads usually carry timestamps ("8m ago", "1h ago", article datelines) — derive source
   time from those + the verified clock at paste time; don't guess.
7. Session texture: Jake works in 10-30 minute ambient check-ins through the day, not marathon
   sessions — don't narrate workload drama ("burnout", "go to sleep") off cumulative chat length.

## 🗂️ ENTITY VIEWS, NOT ENTITY FOLDERS (standing, set 2026-08-11 — Jake's Q)

**Jake: "Is the vault setup with folders? Can we create folders and a search function like a typical OS?
If I upload meta earnings you search 'meta' and the folder comes up? Easier than scanning?"**

```
python3 tools/vault_find.py META --raw        # the "folder" for any entity, generated on demand
python3 tools/vault_find.py "data centre" --days 30
```
**IT RETURNS: 📂 WHERE IT LIVES (notes ranked by coverage) · 📅 dated entries newest-first ·
⛔ corrections · ★★★ standing conclusions · 🚩 open flags · 🗃️ matching raw/ artifacts.**

- **WHY NOT REAL FOLDERS — the structural reason: A FILE LIVES IN EXACTLY ONE FOLDER; AN ENTITY APPEARS
  IN MANY THREADS.** META alone runs to **486 mentions across 36 notes** — earnings in `ai-capex-cycle`,
  the BlackRock JV in `ai-financing-fragility`, FCF in `cepi`, open-source strategy in
  `compression-thesis`, the tape in `market-fragility`, basket weight in `portfolio-state`.
  **A `wiki/meta/` folder forces a choice: fragment the THREADS or duplicate the entries.** The threads
  ARE the product; entities cut across them. **The view keeps one-idea-per-file AND lets one entry
  appear under every entity it touches.**
- **THE MECHANICAL COST OF MOVING FILES, stated so it is not re-proposed: every `[[wiki-link]]` and all
  67 `vault_amend` pointers are path-based.** A reorganisation breaks the amendment trail — **the exact
  feature that makes this a brain rather than a pile.**
- **⚠️ THE ONE PLACE A REAL FOLDER IS WARRANTED: `raw/` IS 178 FLAT FILES** with inconsistent names.
  Nothing links INTO raw/ by path (the librarian scans it by content), **so raw/ can be foldered by
  month without breaking anything.** ⬜ **Not done — proposed, not executed.**
- **THE PRINCIPLE:** *organise storage by IDEA, retrieve by ENTITY. Folders are exclusive; the questions
  are not.*

### ⛔ THE PUSH CREDENTIAL DIES WHEN JAKE CLOSES THE PHONE (diagnosed by him, 2026-08-24)
**Symptom: `git push` → `fatal: could not read Username for 'https://github.com'` on EVERY remote,
after working all session. Reads still succeed. No credential helper is configured and there is no
token in the environment — the write credential is ambient and it goes with the app.**
⇒ **IT IS NOT A REPO PROBLEM, NOT A BRANCH PROBLEM, AND NOT WORTH DIAGNOSING AGAIN. It comes back
when he reopens.**
- **⚠️ THE REAL RISK IS NOT THE ERROR, IT IS THE WINDOW: the container is EPHEMERAL and the repo is
  the persistence layer. Work committed while he is away is STRANDED until he returns.**
- **✅ THE FALLBACK THAT WORKS, PROVEN 2026-08-24: the GitHub MCP API still authenticates when git
  does not.** `mcp__github__create_or_update_file` — push the SUBSTANTIVE file(s) to a
  `handoffs/*-RECOVERY.md`, with the recovery steps in the file header. **Auto-generated timelines do
  NOT need pushing; `timeline_header.py --all --threads --chain` regenerates them.**
- **⇒ ON RECOVERY: `git pull --rebase` (ORIGIN ONLY), delete the recovery file, regenerate
  timelines, push.**

### ⛔ WIKI-BRAIN PUSH = `bash tools/wb_push.sh` — NEVER `git pull --rebase wb main` (set 2026-08-25, after the accident)
**Wiki-Brain main is a ROOT-LEVEL mirror of `research-vault/` with DIFFERENT SHAs (no shared
history) plus content of its own (`work/`, cron-written `data/fragility/*`). `git pull --rebase wb
main` therefore replays the ENTIRE INMA- history — ancient business-site commits included — onto
it.** ⛔ **On 8/25 that rebase hit a conflict on a 2-year-old `Index.html` rename, and `git push wb
HEAD:main` then published the mid-rebase HEAD: five junk site commits and a stray root `Index.html`
landed on the vault repo (reverted by `8b9c821`).** ⇒ **The script grafts the vault state onto
wb/main's tree as ONE commit via a temp index — wb-only content survives, owned paths sync exactly,
always fast-forward, no rebase ever.** ⚠️ **`data/` is deliberately NOT owned: the weekday fragility
cron writes `data/fragility/*` on wb main directly, so its copy can be newer — after any in-session
`move_manual.py`/feed refresh, push `data/fragility/*` separately or re-run the feed on wb.**

### 📱 THE PHONE URL — THE ONE THING THAT WAS NOWHERE IN THIS VAULT UNTIL JAKE ASKED FOR IT (2026-08-23)
**FRAGILITY LADDER (Artifact — this is the link to open on the iPhone):**
**`https://claude.ai/code/artifact/6594cb4c-2970-496d-893c-d8ea041f0c11`**
- ⛔ **IT IS NOT GITHUB PAGES AND MUST NOT BECOME PAGES ON `INMA-`.** Pages there serves
  **inmagent.com** off `main`/(root); changing the source takes down the live business site.
  `Wiki-Brain` is PRIVATE, so Pages there needs a paid plan — deliberately not done.
- ⚠️ **IT IS A STATIC SNAPSHOT, NOT A LIVE PAGE.** The numbers are baked in at BUILD time (a
  JS-fetching page renders empty to WebFetch, which is why it is built this way). ⇒ **It shows
  whatever was true when it was last published, and it does NOT refresh itself.**
- **TO REFRESH IT:** `python3 tools/fragility_feed.py` → `python3 tools/fragility.py` →
  `python3 tools/fragility_html.py` → **re-publish to the SAME URL** (Artifact with the same
  file path, `research-vault/docs/index.html`). **A different path claims a NEW url — don't.**
- ⭐ **RECORD ANY FUTURE HOSTED URL HERE.** It took a retrieval failure to notice the vault had
  no record of its own published page — 130-note recall on refinery data, zero on its own link.

### DAILY: THE FRAGILITY LADDER (run it before answering any "is credit cracking" question)
`python3 tools/fragility.py`  — scores 24 public credit/funding series against their own
3-year history and prints which of the 7 transmission stages are lit. Refresh first with
`python3 tools/fragility_feed.py` (~90s). Page: `docs/index.html`. Data: `data/fragility/`.
- **NO ABSOLUTE THRESHOLDS.** Everything is a percentile against its own history, and
  trending series are scored on RATE OF CHANGE ONLY.
- **⛔ A GAP IS NOT A CALM ROW.** CDX IG/HY, swap spreads and single-name CDS have NO free
  source and are listed as GAPS. Two of them are where AI-complex stress would appear FIRST.
  Never report "the ladder is calm" without naming what the ladder cannot see.
- **⚠️ CHECK THE STALE FLAGS.** A stale number that looks calm is the most dangerous cell.
- **⛔ READ `n/N lit`, NOT JUST THE STAGE COLOUR.** A stage holding 8 series has 8 chances to
  light; one holding 1 has one. **✦ = corroborated (≥2 independent series).** A stage lit on a
  single series is a weak reading and must be reported as one.
- **⭐ MOVE: LIVE ROW, BUT THE CRON CANNOT REFRESH IT.** Every *curl* route is blocked from a
  datacentre IP (Yahoo 429 from container AND runner, CNBC 403, WSJ 401, Stooq JS-gated, FRED
  VXTYN dead since 2020) — **but WebFetch reaches `finance.yahoo.com/quote/%5EMOVE`, because it
  is a DIFFERENT FETCHER, not this container's curl.** ⇒ **Refresh it yourself, in-session:**
  WebFetch the quote → `python3 tools/move_manual.py <date> <value>`.
  **ROUTES: `google.com/finance/quote/MOVE:INDEXNYSEGIS` and `finance.yahoo.com/quote/%5EMOVE`.
  ⬜ WHICH IS FRESHER IS UNTESTED — on 8/22 Google served Aug 21 while Yahoo served Aug 20, but
  that is ONE observation on a SATURDAY, when a systematic lag and a stale cache look identical
  because nothing refreshes to correct either. Try Google first, but CHECK BOTH and take the
  later timestamp.**
  ⚠️ **Either page can be DELAYED — read its "last updated" field and use THAT date, not today's.**
  ⚠️ **Run the QUOTE-HEADER RECONCILIATION TEST on it (`price − change ≈ stated prev close`)
  before recording.** ⛔ **The weekday Action CANNOT call WebFetch, so MOVE lags on any day Claude
  is not asked; the STALE flag is the honest signal.** `--status` lists missing weekdays.
- **🚩 ERROR CLASS 7 — EXHAUSTING VARIATIONS OF ONE TOOL IS NOT EXHAUSTING THE OPTIONS.** I tried
  six curl routes and declared "no free source." **Before calling anything unreachable, vary the
  TOOL: curl · WebFetch · WebSearch · a runner · a browser · Jake's own device.**
- **⚠️ THE VAULT NOW LIVES IN ITS OWN REPO (`wiki-brain`), moved 2026-08-22.** The copy inside
  `INMA-/research-vault/` is STALE. Never edit both. Never touch the INMA business site — Pages
  there serves inmagent.com off `main`, and scheduled Actions only fire from a default branch.

### ⛔ BOARD-CONSTRUCTION RULE — INVENTORY THE INHERITED STATE (set 2026-08-31, Jake's catch: "that should've definitely been in there")
**The UAE left OPEC May 1, 2026 — a cartel-structure break in the vault's core domain — and no board
held it until 8/31.** Not a migration loss and not a live-coverage miss: **the repo existed (Feb 14)
but the oil lane didn't (demand-destruction built 7/1, oil-value-chain 7/20, war-board 7/24). A
board built mid-year starts at "now" and treats the inherited state as continuous history — it never
asks what BROKE in the preceding quarter.** Three gap classes now on the ledger: (1) PRE-REPO
(before Feb 14 — lives in the project space; backfill when a thread reaches for it); (2) MIGRATION
LOSS (covered in the project space, glossed in transfer); (3) **CONSTRUCTION BLIND SPOT (event fell
between repo birth and the relevant board's birth).**
⇒ **THE RULE: opening a NEW board requires a STRUCTURAL-EVENTS INVENTORY of the preceding ~quarter —
regime changes, cartel/alliance breaks, capacity destruction, defaults, nationalizations — filed as
the board's inherited-state header. The present is not the history.**
⬜→✔(partial 8/31: geopolitical/oil class CLOSED via project-gopher sweep — war-board inherited-state header; fiscal/legal/tech-policy classes still open) **RETROACTIVE SWEEP: what else broke Feb-July that the July-built boards silently inherited?
Three surfaced via Jake in four days (Maduro/January, the May 14-15 summit, UAE/May 1). Ask the
project space; more are likely.**
