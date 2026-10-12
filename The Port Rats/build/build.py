"""Build THE PORT RATS: parse manuscript -> chapter HTML fragments (shared by EPUB, PDF, DOCX)."""
import re, subprocess, json, sys, html

SRC = sys.argv[1]
OUT = sys.argv[2]

NUM = ("Zero One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Thirteen Fourteen "
       "Fifteen Sixteen Seventeen Eighteen Nineteen Twenty").split()

text = open(SRC, encoding="utf-8").read()
parts = re.split(r"^## \*\*Chapter (\w+(?:-\w+)?): (.+?)\*\*\s*$", text, flags=re.M)
chapters = []
for i in range(1, len(parts), 3):
    word, title, body = parts[i], parts[i + 1].strip(), parts[i + 2]
    body = re.sub(r"^---\s*$", "\n\nSCENEBREAKMARK\n\n", body, flags=re.M)
    frag = subprocess.run(["pandoc", "-f", "markdown-smart", "-t", "html5", "--wrap=none"],
                          input=body, capture_output=True, text=True, check=True).stdout
    frag = frag.replace("<p>SCENEBREAKMARK</p>", "<hr class=\"scene\"/>")
    frag = frag.replace("<hr />", "<hr class=\"scene\"/>")
    chapters.append({"num": word, "title": title, "html": frag.strip()})

TOKEN = re.compile(r"(<[^>]+>)|([^<\s]+)|(\s+)")


def dress_opener(p_inner):
    """Split first paragraph into drop-cap letter + small-caps lead-in (first ~4 words) + rest."""
    # leading quote marks ride with the initial
    m = re.match(r"^([“‘\"']*)(\w)", p_inner)
    if not m:
        return None, "", p_inner
    initial = m.group(1) + m.group(2)
    rest = p_inner[m.end():]
    out, words, depth = [], 0, 0
    pos = 0
    for tm in TOKEN.finditer(rest):
        tag, word, space = tm.groups()
        if tag:
            depth += -1 if tag.startswith("</") else 1
            out.append(tag)
        elif word:
            if words >= 4 and depth == 0:
                break
            out.append(word)
            words += 1
            # stop early at a clause end so the lead reads naturally
            if re.search(r"[.,;:!?—]$", word) and words >= 2 and depth == 0:
                pos = tm.end()
                break
        else:
            if words >= 4 and depth == 0:
                break
            out.append(space)
        pos = tm.end()
    lead = "".join(out)
    tail = rest[pos:]
    # if the lead swallowed a trailing space, push it to the tail
    if lead.endswith(" "):
        lead, tail = lead.rstrip(), " " + tail
    return initial, lead, tail


for c in chapters:
    paras = re.split(r"(?=<p>|<hr class=\"scene\"/>)", c["html"])
    blocks = []
    after_break = True
    first = True
    for b in paras:
        b = b.strip()
        if not b:
            continue
        if b.startswith("<hr"):
            blocks.append({"t": "scene"})
            after_break = True
            continue
        inner = re.sub(r"^<p>|</p>$", "", b)
        if first:
            ini, lead, tail = dress_opener(inner)
            blocks.append({"t": "opener", "initial": ini, "lead": lead, "tail": tail})
            first = False
        else:
            blocks.append({"t": "flush" if after_break else "p", "html": inner})
        after_break = False
    c["blocks"] = blocks
    c["numword"] = c["num"]

json.dump(chapters, open(OUT, "w"), ensure_ascii=False, indent=1)
print(len(chapters), "chapters;", sum(len(c["blocks"]) for c in chapters), "blocks")
for c in chapters:
    o = c["blocks"][0]
    print(c["num"], "|", o["initial"], "|", o["lead"], "|", o["tail"][:30])
