"""Positive/negative example tables for the rules added in the July 2026
expansion (field survey of humanizer / stop-slop / avoid-ai-writing /
no-ai-slop / slopless). Each rule lands with at least one text that must flag
and one that must not — the audit value of slopless's documentation-as-code
examples, as a plain stdlib test table.

Run: python3 -m unittest discover tests
"""
import unittest

from ai_tell_checker.checker import run, scan_hidden_unicode, has_concrete_evidence


def labels(text, quick=False):
    _, findings = run(text, quick=quick)
    return [f.label for f in findings]


def has_label(text, fragment, quick=False):
    return any(fragment in lab for lab in labels(text, quick=quick))


class TestHiddenUnicode(unittest.TestCase):
    def test_zero_width_space_flags(self):
        fs = scan_hidden_unicode("plain​text here")
        self.assertTrue(any("zero-width space" in f.label for f in fs))
        self.assertTrue(all(f.severity == "P0" for f in fs))

    def test_bidi_override_flags(self):
        fs = scan_hidden_unicode("normal ‮text‬ here")
        self.assertTrue(any("RLO" in f.label for f in fs))

    def test_leading_bom_exempt(self):
        self.assertEqual(scan_hidden_unicode("﻿Ordinary draft text."), [])

    def test_zwj_in_emoji_sequence_exempt(self):
        self.assertEqual(scan_hidden_unicode("family: \U0001F468‍\U0001F469"), [])

    def test_runs_on_raw_text_through_run(self):
        # even inside a code fence, hidden unicode is flagged
        self.assertTrue(has_label("```\ncode​here\n```\nprose.", "zero-width space"))


class TestMechanicalAdditions(unittest.TestCase):
    def test_sycophancy(self):
        self.assertTrue(has_label("You're absolutely right about the schema.",
                                  "sycophantic"))

    def test_attribution_leak(self):
        self.assertTrue(has_label("Fixes bug.\nCo-Authored-By: Claude", "attribution leak"))
        self.assertTrue(has_label("Report 🤖 Generated with Claude Code", "attribution leak"))

    def test_plain_credit_not_flagged(self):
        self.assertFalse(has_label("Thanks to Claude for early feedback.", "attribution leak"))


class TestConcreteEvidenceSuppression(unittest.TestCase):
    def test_vague_attribution_flags_bare(self):
        self.assertTrue(has_label("Studies show the approach works well.",
                                  "vague attribution"))

    def test_suppressed_by_citation(self):
        self.assertFalse(has_label("Studies show the approach works (Smith, 2020).",
                                   "vague attribution"))

    def test_suppressed_by_digit(self):
        self.assertFalse(has_label("Studies show a 40 percent drop in errors.",
                                   "vague attribution"))

    def test_gap_filler_flags_bare(self):
        self.assertTrue(has_label("She maintains a low profile these days.",
                                  "speculative gap-filler"))

    def test_gap_filler_suppressed_by_url(self):
        self.assertFalse(has_label(
            "It is believed that the fund closed, per https://example.com/report.",
            "speculative gap-filler"))

    def test_helper(self):
        self.assertTrue(has_concrete_evidence("grew 40% year on year"))
        self.assertFalse(has_concrete_evidence("many people think so"))


class TestTier1Additions(unittest.TestCase):
    def test_load_bearing_metaphor_flags(self):
        self.assertTrue(has_label("That is a load-bearing assumption in the model.",
                                  "load-bearing"))

    def test_load_bearing_construction_exempt(self):
        self.assertFalse(has_label("We removed a load-bearing wall during the reno.",
                                   "load-bearing"))

    def test_load_bearing_unhyphenated_exempt(self):
        self.assertFalse(has_label("The load bearing analysis was rerun.", "load-bearing"))

    def test_new_tier1_words(self):
        for text, lab in [
            ("A beacon for the industry.", "beacon"),
            ("This was a watershed moment.", "watershed moment"),
            ("An ever-evolving field.", "ever-evolving"),
            ("A thought leader in fintech.", "thought leader"),
            ("The tower stands as a reminder.", "stands as"),
        ]:
            self.assertTrue(has_label(text, lab), f"expected {lab!r} for {text!r}")

    def test_tier2_additions_cluster(self):
        text = "We galvanize teams and illuminate the quintessential path."
        self.assertTrue(has_label(text, "galvanize"))

    def test_tier2_single_word_not_flagged(self):
        self.assertFalse(has_label("The ceremony will commence at noon.", "commence"))


class TestStructuralAdditions(unittest.TestCase):
    def test_throat_clearing(self):
        self.assertTrue(has_label("Here's the thing: we never shipped it.",
                                  "throat-clearing"))
        self.assertTrue(has_label("Make no mistake, this was deliberate.",
                                  "throat-clearing"))

    def test_throat_clearing_truth_variant(self):
        self.assertTrue(has_label("But here's the truth: async wins.", "throat-clearing"))

    def test_antithesis_isnt_just(self):
        self.assertTrue(has_label(
            "Async isn't just a nice-to-have anymore — it's a requirement.",
            "antithesis"))

    def test_isnt_just_without_reveal_not_flagged(self):
        self.assertFalse(has_label("It isn't just the rain that ruined the trip.",
                                   "antithesis"))

    def test_emphasis_crutch(self):
        self.assertTrue(has_label("This matters. Full stop.", "emphasis crutch"))
        self.assertTrue(has_label("Ten years of work. Let that sink in.",
                                  "emphasis crutch"))

    def test_period_word_not_flagged(self):
        self.assertFalse(has_label("The Meiji period. It reshaped Japan.",
                                   "emphasis crutch"))
        self.assertFalse(has_label("It was a period of rapid change.", "emphasis crutch"))

    def test_colon_dramatic(self):
        self.assertTrue(has_label("The best part: it learns.", "colon-dramatic"))
        self.assertTrue(has_label("We tried it. The kicker: nobody noticed.",
                                  "colon-dramatic"))

    def test_ordinary_colon_not_flagged(self):
        self.assertFalse(has_label("Note: install the dependencies first.",
                                   "colon-dramatic"))

    def test_negative_listing_run(self):
        self.assertTrue(has_label("Not a tool. Not a platform. A movement.",
                                  "negative-listing"))

    def test_single_negative_not_flagged(self):
        self.assertFalse(has_label("Not a bad outcome, all things considered.",
                                   "negative-listing"))

    def test_tailing_negation_run(self):
        self.assertTrue(has_label("No guessing. No wasted motion. It just ships.",
                                  "tailing-negation"))

    def test_aphorism_formula(self):
        self.assertTrue(has_label("Trust is the currency of leadership.", "aphorism"))
        self.assertTrue(has_label("Feedback is the lifeblood of any team.", "aphorism"))

    def test_literal_currency_not_flagged(self):
        self.assertFalse(has_label("The euro is the currency in Spain and France.",
                                   "aphorism"))

    def test_emoji_heading(self):
        self.assertTrue(has_label("## 🚀 Launch plan\n\nBody text here.",
                                  "emoji in heading"))

    def test_plain_heading_not_flagged(self):
        self.assertFalse(has_label("## Launch plan\n\nBody text here.",
                                   "emoji in heading"))


class TestEmDashGating(unittest.TestCase):
    BASE = "Here are some ordinary filler words to pad the draft out. " * 3

    def test_closed_emdash_p1(self):
        text = self.BASE + "It works—mostly—and the team—wisely—shipped it."
        _, findings = run(text)
        self.assertTrue(any("closed" in f.label and f.severity == "P1" for f in findings))

    def test_spaced_emdash_only_p2(self):
        text = self.BASE + "It works — mostly — and the team — wisely — shipped it."
        _, findings = run(text)
        self.assertFalse(any("closed" in f.label for f in findings))
        self.assertTrue(any("em-dash over-use (total)" in f.label and f.severity == "P2"
                            for f in findings))

    def test_few_emdashes_pass(self):
        text = ("word " * 999) + "one em-dash — spaced."
        _, findings = run(text)
        self.assertFalse(any("em-dash" in f.label for f in findings))


class TestAnaphora(unittest.TestCase):
    def test_triple_repeat_flags(self):
        text = ("Momentum builds slowly over months. Momentum compounds when you show up. "
                "Momentum dies the week you stop.")
        self.assertTrue(has_label(text, "anaphora"))

    def test_stopword_openers_exempt(self):
        text = "The cat sat down. The dog ran off. The bird flew away."
        self.assertFalse(has_label(text, "anaphora"))

    def test_two_repeats_exempt(self):
        text = "Momentum builds slowly here. Momentum compounds quickly. Then it stops."
        self.assertFalse(has_label(text, "anaphora"))


class TestRegressions(unittest.TestCase):
    def test_existing_tier1_still_flags(self):
        self.assertTrue(has_label("We delve into the details.", "delve"))

    def test_title_case_heading_flags(self):
        self.assertTrue(has_label("## Reclaim Your Focus Time\n\nBody text.",
                                  "title-case heading"))

    def test_sentence_case_heading_not_flagged(self):
        # regression: global re.I used to make [A-Z] match lowercase, flagging
        # every 3+-word heading regardless of case
        self.assertFalse(has_label("## Why async wins for teams\n\nBody text.",
                                   "title-case heading"))

    def test_escape_hatch_still_strips_quotes(self):
        quoted = 'The report said "we leverage robust seamless synergy every day" verbatim.'
        self.assertFalse(has_label(quoted, "leverage"))

    def test_clean_text_passes(self):
        _, findings = run("The build failed twice on Tuesday. Sam fixed the flaky "
                          "test and wrote up what broke.")
        self.assertEqual([f for f in findings if f.severity in ("P0", "P1")], [])


if __name__ == "__main__":
    unittest.main()
