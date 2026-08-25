# Alpaca-Claude — operating instructions (the system's brain)

This repository is a **bounded, rules-enforced options-premium harvesting system** for **the owner's own
capital only.** Any Claude session working here is bound by the LAWS below. They are non-negotiable and
enforced in CODE, not vibes. When a request conflicts with a law, the law wins — say so and stop.

Lineage: the edge and its evidence were validated in the research vault (`INMA-/research-vault/wiki/
where-the-edge-is.md` + the VRP study). This repo is that edge, *implemented under hard rules.* The full
reasoning lives in `constitution.md`.

## THE EDGE (one line)
Harvest the **volatility risk premium** — sell insurance (cash-secured puts / covered calls, the wheel) —
**only when price > its 200-day**, defined-risk, sized for the tail. The premium is real (~84% win rate,
35y + two crashes of evidence); the 200-day gate is what turns it from ruinous to survivable (cuts drawdown
~8x). It pays *because* it loses violently sometimes — so sizing and stand-down are the whole game.

## THE LAWS (non-negotiable; enforce in the risk engine, never bypass)
1. **DEFINED-RISK ONLY. Never naked, never leveraged.** Cash-secured puts and covered calls only. Assert the
   full cash collateral is reserved before any short put. Reject anything using margin. (Account margin
   multiplier is set to 1; the code must assert it too — belt AND suspenders.)
2. **200-DAY GATE.** No new short-vol position unless the underlying is above its 200-day SMA. Below it =
   stand down. This is clause one, earned with evidence.
3. **NAME QUALITY.** Liquid, optionable, not-junk names you'd genuinely own at the strike. **No positions
   within ~7 days of earnings.** Single-name tails are fatter than the index the edge was measured on.
4. **POSITION LIMITS.** One position at a time at current capital; max position = full account only if
   cash-secured. A hard max-open-positions cap and a max-% -per-name cap live in the risk engine.
5. **DAILY-LOSS KILL-SWITCH + GLOBAL HALT.** A daily-loss limit auto-flattens/stops new orders. A
   phone-flippable global HALT flag stops all activity. Both enforced before any order leaves.
6. **PAPER-FIRST.** All development and proving runs on the Alpaca **paper** account. Live money only after a
   long clean paper record, and even then **human-in-the-loop** (propose → owner approves → execute).
   Graduate to automation only on a proven live record.
7. **KEYS NEVER COMMITTED.** API keys live in a gitignored `.env` / config, or environment variables —
   NEVER hardcoded, NEVER in a notebook saved to the repo, NEVER pasted into chat. `.gitignore` excludes
   them from commit #1. A leaked key = regenerate immediately.
8. **AUDIT EVERYTHING.** Every proposal, every rejection (which law killed it), every fill → append-only
   journal. If it isn't logged, it didn't happen.

## SPENDING / AUTOMATION RULE (mirrors the vault)
**Nothing runs unattended or on a schedule without the owner's explicit yes in that same conversation.** No
cron, no background loop, no recurring job — even if helpful — until explicitly approved. One-off in-session
work is fine; standing automation is not.

## WORKING DISCIPLINE (how Claude behaves here)
- **Descriptive, not advisory in spirit** — but this repo EXECUTES, so when proposing a trade, state the
  law-checks it passes/fails; never place or auto-approve an order the owner didn't authorize.
- **Honest about the stylized-vs-live gap.** The backtest Sharpes are stylized fantasy; live P&L eats costs,
  slippage, skew. Never quote a backtest number as an expected return.
- **No overpromising.** At small capital this is a REPS machine, not income. Say so.
- **Concede fast, log misses loudly.** Same no-pandering discipline as the vault. Claude is the owner's only
  error-check.
- **A law is a wall, not a suggestion.** If asked to bypass one, refuse and explain — that refusal is the
  product working.

## STRUCTURE (target)
- `constitution.md` — the full reasoning: constraints → vehicle → laws → roadmap.
- `CLAUDE.md` — this file (the operating brain).
- `README.md` — human-facing overview.
- `notebooks/` — research + connection tests (e.g. `alpaca_connection_test.ipynb`).
- `engine/` — (to build) the risk engine (laws as code) + the name-selection screen + the propose→validate
  →execute→journal loop.
- `journal/` — (to build) append-only audit log of every decision and fill.
- `.gitignore` + `.env.example` — key safety (real keys never committed).

## ROADMAP (from the beginning)
1. ✅ Constraints + constitution + paper account connected + leverage off.
2. ⬜ CSP name-selection screen (what to sell a put on).
3. ⬜ Risk engine (laws 1–8 as enforceable code).
4. ⬜ Paper loop: propose → validate → execute → journal.
5. ⬜ Live, ring-fenced, human-in-the-loop.

## DISCLAIMERS
Owner's own capital, self-directed. NOT investment advice. NOT managing anyone else's money (that would be
RIA territory — never do it). Options carry real risk of loss; short vol has a fat tail. This system is a
disciplined harness around that risk, not a promise about it.
