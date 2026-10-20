"""Builds the workbench: a split-screen page with a browser, a server and a timeline.

The page runs entirely in the visitor's browser. The TypeScript server uses sql.js,
and the Python server (when present) uses Pyodide. Everything except Pyodide is
shipped as plain script files, so the page also opens from a folder on disk.
"""

import json
import re
import shutil
from pathlib import Path

import lib
import theme

# The folder that holds site-src, workbench-src and dist.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# The workbench's own source files.
SOURCE_DIR = PROJECT_ROOT / "workbench-src"
SITE_DIR = PROJECT_ROOT / "docs"
WORKBENCH_DIR = SITE_DIR / "workbench"

# The addresses that the sample pages use, for each level. The pages contain placeholders such as @@LIST@@,
# and fill_address_placeholders() swaps in the address for the chosen level.
# At the Beginner level the address names a query. At the other levels the address follows a route.
# {query.slot} is read from the page's own address, and {slot_id} is read from the row of the button that was pressed.
ADDRESSES = {
    "beginner": {
        "LIST": "/api/list_slots",
        "GET": "/api/get_slot?slot={query.slot}",
        "BUY": "/api/buy_slot?slot={slot_id}",
        "RESTOCK": "/api/restock_slot?slot={query.slot}",
        "SALES": "/api/list_sales",
    },
    "intermediate": {
        "LIST": "/api/slots",
        "GET": "/api/slots/{query.slot}",
        "BUY": "/api/slots/{slot_id}/buy",
        "RESTOCK": "/api/slots/{query.slot}/restock",
        "SALES": "/api/sales",
    },
}
# The Advanced level uses the same addresses as the Intermediate level.
ADDRESSES["advanced"] = ADDRESSES["intermediate"]

# The four pages of the vending machine.
PAGE_NAMES = ["index.html", "item.html", "restock.html", "sales.html"]


def read_text(path):
    """Return the text of a file."""
    return path.read_text()


def fill_address_placeholders(text, level):
    """Replace @@NAME@@ placeholders in a sample file with the address for this level."""
    for key, value in ADDRESSES[level].items():
        text = text.replace("@@" + key + "@@", value)
    return text


def sample_files(mode, level):
    """Return the project files for a mode and level as { file name: text }. The starter project borrows style.css and client.js from the sample."""
    files = {}
    if mode == "explore":
        folder = SOURCE_DIR / "sample"
        names = PAGE_NAMES + ["style.css", "client.js", "schema.sql", "queries.sql", "routes.txt", "handlers.ts", "handlers.py"]
    else:
        folder = SOURCE_DIR / "starter"
        names = ["index.html", "schema.sql", "queries.sql", "routes.txt", "handlers.ts", "handlers.py"]
    for name in names:
        path = folder / name
        if not path.exists():
            path = SOURCE_DIR / "sample" / name
        if path.exists():
            files[name] = fill_address_placeholders(read_text(path), level)
    for name in ["style.css", "client.js"]:
        if name not in files:
            files[name] = read_text(SOURCE_DIR / "sample" / name)
    return files


def server_sources():
    """Return the text of each server file, by language and level. Students read these files, and the workbench runs them."""
    result = {"ts": {}, "py": {}}
    for level in ["beginner", "intermediate", "advanced"]:
        ts = SOURCE_DIR / "engine" / "ts" / (level + ".ts")
        py = SOURCE_DIR / "engine" / "py" / (level + ".py")
        if ts.exists():
            result["ts"][level] = read_text(ts)
        if py.exists():
            result["py"][level] = read_text(py)
    return result


def code_pane(side, accept, extra_tools="", extra_after=""):
    """The HTML for one code editor with its file tabs and buttons. The accept text lists the file endings that its Upload button offers."""
    return f"""<div class="code" id="code-{side}">
<div class="code-bar">
<div class="tabs" role="tablist" aria-label="Files"></div>
<div class="tools">
<button type="button" class="upload">Upload</button>
<button type="button" class="download">Download</button>
<button type="button" class="revert">Revert</button>{extra_tools}
<input class="picker" type="file" multiple hidden accept="{accept}">
</div></div>{extra_after}
<p class="notice" id="notice-{side}" role="status" hidden></p>
<p class="lock-note" hidden>This file is read only. The workbench runs exactly this code, so you can read it and learn from it.</p>
{'<p class="problem" id="server-problem" role="alert" hidden></p>' if side == "right" else ""}
<div class="editor"></div>
</div>"""


def page_html():
    """The HTML of the whole workbench page."""
    settings = theme.SETTINGS_HTML
    # The site settings panel offers a choice about long lines of code. The workbench editors do not wrap, so we remove that choice.
    settings = re.sub(r'<fieldset><legend>Long lines of code</legend>.*?</fieldset>\n', "", settings, flags=re.S)
    left_code = code_pane(
        "left", ".html,.htm,.css,.js",
        extra_tools='\n<button type="button" class="add">Add file</button>\n<button type="button" class="delete">Remove</button>',
        extra_after='\n<form id="add-bar" hidden><input type="text" placeholder="about.html" aria-label="Name of the new file"><button type="submit">Create</button></form>',
    )
    right_code = code_pane("right", ".sql,.txt,.ts,.py")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Front End Back End Workbench</title>
<meta name="description" content="A split-screen workbench that shows a request travelling from a browser page to a server and a database and back.">
{theme.HEAD_SCRIPT}
<link rel="stylesheet" href="workbench.css">
</head>
<body data-view="browser">
<header class="wb-head">
<div class="title"><h1>Workbench</h1></div>
<div class="controls">
<div class="ctl"><span class="ctl-label" id="l-mode">Mode</span><div class="seg" data-setting="mode" role="group" aria-labelledby="l-mode"><button type="button" data-value="explore">Explore</button><button type="button" data-value="own">Bring your own</button></div></div>
<div class="ctl"><span class="ctl-label" id="l-level">Level</span><div class="seg" data-setting="level" role="group" aria-labelledby="l-level"><button type="button" data-value="beginner">Beginner</button><button type="button" data-value="intermediate">Intermediate</button><button type="button" data-value="advanced">Advanced</button></div></div>
<div class="ctl"><span class="ctl-label" id="l-language">Server</span><div class="seg" data-setting="language" role="group" aria-labelledby="l-language"><button type="button" data-value="ts">TypeScript</button><button type="button" data-value="py">Python</button></div></div>
<a class="home" href="../index.html">Back to the tutorial</a>
{settings}
</div>
</header>
<div class="helpline"><p><span id="mode-help"></span><span id="level-help"></span></p>
<div class="helptools"><button type="button" class="linkish" id="start-over">Start over</button>
<details class="try"><summary>Things to try</summary><div class="try-panel"><p>Pick one and see what the timeline shows.</p><ol id="try-list"></ol></div></details></div></div>
<div class="viewtabs" role="group" aria-label="Part of the workbench to show">
<button type="button" data-view="browser" aria-pressed="true">Browser</button>
<button type="button" data-view="server" aria-pressed="false">Server</button>
<button type="button" data-view="timeline" aria-pressed="false">Timeline</button>
</div>
<div id="main" class="wb-main">
<section id="pane-left" class="pane" aria-label="Front end">
<h2 class="pane-title"><b>Front end</b> &middot; the browser</h2>
<div id="left-top" class="pane-top">
<div class="chrome"><button type="button" id="back" aria-label="Back" disabled>&larr;</button><button type="button" id="reload" aria-label="Reload the page">&#8635;</button><div class="address" id="address">machine.local/index.html</div></div>
<iframe id="preview" sandbox="allow-scripts allow-forms" title="The page as the browser shows it"></iframe>
</div>
<div id="split-left" class="splitter h" role="separator" aria-orientation="horizontal" aria-label="Resize the page and its code" tabindex="0"></div>
{left_code}
</section>
<div id="split-x" class="splitter v" role="separator" aria-orientation="vertical" aria-label="Resize the front end and the back end" tabindex="0"></div>
<section id="pane-right" class="pane" aria-label="Back end">
<h2 class="pane-title"><b>Back end</b> &middot; the server and the database</h2>
<div id="right-top" class="pane-top">
<div class="subtabs" data-group="server" role="tablist">
<button type="button" role="tab" data-name="data" aria-selected="true">Database</button>
<button type="button" role="tab" data-name="routes" aria-selected="false">Routes</button>
<button type="button" role="tab" data-name="sql" aria-selected="false">Try SQL</button>
<span class="spacer"></span>
<button type="button" class="action" id="reset-db">Reset database</button>
</div>
<div class="panel" data-panel="server" data-name="data"><div id="db-tables"></div></div>
<div class="panel" data-panel="server" data-name="routes" hidden><div id="routes-view"></div></div>
<div class="panel" data-panel="server" data-name="sql" hidden>
<p>This box talks to the database directly, the way the server does after it receives a request.</p>
<form id="sql-form"><textarea id="sql-input" aria-label="SQL to run" spellcheck="false">SELECT * FROM slots;</textarea><button type="submit">Run</button></form>
<div id="sql-result"></div>
</div>
</div>
<div id="split-right" class="splitter h" role="separator" aria-orientation="horizontal" aria-label="Resize the database and the server code" tabindex="0"></div>
{right_code}
</section>
</div>
<div id="split-timeline" class="splitter h" role="separator" aria-orientation="horizontal" aria-label="Resize the timeline" tabindex="0"></div>
<section id="timeline" aria-label="Timeline of the request">
<div class="tl-bar">
<h2>Timeline</h2>
<ol id="chips" class="chips"><li>Click</li><li>Request</li><li>Route</li><li>SQL</li><li>Response</li><li>Screen</li></ol>
<div class="tl-controls">
<span class="ctl-label" id="l-speed">Speed</span><div class="seg" data-setting="speed" role="group" aria-labelledby="l-speed"><button type="button" data-value="fast">Fast</button><button type="button" data-value="slow">Slow</button><button type="button" data-value="step">Step</button></div>
<button type="button" class="plain" id="next" disabled>Next</button>
<button type="button" class="plain" id="skip" disabled>Skip to end</button>
<label><input type="checkbox" id="follow"> Follow in the code</label>
<span id="tl-state" role="status"></span>
<button type="button" class="plain" id="download-project">Download project</button>
<details class="logbox"><summary>Log</summary><div class="log-panel"><pre id="log"></pre><button type="button" class="plain" id="clear-log">Clear</button></div></details>
</div>
</div>
<div id="cards" class="cards" tabindex="0" aria-label="Steps of the current request"></div>
</section>
<div id="busy" role="status"></div>
<script src="vendor/sql-wasm-data.js"></script>
<script src="vendor/sql-wasm.js"></script>
<script src="vendor/sucrase.js"></script>
<script src="vendor/prism.js"></script>
<script src="data.js"></script>
<script src="workbench.js"></script>
<script>{theme.SETTINGS_JS}</script>
</body>
</html>
"""


def build():
    """Write the workbench into dist/workbench: the page, the styles, the data, the scripts and the libraries."""
    WORKBENCH_DIR.mkdir(parents=True, exist_ok=True)
    (WORKBENCH_DIR / "vendor").mkdir(exist_ok=True)
    for name in ["sql-wasm.js", "sql-wasm-data.js", "sucrase.js", "prism.js"]:
        shutil.copy(SOURCE_DIR / "vendor" / name, WORKBENCH_DIR / "vendor" / name)
    shutil.copy(SOURCE_DIR / "pyodide-engine.js", WORKBENCH_DIR / "pyodide-engine.js")

    # data.js holds everything the page needs to start: the project files, the server files and the bridge script.
    data = {
        "samples": {mode: {level: sample_files(mode, level) for level in ADDRESSES} for mode in ["explore", "own"]},
        "engines": server_sources(),
        "bridge": read_text(SOURCE_DIR / "bridge.js"),
    }
    (WORKBENCH_DIR / "data.js").write_text("window.WB_DATA = " + json.dumps(data) + ";\n")

    # The three scripts are joined into one file and wrapped in a function, so their names do not leak into the page.
    parts = [read_text(SOURCE_DIR / n) for n in ["wb-editor.js", "wb-engines.js", "wb-app.js"]]
    (WORKBENCH_DIR / "workbench.js").write_text('(function () {\n"use strict";\n' + "\n".join(parts) + "\n})();\n")

    css = theme.token_css() + "\n" + theme.SETTINGS_CSS + "\n" + read_text(SOURCE_DIR / "workbench.css")
    (WORKBENCH_DIR / "workbench.css").write_text(css)

    # The Python engine loads before the workbench script, which looks for it when the page starts.
    html = page_html().replace('<script src="workbench.js"></script>', '<script src="pyodide-engine.js"></script>\n<script src="workbench.js"></script>')
    (WORKBENCH_DIR / "index.html").write_text(html)
    print("workbench built:", WORKBENCH_DIR)


if __name__ == "__main__":
    import diagrams  # noqa: F401  (importing it extends lib.CSS, which the token reader expects)

    theme.apply()
    build()
