# AI-Tell Reference

A reference catalogue of the tells that give away AI-generated writing, with
suggested fixes. It is a knowledge base, not a set of instructions: a custom GPT
retrieves from it when spotting and fixing AI tells in a draft. The catalogue is
adapted from a deterministic detector, so it is meant to be applied
consistently — the same passage should earn the same flags every time.

The catalogue covers both the shared AI signature and the habits specific to
each model family: the Claude-flavoured tells (over-hedging, "it's not X, it's
Y" antithesis, tidy triads) and the ChatGPT-flavoured tells (see the dedicated
ChatGPT section under P1). The categories overlap heavily in practice, and a
strong draft passes every one regardless of which tool produced it.

> **Using this file.** Pair it with a short Instructions block in the GPT's
> setup — a suggested block is at the end of this document under
> "Suggested GPT instructions". The Instructions tell the GPT *what to do*; this
> knowledge file is *what it looks things up in*.

---

## Severity tiers

Each tell carries a severity, which governs whether a draft passes:

- **P0 — Mechanical.** Machine fingerprints with a near-zero false-positive
  rate. Any P0 means the draft fails.
- **P1 — High-signal.** Over-used vocabulary and structural habits. Any P1 means
  the draft fails.
- **P2 — Advisory.** Density and stylometric signals worth a second look, but not
  disqualifying on their own.

A clean draft has zero P0 and zero P1 findings.

## Escape hatch — what is never a tell

These spans are excluded before any scan, because a document that *quotes* bad
writing as an example, or cites a source verbatim, should not be penalized for
the quoted words. Only the author's own prose is judged.

- fenced code blocks and inline `code`
- blockquotes (lines beginning with `>`)
- any long verbatim quotation (roughly 20+ characters inside quote marks)

---

## P0 — Mechanical tells (near-zero false-positive; always fail)

Machine fingerprints. Each can be deleted or replaced without a judgment call.

- **Chatbot artifacts:** "I hope this helps", "Great question!", "Certainly!",
  "feel free to reach out", "let me know if you need anything else",
  "as an AI (language model)". → Delete outright.
- **Cutoff disclaimers:** "as of my last update/training", "I don't have access
  to real-time…", "while specific details are limited". → Delete, or replace
  with a real, dated fact.
- **Chat-tool citation-markup leaks:** `citeturn0search0`,
  `contentReference[oaicite:1]`, `oai_citation`, `[attached_file:2]`,
  `grok_card`, and similar. → Delete; these are copy-paste residue.
- **AI-tool URL tracking parameters:** `utm_source=chatgpt` (or `copilot`,
  `openai`, `claude`), `referrer=grok.com`. → Strip the parameter from the URL.
- **Unfilled placeholders:** `[Your Name]`, `[Insert date]`, `[Add company]`,
  `[Describe…]`, `2026-XX-XX`, and the like. → Fill in, or flag as missing input.
- **Vague attribution with no source:** "experts believe", "studies show",
  "research suggests", "industry leaders agree" — *when no citation follows in
  the same sentence*. → Name the source, or cut the claim. A missing source is
  never filled with an invented one.
- **Reasoning-chain artifacts:** "let's think step by step", "breaking this
  down", "to approach this systematically", "here's my thought process",
  "working through this logically". → Delete; the conclusion is stated directly.

---

## P1 — High-signal tells (fail the draft)

### Tier-1 vocabulary — a tell on sight
Fine once in a blue moon, but wildly over-represented in LLM output. Each
occurrence is a flag, and the fix is a plainer word.

delve · tapestry · realm · paradigm · embark · testament to · robust ·
comprehensive · cutting-edge · leverage · pivotal · underscore · meticulous ·
seamless · game-changer · utilize · nestled · vibrant · thriving · showcasing ·
deep dive / dive into · unpack · intricate / intricacies · holistic ·
actionable · impactful · learnings · best practices · at its core · synergy ·
interplay · in order to · due to the fact that · serves as · boasts ·
genuinely / genuine (as an intensifier) · moreover · furthermore ·
"not only … but also"

Typical fixes: *utilize → use · leverage → use · in order to → to · due to the
fact that → because · underscore → show · robust → strong/reliable · showcase →
show · delve into → look at · a testament to → shows.*

### Structural tells — a tell on sight
- **Antithesis:** "It's not X — it's Y" / "This isn't about X, it's about Y."
  → The positive claim, made directly.
- **Hedge-stacked predictions:** "could potentially", "may eventually", "might
  ultimately", "will ultimately". → One word, or no hedge.
- **"Let's" transition openers** at the start of a line ("Let's dive in",
  "Let's explore"). → Cut; open on the substance.
- **List-label period:** a bullet that starts `**Bold label.**` with a period.
  → A colon, or the label folded into a sentence.
- **Title-Case Headings** where most words are capitalized. → Sentence case.
- **Generic future-narrative closer:** "may become one of the most important
  narratives/stories/trends…". → Cut, or a concrete claim.
- **Social-endorsement closer:** "this is a must-read", "don't sleep on this",
  "bookmark this", "trust me, you'll want to read this". → Delete.
- **"In today's fast-paced / digital / ever-changing…" opener.** → Cut; open on
  the actual topic.
- **"It's important to note"** → State the note.
- **"In conclusion" / "to summarize" / "in summary" wrap-up.** → End on the
  point itself.
- **Filler connectives:** "at the end of the day", "when it comes to", "that
  (being) said". → Cut, or a precise transition.
- **"Plays a vital/key/crucial/pivotal/significant role"** → What it actually does.
- **Em-dash over-use:** more than ~1 em-dash (—) per 1000 words is a tell. →
  Some converted to commas, colons, or full stops.

### ChatGPT-signature tells — a tell on sight
The habits most strongly associated with ChatGPT/GPT-family output. They overlap
with the lists above, but ChatGPT reaches for them so relentlessly that their
presence — especially two or more together — is a reliable signature.

**Sentence-opener formulas** (a frame instead of the point):
- "It is important to note/understand/consider that…"
- "In today's world…" / "In today's fast-paced world…" / "In an era where…" /
  "In a world where…"
- "In the world of X…" / "In this digital world / digital age…"
- "Let's take a closer look at…" / "Let's dive deeper…"
- "Another important factor to consider is…"
→ Cut the frame; open on the substance.

**Stock explanatory phrases** (formulaic connective tissue between points):
- "plays a crucial role" / "plays a vital role"
- "highlights the importance of…" / "this underscores the need for…"
- "presents the key challenge…" / "that's why X is so important"
- "when it comes to…" / "with that being said" / "on the other hand" (as a
  reflexive pivot) / "as a result" (over-used)
→ The specific claim, or cut.

**Closers:** "In conclusion", "In summary", "In short", "Overall", "Ultimately"
as a wrap-up move. → End on the actual point.

**Filler adverbs / hedges ChatGPT leans on:** additionally · certainly · surely
· typically · generally · various · numerous · overall · essentially. A tell
when they recur; the fix is usually to cut them.

**Extra ChatGPT-favoured vocabulary** (treated like Tier-1 — a tell on sight):
kaleidoscope · landscape (as metaphor, "the X landscape") · vital · essential ·
complex · multifaceted · additionally · aforementioned · notably ·
significantly (as a sentence adverb).

**Punctuation habits:**
- **Em-dashes set tight** with no spaces (word—word) used repeatedly. Combined
  with the >1-per-1k rate cap above, tight repeated em-dashes are a strong tell.
  → Some converted to commas/colons/periods; any kept match the author's spacing.
- **Hyphenated compound adjectives everywhere**, including where they aren't
  needed ("state-of-the-art, results-driven, best-in-class"). → De-hyphenated or
  simplified.

**Sentiment & shape:**
- **Relentless positivity** — every item framed as exciting, powerful, or
  transformative, with no friction or trade-offs named. → Balance restored; the
  real limitations and costs named.
- **The five-paragraph skeleton** — intro → three evenly-weighted points → neat
  conclusion, with each section about the same length. → Symmetry broken; the
  structure follows the argument, not a template.

### Tier-2 vocabulary — a tell only in clusters
Legitimate individually. A paragraph is flagged **only when two or more distinct
Tier-2 words appear in it** — the cluster is the tell.

harness · navigate · foster · elevate · unleash · streamline · empower ·
bolster · spearhead · resonate · revolutionize · facilitate · underpin ·
nuanced · crucial · multifaceted · ecosystem · myriad · plethora · encompass ·
catalyze · reimagine · cultivate · transformative / transformation ·
cornerstone · paramount · poised · burgeoning · nascent · overarching

The fix for a tripped cluster: rewrite the paragraph to remove enough of these
words to break the cluster, favouring concrete verbs and nouns.

---

## P2 — Advisory tells (note, don't fail)

### Tier-3 vocabulary — a tell only by density
Normal words that only signal AI in bulk. Flagged as **"high Tier-3 density"**
only when these together make up **3% or more of total words**:

significant(ly) · innovat* · effective(ly) · dynamic(s) · compelling ·
unprecedented · exceptional(ly) · remarkable · sophisticated · instrumental ·
world-class · state-of-the-art

### Tier-3 boilerplate phrases — a tell by repetition
A phrase is flagged if it **repeats 2+ times**; a **"boilerplate cluster"** is
flagged when **3+ distinct** ones appear anywhere:

"the intersection of X and Y" · "community-driven" · "long-term sustainability"
· "user engagement" · "emerging sector/space/category"

### Rule-of-three triads — a tell only when they recur
The "X, Y, and Z" triad is fine occasionally. Flagged only when triads appear
**more than ~1 per 1000 words** — habitual triads are an AI cadence. The fix:
break some into pairs or single items.

### Stylometric signals
- **Low vocabulary diversity:** on drafts of 200+ words, a type-token ratio
  below 0.40 (unique words ÷ total words) suggests repetitive phrasing. → Vary
  word choice.
- **Uniform paragraph length:** on 4+ paragraphs, when every paragraph is nearly
  the same length (standard deviation under 15% of the mean), the text reads
  machine-blocked. → Vary paragraph length; let some be short.

### Spelling register (optional)
When a target register is known, mismatched spellings are a tell: for British
English, US spellings (organize, color, behavior, favor, center, analyze,
defense, program, fulfill, math) — and vice versa. Applied only when the user
states which register they want.

---

## Rewriting principles

- **Preserve meaning and facts.** No real claim dropped for the sake of cleaner
  prose, and no fact, source, name, or number fabricated to fill a flagged gap.
- **Prefer the plain word.** Short, concrete, common words over inflated ones.
- **Prefer the direct claim.** State things; no framing, hedging, or
  throat-clearing.
- **Vary rhythm.** Mixed sentence and paragraph lengths.
- **Keep the author's voice.** Match their register; personality is not flattened
  into corporate neutral — the goal is human, not generic.
- **When a flag is load-bearing, leave it.** A term of art, a quoted title, or a
  proper noun stays, with a note, rather than being mangled.

---

## Reference: a worked review

A review that applies this catalogue typically produces a verdict line, a list
of findings, then a clean rewrite. Example:

```
Verdict: heavy AI signature — 2 P0, 5 P1, 3 P2

P0  mechanical — "I hope this helps!" (closing line) → delete
P0  vague-attribution — "studies show" with no source → name it or cut
P1  tier1 — "leverage" ×3 → use
P1  tier1 — "utilize" → use
P1  structural — antithesis "it's not a tool, it's a platform" → state it directly
P1  structural — em-dash over-use, 4/1k → convert some to commas/periods
P1  tier2-cluster — "empower" + "streamline" in ¶2 → rewrite
P2  tier3-density — 3.4% of words → vary vocabulary
P2  stylometric — uniform paragraph length → vary lengths

--- Rewrite ---
[clean version of the draft here]
```

---

## Suggested GPT instructions

Paste a block like this into the custom GPT's **Instructions** field (the
Configure tab). It is deliberately short; the detail lives in this knowledge file.

```
You spot and fix the tells that give away AI-generated writing. You have a
knowledge file, "AI-Tell Reference," that catalogues every tell, its severity
(P0/P1/P2), and its fix — consult it and apply it consistently.

For each draft the user gives you, unless they ask for something narrower:
1. Scan it against every category in the reference, respecting the escape hatch
   (never flag code, blockquotes, or quoted material).
2. Report each tell as: [SEVERITY] category — what you found → suggested fix.
3. Rewrite the whole draft with the tells removed, preserving meaning, facts,
   and the author's voice. Never invent a fact or source to fill a gap; flag it
   instead.
4. Open with a verdict line: total P0/P1/P2 counts and a one-line judgment
   (reads clean / light polish / heavy AI signature).

Any P0 or P1 finding means the draft fails and needs revision; P2 is advisory.
Keep the tone matter-of-fact — show the fix, don't lecture.
```
