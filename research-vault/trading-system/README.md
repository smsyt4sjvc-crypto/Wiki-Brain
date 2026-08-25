# Alpaca-Claude

A **bounded, rules-enforced options-premium harvesting system** — for the owner's own capital only, paper-first.

It harvests the **volatility risk premium** (selling cash-secured puts / covered calls — "the wheel") under
hard, code-enforced laws, the most important being: **only sell vol when the underlying is above its 200-day**,
defined-risk, never naked, never leveraged. The edge and its evidence were validated first as research (short
vol above the 200-day: ~84% win rate over 35 years, and the 200-day gate cuts drawdown ~8x). This repo is that
edge implemented with guardrails.

## Safety model (read first)
- **Paper-first.** Everything is developed and proven on an Alpaca *paper* account (fake money). Live money
  only after a long clean paper record — and even then, **human-in-the-loop** (the system proposes, the owner
  approves, then it executes).
- **Ring-fenced.** A dedicated, small account. The blast radius is capped at what it's funded with. Never the
  main savings.
- **No leverage, no naked.** Account margin multiplier = 1; the code asserts cash-secured/defined-risk too.
- **Keys never committed.** API keys live in a gitignored `.env` / environment only. Never hardcoded, never in
  a saved notebook, never in chat. See `.gitignore`.
- **Laws as code.** The rules live in a risk engine that *rejects* any order breaking them — before it reaches
  the broker. The rules are walls, not suggestions.

## What's here
- `CLAUDE.md` — the operating brain (the laws any Claude session here is bound by).
- `constitution.md` — the full reasoning: constraints → vehicle → laws → roadmap.
- `notebooks/` — research + the Alpaca paper connection test.
- `engine/`, `journal/` — to build (risk engine, name screen, the loop, the audit log).

## Status
Paper account connected, leverage off, constitution written. Next: the CSP name-selection screen, then the
risk engine.

## Disclaimer
Owner's own capital, self-directed. **Not investment advice.** Not for managing anyone else's money. Options
carry real risk of loss; short volatility has a fat tail. This system is a disciplined harness around that
risk — not a promise about it.
