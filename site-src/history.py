"""Build the two history pieces into docs/history/.

Each piece lives in site-src/history/<name>/ and has two parts:

- site.html is a long page whose look changes era by era. It is written as the body of a
  page (title, styles, content, scripts) and this script wraps it in a full document.
- deck/ holds a slide deck in the format of the Slides artifact: deck.json lists the slide
  order, the chapters and the fonts, and deck/slides/<id>.html holds one <section> each,
  drawn on a 1920 by 1080 canvas, with speaker notes in <aside>. This script joins the
  slides into one page with a small viewer, so the deck works on GitHub Pages too.
"""

import html
import json
import re
import shutil
from pathlib import Path

W = Path(__file__).resolve().parent.parent
SRC = W / "site-src" / "history"
DIST = W / "docs" / "history"

PIECES = [
    ("web", "The Web Rebuilds Itself", "How the Web Learned to Respond",
     "The front end's story: HTML, CSS and scripts, from the first page in 1991 to AI."),
    ("server", "The Server Remembers", "Behind the Page",
     "The back end's story: servers and databases, from punched cards to vector search."),
]

# Simple line icons for the <x-icon> tags that the Slides artifact draws for itself.
ICONS = {
    "Database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "Globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.5 3.8 5.5 3.8 9s-1.3 6.5-3.8 9c-2.5-2.5-3.8-5.5-3.8-9S9.5 5.5 12 3z"/>',
    "Book": '<path d="M4 4h6a2 2 0 0 1 2 2v14a2 2 0 0 0-2-2H4zM20 4h-6a2 2 0 0 0-2 2v14a2 2 0 0 1 2-2h6z"/>',
    "Code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5M14 4l-4 16"/>',
    "Star": '<path d="M12 3l2.8 5.7 6.2.9-4.5 4.4 1 6.2L12 17.3 6.5 20.2l1-6.2L3 9.6l6.2-.9z"/>',
    "Lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
    "Clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "Tool": '<path d="M14.5 6.5a4 4 0 0 0 5 5L12 19a2.1 2.1 0 0 1-3-3l7.5-7.5a4 4 0 0 0-2-2z"/>',
    "Users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.5-3.6 3.2-6 6.5-6s6 2.4 6.5 6"/><circle cx="17" cy="9" r="2.5"/><path d="M16.5 14c2.7.2 4.6 2.5 5 5.5"/>',
    "Chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "Lightning": '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
    "Server": '<rect x="3" y="4" width="18" height="7" rx="1.5"/><rect x="3" y="13" width="18" height="7" rx="1.5"/><path d="M7 7.5h.01M7 16.5h.01"/>',
    "Cloud": '<path d="M7 18a4.5 4.5 0 0 1-.6-9A6 6 0 0 1 18 9.5a4.3 4.3 0 0 1-.5 8.5z"/>',
    "Key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/>',
    "Search": '<circle cx="11" cy="11" r="7"/><path d="M16 16l5 5"/>',
    "Settings": '<circle cx="12" cy="12" r="3.5"/><path d="M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1"/>',
    "Box": '<path d="M3 7l9-4 9 4v10l-9 4-9-4z"/><path d="M3 7l9 4 9-4M12 11v10"/>',
}


def icon_svg(match):
    name = match.group(1)
    style = match.group(2) or ""
    paths = ICONS.get(name, '<circle cx="12" cy="12" r="9"/>')
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex:none;{style}">{paths}</svg>')


def replace_icons(text):
    return re.sub(r'<x-icon name="([^"]+)"(?: style="([^"]*)")?\s*></x-icon>', icon_svg, text)


VIEWER_CSS = """
*, *::before, *::after { box-sizing: border-box; }
html, body { margin: 0; height: 100%; background: #0d1424; color: #f4f1ea; font: 15px/1.4 "Public Sans", system-ui, sans-serif; }
body { display: grid; grid-template-rows: auto 1fr auto; }
.bar { display: flex; flex-wrap: wrap; gap: 8px 14px; align-items: center; padding: 8px 14px; background: #1b2a4a; }
.bar a { color: #c9d2e3; }
.bar .title { font-weight: 700; margin-right: auto; }
.bar select { max-width: min(320px, 60vw); }
.bar button, .bar select { font: inherit; background: #24365c; color: #f4f1ea; border: 1px solid #3d527c; border-radius: 6px; padding: 5px 10px; cursor: pointer; }
.bar button:focus-visible, .bar select:focus-visible { outline: 3px solid #e9c46a; outline-offset: 2px; }
.stage-wrap { position: relative; overflow: hidden; }
.stage { position: absolute; left: 50%; top: 50%; width: 1920px; height: 1080px; transform-origin: 0 0; }
.stage > section { position: absolute; inset: 0; width: 1920px; height: 1080px; overflow: hidden; box-sizing: border-box; }
.stage > section:not(.on) { display: none !important; }
.stage section * { margin: 0; box-sizing: border-box; }
.stage aside { display: none !important; }
.notes { background: #f7f5f0; color: #1b2a4a; padding: 12px 18px; max-height: 30vh; overflow: auto; font-size: 16px; line-height: 1.5; }
.notes[hidden] { display: none; }
.count { font-variant-numeric: tabular-nums; color: #c9d2e3; }
"""

VIEWER_JS = """
(function () {
  var slides = Array.prototype.slice.call(document.querySelectorAll('.stage > section'));
  var stage = document.querySelector('.stage'), wrap = document.querySelector('.stage-wrap');
  var notes = document.getElementById('notes'), count = document.getElementById('count'), jump = document.getElementById('jump');
  var i = 0;
  function fit() {
    var s = Math.min(wrap.clientWidth / 1920, wrap.clientHeight / 1080);
    stage.style.transform = 'scale(' + s + ') translate(-50%, -50%)';
  }
  function show(n) {
    i = Math.max(0, Math.min(slides.length - 1, n));
    slides.forEach(function (s, k) { s.classList.toggle('on', k === i); s.setAttribute('aria-hidden', k === i ? 'false' : 'true'); });
    var aside = slides[i].querySelector('aside');
    notes.textContent = aside ? aside.textContent : '';
    count.textContent = (i + 1) + ' / ' + slides.length;
    var best = 0;
    Array.prototype.forEach.call(jump.options, function (o, k) { if (+o.value <= i) best = k; });
    jump.selectedIndex = best;
    if (location.hash !== '#' + (i + 1)) history.replaceState(null, '', '#' + (i + 1));
  }
  document.getElementById('prev').onclick = function () { show(i - 1); };
  document.getElementById('next').onclick = function () { show(i + 1); };
  document.getElementById('toggle-notes').onclick = function () {
    notes.hidden = !notes.hidden; this.setAttribute('aria-pressed', String(!notes.hidden)); fit();
  };
  jump.onchange = function () { show(+jump.value); };
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'SELECT') return;
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') { e.preventDefault(); show(i + 1); }
    if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); show(i - 1); }
    if (e.key === 'Home') show(0);
    if (e.key === 'End') show(slides.length - 1);
    if (e.key === 'n' || e.key === 'N') document.getElementById('toggle-notes').click();
  });
  window.addEventListener('resize', fit);
  var start = parseInt(location.hash.slice(1), 10);
  fit(); show(isNaN(start) ? 0 : start - 1);
})();
"""


def build_deck(name, deck_title, out):
    deck_dir = SRC / name / "deck"
    deck = json.loads((deck_dir / "deck.json").read_text())
    order = deck["order"]
    fonts = "".join(f'<link rel="stylesheet" href="{html.escape(face["href"])}">\n' for face in deck.get("faces", {}).values())
    sections = []
    for slide_id in order:
        text = (deck_dir / "slides" / f"{slide_id}.html").read_text()
        sections.append(replace_icons(text.strip()))
    options = []
    for key in sorted(deck.get("sections", {})):
        chapter = deck["sections"][key]
        options.append(f'<option value="{order.index(chapter["start"])}">{html.escape(chapter["description"])}</option>')
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(deck_title)} · slides</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
{fonts}<style>{VIEWER_CSS}</style>
</head>
<body>
<div class="bar">
<span class="title">{html.escape(deck_title)}</span>
<a href="index.html">The era-by-era page</a>
<a href="notes.html">Notes</a>
<a href="../index.html">All history pages</a>
PPTX_LINK<label for="jump" class="count">Chapter</label> <select id="jump">{''.join(options)}</select>
<button type="button" id="prev" aria-label="Previous slide">←</button>
<span class="count" id="count" aria-live="polite"></span>
<button type="button" id="next" aria-label="Next slide">→</button>
<button type="button" id="toggle-notes" aria-pressed="false">Notes</button>
</div>
<div class="stage-wrap"><div class="stage">
{chr(10).join(sections)}
</div></div>
<div class="notes" id="notes" hidden></div>
<script>{VIEWER_JS}</script>
</body>
</html>
"""
    pptx = sorted((SRC / name).glob("*.pptx"))
    link = "".join(f'<a href="{f.name}" download>PowerPoint</a>\n' for f in pptx)
    (out / "slides.html").write_text(page.replace("PPTX_LINK", link))


def build_site(name, site_title, out):
    text = (SRC / name / "site.html").read_text()
    head_end = text.index("</style>") + len("</style>")
    head, body = text[:head_end], text[head_end:]
    footer = ('<p style="max-width:960px;margin:0 auto;padding:18px 16px 40px;font:15px system-ui, sans-serif">'
              '<a href="slides.html">The slides that go with this page</a> · <a href="../index.html">All history pages</a> · '
              '<a href="../../index.html">From a click to a database row and back</a></p>')
    body = body.replace("<script", footer + "\n<script", 1)
    page = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "\n</head>\n<body>\n" + body + "\n</body>\n</html>\n")
    (out / "index.html").write_text(page)


NOTES_CSS = """
:root { --bg: #fbfaf7; --fg: #1b2a4a; --muted: #4a5568; --line: #ddd6c8; --card: #fff; --code: #f1eee6;
  --html: #E8955C; --css: #8DB4E2; --scripts: #E9C46A; --server: #8CC9A6; --db: #B9A6E0; --plugin: #C9D2E3; }
@media (prefers-color-scheme: dark) { :root { --bg: #131b2e; --fg: #eef0f5; --muted: #c4cbda; --line: #33456b; --card: #1b2a4a; --code: #0f1729; } }
*, *::before, *::after { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--fg); font: 17px/1.65 "Public Sans", system-ui, sans-serif; }
main { max-width: 820px; margin: 0 auto; padding: 32px 16px 80px; }
h1 { font: 700 clamp(32px, 6vw, 48px)/1.1 "Libre Baskerville", Georgia, serif; margin: 12px 0 10px; }
h2 { font: 700 clamp(24px, 4vw, 30px)/1.2 "Libre Baskerville", Georgia, serif; margin: 56px 0 8px; padding-top: 18px; border-top: 3px solid var(--line); }
h3 { font: 700 21px/1.3 "Public Sans", system-ui, sans-serif; margin: 34px 0 6px; }
.lede { font-size: 19px; color: var(--muted); }
a { color: inherit; text-underline-offset: 3px; }
code, pre { font: 14px/1.55 "JetBrains Mono", ui-monospace, Menlo, monospace; }
code { background: var(--code); padding: 1px 5px; border-radius: 4px; }
pre { background: var(--code); border: 1px solid var(--line); border-radius: 8px; padding: 12px 14px; white-space: pre-wrap; overflow-wrap: anywhere; margin: 10px 0 14px; }
pre code { background: none; padding: 0; }
table { border-collapse: collapse; width: 100%; margin: 10px 0 16px; font-size: 15px; display: block; overflow-x: auto; }
th, td { text-align: left; vertical-align: top; padding: 7px 10px; border-bottom: 1px solid var(--line); }
th { font-size: 13px; text-transform: uppercase; letter-spacing: .05em; color: var(--muted); }
.t { display: inline-block; font: 700 12px "Public Sans", sans-serif; color: #1b2a4a; padding: 2px 10px; border-radius: 999px; vertical-align: middle; white-space: nowrap; }
[data-part="html"].t { background: var(--html); } [data-part="css"].t { background: var(--css); } [data-part="scripts"].t { background: var(--scripts); }
[data-part="server"].t { background: var(--server); } [data-part="db"].t { background: var(--db); } [data-part="plugin"].t { background: var(--plugin); }
.parts { display: grid; gap: 10px; margin: 12px 0; }
.parts > div, .node { background: var(--card); border: 1px solid var(--line); border-left: 8px solid var(--line); border-radius: 8px; padding: 10px 14px; }
[data-part="html"].node, .parts [data-part="html"] { border-left-color: var(--html); } [data-part="css"].node, .parts [data-part="css"] { border-left-color: var(--css); }
[data-part="scripts"].node, .parts [data-part="scripts"] { border-left-color: var(--scripts); } [data-part="server"].node, .parts [data-part="server"] { border-left-color: var(--server); }
[data-part="db"].node, .parts [data-part="db"] { border-left-color: var(--db); }
figure { margin: 14px 0 16px; }
.flow { display: grid; grid-template-columns: 1fr auto 1fr; gap: 12px; align-items: center; }
.flow.three { grid-template-columns: 1fr auto 1fr auto 1fr; align-items: stretch; }
.flow .arrow { text-align: center; color: var(--muted); font-size: 14px; align-self: center; }
@media (max-width: 640px) { .flow, .flow.three { grid-template-columns: 1fr; } .flow .arrow { transform: none; } }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
@media (max-width: 640px) { .pair { grid-template-columns: 1fr; } }
.pair pre { margin-top: 2px; }
.cap { font-size: 13px; font-weight: 700; color: var(--muted); margin: 6px 0 0; text-transform: uppercase; letter-spacing: .04em; }
.dates { list-style: none; padding: 0; }
.dates li { border-left: 4px solid var(--line); padding: 2px 0 2px 12px; margin: 8px 0; }
.discuss { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 12px 16px; margin: 14px 0; }
.screens { display: flex; gap: 24px; align-items: flex-end; flex-wrap: wrap; }
.screens > div { background: var(--card); border: 1px solid var(--line); border-radius: 8px; padding: 8px; display: grid; gap: 6px; }
.screens .wide { width: min(300px, 100%); } .screens .narrow { width: 110px; }
.screens span { display: block; height: 14px; background: var(--muted); opacity: .5; border-radius: 3px; }
.screens i { display: block; height: 40px; background: var(--css); border-radius: 4px; }
.screens .wide > div { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6px; }
.screens small { font-size: 12px; color: var(--muted); }
.gridfig { display: grid; grid-template-columns: 1fr 2fr; grid-template-rows: 36px 90px 32px; gap: 6px; grid-template-areas: "h h" "n m" "f f"; max-width: 420px; }
.gridfig div { background: var(--css); color: #1b2a4a; border-radius: 5px; padding: 6px 10px; font: 600 13px "JetBrains Mono", monospace; }
.gridfig div:nth-child(2n) { background: var(--plugin); }
.bars p { background: var(--card); border: 1px solid var(--line); border-radius: 999px; padding: 6px 14px; margin: 6px 0; width: fit-content; }
.bars .bad { color: #b3261e; } .bars .good { color: #2e6b4a; }
.search { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px; max-width: 520px; }
.search .q { border: 1px solid var(--line); border-radius: 999px; padding: 6px 14px; margin: 0 0 10px; }
.search .aio { border: 2px solid var(--css); border-radius: 10px; padding: 8px 12px; }
.search .aio p { margin: 4px 0; } .search small { color: var(--muted); }
.search .link { color: #1a0dab; margin: 6px 0 0; }
@media (prefers-color-scheme: dark) { .search .link { color: #8ab4f8; } }
.map { position: relative; height: 240px; background: var(--card); border: 1px solid var(--line); border-radius: 12px; }
.map span { position: absolute; font-size: 13px; line-height: 1.25; color: var(--muted); max-width: 36%; }
.map span::before { content: "● "; color: var(--db); }
.map span.q { color: var(--fg); font-weight: 700; } .map span.q::before { content: ""; }
.toc { background: var(--card); border: 1px solid var(--line); border-radius: 10px; padding: 12px 18px; margin: 18px 0; }
.toc ol { margin: 6px 0 0; padding-left: 1.3em; }
.top { display: flex; flex-wrap: wrap; gap: 6px 16px; font-size: 14px; color: var(--muted); }
.sources li { margin: 6px 0; }
@media print { .top, .toc { display: none; } h2 { break-before: page; border: 0; } pre, figure, table { break-inside: avoid; } body { background: #fff; color: #000; } }
"""


def build_notes(name, deck_title, out, pptx):
    body = (SRC / name / "notes.html").read_text()
    heads = re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body)
    toc = "".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in heads)
    links = ['<a href="slides.html">The slides</a>', '<a href="index.html">The era-by-era page</a>']
    links += [f'<a href="{f.name}" download>The slides as PowerPoint</a>' for f in pptx]
    links.append('<a href="../index.html">All history pages</a>')
    top = '<p class="top">' + " · ".join(links) + "</p>"
    first_h2 = body.index("<h2")
    body = body[:first_h2] + f'<nav class="toc" aria-label="Contents"><b>Contents</b><ol>{toc}</ol></nav>\n' + body[first_h2:]
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(deck_title)} · notes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Public+Sans:wght@400;700&family=JetBrains+Mono:wght@400&display=swap">
<style>{NOTES_CSS}</style>
</head>
<body>
<main>
{top}
{body}
</main>
</body>
</html>
"""
    (out / "notes.html").write_text(page)


HUB = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Two histories of the web</title>
<style>
:root { --bg: #f7f5f0; --fg: #1b2a4a; --muted: #5a6478; --card: #fffdf9; --line: #d9d3c7; }
@media (prefers-color-scheme: dark) { :root { --bg: #131b2e; --fg: #f4f1ea; --muted: #c9d2e3; --card: #1b2a4a; --line: #33456b; } }
body { margin: 0; background: var(--bg); color: var(--fg); font: 17px/1.6 system-ui, sans-serif; }
main { max-width: 860px; margin: 0 auto; padding: 48px 16px 80px; }
h1 { font: 700 clamp(30px, 6vw, 44px)/1.1 Georgia, serif; margin: 0 0 12px; }
.lede { color: var(--muted); max-width: 62ch; }
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; margin-top: 28px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px 20px; }
.card h2 { margin: 0 0 6px; font-size: 1.3rem; }
.card p { color: var(--muted); margin: 0 0 12px; }
a { color: inherit; text-underline-offset: 3px; }
.key { display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 0; padding: 0; list-style: none; }
.key li { color: #1b2a4a; font-weight: 700; font-size: 14px; padding: 3px 12px; border-radius: 999px; }
</style>
</head>
<body>
<main>
<h1>Two histories of the web</h1>
<p class="lede">The same thirty-odd years, told twice. The first history watches from the browser: HTML, CSS and scripts. The second watches from behind the page: the servers that answer and the databases that remember. Both use the same colours for the four parts of a website.</p>
<ul class="key"><li style="background:#E8955C">HTML</li><li style="background:#8DB4E2">CSS</li><li style="background:#E9C46A">Scripts</li><li style="background:#8CC9A6">Server</li></ul>
<div class="cards">
CARDS
</div>
<p style="margin-top:32px"><a href="../index.html">Back to From a click to a database row and back</a></p>
</main>
</body>
</html>
"""


def build():
    DIST.mkdir(parents=True, exist_ok=True)
    cards = []
    for name, site_title, deck_title, blurb in PIECES:
        if not (SRC / name / "site.html").exists():
            continue
        out = DIST / name
        if out.exists():
            shutil.rmtree(out)
        out.mkdir(parents=True)
        build_site(name, site_title, out)
        build_deck(name, deck_title, out)
        pptx = sorted((SRC / name).glob("*.pptx"))
        for f in pptx:
            shutil.copy(f, out / f.name)
        if (SRC / name / "notes.html").exists():
            build_notes(name, deck_title, out, pptx)
        cards.append(f'<div class="card"><h2>{html.escape(site_title)}</h2><p>{html.escape(blurb)}</p>'
                     f'<p><a href="{name}/index.html">The era-by-era page</a><br><a href="{name}/slides.html">The slides</a><br><a href="{name}/notes.html">The notes, to read on their own</a>'
                     + "".join(f'<br><a href="{name}/{f.name}" download>The slides as PowerPoint</a>' for f in pptx) + '</p></div>')
    (DIST / "index.html").write_text(HUB.replace("CARDS", "\n".join(cards)))


if __name__ == "__main__":
    build()
