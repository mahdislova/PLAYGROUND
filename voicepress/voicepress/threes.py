"""Rule-of-three detector, at every level a reader feels it.

Machine prose groups things in threes reflexively: three adjectives, three clauses, three
fragments, three one-line paragraphs, a word said three times. Any one is fine. The tell is
the density, and the way the threes stack until the prose reads like it's on a metronome.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .lint import _line_of, paragraphs, sentences

ITEM = r"[\w'’-]+(?: [\w'’-]+){0,4}"
# "A, B, and C" / "A, B and C" / "A, B, C." (asyndeton) inside one sentence
SHORT = r"[\w'’-]+(?: [\w'’-]+){0,2}"
LIST3 = re.compile(rf"\b{ITEM}, {ITEM},? (?:and|or) {ITEM}\b|\b{SHORT}, {SHORT}, {SHORT}[.!?]", re.I)
# Direct address and dialogue tags make comma runs that aren't lists.
NOT_A_LIST = re.compile(r"\b(friend|brother|sister|sir|lord|lady|my \w+|said|asked|laughed|growled|hissed|whispered)\b|\?|\b[A-Z][a-z]+ [A-Z][a-z]+\b")
# "A and B and C" (polysyndeton)
POLY3 = re.compile(rf"\b{ITEM} and {ITEM} and {ITEM}\b", re.I)
# "ringing, ringing, ringing" / "again and again and again"
WORD3 = re.compile(r"\b(\w+)\b(?:[,.]? (?:and )?\1\b){2}", re.I)


@dataclass
class Three:
    kind: str
    text: str
    line: int


def find_threes(text: str) -> list[Three]:
    out: list[Three] = []
    for kind, pat in (("list", LIST3), ("polysyndeton", POLY3), ("word x3", WORD3)):
        for m in pat.finditer(text):
            if kind == "list" and NOT_A_LIST.search(m.group(0)):
                continue
            out.append(Three(kind, m.group(0), _line_of(text, m.start())))

    # Three short sentences in a row (≤6 words each), the triple drumbeat: "Too much. Too soon. He hadn't called them."
    for para in paragraphs(text):
        ss = sentences(para)
        lens = [len(s.split()) for s in ss]
        i = 0
        while i + 2 < len(ss):
            if all(n <= 6 for n in lens[i:i + 3]) and (i + 3 >= len(ss) or lens[i + 3] > 6):
                out.append(Three("triple beat", " ".join(ss[i:i + 3]), _line_of(text, text.find(ss[i]))))
                i += 3
            else:
                i += 1

    # Three one-line paragraphs in a row: the staircase.
    paras = paragraphs(text)
    i = 0
    while i + 2 < len(paras):
        trio = paras[i:i + 3]
        if all(len(sentences(p)) == 1 and len(p.split()) <= 10 for p in trio):
            nxt = paras[i + 3] if i + 3 < len(paras) else ""
            if not (len(sentences(nxt)) == 1 and len(nxt.split()) <= 10):
                out.append(Three("3-step paragraphs", " / ".join(trio), _line_of(text, text.find(trio[0]))))
                i += 3
                continue
        i += 1

    out.sort(key=lambda t: t.line)
    return out


def threes_per_1k(text: str) -> float:
    words = len(re.findall(r"\b[\w'’-]+\b", text))
    return len(find_threes(text)) / max(words, 1) * 1000


def rates(text: str) -> dict[str, float]:
    words = len(re.findall(r"\b[\w'’-]+\b", text))
    k = max(words, 1) / 1000
    th = find_threes(text)
    count = lambda kind: sum(t.kind == kind for t in th) / k  # noqa: E731
    return {
        "threes_per_1k": len(th) / k,
        "polysyndeton3_per_1k": count("polysyndeton"),
        "triple_beats_per_1k": count("triple beat"),
        "stair_paragraphs_per_1k": count("3-step paragraphs"),
    }
