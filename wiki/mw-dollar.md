# MW/$ — the sibling compute-economics repo (`smsyt4sjvc-crypto/MW-`)

*Opened 2026-10-02 ~8:50pm PDT (filed under rule 22c) when Jake shared the link. Read-only from this vault.*

**WHY THIS MATTERS (plain English):** Jake runs a second, separate research repo that measures one thing: how many dollars of revenue an AI data center earns per megawatt, company by company, plus a scorecard of which construction bottlenecks (power, cooling, electrical gear) are tight and which suppliers profit. It is the measurement engine for the "chips vs. power" question this vault argues about. Its daily company reviews stopped on 9/20.

## DATA (observed — clone of `main` at `71e4ac5`, 2026-10-02)
- **What it is:** "Agent-native persistent memory for AI-compute economics." Source of truth = atomic JSONL under `memory/` (236 facts · 107 sources · 24 claims · 15 methods · 28 open questions); CSV/XLSX/Markdown are projections. Canonical unit: **USD millions per effective utilized IT MW-year**. Its rules mirror this vault's (DATA/THESIS split, labelled power scope, no exit-rate denominators, visible supersedes).
- **Public:** `ops/authorization.json` (as of 9/9) — `"public_publication_approved": true`.
- **Boundary, stated in MW-'s own files:** its agent must "never access, modify, synchronize with, or push to" Wiki-Brain. This vault reads MW- read-only on Jake's request and never writes to it.
- **Automation:** (a) a daily one-company review scheduled 8am PT since 9/11 (`ops/daily-task.json`, run by an external scheduler with a GitHub connector); (b) GitHub Actions rebuilding the infrastructure backlog daily and weekly (bot commit 9/28).
- **⛔ Freshness:** last company review **9/20 (Alphabet)**; reviews 9/11 ORCL · 9/12 CRWV · 9/15 NBIS · 9/16 IREN · 9/17 MSFT · 9/19 AMZN · 9/20 GOOGL; last changelog 9/22 (Ramp AI index); newest fact `as_of` 9/20 ⇒ **~12 days with no review despite a daily schedule** (next in queue: Meta — never reviewed). `state/CURRENT_STATE.md` is dated 9/10. Infrastructure board "as of 9/21, source data through 9/18," evidence "seeded_primary_sparse," coverage 15-39% per layer.
- **Its current answers (9/10 state):** operator revenue anchors ~$10-12B per IT-load GW-year (spot) · $15B (Radio Free Mobile line) · $16.3B (Nscale/Anthropic contracted) · $25B aspirational · SpaceX management guided $30-50B per GW-year · Blackwell compute content ~$25B per IT-load GW (Hopper $18B · Rubin $40B) · Vercel July: tokens +59%, price/token −13.6%, spend +37% (exact Jevons break-even +15.7%).
- **Its infrastructure board (9/21):** ACCUMULATE Trane (TT), Sterling (STRL), Comfort Systems (FIX) · ADD_HOLD Eaton (ETN) · HOLD GE Vernova (GEV), Modine (MOD) · layers: generation pressure 99 (CAPACITY_CATCH_UP), HV/interconnect 90 and cooling 84.8 (PEAK_MONETIZATION).

## THESIS (analysis)
- **Agreements with this vault:** the $16.3B/GW-yr Nscale/Anthropic anchor, the $18/25/40B NVDA content ladder and the "monetization deflating while demand is strong" read are the same numbers ([[metered-compute]], [[power-to-silicon-thesis]]); ETN add/GEV hold roughly match the money board (ETN bull 9/23 · GEV FLAT 0.5 9/30).
- **⚠️ Where MW- is stale against this vault:** its state carries Silicon Data **H100 rent −2.9% (9/2)** as "no physical-rental deflation"; this vault's 10/1 Silicon Data chart shows rents **RISING** (B200 ~+31% YTD, H100 ~+7%; [[metered-compute]] 10/1 "squeeze in the middle") — the squeeze is sharper than MW-'s last state says.
- **The one thing it could add that the vault lacks:** the compute-to-power coverage ratio from irreversible commitments only — MW- lists it as incomplete too, and the dual-clock dashboard withholds it ([[power-to-silicon-thesis]] 10/2).
- **New names for this vault:** Modine (MOD), Sterling (STRL), Trane (TT) carry ~no history here; MW-'s labels are model states on thin coverage, not trade signals (its own caveat).

**📌 REGISTERED:** ⬜ why MW-'s daily review stopped after 9/20 (Jake's scheduler) · ⬜ MW-'s Meta review when it resumes · ⬜ coverage ratio, if either repo computes it.

**Links:** [[power-to-silicon-thesis]] · [[metered-compute]] · [[buildout-bottleneck-map]] · [[money-board]]
