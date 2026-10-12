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
| `voice.yaml` | Forbidden strings (em/en dash), linter checks switched off because they misfire on your style, your pet hates, chapter length. |

**Fingerprint.** Each run measures your samples (punctuation dialect, subject-dropping rate,
sentence-length gears, paragraph size, contractions, adverbs, similes) and turns them into target
ranges. Every draft is checked against them. `python -m voicepress fingerprint` shows the ranges.

**Auto-allow.** If a phrase on the generic AI-ism list appears in your own samples ("jaw set",
"couldn't help but", "And yet."), it's your voice, so it isn't flagged.

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
