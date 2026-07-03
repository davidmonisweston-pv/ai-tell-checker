"""ai_tell_checker — deterministic, stdlib-only detector for AI-writing tells.

Author-agnostic by design: ships a generic default ruleset (mechanical
fingerprints, tiered vocabulary, structural regexes, stylometric metrics) and
accepts an optional Profile (see the sibling `voice_calibration` package) to
adapt register ranges and reclassify individual tells as allowed/soft for a
specific writer's verified usage.

No third-party dependencies, no LLM in the loop — every number is computed by
Python so results are reproducible and auditable.
"""
from .checker import Finding, metrics, run, strip_escaped

__all__ = ["Finding", "metrics", "run", "strip_escaped"]
__version__ = "1.0.0"
