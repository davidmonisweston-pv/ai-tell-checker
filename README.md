# ai-tell-checker

A deterministic, stdlib-only detector for AI writing tells. No LLM in the loop, no
third-party dependencies — every number is computed in Python so results are
reproducible and auditable.

**Designed to be extracted into its own repository.** This directory has no
dependency on anything else in the parent project; it can be copied out wholesale,
`pip install -e .`'d, and published on its own. It ships a generic default ruleset
(no author-specific calibration) — for corpus-calibrated register checking against
a specific writer's voice, see the sibling `tools/voice_calibration` package, which
consumes this one but is not required to use it.

## What it catches

- **Mechanical (P0):** chatbot artifacts ("I hope this helps!"), cutoff disclaimers,
  chat-tool citation-markup leaks, AI-tool URL tracking params, unfilled
  placeholders, unsourced vague attributions ("experts believe"), reasoning-chain
  artifacts ("let's think step by step"). Near-zero false-positive rate.
- **Tiered vocabulary (P1/P2):** Tier-1 words flagged on sight (delve, leverage,
  robust, seamless, utilize, …); Tier-2 words flagged only when 2+ appear in the
  same paragraph (harness, foster, empower, crucial, ecosystem, …); Tier-3 words
  and boilerplate phrases flagged only by density.
- **Structural (P1/P2):** antithesis ("it's not X — it's Y"), hedge-stacked
  predictions, "let's" transition openers, list-label periods, title-case
  headings, rule-of-three triad density, generic future-narrative closers, social
  endorsement closers, em-dash over-use.
- **Stylometric (P2):** type-token ratio (vocabulary diversity), paragraph-length
  uniformity.
- **Escape hatch:** fenced code, inline code, blockquotes, and long double-quoted
  spans are stripped before scanning, so quoted material and code aren't flagged.

## Usage

```bash
python3 -m ai_tell_checker draft.md            # full scan
python3 -m ai_tell_checker draft.md --quick    # P0+P1 only, skips tier-3/stylometric
python3 -m ai_tell_checker draft.md --json     # machine-readable
```

Exit code 0 if no P0/P1 findings; 1 otherwise. P2-only findings don't fail the gate.

## Library use

```python
from ai_tell_checker import run
metrics, findings = run(open("draft.md").read())
```

Pass a `profile` (see `voice_calibration.Profile`) to add register-range checks and
reclassify any default tell as `allow` (never flag) or `soft` (rate-gated) for a
verified author usage pattern.
