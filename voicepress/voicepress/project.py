"""Setting up a new project: a voice folder and a book folder.

  new-voice  copy the template (general craft rules + settings) into voices/<name>/
  distill    draft the voice-specific half of the bible from the samples (needs the API)
  new-book   make a book folder; optionally import existing chapters and build the ledger from them
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "voices" / "_template"

DISTILL = """You are a literary analyst preparing a style bible for a ghostwriter who will write new
chapters in this author's voice. You have the author's own pages and measured statistics.

Write ONLY these sections, in markdown, with these exact headings:

## 1. The voice in one paragraph
## 2. Mechanics. These are hard rules.
   (punctuation dialect, sentence-length habits, paragraph size, dialogue tagging, contractions,
   point of view and tense, register; cite the measured numbers where they matter)
## 3. Signature moves
   (the 6 to 12 habits that most make this author sound like themselves, each with one or two short
   quotes from the samples)
## 4. Scene types
   (how the author handles each kind of scene present in the samples: dialogue, action, interior,
   introductions, intimacy if present)
## 5. Borrowed from inspired-by authors (technique only)
   (write "None yet." unless notes on inspired-by authors are provided below)

Be specific and evidential: every claim should be visible in the samples. Describe what the author
actually does, including plain or unglamorous habits, not what good writing in general does.
Quotes must be short (under 25 words each). Don't invent habits the samples don't show."""


def new_voice(name: str, voices_dir: Path) -> Path:
    dest = voices_dir / name
    if dest.exists():
        raise SystemExit(f"{dest} already exists")
    shutil.copytree(TEMPLATE, dest)
    for f in (dest / "bible.md", dest / "voice.yaml"):
        f.write_text(f.read_text().replace("<VOICE NAME>", name).replace("<voice name>", name))
    return dest


def distill(voice: dict, llm, inspired_notes: str = "") -> Path:
    """Draft bible sections 1-5 from the samples and splice them into bible.md."""
    from .fingerprint import measure

    vdir: Path = voice["_dir"]
    samples = voice["_samples"]
    if len(samples.split()) < 1500:
        raise SystemExit(f"Only {len(samples.split())} words in {vdir / 'samples'}; add at least 3,000 of the author's own pages first.")
    stats = measure(samples)
    stat_lines = "\n".join(f"- {k}: {v:.2f}" for k, v in stats.items())
    user = (f"<measured_statistics>\n{stat_lines}\n</measured_statistics>\n\n"
            + (f"<inspired_by_notes>\n{inspired_notes}\n</inspired_by_notes>\n\n" if inspired_notes else "")
            + f"<author_samples>\n{samples}\n</author_samples>")
    drafted = llm.complete([{"type": "text", "text": DISTILL}], user).strip()

    bible = vdir / "bible.md"
    text = bible.read_text()
    pattern = re.compile(r"<!-- VOICE-SPECIFIC:START -->.*?<!-- VOICE-SPECIFIC:END -->", re.S)
    block = f"<!-- VOICE-SPECIFIC:START -->\n{drafted}\n<!-- VOICE-SPECIFIC:END -->"
    if pattern.search(text):
        text = pattern.sub(lambda _: block, text)
    else:
        text = block + "\n\n" + text
    (vdir / "bible.before-distill.md").write_text(bible.read_text())
    bible.write_text(text)
    return bible


LEDGER_TEMPLATE = """# Story ledger

## Cast
- (name: what they are, what they want, where they are now, who they're tangled up with)

## World
- (places, factions, rules of magic or technology, money, religion)

## Threads
- (open setups, promises, mysteries, debts; note the chapter each was planted in)

## Timeline
- (one line per chapter)
"""


def new_book(path: Path, import_dir: Path | None = None) -> list[Path]:
    """Create a book folder. Existing chapters are copied in, in name order, as ch01.md, ch02.md..."""
    chapters = path / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    ledger = path / "ledger.md"
    if not ledger.exists():
        ledger.write_text(LEDGER_TEMPLATE)
    imported = []
    if import_dir:
        files = sorted(f for f in import_dir.iterdir() if f.suffix.lower() in {".md", ".txt"})
        start = len(list(chapters.glob("ch*.md")))
        for i, f in enumerate(files, start + 1):
            dest = chapters / f"ch{i:02d}.md"
            dest.write_text(f.read_text())
            imported.append(dest)
    return imported
