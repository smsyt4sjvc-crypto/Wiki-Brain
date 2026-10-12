# Meta Muse Wonder launch + Polymarket "best AI model end of October" — checks (2026-10-12 ~1:00pm PDT)

Jake's screenshot (12:51pm PT): ZH ~12:23pm "It won't be Meta, but prediction markets increasingly confident Google will have the best AI model by the end of the month (per Arena Overall benchmark)" + ZH ~11:51am "*META DEBUTS MUSE WONDER AI MODEL WITH 'FRONTIER' CAPABILITIES". Image: `raw/2026-10-12-x-zh-polymarket-best-ai-model-meta-muse-wonder.png`.
⛔⛔ VENDOR CONFLICT, MAXIMAL: Anthropic (this vault's model vendor) is one of the four names in the market and one of the comparison models in Meta's release. Numbers and perimeters only.

## Polymarket (gamma API, ~1:00pm PT)
- Event "Which company has the best AI model end of October?" (ends 2026-10-31 16:00 UTC), volume ~$2.26M. Google 0.7025 · Anthropic 0.23 · Meta 0.0355 · OpenAI 0.0075.
- **Resolution:** the "Rank" column of arena.ai Text Arena | Overall, **style control OFF**, filtered for Models, checked Oct 31 2026 12:00pm ET; models marked "AutoEval" excluded. ⇒ one human-preference leaderboard, not "best model" in general.
- The Sep 30 step change in the screenshot (Anthropic ~88% → ~25%; Google ~10% → ~70%) lines up with Google's Gemini 4 Argon release on 9/30 (blog.google, CNBC, Reuters, TechCrunch 9/30; vault `compression-thesis:L3691`). Causation inferred from timing.

## Meta Muse Wonder (company primaries: about.fb.com 10/12 17:08 UTC; research.meta.ai/blog/muse-wonder)
- Muse Wonder + Muse Wonder Full; "state-of-the-art performance on personal and professional agentic tasks"; trained at the gigawatt-scale Prometheus data center; Active Memory / Active Focus; full safety report "soon".
- Access: Muse Wonder via Meta Model API and Muse Code today; Muse Wonder Full only for Muse Code subscribers (not on the API, per TechCrunch); will power the Muse agent, subscribers first.
- Pricing (REPORTED): API **$4.00 / $20.00 per M input/output tokens** (TechCrunch); Muse app subscriptions **$20 or $100/month**, Muse Code **$50 or $200/month** (CNBC). TechCrunch: "roughly equivalent in cost" to the top OpenAI/Anthropic models; CNBC quotes Meta's Wang: priced "meaningfully below" them — ⬜ the two accounts disagree.
- Benchmarks (Meta's own testing, model card): comparable to Fable 5.1 and GPT-6 Astra (TechCrunch); Wonder Full above Fable 5.1 and below Opus 5.5 on the Artificial Analysis Intelligence Index, per Meta (WIRED). Independent verification ⬜.
- Watermelon link: BI 7/5 (vault `compression-thesis:L3718`) — Watermelon = the next frontier model, ~10x Muse Spark compute; Investing.com 10/12 headline "Muse buys a watermelon" ties the codename to this launch (REPORTED).

## Tape (Yahoo, ~1:00pm PT)
- META prev close 741.90 · 748.07 at 10:00am PT (launch) · 743.23 now (+0.2%) · QQQ −1.35% · NVDA −5.2% · GOOGL +1.8% · MSFT +3.0% · AMZN +3.2%.
- META options (Cboe delayed, META 743.53, iv30 44.6): 10/23 ATM straddle 5.1% · 10/30 8.6% · Nov-20 11.0% (was ±11.7% on 10/2 per flag-board). Implied for a Q3 print inside the 10/30 expiry ≈ √(8.6² − (5.1·√(14/9))²) ≈ 5.8%. Q3 date still not confirmed by Meta IR (⬜; ~10/28 inferred).

## ⛔ CORRECTION (2026-10-12 ~1:15pm PDT)
The "Tape" section above used `meta.chartPreviousClose` from a range=5d / interval=5m pull, which is the close five sessions back, not Friday's (error class 2). Correct via `tools/tape.py` (Fri 10/9 close → Mon 10/12 close): META 718.67 → 742.96 **+3.38%** · QQQ −0.70% · MSFT +1.14% · AMZN −1.11% · AAPL +1.29% · GOOGL +0.30% · NVDA −1.29%. META intraday (Yahoo 5m, PT): open 727.97 · 7:00am 743.68 · 9:55am 739.00 · 10:00am 748.07 · close 742.96 ⇒ the gain came before the 10am launch.
