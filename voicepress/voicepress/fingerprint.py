"""Measure a voice from its samples, then check new prose against it.

The linter asks "does this look machine-made?". This module asks the sharper
question: "does this look like *this author*?" — same punctuation dialect, same
sentence-length spread, same paragraph size, same habits.
"""

from __future__ import annotations

import re
import statistics

from .lint import sentences
from .threes import rates as three_rates

WORD = re.compile(r"\b[\w'’-]+\b")
CONTRACTION = re.compile(r"\b\w+['’](?:s|t|d|ll|re|ve|m)\b", re.I)
LY = re.compile(r"\b\w{3,}ly\b", re.I)
LY_NOT_ADVERB = {"only", "early", "family", "reply", "supply", "lonely", "lovely", "ugly", "holy", "belly",
                 "bully", "jelly", "silly", "rally", "fly", "july", "italy", "friendly", "likely", "daily",
                 "elderly", "deadly", "kindly", "costly", "curly", "surly", "burly", "comely", "lowly", "stately"}
# Sentence opening on a verb with the subject carried over: "Looked up at him." "Stepped inside, picked up..."
SUBJECTLESS = re.compile(
    r"^(?:[A-Z][a-z]{2,}(?:ed|ped|ted)|Felt|Saw|Took|Gave|Bent|Drove|Made|Held|Fought|Began|Found|Threw|Drew"
    r"|Knew|Let|Kept|Spun|Struck|Stood|Sat|Ran|Shook|Caught|Swung|Hit|Cut|Rose|Fell|Bit|Thought|Heard|Brought|Sank)\b"
    r"(?! (?:to|by|with) (?:the|a|an|his|her|their)\b)"
)
NOT_VERBS = {"Red", "Bed", "Shed", "Sped", "Fred", "Ned", "Wed", "Need", "Speed", "Seed", "Indeed", "Hundred",
             "Sacred", "Naked", "Wicked", "Rugged", "Kindred", "Wretched", "Crooked", "Ragged", "Beloved"}


def _body(text: str) -> str:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"^\s*(#.*|\*Words:.*|---|\* \* \*|\*\*\*)\s*$", "", text, flags=re.M)
    return re.sub(r"[*_`>]", "", text)


def measure(text: str) -> dict[str, float]:
    body = _body(text)
    words = len(WORD.findall(body))
    k = max(words, 1) / 1000
    sents = sentences(body)
    lens = [len(s.split()) for s in sents] or [0]
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    plens = [len(p.split()) for p in paras] or [0]
    ly = [w for w in LY.findall(body) if w.lower() not in LY_NOT_ADVERB]
    subjless = [s for s in sents if SUBJECTLESS.match(s) and s.split()[0].rstrip(",.") not in NOT_VERBS]
    return {
        "words": words,
        "em_dash_per_1k": body.count("—") / k,
        "spaced_hyphen_per_1k": len(re.findall(r"\s-(?:\s|$)|\s-[”\"]", body, re.M)) / k,
        "ellipsis_per_1k": len(re.findall(r"…|\.\.\.|\. \. \.", body)) / k,
        "semicolon_per_1k": body.count(";") / k,
        "contractions_per_1k": len(CONTRACTION.findall(body)) / k,
        "ly_adverbs_per_1k": len(ly) / k,
        "similes_per_1k": len(re.findall(r"\b(like a|like an|as if|as though)\b", body, re.I)) / k,
        "subjectless_per_1k": len(subjless) / k,
        "sentence_mean": statistics.mean(lens),
        "sentence_sd": statistics.pstdev(lens),
        "short_sentence_share": sum(n <= 6 for n in lens) / len(lens),
        "long_sentence_share": sum(n >= 30 for n in lens) / len(lens),
        "paragraph_mean": statistics.mean(plens),
        **three_rates(text),
    }


# How to fix each stat when it's out of range — written as instructions for the polish layer.
ADVICE = {
    "em_dash_per_1k": ("", "Remove every em dash. Use ' - ' for a hard cut-off, '...' for trailing off, otherwise a comma or period."),
    "spaced_hyphen_per_1k": ("Add a hard cut-off or two: speech or thought broken off mid-word with ' -'.", "Fewer ' -' cut-offs."),
    "ellipsis_per_1k": ("Let a character trail off or revise mid-sentence with '...' (often followed by 'well', 'oh', 'right').", "Fewer ellipses."),
    "semicolon_per_1k": ("", "Fewer semicolons; use a period."),
    "contractions_per_1k": ("Narration and dialogue are too stiff; contract where people would.", "Narration is too loose; uncontract some narration (dialogue can stay)."),
    "ly_adverbs_per_1k": ("", "Cut -ly adverbs; let the verb carry it."),
    "similes_per_1k": ("", "Cut similes; keep only the best one or two."),
    "subjectless_per_1k": ("Drop the subject more often when it carries over: 'Looked up at him.' 'Stepped inside, picked up his sword.'", "Fewer subjectless sentences."),
    "sentence_mean": ("Sentences are too short across the board; let action and sex run long.", "Sentences run long across the board; add clipped beats."),
    "sentence_sd": ("Rhythm is too even. Push both gears: stacks of short declaratives, and long comma-chained participial sentences of 30+ words.", "Rhythm is erratic; settle some mid-length lines."),
    "short_sentence_share": ("More short beats (6 words or fewer).", "Too many short beats; join some."),
    "long_sentence_share": ("Add long comma-chained sentences (30+ words) in action, sex, or emotional surges.", "Fewer runaway sentences."),
    "threes_per_1k": ("", "Too many groups of three. Break most into pairs, fours, or lopsided groups (two short items and a long trailing one); let some lists trail off. Keep only the threes that earn it."),
    "polysyndeton3_per_1k": ("", "Too many 'X and Y and Z' chains. Keep one for a real surge; recast the rest."),
    "triple_beats_per_1k": ("", "Too many three-short-sentence drumbeats. Fold one of the three into its neighbour, or let the beat run to two or four."),
    "stair_paragraphs_per_1k": ("", "Too many runs of exactly three one-line paragraphs. Merge one into the paragraph next to it."),
    "paragraph_mean": ("Paragraphs are too short; let some breathe.", "Paragraphs are too long; break them. The short paragraph is the unit of rhythm."),
}


# Rhythm stats are tight identity markers; punctuation counts swing more chapter to chapter.
SLACK = {"threes_per_1k": 0.15, "polysyndeton3_per_1k": 0.5, "triple_beats_per_1k": 0.25, "stair_paragraphs_per_1k": 0.6, "sentence_sd": 0.22, "sentence_mean": 0.25, "short_sentence_share": 0.2, "paragraph_mean": 0.35}


def derive_targets(sample_text: str, slack: float = 0.45, inspired: dict | None = None,
                   blend: float = 0.0, locked: tuple[str, ...] = ()) -> dict[str, list[float]]:
    """Target ranges from the voice's own samples, with slack because a chapter isn't the whole corpus.

    With `inspired` stats and a `blend` weight, every stat not in `locked` is centred part-way
    toward the inspired-by author. Locked stats (the author's identity markers) stay pure.
    """
    m = measure(sample_text)
    targets = {}
    for key, v in m.items():
        if key == "words":
            continue
        if inspired and key in inspired and key not in locked:
            v = (1 - blend) * v + blend * inspired[key]
        slack_k = SLACK.get(key, slack)
        if v == 0:
            targets[key] = [0.0, 0.0]
        else:
            targets[key] = [round(v * (1 - slack_k), 2), round(v * (1 + slack_k), 2)]
    return targets


def compare(text: str, targets: dict[str, list[float]]) -> list[str]:
    """Human/LLM-readable list of deviations from the voice."""
    m = measure(text)
    out = []
    if m["words"] < 300:
        return out  # too short to judge statistically
    for key, (lo, hi) in targets.items():
        v = m.get(key)
        if v is None:
            continue
        low_fix, high_fix = ADVICE.get(key, ("Increase.", "Decrease."))
        if v < lo and low_fix:
            out.append(f"{key} = {v:.2f}, voice range {lo}–{hi}. {low_fix}")
        elif v > hi:
            out.append(f"{key} = {v:.2f}, voice range {lo}–{hi}. {high_fix}")
    return out
