# Brian Armstrong (Coinbase CEO) on X — fine-tuned Qwen3.5-9B beats frontier models on fraud (Jake's paste 2026-10-11 ~7:25pm PDT)
Images: `raw/2026-10-11-x-armstrong-coinbase-qwen-finetune-fraud-metrics.png` · `raw/2026-10-11-x-armstrong-coinbase-qwen-latency.png`

## Post text (as pasted)
> We were able to fine tune an open weight model (Qwen3.5-9B) on proprietary internal data at @coinbase, and it out performed frontier models, at much lower cost and speed, for a specialized task (fraud prevention in this case).
> I think we'll see more of this pattern inside companies. The frontier models are amazing generalists. But increasingly you'll see specialist models out perform on more narrow tasks, either working on teams, or by themselves.
> We're making it easy to fine tune models internally for our employees. We even have a skill for it in our internal harness that makes it easy to spin these up and start training them:
> "/fine-tune-and-serve-llm I want to fine-tune Qwen for payments risk review. help me get started"
> I imagine we'll have some backend services that could be replaced entirely by this new architecture.

## Chart 1 — "Post-training improved fraud detection" (Figure 2; percentage-point differences, not relative %)
| metric | vs unadapted Qwen3.5-9B | vs Opus 4.5 decision agent |
|---|---|---|
| Precision | +24.2 | +7.5 |
| Recall | +19.6 | +12.0 |
| F1 | +23.0 | +9.6 |
| Dollar-weighted recall | +45.1 | +35.4 |

## Chart 2 — "Online inference: P50 and P99 latency" (successful online LLM calls; complete client-observed LLM request; "not the full checkout flow")
| | Post-trained Qwen3.5-9B | Opus 4.5 |
|---|---|---|
| P50 | 0.683 s | 1.515 s ("55% lower LLM-request P50") |
| P99 | 1.036 s | 3.312 s |

## Verification (Google News `when:7d` + Exa, ~7:30pm PDT)
- **Author:** Coinbase CEO Brian Armstrong (Lookonchain 10/12 00:49 UTC; Crypto Briefing 10/11 22:37 UTC).
- **Coinbase's two disclosures (via CryptoSlate 10/10, The Token Press 10/10, cryptonews.net):**
  - **Oct 7 — model-upgrade regression on its Onramp fraud replay:** 16,140 transactions, 7,293 users, 813 confirmed fraudulent; nine weeks before its risk agent rolled out; all matured fraud kept, legitimate traffic sampled; fixed guidance and risk-to-decision policy. Pairs: Opus 4.5→Opus 5, Sonnet 4.6→Sonnet 5, GPT-5.4→GPT-5.6 (sol). **Every newer version had lower recall, F1 and dollar-weighted recall.** Sonnet recall −22.2pp, DW recall −22.9pp; Opus recall −0.8pp; both newer Anthropic versions lower precision; GPT precision +11.5pp, recall −20.7pp, DW recall −21.8pp. Retrospective; cause not identified; no customer losses shown; dataset not releasable.
  - **Oct 8 — post-trained Qwen3.5-9B exceeded Opus 4.5 on four metrics** (F1 +9.6pp, DW recall +35.4pp), trained on historical fraud outcomes with deterministic rewards balancing fraudulent and legitimate examples. **Latency is a separate PRODUCTION measurement** (P50 0.683s vs 1.515s); "Faster inference and stronger benchmark detection came from different evaluations" (CryptoSlate).
  - Snippet (cryptonews.net, partially garbled): agent-enabled screening vs rules alone recorded 30% fewer fraudulent transactions and 22% less fraud value (⬜ exact baseline).
- **No cost figure disclosed** in what was read; "much lower cost" is the post's claim (⬜).
