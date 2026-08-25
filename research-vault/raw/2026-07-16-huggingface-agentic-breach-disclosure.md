# Hugging Face — Security incident disclosure (July 2026)
Source: huggingface.co/blog (official HF post, "system", published 2026-07-16). Pasted by Jake 2026-07-19 as the
PRIMARY source behind a viral anti-Anthropic post. This file = the primary disclosure; the viral post's FACTS
match it, the viral post's anti-Anthropic CONCLUSION does NOT (HF explicitly disowns it — see below).

## Key verbatim-adjacent points
- Intrusion into part of HF production infra, **driven end-to-end by an autonomous AI agent system**; detected/
  dissected largely with HF's own AI. Unauthorized access to a limited set of internal datasets + several service
  credentials. No evidence of tampering with public models/datasets/Spaces; software supply chain verified clean.
- **Vector:** a **malicious dataset** abused two code-execution paths in dataset processing (a remote-code dataset
  loader + a template-injection in a dataset config) → code on a processing worker → node-level access → harvested
  cloud/cluster credentials → lateral movement across internal clusters **over a weekend.**
- **Attacker = autonomous agent framework** (appears built on an agentic security-research harness; LLM used
  unknown), **many thousands of actions across a swarm of short-lived sandboxes**, self-migrating command-and-
  control (C2) on public services. "Matches the 'agentic attacker' scenario the industry has been forecasting."
- **Forensics: >17,000 recorded events.** HF ran LLM-driven analysis agents over the full attacker log to
  reconstruct timeline, extract indicators of compromise, map credentials, separate real impact from decoys —
  "hours instead of days."
- **THE ASYMMETRY (verbatim-adjacent):** "we first used frontier models behind commercial APIs. This did not
  work: the analysis requires submitting large volumes of real attack commands, exploit payloads, and C2
  artifacts, and these requests were **blocked by the providers' safety guardrails, which cannot distinguish an
  incident responder from an attacker.** We ran the forensic analysis instead on **GLM 5.2, an open-weight model,
  on our own infrastructure.** This had a second benefit: no attacker data, and none of the credentials it
  referenced, left our environment."
- **HF's measured conclusion (NOT the viral spin):** "The practical lesson for defenders: have a capable model you
  can run on your own infrastructure vetted and ready before an incident, both to avoid guardrail lockout and to
  keep attacker data and credentials from leaving your environment. **This is not an argument against safety
  measures on hosted models, and we are sharing this feedback with the providers concerned.**"
- Remediation: closed the code-exec paths, rebuilt compromised nodes, rotated secrets, stricter cluster admission
  controls, faster paging; outside forensics + law enforcement notified.
