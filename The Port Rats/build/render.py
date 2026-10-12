"""Render book.json -> EPUB 3 and print HTML (for 6x9 PDF)."""
import json, os, re, sys, zipfile, uuid, datetime, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
book = json.load(open(os.path.join(HERE, "book.json"), encoding="utf-8"))
TITLE, AUTHOR = "The Port Rats", "Patrick"
FONTFILES = {"EBGaramond-Regular.ttf": ("Garamond", "normal", "normal"),
             "EBGaramond-Italic.ttf": ("Garamond", "normal", "italic"),
             "EBGaramond-SemiBold.ttf": ("Garamond", "600", "normal"),
             "IMFeENsc28P.ttf": ("FellSC", "normal", "normal"),
             "IMFeENit28P.ttf": ("FellItalic", "normal", "normal"),
             "IMFeENrm28P.ttf": ("Fell", "normal", "normal")}


def fontfaces(prefix):
    return "\n".join(f'@font-face {{ font-family: "{fam}"; font-weight: {w}; font-style: {s}; src: url("{prefix}{f}"); }}'
                     for f, (fam, w, s) in FONTFILES.items())


TWEAKS = json.load(open(os.path.join(HERE, "tweaks.json"))) if os.path.exists(os.path.join(HERE, "tweaks.json")) else {}


def para_html(b, img, bid=""):
    if b["t"] == "scene":
        return f'<div class="scene"><img src="{img}mooring.svg" alt="* * *"/></div>'
    if b["t"] == "opener":
        ini = b["initial"]
        q = ""
        m = re.match(r"^([“‘\"']+)(.*)$", ini)
        if m:
            q, ini = m.group(1), m.group(2)
        qspan = f'<span class="hangq">{q}</span>' if q else ""
        return (f'<p class="opener">{qspan}<span class="dropcap">{ini}</span>'
                f'<span class="lead">{b["lead"]}</span>{b["tail"]}</p>')
    classes = (["flush"] if b["t"] == "flush" else []) + ([TWEAKS[bid]] if bid in TWEAKS else [])
    cls = f' class="{" ".join(classes)}"' if classes else ""
    return f"<p{cls}>{b['html']}</p>"


def chapter_html(c, img, last=False):
    body = "\n".join(para_html(b, img, f"{c['num']}-{i}") for i, b in enumerate(c["blocks"]))
    tail = (f'\n<div class="tailpiece"><img src="{img}ashleaf.svg" alt=""/></div>'
            f'\n<p class="endnote">End of the draft · October 2026</p>') if last else ""
    return f'''<section class="chapter" epub:type="chapter" id="ch{c['num']}">
<header class="chap-head">
<p class="chap-num">Chapter {c['num']}</p>
<h1 class="chap-title">{c['title']}</h1>
<div class="chap-orn"><img src="{img}ratline.svg" alt=""/></div>
</header>
{body}{tail}
</section>'''


TITLEPAGE = '''<section class="titlepage" epub:type="titlepage">
<div class="tp-emblem"><img src="{img}emblem.svg" alt=""/></div>
<p class="tp-the">The</p>
<h1 class="tp-title">Port Rats</h1>
<p class="tp-sub">a novel of the Lowers</p>
<div class="tp-leaf"><img src="{img}ashleaf.svg" alt=""/></div>
<p class="tp-author">Patrick</p>
</section>'''

COPYRIGHT = '''<section class="copyright" epub:type="copyright-page">
<p>This is a work of fiction. Names, characters, places, and incidents are the product of the author’s imagination. Any resemblance to actual persons, living or dead, or to actual events, is coincidental.</p>
<p>All characters depicted are adults.</p>
<p>For mature readers. Contains explicit sexual content, violence, and strong language.</p>
<p>Copyright © 2026 by Patrick<br/>All rights reserved.</p>
<p>Draft edition · October 2026</p>
<p>Text set in EB Garamond. Display type IM Fell English, after the types cut for Dr. John Fell, Oxford, 1670s.</p>
<div class="cp-orn"><img src="{img}mooring.svg" alt=""/></div>
</section>'''


def contents(img, links=True):
    rows = []
    for c in book:
        t = f'<span class="toc-n">{c["num"]}</span> <span class="toc-t">{c["title"]}</span>'
        rows.append(f'<li><a href="ch{c["num"]}.xhtml#ch{c["num"]}">{t}</a></li>' if links
                    else f'<li><a href="#ch{c["num"]}">{t}</a></li>')
    return f'''<section class="contents" epub:type="toc">
<h2 class="toc-head">Contents</h2>
<div class="toc-orn"><img src="{img}ashleaf.svg" alt=""/></div>
<ol class="toc">{"".join(rows)}</ol>
</section>'''


BASE_CSS = open(os.path.join(HERE, "book.css"), encoding="utf-8").read()


def xhtml(title, body, css="../styles/book.css", bodycls=""):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head><meta charset="utf-8"/><title>{title}</title><link rel="stylesheet" type="text/css" href="{css}"/></head>
<body class="{bodycls}">
{body}
</body></html>'''


def build_epub(path):
    img = "../images/"
    files = {}
    files["OEBPS/text/cover.xhtml"] = xhtml("Cover", '<div class="cover"><img src="../images/cover.jpg" alt="The Port Rats"/></div>', bodycls="coverbody")
    files["OEBPS/text/title.xhtml"] = xhtml(TITLE, TITLEPAGE.format(img=img))
    files["OEBPS/text/copyright.xhtml"] = xhtml("Copyright", COPYRIGHT.format(img=img))
    files["OEBPS/text/contents.xhtml"] = xhtml("Contents", contents(img))
    for i, c in enumerate(book):
        files[f"OEBPS/text/ch{c['num']}.xhtml"] = xhtml(f"Chapter {c['num']}", chapter_html(c, img, last=(i == len(book) - 1)))
    nav_items = "".join(f'<li><a href="ch{c["num"]}.xhtml">Chapter {c["num"]}: {c["title"]}</a></li>' for c in book)
    files["OEBPS/text/nav.xhtml"] = xhtml("Navigation", f'''<nav epub:type="toc" id="toc"><h2>Contents</h2><ol>
<li><a href="title.xhtml">Title Page</a></li><li><a href="contents.xhtml">Contents</a></li>{nav_items}</ol></nav>
<nav epub:type="landmarks" hidden=""><ol><li><a epub:type="cover" href="cover.xhtml">Cover</a></li>
<li><a epub:type="toc" href="contents.xhtml">Contents</a></li>
<li><a epub:type="bodymatter" href="ch{book[0]["num"]}.xhtml">Begin Reading</a></li></ol></nav>''')
    files["OEBPS/styles/book.css"] = fontfaces("../fonts/") + "\n" + BASE_CSS
    uid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, "the-port-rats-patrick"))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    man, spine = [], []
    order = ["cover", "title", "copyright", "contents"] + [f"ch{c['num']}" for c in book]
    for n in order:
        props = ' properties="svg"' if n in ("title", "copyright", "contents") or n.startswith("ch") else ""
        man.append(f'<item id="{n}" href="text/{n}.xhtml" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="{n}"{" linear=\"yes\"" if n != "cover" else ""}/>')
    man.append('<item id="nav" href="text/nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>')
    man.append('<item id="css" href="styles/book.css" media-type="text/css"/>')
    man.append('<item id="coverimg" href="images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>')
    for s in ("mooring", "ratline", "ashleaf", "emblem"):
        man.append(f'<item id="i-{s}" href="images/{s}.svg" media-type="image/svg+xml"/>')
    for i, f in enumerate(FONTFILES):
        man.append(f'<item id="f{i}" href="fonts/{f}" media-type="font/ttf"/>')
    files["OEBPS/content.opf"] = f'''<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="uid" xml:lang="en">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
<dc:identifier id="uid">{uid}</dc:identifier><dc:title>{TITLE}</dc:title><dc:creator>{AUTHOR}</dc:creator>
<dc:language>en</dc:language><dc:date>2026-10-12</dc:date><meta property="dcterms:modified">{now}</meta>
<meta name="cover" content="coverimg"/>
</metadata>
<manifest>{"".join(man)}</manifest>
<spine>{"".join(spine)}</spine>
</package>'''
    # (svg property is only valid when the doc embeds inline SVG; ours use <img>, so strip it)
    files["OEBPS/content.opf"] = files["OEBPS/content.opf"].replace(' properties="svg"', "")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", '''<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container"><rootfiles>
<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>''',
                   compress_type=zipfile.ZIP_DEFLATED)
        for k, v in files.items():
            z.writestr(k, v, compress_type=zipfile.ZIP_DEFLATED)
        z.write(os.path.join(HERE, "img", "cover.jpg"), "OEBPS/images/cover.jpg", compress_type=zipfile.ZIP_DEFLATED)
        for s in ("mooring", "ratline", "ashleaf", "emblem"):
            z.write(os.path.join(HERE, "img", f"{s}.svg"), f"OEBPS/images/{s}.svg", compress_type=zipfile.ZIP_DEFLATED)
        for f in FONTFILES:
            z.write(os.path.join(FONTS, f), f"OEBPS/fonts/{f}", compress_type=zipfile.ZIP_DEFLATED)


def build_print(path):
    img = "img/"
    css = fontfaces("../fonts/") + "\n" + BASE_CSS + "\n" + open(os.path.join(HERE, "print.css"), encoding="utf-8").read()
    chs = "\n".join(chapter_html(c, img, last=(i == len(book) - 1)) for i, c in enumerate(book))
    html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{TITLE}</title><style>{css}</style></head>
<body class="print">
<div class="front">{TITLEPAGE.format(img=img)}{COPYRIGHT.format(img=img)}{contents(img, links=False)}</div>
<div class="bodymatter">{chs}</div>
</body></html>'''
    open(path, "w", encoding="utf-8").write(html)


if __name__ == "__main__":
    build_epub(os.path.join(HERE, "The Port Rats.epub"))
    build_print(os.path.join(HERE, "print.html"))
    print("built")
