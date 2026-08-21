# Phase 5 — AI Match Explanation Layer (Bedrock): Manual Test Checklist

AWS setup: Bedrock model access enabled in `eu-north-1`. The account only had current-generation
Anthropic models available (no legacy Claude 3) — confirmed via `list_foundation_models` /
`list_inference_profiles`, and landed on the EU cross-region inference profile
`eu.anthropic.claude-haiku-4-5-20251001-v1:0` (Haiku, for cost) after the plain model ID returned
`ValidationException: model identifier is invalid`. IAM access key provided by the user, stored in
`backend/.env` (gitignored, confirmed not tracked) and loaded into the api container via
`env_file` in docker-compose — never committed, never echoed back in chat.

Prompt design: `app/services/explain.py` hands the model a fixed fact block (counterparty name/country,
M4 tier + score, M3's pooled on-time ratio / median delay / transaction count, the two SME names, matched
amount) with an explicit system instruction not to invent numbers or claims outside that block. On any
Bedrock failure, generation falls back to a deterministic template built from the same fact dict — a
netting run must never fail because the AI layer is down. `eligibility_flag`: tiers A/B → `auto_eligible`,
C/D/E → `needs_review`, both stored on `OffsetMatch` alongside `confidence_tier`, `justification_text`,
and `ai_generated` (true = real Bedrock completion, false = fallback template).

- [x] Trigger a netting run, confirm every match has a non-empty, coherent justification string — live run
      produced 4 matches, all with substantive text (e.g. *"This netting match of $60.0 USD-equivalent
      reduces payment obligations across three parties... tier E rating (27.0/100) and poor payment history
      (10.0% on-time rate with 2.0-day median delays)"*).
- [x] Confirm justification text only references facts present in the input — hand-checked against live
      data: Northwind Traders' justification cited **"16.7% on-time performance with a median delay of 1.5
      days"** and **"tier D rating (46.19/100)"**, both verified exact matches against
      `GET /behavior-profiles/{id}` (`on_time_ratio=0.16666...`, `median_delay_days=1.5`) and
      `GET /reliability-scores/counterparty/{id}` (`score=46.19, tier=D`). No fabricated numbers.
- [x] Confirm a Tier A/B match is flagged `auto_eligible` and a Tier C/D/E match is flagged `needs_review`
      — constructed a small matchable pair for Harbor Logistics (tier B from Phase 3): flagged
      `auto_eligible`. All three D/E-tier matches in the same run flagged `needs_review`.
- [x] Kill Bedrock connectivity (bad credentials) and confirm the netting run degrades gracefully — ran
      netting with `BEDROCK_MODEL_ID` overridden to an invalid value: the run completed normally (4/4
      matches created), every match got `ai_generated=false` with a coherent fallback justification built
      from the same real facts (no crash, no null/empty text). Exception logged, not raised.
- [x] Check AWS Bedrock usage/cost after a batch of runs — sampled real token usage from a live call:
      **210 input / 67 output tokens** per justification (Haiku-tier pricing). A full run of 3–4 matches is
      roughly 1,000 tokens total — negligible against the $300 credit budget. (Console-side dollar
      confirmation is on the user's AWS Billing page — not something this session can check directly.)
- [x] Automated coverage: `tests/test_explain.py` — 6 tests covering the eligibility-flag mapping, a mocked
      successful Bedrock call, fallback on exception, fallback on empty completion, the "no history yet"
      wording branch, and `build_counterparty_context` against a real M3/M4-backed counterparty. Bedrock is
      mocked in the automated suite (fast, free, no live-credential dependency for CI); the live-model
      checks above were run by hand against the real account. Full suite: **28/28 passing**.

**Result:** PASS — Phase 5 complete, proceed to Phase 6.
