# Trading System — Constitution (FOUNDATION / v0)

Started 2026-07-17 ~11:00am PT. A bounded, rules-enforced volatility-premium harvest for **Jake's own capital
only** (self-directed — no other people's money, ever; that would be RIA territory). **Paper-first.** This doc
is the foundation stone; it grows clause by clause as we build. Sister to [[where-the-edge-is]] (the edge) and
[[market-fragility]] (the stand-down signals). This folder (`trading-system/`) is designed to lift into a
standalone repo later.

> Design order (non-negotiable): **constraints → vehicle → laws → paper → (much later) live.** You design
> AROUND the constraints, not the other way around.

> **Destination repo (created 2026-07-17):** `github.com/smsyt4sjvc-crypto/Alpaca-Claude` (PRIVATE, README +
> Python .gitignore). This `trading-system/` folder is built in the vault (where Claude has push access) and
> TRANSPLANTS into Alpaca-Claude later (from a computer, or a session where that repo is in Claude's scope).
> Claude currently CANNOT push to Alpaca-Claude (out of GitHub-tool scope). First file into it = a .gitignore
> that excludes secrets/config; keys ALWAYS via gitignored config/env, NEVER hardcoded or committed.

## §0 — ACCOUNT CONSTRAINTS (the foundation; everything is built on these)
- **DECISION 2026-07-17: the project runs in a SEPARATE, RING-FENCED account — NOT Jake's main Fidelity.**
  Safety principle: *bound the downside to a number you can name.* A dedicated account caps the blast radius at
  what it's funded with; the main savings never share space with the AI + an unproven rules engine.
- **Existing account (context, NOT used for this project): Fidelity, options Tier 1** (CSPs + covered calls
  permitted; no spreads/naked). Has **no retail API** → couldn't be automated anyway. Left out on purpose.
- **Project broker: Alpaca (recommended).** API-first (laws-as-code can enforce + execute), **paper account
  built in** (real data, fake money), $0 min, commission-free, options **Level 1 = covered calls + CSPs**
  (same core as Fidelity Tier 1 → the CSP design carries over). IBKR = heavier alt; avoid Robinhood (no API).
- **The separate broker's API UNLOCKS the original vision** — an AI-managed, rules-enforced, recurring-task
  loop — which the Fidelity(manual) path could never do. Separate ≠ just safer; it's *more capable.*
- **Capital: ~$1,000, cash, ring-fenced** → one CSP at a time on a ~$5–10 name (strike×100 collateral).
  **Learning/proof vehicle, NOT income** (~$20–60/mo premium). The real deliverable of this phase = REPS, not $.
- **Safest sequence (costs $0 to start):** (1) open Alpaca **paper** today — free, no funding; (2) build + run
  the whole loop on paper for MONTHS, zero real $ at risk; (3) only then fund the small live account; (4)
  graduate size on a clean paper+live record. The build needs reps, not money — paper gives unlimited reps free.

### §0.1 — MILESTONE + a key finding (2026-07-17 ~11:52am PT): paper API CONNECTED; it's a MARGIN account
- ✅ Alpaca paper connection test passed: status ACTIVE, cash $100,000, **buying power $400,000 (4x)**, PDT flag None.
- **⚠️ Buying power 4x cash = a MARGIN account.** Consequence: **Alpaca will let us sell puts on MARGIN (naked)**
  — unlike Fidelity Tier 1 (cash), which physically forbids it. **The broker guardrail is GONE.** Therefore the
  "cash-secured / defined-risk only" law MUST be enforced in OUR code (the risk engine), not assumed from the
  account. This is the live proof of "laws as CODE, not suggestions." First risk-engine job = assert full cash
  is reserved before any short put; reject anything that would use margin/leverage. (Live phase: consider a
  CASH account to get the broker guardrail back, or keep margin + enforce in code — decide before funding.)
- **✅ RESOLVED same session (Jake, unprompted):** set **max margin multiplier 4 → 1** → buying power now = cash
  ($100k), **no leverage possible.** The broker guardrail is RESTORED — the account itself now prevents naked/
  margin puts. Belt AND suspenders (account-enforced + risk-engine-enforced). Behavior modeled: saw an unwanted
  risk and turned it off STRUCTURALLY so the mistake is impossible, rather than relying on willpower. That IS
  the project's discipline. (Leverage now moot — multiplier stays 1; risk engine still asserts cash-secured.)
- **Paper options approval = LEVEL 3** (covered calls, CSPs, long calls/puts, spreads, covered straddles,
  multi-leg — all DEFINED-RISK; NO naked writing on the list). Alpaca won't let paper downgrade to L1 — a
  non-issue: the approval level is the broker's CEILING on order types, not our constraint. What we trade is
  governed by (a) margin=1 (can't exceed cash) + (b) the risk-engine allowlist (wheel only). Ceiling > floor;
  we never walk up to the ceiling. Level matters only on the LIVE account (applied for separately; expect L1–2).

## §1 — THE VEHICLE (what the constraints force, and it's the right tool)
**The regime-gated wheel:**
1. Sell a **cash-secured put** on a liquid, quality, optionable name you'd genuinely be happy to own, at a
   strike you'd accept — **only while price > its 200-day**, **not within ~7 days of earnings**.
2. Collect the premium = the volatility risk premium (the validated edge, single-name expression).
3. If assigned → you own 100 shares → sell **covered calls** above your cost basis → repeat.
- This is the ONLY capital-efficient VRP vehicle at Tier 1 / $1k, and it's defined-risk by construction.
- ⚠️ Callback: the wheel was on the "four dead systems" list — dead as a way to BEAT buy-and-hold in a bull
  (caps upside). It is ALIVE as a **regime-gated premium harvest**. Different job; the discipline is the difference.

## §2 — CLAUSE ONE (the first law — earned, evidenced)
**Harvest vol ONLY above the 200-day. Stand down below it.**
- Evidence ([[where-the-edge-is]] VRP study + decay recheck): the 200-day gate keeps ~87–161% of the income
  while cutting drawdown ~8x (−533 → −68), across FULL / 2010+ / 2019+ eras — and got MORE valuable post-2019.
  It's an **ex-ante, real-time** rule (no lookahead), battle-tested through 2020 & 2022.
- Caveat baked in: the 200-day is LAGGING — a bolt-from-blue crash from ABOVE the line still bites. Size for
  the residual tail; never treat the gate as a force field.

## §3 — HONEST RISKS (the single-name tail vs the index we tested)
- The VRP study was on the INDEX. Single-name vol has a FATTER idiosyncratic tail (earnings gaps, low-priced
  junk can −30% on news). Mitigations become laws: **liquid + quality names only, no near-earnings, above the
  200-day, only names you'd own at the strike.**
- Assignment is not failure — it's the deal. You sold the put because you'd own it. If you wouldn't, don't sell it.

## §4 — BUILD ROADMAP (from the beginning)
1. **§0 constraints** — done (this doc).
2. **CSP name-selection screen** (Colab, token-free): the affordable/liquid/above-200d/no-near-earnings/
   not-junk optionable universe under ~$10, ranked by premium-yield vs risk. ← *next*
3. **Complete the laws** (constitution §5+): position size, max-loss/kill-switch, one-position rule, logging,
   halt flag — as enforceable CODE for the paper engine.
4. **Alpaca paper account**: prove the whole loop (propose → validate → execute → journal) with fake money,
   months. Free, no funding — the build target from here.
5. **Live (Alpaca, ring-fenced ~$1k)**: one CSP at a time, above the 200-day. START human-in-the-loop
   (propose → Jake approves → execute); graduate to automated only on a clean paper+live record. The API
   makes automation POSSIBLE, but earn it — don't start there.

## §5+ — LAWS AS CODE (to be written)
*(placeholder — the enforceable risk engine: instrument allowlist, max position % , defined-risk-only assert,
daily-loss kill-switch, max open positions, mandatory audit log, phone-flippable global HALT.)*

## §6 — OPERATIONAL SECURITY (account safety — a law, not an afterthought)
- **API secret = account password.** Never shared, never in a public repo, never in chat. Leaked → regenerate
  immediately (kills the old key). Paper keys now; same discipline so it's automatic when live.
- **2FA app backup, not reliance on broker recovery.** Alpaca's own 2FA recovery is clunky (forum-confirmed).
  Mitigate by backing up the AUTHENTICATOR APP (Authy cloud backup w/ password, or Google Authenticator sync)
  → lost phone = re-sync, no dependence on broker codes.
- **LIVE-phase requirement (before real money):** saved recovery/backup codes in **2 separate secure places**
  (password manager + one offline). Paper phase: app-backup suffices. Different stakes, different rigor.
- Principle: the fastest way to lose a trading account isn't a bad trade — it's losing ACCESS or leaking a KEY.
  Treat key management + recovery as clause-level laws.
