"""Build The Green Gallows, Episode One, as an EPUB 3 (with EPUB 2 NCX fallback).

Usage:  python3 books/green-gallows/build_epub.py
Output: books/green-gallows/the-green-gallows-episode-one.epub
"""
from __future__ import annotations

import html
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "the-green-gallows-episode-one.epub"
TITLE = "The Green Gallows"
SUBTITLE = "Episode One: The Exhibition"
AUTHOR = "Draft"
BOOK_ID = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "green-gallows-episode-one"))
CHAPTERS = ["00-prologue.md", "01-nathaniel.md", "02-alice.md", "03-nathaniel.md", "04-coda.md"]

CSS = """
@namespace epub "http://www.idpf.org/2007/ops";
html { font-size: 100%; }
body { font-family: Georgia, "Palatino Linotype", "Book Antiqua", serif; line-height: 1.5;
       margin: 0 5%; text-align: justify; hyphens: auto; -webkit-hyphens: auto; }
p { margin: 0; text-indent: 1.4em; orphans: 2; widows: 2; }
p.first, p.after-break { text-indent: 0; }
p.first::first-line { font-variant: small-caps; letter-spacing: 0.04em; }
h1.chapter { font-weight: normal; text-align: center; font-size: 1.5em; letter-spacing: 0.06em;
             margin: 3.5em 0 0.4em; page-break-before: always; break-before: page; }
h1.chapter span.label { display: block; font-size: 0.6em; letter-spacing: 0.3em;
                        text-transform: uppercase; color: #6b6b6b; margin-bottom: 0.6em; }
p.pov { text-align: center; text-indent: 0; font-style: italic; color: #4a6b55;
        margin: 0 0 2.6em; letter-spacing: 0.08em; }
p.break { text-align: center; text-indent: 0; margin: 1.2em 0; color: #4a6b55; letter-spacing: 0.8em; }
em { font-style: italic; }
.title-page { text-align: center; margin-top: 30%; }
.title-page h1 { font-weight: normal; font-size: 2.4em; letter-spacing: 0.12em; margin: 0; }
.title-page .rule { color: #4a6b55; margin: 1em 0; letter-spacing: 0.6em; }
.title-page .sub { font-style: italic; font-size: 1.1em; margin: 0; text-indent: 0; text-align: center; }
.note { margin-top: 20%; font-size: 0.9em; }
.note p { text-indent: 0; margin-bottom: 0.8em; text-align: left; }
nav ol { list-style: none; padding-left: 0; }
nav li { margin: 0.5em 0; }
nav a { text-decoration: none; color: inherit; }
"""

LABELS = {"Prologue": "Prologue", "Chapter One": "One", "Chapter Two": "Two",
          "Chapter Three": "Three", "Coda": "Coda"}


def typeset(text: str) -> str:
    """Escape, then curl quotes, ellipses and the voice's spaced-hyphen cut-offs."""
    s = html.escape(text, quote=False)
    s = s.replace("...", "\u2026")
    # double quotes alternate within a paragraph
    out, open_q = [], True
    for ch in s:
        if ch == '"':
            out.append("\u201c" if open_q else "\u201d")
            open_q = not open_q
        else:
            out.append(ch)
    s = "".join(out)
    # single quotes: opening after start/space/open-paren/opening double quote, else apostrophe/closing
    s = re.sub(r"(^|[\s(\u201c])'", "\\1\u2018", s)
    s = s.replace("'", "\u2019")
    # keep cut-off hyphen glued to the word before it, and tidy the space before a closing quote
    s = re.sub(r" -(\s*)\u201d", "\u00a0-\u201d", s)
    s = re.sub(r" - ", "\u00a0- ", s)
    s = re.sub(r" -$", "\u00a0-", s)
    s = re.sub(r"\u2026 \u201d", "\u2026\u201d", s)
    s = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s)
    return s


def chapter_xhtml(md: str, idx: int) -> tuple[str, str]:
    blocks = [b.strip() for b in md.strip().split("\n\n") if b.strip()]
    heading = blocks[0].lstrip("# ").strip()
    pov = blocks[1].strip("*") if blocks[1].startswith("*") else ""
    body = blocks[2:] if pov else blocks[1:]
    label, _, name = heading.partition(":")
    label_txt = LABELS.get(label.strip(), label.strip())
    parts = [f'<h1 class="chapter" id="c{idx}"><span class="label">{html.escape(label_txt)}</span>'
             f'{typeset(name.strip() or heading)}</h1>']
    if pov:
        parts.append(f'<p class="pov">{typeset(pov)}</p>')
    cls = "first"
    for b in body:
        if b.replace(" ", "") == "***":
            parts.append('<p class="break">\u2022 \u2022 \u2022</p>')
            cls = "after-break"
            continue
        para = typeset(" ".join(line.strip() for line in b.splitlines()))
        parts.append(f'<p class="{cls}">{para}</p>' if cls else f"<p>{para}</p>")
        cls = ""
    return heading, page(heading, "\n".join(parts))


def page(title: str, body: str) -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en-GB" xml:lang="en-GB">
<head><meta charset="utf-8"/><title>{html.escape(title)}</title>
<link rel="stylesheet" type="text/css" href="style.css"/></head>
<body>
{body}
</body>
</html>
"""


def main() -> None:
    title_body = f"""<div class="title-page">
<h1>{TITLE.upper()}</h1>
<p class="rule">\u2022 \u2022 \u2022</p>
<p class="sub">{SUBTITLE}</p>
</div>"""
    note_body = """<div class="note">
<p><em>Working draft.</em> A prose adaptation of Episode One of the series bible, written to test whether the season reads as a novel.</p>
<p>Not canon. Scenes follow the episode outline; small connective details (names of minor characters, Jamie\u2019s last words, the Wapping clerk) are invented and can be cut.</p>
</div>"""
    files = {"title.xhtml": page(TITLE, title_body), "note.xhtml": page("Note", note_body)}
    toc = []
    for i, name in enumerate(CHAPTERS):
        heading, xhtml = chapter_xhtml((HERE / name).read_text(encoding="utf-8"), i)
        fn = f"ch{i:02d}.xhtml"
        files[fn] = xhtml
        toc.append((fn, heading))

    nav_items = "\n".join(f'<li><a href="{fn}">{typeset(h)}</a></li>' for fn, h in toc)
    files["nav.xhtml"] = page("Contents", f"""<nav epub:type="toc" id="toc"><h1 class="chapter"><span class="label">Contents</span></h1>
<ol>
{nav_items}
</ol></nav>
<nav epub:type="landmarks" hidden="hidden"><ol>
<li><a epub:type="titlepage" href="title.xhtml">Title</a></li>
<li><a epub:type="bodymatter" href="ch00.xhtml">Start</a></li>
</ol></nav>""")

    spine_order = ["title.xhtml", "note.xhtml", "nav.xhtml"] + [fn for fn, _ in toc]
    ids = {fn: re.sub(r"\W", "_", fn) for fn in spine_order}
    manifest = "\n".join(
        f'<item id="{ids[fn]}" href="{fn}" media-type="application/xhtml+xml"'
        + (' properties="nav"' if fn == "nav.xhtml" else "") + "/>" for fn in spine_order)
    spine = "\n".join(f'<itemref idref="{ids[fn]}"/>' for fn in spine_order)
    modified = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid" xml:lang="en-GB">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="bookid">{BOOK_ID}</dc:identifier>
<dc:title>{TITLE}: {SUBTITLE}</dc:title>
<dc:creator>{AUTHOR}</dc:creator>
<dc:language>en-GB</dc:language>
<meta property="dcterms:modified">{modified}</meta>
</metadata>
<manifest>
<item id="css" href="style.css" media-type="text/css"/>
<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
{manifest}
</manifest>
<spine toc="ncx">
{spine}
</spine>
</package>
"""
    navpoints = "\n".join(
        f'<navPoint id="np{i}" playOrder="{i + 1}"><navLabel><text>{html.escape(h)}</text></navLabel>'
        f'<content src="{fn}"/></navPoint>' for i, (fn, h) in enumerate(toc))
    ncx = f"""<?xml version="1.0" encoding="utf-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
<head><meta name="dtb:uid" content="{BOOK_ID}"/></head>
<docTitle><text>{TITLE}</text></docTitle>
<navMap>
{navpoints}
</navMap>
</ncx>
"""
    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>
"""
    with zipfile.ZipFile(OUT, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/content.opf", opf, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/toc.ncx", ncx, compress_type=zipfile.ZIP_DEFLATED)
        z.writestr("OEBPS/style.css", CSS, compress_type=zipfile.ZIP_DEFLATED)
        for fn, content in files.items():
            z.writestr(f"OEBPS/{fn}", content, compress_type=zipfile.ZIP_DEFLATED)
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
