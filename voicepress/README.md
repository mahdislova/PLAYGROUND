# voicepress

Prose pipeline: you describe your voice, Claude drafts, then narrow rewrite layers
fish out machine tells one category at a time, and a deterministic linter checks every stage.

```
brief ─▶ draft ─▶ scrub ─▶ structure ─▶ voice ─▶ (lint dirty? scrub+structure again) ─▶ FINAL.md
                    ▲          ▲           ▲
                    └──── lint findings fed to each layer as targets
```

| layer | job |
|---|---|
| **lint** (no model) | phrase tells (“something shifted”, “the kind of X that”, “it wasn't X, it was Y”), stock body language, repeated 4-grams, same-word paragraph openers, stacked fragments, em-dash / simile / triad density, sentence-length variance, one-line-paragraph ratio |
| **scrub** | swaps flagged clichés for scene-specific detail, or cuts them |
| **structure** | rhythm: varies sentence length, collapses fragment stacks, breaks triads, thins em-dashes and similes |
| **voice** | rewrites toward *your* samples: their rhythm, punctuation, dialogue tags, what they notice |

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # or `ant auth login`
```

1. Put 1–5k words of **your own** writing in `samples/` and list them in `style.yaml`. This is the
   most important step: the voice layer imitates whatever is there.
2. Edit `voice:` and `rules:` in `style.yaml`. Add your own pet hates to `banned_phrases`, and
   anything the linter flags that you actually like to `allowed_phrases`.

## Use

```bash
python -m voicepress lint chapter.md                 # free report, no API
python -m voicepress refine chapter.md               # run an existing draft through the layers
python -m voicepress write @brief.md                 # draft from a brief, then the layers
python -m voicepress refine ch1.md --layers scrub,structure --extra-passes 2
```

Each run lands in `runs/<timestamp>/` with every stage (`01_input.md`, `02_scrub.md`, …) and its
lint report alongside, so you can diff what each layer did and throw out a layer that hurt.

## Notes

- The linter is a prose-quality tool, not a detector clone. Commercial AI detectors are noisy
  and change constantly; nothing here guarantees a score on any of them. What it does is strip
  the habits readers and editors notice.
- The output is only as much “yours” as the samples and your own editing pass make it. Read
  `FINAL.md` with a pen.
- If you publish through a platform with AI-content disclosure rules (e.g. Amazon KDP), those
  still apply to text drafted this way.
