"""Chapter writer + cleanup layers, driven by a voice folder.

A voice folder holds:
  voice.yaml   settings, linter overrides
  bible.md     the distilled style bible
  samples/     the author's own pages (few-shot examples + fingerprint source)

Flow for a chapter:
  WRITER (bible + samples + never-list + fingerprint targets loaded up front)
    → lint + fingerprint check
    → POLISH only the flagged spans, only if anything is flagged
    → save chapter, update the story ledger
"""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

import yaml

from .fingerprint import compare, derive_targets
from .lint import PHRASES, lint, paragraphs
from .threes import find_threes
from .llm import LLM, extract_prose

# --------------------------------------------------------------------------- voice


def load_voice(path: str | Path) -> dict:
    path = Path(path)
    vdir = path if path.is_dir() else path.parent
    cfg = path / "voice.yaml" if path.is_dir() else path
    voice = yaml.safe_load(cfg.read_text()) or {}
    voice["_dir"] = vdir

    bible = vdir / "bible.md"
    voice["_bible"] = bible.read_text() if bible.exists() else voice.get("voice", "")

    samples = sorted((vdir / "samples").glob("*.md")) if (vdir / "samples").exists() else []
    voice["_sample_list"] = [(p.stem, p.read_text()) for p in samples]
    voice["_samples"] = "\n\n".join(t for _, t in voice["_sample_list"])

    techniques = sorted((vdir / "techniques").glob("*.md")) if (vdir / "techniques").exists() else []
    voice["_techniques"] = [(p.stem, p.read_text()) for p in techniques]

    if voice["_samples"]:
        # Anything the generic AI-ism list flags that the author actually writes is their voice, not a tell.
        evidenced = {m.group(0).lower() for _, pat in PHRASES for m in re.finditer(pat, voice["_samples"], re.I)}
        voice["allowed_phrases"] = sorted(set(voice.get("allowed_phrases") or []) | evidenced)
        insp = voice.get("inspired") or {}
        voice["_inspired_stats"] = inspired_stats(vdir) if insp else None
        voice["_targets"] = {
            **derive_targets(voice["_samples"], inspired=voice["_inspired_stats"],
                             blend=float(insp.get("blend", 0)), locked=tuple(insp.get("locked") or ())),
            **(voice.get("targets") or {}),
        }
    else:
        voice["_targets"] = voice.get("targets") or {}
    return voice


def inspired_stats(vdir: Path) -> dict | None:
    """Measure the inspired-by author from inspired/*.md (kept local, never sent to the model).

    Only the numbers are saved, to inspired_fingerprint.json, which is what gets committed.
    """
    import json

    from .fingerprint import measure

    files = sorted((vdir / "inspired").glob("*.md")) if (vdir / "inspired").exists() else []
    cache = vdir / "inspired_fingerprint.json"
    if files:
        stats = measure("\n\n".join(f.read_text() for f in files))
        stats.pop("words", None)
        stats = {k: round(v, 3) for k, v in stats.items()}
        cache.write_text(json.dumps(stats, indent=1) + "\n")
        return stats
    return json.loads(cache.read_text()) if cache.exists() else None


def fingerprint_block(voice: dict) -> str:
    t = voice["_targets"]
    if not t:
        return ""
    rows = "\n".join(f"- {k}: {lo:g}–{hi:g}" for k, (lo, hi) in t.items())
    return f"<voice_fingerprint>\nMeasured from the author's pages. Your chapter will be measured against these ranges.\n{rows}\n</voice_fingerprint>"


def voice_system(voice: dict, role: str) -> list[dict]:
    """Stable system prompt (cached): role, bible, samples, fingerprint."""
    samples = "\n\n".join(f'<sample id="{sid}">\n{text}\n</sample>' for sid, text in voice["_sample_list"])
    text = (
        f"{role}\n\n<style_bible>\n{voice['_bible']}\n</style_bible>\n\n"
        f"<author_samples>\nThe author's own published pages. This is what correct sounds like. "
        f"Imitate the habits, never reuse the sentences, names or events.\n{samples}\n</author_samples>\n\n"
        + (
            "<technique_studies>\nOriginal passages written to show the inspired-by author's moves (style bible "
            "section 5) carried out in this author's mechanics. Study how the moves are done; never reuse "
            "their sentences, names or situations.\n"
            + "\n\n".join(f'<study id="{sid}">\n{text}\n</study>' for sid, text in voice["_techniques"])
            + "\n</technique_studies>\n\n"
            if voice.get("_techniques") else ""
        )
        + f"{fingerprint_block(voice)}"
    )
    return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]


# --------------------------------------------------------------------------- prompts

WRITER = """You are the author of this novel, writing its next chapter. Every word you write must read as
the author's own: their rhythm, punctuation dialect, habits of attention, and humour, as set out in the
style bible and shown in the samples. The book is for adults, and you write its sex and violence as
explicitly as the author does. All characters in sexual content are adults.

Before you write, plan the chapter's beats privately. While drafting, keep the bible's mechanics in
your hands, not your head: drop inherited subjects, shift hard between the clipped and surge gears,
use ' -' for cut-offs and '...' for trailing off, and never use an em dash. Break the rule of three:
pairs, fours and lopsided lists, never stacked threes. Let some sentences be plain and some paragraphs
end flat. Build the plot per the bible's "Story shape". Before you finish, reread your draft against
sections 6 to 8 of the bible and fix anything that fails them.

Don't caricature the voice. Imitators overdo an author's signatures: too much subject-dropping, every
sentence clipped, fragments everywhere. Match the rates in the voice fingerprint, not your impression
of them. Most sentences in the samples are ordinary, complete and unshowy; the signatures are seasoning.
Work in the inspired-by moves from bible section 5 (moves 4 to 11) the way the technique studies do.

Return only the chapter inside <prose></prose>. Start with the chapter heading. No notes and no
commentary."""

EDITOR = """You are the author's line editor. You revise only the flagged problems in the passage and
leave everything else exactly as written: plot, events, dialogue meaning, names, POV, tense, heat,
violence and profanity stay as they are. Every fix must land in the author's voice per the style bible.
Do not add beats, summaries or morals. Do not soften. Return the full passage inside <prose></prose>
and nothing else."""

STORY_EDITOR = """You are a developmental editor. You read a draft chapter for story shape, not sentences.
Machine-written fiction gives itself away in its plot shape: themes spelled out, tidy single-track
plots, flat escalation, linear time, protagonists whose choices cost nothing, and antagonists who exist
only to be beaten. Check the draft for each of these:

1. ESCALATION: does each scene beat raise the stakes or turn the situation? Name any beat that only repeats the previous one's tension.
2. THEME: is any meaning, lesson or feeling stated outright, in narration or a speech, when the action already showed it? Quote it.
3. TRACKS: is there a second pressure running under the main one (a relationship strain, a secret, a debt, a body problem)? If the chapter is single-track, propose one, drawn from the ledger.
4. COST: does the protagonist make at least one choice that is morally grey or costs him something he can't get back? If not, propose where.
5. TIME: is there texture beyond straight chronology, like a memory intrusion, a jump, or an aftermath shown before its cause? Propose one if it would earn its place.
6. OTHERS' WANTS: does every named character want something of their own and act on it, rather than reacting to the protagonist?
7. SURPRISE: name the most predictable beat and an alternative the reader won't see coming but will believe.
8. INSPIRED-BY MOVES: the style bible (section 5, moves 4-6) requires in every chapter at least one
   needling banter exchange closed by a wry one-line verdict, one passage of scheming interiority
   (odds, distances, costs, fallbacks), and one important exchange that turns on what isn't said.
   For each one missing or weak, say where it belongs and sketch it.

Return 3 to 7 numbered revision notes, the most important first. Each note gives the exact passage
and a concrete fix. Skip any check the draft already passes. Do not rewrite the chapter."""

STORY_REVISE = """Apply the editor's notes to the chapter. Change what the notes require, keep everything else.
Every new or changed line must be in the author's voice per the style bible. Return the full revised
chapter inside <prose></prose>, starting with the chapter heading. No commentary."""

LEDGER = """You maintain the story ledger for a novel in progress: a compact, factual reference the
author's ghostwriter reads before every chapter. Update it with what the new chapter establishes or
changes. Keep these sections: Cast (name, what they are, current state and location, relationships),
World (places, factions, gods, magic rules introduced), Threads (open setups, promises, mysteries,
with chapter numbers), Timeline (one line per chapter). Remove what is resolved. Stay terse.
Return the full updated ledger inside <ledger></ledger>."""

# Generic one-category rewrite layers, for refining outside drafts (the `refine` command).
LAYERS = {
    "scrub": "JOB: diction and stock phrasing. Replace every flagged phrase with something specific to this "
             "scene and character, or cut it. Don't replace one cliché with another; plain beats clever.",
    "structure": "JOB: rhythm and construction. Fix the flagged structure and bring the passage onto the voice "
                 "fingerprint: punctuation dialect, sentence-length gears, subject-dropping, paragraph size.",
    "voice": "JOB: voice match. Rewrite so it reads as if the author of the samples wrote it: their rhythm, "
             "punctuation, dialogue tagging, what they notice and what they skip. Same events, same content.",
}


# --------------------------------------------------------------------------- helpers


def chunk(text: str, words: int) -> list[str]:
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


def issues(text: str, voice: dict) -> tuple[str, list[str]]:
    """Flagged spans (for the prompt) and whole-text fingerprint deviations."""
    rep = lint(text, voice)
    flagged = rep.for_prompt() if rep.findings or rep.flags else ""
    dev = compare(text, voice["_targets"])
    if any(d.startswith(("threes", "polysyndeton3", "triple_beats", "stair_paragraphs")) for d in dev):
        found = find_threes(text)
        flagged += "\n\nGroups of three in this passage (break most of them; keep only the one or two that earn it):\n"
        flagged += "\n".join(f"- [{t.kind}] “{t.text.strip()}”" for t in found)
    return flagged.strip(), dev


def tail(text: str, words: int) -> str:
    w = text.split(" ")
    return text if len(w) <= words else "…" + " ".join(w[-words:])


# --------------------------------------------------------------------------- engine


class Engine:
    def __init__(self, voice: dict, llm: LLM, out_dir: Path, chunk_words: int = 1500, log=print):
        self.voice, self.llm, self.out, self.chunk_words, self.log = voice, llm, out_dir, chunk_words, log
        self.out.mkdir(parents=True, exist_ok=True)
        self.step = 0

    def _save(self, name: str, text: str) -> None:
        self.step += 1
        (self.out / f"{self.step:02d}_{name}.md").write_text(text)
        rep = lint(text, self.voice)
        dev = compare(text, self.voice["_targets"])
        report = rep.to_markdown() + ("\n\n**Off-voice:**\n" + "\n".join(f"- {d}" for d in dev) if dev else "")
        (self.out / f"{self.step:02d}_{name}.report.md").write_text(report)
        self.log(f"  {self.step:02d} {name:<10} {rep.words:>6} words  {len(rep.findings):>3} flagged spans  "
                 f"{len(dev)} off-voice stats")

    def _rewrite(self, job: str, text: str, deviations: list[str]) -> str:
        system = voice_system(self.voice, EDITOR)
        out, prev = [], ""
        dev = "\n".join(f"- {d}" for d in deviations) or "(none)"
        for piece in chunk(text, self.chunk_words):
            flagged, _ = issues(piece, self.voice)
            if job != "voice" and not flagged and not deviations:
                out.append(piece)
                continue
            user = (
                f"{job}\n\n"
                + (f"<preceding_text_do_not_return>\n{prev}\n</preceding_text_do_not_return>\n\n" if prev else "")
                + f"<flagged_spans>\n{flagged or '(none)'}\n</flagged_spans>\n\n"
                + f"<off_voice_for_whole_chapter>\n{dev}\n</off_voice_for_whole_chapter>\n\n"
                + f"<passage>\n{piece}\n</passage>"
            )
            revised = extract_prose(self.llm.complete(system, user))
            out.append(revised)
            prev = "\n\n".join(paragraphs(revised)[-3:])
        return "\n\n".join(out)

    def polish(self, text: str, passes: int = 2) -> str:
        """Targeted cleanup: runs only while something is flagged."""
        for i in range(passes):
            flagged, dev = issues(text, self.voice)
            if not flagged and not dev:
                self.log("  clean, no polish needed" if i == 0 else "  clean")
                break
            job = ("JOB: fix the flagged spans and bring the passage back onto the voice fingerprint. "
                   "Touch nothing that isn't flagged unless a fingerprint fix requires it.")
            text = self._rewrite(job, text, dev)
            self._save(f"polish{i + 1}", text)
        return text

    # ---- chapter mode

    def write_chapter(self, brief: str, ledger: str, previous: str, number: int, words: int) -> str:
        user = (
            f"<story_ledger>\n{ledger or '(first chapter — no ledger yet)'}\n</story_ledger>\n\n"
            + (f"<end_of_previous_chapter>\n{tail(previous, 1500)}\n</end_of_previous_chapter>\n\n" if previous else "")
            + f"<chapter_brief>\nChapter {number}. About {words} words.\n{brief}\n</chapter_brief>"
        )
        text = extract_prose(self.llm.complete(voice_system(self.voice, WRITER), user))
        self._save("draft", text)
        return text

    def story_pass(self, text: str, ledger: str, brief: str) -> str:
        """Developmental edit: critique the plot shape, then revise against the notes."""
        notes = self.llm.complete(
            voice_system(self.voice, STORY_EDITOR),
            f"<story_ledger>\n{ledger or '(none)'}\n</story_ledger>\n\n<brief>\n{brief}\n</brief>\n\n<chapter>\n{text}\n</chapter>",
        )
        (self.out / f"{self.step + 1:02d}_story-notes.md").write_text(notes)
        user = f"<editor_notes>\n{notes}\n</editor_notes>\n\n<chapter>\n{text}\n</chapter>"
        text = extract_prose(self.llm.complete(voice_system(self.voice, STORY_REVISE), user))
        self._save("story", text)
        return text

    def update_ledger(self, ledger: str, chapter: str, number: int) -> str:
        reply = self.llm.complete(
            [{"type": "text", "text": LEDGER}],
            f"<current_ledger>\n{ledger or '(empty)'}\n</current_ledger>\n\n<chapter number=\"{number}\">\n{chapter}\n</chapter>",
        )
        m = re.search(r"<ledger>\s*(.*?)\s*</ledger>", reply, re.S)
        return (m.group(1) if m else reply).strip()

    # ---- refine mode (outside drafts)

    def refine(self, text: str, layers: list[str], passes: int = 2) -> str:
        self._save("input", text)
        for name in layers:
            _, dev = issues(text, self.voice)
            text = self._rewrite(LAYERS[name], text, dev)
            self._save(name, text)
        return self.polish(text, passes)


def run_dir(root: Path) -> Path:
    return root / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
