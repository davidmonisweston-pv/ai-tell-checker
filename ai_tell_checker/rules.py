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
    (r"\b(experts (believe|agree)|studies show|research suggests|"
     r"industry leaders agree)\b(?![^.?!]{0,60}\([A-Z][a-zA-Z.&]+,?\s*\d{4})",
     "vague attribution (no source in-sentence)"),
    (r"\b(let'?s think step by step|breaking this down|to approach this systematically|"
     r"here'?s my thought process|working through this logically)\b",
     "reasoning-chain artifact"),
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
    (r"\bserves? as\b", "serves as"),
    (r"\bboasts?\b", "boasts"),
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
    (r"\b(could|may|might|will)\s+(potentially|eventually|ultimately)\b", "hedge-stacked prediction"),
    (r"^\s*let'?s\s+\w+", "\"let's\" transition opener"),
    (r"^\s*[-*]\s*\*\*[^:*\n]{2,50}\.\*\*\s", "list-label period (use a colon)"),
    (r"^#{1,6}\s+([A-Z][a-z']*\s+){2,}[A-Z][a-z']*\s*$", "title-case heading"),
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
]

US_SPELLINGS = [
    r"\borganiz", r"\bcolor\b", r"\bcolors\b", r"\bbehavior", r"\bfavor\b",
    r"\bcenter\b", r"\bcenters\b", r"\banaly[z]", r"\bdefense\b", r"\bprogram\b",
    r"\bfulfill\b", r"\bmath\b",
]
