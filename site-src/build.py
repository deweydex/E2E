"""Build the tutorial site: python.html, typescript.html, index.html and the two zips."""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import diagrams  # noqa: F401,E402  (extends lib.CSS and lib.JS)
import lib  # noqa: E402
import terms  # noqa: E402
import theme  # noqa: E402

theme.apply()

import svgfiles  # noqa: E402
import py_edition  # noqa: E402
import shared_a as A  # noqa: E402
import shared_b as B  # noqa: E402
import ts_edition  # noqa: E402
import workbench  # noqa: E402

W = Path(__file__).resolve().parent.parent
DIST = W / "docs"

MACHINE = lib.png_data_uri(W / "machine.png")


def build_sections(E, edition):
    sections = [
        A.sec_start(E, MACHINE),
    ]
    if hasattr(edition, "sec_try_first"):
        sections.append(edition.sec_try_first())
    sections += [
        A.sec_journey(E),
        edition.sec_build_db(),
        edition.sec_build_server(),
        edition.sec_build_page(),
        edition.sec_build_script(),
        B.sec_run(E),
        B.sec_http(E),
        B.sec_experiments(E),
        B.sec_choices(E),
        B.sec_extensions(E),
        B.sec_glossary(E),
    ]
    return sections


def toc_html(sections, sibling_href, sibling_label):
    items = []
    for sec in sections:
        match = re.match(r'<section id="([^"]+)"><h2><span class="part">([^<]+)</span>(.*?)</h2>', sec, re.S)
        assert match, "section without heading: " + sec[:80]
        sec_id, part, title = match.groups()
        label = title if not part.startswith("Step ") else f"{part.replace('Step ', '')}. {title}"
        items.append(f'<li><a href="#{sec_id}">{label}</a></li>')
    return (
        '<nav class="toc" aria-label="Contents"><details open><summary>Contents</summary>'
        f'<ol>{"".join(items)}</ol></details>'
        f'<div class="sibling"><a href="index.html">All editions</a><br><a href="{sibling_href}">{sibling_label}</a></div></nav>'
    )


def build_edition(E, edition, filename, sibling_href, sibling_label, title):
    sections = build_sections(E, edition)
    titles = [s["title"] for s in diagrams.stations_data(E)]
    sections = [lib.build_trails(section, titles) for section in sections]
    nav = toc_html(sections, sibling_href, sibling_label)
    body = (
        '<div class="shell">' + nav + "<main>"
        f"<header><h1>{title}</h1></header>" + terms.mark("".join(sections)) + "</main></div>"
    )
    page = lib.shell(
        f"{title} ({E['name']} edition)",
        "A guided tour from a button click to a database row and back: what a server, an API, SQL and JSON are, with every line of a working project explained.",
        nav,
        body,
    )
    (DIST / filename).write_text(page)
    return page


def banner_html(starting, ready, served_by):
    return (
        f'<body>\n  <p id="sim-banner" role="status" data-starting="{starting}" data-ready="{ready}" data-served-by="{served_by}">Starting...</p>\n'
        '  <script>\n    // A page opened from a file cannot load modules or service workers, so say so plainly.\n'
        '    if (location.protocol === "file:") {\n      const banner = document.getElementById("sim-banner");\n'
        '      banner.textContent = "This demo needs a web server. Open the tutorial through http, for example with: python -m http.server";\n'
        '      banner.classList.add("failed");\n    }\n  </script>\n'
    )


def demo_page(project, banner):
    html_text = (project / "public" / "index.html").read_text()
    replacements = [
        ('href="/style.css"', 'href="style.css"'),
        ('  <!-- The script comes last, so every element it looks for already exists. -->\n  <script type="module" src="/app.js"></script>\n',
         '  <!-- host.js starts the simulated server, and then loads app.js, the same file as in the project. -->\n  <script type="module" src="host.js"></script>\n'),
        ("<body>\n", banner),
        ("</head>", DEMO_STYLE + "</head>"),
    ]
    for old, new in replacements:
        assert old in html_text, "demo page: missing " + old[:40]
        html_text = html_text.replace(old, new, 1)
    return html_text


def copy_common(demo, project):
    source = W / "demo-src"
    for name in ["sw.js", "host.js"]:
        shutil.copy(source / "common" / name, demo / name)
    shutil.copy(project / "public" / "style.css", demo / "style.css")


def build_demo():
    """The Python edition's simulated server: Pyodide runs the real Python files."""
    demo = DIST / "demo"
    (demo / "py").mkdir(parents=True, exist_ok=True)
    project = W / "vending-py"
    source = W / "demo-src"
    copy_common(demo, project)
    shutil.copy(source / "py" / "worker.js", demo / "worker.js")
    shutil.copy(source / "py" / "adapter.py", demo / "py" / "adapter.py")
    shutil.copy(project / "server.py", demo / "py" / "server.py")
    shutil.copy(project / "setup_db.py", demo / "py" / "setup_db.py")
    shutil.copy(project / "public" / "app.js", demo / "app.js")
    banner = banner_html(
        "Starting Python in your browser. The first visit downloads about 10 MB.",
        "Simulated server: your browser is running the Python data layer and routes. Reload the page to reset the machine.",
        "Python running in this browser (Pyodide)",
    )
    (demo / "vending.html").write_text(demo_page(project, banner))


def strip_types(code):
    with tempfile.NamedTemporaryFile("w", suffix=".ts", delete=False) as handle:
        handle.write(code)
    result = subprocess.run(["node", str(Path(__file__).parent / "strip.mjs"), handle.name], capture_output=True, text=True)
    os.unlink(handle.name)
    assert result.returncode == 0, result.stderr
    return result.stdout


def indent(code, spaces=4):
    return "\n".join((" " * spaces + line) if line.strip() else line for line in code.split("\n"))


def build_demo_ts():
    """The TypeScript edition's simulated server: sql.js stands in for node:sqlite."""
    demo = DIST / "demo-ts"
    demo.mkdir(parents=True, exist_ok=True)
    project = W / "vending-ts"
    source = W / "demo-src"
    copy_common(demo, project)

    compiled = project / "public" / "app.js"
    assert compiled.exists() and compiled.stat().st_mtime >= (project / "client" / "app.ts").stat().st_mtime, "run npm run build in vending-ts first"
    shutil.copy(compiled, demo / "app.js")

    # Cut the data layer and the route layer out of the real server.ts.
    server_text = (project / "src" / "server.ts").read_text()
    region_start = server_text.index("// The shape of one slot.")
    region_end = server_text.index("// --- HTTP layer")
    region = server_text[region_start:region_end].replace("import.meta.dirname", '"/app/src"')
    machine_js = strip_types(region)

    # The real setup script, without its import lines.
    setup_text = (project / "src" / "setup-db.ts").read_text()
    setup_text = re.sub(r"(?m)^import .*;\n", "", setup_text).replace("import.meta.dirname", '"/app/src"')
    setup_js = strip_types(setup_text)

    adapter_js = strip_types((source / "ts" / "adapter.ts").read_text())
    shim_js = (source / "ts" / "node-sqlite-shim.js").read_text()

    worker = (source / "ts" / "worker.template.js").read_text()
    for marker, code in [
        ("/*@@SHIM@@*/", shim_js),
        ("/*@@ADAPTER@@*/", adapter_js),
        ("/*@@SETUP@@*/", indent(setup_js)),
        ("/*@@MACHINE@@*/", indent(machine_js)),
    ]:
        assert marker in worker
        worker = worker.replace(marker, code)
    (demo / "worker.js").write_text(worker)

    banner = banner_html(
        "Starting SQLite in your browser. The first visit downloads about 1 MB.",
        "Simulated server: your browser is running the data layer and routes from server.ts, over sql.js. Reload the page to reset the machine.",
        "TypeScript running in this browser (sql.js)",
    )
    (demo / "vending.html").write_text(demo_page(project, banner))


DEMO_STYLE = """  <style>
    #sim-banner { margin: 0 auto 12px; max-width: 480px; padding: 8px 12px; font: 13px/1.4 system-ui, sans-serif;
      background: #fff3cd; color: #5c4400; border: 1px solid #e6c765; border-radius: 8px; }
    #sim-banner.failed { background: #f8d7da; color: #58151c; border-color: #e4a2a8; }
    body { padding-top: 12px; flex-direction: column; align-items: center; }
    #sim-banner { box-sizing: border-box; width: min(100%, 480px); }
    html[data-theme="dark"] body { background: #12161d; }
    html[data-theme="dark"] #sim-banner { background: #3a2c10; color: #f0d79a; border-color: #6b5420; }
    html[data-theme="dark"] #sim-banner.failed { background: #3d1b1e; color: #ffb3b8; border-color: #7a3a40; }
  </style>
  <script>
    // Follow the theme that the reader chose in the tutorial's settings, which live in the same origin.
    (function () {
      let theme = "system";
      try { theme = (JSON.parse(localStorage.getItem("tutorial-settings") || "{}").theme) || "system"; } catch (error) { /* ignore */ }
      const dark = theme === "dark" || (theme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches);
      if (dark) document.documentElement.dataset.theme = "dark";
    })();
  </script>
"""


def make_zip(project_dir, zip_path, excluded_names, excluded_files):
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    root = project_dir.name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(project_dir.rglob("*")):
            if path.is_dir():
                continue
            relative = path.relative_to(project_dir)
            if any(part in excluded_names for part in relative.parts):
                continue
            if relative.as_posix() in excluded_files:
                continue
            archive.write(path, f"{root}/{relative.as_posix()}")


LANDING_CSS = """
<style>
.landing { max-width: 880px; margin: 0 auto; padding: 56px 20px 90px; }
.landing .cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; margin-top: 28px; }
.landing .card { display: block; border: 1px solid var(--line); background: var(--surface); border-radius: 12px; padding: 18px 20px; color: inherit; text-decoration: none; }
.landing .card:hover { border-color: var(--accent); }
.landing .card.wide { grid-column: 1 / -1; }
.landing .card h2 { margin: 0 0 6px; padding: 0; font-size: 1.3rem; }
.landing .card p { margin: 0; color: var(--muted); }
</style>
"""


def build_landing(diagram_items):
    gallery = "".join(f'<li><a href="diagrams/{name}">{description}</a></li>' for name, description in diagram_items)
    body = """
<div class="landing">
<h1>From a click to a database row and back</h1>
<p class="lede">A guided tour of what happens when you press a button on a web page and the screen changes: the browser, the network, a server, an API, SQL, a database, JSON and the DOM. Every line of a small working project is explained beside the code, together with the reason for each choice.</p>
<p>Both editions build the same vending machine page and explain the same ideas. They differ in the language of the server, and the page itself is identical. Choose one, or read both and compare how each language expresses the same design.</p>
<div class="cards">
<a class="card" href="python.html"><h2>Python edition</h2><p>The server, the database code and the setup script are written in Python, using only its standard library. Needs Python 3.10 or newer.</p></a>
<a class="card" href="typescript.html"><h2>TypeScript edition</h2><p>Everything is TypeScript on Node, including the short script in the page. Needs Node 22.18 or newer.</p></a>
<a class="card wide" href="workbench/index.html"><h2>Workbench</h2><p>A split screen with the browser on the left and the server and database on the right. Press a button and follow the request through a timeline, one stage at a time. Edit the HTML, the CSS, the SQL and the server code, or upload your own files. It has three levels and offers a TypeScript server and a Python server.</p></a>
</div>
<h2>The diagrams as files</h2>
<p>Every diagram in the tutorial is also a standalone SVG file that you can use in your own worksheets and slides. Each file carries its own colours and follows the light or dark setting of the device that opens it.</p>
<ul class="gallery">""" + gallery + """</ul>
</div>
"""
    page = lib.shell(
        "From a click to a database row and back",
        "A two-edition tutorial on servers, APIs and databases for beginners.",
        "",
        body,
        extra_head=LANDING_CSS,
    )
    (DIST / "index.html").write_text(page)


def main():
    DIST.mkdir(exist_ok=True)
    py_page = build_edition(
        py_edition.E, py_edition, "python.html", "typescript.html", "Read the TypeScript edition",
        "How a click reaches a database and comes back",
    )
    ts_page = build_edition(
        ts_edition.E, ts_edition, "typescript.html", "python.html", "Read the Python edition",
        "How a click reaches a database and comes back",
    )
    diagram_items = svgfiles.write_all(DIST, (py_edition.E, ts_edition.E))
    build_landing(diagram_items)
    build_demo()
    build_demo_ts()
    workbench.build()
    make_zip(W / "vending-py", DIST / "downloads" / "vending-py.zip", {"__pycache__", "vending.db"}, set())
    make_zip(W / "vending-ts", DIST / "downloads" / "vending-ts.zip", {"node_modules", "vending.db"}, {"public/app.js"})
    print("python.html", len(py_page) // 1024, "KB;", "typescript.html", len(ts_page) // 1024, "KB")


if __name__ == "__main__":
    main()
