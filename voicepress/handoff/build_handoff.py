"""Assemble the ChatGPT handoff pack from the live engine: python3 handoff/build_handoff.py"""
import glob, re, zipfile
from pathlib import Path
from voicepress import pipeline, lint, fingerprint, pov, project
from voicepress.pipeline import load_voice

import sys
V = Path(sys.argv[1] if len(sys.argv) > 1 else "voices/voice-a")
OUT = Path(sys.argv[2] if len(sys.argv) > 2 else "handoff/chatgpt"); OUT.mkdir(parents=True, exist_ok=True)
voice = load_voice(V)

# 02 bible
(OUT / "02-style-bible.md").write_text((V / "bible.md").read_text())
# 03 craft
craft = (Path("voicepress") / "craft.md").read_text()
if voice.get("mode") == "relaxed":
    craft = craft.split("## 5.")[0] + "\n(Relaxed mode: the style bible and benchmark sample override everything else.)\n"
(OUT / "03-craft-library.md").write_text(craft)

# 04 checks
def readable(rx):
    s = re.sub(r"\\b|\(\?:|\)\?|\(|\)|\^|\$|\\s\+|\\s", " ", rx).replace("['’]?", "'").replace("|", " / ")
    return re.sub(r"\s+", " ", s).strip()
by = {}
for cat, rx in lint.PHRASES:
    by.setdefault(cat, []).append(readable(rx))
ycfg = (V / "voice.yaml").read_text()
L = ["# Checks, targets and editor passes", "",
     "Everything the engine checks, in one place. Run every section on every chapter. If you can run code, the zip does all of this automatically (`python -m voicepress lint file.md --top 0`).", "",
     "## 1. Banned phrases and constructions", "",
     "Each line is a pattern (alternatives separated by /). Any match must be recast. 'and yet' is allowed once per chapter.", ""]
by["construction"] = [
    "'the kind of X that/who/where'",
    "reversal: 'It wasn't X. It was Y.' / 'it isn't A, it is B'",
    "'not because X, but because Y'",
    "'Not a X. A Y.' / 'Not the X. Just Y.'",
    "'maybe, just maybe'",
    "'and yet' (once per chapter at most)",
    "'a reminder that / of'",
    "'somehow'",
]
for cat, items in by.items():
    L += [f"**{cat}**", ""] + [f"- {i}" for i in items] + [""]
L += ["**Stock one-line beats** (a paragraph that is only this): He looked up. / She went still. / They didn't move. / He swallowed. / She exhaled. / He nodded slowly. / She said nothing. / Too much. Too soon. / And then silence. / Silence fell. / Nothing happened. / Time stopped.", "",
      "**Other line checks**", "",
      "- No em dash or en dash, ever (also no `--`).",
      "- Similes ('like a', 'as if', 'as though'): rare, 1 to 3 per 1,000 words.",
      "- Same word opening 4 narration sentences in a row, or 4 paragraphs in a row: vary.",
      "- Any 4-word phrase used 3+ times in a chapter: a tic; vary.",
      "- Stacked fragment runs ('Cold. Dark. Alone.'): rare.", "",
      "## 2. The voice fingerprint (measured from the author's samples)", "",
      "Rates are per 1,000 words unless they're shares (0 to 1). Stay inside the range.", "",
      "| measure | target range | if out of range |", "|---|---|---|"]
for k, (lo, hi) in voice["_targets"].items():
    low, high = fingerprint.ADVICE.get(k, ("", ""))
    L.append(f"| {k} | {lo:.2f} to {hi:.2f} | {('LOW: ' + low + ' ') if low else ''}{('HIGH: ' + high) if high else ''} |")
L += ["", "Definitions: *spaced_hyphen* = ' -' cut-offs; *subjectless* = sentences that drop a carried-over subject; *short/long_sentence_share* = sentences of 6 words or fewer / 30 or more; *threes* = groups of three items; *polysyndeton3* = 'X and Y and Z'; *triple_beats* = three short sentences in a row; *stair_paragraphs* = three one-line paragraphs in a row; *the_way_similes* = 'the way a man does X'; *reversals* = 'not X, but Y'; *aphorisms* = quotable general truths; *image_paragraph_share* = share of long paragraphs carrying an image; *explained_subtext* = narration explaining a gesture already shown; *plain_dialogue_share* = share of dialogue lines that hedge ('well', 'I don't know', literal answers).", "",
      "## 3. Deep third and dialogue checks", "", "| check | range | fix |", "|---|---|---|"]
for k, (lo, hi) in pov.TARGETS.items():
    L.append(f"| {k} | {lo} to {hi} | {pov.ADVICE[k]} |")
L += ["", "Filter verbs: saw, heard, felt, noticed, watched, realised, wondered, thought, knew, sensed, seemed to. Outside emotion: 'looked/seemed/sounded (very) tired/sad/angry/afraid...'. Stage beats: one-line 'She waited.' 'He nodded.' 'She looked at him.' Echo line: a 1 to 2 word reply repeating the previous speaker's word. Interior sentences: narration that can only be the character's own voice (interjections, verdicts, self-address by name, rhetorical questions, imperatives to self, generic 'you').", "",
      "## 4. Writer brief (the full drafting prompt)", "", "```", pipeline.writer_prompt(voice), "```", "",
      "## 5. Story editor checks", "", "```", pipeline.STORY_EDITOR, "```", "",
      "## 6. Story revision brief", "", "```", pipeline.STORY_REVISE, "```", "",
      "## 7. Line editor brief", "", "```", pipeline.EDITOR, "```", "",
      "## 8. Story ledger", "", "Brief:", "", "```", pipeline.LEDGER, "```", "", "Template:", "", "```", project.LEDGER_TEMPLATE, "```", "",
      "## 9. Author pass (for the human)", "",
      "After the chapter, list 5 to 10 lines the author should rewrite in their own hand: the most polished-sounding line, any quotable line, the most 'writerly' image, a dialogue line that lands too neatly, and any sentence that explains what a gesture already showed. One line each: quote it, say why.", "",
      "## 10. Voice settings (voice.yaml)", "", "```yaml", ycfg, "```"]
(OUT / "04-checks-and-targets.md").write_text("\n".join(L))

# 05 samples, 06 techniques
def bundle(title, files):
    return f"# {title}\n\n" + "\n\n---\n\n".join(Path(f).read_text().strip() for f in files) + "\n"
(OUT / "05-voice-samples.md").write_text(bundle("Voice A: the author's own pages", sorted(glob.glob(str(V / "samples/own-*.md")))))
tech = sorted(glob.glob(str(V / "techniques/*.md")))
if tech:
    (OUT / "06-technique-studies.md").write_text(bundle("Technique studies: inspired-by moves in Voice A", tech))

# engine zip
with zipfile.ZipFile(OUT / "voicepress-engine.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for f in glob.glob("voicepress/*.py") + ["voicepress/craft.md", "README.md"]:
        z.write(f)
    for f in glob.glob("voices/voice-a/**/*", recursive=True) + glob.glob("voices/_template/**/*", recursive=True):
        if Path(f).is_file() and "/inspired/" not in f and not f.endswith(".pyc"):
            z.write(f)
print("ok")
