# Voicepress handoff for ChatGPT

This is the complete writing method: voice, craft, every check, and the engine code. It's built so another model can work in the same way.

## Setup (Custom GPT, best)
1. ChatGPT → Explore GPTs → Create → Configure.
2. **Instructions:** paste all of `01-INSTRUCTIONS.md`.
3. **Knowledge:** upload `02-style-bible.md`, `03-craft-library.md`, `04-checks-and-targets.md`, `05-voice-samples.md`, `06-technique-studies.md`, and `voicepress-engine.zip`.
4. **Capabilities:** turn on Code Interpreter & Data Analysis.
5. **Conversation starter:** "Write chapter N. Beats: … POV: … Canon notes: …"

## Setup (ChatGPT Project, also fine)
Put `01-INSTRUCTIONS.md` in the project instructions, and upload the other files to the project.

## Using it
- Give it the chapter brief: POV, the beats or episode outline, and anything canon.
- Ask for the full workflow: beat sheet, draft, story pass, line pass, measure, author-pass list.
- To measure a chapter it wrote (Code Interpreter), say: "Save the chapter as ch.md, unzip voicepress-engine.zip, pip install pyyaml, run `python -m voicepress lint ch.md --top 0`, and fix everything flagged."
- Other engine commands in the zip: `python -m voicepress fingerprint ch.md` (voice-target comparison) and `python -m voicepress author-pass ch.md` (lines to rewrite by hand).
- The `chapter`/`refine` commands call the Anthropic API and won't run inside ChatGPT. The workflow in 01 replaces them.

## What's not included
The Brent Weeks, Black Prism and Barrow passages used for calibration are not included. Only the measured stats and the distilled techniques are, in Voice A's own words.
