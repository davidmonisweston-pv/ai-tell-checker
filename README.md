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

- **Mechanical (P0):** chatbot artifacts ("I hope this helps!"), sycophancy
  ("You're absolutely right"), cutoff disclaimers, chat-tool citation-markup
  leaks, AI-tool URL tracking params and attribution leaks ("Co-Authored-By:
  Claude"), unfilled placeholders, hidden zero-width/bidi unicode
  (detector-bypass fingerprints), unsourced vague attributions and speculative
  gap-fillers — suppressed when a digit, URL, citation, or code shares the
  sentence — and reasoning-chain artifacts. Near-zero false-positive rate.
- **Tiered vocabulary (P1/P2):** Tier-1 words flagged on sight (delve, leverage,
  robust, seamless, utilize, …, plus the Claude-signature "load-bearing"
  metaphor, with a construction-noun carve-out); Tier-2 words flagged only when
  2+ appear in the same paragraph (harness, foster, empower, crucial,
  ecosystem, …); Tier-3 words and boilerplate phrases flagged only by density.
- **Structural (P1/P2):** antithesis ("it's not X — it's Y"), hedge-stacked
  predictions, "let's" transition openers, throat-clearing openers ("here's the
  thing:"), emphasis crutches ("Full stop."), colon-dramatic reveals ("The best
  part: it learns."), negative-listing runs ("Not a X. Not a Y."), aphorism
  formulas ("the lifeblood of"), list-label periods, title-case headings, emoji
  in headings, rule-of-three triad density, generic future-narrative closers,
  social endorsement closers, em-dash over-use (closed word—word dashes gate at
  P1; spaced ones only warn at 2× the cap).
- **Stylometric (P2):** type-token ratio (vocabulary diversity), paragraph-length
  uniformity, repeated sentence openers (anaphora, gated against function words).
- **Escape hatch:** fenced code, inline code, blockquotes, and long double-quoted
  spans are stripped before scanning, so quoted material and code aren't flagged.

## Usage

```bash
python3 -m ai_tell_checker draft.md            # full scan
python3 -m ai_tell_checker draft.md --quick    # P0+P1 only, skips tier-3/stylometric
python3 -m ai_tell_checker draft.md --json     # machine-readable
python3 -m unittest discover tests             # rule regression tests (positive/negative examples)
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

## Prior art and acknowledgements

Several rules in this ruleset were adapted from a July 2026 survey of the most
popular open-source AI-slop tools. Credit where it's due:

- **[seochecks-ai/slopless](https://github.com/seochecks-ai/slopless)** — the
  other deterministic linter in the field, and the source of our best
  false-positive guards: concrete-evidence suppression (a digit, URL, citation,
  or code span in the same sentence cancels a vague-attribution flag), the
  closed-vs-spaced em-dash distinction, hidden-unicode detection, and the
  function-word-gated anaphora rule.
- **[hardikpandya/stop-slop](https://github.com/hardikpandya/stop-slop)** —
  throat-clearing openers, emphasis crutches ("Full stop.", "Let that sink
  in"), and negative-listing runs.
- **[petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop)** — the
  colon-dramatic reveal pattern and formatting-slop tells (emoji in headings).
- **[blader/humanizer](https://github.com/blader/humanizer)** — aphorism
  formulas ("the lifeblood of"), tailing-negation runs, speculative
  gap-fillers, and the cluster-not-instance flagging philosophy.
- **[conorbronsdon/avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing)** —
  the "load-bearing"-as-metaphor Claude tell (with its construction-noun
  carve-out) and several tiered-vocabulary additions. Its taxonomy
  independently converged on the same 3-tier/P0-P1-P2 design as this tool.
- **[tbhb/vale-ai-tells](https://github.com/tbhb/vale-ai-tells)** — the
  AI-attribution-leak category ("Co-Authored-By: Claude" residue in prose).

Rules those projects tried and reverted after false-positive audits (e.g.
wall-of-text regexes, bare vague-quantifier flagging) were deliberately left
out here on the strength of their evidence.
