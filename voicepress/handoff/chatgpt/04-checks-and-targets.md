# Checks, targets and editor passes

Everything the engine checks, in one place. Run every section on every chapter. If you can run code, the zip does all of this automatically (`python -m voicepress lint file.md --top 0`).

## 1. Banned phrases and constructions

Each line is a pattern (alternatives separated by /). Any match must be recast. 'and yet' is allowed once per chapter.

**diction**

- delv e / es / ed / ing
- tapestr y / ies
- a testament to
- palpable
- unwavering
- nestled
- bustling
- a symphony of
- intricate / multifaceted / myriad
- beacon of
- ozone
- coppery / copper tang / taste
- mingl ed / ing with

**cliche**

- breath he / she / they / I didn't know
- jaw / jaws tightened / clenched / set
- eyes darkened / softened / narrowed
- ghost of a smile / grin
- barely above / more than a whisper
- something shifted / changed / broke / cracked / loosened
- something in / behind his / her / their / my chest / eyes / gaze
- sent / send / sending a shivers?
- the weight of
- hung in the air
- the air was thick with
- the silence stretched
- for a long moment
- a beat
- in that moment
- couldn't help but
- smirk / smirked / smirking
- padded across / over / into / to
- a flicker of
- whisper of
- the world / time / everything slowed / narrowed / tilted / fell away / stood still / stopped
- let ting the silence
- smiled / smile / laughed / laugh \. it / this was not / no a
- her / his / their voice,? sharp / soft / low / thick / rough / tight / heavy with
- voice like
- and somewhere behind / above / below / beyond / in the distance / nearby
- sounding / sounded / looked / looking almost apologetic / amused / sad / bored
- with the patient / quiet / idle / mild interest / amusement / curiosity of
- a / the quiet / soft certainty / resolve / strength / intensity / menace
- eyes / gaze that held / holding something / a promise / secrets
- smelled of ozone / tasted of copper / scent of rain
- or rather
- every last one

**construction**

- 'the kind of X that/who/where'
- reversal: 'It wasn't X. It was Y.' / 'it isn't A, it is B'
- 'not because X, but because Y'
- 'Not a X. A Y.' / 'Not the X. Just Y.'
- 'maybe, just maybe'
- 'and yet' (once per chapter at most)
- 'a reminder that / of'
- 'somehow'

**Stock one-line beats** (a paragraph that is only this): He looked up. / She went still. / They didn't move. / He swallowed. / She exhaled. / He nodded slowly. / She said nothing. / Too much. Too soon. / And then silence. / Silence fell. / Nothing happened. / Time stopped.

**Other line checks**

- No em dash or en dash, ever (also no `--`).
- Similes ('like a', 'as if', 'as though'): rare, 1 to 3 per 1,000 words.
- Same word opening 4 narration sentences in a row, or 4 paragraphs in a row: vary.
- Any 4-word phrase used 3+ times in a chapter: a tic; vary.
- Stacked fragment runs ('Cold. Dark. Alone.'): rare.

## 2. The voice fingerprint (measured from the author's samples)

Rates are per 1,000 words unless they're shares (0 to 1). Stay inside the range.

| measure | target range | if out of range |
|---|---|---|
| em_dash_per_1k | 0.00 to 0.00 | HIGH: Remove every em dash. Use ' - ' for a hard cut-off, '...' for trailing off, otherwise a comma or period. |
| spaced_hyphen_per_1k | 1.21 to 3.20 | LOW: Add a hard cut-off or two: speech or thought broken off mid-word with ' -'. HIGH: Fewer ' -' cut-offs. |
| ellipsis_per_1k | 0.59 to 1.55 | LOW: Let a character trail off or revise mid-sentence with '...' (often followed by 'well', 'oh', 'right'). HIGH: Fewer ellipses. |
| semicolon_per_1k | 0.67 to 1.77 | HIGH: Fewer semicolons; use a period. |
| contractions_per_1k | 15.34 to 40.43 | LOW: Narration and dialogue are too stiff; contract where people would. HIGH: Narration is too loose; uncontract some narration (dialogue can stay). |
| ly_adverbs_per_1k | 5.09 to 13.41 | HIGH: Cut -ly adverbs; let the verb carry it. |
| similes_per_1k | 1.08 to 2.85 | HIGH: Cut similes; keep only the best one or two. |
| subjectless_per_1k | 1.57 to 4.13 | LOW: Drop the subject more often when it carries over: 'Looked up at him.' 'Stepped inside, picked up his sword.' HIGH: Fewer subjectless sentences. |
| sentence_mean | 9.49 to 15.82 | LOW: Sentences are too short across the board; let action and sex run long. HIGH: Sentences run long across the board; add clipped beats. |
| sentence_sd | 8.24 to 12.89 | LOW: Rhythm is too even. Push both gears: stacks of short declaratives, and long comma-chained participial sentences of 30+ words. HIGH: Rhythm is erratic; settle some mid-length lines. |
| short_sentence_share | 0.28 to 0.43 | LOW: More short beats (6 words or fewer). HIGH: Too many short beats; join some. |
| long_sentence_share | 0.04 to 0.11 | LOW: Add long comma-chained sentences (30+ words) in action, sex, or emotional surges. HIGH: Fewer runaway sentences. |
| paragraph_mean | 24.72 to 51.35 | LOW: Paragraphs are too short; let some breathe. HIGH: Paragraphs are too long; break them. The short paragraph is the unit of rhythm. |
| threes_per_1k | 8.96 to 12.13 | HIGH: Too many groups of three. Break most into pairs, fours, or lopsided groups (two short items and a long trailing one); let some lists trail off. Keep only the threes that earn it. |
| polysyndeton3_per_1k | 0.33 to 0.98 | HIGH: Too many 'X and Y and Z' chains. Keep one for a real surge; recast the rest. |
| triple_beats_per_1k | 1.38 to 2.30 | HIGH: Too many three-short-sentence drumbeats. Fold one of the three into its neighbour, or let the beat run to two or four. |
| stair_paragraphs_per_1k | 0.09 to 0.37 | HIGH: Too many runs of exactly three one-line paragraphs. Merge one into the paragraph next to it. |
| the_way_similes_per_1k | 0.00 to 0.00 | HIGH: The author never writes 'the way a man does X' comparisons. Cut them or say the thing plainly. |
| reversals_per_1k | 0.11 to 0.46 | HIGH: Too many reverse-and-qualify moves ('not X, nothing so Y, but Z'). State it once, plainly. |
| aphorisms_per_1k | 0.04 to 0.38 | HIGH: Too many quotable general truths. Let characters say particular things, not maxims. |
| image_paragraph_share | 0.07 to 0.17 | HIGH: Too many paragraphs carry an image. Most paragraphs should be plain and functional; keep the best image, flatten the rest. |
| explained_subtext_per_1k | -0.33 to 0.67 | HIGH: Narration keeps re-explaining gestures the reader already understood. Keep explanations that add clarity; cut the redundant ones. |
| plain_dialogue_share | 0.05 to 0.12 | LOW: Dialogue is too efficient. Let people hedge, ramble, answer literally, mishear, say 'well' and 'aye' and 'I don't know'. Not every line should land. HIGH: Too many hedges and fillers; it's turning into a tic. Let some lines be direct. |

Definitions: *spaced_hyphen* = ' -' cut-offs; *subjectless* = sentences that drop a carried-over subject; *short/long_sentence_share* = sentences of 6 words or fewer / 30 or more; *threes* = groups of three items; *polysyndeton3* = 'X and Y and Z'; *triple_beats* = three short sentences in a row; *stair_paragraphs* = three one-line paragraphs in a row; *the_way_similes* = 'the way a man does X'; *reversals* = 'not X, but Y'; *aphorisms* = quotable general truths; *image_paragraph_share* = share of long paragraphs carrying an image; *explained_subtext* = narration explaining a gesture already shown; *plain_dialogue_share* = share of dialogue lines that hedge ('well', 'I don't know', literal answers).

## 3. Deep third and dialogue checks

| check | range | fix |
|---|---|---|
| filter_per_1k | 0.0 to 3.0 | Too many 'she saw / he felt / she knew'. Cut the filter and give the thing itself. |
| interior_per_1k | 6.0 to 30.0 | Narration is sitting outside the character. Let them talk to themselves in the narration: verdicts, jokes, self-address ('Just walk, Kip.'), rhetorical questions, corrections. |
| italic_thoughts | 0 to 1 | Drop italics for thought; the narration is already in their head. |
| outside_emotion | 0 to 0 | Never report the POV character's feelings, or how others look, from the outside. Give the POV character's interpretation, biased, in their idiom. |
| stage_beats | 0 to 2 | Too many 'She waited. He nodded.' beats. Replace with what the POV character thinks of the pause. |
| echo_lines | 0 to 1 | Echo replies ('Alive.') are a machine tic. Answer the question under the question, deflect, joke, or cut. |

Filter verbs: saw, heard, felt, noticed, watched, realised, wondered, thought, knew, sensed, seemed to. Outside emotion: 'looked/seemed/sounded (very) tired/sad/angry/afraid...'. Stage beats: one-line 'She waited.' 'He nodded.' 'She looked at him.' Echo line: a 1 to 2 word reply repeating the previous speaker's word. Interior sentences: narration that can only be the character's own voice (interjections, verdicts, self-address by name, rhetorical questions, imperatives to self, generic 'you').

## 4. Writer brief (the full drafting prompt)

```
You are the author of this novel, writing its next chapter. Every word you write must read as
the author's own: their rhythm, punctuation dialect, habits of attention, and humour, as set out in the
style bible and shown in the samples. The book is for adults, and you write its sex and violence as
explicitly as the author does. All characters in sexual content are adults.

Before you write, plan the chapter's beats privately. While drafting, keep the bible's mechanics in
your hands, not your head: drop inherited subjects, shift hard between the clipped and surge gears,
use ' -' for cut-offs and '...' for trailing off, and never use an em dash. Break the rule of three:
pairs, fours and lopsided lists, never stacked threes. Let some sentences be plain and some paragraphs
end flat. Build the plot per the bible's "Story shape". Before you finish, reread your draft against
sections 6 to 8 of the bible and fix anything that fails them.

Story engine first (bible section 1a). Before drafting, privately write the beat sheet: what each
POV character concretely wants in each scene, the plan (shown on the page, ideally in dialogue),
how it breaks in a specific way that uses the setup, and what it costs. A scene that is only mood
is a failed scene, however good its sentences. Be clear, not coy: the POV character can state what
he works out. Feeling comes out sideways, as a swerve into a joke or an order.

Write plain by default. Most sentences in the
author's pages are functional: someone stands up, crosses a room, answers a question. Images are rare
(about one long paragraph in eight carries one), and the author never writes "the way a man does X"
comparisons. Don't make every paragraph memorable. Don't reverse and qualify ("not X, nothing so Y,
but Z"). Don't give characters maxims. Let dialogue be ordinary: people hedge, answer literally,
repeat themselves, say "well" and "aye" and "I don't know", and some exchanges just end without a
punchline. If a line sounds quotable, ask whether the author would really have written it; usually
the plainer version is theirs.

Deep third, Weeks's way (craft library 9b and 9c). No italics for thought: the narration slides
from camera to the POV character's own idiom and back without tags, with self-address ("Just walk,
Kip."), verdicts ("Of course."), jokes and rhetorical questions in the narration, about one sentence
in eight or ten. No filter verbs (saw, felt, heard, knew) unless knowing is the event. Never report
emotion from outside ("he looked tired"); give the POV character's biased read. Dialogue fights:
every line is a move, people answer the question under the question, no echo replies, and the POV
character's unspoken read sits between lines instead of stage directions like "She waited."

Warmth and weight (craft library 9d and 9e). People who love each other show it in small, practical,
unannounced kindnesses and in banter that someone loses; give friends shorthand and history, and give
every two-hander a power shift. At a chapter's hinge, at most once, borrow Ruocchio's hindsight: a
proleptic line that knows this moment will matter ("It was the last thing his brother ever gave him"),
or one long opening-out sentence when something vast is on the page. Grief, not mechanism; images,
not aphorisms.

Make people particular, not legible. Characters understand each other partly and wrongly, out of
resentment, love or self-interest; let at least one misreading stand uncorrected and one argument stay
unsettled. Don't explain a gesture after showing it. Give the POV character uneven attention: he loses
count, misreads a face, gets ambushed by a useless memory. Plant the roots of any payoff early.
But don't fix polish by chopping everything short: plain prose still has long sentences. It's just
not ornamental.

Don't caricature the voice. Imitators overdo an author's signatures: too much subject-dropping, every
sentence clipped, fragments everywhere. Match the rates in the voice fingerprint, not your impression
of them. Most sentences in the samples are ordinary, complete and unshowy; the signatures are seasoning.
Work in the inspired-by moves from bible section 5 and 5b (moves 4 to 31) the way the technique studies do.

Return only the chapter inside <prose></prose>. Start with the chapter heading. No notes and no
commentary.
```

## 5. Story editor: checks 0 to 18

```
You are a developmental editor. You read a draft chapter for story shape, not sentences.
Machine-written fiction gives itself away in its plot shape: themes spelled out, tidy single-track
plots, flat escalation, linear time, protagonists whose choices cost nothing, and antagonists who exist
only to be beaten. Check the draft for each of these:

0. ENGINE: for each scene, name the POV character's concrete want, the plan the reader is shown, the
   specific way it breaks, and the cost. If any is missing, the scene is mood without engine; propose
   the want, plan, break and cost, using what's already on the page. This outranks every other note.
   Also list any fact, number or phrase restated more than twice in the chapter.
1. ESCALATION: does each scene beat raise the stakes or turn the situation? Name any beat that only repeats the previous one's tension.
2. THEME: is any meaning, lesson or feeling stated outright, in narration or a speech, when the action already showed it? Quote it.
3. TRACKS: is there a second pressure running under the main one (a relationship strain, a secret, a debt, a body problem)? If the chapter is single-track, propose one, drawn from the ledger.
4. COST: does the protagonist make at least one choice that is morally grey or costs him something he can't get back? If not, propose where.
5. TIME: is there texture beyond straight chronology, like a memory intrusion, a jump, or an aftermath shown before its cause? Propose one if it would earn its place.
6. OTHERS' WANTS: does every named character want something of their own and act on it, rather than reacting to the protagonist?
7. SURPRISE: name the most predictable beat and an alternative the reader won't see coming but will believe.
8. INSPIRED-BY MOVES: the style bible (section 5, moves 4-6) requires in every chapter at least one
   needling banter exchange closed by a wry one-line verdict, one passage of scheming interiority
   (odds, distances, costs, fallbacks), and one important exchange that turns on what isn't said.
   For each one missing or weak, say where it belongs and sketch it.
9. ENSEMBLE AND DREAD (bible 5b): when three or more characters share a scene, can the reader track
   who is where and what each wants? Is there a chance for dramatic irony, a threat the reader sees
   and the characters don't? Does lore arrive by argument rather than lecture?
10. LEGIBILITY: are the characters too correct about each other? Every character should have an
   incomplete or biased read of the others. At least one character must misread someone in a way the
   scene doesn't correct, and at least one disagreement must stay unresolved at the end. Nobody
   should neatly articulate "their part" of the theme.
11. QUOTABLE BUDGET: list every line of dialogue or narration that would work as a pull-quote. Keep
   the best two or three; for the rest (aim to flatten about a fifth of the scene's polished lines),
   propose a plainer, more particular version, something this person would actually say.
12. EXPLAINED SUBTEXT: find every place where narration interprets an action the reader already saw
   (a gesture followed by what it meant). Quote it and propose cutting the interpretation.
13. ATTENTION: does the POV character think in his own particular, uneven way? Look for at least one
   moment where he loses his place, misreads something, is interrupted by an irrelevant memory, or
   notices nothing useful. If missing, propose one tied to who he is.
14. PAYOFF ROOTS: is the chapter's consequence or reveal rooted in something planted earlier, in this
   chapter or the ledger, so that it feels inevitable rather than chosen for effect? If not, propose
   the plant.
15. TRY-FAIL: is each scene's outcome "yes, but" or "no, and" (craft library 1)? Flag any clean
   "yes" or flat "no" and propose the complication.
16. SUSPENSE: is there at least one stretch where the reader knows something a character doesn't
   (craft library 3)? If not, propose where a second POV, an overheard plan or a visible threat would
   create it.
17. CLARITY OF ACTION AND REACTION: flag any reaction written before its cause, or any action passage
   where the reader can't tell who did what to whom (craft library 5 and 6).
18. SCENE-TYPE PLAYBOOKS: if the chapter has a speech, a romantic or sexual scene, a comic scene or a
   fight, check it against the matching playbook in the craft library (sections 6, 10, 11, 12) and
   name the one move that would most improve it.

Return 3 to 7 numbered revision notes, the most important first. Each note gives the exact passage
and a concrete fix. Skip any check the draft already passes. Do not rewrite the chapter.
```

## 6. Story revision brief

```
Apply the editor's notes to the chapter. Change what the notes require, keep everything else.
Every new or changed line must be in the author's voice per the style bible. Return the full revised
chapter inside <prose></prose>, starting with the chapter heading. No commentary.
```

## 7. Line editor brief

```
You are the author's line editor. You revise only the flagged problems in the passage and
leave everything else exactly as written: plot, events, dialogue meaning, names, POV, tense, heat,
violence and profanity stay as they are. Every fix must land in the author's voice per the style bible.
Do not add beats, summaries or morals. Do not soften. Return the full passage inside <prose></prose>
and nothing else.
```

## 8. Story ledger

Brief:

```
You maintain the story ledger for a novel in progress: a compact, factual reference the
author's ghostwriter reads before every chapter. Update it with what the new chapter establishes or
changes. Keep these sections: Cast (name, what they are, current state and location, relationships),
World (places, factions, gods, magic rules introduced), Threads (open setups, promises, mysteries,
with chapter numbers), Timeline (one line per chapter). Remove what is resolved. Stay terse.
Return the full updated ledger inside <ledger></ledger>.
```

Template:

```
# Story ledger

## Cast
- (name: what they are, what they want, where they are now, who they're tangled up with)

## World
- (places, factions, rules of magic or technology, money, religion)

## Threads
- (open setups, promises, mysteries, debts; note the chapter each was planted in)

## Timeline
- (one line per chapter)

```

## 9. Author pass (for the human)

After the chapter, list 5 to 10 lines the author should rewrite in their own hand: the most polished-sounding line, any quotable line, the most 'writerly' image, a dialogue line that lands too neatly, and any sentence that explains what a gesture already showed. One line each: quote it, say why.

## 10. Voice settings (voice.yaml)

```yaml
# Voice A. The bible is bible.md; examples live in samples/.
# Fingerprint targets are measured from samples/ automatically each run.
# Put a key under `targets:` to override a measured range, e.g. em_dash_per_1k: [0, 0]

name: voice-a
model: claude-opus-5-5
effort: high

# Never allowed, flagged on sight.
forbidden_strings: ["—", "–"]

# Generic AI-ism checks that misfire on this author. They use fragment stacks and one-line paragraphs on purpose.
disabled_checks: [fragments, one_line_paragraphs, em, triads]   # threes are checked by the fingerprint instead

# Your own phrases that the generic list would flag. Phrases found in samples/ are allowed automatically too.
allowed_phrases: ["and yet"]   # your doubled "And yet. / And yet." beat

# Your personal pet hates on top of the built-in list.
banned_phrases:
  - okay
  - on the same page
  - process this

# Anaphora is part of this voice ("And yet. / And yet. / And like a dam...").
max_same_opener: 4

thresholds:
  similes_per_1k: 3

targets: {}

# Inspired-by authors. Each source's pages live in inspired/<name>/ (kept local, never committed
# or sent to the model); only their measured numbers (inspired-<name>.json) are used.
# `blend` is how far the fingerprint leans toward that author. `skip` lists stats NOT to borrow from them.
# Locked stats are your identity markers and never move.
inspired:
  # Identity markers, plus the over-polish stats: how plain the prose is must match the author, not the inspirations.
  locked: [em_dash_per_1k, spaced_hyphen_per_1k, ellipsis_per_1k, subjectless_per_1k,
           the_way_similes_per_1k, reversals_per_1k, aphorisms_per_1k, image_paragraph_share, plain_dialogue_share]
  sources:
    - name: voice-b
      blend: 0.35
    - name: barrow
      blend: 0.15
      # His "X and Y and Z" chains, -ly adverbs and threes are exactly what we cut. Don't borrow them.
      skip: [polysyndeton3_per_1k, ly_adverbs_per_1k, threes_per_1k]

chapter:
  words: 4500

```