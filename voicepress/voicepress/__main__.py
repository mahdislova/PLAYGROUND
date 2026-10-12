"""voicepress CLI.

  python -m voicepress lint  FILE            # free, no API: AI-ism report
  python -m voicepress refine FILE           # run an existing draft through the layers
  python -m voicepress write  "brief..."     # draft from a brief, then run the layers
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .lint import lint
from .pipeline import Pipeline, load_style, run_dir

HERE = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(prog="voicepress")
    ap.add_argument("--style", default=str(HERE / "style.yaml"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("lint", help="scan a file for AI-isms (no API calls)")
    p.add_argument("file")
    p.add_argument("--top", type=int, default=40, help="findings to print")

    for name in ("refine", "write"):
        p = sub.add_parser(name)
        p.add_argument("input", help="file to refine" if name == "refine" else "brief text, or @path/to/brief.md")
        p.add_argument("--layers", default="scrub,structure,voice")
        p.add_argument("--extra-passes", type=int, default=1)
        p.add_argument("--chunk-words", type=int, default=1500)
        p.add_argument("--out", default=str(HERE / "runs"))

    a = ap.parse_args(argv)
    style = load_style(a.style)

    if a.cmd == "lint":
        rep = lint(Path(a.file).read_text(), style)
        md = rep.to_markdown()
        if a.top:
            head, _, table = md.partition("| line |")
            rows = table.splitlines()
            md = head + "| line |" + "\n".join(rows[: a.top + 2])
            if len(rows) > a.top + 2:
                md += f"\n\n…{len(rows) - a.top - 2} more (use --top 0 for all)"
        print(md)
        return

    from .llm import LLM  # imported late so `lint` works without the SDK
    llm = LLM(style.get("model", "claude-opus-5-5"), style.get("effort", "high"))
    out = run_dir(Path(a.out))
    pipe = Pipeline(style, llm, out, a.chunk_words, log=lambda s: print(s, file=sys.stderr))
    print(f"run → {out}", file=sys.stderr)

    if a.cmd == "write":
        brief = Path(a.input[1:]).read_text() if a.input.startswith("@") else a.input
        text = pipe.draft(brief)
    else:
        text = Path(a.input).read_text()

    pipe.run(text, [l for l in a.layers.split(",") if l], a.extra_passes)
    print(f"done → {out / 'FINAL.md'}", file=sys.stderr)


if __name__ == "__main__":
    main()
