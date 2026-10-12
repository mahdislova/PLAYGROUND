"""voicepress CLI.

  python -m voicepress chapter "brief..."      # write the next chapter of the book
  python -m voicepress lint FILE                # free: AI-isms + off-voice stats, no API
  python -m voicepress fingerprint              # show the voice's measured targets
  python -m voicepress refine FILE              # pull an outside draft into the voice
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from .fingerprint import compare, measure
from .lint import lint
from .pipeline import load_voice, run_dir

HERE = Path(__file__).resolve().parent.parent


def _brief(arg: str) -> str:
    return Path(arg[1:]).read_text() if arg.startswith("@") else arg


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="voicepress")
    ap.add_argument("--voice", default=str(HERE / "voices" / "voice-a"), help="voice folder")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("lint", help="flag AI-isms and off-voice stats (no API calls)")
    p.add_argument("file")
    p.add_argument("--top", type=int, default=40, help="flagged spans to print (0 = all)")

    sub.add_parser("fingerprint", help="print the voice's measured target ranges")

    p = sub.add_parser("chapter", help="write the next chapter")
    p.add_argument("brief", help="what happens in this chapter, or @path/to/brief.md")
    p.add_argument("--book", default=str(HERE / "book"), help="book folder: chapters/ and ledger.md")
    p.add_argument("--words", type=int, help="target length (default from voice.yaml)")
    p.add_argument("--passes", type=int, default=2, help="max polish passes")

    p = sub.add_parser("refine", help="run an outside draft through the layers")
    p.add_argument("file")
    p.add_argument("--layers", default="voice", help="comma list of scrub,structure,voice (polish always runs)")
    p.add_argument("--passes", type=int, default=2)
    p.add_argument("--out", default=str(HERE / "runs"))

    for sp in sub.choices.values():
        sp.add_argument("--chunk-words", type=int, default=1500)

    a = ap.parse_args(argv)
    voice = load_voice(a.voice)

    if a.cmd == "fingerprint":
        for k, (lo, hi) in voice["_targets"].items():
            print(f"{k:24} {lo:>7g} – {hi:g}")
        return

    if a.cmd == "lint":
        text = Path(a.file).read_text()
        md = lint(text, voice).to_markdown()
        if a.top:
            head, _, table = md.partition("| line |")
            rows = table.splitlines()
            md = head + ("| line |" + "\n".join(rows[: a.top + 2]) if table else "")
            if len(rows) > a.top + 2:
                md += f"\n\n…{len(rows) - a.top - 2} more (use --top 0 for all)"
        print(md)
        dev = compare(text, voice["_targets"])
        print("\n**Off-voice:**\n" + "\n".join(f"- {d}" for d in dev) if dev else "\n**On-voice** (fingerprint in range)")
        return

    from .llm import LLM  # imported late so lint/fingerprint work without the SDK
    from .pipeline import Engine

    llm = LLM(voice.get("model", "claude-opus-5-5"), voice.get("effort", "high"))
    log = lambda s: print(s, file=sys.stderr)  # noqa: E731

    if a.cmd == "refine":
        out = run_dir(Path(a.out))
        eng = Engine(voice, llm, out, a.chunk_words, log)
        log(f"run → {out}")
        text = eng.refine(Path(a.file).read_text(), [x for x in a.layers.split(",") if x], a.passes)
        (out / "FINAL.md").write_text(text)
        log(f"done → {out / 'FINAL.md'}")
        return

    # chapter
    book = Path(a.book)
    chapters = book / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)
    ledger_path = book / "ledger.md"
    existing = sorted(chapters.glob("ch*.md"))
    number = int(re.search(r"\d+", existing[-1].stem).group()) + 1 if existing else 1
    previous = existing[-1].read_text() if existing else ""
    ledger = ledger_path.read_text() if ledger_path.exists() else ""
    words = a.words or (voice.get("chapter") or {}).get("words", 4500)

    out = book / "runs" / f"ch{number:02d}-{run_dir(Path('.')).name}"
    eng = Engine(voice, llm, out, a.chunk_words, log)
    log(f"chapter {number} → working files in {out}")
    text = eng.write_chapter(_brief(a.brief), ledger, previous, number, words)
    text = eng.polish(text, a.passes)

    final = chapters / f"ch{number:02d}.md"
    final.write_text(text + "\n")
    log("  updating ledger")
    ledger_path.write_text(eng.update_ledger(ledger, text, number) + "\n")
    m = measure(text)
    log(f"done → {final}  ({m['words']} words)")


if __name__ == "__main__":
    main()
