"""Core detection engine. Stdlib only — no LLM in the loop.

`run(text, profile=None, quick=False)` is the main entry point: it strips
code/quoted spans (escape hatch), computes stylometric metrics, scans the
default ruleset (or a Profile-adjusted version of it), and returns
(metrics_dict, [Finding, ...]) with each finding tagged P0/P1/P2.
"""
import re
import statistics
from dataclasses import dataclass
from typing import Optional

from . import rules

# Generic default hedge/booster words, used only when no Profile supplies its own.
DEFAULT_HEDGES = ["may ", "might ", "could ", "would ", "often", "typically",
                   "broadly", "relatively", "perhaps", "tend", "appears",
                   "seems", "suggests", "likely", "fairly", "potential"]
DEFAULT_BOOSTERS = ["significant", "crucial", " key ", "vital", "clearly",
                     "essential", "transform", "hugely", "truly", "powerful",
                     "critical", "remarkable"]

TIER3_DENSITY_MIN = 0.03          # tier-3 words as a fraction of total words
TIER3_PHRASE_REPEAT_MIN = 2       # same tier-3 phrase repeated this many times
TIER3_PHRASE_CLUSTER_MIN = 3      # distinct tier-3 phrases anywhere in the piece
TIER2_CLUSTER_MIN = 2             # distinct tier-2 words in one paragraph
RULE_OF_THREE_PER1K_MAX = 1.0     # triads are fine occasionally; flag only if they recur
TTR_MIN = 0.40                    # below this on 200+ words is worth a second look
TTR_MIN_WORDS = 200
EMDASH_PER1K_DEFAULT_MAX = 1.0    # cap on CLOSED em-dashes (word—word); total gets 2×
ANAPHORA_RUN_MIN = 3              # consecutive sentences opening on the same word

# Zero-width / bidi codepoints. Legitimate prose never contains these; their
# presence is a detector-bypass or copy-paste fingerprint. A leading BOM is
# exempted (editor artifact), as is ZWJ inside an emoji sequence.
HIDDEN_UNICODE = {
    "\u200b": "zero-width space",
    "\u200c": "zero-width non-joiner",
    "\u200d": "zero-width joiner",
    "\u2060": "word joiner",
    "\ufeff": "zero-width no-break space (BOM)",
    "\u00ad": "soft hyphen",
    "\u202a": "bidi control (LRE)",
    "\u202b": "bidi control (RLE)",
    "\u202c": "bidi control (PDF)",
    "\u202d": "bidi control (LRO)",
    "\u202e": "bidi control (RLO)",
    "\u2066": "bidi isolate (LRI)",
    "\u2067": "bidi isolate (RLI)",
    "\u2068": "bidi isolate (FSI)",
    "\u2069": "bidi isolate (PDI)",
}

# Common sentence openers whose repetition is ordinary structure, not anaphora
# (slopless gates its triple-repeat rule the same way, after a human-corpus audit).
ANAPHORA_STOPWORDS = {
    "the", "a", "an", "it", "its", "this", "that", "these", "those", "there",
    "i", "we", "you", "he", "she", "they", "and", "but", "or", "so", "if",
    "in", "on", "at", "for", "to", "as", "when", "while", "after", "before",
    "one", "two", "three", "first", "second", "third", "next", "then",
    "chapter", "step", "note", "example", "figure", "table",
}


@dataclass
class Finding:
    severity: str    # "P0" | "P1" | "P2"
    category: str
    label: str
    detail: str       # snippet or occurrence count, human-readable


def strip_escaped(text: str) -> str:
    """Remove fenced code, inline code, blockquotes, and long verbatim quotes
    before tell-scanning — the 'self-reference escape hatch': a document that
    quotes bad writing as an example, or a report that quotes a source
    verbatim, should not be flagged for it."""
    t = re.sub(r"```.*?```", "", text, flags=re.S)
    t = re.sub(r"`[^`\n]+`", "", t)
    t = "\n".join(line for line in t.split("\n") if not line.lstrip().startswith(">"))
    t = re.sub(r'"[^"\n]{20,}?"', "", t)
    t = re.sub(r"“[^”\n]{20,}?”", "", t)
    return t


def clean(text: str) -> str:
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"[*_`#>]", "", t)
    return t


def _syllables(w: str) -> int:
    w = w.lower()
    vowels = "aeiouy"
    n = 0
    prev = False
    for c in w:
        if c in vowels and not prev:
            n += 1
        prev = c in vowels
    if w.endswith("e"):
        n = max(1, n - 1)
    return max(1, n)


def metrics(text: str, hedges=None, boosters=None) -> dict:
    hedges = hedges or DEFAULT_HEDGES
    boosters = boosters or DEFAULT_BOOSTERS
    t = clean(text)
    words = re.findall(r"[A-Za-z][A-Za-z'\-]*", t)
    sents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", t.replace("\n", " "))
             if len(s.split()) > 1]
    sl = [len(s.split()) for s in sents] or [0]
    nw = max(1, len(words))
    ns = max(1, len(sents))
    per1k = lambda c: round(1000 * c / nw, 1)
    tl = t.lower()
    cnt = lambda ws: sum(tl.count(w) for w in ws)
    syll = sum(_syllables(w) for w in words)
    flesch = 206.835 - 1.015 * (nw / ns) - 84.6 * (syll / nw)
    hed, boo = cnt(hedges), cnt(boosters)
    ttr = round(len(set(w.lower() for w in words)) / nw, 3)
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    para_lens = [len(re.findall(r"[A-Za-z']+", p)) for p in paragraphs] or [0]
    return dict(
        words=nw, sentences=ns, paragraphs=len(paragraphs),
        sent_mean=statistics.mean(sl),
        sent_sd=statistics.pstdev(sl) if len(sl) > 1 else 0.0,
        sent_max=max(sl),
        pct_short=sum(x < 12 for x in sl) / ns,
        pct_long=sum(x > 30 for x in sl) / ns,
        emdash_per1k=per1k(t.count("—")), endash_per1k=per1k(t.count("–")),
        emdash_closed_per1k=per1k(len(re.findall(r"\w—\w", t))),
        semicolon_per1k=per1k(t.count(";")), paren_per1k=per1k(t.count("(")),
        flesch=flesch, hedge_booster=(hed / boo if boo else float("inf")),
        hedges=hed, boosters=boo, ttr=ttr,
        para_len_mean=statistics.mean(para_lens),
        para_len_sd=statistics.pstdev(para_lens) if len(para_lens) > 1 else 0.0,
    )


def _flatten(text: str) -> str:
    """Collapse whitespace runs (incl. line wraps) to a single space, so a phrase
    that happens to word-wrap across a line break still matches. Line-anchored
    checks (headings, list labels) must use the unflattened text instead."""
    return re.sub(r"\s+", " ", text)


def _snippet(text, mo, pad=25):
    s = max(0, mo.start() - pad)
    return "…" + text[s:mo.end() + pad].replace("\n", " ").strip() + "…"


def _in_emoji_sequence(text: str, i: int) -> bool:
    """True when the char at i sits next to an emoji codepoint — a ZWJ inside
    a legitimate emoji sequence (👨‍👩‍👧) is not a hidden-unicode tell."""
    def is_emoji(c):
        cp = ord(c)
        return 0x1F000 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF or cp == 0xFE0F
    before = text[i - 1] if i > 0 else ""
    after = text[i + 1] if i + 1 < len(text) else ""
    return (before and is_emoji(before)) or (after and is_emoji(after))


def scan_hidden_unicode(text: str) -> list:
    """P0 scan for zero-width/bidi codepoints. Runs on the RAW input, before
    strip_escaped — these chars hide anywhere, including inside code spans."""
    if text.startswith("\ufeff"):          # leading BOM is an editor artifact
        text = text[1:]
    counts = {}
    for i, ch in enumerate(text):
        if ch in HIDDEN_UNICODE:
            if ch == "\u200d" and _in_emoji_sequence(text, i):
                continue
            counts[ch] = counts.get(ch, 0) + 1
    return [Finding("P0", "mechanical", f"hidden unicode: {HIDDEN_UNICODE[ch]}",
                    f"U+{ord(ch):04X} ×{n}")
            for ch, n in sorted(counts.items())]


# Signals that a shape-matched claim is anchored to something concrete: a digit,
# URL, "et al", a parenthetical citation, or inline code. Any of these in the
# same sentence suppresses the vague-attribution / gap-filler flag (slopless's
# concrete-evidence suppression, its single best false-positive guard).
_CONCRETE_EVIDENCE = re.compile(r"\d|https?://|\bet al\b|\([A-Z][^)]{1,60}\)|`")

# MECHANICAL labels the suppression applies to.
_SUPPRESSIBLE = {"vague attribution (no source in-sentence)", "speculative gap-filler"}


def has_concrete_evidence(span: str) -> bool:
    return bool(_CONCRETE_EVIDENCE.search(span))


def _sentence_around(text: str, start: int, end: int) -> str:
    """The sentence containing [start:end) of flattened text."""
    s = max(text.rfind(". ", 0, start), text.rfind("! ", 0, start),
            text.rfind("? ", 0, start)) + 1
    e_candidates = [text.find(p, end) for p in (". ", "! ", "? ")]
    e_candidates = [x for x in e_candidates if x != -1]
    e = min(e_candidates) + 1 if e_candidates else len(text)
    return text[s:e]


def scan_mechanical(text: str) -> list:
    out = []
    flat = _flatten(text)
    for pat, label in rules.MECHANICAL:
        if label in _SUPPRESSIBLE:
            mo = next((m for m in re.finditer(pat, flat, re.I | re.S)
                       if not has_concrete_evidence(_sentence_around(flat, m.start(), m.end()))),
                      None)
        else:
            mo = re.search(pat, flat, re.I | re.S)
        if mo:
            out.append(Finding("P0", "mechanical", label, _snippet(flat, mo)))
    return out


def scan_tier1(text: str, nwords: int, allow=None, soft=None, soft_rate_max=0.6) -> list:
    allow = allow or set()
    soft = soft or set()
    out = []
    flat = _flatten(text)
    for pat, label in rules.TIER1:
        if label in allow:
            continue
        matches = list(re.finditer(pat, flat, re.I))
        if not matches:
            continue
        if label in soft:
            rate = 1000 * len(matches) / max(1, nwords)
            if rate > soft_rate_max:
                out.append(Finding("P1", "tier1-soft", label, f"×{len(matches)} (rate {rate:.2f}/1k)"))
        else:
            out.append(Finding("P1", "tier1", label, _snippet(flat, matches[0])))
    return out


def scan_tier2_clusters(text: str) -> list:
    out = []
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    for para in paragraphs:
        flat_para = _flatten(para)
        hits = set()
        for pat, label in rules.TIER2:
            if re.search(pat, flat_para, re.I):
                hits.add(label)
        if len(hits) >= TIER2_CLUSTER_MIN:
            out.append(Finding("P1", "tier2-cluster", "+".join(sorted(hits)),
                                flat_para[:80].strip() + "…"))
    return out


def scan_tier3(text: str, nwords: int) -> list:
    out = []
    tl = _flatten(text).lower()
    total_hits = sum(len(re.findall(pat, tl)) for pat in rules.TIER3_WORDS)
    density = total_hits / max(1, nwords)
    if density >= TIER3_DENSITY_MIN:
        out.append(Finding("P2", "tier3-density", "tier-3 word density",
                            f"{density:.1%} of words (threshold {TIER3_DENSITY_MIN:.0%})"))
    distinct_phrases = set()
    for pat, label in rules.TIER3_PHRASES:
        n = len(re.findall(pat, tl))
        if n >= TIER3_PHRASE_REPEAT_MIN:
            out.append(Finding("P2", "tier3-phrase", label, f"×{n}"))
        if n:
            distinct_phrases.add(label)
    if len(distinct_phrases) >= TIER3_PHRASE_CLUSTER_MIN:
        out.append(Finding("P2", "tier3-phrase-cluster", "boilerplate phrase cluster",
                            f"{len(distinct_phrases)} distinct phrases: {', '.join(sorted(distinct_phrases))}"))
    return out


def scan_structural(text: str, nwords: int) -> list:
    """Line-anchored patterns (heading/list-label shape) scan the original text
    with re.M; everything else scans flattened text so a phrase that word-wraps
    across a line break still matches."""
    out = []
    flat = _flatten(text)
    for pat, label in rules.STRUCTURAL:
        line_anchored = pat.startswith("^")
        haystack = text if line_anchored else flat
        matches = list(re.finditer(pat, haystack, re.I | re.M | re.S))
        if not matches:
            continue
        if label == "rule-of-three triad":
            rate = 1000 * len(matches) / max(1, nwords)
            if rate > RULE_OF_THREE_PER1K_MAX:
                out.append(Finding("P2", "structural", label, f"×{len(matches)} (rate {rate:.2f}/1k)"))
        else:
            out.append(Finding("P1", "structural", label, _snippet(haystack, matches[0])))
    return out


def scan_anaphora(text: str) -> list:
    """3+ consecutive sentences opening on the same word (triple-repeat
    anaphora). Gated against ANAPHORA_STOPWORDS and digit openers, because
    repeated function-word or enumerator openers are ordinary structure. P2 —
    anaphora is also a deliberate human rhetorical device."""
    flat = _flatten(clean(text))
    sents = [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", flat) if len(s.split()) > 1]
    out = []
    run_word, run_len = None, 0
    for s in sents + [""]:            # sentinel flushes the final run
        mo = re.match(r"[A-Za-z']+", s)
        w = mo.group(0).lower() if mo else None
        if w is not None and w == run_word:
            run_len += 1
        else:
            if (run_word and run_len >= ANAPHORA_RUN_MIN
                    and run_word not in ANAPHORA_STOPWORDS and not run_word.isdigit()):
                out.append(Finding("P2", "structural", "repeated sentence openers (anaphora)",
                                   f"\"{run_word.capitalize()} …\" ×{run_len} consecutive"))
            run_word, run_len = w, 1
    return out


def scan_stylometrics(m: dict) -> list:
    out = []
    if m["words"] >= TTR_MIN_WORDS and m["ttr"] < TTR_MIN:
        out.append(Finding("P2", "stylometric", "low vocabulary diversity (TTR)",
                            f"{m['ttr']:.2f} (warn below {TTR_MIN})"))
    return out


def scan_spelling(text: str, patterns=None) -> list:
    patterns = patterns or rules.US_SPELLINGS
    hits = sorted({mo.group(0) for pat in patterns for mo in re.finditer(pat, text, re.I)})
    return [Finding("P2", "spelling", "possible US spelling", w) for w in hits]


def run(text: str, profile=None, quick: bool = False):
    """Returns (metrics: dict, findings: list[Finding]).

    profile: optional voice_calibration.Profile — supplies register ranges,
    hedge/booster words, em-dash cap, and tier1 allow/soft overrides. Without
    one, only the generic mechanical/structural/tier checks run (no register
    range checks, since those are author-specific by construction).
    """
    scan_text = strip_escaped(text)
    hedges = profile.hedges if profile else None
    boosters = profile.boosters if profile else None
    m = metrics(scan_text, hedges=hedges, boosters=boosters)

    findings = scan_hidden_unicode(text)   # raw text: these chars hide anywhere
    findings += scan_mechanical(scan_text)
    allow = profile.tier1_allow if profile else None
    soft = profile.tier1_soft if profile else None
    soft_rate = profile.soft_rate_per1k_max if profile else 0.6
    findings += scan_tier1(scan_text, m["words"], allow=allow, soft=soft, soft_rate_max=soft_rate)
    findings += scan_structural(scan_text, m["words"])

    # Closed em-dashes (word—word) are the AI signature; spaced ones are a normal
    # human habit. P1 gates on the closed rate; the total rate only warns at 2×.
    emdash_max = profile.emdash_per1k_max if profile else EMDASH_PER1K_DEFAULT_MAX
    if m["emdash_closed_per1k"] > emdash_max:
        findings.append(Finding("P1", "structural", "em-dash over-use (closed, word—word)",
                                 f"{m['emdash_closed_per1k']}/1k (cap {emdash_max}/1k)"))
    elif m["emdash_per1k"] > 2 * emdash_max:
        findings.append(Finding("P2", "structural", "em-dash over-use (total)",
                                 f"{m['emdash_per1k']}/1k (cap {2 * emdash_max}/1k)"))

    if not quick:
        findings += scan_tier2_clusters(scan_text)
        findings += scan_tier3(scan_text, m["words"])
        findings += scan_anaphora(scan_text)
        findings += scan_stylometrics(m)
        if m["paragraphs"] >= 4 and m["para_len_sd"] < m["para_len_mean"] * 0.15:
            findings.append(Finding("P2", "stylometric", "uniform paragraph length",
                                     f"sd {m['para_len_sd']:.1f} vs mean {m['para_len_mean']:.1f}"))
        us_patterns = profile.us_spellings if profile else None
        findings += scan_spelling(scan_text, patterns=us_patterns)

    if profile:
        findings += profile.check_ranges(m)
        flat_scan_text = _flatten(scan_text)
        for pat, label in getattr(profile, "hard_tell_patterns", lambda: [])():
            mo = re.search(pat, flat_scan_text, re.I | re.S)
            if mo:
                findings.append(Finding("P1", "profile-hard-tell", label, _snippet(flat_scan_text, mo)))

    return m, findings
