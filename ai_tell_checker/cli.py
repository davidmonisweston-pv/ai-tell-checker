#!/usr/bin/env python3
"""CLI for the generic checker (no author profile — use voice_calibration.validate
for a profile-aware, register-checked run).

Usage:
    python3 -m ai_tell_checker <draft.txt> [--quick] [--json]

Exit code 0 if no P0/P1 findings, 1 otherwise (P2-only findings do not fail the gate).
"""
import argparse
import json
import sys

from .checker import run


def main(argv=None):
    ap = argparse.ArgumentParser(description="Scan a draft for AI-writing tells.")
    ap.add_argument("file")
    ap.add_argument("--quick", action="store_true", help="P0+P1 checks only (skip tier-3/stylometric)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    text = open(args.file, encoding="utf-8", errors="ignore").read()
    m, findings = run(text, profile=None, quick=args.quick)
    p0 = [f for f in findings if f.severity == "P0"]
    p1 = [f for f in findings if f.severity == "P1"]
    p2 = [f for f in findings if f.severity == "P2"]

    if args.json:
        print(json.dumps(dict(
            metrics=m,
            findings=[dict(severity=f.severity, category=f.category, label=f.label, detail=f.detail)
                      for f in findings],
        ), indent=2, default=str))
    else:
        print(f"AI-tell scan — {m['words']} words, {m['sentences']} sentences, TTR {m['ttr']:.2f}\n")
        for tier, items in (("P0 (credibility killers)", p0), ("P1 (obvious AI smell)", p1),
                             ("P2 (stylistic polish)", p2)):
            if not items:
                continue
            print(f"  {tier}:")
            for f in items:
                print(f"    [{f.category}] {f.label} — {f.detail}")
            print()
        if not findings:
            print("  No tells found.\n")
        verdict = "PASS" if not (p0 or p1) else f"FAIL — {len(p0)} P0, {len(p1)} P1 finding(s)"
        print(f"  VERDICT: {verdict}")

    sys.exit(0 if not (p0 or p1) else 1)


if __name__ == "__main__":
    main()
