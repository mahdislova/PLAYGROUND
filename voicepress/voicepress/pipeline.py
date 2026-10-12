"""The layer stack: draft → scrub → structure → voice → (repeat scrub/structure if still dirty).

Each layer is one focused rewrite. Narrow jobs beat one giant "make it sound human"
prompt, which mostly swaps one set of tics for another.
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import yaml

from .lint import lint, paragraphs
from .llm import LLM, extract_prose

EDITOR = """You are a line editor working on a novelist's manuscript. You revise only what your
current job covers and leave everything else alone: plot, events, dialogue meaning, names,
POV, tense, and content stay exactly as they are. The author writes for adults; keep their
heat, violence and profanity at the level you find it. Do not add summaries, morals,
or new beats. Do not soften. Return the full revised passage inside <prose></prose> and nothing else."""

LAYERS = {
    "scrub": """JOB: diction and cliché.
Replace every flagged stock phrase with something specific to THIS scene and THIS character —
an object, a sensation, an action — or cut it if the sentence stands without it.
Kill: stock body language (jaw tightening, eyes darkening, breath they didn't know they held),
"something shifted", "the weight of", "the kind of X that Y", "it wasn't X, it was Y",
"a flicker/whisper of", vague abstractions doing the work concrete detail should do.
Do not replace one cliché with a fresher cliché. Plain is better than clever.""",

    "structure": """JOB: rhythm and construction.
- Vary sentence length hard: some long sentences that run on momentum, some flat medium ones.
  Not every paragraph ends on a short punchy line.
- Collapse stacked fragments ("Fast. Professional. Cold.") into real sentences; keep at most one per scene.
- Break reflexive triads (X, Y, and Z) — use two items, or four, or one.
- Cut em-dashes down to the few that earn it; use commas, periods, or restructure.
- Cut similes by half; keep only those drawn from the POV character's own world.
- Merge one-line paragraphs that aren't doing dramatic work.
- Don't open consecutive paragraphs with the same word.""",

    "voice": """JOB: voice match.
Rewrite the passage so it reads as if the author of the SAMPLES wrote it. Study the samples for:
sentence rhythm, paragraph length, how scenes open and close, punctuation habits, vocabulary
register, how dialogue is tagged, what they notice and what they skip. Imitate the habits,
not the content. Where the style profile and the samples disagree, the samples win.""",
}


def load_style(path: str | Path) -> dict:
    path = Path(path)
    style = yaml.safe_load(path.read_text()) or {}
    texts = []
    for s in style.get("samples") or []:
        p = (path.parent / s)
        if p.exists():
            texts.append(p.read_text())
    style["_samples"] = "\n\n---\n\n".join(texts)
    return style


def style_block(style: dict) -> str:
    rules = "\n".join(f"- {r}" for r in style.get("rules") or [])
    out = f"<style_profile>\n{style.get('voice', '').strip()}\n\nRules:\n{rules}\n</style_profile>"
    if style.get("_samples"):
        out += f"\n\n<samples>\n{style['_samples'][:60000]}\n</samples>"
    return out


def chunk(text: str, words: int) -> list[str]:
    """Split on paragraph boundaries into ~`words`-sized pieces."""
    chunks, cur, n = [], [], 0
    for p in re.split(r"\n\s*\n", text.strip()):
        cur.append(p)
        n += len(p.split())
        if n >= words:
            chunks.append("\n\n".join(cur))
            cur, n = [], 0
    if cur:
        chunks.append("\n\n".join(cur))
    return chunks


class Pipeline:
    def __init__(self, style: dict, llm: LLM, out_dir: Path, chunk_words: int = 1500, log=print):
        self.style, self.llm, self.out, self.chunk_words, self.log = style, llm, out_dir, chunk_words, log
        self.out.mkdir(parents=True, exist_ok=True)
        self.step = 0

    def _save(self, name: str, text: str) -> None:
        self.step += 1
        (self.out / f"{self.step:02d}_{name}.md").write_text(text)
        rep = lint(text, self.style)
        (self.out / f"{self.step:02d}_{name}.lint.md").write_text(rep.to_markdown())
        self.log(f"  {self.step:02d} {name:<10} {rep.words:>6} words  {len(rep.findings):>4} findings  "
                 f"{rep.per_1k:5.1f}/1k  flags={len(rep.flags)}")

    def draft(self, brief: str) -> str:
        system = EDITOR.replace("line editor working on", "ghostwriter drafting") + "\n\n" + style_block(self.style)
        text = extract_prose(self.llm.complete(system, f"Write this, in the author's voice:\n\n{brief}"))
        self._save("draft", text)
        return text

    def layer(self, name: str, text: str) -> str:
        system = EDITOR + "\n\n" + style_block(self.style)
        out, prev_tail = [], ""
        for piece in chunk(text, self.chunk_words):
            rep = lint(piece, self.style)
            if name != "voice" and not rep.findings and not rep.flags:
                out.append(piece)  # already clean for this job
                continue
            user = (
                f"{LAYERS[name]}\n\n"
                + (f"<preceding_text_for_continuity_do_not_return>\n{prev_tail}\n</preceding_text_for_continuity_do_not_return>\n\n" if prev_tail else "")
                + f"<flagged>\n{rep.for_prompt()}\n</flagged>\n\n<passage>\n{piece}\n</passage>"
            )
            revised = extract_prose(self.llm.complete(system, user))
            out.append(revised)
            prev_tail = "\n\n".join(paragraphs(revised)[-3:])
        result = "\n\n".join(out)
        self._save(name, result)
        return result

    def run(self, text: str, layers: list[str], extra_passes: int = 1) -> str:
        self._save("input", text)
        for name in layers:
            text = self.layer(name, text)
        for _ in range(extra_passes):
            rep = lint(text, self.style)
            if rep.per_1k < 2 and not rep.flags:
                break
            text = self.layer("scrub", text)
            text = self.layer("structure", text)
        (self.out / "FINAL.md").write_text(text)
        return text


def run_dir(root: Path) -> Path:
    return root / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
