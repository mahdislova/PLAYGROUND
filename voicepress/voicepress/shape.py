"""Paragraph shape: does the page look like a printed novel or like web fiction?

Machine prose and web serials paragraph by formula: blocks of three or four sentences, with a
single line pulled out on its own every few paragraphs for emphasis ("Two fingers and a thumb.").
Printed novels don't. A paragraph runs as long as the thought does, sometimes half a page; dialogue
comes in quick exchanges; a line alone on the page is saved for the one moment in a chapter that
earns it.

These checks look at narration paragraphs only (dialogue paragraphs are naturally short).
"""
from __future__ import annotations

import re
import statistics
from dataclasses import dataclass


@dataclass
class ShapeFinding:
    category: str
    text: str
    line: int
    note: str


def _paras(text: str) -> list[tuple[int, str]]:
    out = []
    for i, block in enumerate(text.split("\n")):
        b = block.strip()
        if not b or b.startswith("#") or b in ("* * *", "***") or re.fullmatch(r"\*[^*]+\*", b):
            continue
        out.append((i + 1, b))
    return out


def _sentences(p: str) -> int:
    return max(1, len(re.findall(r"[.!?…](?:[\"”’*)]*)(?:\s|$)", p)))


def _is_dialogue(p: str) -> bool:
    return p.startswith(('"', "“"))


def analyse(text: str) -> tuple[dict[str, float], list[ShapeFinding]]:
    paras = _paras(text)
    narr = [(ln, p) for ln, p in paras if not _is_dialogue(p)]
    if len(narr) < 4:
        return {}, []
    words = [len(p.split()) for _, p in narr]
    sents = [_sentences(p) for _, p in narr]
    mean = statistics.mean(words)
    out: list[ShapeFinding] = []

    # Isolated emphasis lines: a short narration paragraph standing alone between other paragraphs.
    for i, (ln, p) in enumerate(narr):
        if sents[i] <= 2 and words[i] <= 12:
            out.append(ShapeFinding("lone-line", p[:60], ln,
                                    "line set alone for emphasis; fold it into the paragraph it belongs to"))

    # Formula blocks: long runs of paragraphs all in the same 3-4 sentence, 30-80 word band.
    run = 0
    for i, (ln, p) in enumerate(narr):
        if 2 <= sents[i] <= 5 and 25 <= words[i] <= 80:
            run += 1
            if run == 5:
                out.append(ShapeFinding("block-run", p[:60], narr[i - 4][0],
                                        "5 same-size paragraphs in a row; let one run long or merge two"))
        else:
            run = 0

    stats = {
        "narr_para_mean": mean,
        "narr_para_cv": statistics.pstdev(words) / mean if mean else 0.0,
        "lone_line_share": sum(f.category == "lone-line" for f in out) / len(narr),
        "longest_para": float(max(words)),
        "mid_band_share": sum(1 for w in words if 25 <= w <= 80) / len(words),
    }
    return stats, out


# Book shape, not web shape. Set from printed literary and epic fantasy narration, not from samples.
TARGETS = {
    "narr_para_mean": (55.0, 140.0),
    "narr_para_cv": (0.6, 2.0),
    "lone_line_share": (0.0, 0.08),
    "longest_para": (150.0, 600.0),
    "mid_band_share": (0.0, 0.5),
}

ADVICE = {
    "narr_para_mean": "Narration paragraphs are too short. Let a paragraph run as long as the thought: "
                      "fold reactions, memories and verdicts into the paragraph of the action that caused them.",
    "narr_para_cv": "Paragraphs are all one size. Vary hard: one runs half a page, the next is two lines.",
    "lone_line_share": "Too many lines set alone for emphasis. Keep at most one or two a chapter, for the moment "
                       "that earns it; fold the rest into their paragraphs.",
    "longest_para": "No paragraph ever opens out. Give the chapter at least one long paragraph (150+ words) "
                    "where memory, scene and feeling run together.",
    "mid_band_share": "Most paragraphs sit in the same 25 to 80 word band. That evenness is the web-fiction look; "
                      "break the band both ways.",
}


def compare(stats: dict[str, float]) -> list[str]:
    msgs = []
    for k, (lo, hi) in TARGETS.items():
        if k in stats and not (lo <= stats[k] <= hi):
            msgs.append(f"{k} = {stats[k]:.2f}, book range {lo}–{hi}. {ADVICE[k]}")
    return msgs
