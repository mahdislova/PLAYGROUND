"""Over-polish detector.

The AI-ism linter catches stock phrasing. This catches the opposite fault: prose where every beat
is optimised for impact. Too many quotable images, too many reverse-and-qualify moves, aphorisms,
and dialogue so efficient nobody ever just answers the question. Every rate is calibrated against
the author's own pages through the fingerprint, and locked there.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .lint import _line_of, paragraphs, sentences

# "the way a man rests his hand on a dog he isn't sure of" - the generalising simile
THE_WAY = re.compile(r"\bthe way (?:a|an|you|someone|somebody|men|people|one)\b[^.!?\"”]*", re.I)
# Correction / reversal: "not forgiveness, nothing so warm as that, but", "not X, but Y", ". Or rather"
REVERSAL = re.compile(
    r"\bnot [^.;!?]{1,40}, (?:nothing|not) [^.;!?]{1,40}, but\b"
    r"|\bnot [^.;!?]{2,40}, but\b"
    r"|\bnothing so \w+ as\b"
    r"|\. Or (?:had|rather|not|perhaps)\b"
    r"|\bNo\. Not\b",
    re.I,
)
# Any figurative comparison
IMAGE = re.compile(r"\b(like a|like an|like the|as if|as though|the way a|the way an|as \w+ as (?:a|an|the)|\w+ as a \w+)\b", re.I)
APHORISM_START = re.compile(r"^(The dead|Men|A man|Nobody|No one|People|Every man|The living|Words|Death|You never|You can't)\b")
FILLER = re.compile(
    r"\b(well|um|uh|I mean|I suppose|I think|maybe|sort of|you know|just|right|look|anyway|"
    r"I don't know|I guess|aye|yeah|hmm|oh)\b", re.I)
UTTERANCE = re.compile(r"[\"“]([^\"”]{2,400})[\"”]")


def _body(text: str) -> str:
    return re.sub(r"^#[^\n]*$", "", re.sub(r"<!--.*?-->", "", text, flags=re.S), flags=re.M)


def _aphorisms(text: str) -> list[str]:
    out = []
    for s in sentences(text):
        s2 = s.strip("\"“”")
        if APHORISM_START.match(s2) and re.search(r"\b(is|are|has|have|do|does|never|always|can't|won't)\b", s2) \
                and not re.search(r"\b(was|were|had|did)\b", s2):
            out.append(s2)
    return out


def rates(text: str) -> dict[str, float]:
    t = _body(text)
    k = max(len(re.findall(r"\b[\w'’-]+\b", t)), 1) / 1000
    long_paras = [p for p in paragraphs(t) if len(p.split()) >= 25]
    utts = UTTERANCE.findall(t)
    return {
        "the_way_similes_per_1k": len(THE_WAY.findall(t)) / k,
        "reversals_per_1k": len(REVERSAL.findall(t)) / k,
        "aphorisms_per_1k": len(_aphorisms(t)) / k,
        "image_paragraph_share": sum(1 for p in long_paras if IMAGE.search(p)) / max(len(long_paras), 1),
        "plain_dialogue_share": sum(1 for u in utts if FILLER.search(u)) / max(len(utts), 1),
    }


@dataclass
class Polished:
    kind: str
    text: str
    line: int


def find_polish(text: str) -> list[Polished]:
    """Every over-polished line, for the polish layer and the author-pass worksheet."""
    out = [Polished("the-way simile", m.group(0), _line_of(text, m.start())) for m in THE_WAY.finditer(text)]
    out += [Polished("reversal", m.group(0), _line_of(text, m.start())) for m in REVERSAL.finditer(text)]
    out += [Polished("aphorism", a, _line_of(text, text.find(a[:30]))) for a in _aphorisms(_body(text))]
    for p in paragraphs(text):
        for m in IMAGE.finditer(p):
            s = next((x for x in sentences(p) if m.group(0) in x), m.group(0))
            out.append(Polished("image", s, _line_of(text, text.find(p))))
    seen, uniq = set(), []
    for x in sorted(out, key=lambda x: x.line):
        if (x.kind, x.text) not in seen:
            seen.add((x.kind, x.text))
            uniq.append(x)
    return uniq


def author_pass(text: str, title: str = "") -> str:
    """A worksheet for the author: the lines most likely to read as engineered, to rewrite by hand.

    This is the step that makes the chapter the author's. The engine can't do it for them.
    """
    found = find_polish(text)
    order = {"the-way simile": 0, "aphorism": 1, "reversal": 2, "image": 3}
    found.sort(key=lambda x: (order.get(x.kind, 9), x.line))
    utts = [(m.group(1), _line_of(text, m.start())) for m in UTTERANCE.finditer(text)]
    zingers = [(u, ln) for u, ln in utts if len(u.split()) >= 8 and not FILLER.search(u)]
    lines = [f"# Author pass{': ' + title if title else ''}", "",
             "Go through this before the chapter goes anywhere. For each line: rewrite it the way *you* "
             "would say it, make it plainer, or cut it. Keep the few you'd genuinely have written.", "",
             "## Polished lines (images, maxims, reversals)", ""]
    lines += [f"- [ ] line {x.line} · {x.kind}: {x.text.strip()[:200]}" for x in found] or ["- (none)"]
    lines += ["", "## Dialogue that lands too cleanly", "",
              "Pick a few and make them ordinary: a hedge, a literal answer, a repeat, a line that misses.", ""]
    lines += [f"- [ ] line {ln}: \"{u.strip()[:160]}\"" for u, ln in zingers[:15]] or ["- (none)"]
    lines += ["", "## Add yourself", "",
              "- [ ] One beat only you would write: a joke, a memory, a detail from your own life or research.",
              "- [ ] One place where a character says something dull, wrong, or beside the point.",
              "- [ ] Read one scene aloud and change every line you trip on.", ""]
    return "\n".join(lines)
