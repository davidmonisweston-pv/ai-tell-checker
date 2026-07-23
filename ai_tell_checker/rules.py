"""Default AI-writing-tell ruleset.

Every entry is a regex (case-insensitive) plus a short label. Organised into
the same shape a Profile can override:

- MECHANICAL: near-zero-false-positive fingerprints (chat-tool leakage,
  cutoff disclaimers, unfilled placeholders, unsourced attribution). Flagged
  regardless of author, always P0.
- TIER1: words that are fine in isolation but disproportionately common in
  LLM output. Flagged on sight by default (P1); a Profile may move any of
  these to `soft` (rate-gated) or `allow` (never flagged) if the author is
  verified to use them.
- TIER2: legitimate words individually; flagged only when 2+ distinct TIER2
  words land in the same paragraph (P1).
- TIER3_WORDS / TIER3_PHRASES: normal vocabulary, flagged only by density —
  TIER3_WORDS at >=3% of total words, TIER3_PHRASES when the same phrase
  recurs 2+ times or 3+ distinct phrases appear across the piece (P2).
- STRUCTURAL: regex patterns for sentence/paragraph-level AI shapes (P1
  unless noted).
"""

MECHANICAL = [
    (r"\b(i hope this helps|great question!|certainly!|feel free to reach out|"
     r"let me know if you need anything else|as an ai( language model)?)\b",
     "chatbot artifact"),
    (r"\bas of my last (update|training)\b|\bi don'?t have access to real-time\b|"
     r"\bwhile specific details are limited\b",
     "cutoff disclaimer"),
    (r"citeturn\d+search\d+|contentReference\[oaicite:\d+\]|oai_citation|"
     r"\[attached_file:\d+\]|grok_card",
     "chatbot citation-markup leak"),
    (r"utm_source=(chatgpt|copilot|openai|claude)\S*|referrer=grok\.com",
     "AI-tool URL tracking parameter"),
    (r"\[(?:Your|Insert|Add|Enter|Describe|Specify|Choose)[^\]]{0,60}\]|"
     r"\b\d{4}-XX-XX\b",
     "unfilled placeholder"),
    # Suppression (any digit, URL, "et al", parenthetical cite, or backtick in
    # the same sentence) lives in checker.has_concrete_evidence, not here.
    (r"\b(experts (believe|agree)|studies show|research suggests|"
     r"research indicates|industry leaders agree)\b",
     "vague attribution (no source in-sentence)"),
    (r"\b(let'?s think step by step|breaking this down|to approach this systematically|"
     r"here'?s my thought process|working through this logically)\b",
     "reasoning-chain artifact"),
    (r"\byou'?re absolutely right\b|\bthat'?s an excellent (point|question)\b|"
     r"\bwhat a great question\b",
     "sycophantic chatbot artifact"),
    (r"Co-Authored-By:\s*(Claude|ChatGPT|GPT|Copilot|Cursor|Gemini)|"
     r"Generated with \[?(Claude Code|ChatGPT|Copilot)|🤖 Generated with",
     "AI-tool attribution leak"),
    # Speculative gap-filling around an unknown subject — suppressed in the
    # checker when concrete evidence (digit, URL, citation) shares the sentence.
    (r"\bit is believed that\b|\bwidely (regarded|considered|believed)\b|"
     r"\bmaintains a low profile\b|\bprefers to stay out of the spotlight\b",
     "speculative gap-filler"),
]

TIER1 = [
    (r"\bdelv(e|es|ed|ing)\b", "delve"),
    (r"\btapestr(y|ies)\b", "tapestry"),
    (r"\brealm\b", "realm"),
    (r"\bparadigm\b", "paradigm"),
    (r"\bembark(s|ed|ing)?\b", "embark"),
    (r"\btestament to\b", "testament to"),
    (r"\brobust\w*\b", "robust"),
    (r"\bcomprehensive\w*\b", "comprehensive"),
    (r"\bcutting[- ]edge\b", "cutting-edge"),
    (r"\bleverag(e|es|ed|ing)\b", "leverage"),
    (r"\bpivotal\b", "pivotal"),
    (r"\bunderscore[sd]?\b", "underscore"),
    (r"\bmeticulous(ly)?\b", "meticulous"),
    (r"\bseamless\w*\b", "seamless"),
    (r"\bgame[- ]?chang\w+\b", "game-changer"),
    (r"\butiliz(e|es|ed|ing|ation)\b", "utilize"),
    (r"\bnestled\b", "nestled"),
    (r"\bvibrant\b", "vibrant"),
    (r"\bthriving\b", "thriving"),
    (r"\bshowcas\w+\b", "showcasing"),
    (r"\b(deep dive|dive into)\b", "deep dive"),
    (r"\bunpack(ing)?\b", "unpack"),
    (r"\bintricac(y|ies)\b|\bintricate\b", "intricate/intricacies"),
    (r"\bholistic(ally)?\b", "holistic"),
    (r"\bactionable\b", "actionable"),
    (r"\bimpactful\b", "impactful"),
    (r"\blearnings\b", "learnings"),
    (r"\bbest practices\b", "best practices"),
    (r"\bat its core\b", "at its core"),
    (r"\bsynerg(y|ies)\b", "synergy"),
    (r"\binterplay\b", "interplay"),
    (r"\bin order to\b", "in order to"),
    (r"\bdue to the fact that\b", "due to the fact that"),
    (r"\b(?:serves?|stands?) as\b", "serves as / stands as"),
    (r"\bboasts?\b", "boasts"),
    # Claude-signature metaphor ("load-bearing assumption/claim/test/invariant").
    # Hyphen required; literal construction nouns are carved out.
    (r"\bload-bearing\b(?!\s+(?:walls?|beams?|columns?|structures?|members?|"
     r"capacity|elements?|joists?))",
     "load-bearing (Claude metaphor)"),
    (r"\bbeacon\b", "beacon"),
    (r"\bwatershed moment\b", "watershed moment"),
    (r"\bever[- ]evolving\b", "ever-evolving"),
    (r"\bthought leader(s|ship)?\b", "thought leader"),
    (r"\bgenuinely\b|\bgenuine\b", "genuinely/genuine (intensifier)"),
    (r"\bmoreover\b", "moreover"),
    (r"\bfurthermore\b", "furthermore"),
    (r"\bnot only\b[^.?!]{0,70}\bbut also\b", "not only… but also"),
]

TIER2 = [
    (r"\bharness(es|ed|ing)?\b", "harness"),
    (r"\bnavigat\w*\b", "navigate"),
    (r"\bfoster(s|ed|ing)?\b", "foster"),
    (r"\belevat(e|es|ed|ing)\b", "elevate"),
    (r"\bunleash\w*\b", "unleash"),
    (r"\bstreamlin\w*\b", "streamline"),
    (r"\bempower\w*\b", "empower"),
    (r"\bbolster(s|ed|ing)?\b", "bolster"),
    (r"\bspearhead\w*\b", "spearhead"),
    (r"\bresonat\w*\b", "resonate"),
    (r"\brevolutioniz\w*\b", "revolutionize"),
    (r"\bfacilitat\w*\b", "facilitate"),
    (r"\bunderpin\w*\b", "underpin"),
    (r"\bnuanced?\b", "nuanced"),
    (r"\bcrucial(ly)?\b", "crucial"),
    (r"\bmultifaceted\b", "multifaceted"),
    (r"\becosystem\b", "ecosystem"),
    (r"\bmyriad\b", "myriad"),
    (r"\bplethora\b", "plethora"),
    (r"\bencompass\w*\b", "encompass"),
    (r"\bcatalyz\w*\b", "catalyze"),
    (r"\breimagin\w*\b", "reimagine"),
    (r"\bcultivat\w*\b", "cultivate"),
    (r"\btransformative\b|\btransformation\b", "transformative"),
    (r"\bcornerstone\b", "cornerstone"),
    (r"\bparamount\b", "paramount"),
    (r"\bpoised\b", "poised"),
    (r"\bburgeoning\b", "burgeoning"),
    (r"\bnascent\b", "nascent"),
    (r"\boverarching\b", "overarching"),
    (r"\bcommenc(e|es|ed|ing)\b", "commence"),
    (r"\bascertain\w*\b", "ascertain"),
    (r"\bendeavou?r\w*\b", "endeavor"),
    (r"\bembrac(e|es|ed|ing)\b", "embrace"),
    (r"\bgalvani[zs]\w+\b", "galvanize"),
    (r"\billuminat\w+\b", "illuminate"),
    (r"\bquintessential(ly)?\b", "quintessential"),
    (r"\bsymphony of\b", "a symphony of"),
]

TIER3_WORDS = [
    r"\bsignificant(ly)?\b", r"\binnovat\w+\b", r"\beffective(ly)?\b",
    r"\bdynamic(s)?\b", r"\bcompelling\b", r"\bunprecedented\b",
    r"\bexceptional(ly)?\b", r"\bremarkabl\w+\b", r"\bsophisticated\b",
    r"\binstrumental\b", r"\bworld[- ]class\b", r"\bstate[- ]of[- ]the[- ]art\b",
]

TIER3_PHRASES = [
    (r"\bthe intersection of\b", "the intersection of X and Y"),
    (r"\bcommunity[- ]driven\b", "community-driven"),
    (r"\blong[- ]term sustainability\b", "long-term sustainability"),
    (r"\buser engagement\b", "user engagement"),
    (r"\bemerging (sector|space|category)\b", "emerging sector/space"),
]

STRUCTURAL = [
    (r"\bit'?s not( just)?\b[^.?!]{0,70}\bit'?s\b", "antithesis (\"it's not X — it's Y\")"),
    (r"\bthis isn'?t about\b[^.?!]{0,70},\s*it'?s about\b", "antithesis (\"this isn't about X, it's about Y\")"),
    (r"\b(is|are)n'?t just\b[^.?!]{0,70}\b(it'?s|they'?re)\b",
     "antithesis (\"isn't just X — it's Y\")"),
    (r"\bis,? (itself|in itself),? (the|an?)\b", "\"X is itself the Y\" emphasis tic"),
    (r"\bis the real (point|story|question|issue|prize|test|lesson|win|work)\b",
     "\"X is the real Y\" emphasis tic"),
    (r"\b(could|may|might|will)\s+(potentially|eventually|ultimately)\b", "hedge-stacked prediction"),
    (r"^\s*let'?s\s+\w+", "\"let's\" transition opener"),
    (r"^\s*[-*]\s*\*\*[^:*\n]{2,50}\.\*\*\s", "list-label period (use a colon)"),
    # (?-i: …) keeps this case-sensitive even though scan_structural passes re.I —
    # without it every 3+-word heading matches, sentence case included.
    (r"^(?-i:#{1,6}\s+(?:[A-Z][a-z']*\s+){2,}[A-Z][a-z']*)\s*$", "title-case heading"),
    (r"\b\w+,\s+\w+,?\s+and\s+\w+\b", "rule-of-three triad"),
    (r"\b(may|could|will|is poised to)\s+become\s+(one of the most|the most)\s+\w+\s+"
     r"(narrative|story|trend|theme|chapter|movement|force)", "generic future-narrative closer"),
    (r"\bthis one'?s? (is )?(a must[- ]read|worth your time)\b|\bdon'?t sleep on this\b|"
     r"\bbookmark this\b|\btrust me,? you'?ll want to read this\b",
     "social endorsement closer"),
    (r"\bin today'?s\s+(fast-paced|digital|rapidly|ever-)", "\"in today's fast-paced …\" opener"),
    (r"\bit'?s important to note\b", "\"it's important to note\""),
    (r"\bin conclusion\b|\bto summarize\b|\bin summary\b", "\"in conclusion\" wrap-up"),
    (r"\bat the end of the day\b", "\"at the end of the day\""),
    (r"\bwhen it comes to\b", "\"when it comes to\""),
    (r"\bthat (being )?said\b", "\"that said\""),
    (r"\bplays?\s+an?\s+(vital|key|crucial|pivotal|significant)\s+role\b", "\"plays a … role\""),
    (r"\b(here'?s the (thing|truth|reality)[:,]|let me be clear\b|"
     r"the uncomfortable (truth|reality) is\b|make no mistake\b)",
     "throat-clearing opener"),
    # "Full stop." / "Period." only as standalone sentences; the others anywhere.
    (r"(?:^|[.!?…]\s+)(full stop\.|period\.)|\blet that sink in\b|\bread that again\b",
     "emphasis crutch (\"Full stop.\" / \"Let that sink in\")"),
    # Portentous lead-in + colon + short no-comma payoff ("The best part: it learns.").
    # The lead-in whitelist is the false-positive guard — a plain "Note:" never fires.
    (r"(?:^|[.!?]\s+)the (truth|best part|kicker|catch|result|reality|good news|bad news|"
     r"real (problem|question|story))(\s+(is|was))?:\s+\S+(\s+\S+){0,4}[.!?]",
     "colon-dramatic reveal"),
    # Cluster-gated: a single "Not X." fragment is normal writing; 2+ consecutive is the tell.
    (r"(?:\bnot (a|an|the|just|because)\b[^.?!\n]{1,40}[.?!]\s+){2,}",
     "negative-listing run (\"Not X. Not Y.\")"),
    (r"(?:\bno \w[^.?!,\n]{0,30}\.\s+){2,}",
     "tailing-negation run (\"No X. No Y.\")"),
    (r"\bthe (currency|lifeblood|connective tissue|dna|heartbeat|beating heart) of\b",
     "aphorism formula (\"the lifeblood of\")"),
    (r"^#{1,6}\s+[^\n]*[☀-➿⬀-⯿\U0001F000-\U0001FAFF]",
     "emoji in heading"),
]

US_SPELLINGS = [
    r"\borganiz", r"\bcolor\b", r"\bcolors\b", r"\bbehavior", r"\bfavor\b",
    r"\bcenter\b", r"\bcenters\b", r"\banaly[z]", r"\bdefense\b", r"\bprogram\b",
    r"\bfulfill\b", r"\bmath\b",
]
