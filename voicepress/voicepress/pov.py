"""Deep third-person checks: how close the narration sits to the POV character's head, and whether
the dialogue does work.

Brent Weeks's third limited runs without italics. The narration slides from camera to the
character's own idiom ("Just walk, Kip. Places to be.") and back without tags, so the reader is
inside a biased, funny, fallible mind. Flat machine prose sits outside: it reports emotion from the
outside ("He looked very tired"), filters every perception through "she saw / she felt", fences
thought off in italics, and lets dialogue trade information with stage directions ("She waited.")
between the lines.

Each check below finds one of those habits. `interior_per_1k` measures the opposite: narration
sentences that can only be the character talking to themselves.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

PRONOUN = r"(?:he|she|they|I|we)"
FILTER = re.compile(
    rf"\b{PRONOUN} (?:could )?(?:saw|see|heard|hear|felt|feel|noticed|watched|realised|realized|wondered|"
    rf"thought|knew|sensed|seemed to|found (?:herself|himself|themselves))\b", re.I)
EXTERNAL_EMOTION = re.compile(
    r"\b(?:looked|seemed|appeared|sounded)\s+(?:very\s+|so\s+|a little\s+|quite\s+|rather\s+|suddenly\s+)?"
    r"(?:tired|sad|angry|frightened|afraid|worried|nervous|happy|pleased|scared|upset|confused|surprised|"
    r"relieved|anxious|unhappy|exhausted|hurt|guilty|lost|grim|shaken)\b", re.I)
STAGE_BEAT = re.compile(
    r"^(?:[A-Z][a-z]+ )?(?:He|She|They|[A-Z][a-z]+) (?:waited|nodded|shrugged|smiled|sighed|paused|"
    r"swallowed|blinked|frowned|said nothing|didn't (?:say anything|answer|reply)|looked at (?:him|her|them|it)"
    r"|looked away|looked up|looked down)(?: [a-z]+){0,3}\.$")
ONOMATOPOEIA = re.compile(r"^[a-z]+(?:[-, ]+[a-z]+){0,4}[.!]?$", re.I)
# Narration that can only be the character's own voice: interjections, self-address, verdicts,
# rhetorical questions, mid-thought corrections.
INTERIOR = re.compile(
    r"^(?:Of course|Well|Oh|Right|Good|Fine|Hell|Damn|Gods?|God|Great|Perfect|Wonderful|Brilliant|"
    r"Typical|Naturally|Obviously|Wait|No|Yes|Sure|So much for|Not that|Which was|Never mind|Idiot|Fool|"
    r"Stupid|Lovely|Marvellous|Splendid|Bloody|Christ|Lord|Too late|Fair enough|All right|Nothing|"
    r"Some \w+|What a|Look on the bright side|Just|Careful|Don't|Funny|Close|Practice|There it was|"
    r"Let (?:him|her|them)|Idiot|Liar|Bastard|Hello|Typical|Sod|Bugger)\b"
    r"|^[A-Z][\w' ]{0,30}, (?:girl|boy|lad|love|[A-Z][a-z]+)\.$", re.I)


SELF_ADDRESS = re.compile(r", (?:[A-Z][a-z]+|girl|boy|lad|love)[.!]$")
SECOND_PERSON = re.compile(r"\byou(?:'d|'ll|r|rself)?\b", re.I)
IMPERATIVE = re.compile(r"^(?:Don't|Get|Look|Stop|Steady|Shut up|Careful|Keep|Go on|Let|Think|Breathe|Come on)\b")


@dataclass
class PovFinding:
    category: str
    text: str
    line: int
    note: str


def _narration(paragraph: str) -> str:
    """The paragraph with quoted speech removed."""
    return re.sub(r"[\"“][^\"”]*[\"”]", " ", paragraph)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", text) if s.strip()]


def _is_dialogue(p: str) -> bool:
    return bool(re.match(r"^[\"“]", p))


def _spoken(p: str) -> str:
    return " ".join(re.findall(r"[\"“]([^\"”]*)[\"”]", p))


def analyse(text: str) -> tuple[dict[str, float], list[PovFinding]]:
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    lines = text.split("\n")
    paras = [(i + 1, l.strip()) for i, l in enumerate(lines)
             if l.strip() and not l.startswith("#") and l.strip() not in ("* * *", "***")]
    words = max(len(re.findall(r"\b[\w'’-]+\b", text)), 1)
    k = words / 1000
    out: list[PovFinding] = []
    interior = filters = 0

    for ln, p in paras:
        narr = _narration(p)
        for m in FILTER.finditer(narr):
            filters += 1
            out.append(PovFinding("filter", m.group(0), ln,
                                  "filter verb holds the reader outside; give the thing seen/felt directly"))
        for m in EXTERNAL_EMOTION.finditer(narr):
            out.append(PovFinding("outside-emotion", m.group(0), ln,
                                  "emotion reported from outside; give the POV character's read of it, in their words"))
        if re.fullmatch(r"\*[^*]+\*", p):
            continue  # a POV / dateline tag, not thought
        for m in re.finditer(r"\*([^*]+)\*", narr):
            inner = m.group(1).strip()
            if len(inner.split()) >= 3 and not ONOMATOPOEIA.match(inner):
                out.append(PovFinding("italic-thought", inner[:60], ln,
                                      "drop the italics; let the thought run in the narration (deep third)"))
        if STAGE_BEAT.match(narr.strip()) and len(narr.split()) <= 7:
            out.append(PovFinding("stage-beat", narr.strip(), ln,
                                  "empty stage direction; replace with what the POV character makes of the moment"))
        for s in _sentences(narr):
            if INTERIOR.match(s) or s.endswith("?") or SELF_ADDRESS.search(s) or SECOND_PERSON.search(s) \
                    or IMPERATIVE.match(s):
                interior += 1

    # Dialogue: echo answers and long bare ping-pong.
    prev_spoken, bare_run, run_start = "", 0, 0
    for ln, p in paras:
        if _is_dialogue(p):
            spoken = _spoken(p)
            narr_words = len(_narration(p).split())
            sw = re.findall(r"[a-z']+", spoken.lower())
            if 1 <= len(sw) <= 2 and prev_spoken and all(w in prev_spoken.lower() for w in sw) \
                    and sw[0] not in ("yes", "no", "what", "why", "who", "oh", "well"):
                out.append(PovFinding("echo-line", spoken, ln,
                                      "echo reply repeats the last speaker's word; answer the subtext or cut it"))
            bare_run = bare_run + 1 if narr_words <= 3 else 0
            if bare_run == 1:
                run_start = ln
            if bare_run == 7:
                out.append(PovFinding("ping-pong", p[:50], run_start,
                                      "7+ bare lines in a row; put the POV character's read between two of them"))
            prev_spoken = spoken
        else:
            bare_run = 0

    stats = {
        "filter_per_1k": filters / k,
        "interior_per_1k": interior / k,
        "italic_thoughts": float(sum(f.category == "italic-thought" for f in out)),
        "outside_emotion": float(sum(f.category == "outside-emotion" for f in out)),
        "stage_beats": float(sum(f.category == "stage-beat" for f in out)),
        "echo_lines": float(sum(f.category == "echo-line" for f in out)),
    }
    return stats, out


TARGETS = {
    # (min, max) per chapter or per 1k. Interior floor is the deep-third target, set above the
    # author's own samples so the narration leans into the POV head.
    "filter_per_1k": (0.0, 3.0),
    "interior_per_1k": (6.0, 30.0),
    "italic_thoughts": (0, 1),
    "outside_emotion": (0, 0),
    "stage_beats": (0, 2),
    "echo_lines": (0, 1),
}

ADVICE = {
    "filter_per_1k": "Too many 'she saw / he felt / she knew'. Cut the filter and give the thing itself.",
    "interior_per_1k": "Narration is sitting outside the character. Let them talk to themselves in the narration: "
                       "verdicts, jokes, self-address ('Just walk, Kip.'), rhetorical questions, corrections.",
    "italic_thoughts": "Drop italics for thought; the narration is already in their head.",
    "outside_emotion": "Never report the POV character's feelings, or how others look, from the outside. "
                       "Give the POV character's interpretation, biased, in their idiom.",
    "stage_beats": "Too many 'She waited. He nodded.' beats. Replace with what the POV character thinks of the pause.",
    "echo_lines": "Echo replies ('Alive.') are a machine tic. Answer the question under the question, deflect, joke, or cut.",
}


def compare(stats: dict[str, float]) -> list[str]:
    msgs = []
    for key, (lo, hi) in TARGETS.items():
        v = stats[key]
        if v < lo or v > hi:
            msgs.append(f"{key} = {v:.2f}, deep-third range {lo}–{hi}. {ADVICE[key]}")
    return msgs
