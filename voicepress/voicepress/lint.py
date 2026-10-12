"""Deterministic AI-ism scanner. No model calls — just patterns and rhythm stats.

Every finding carries the exact span so the rewrite layers can target it
instead of re-rolling the whole passage.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from dataclasses import dataclass, field

# --- Phrase-level tells -------------------------------------------------------
# (category, regex). Case-insensitive. Keep these specific: a pattern that fires
# on ordinary prose is worse than no pattern.
PHRASES: list[tuple[str, str]] = [
    # Stock diction
    ("diction", r"\bdelv(e|es|ed|ing)\b"),
    ("diction", r"\btapestr(y|ies)\b"),
    ("diction", r"\b(a )?testament to\b"),
    ("diction", r"\bpalpable\b"),
    ("diction", r"\bunwavering\b"),
    ("diction", r"\bnestled\b"),
    ("diction", r"\bbustling\b"),
    ("diction", r"\ba symphony of\b"),
    ("diction", r"\b(intricate|multifaceted|myriad)\b"),
    ("diction", r"\bbeacon of\b"),
    ("diction", r"\bozone\b"),
    ("diction", r"\b(coppery|copper) (tang|taste)\b"),
    ("diction", r"\bmingl(ed|ing) with\b"),
    # Stock body language / interiority
    ("cliche", r"\bbreath (he|she|they|I) didn['’]?t know\b"),
    ("cliche", r"\b(jaw|jaws) (tightened|clenched|set)\b"),
    ("cliche", r"\beyes (darkened|softened|narrowed)\b"),
    ("cliche", r"\bghost of a (smile|grin)\b"),
    ("cliche", r"\bbarely (above|more than) a whisper\b"),
    ("cliche", r"\bsomething (shifted|changed|broke|cracked|loosened)\b"),
    ("cliche", r"\bsomething (in|behind) (his|her|their|my) (chest|eyes|gaze)\b"),
    ("cliche", r"\b(sent|send|sending) (a )?shivers?\b"),
    ("cliche", r"\bthe weight of\b"),
    ("cliche", r"\bhung in the air\b"),
    ("cliche", r"\b(the )?air (was )?thick with\b"),
    ("cliche", r"\bthe silence stretched\b"),
    ("cliche", r"\bfor a long moment\b"),
    ("cliche", r"\ba beat\b"),
    ("cliche", r"\bin that moment\b"),
    ("cliche", r"\bcouldn['’]?t help but\b"),
    ("cliche", r"\b(smirk|smirked|smirking)\b"),
    ("cliche", r"\bpadded (across|over|into|to)\b"),
    ("cliche", r"\b(a )?flicker of\b"),
    ("cliche", r"\bwhisper of\b"),
    # Stock fiction moves (reader reports + the stock phrasing a detector flagged in our own example chapter)
    ("cliche", r"\b(the )?(world|time|everything) (slowed|narrowed|tilted|fell away|stood still|stopped)\b"),
    ("cliche", r"\blet(ting)? the silence\b"),
    ("cliche", r"\b(smiled|smile|laughed|laugh)\. (it|this) was (not|no) a\b"),
    ("cliche", r"\b(her|his|their) voice,? (sharp|soft|low|thick|rough|tight|heavy) with\b"),
    ("cliche", r"\bvoice like\b"),
    ("cliche", r"\b(and )?somewhere (behind|above|below|beyond|in the distance|nearby)\b"),
    ("cliche", r"\b(sounding|sounded|looked|looking) almost (apologetic|amused|sad|bored)\b"),
    ("cliche", r"\bwith the (patient|quiet|idle|mild) (interest|amusement|curiosity) of\b"),
    ("cliche", r"\b(a|the) (quiet|soft) (certainty|resolve|strength|intensity|menace)\b"),
    ("cliche", r"\b(eyes|gaze) (that held|holding) (something|a promise|secrets)\b"),
    ("cliche", r"\bsmelled of ozone|tasted of copper|scent of rain\b"),
    ("cliche", r"\bor rather\b"),
    ("cliche", r"\bevery last one\b"),
    # Construction tells
    ("construction", r"\bthe kind of \w+ (that|who|where)\b"),
    ("construction", r"\b(it|this|that) (wasn['’]?t|isn['’]?t|was not|is not) [^.;:!?]{1,40}[.;,—-]+\s*(it|this|that) (was|is)\b"),
    ("construction", r"\bnot because\b[^.]{1,60}\bbut because\b"),
    ("construction", r"\bNot (a|an|the) [^.!?\n]{1,30}\. (A|An|The|Just) "),
    ("construction", r"\bmaybe,? just maybe\b"),
    ("construction", r"\band yet\b"),
    ("construction", r"\ba reminder (that|of)\b"),
    ("construction", r"\bsomehow\b"),
]

SIMILE = re.compile(r"\b(like a|like an|like the|as if|as though)\b", re.I)
EM_DASH = re.compile(r"—|(?<!-)--(?!-)| – ")
# "X, Y, and Z" — the reflexive triad.
TRIAD = re.compile(r"\b[\w'-]+(?: [\w'-]+){0,3}, [\w'-]+(?: [\w'-]+){0,3},? and [\w'-]+", re.I)
# Two or more consecutive short fragment sentences: "Fast. Professional."
FRAGMENT_RUN = re.compile(r"(?:(?<=[.!?] )|^)(?:[A-Z][\w'-]*(?: [\w'-]+){0,2}[.!](?: +|$)){2,}", re.M)
STOCK_BEAT = re.compile(
    r"^(?:(?:He|She|They|It|[A-Z][a-z]+) (?:looked up|went down|didn['’]t care|froze|went still|didn['’]t move|"
    r"swallowed|exhaled|nodded slowly|said nothing)|Too (?:much|soon|late)\. Too (?:much|soon|late)|"
    r"(?:And then|Then) (?:silence|nothing)|Silence fell|Nothing happened|Time stopped)\.?$"
)
def _opener(sentence: str) -> str:
    """First word, ignoring articles/conjunctions, which repeat on purpose in anaphora."""
    toks = re.findall(r"[\w'’]+", sentence)
    w = toks[0].lower() if toks else ""
    return "" if w in {"the", "a", "an", "and", "but", "or", "so", "then", "no", "not"} else w


SENT_SPLIT = re.compile(r"(?<=[.!?])[\"”’)]*\s+(?=[\"“‘(]?[A-Z*])")


@dataclass
class Finding:
    category: str
    text: str
    line: int
    note: str = ""


@dataclass
class Report:
    words: int
    findings: list[Finding] = field(default_factory=list)
    stats: dict[str, float] = field(default_factory=dict)
    flags: list[str] = field(default_factory=list)

    @property
    def per_1k(self) -> float:
        return len(self.findings) / max(self.words, 1) * 1000

    def by_category(self) -> Counter:
        return Counter(f.category for f in self.findings)

    def to_markdown(self) -> str:
        out = [
            f"**{self.words} words · {len(self.findings)} findings · {self.per_1k:.1f}/1k**",
            "",
            "| stat | value |",
            "|---|---|",
        ]
        out += [f"| {k} | {v:.2f} |" for k, v in self.stats.items()]
        if self.flags:
            out += ["", "**Over threshold:**"] + [f"- {f}" for f in self.flags]
        if self.findings:
            out += ["", "| line | category | text | note |", "|---|---|---|---|"]
            for f in self.findings:
                snippet = f.text.replace("|", "\\|").replace("\n", " ")[:90]
                out.append(f"| {f.line} | {f.category} | {snippet} | {f.note} |")
        return "\n".join(out)

    def for_prompt(self, limit: int = 120) -> str:
        """Compact list a rewrite layer can act on."""
        lines = [f"- [{f.category}] line {f.line}: “{f.text.strip()}” {f.note}".rstrip() for f in self.findings[:limit]]
        lines += [f"- [global] {flag}" for flag in self.flags]
        return "\n".join(lines) or "(none)"


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def _strip_markup(text: str) -> str:
    return re.sub(r"[*_#>`]", "", text)


def sentences(text: str) -> list[str]:
    body = _strip_markup(text)
    out = []
    for para in re.split(r"\n\s*\n", body):
        para = " ".join(para.split())
        if para:
            out += [s for s in SENT_SPLIT.split(para) if s.strip()]
    return out


def paragraphs(text: str) -> list[str]:
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip() and not p.strip().startswith("#")]


def lint(text: str, style: dict | None = None) -> Report:
    style = style or {}
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    th = {
        "em_dashes_per_1k": 6, "similes_per_1k": 8, "triads_per_1k": 4,
        "fragment_runs_per_1k": 3, "min_sentence_length_cv": 0.55,
        "max_one_line_paragraph_ratio": 0.35, **(style.get("thresholds") or {}),
    }
    allowed = [a.lower() for a in style.get("allowed_phrases") or []]
    disabled = set(style.get("disabled_checks") or [])
    patterns = [(c, p) for c, p in PHRASES if c not in disabled]
    patterns += [("banned", rf"\b{re.escape(p)}\b") for p in style.get("banned_phrases") or []]
    patterns += [("forbidden", re.escape(p)) for p in style.get("forbidden_strings") or []]

    words = len(re.findall(r"\b[\w'’-]+\b", text))
    k = max(words, 1) / 1000
    rep = Report(words=words)

    for cat, pat in patterns:
        for m in re.finditer(pat, text, re.I):
            if any(a in m.group(0).lower() for a in allowed):
                continue
            rep.findings.append(Finding(cat, m.group(0), _line_of(text, m.start())))

    # Repeated 4-grams: the model's verbal tics within one piece.
    toks = re.findall(r"[a-z'’]+", text.lower())
    grams = Counter(" ".join(toks[i:i + 4]) for i in range(len(toks) - 3))
    stop = {"the", "a", "of", "and", "to", "in", "he", "she", "it", "was", "his", "her", "that", "on", "at"}
    for g, n in grams.most_common(40):
        if n >= 3 and len(set(g.split()) - stop) >= 2:
            m = re.search(r"[^a-z'’]+".join(map(re.escape, g.split())), text, re.I)
            rep.findings.append(Finding("repetition", g, _line_of(text, m.start()) if m else 0, f"×{n}"))

    # Paragraph openers repeated back-to-back ("He ... / He ... / He ...").
    paras = paragraphs(text)
    openers = [re.findall(r"[\w'’]+", _strip_markup(p))[:1] for p in paras]
    run = 1
    for i in range(1, len(openers)):
        if openers[i] and openers[i] == openers[i - 1]:
            run += 1
            if run == int(style.get("max_same_opener", 3)):
                idx = text.find(paras[i])
                rep.findings.append(Finding("rhythm", paras[i][:60], _line_of(text, idx),
                                            f"{run}+ paragraphs in a row open with “{openers[i][0]}”"))
        else:
            run = 1

    # Stock short beats: one-line paragraphs that carry no information, just drama.
    if "stock_beats" not in disabled:
        for p in paras:
            if STOCK_BEAT.match(_strip_markup(p).strip()):
                rep.findings.append(Finding("stock-beat", p, _line_of(text, text.find(p)),
                                            "dramatic filler beat; make it carry a concrete fact or cut it"))

    # Narration opening the same way over and over ("He drew. He turned. He looked up. He ...").
    narr = [x for x in sentences(text) if not re.match(r"^[\"“‘']", x)]
    run = 1
    for i in range(1, len(narr)):
        same = _opener(narr[i]) and _opener(narr[i]) == _opener(narr[i - 1])
        run = run + 1 if same else 1
        if run == 4:
            rep.findings.append(Finding("rhythm", " / ".join(narr[i - 3:i + 1])[:90], _line_of(text, text.find(narr[i][:30])),
                                        f"4 narration sentences in a row open with “{_opener(narr[i])}”"))

    for m in FRAGMENT_RUN.finditer(text) if "fragments" not in disabled else ():
        rep.findings.append(Finding("fragments", m.group(0).strip(), _line_of(text, m.start()), "stacked fragments"))

    sents = sentences(text)
    lens = [len(s.split()) for s in sents] or [0]
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0.0
    one_liners = sum(1 for p in paras if len(sentences(p)) <= 1) / max(len(paras), 1)

    rep.stats = {
        "em_dashes_per_1k": len(EM_DASH.findall(text)) / k,
        "similes_per_1k": len(SIMILE.findall(text)) / k,
        "triads_per_1k": len(TRIAD.findall(text)) / k,
        "fragment_runs_per_1k": len(FRAGMENT_RUN.findall(text)) / k,
        "sentence_length_mean": mean,
        "sentence_length_cv": cv,
        "one_line_paragraph_ratio": one_liners,
    }
    s = rep.stats
    for key in ("em_dashes_per_1k", "similes_per_1k", "triads_per_1k", "fragment_runs_per_1k"):
        if key.split("_")[0] in disabled or key.replace("_per_1k", "") in disabled:
            continue
        if s[key] > th[key]:
            rep.flags.append(f"{key} = {s[key]:.1f} (limit {th[key]})")
    if s["sentence_length_cv"] < th["min_sentence_length_cv"]:
        rep.flags.append(f"sentence lengths too uniform: cv {cv:.2f} (want ≥ {th['min_sentence_length_cv']})")
    if one_liners > th["max_one_line_paragraph_ratio"] and "one_line_paragraphs" not in disabled:
        rep.flags.append(f"one-line paragraphs {one_liners:.0%} (limit {th['max_one_line_paragraph_ratio']:.0%})")

    rep.findings.sort(key=lambda f: f.line)
    return rep
