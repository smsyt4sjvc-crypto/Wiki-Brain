# RAW — DeLong: "Convergence in LLM Quality & Slowdown in LLM Improvement" (pasted by Jake 2026-07-26 ~11:55pm PT)

Source: Brad DeLong, Grasping Reality weblog, **Jul 21, 2026 12:38pm**, reprinting Paul Kedrosky
("Kimi, Model Convergence, & the Post-Training Era", paulkedrosky.com), chart sourced to Epoch.ai
Capability Index (ECI). Companion chart: `2026-07-26-kedrosky-epoch-convergence-chart.png`.
Verbatim paste below (asterisked expletives as pasted). Never edited.

---

**DELONG'S GRASPING REALITY WEBLOG**

### **Convergence in LLM Quality & Slowdown in LLM Improvement: CHART OF THE DAY**
From two Epoch-Capability points a month back in 2023 to one every six months today, with the spread of assessed model capabilities across frontier labs shrinking by half...

**BRAD DELONG** — **JUL 21, 2026 AT 12:38 PM**

But are these epoch.ai assessments real numbers that mean anything? And how could we tell? The apparent slowdown in LLM improvement is exactly what you would expect if the LLMs are at base just emulating internet s***posters. But if the compression = true understanding crowd is right, the scale may well be measuring the wrong thing...

Whether we are on the road to AGI hinges on an unsettled question: What are LLMs?

If they are sophisticated mimics of human conversation, plateauing capability scores make sense and the AGI story is hype.

If compression-into-weights actually recovers, by seeking minimum Kolmogorov complexity, the true generating structure of deep thought that humans carry on before they then produce their jittery and very human text, then maybe it is time to start planning to welcome our potential AGI overlords.

Paul Kedrosky reprints a graph he has had on his mind for some time:

[Chart: Model Convergence in the Post-Training Era]

> Paul Kedrosky: Kimi, Model Convergence, & the Post-Training Era: 'Moonshot's Kimi K3 model has people over-excited, as if some trend has been broken, but they're wrong.... We exited the pre-training era and became more reliant on post-training, like RLHF. In the post-training era, successive releases deliver smaller capability gains, fewer durable outliers, and less defensible technical differentiation.... The value of each incremental model release (ignoring harnesses) is falling, even if production costs aren't.... Model prices compress.... Inference becomes increasingly commoditized.... Frontier development becomes harder to monetize.... Value shifts away from the base model...

The big joker in his analysis of course is this: What exactly is on the vertical axis of these scores from epoch.ai? Why should we care? What difference does it really make?

If you believe, as I do, that LLMs are going around Robin Hood's barn, yeah, because they're "emulations of the typical internet shit poster", then frantically corrected to sanity by RLHF and such, this is as expected. You are trying to faithfully emulate what the person whose ghost you are pantomiming said, so it is really hard to get smarter than them. After a point, the better classification of what human conversations are "close" to the one the LLM is having is not worth much at all.

That leaves the use of MAMLMs for very big-data, very high-dimension, very flexible-function classification. True deep magic appears to have emerged with respect to programming here—perhaps. And there is no doubt that other superuse cases will emerge at a rate and with an impact I cannot forecast.

There are, however, people who say that the frontier model-builders are closing in on true "AGI", true "Artificial General Intelligence", something that, surveying across all of the subdomains of cognition and averaging, is human-level albeit not human-like.

When I ask them how it can possibly do this, they are either (a) silent, or (b) they say compression. They say that the "fuzzy .jpeg of the web" line of Ted Chiang's gets it exactly backwards. What the LLM does as it compresses its training data into the weights of its virtual emulation of a neural network is to, in some way, generalize. What it loses is not fuzziness, but the jitteriness of individual human error. Thus it gains the wisdom of crowds à la Sean Trott: it says not what the human did in the closest conversation, but what each of the humans would have said in all of the close conversations if each had had knowledge of what all the other humans in similar conversations were saying and thinking.

What that does is produce structural recovery: true knowledge of what is going on, in a context where it is the humans who each have only a fuzzy .jpeg view of the surface appearance of things, or at least of relationships between words.

If they are right, then this Capability Index is fundamentally wrong, and misleading us.

Um—maybe?

How could I figure this out? Damned if I know. Some thoughts below:

As best as I can figure it out, the pro-compression-induces-true-knowledge line is pushed by people like Ilya Sutskever and Jack Rae: Rae, especially, sees LLM training as computing the probability distribution that lets you transmit all of human knowledge over a low-bandwidth channel in the fewest bits, reconstructing the generating distribution rather than making a blurry copy, and so doing something much much more than pantomiming the nearest conversation internet s***poster. And Yuzhen Huang, Jinghan Zhang, Zifei Shan, & Junxian He argue that compression is indeed the essence of what LLMs are doing (arxiv 2404.09937).

And then there comes is the argumentative jump that I cannot quite follow: that the minimum-bit compression of the conversation generating function with the individual human jitteriness cleared out is what AGI is, for, in Ted Chiang's terms it is a fact that "the greatest degree of compression can [only] be achieved by understanding the text…"

Thus the core move is this: successful emulation requires minimum Kolmogorov complexity, which forces a world model. The only way to keep driving LLM loss down is to "learn" and then internally simulate and understand the processes that generated the text: physics, arithmetic, theory of mind, causal structure. Pushing compression far enough is then not analogous to intelligence; it is the operational definition of it. The model recovers as its object not an internet s***poster but rather the latent structure of cognition.

But Ted Chiang then, as I understand him, then says: the model-builders do not dare set temperature=0 because without human-like jitteriness added, the compressed version fails to convince us that it is thinking. Point. François Chollet (arxiv 1911.01547) reinforces the anti-argument with his claim that intelligence is skill-acquisition efficiency on genuinely novel tasks, and draws a sharp distinction between models that look intelligent on benchmarks that are in the hyperplane of its training data and yet have near-zero generalization capability. And Gary Marcus declares victory for the "scale is not all you need" crowd:

> Gary Marcus: Scale Is Not All You Need: 'Altman claimed that "the intelligence of an AI model roughly equals the log of the resources used to train and run it..."… He bet the entire company on this notion. He was wrong.... Let's bring in the cognitive scientists, and stop fantasizing that data and compute will solve all our problems. The time for neurosymbolic AI and world models and causality is now…

I am, in general, a bear on MAMLMs and a superbear on the usefulness of unharnessed LLMs: stochastic parrotage enables natural-language interfaces, which are wonderful. Full stop.

The thing that keeps me from being confident in my bearishness on MAMLMs in general is this: The genuine open frontier is not chat but MAMLMs used in other big-data, high-dimensional, flexible-function classification—like programming, where true deep magic has apparently emerged from Claude Code's harness. Yes, writing code is a domain where surface prediction and correct world-modeling are very very close—programs either work or don't, for there is no underlying reality to which the incantations in their correct form point. If compression is producing real generalization anywhere, that would be the cleanest place to see it.

And are there other similar domains where true deep magic is possible as well? How common are they? Where are they? Or is computer code the only domain where getting the symbols right invokes the reality directly?

So I guess the bottom line is this: right now um—maybe? is still the only sensible answer we can give.

---

## Chart contents (as read from the PNG, for text search)
"Model Convergence in the Post-Training Era" — Epoch.ai ECI score vs release date, Apr 2023 → mid-2026,
195 results, by org (OpenAI/Google/Anthropic/Meta/xAI/Other). Dashed line ≈ Jan 2024 = pre-training →
post-training era transition. Fitted curve: ~100 (Apr-23) → ~127 (Jan-24) → ~145 (mid-25) → ~151 flattening
(mid-26). Landmarks: GPT-4 (Mar-23) ~126, LLaMA-65B ~110, Claude 3 Opus ~127, Claude 3.5 Sonnet ~131,
o1-mini ~136, Gemini 2.5 Pro (Mar-25) ~140, o3 ~146, GPT-5 ~149, Gemini 3 Pro ~152, GPT-5.4/5.5 Pro ~156-160
(top edge, ABOVE fit). **Kimi 3 arrowed INSIDE the frontier band (~152-155).** Spread band visibly narrows
left → right.
