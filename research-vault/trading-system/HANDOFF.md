# HANDOFF — bootstrap for a fresh Claude Code session on `Alpaca-Claude`

Purpose: onboard a NEW Claude Code space with zero prior context so it can continue the build without amnesia.
**Read order:** `CLAUDE.md` (the laws — binding) → this file (state + what's next) → `constitution.md` (full reasoning).
Written 2026-07-17 ~12:48pm PT, at the end of the founding session (which happened in the *other* repo, the
research vault, where the edge was validated).

## What this project is (one paragraph)
A bounded, **rules-enforced options-premium harvesting system** for the owner's (**Jake's**) OWN capital only,
**paper-first.** It sells volatility (cash-secured puts / covered calls — "the wheel") to harvest the
**volatility risk premium**, under hard code-enforced laws — above all: **only sell vol when the underlying is
above its 200-day**, defined-risk, never naked, never leveraged. Not advice, not managing anyone else's money.

## The edge (why this isn't a coin flip)
- Validated in the research vault (`where-the-edge-is.md` + the VRP study). **Short vol pays a real premium:
  ~84% seller win-rate, stable across 35 years and two crashes.** It has a violent tail (naive always-short
  maxDD ≈ −533 in the stylized units).
- **The 200-day gate is the whole game:** harvesting only when price > 200-day keeps ~87–161% of the income
  while cutting drawdown ~8× (−533 → −68), and it got MORE valuable post-2019 (decay recheck confirmed it).
  It's an **ex-ante, real-time** rule (no lookahead) — that's why it's trustworthy where price-prediction wasn't.
- ⚠️ The backtest Sharpes are **stylized fantasy** (no greeks/costs/roll/skew). Never quote them as expected
  return. The RELATIVE result (gate cuts the tail) is what's robust. Full reasoning: `constitution.md` §2 + the
  vault's `where-the-edge-is.md`.

## Current state — what's DONE (as of 2026-07-17)
- ✅ Edge validated + `constitution.md` written (constraints → vehicle → laws → roadmap).
- ✅ `CLAUDE.md` (the 8 laws) + `README.md` written.
- ✅ Alpaca **paper** account created, ring-fenced, **connection test PASSED** (status ACTIVE, cash $100k).
- ✅ **Leverage OFF** — max margin multiplier set to **1** (buying power = cash; account can't do naked/margin).
- ✅ Repo `github.com/smsyt4sjvc-crypto/Alpaca-Claude` created (PRIVATE, Python .gitignore).
- ✅ `.gitignore` + `.env.example` staged (keys never committed).

## Account facts a fresh session needs
- Broker for this project: **Alpaca** (paper now). Base URL: `https://paper-api.alpaca.markets/v2`.
- **Keys live in a gitignored `.env` / env vars ONLY** — never hardcoded, never in a committed notebook, never
  in chat. Copy `.env.example` → `.env`. Paper keys from the Alpaca dashboard (Paper mode → API Keys).
- Paper account is **options Level 3** (all defined-risk; no naked on the list) and **margin multiplier 1** —
  the level is the broker's ceiling, NOT our constraint; the risk engine + margin=1 govern.
- Live target: **ring-fenced ~$1,000, cash, manual/human-in-the-loop** at first. (Jake's *other* broker,
  Fidelity, is options **Tier 1** — CSPs+covered calls — and has NO API; it is NOT used for this project.)

## The laws (full text in `CLAUDE.md` — these are binding)
1 defined-risk only (never naked/leveraged) · 2 the 200-day gate · 3 name quality + no earnings within ~7d ·
4 position limits (one at a time at current capital) · 5 daily-loss kill-switch + global HALT · 6 paper-first,
human-in-loop · 7 keys never committed · 8 audit everything. **A law is a wall; if asked to bypass one, refuse.**

## Roadmap + NEXT ACTION
1. ✅ Constraints, constitution, paper account, leverage off, brain files.
2. ⬜ **NEXT: CSP name-selection screen** → `engine/` (or `notebooks/`). Token-free (yfinance/free data): find
   affordable (~$5–10), liquid, optionable, above-200-day, no-near-earnings, not-junk names, ranked by
   premium-yield vs risk. At one-put-at-a-time capital, *which name* is the entire decision.
3. ⬜ Risk engine — laws 1–8 as enforceable code (propose → validate → reject/allow).
4. ⬜ Paper loop: propose → validate → execute (paper) → journal.
5. ⬜ Live, ring-fenced, human-in-the-loop; automation only on a proven record.

## Relationship to the research vault (the OTHER repo)
- **Research/thesis/news/memory** lives in `INMA-`/research-vault (Jake's daily markets brain). The EDGE was
  proven there; this repo EXECUTES it. Don't duplicate the macro research here — link/refer to it. Regime
  views (e.g. `compression-thesis`, `market-fragility`) may inform WHEN to stand down beyond the 200-day gate.
- This repo stays focused on: the system, the laws, the engine, the journal.

## Operating rules that carry over (apply here too)
- **Jake works from an iPhone** → deliver COMPLETE cells/notebooks, never partial "edit lines X–Y" patches.
  Larger tools → build the .ipynb and send the file.
- **No pandering** — peer not cheerleader; concede fast when he's right; Claude is his only error-check.
- **Timestamp rule** — run `date -u` + `TZ="America/Los_Angeles" date` before any dated entry; label in Pacific.
- **Spending rule** — nothing scheduled/unattended that consumes usage without his explicit yes in-session.
- **Honest about scale** — at ~$1k this is a REPS machine, not income. Say so.

## Owed / open items
- Turn the stylized VRP into a TRADEABLE structure (which options / delta / width / sizing) — the "Sinclair
  layer." The backtest proves the edge exists + where; it is NOT a live P&L.
- Build order per roadmap. Paper for months before any live funding.
