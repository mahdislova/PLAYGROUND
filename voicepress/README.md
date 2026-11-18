# voicepress

Writes new chapters of your book in your voice. The voice rules and the AI-ism avoidance are
loaded into the writer *before* it drafts, so the cleanup pass only catches what slips through.

```
voices/voice-a/                     book/
  bible.md      ─┐                    ledger.md        (cast, world, open threads, timeline)
  samples/*.md  ─┼─▶  WRITER  ◀──────  chapters/chNN.md (last ~1,500 words for continuity)
  voice.yaml    ─┘      │      ◀────  your brief
                        ▼
              lint + fingerprint  (no model, free)
                        │ anything flagged?
                        ▼
              POLISH flagged spans only (≤2 passes)
                        ▼
              book/chapters/chNN.md  +  ledger updated
```

## The voice folder

| file | what it is |
|---|---|
| `bible.md` | The distilled style bible: mechanics, signature moves, scene-type playbooks, the three techniques borrowed from Voice B, and the Never list. Edit it freely; the writer reads it every chapter. |
| `samples/` | Your own pages (OWN-01…06). The writer studies them as examples and the fingerprint is measured from them. Add more of your pages here and everything recalibrates. |
| `techniques/` | Original passages showing the inspired-by author's moves (banter, scheming, withholding, appraisal, cool violence) done in your mechanics. The writer studies them next to your samples. |
| `inspired/<name>/` | One folder per inspired-by author (currently `voice-b` and `barrow`). **Kept local**: gitignored, never sent to the model. Only their measured numbers (`inspired-<name>.json`) are used. |
| `voice.yaml` | Forbidden strings (em/en dash), linter checks switched off because they misfire on your style, your pet hates, chapter length. |

**Fingerprint.** Each run measures your samples (punctuation dialect, subject-dropping rate,
sentence-length gears, paragraph size, contractions, adverbs, similes) and turns them into target
ranges. Every draft is checked against them. `python -m voicepress fingerprint` shows the ranges.

**Blend.** Each source under `inspired.sources` in `voice.yaml` has a `blend` weight (Voice B 0.35,
The Barrow 0.15) and an optional `skip` list of stats not to borrow. The `locked` identity stats
(your dash dialect and subject-dropping) never move.

**Auto-allow.** If a phrase on the generic AI-ism list appears in your own samples ("jaw set",
"couldn't help but", "And yet."), it's your voice, so it isn't flagged.

## Craft library

`voicepress/craft.md` is general fiction craft every voice gets, loaded into the writer and the story
editor on every chapter: scene architecture (scene/sequel, try-fail "yes, but / no, and", arrive late
leave early, the plan rule), promises and payoffs, suspense versus mystery versus surprise, stakes,
motivation-reaction order, action clarity, dialogue, exposition, POV and interiority, humour (bathos,
callbacks), desire and sex scenes, speeches, description, pacing, openings and endings, character, and a
pre-flight checklist. The voice bible decides how sentences sound; the craft library decides how scenes
work. Edit it freely; it's plain markdown.

## Start a new project

Four steps, about ten minutes plus writing time. Replace `myvoice` and `books/mybook` with your names.

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...                     # or `ant auth login`

# 1. A voice: copies the general craft rules (story engine, plain prose, threes, story shape, Never list)
python -m voicepress new-voice myvoice
#    then put 3,000+ words of the author's OWN pages in voices/myvoice/samples/, one scene per .md file

# 2. Draft the voice-specific half of the bible from those samples, then read and correct it
python -m voicepress --voice voices/myvoice distill
python -m voicepress --voice voices/myvoice fingerprint     # the measured targets every chapter is checked against

# 3. A book. To continue an existing manuscript, import its chapters and build the story ledger from them
python -m voicepress --voice voices/myvoice new-book books/mybook --import path/to/existing/chapters --seed-ledger

# 4. Write chapters. Each brief should name the scene's want, the plan, and what goes wrong (bible 1a)
python -m voicepress --voice voices/myvoice chapter --book books/mybook \
  "Kira needs the harbour master's seal before dawn. Plan: swap it during the tide-bell. It breaks when..."
```

Each chapter lands in `books/mybook/chapters/chNN.md` with an `chNN.author-pass.md` worksheet next to it.
Work through that worksheet by hand before the chapter goes anywhere. Optional: inspired-by authors go in
`voices/myvoice/inspired/<name>/` (kept local) with a `sources:` entry in `voice.yaml`, and their moves
can be written up in bible section 5.

## Use

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...                       # or `ant auth login`

python -m voicepress chapter "Hugh tracks the Mink's backers to the salt market. Morwyn insists on coming. Ends with the ambush."
python -m voicepress chapter @briefs/ch07.md --words 6000

python -m voicepress lint book/chapters/ch03.md    # free check: flagged spans + off-voice stats
python -m voicepress refine some_draft.md          # pull an outside draft into the voice
```

`book/ledger.md` is plain markdown. Fix it by hand whenever it gets something wrong, and the
next chapter will follow your version. Every chapter's working files (draft, each polish pass,
and a report for each) land in `book/runs/`.

## Notes

- The fingerprint and linter measure craft habits, not any detector's score. Nothing here
  guarantees a result on a commercial AI detector.
- The quality ceiling is the samples. More of your own pages, across more scene types, gives a
  better writer and a tighter fingerprint.
- Voice B's text isn't stored here or sent to the model; only the techniques distilled from it
  (in `bible.md`) are.
- Publishing platforms' AI-disclosure rules (e.g. Amazon KDP) apply to text made this way.
