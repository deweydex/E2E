"""Shared helpers: styles, script, page shell, annotated code, diagrams."""

import base64
import html
import re
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

# --------------------------------------------------------------------- css

CSS = r"""
:root {
  color-scheme: light dark;
  --bg: #fbfaf6;
  --surface: #ffffff;
  --surface-2: #f2efe6;
  --code-bg: #f4f1e8;
  --text: #1d2430;
  --muted: #586071;
  --line: #ddd7c8;
  --accent: #0b6e6e;
  --accent-soft: #dcefee;
  --on-accent: #ffffff;
  --warn: #8a5300;
  --warn-soft: #fbefd6;
  --bad: #a4262c;
  --bad-soft: #f8e2e3;
  --good: #25663a;
  --good-soft: #e0f1e5;
  --tok-keyword: #8a2b9b;
  --tok-string: #1c6b3a;
  --tok-comment: #6b7280;
  --tok-func: #0a58a8;
  --tok-number: #a34a00;
  --tok-name: #0b6e6e;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #12161d;
    --surface: #1a2029;
    --surface-2: #222a36;
    --code-bg: #0f131a;
    --text: #e6e9ef;
    --muted: #a0a9b8;
    --line: #2d3644;
    --accent: #5fcaca;
    --accent-soft: #163a3c;
    --on-accent: #0b1a1a;
    --warn: #f0b34d;
    --warn-soft: #3a2c10;
    --bad: #ff8f95;
    --bad-soft: #3d1b1e;
    --good: #7fd49a;
    --good-soft: #14301f;
    --tok-keyword: #d79bef;
    --tok-string: #8fd9a8;
    --tok-comment: #8b94a5;
    --tok-func: #7db8f5;
    --tok-number: #f2a864;
    --tok-name: #5fcaca;
  }
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; scroll-padding-top: 16px; }
body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 17px/1.65 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}
.shell {
  display: grid;
  grid-template-columns: 236px minmax(0, 1fr);
  gap: 44px;
  max-width: 1360px;
  margin: 0 auto;
  padding: 0 24px;
}
nav.toc {
  position: sticky;
  top: 0;
  align-self: start;
  max-height: 100vh;
  overflow: auto;
  padding: 28px 0;
  font-size: 15px;
}
nav.toc summary {
  cursor: pointer;
  font-weight: 700;
  margin-bottom: 8px;
}
nav.toc ol { list-style: none; margin: 0; padding: 0; }
nav.toc a {
  display: block;
  padding: 4px 10px;
  color: var(--muted);
  text-decoration: none;
  border-left: 2px solid var(--line);
}
nav.toc a:hover, nav.toc a.current { color: var(--text); border-left-color: var(--accent); }
nav.toc .sibling { margin-top: 18px; font-size: 14px; }
main { padding: 36px 0 110px; min-width: 0; }
.prose { max-width: 760px; }
h1 { font-size: 2.3rem; line-height: 1.2; margin: 0 0 12px; letter-spacing: -0.01em; }
h2 {
  font-size: 1.6rem;
  line-height: 1.3;
  margin: 72px 0 8px;
  padding-top: 8px;
}
h2 .part { color: var(--accent); font-size: 0.95rem; display: block; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 4px; }
h3 { font-size: 1.15rem; margin: 34px 0 6px; }
p { margin: 0 0 16px; }
.lede { font-size: 1.15rem; color: var(--muted); max-width: 720px; }
a { color: var(--accent); }
code, kbd {
  font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  font-size: 0.88em;
  background: var(--code-bg);
  border: 1px solid var(--line);
  border-radius: 4px;
  padding: 0.05em 0.35em;
}
pre code { background: none; border: none; padding: 0; font-size: inherit; }
dfn { font-style: normal; font-weight: 700; }
.edition {
  display: inline-block;
  background: var(--accent-soft);
  color: var(--accent);
  font-weight: 700;
  font-size: 0.85rem;
  padding: 3px 10px;
  border-radius: 999px;
  margin-bottom: 14px;
}
.hero-grid { display: grid; grid-template-columns: minmax(0, 1fr) 280px; gap: 32px; align-items: start; margin-top: 18px; }
.hero-grid img { width: 100%; height: auto; border-radius: 10px; border: 1px solid var(--line); }
.hero-grid figcaption { font-size: 14px; color: var(--muted); margin-top: 6px; }
.downloads { display: flex; flex-wrap: wrap; gap: 10px; margin: 8px 0 20px; }
.btn {
  display: inline-block;
  background: var(--accent);
  color: var(--on-accent);
  font-weight: 700;
  text-decoration: none;
  padding: 10px 16px;
  border-radius: 8px;
}
.btn.secondary { background: var(--surface-2); color: var(--text); border: 1px solid var(--line); }

/* boxes */
.box {
  border-left: 4px solid var(--accent);
  background: var(--accent-soft);
  padding: 12px 16px;
  border-radius: 0 8px 8px 0;
  margin: 22px 0;
  max-width: 760px;
}
.box > :last-child { margin-bottom: 0; }
.box .label { display: block; font-weight: 700; margin-bottom: 4px; }
.box.warn { border-left-color: var(--warn); background: var(--warn-soft); }
.box.try { border-left-color: var(--good); background: var(--good-soft); }
.box.bad { border-left-color: var(--bad); background: var(--bad-soft); }
.box.goal ul, .box.check ul { margin: 4px 0 0; padding-left: 20px; }
.box.goal li, .box.check li { margin: 2px 0; }
.box.check { border-left-color: var(--good); background: var(--good-soft); }

/* numbered steps for making things */
ol.make { max-width: 760px; margin: 12px 0 22px; padding: 0; list-style: none; counter-reset: make; }
ol.make > li { counter-increment: make; position: relative; padding: 0 0 10px 38px; }
ol.make > li::before {
  content: counter(make);
  position: absolute; left: 0; top: 0;
  width: 26px; height: 26px; border-radius: 50%;
  background: var(--accent-soft); color: var(--accent); border: 1px solid var(--accent);
  font-weight: 700; font-size: 14px;
  display: grid; place-items: center;
}

/* optional detail that a reader can open */
details.deeper { max-width: 760px; margin: 18px 0; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); }
details.deeper > summary { cursor: pointer; padding: 10px 14px; font-weight: 700; }
details.deeper > summary .tag { color: var(--muted); font-weight: 400; margin-right: 6px; }
details.deeper[open] > summary { border-bottom: 1px solid var(--line); }
details.deeper > .inner { padding: 4px 16px 6px; }
details.deeper > .inner > :last-child { margin-bottom: 8px; }

.term { border-bottom: 1.5px dotted var(--accent); cursor: help; position: relative; }
.term::after {
  content: attr(data-def); position: absolute; left: 50%; bottom: calc(100% + 8px); transform: translateX(-50%);
  width: max-content; max-width: min(280px, 78vw); padding: 8px 10px; border-radius: 8px;
  background: var(--text); color: var(--bg); font-size: 0.85rem; line-height: 1.4; font-weight: 400; font-style: normal;
  display: none; pointer-events: none; z-index: 20; text-align: left;
}
.term:hover::after, .term:focus::after { display: block; }
svg text.term-svg { text-decoration: underline dotted; text-underline-offset: 4px; cursor: help; }
dl.glossary .where { color: var(--muted); }
.prose code, .box code, details.deeper code, ol.make code, td code { overflow-wrap: anywhere; }
/* annotated code */
figure.file {
  margin: 28px 0 36px;
  border: 1px solid var(--line);
  border-radius: 10px;
  overflow: hidden;
  background: var(--surface);
  max-width: 1080px;
}
figure.file > figcaption {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: var(--surface-2);
  border-bottom: 1px solid var(--line);
  font-size: 14px;
}
figcaption .fname { font-family: ui-monospace, Menlo, Consolas, monospace; font-weight: 700; font-size: 15px; }
figcaption .where { color: var(--muted); flex: 1; }
button.copy {
  font: inherit;
  font-size: 13px;
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 6px;
  padding: 3px 10px;
  cursor: pointer;
}
button.copy:hover { border-color: var(--accent); }
.chunk {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr);
  border-top: 1px solid var(--line);
}
.chunk:first-of-type { border-top: none; }
.chunk pre.code { white-space: pre-wrap; overflow-wrap: anywhere; font-size: 13px; }
pre.code {
  margin: 0;
  padding: 14px 16px;
  background: var(--code-bg);
  font: 13.5px/1.55 ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  overflow-x: auto;
  tab-size: 4;
}
.why { padding: 14px 20px 6px; font-size: 15.5px; line-height: 1.6; }
.why p { margin: 0 0 12px; }
.trails { margin-bottom: 8px; }
.trail { margin-bottom: 8px; }
.trail .now { display: flex; flex-wrap: wrap; gap: 6px; align-items: baseline; }
.trail .now-title { font-weight: 700; font-size: 0.95rem; }
.trail .around { display: flex; flex-direction: column; gap: 1px; font-size: 12.5px; color: var(--muted); margin-top: 3px; }
.trail .around a { color: var(--muted); text-decoration: none; }
.trail .around a:hover { color: var(--accent); text-decoration: underline; }
.badges { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px; }
.badge {
  background: var(--accent);
  color: var(--on-accent);
  font-size: 12px;
  font-weight: 700;
  padding: 1px 9px;
  border-radius: 999px;
  white-space: nowrap;
}
.badge.plain { background: var(--surface-2); color: var(--muted); border: 1px solid var(--line); }
.snippet { position: relative; margin: 14px 0 22px; max-width: 760px; }
.snippet pre.code { border: 1px solid var(--line); border-radius: 8px; }
.snippet .copy { position: absolute; top: 8px; right: 8px; }
.snippet .cap { font-size: 14px; color: var(--muted); margin: 0 0 4px; }

/* syntax colours */
.hl .k, .hl .kn, .hl .kd, .hl .kc, .hl .kr, .hl .kt, .hl .ow { color: var(--tok-keyword); }
.hl .s, .hl .s1, .hl .s2, .hl .sa, .hl .sb, .hl .sc, .hl .sd, .hl .se, .hl .si, .hl .sx, .hl .sr { color: var(--tok-string); }
.hl .c, .hl .c1, .hl .cm, .hl .cs, .hl .ch, .hl .cp { color: var(--tok-comment); font-style: italic; }
.hl .nf, .hl .fm, .hl .nd { color: var(--tok-func); }
.hl .nc, .hl .nn, .hl .nt, .hl .na { color: var(--tok-name); }
.hl .nb, .hl .bp { color: var(--tok-func); }
.hl .m, .hl .mi, .hl .mf, .hl .mh { color: var(--tok-number); }

/* tables */
table.tbl { border-collapse: collapse; width: 100%; max-width: 1080px; margin: 18px 0 28px; font-size: 15.5px; }
table.tbl th, table.tbl td { text-align: left; vertical-align: top; padding: 9px 12px; border-bottom: 1px solid var(--line); }
table.tbl th { background: var(--surface-2); font-size: 14px; }
.tablewrap { overflow-x: auto; }

/* diagrams */
figure.diagram { margin: 26px 0 30px; max-width: 1080px; }
figure.diagram svg { width: 100%; height: auto; display: block; background: var(--surface); border: 1px solid var(--line); border-radius: 10px; }
figure.diagram figcaption { font-size: 15px; color: var(--muted); margin-top: 8px; max-width: 760px; }
svg text { font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; fill: var(--text); }
svg .t-muted { fill: var(--muted); }
svg .t-on { fill: var(--on-accent); font-weight: 700; }
svg .lane { stroke: var(--line); stroke-width: 2; stroke-dasharray: 5 6; }
svg .head { fill: var(--surface-2); stroke: var(--line); stroke-width: 1.5; }
svg .note { fill: var(--surface); stroke: var(--line); stroke-width: 1.5; }
svg .arrow { stroke: var(--accent); stroke-width: 2.5; fill: none; }
svg .arrow.back { stroke: var(--muted); stroke-dasharray: 7 5; }
svg .arrow.bad { stroke: var(--bad); stroke-dasharray: 7 5; }
svg .dot { fill: var(--accent); }
svg .zone-bad { fill: var(--warn-soft); stroke: var(--warn); stroke-width: 2; }
svg .zone-good { fill: var(--accent-soft); stroke: var(--accent); stroke-width: 2; }
svg .zone-db { fill: var(--surface-2); stroke: var(--muted); stroke-width: 2; }
svg .strong { font-weight: 700; }

/* shapes pipeline */
.pipeline { max-width: 760px; margin: 22px 0 30px; }
.pipeline .stage { border: 1px solid var(--line); background: var(--surface); border-radius: 8px; padding: 10px 14px; }
.pipeline .stage h4 { margin: 0 0 4px; font-size: 15px; }
.pipeline .stage pre { margin: 0; font: 13.5px/1.5 ui-monospace, Menlo, Consolas, monospace; overflow-x: auto; white-space: pre-wrap; word-break: break-word; }
.pipeline .step { text-align: center; color: var(--accent); font-size: 14px; padding: 6px 0; }
.pipeline .step b { font-size: 18px; }

/* two-up comparison */
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; max-width: 1000px; margin: 20px 0; }
.two > div { border: 1px solid var(--line); background: var(--surface); border-radius: 10px; padding: 14px 18px 4px; }
.two h4 { margin: 0 0 6px; }

/* station list */
ol.stations { padding: 0; margin: 20px 0; list-style: none; counter-reset: st; max-width: 760px; }
ol.stations li { counter-increment: st; position: relative; padding: 0 0 14px 48px; }
ol.stations li::before {
  content: counter(st);
  position: absolute; left: 0; top: 1px;
  width: 32px; height: 32px; border-radius: 50%;
  background: var(--accent); color: var(--on-accent);
  font-weight: 700; font-size: 15px;
  display: grid; place-items: center;
}
ol.stations li strong { display: block; }

/* glossary */
dl.glossary { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 12px; margin: 22px 0; max-width: 1080px; }
dl.glossary > div { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 10px 14px; }
dl.glossary dt { font-weight: 700; }
dl.glossary dd { margin: 2px 0 0; font-size: 15px; color: var(--muted); }

/* landing cards */
.cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 28px 0; max-width: 1000px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 20px 22px; }
.card h2 { margin: 0 0 6px; font-size: 1.35rem; padding: 0; }
.landing { max-width: 900px; margin: 0 auto; padding: 56px 24px 96px; }

@media (max-width: 1000px) {
  .shell { grid-template-columns: minmax(0, 1fr); gap: 0; padding: 0 16px; }
  nav.toc { position: static; max-height: none; padding: 16px 0 0; }
  .hero-grid { grid-template-columns: minmax(0, 1fr); }
  .hero-grid figure { max-width: 320px; }
}
@media (max-width: 820px) {
  .chunk { grid-template-columns: minmax(0, 1fr); }
  .why { border-top: 1px dashed var(--line); }
  .two { grid-template-columns: 1fr; }
  body { font-size: 16.5px; }
  h1 { font-size: 1.9rem; }
}
"""

# ---------------------------------------------------------------------- js

JS = r"""
document.querySelectorAll("button.copy").forEach((button) => {
  button.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(button.dataset.code);
      const old = button.textContent;
      button.textContent = "Copied";
      setTimeout(() => { button.textContent = old; }, 1400);
    } catch {
      button.textContent = "Copy failed";
    }
  });
});

const toc = document.querySelector("nav.toc details");
if (toc && window.matchMedia("(max-width: 1000px)").matches) {
  toc.open = false;
}

const links = [...document.querySelectorAll("nav.toc a[href^='#']")];
const sections = links.map((a) => document.querySelector(a.getAttribute("href"))).filter(Boolean);
if ("IntersectionObserver" in window && sections.length) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        links.forEach((a) => a.classList.toggle("current", a.getAttribute("href") === "#" + entry.target.id));
      }
    });
  }, { rootMargin: "0px 0px -70% 0px" });
  sections.forEach((s) => observer.observe(s));
}
"""

# ----------------------------------------------------------------- helpers

_FORMATTER = HtmlFormatter(nowrap=True)


def esc(text):
    return html.escape(text, quote=True)


def highlight_code(text, lang):
    if lang in (None, "text"):
        return esc(text.rstrip("\n"))
    lexer = get_lexer_by_name(lang)
    return highlight(text.rstrip("\n"), lexer, _FORMATTER).rstrip("\n")


def station_badges(stations):
    """A marker that build.py later turns into a trail: where this code sits in the journey, and what comes before and after."""
    if not stations:
        return ""
    return f'<!--TRAIL:{",".join(str(n) for n in stations)}-->'


def _runs(numbers):
    """Group sorted station numbers into runs of consecutive numbers: [1,2,10,11] becomes [[1,2],[10,11]]."""
    runs = []
    for n in sorted(numbers):
        if runs and n == runs[-1][-1] + 1:
            runs[-1].append(n)
        else:
            runs.append([n])
    return runs


def build_trails(page, titles):
    """Replace each trail marker with badges that show the current station and its neighbours.

    titles[0] is the title of Station 1. Each run of consecutive stations gets one trail:
    the current station or stations, the station before, and the station after.
    """

    def short(n):
        return titles[n - 1].rstrip(".")

    def trail(run):
        first, last = run[0], run[-1]
        if first == last:
            now = f'<span class="badge">Station {first}</span> <span class="now-title">{short(first)}</span>'
        else:
            now = (
                f'<span class="badge">Stations {first} to {last}</span> '
                f'<span class="now-title">{short(first)}, then {short(last)[0].lower() + short(last)[1:]}</span>'
            )
        if first > 1:
            before_text = f'<a class="was" href="#journey">&larr; Before: Station {first - 1}, {short(first - 1)}</a>'
        else:
            before_text = '<span class="was">&larr; Before: the click has not happened yet</span>'
        if last < len(titles):
            after_text = f'<a class="then" href="#journey">Next: Station {last + 1}, {short(last + 1)} &rarr;</a>'
        else:
            after_text = '<span class="then">Next: the journey is over &rarr;</span>'
        return f'<div class="trail"><div class="now">{now}</div><div class="around"><span>{before_text}</span><span>{after_text}</span></div></div>'

    def repl(match):
        numbers = [int(x) for x in match.group(1).split(",")]
        return '<div class="trails">' + "".join(trail(run) for run in _runs(numbers)) + "</div>"

    return re.sub(r"<!--TRAIL:([0-9,]+)-->", repl, page)


def chunk_html(code_text, lang, explanation, stations=()):
    return (
        '<div class="chunk">'
        f'<pre class="code hl" tabindex="0"><code>{highlight_code(code_text, lang)}</code></pre>'
        f'<div class="why">{station_badges(stations)}{explanation}</div>'
        "</div>"
    )


def file_block(project_dir, relpath, chunks, lang, where, file_id=None):
    """Render a real project file as a series of annotated chunks.

    chunks is a list of (anchor, stations, explanation_html). Each anchor is the
    start of the first line of its chunk. The first anchor must be "".
    The rendered chunks always cover the whole file, because each one runs
    from its anchor to the next anchor.
    """
    text = (Path(project_dir) / relpath).read_text()
    lines = text.rstrip("\n").split("\n")
    starts = []
    position = 0
    for index, (anchor, _, _) in enumerate(chunks):
        if index == 0:
            assert anchor == "", "first chunk anchor must be empty"
            starts.append(0)
            continue
        found = None
        for i in range(position, len(lines)):
            if anchor.startswith("ends:"):
                matches = lines[i].endswith(anchor[5:].strip()) and lines[i].startswith("# -")
            else:
                matches = lines[i].startswith(anchor)
            if matches:
                found = i
                break
        assert found is not None, f"anchor not found in {relpath}: {anchor!r}"
        starts.append(found)
        position = found + 1
    starts.append(len(lines))

    parts = []
    for index, (_, stations, explanation) in enumerate(chunks):
        piece = "\n".join(lines[starts[index]:starts[index + 1]]).strip("\n")
        parts.append(chunk_html(piece, lang, explanation, stations))

    fid = file_id or "file-" + relpath.replace("/", "-").replace(".", "-")
    return (
        f'<figure class="file" id="{fid}">'
        f'<figcaption><span class="fname">{esc(relpath)}</span>'
        f'<span class="where">{esc(where)}</span>'
        f'<button class="copy" type="button" data-code="{esc(text)}">Copy file</button></figcaption>'
        + "".join(parts)
        + "</figure>"
    )


def snippet(text, lang="text", caption=None, copy=True):
    cap = f'<p class="cap">{caption}</p>' if caption else ""
    btn = f'<button class="copy" type="button" data-code="{esc(text)}">Copy</button>' if copy else ""
    return (
        f'<div class="snippet">{cap}{btn}'
        f'<pre class="code hl" tabindex="0"><code>{highlight_code(text, lang)}</code></pre></div>'
    )


def annotated(items, lang, caption=None):
    """Annotated chunks for text that is not a project file (for example raw HTTP)."""
    body = "".join(chunk_html(code, lang, why, stations) for code, why, stations in items)
    cap = f'<figcaption><span class="fname">{caption}</span></figcaption>' if caption else ""
    return f'<figure class="file">{cap}{body}</figure>'


def box(kind, label, body):
    cls = "box" if kind == "note" else f"box {kind}"
    return f'<aside class="{cls}"><span class="label">{label}</span>{body}</aside>'


def goal(bullets, label="In this step you will"):
    """A box that says, in a few bullets, what the reader is about to make or learn."""
    items = "".join(f"<li>{b}</li>" for b in bullets)
    return f'<aside class="box goal"><span class="label">{label}</span><ul>{items}</ul></aside>'


def make_steps(items):
    """Numbered steps for the actions a reader performs, such as creating a file or running a command."""
    return '<ol class="make">' + "".join(f"<li>{i}</li>" for i in items) + "</ol>"


def check(items, label="Check that it works"):
    """A box that says what the reader should see when the step has worked."""
    lis = "".join(f"<li>{i}</li>" for i in items)
    return f'<aside class="box check"><span class="label">{label}</span><ul>{lis}</ul></aside>'


def deeper(title, body, tag="Optional"):
    """A collapsed block for detail that a reader can skip."""
    return f'<details class="deeper"><summary><span class="tag">{tag}:</span>{title}</summary><div class="inner">{body}</div></details>'


def predict(body):
    return box("note", "A prediction to make first", body)


def tryit(body):
    return box("try", "Try it", body)


def section(sec_id, part, title, body):
    return f'<section id="{sec_id}"><h2><span class="part">{part}</span>{title}</h2>{body}</section>'


def png_data_uri(path):
    data = base64.b64encode(Path(path).read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


# ---------------------------------------------------------------- diagrams


def journey_svg(server_label):
    """Sequence diagram of one click, twelve numbered stations."""
    bx, sx, dx = 160, 560, 930
    width, height = 1080, 800

    def badge(n, x, y):
        return (
            f'<circle class="dot" cx="{x}" cy="{y}" r="15"/>'
            f'<text class="t-on" x="{x}" y="{y + 5}" text-anchor="middle" font-size="14">{n}</text>'
        )

    def selfnote(x, y, w, text, side="right"):
        left = x + 26 if side == "right" else x - 26 - w
        return (
            f'<rect class="note" x="{left}" y="{y - 20}" width="{w}" height="40" rx="8"/>'
            f'<text x="{left + 12}" y="{y + 5}" font-size="15">{text}</text>'
        )

    def arrow(x1, x2, y, label, back=False, bad=False):
        cls = "arrow back" if back else "arrow"
        direction = 1 if x2 > x1 else -1
        end = x2 - 10 * direction
        mid = (x1 + x2) / 2
        head = (
            f'<path class="{cls}" d="M {x2 - 12 * direction} {y - 7} L {x2} {y} L {x2 - 12 * direction} {y + 7}" />'
        )
        return (
            f'<path class="{cls}" d="M {x1} {y} L {end} {y}"/>{head}'
            f'<text x="{mid}" y="{y - 12}" font-size="14.5" text-anchor="middle">{label}</text>'
        )

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="jt jd">',
        '<title id="jt">The journey of one click</title>',
        '<desc id="jd">A sequence diagram with three lanes, the browser, the server and the database, showing twelve numbered stations from the click to the repainted screen.</desc>',
    ]
    for x, name, sub in [(bx, "Browser", "HTML, CSS and a script"), (sx, "Server", server_label), (dx, "Database", "SQLite file")]:
        parts.append(f'<line class="lane" x1="{x}" y1="84" x2="{x}" y2="{height - 20}"/>')
        parts.append(f'<rect class="head" x="{x - 105}" y="16" width="210" height="62" rx="10"/>')
        parts.append(f'<text class="strong" x="{x}" y="43" text-anchor="middle" font-size="17">{name}</text>')
        parts.append(f'<text class="t-muted" x="{x}" y="64" text-anchor="middle" font-size="13.5">{sub}</text>')

    # station 1
    parts.append(badge(1, bx, 130))
    parts.append(selfnote(bx, 130, 250, "The click event fires"))
    # stations 2 and 3
    parts.append(arrow(bx, sx, 200, "POST /api/slots/A1/buy"))
    parts.append(badge(2, bx + 40, 226))
    parts.append(f'<text class="t-muted" x="{bx + 64}" y="231" font-size="13.5">fetch builds the request</text>')
    parts.append(badge(3, sx - 40, 226))
    parts.append(f'<text class="t-muted" x="{sx - 62}" y="231" font-size="13.5" text-anchor="end">it travels to port 8000</text>')
    # 4, 5
    parts.append(badge(4, sx, 280))
    parts.append(selfnote(sx, 280, 290, "The route table picks a handler"))
    parts.append(badge(5, sx, 335))
    parts.append(selfnote(sx, 335, 290, "The input is checked"))
    # 6
    parts.append(arrow(sx, dx, 400, "UPDATE ... SET stock = stock - 1"))
    parts.append(badge(6, sx + 40, 426))
    parts.append(f'<text class="t-muted" x="{sx + 64}" y="431" font-size="13.5">the SQL travels over a connection</text>')
    # 7
    parts.append(badge(7, dx, 480))
    parts.append(selfnote(dx, 480, 250, "Row changed and committed", side="left"))
    parts.append(arrow(dx, sx, 535, "1 row changed", back=True))
    # 8
    parts.append(badge(8, sx, 590))
    parts.append(selfnote(sx, 590, 290, "The result becomes JSON"))
    # 9
    parts.append(arrow(sx, bx, 655, "200 OK with a JSON body", back=True))
    parts.append(badge(9, sx - 40, 681))
    parts.append(f'<text class="t-muted" x="{sx - 62}" y="686" font-size="13.5" text-anchor="end">status, headers and body</text>')
    # 10, 11, 12
    parts.append(badge(10, bx, 715))
    parts.append(selfnote(bx, 715, 330, "fetch hands the reply to our script"))
    parts.append(badge(11, bx, 760))
    parts.append(selfnote(bx, 760, 330, "The script changes the DOM"))
    # station 12 sits to the right so the diagram stays inside its frame
    parts.append(badge(12, sx + 120, 760))
    parts.append(f'<text x="{sx + 146}" y="765" font-size="15">The browser repaints the screen</text>')
    parts.append("</svg>")
    return "".join(parts)


def trust_svg():
    width, height = 1080, 400
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="tt td">',
        '<title id="tt">Who controls what</title>',
        '<desc id="td">The visitor controls the browser, so the server checks every request. Only the server can reach the database.</desc>',
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)"/></marker>'
        '<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--bad)"/></marker></defs>',
    ]
    boxes = [
        (30, 300, "zone-bad", "The visitor's browser", "Not under our control",
         ["The visitor can edit the page,", "run any script in the console,", "or send requests by hand."]),
        (390, 300, "zone-good", "Our server", "Under our control",
         ["It checks every request,", "owns every SQL statement,", "and decides what is allowed."]),
        (750, 300, "zone-db", "The database", "Reachable only from the server",
         ["It holds the data and the rules", "(constraints) that protect it,", "and it never faces the visitor."]),
    ]
    for x, w, cls, title, sub, lines in boxes:
        parts.append(f'<rect class="{cls}" x="{x}" y="120" width="{w}" height="220" rx="12"/>')
        parts.append(f'<text class="strong" x="{x + w / 2}" y="156" text-anchor="middle" font-size="18">{title}</text>')
        parts.append(f'<text class="t-muted" x="{x + w / 2}" y="180" text-anchor="middle" font-size="14.5">{sub}</text>')
        for i, line in enumerate(lines):
            parts.append(f'<text x="{x + w / 2}" y="{222 + i * 28}" text-anchor="middle" font-size="15">{line}</text>')
    parts.append('<path class="arrow" d="M 330 215 L 388 215" marker-end="url(#ah)"/>')
    parts.append('<path class="arrow" d="M 690 215 L 748 215" marker-end="url(#ah)"/>')
    parts.append('<text x="360" y="203" text-anchor="middle" font-size="13">requests</text>')
    parts.append('<text x="720" y="203" text-anchor="middle" font-size="13">our SQL</text>')
    parts.append('<path class="arrow bad" d="M 180 118 C 180 40, 900 40, 900 116" marker-end="url(#ahb)"/>')
    parts.append('<text class="strong" x="540" y="62" text-anchor="middle" font-size="16" style="fill: var(--bad)">No direct route from the browser to the database</text>')
    parts.append("</svg>")
    return "".join(parts)


def shell(title, description, nav_html, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<style>{CSS}</style>
{extra_head}
</head>
<body>
{body}
<script>{JS}</script>
</body>
</html>
"""
