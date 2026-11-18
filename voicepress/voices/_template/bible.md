# Style Bible: <VOICE NAME>

Sections 1 to 5 describe THIS author and are drafted from the samples by `python -m voicepress distill`.
Sections 1a and 6 to 8 are general craft rules that work for any book; keep or edit them.

<!-- VOICE-SPECIFIC:START -->
## 1. The voice in one paragraph
(run `distill`, or write it yourself)

## 2. Mechanics. These are hard rules.

## 3. Signature moves

## 4. Scene types

## 5. Borrowed from inspired-by authors (technique only)
<!-- VOICE-SPECIFIC:END -->

---

## 1a. Story engine first (the most important section)

Sentence polish is the last 10%. What makes a scene work, measured against Voice B's best pages
(the Kylar dock job):

1. **Somebody wants something concrete, now.** Money, a person out of a cell, a boy up the stairs
   before the constable arrives. Not a mood.
2. **Show the plan.** Let a character lay it out in plain dialogue, with who pays, why, the timing,
   and what could go wrong. Exposition is fine when it's a plan, because the reader is now holding
   a promise the scene will break.
3. **Break the plan in a specific, surprising way** that uses the setup: the knife goes into the
   stomach, not the blood bladder. The reader should think "oh no" before the character does.
4. **Pay the cost in physical, procedural detail,** and if a mind is failing, let it fail confusedly
   (the catchpole he can't remember).
5. **Let feeling come out sideways.** The character starts to say the true thing, swerves into a joke
   or an order, and someone needles him back.
6. **Be clear, not coy.** The POV character may say exactly what he works out: "Kylar could tell Jarl
   was avoiding details because Uly was in the room." Ban only *redundant* interpretation, never clarity.
7. **Button on the other side.** Sometimes cut to the antagonist for the last line, pleased with himself.

Transparent prose is allowed to be ordinary, and even to use a stock phrase now and then. A chapter
with a plan, a break and a cost in plain sentences beats a beautiful chapter where nothing is at stake.
Watch for repeated tics the linter can't see: the same fact or number restated ("thirty-one years"
six times), the same sentence opener, the same kind of beat.

---

## 1b. Plain is the default

Most sentences just move people around and say what happened. Images are rare: spend them like
money. Avoid "the way a man does X" comparisons, reverse-and-qualify moves ("not X, nothing so Y,
but Z") and maxims. Dialogue can hedge, answer literally and end flat. The fingerprint holds the
author's real rates for all of these. Every chapter ends with an author-pass worksheet.

---

## 6. Loose, not metered

Machine prose falls into a metronome: groups of three, a short beat after every long sentence,
every paragraph landing on a button. The author's pages are lumpier than that. Write lumpy.

**Break the rule of three.** Measured on the author's pages (see `python -m voicepress fingerprint`): keep threes at the author's rate.
- Default to **pairs** (`hatchets and boning knives`) or **fours and more** .
- Make lists **lopsided**: two short items and a long trailing one, or one item that runs on so long the list forgets it was a list.
- Let some lists **trail off** with an ellipsis, or break off with ` -`, instead of closing neatly.
- Three short sentences in a row is a drumbeat. Use it at most once per scene, and only where the scene peaks. Otherwise run to two, or to four and more.
- Never three one-line paragraphs in a row as a staircase. Merge one into its neighbour.
- A word repeated three times ("ringing, ringing, ringing") gets one use per book, not one per chapter.

**Let some sentences be plain.** Not every line is a beat. Some just carry information and stop:
`The salt-wives' stalls ran down to the tideline. Hugh walked the long way round.`

**Let paragraphs end flat.** Not every paragraph lands on a quip, a reveal or a punchy fragment.
Some stop mid-thought, or on an ordinary detail.

**Short beats must carry a fact.** The author's one-line paragraphs say something new (`Alas.`,
`But they didn't have a chance.`, `There. / It was done.`). Stock drama like `She went down.`,
`They didn't care.`, `He looked up.`, `Bartoss went still.` or `Too much. Too soon.` adds nothing.
Cut it, or make it carry a concrete fact.

**Asides and wandering.** Let the POV character's mind go somewhere irrelevant for a line: a petty
thought, a smell that reminds him of something stupid, a grudge. Real attention is untidy.

---

---

## 7. Story shape

How the plot is built gives machine fiction away as much as the prose does. Check every chapter
against these:
- **Escalate.** Every beat turns the situation or raises the price. Never two beats in a row at the same pitch.
- **Never state the theme.** No narration or speech explaining what a scene meant. The author lets Elena say it, then Hugh fights it.
- **Run two tracks.** Something else is always pressing under the main action: a debt, a secret, the dead, a lover's grudge, a wound that's getting worse.
- **Make choices cost.** At least once a chapter, Hugh chooses something he can't take back, or that's not clean.
- **Bend time.** Memory intrusions, flashes, an aftermath before its cause. The author uses `A flash of memory:` and the dead's voices to do this.
- **Give everyone wants.** Every named character is pursuing something, including enemies, and they act on it whether or not Hugh is in the room.
- **Nobody is fully legible.** Characters read each other partly and wrongly, through resentment, love
  or self-interest. Let one misreading stand uncorrected, and let one argument end unsettled.  Nobody
  articulates "their slice" of the chapter's theme.
- **Uneven attention.** The POV character loses count, misreads a face, is ambushed by a useless memory
  at the worst moment, or simply notices nothing helpful. Specific mental habits reveal feeling better
  than a polished sentence about the feeling.
- **Don't explain the gesture.** If a hand comes off a hilt, that's the moment. Don't follow it with
  what it meant.
- **A quotable-line budget.** Two or three lines a scene may land hard. The rest should be what this
  particular person would say, which is usually plainer.
- **Root the payoff.** A cost or reveal at the end should grow from something planted earlier, so it
  feels inevitable rather than picked for effect.
- **Kill the predictable beat.** Find the scene's most expected turn and swap it for one the reader won't see coming but will believe.

---

---

## 8. Never

Machine tells. Any of these is a defect.
- (Edit for this voice: punctuation this author never uses.)
- `It wasn't X. It was Y.` / `Not X. Not Y. Just Z.` / `not because…, but because…`
- `the kind of [noun] that…`, `something shifted`, `a testament to`, `the weight of the world`,
  `let out a breath he didn't know he was holding`, `a beat`, `the silence stretched`, `hung in the air`,
  `air thick with`, `ozone`, `copper tang`, `ghost of a smile`, `barely above a whisper`, `delve`, `tapestry`.
- Sensory lists of three as a paragraph opener (`The smell of X, Y, and Z filled the room.`).
- Every paragraph ending on a quip or punchline. Some paragraphs should just stop.
- Characters narrating their own feelings in therapy language (`I need to process this`, `boundaries`, `I hear you`, `valid`).
- Modern idioms that break the world: `okay`, `deal with it`, `on the same page`.
- Explaining a world noun the first time it appears.
- Summarising, in narration, what a line of dialogue just showed.
- A closing reflection or moral. Ending a chapter on a question.
- Said-bookisms. Adverb-laden tags (`said softly`, `said angrily`), except rarely.
- Symmetry: paragraphs of identical length, alternating dialogue and description like a metronome.
- Stock fiction moves: `the world slowed`, `time stood still`, `let the silence answer`, `smiled. It was not a pleasant smile`,
  `her voice, sharp with…`, `a voice like…`, `and somewhere behind him…`, `sounding almost apologetic`,
  `with the patient interest of…`, `quiet certainty/menace`, `or rather`, `every last one`.
- Stacks of threes (section 6).
