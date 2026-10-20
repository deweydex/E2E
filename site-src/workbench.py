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


# Words that get a hover explanation in the workbench. Most come from the tutorial, so the two sites explain a word in the same way.
WB_TERMS = [
    "route table", "handler", "service worker", "JSON", "DOM", "SQL injection", "SQL", "API", "endpoint", "status code",
    "placeholder", "schema", "primary key", "constraint", "transaction", "HTTP", "request", "response", "server", "client",
    "query", "row", "column", "HTML", "CSS", "JavaScript", "CORS", "prepared statement",
]
WB_EXTRA = {
    "route": "One entry in the server's list: a method and a path, and the code or query that answers them.",
    "method": "The kind of action a request asks for. GET reads, and POST changes something.",
    "path": "The part of the address that says which thing the request is about, such as /api/slots.",
    "body": "The data that travels with a request or a response, usually JSON.",
    "event": "Something the browser notices, such as a click, that a script can react to.",
    "script": "A piece of JavaScript that runs inside a page.",
    "database": "The program that stores the tables and answers queries.",
    "table": "Rows and columns of data with a name, such as slots.",
    "parameter": "A value that travels separately from the SQL, such as :slot. The database can only treat it as data.",
    "timeline": "The list of steps that one request goes through, from the click to the screen update.",
    "station": "One stop on the journey of a request. The tutorial numbers them 1 to 12.",
    "handler file": "The file in which you write your own handlers. The machine in server.ts calls them.",
}


def workbench_terms():
    """The hover texts as { word: text }, for the script of the workbench."""
    import terms

    defs = terms.definitions()
    result = {name: defs[name] for name in WB_TERMS}
    result.update(WB_EXTRA)
    return result


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
<button type="button" class="plain" id="open-setup">Change setup</button>
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
<ol id="chips" class="chips"><li><b>1</b> Click</li><li><b>2&ndash;3</b> Request</li><li><b>4</b> Route</li><li><b>6&ndash;7</b> SQL</li><li><b>8&ndash;9</b> Response</li><li><b>10&ndash;12</b> Screen</li></ol>
<div class="tl-controls">
<div class="stepper" role="group" aria-label="Step through the request">
<button type="button" class="plain" id="step-start" title="Go to the first step" disabled>&laquo; Start</button>
<button type="button" class="plain" id="step-back" title="Go back one step" disabled>&lsaquo; Back</button>
<span id="step-pos" aria-live="polite">No steps yet</span>
<button type="button" class="plain primary" id="step-forward" title="Go forward one step" disabled>Forward &rsaquo;</button>
<button type="button" class="plain" id="step-end" title="Run to the last step" disabled>End &raquo;</button>
</div>
<label title="When this is ticked, a request stops after every step and waits for Forward"><input type="checkbox" id="stepping" checked> Stop at each step</label>
<label><input type="checkbox" id="follow"> Follow in the code</label>
<span id="tl-state" role="status"></span>
<button type="button" class="plain" id="download-project">Download project</button>
<details class="logbox"><summary>Log</summary><div class="log-panel"><pre id="log"></pre><button type="button" class="plain" id="clear-log">Clear</button></div></details>
</div>
</div>
<div id="cards" class="cards" tabindex="0" aria-label="Steps of the current request"></div>
</section>
<div id="intro" class="intro" role="dialog" aria-modal="true" aria-labelledby="intro-title">
<div class="intro-card">
<section id="intro-choose">
<h1 id="intro-title">Set up the workbench</h1>
<p class="intro-lead">Choose how you want to work. You can change any of this later with <b>Change setup</b>.</p>
<p id="intro-saved" hidden><button type="button" class="plain primary" id="intro-continue">Continue with my saved project</button> <span>or start a new one below.</span></p>
<fieldset><legend>1. What do you want to start from?</legend>
<label class="opt"><input type="radio" name="intro-mode" value="explore" checked><span><b>Explore</b> A finished vending machine with four pages. Press Buy and watch the request travel.</span></label>
<label class="opt"><input type="radio" name="intro-mode" value="own"><span><b>Bring your own</b> A small page to build on. Upload your own HTML, CSS and SQL if you have them.</span></label>
<div id="intro-upload" hidden><label class="upload-line">Upload your files (optional) <input type="file" id="intro-files" multiple accept=".html,.htm,.css,.js,.sql,.txt,.ts,.py"></label><p id="intro-staged" class="quiet"></p></div>
</fieldset>
<fieldset><legend>2. How much do you want to write?</legend>
<label class="opt"><input type="radio" name="intro-level" value="beginner" checked><span><b>Beginner</b> You write HTML, CSS and SQL. The address names the query, so the server stays out of your way.</span></label>
<label class="opt"><input type="radio" name="intro-level" value="intermediate"><span><b>Intermediate</b> You also write <code>routes.txt</code>, which maps each method and path to a query.</span></label>
<label class="opt"><input type="radio" name="intro-level" value="advanced"><span><b>Advanced</b> You write the handlers yourself, in the server language you choose.</span></label>
</fieldset>
<fieldset><legend>3. Which language does the server use?</legend>
<label class="opt"><input type="radio" name="intro-language" value="ts" checked><span><b>TypeScript</b> Runs at once.</span></label>
<label class="opt"><input type="radio" name="intro-language" value="py"><span><b>Python</b> Downloads about 10 MB the first time.</span></label>
</fieldset>
<p class="intro-actions"><button type="button" class="plain primary" id="intro-next">Show me the project &rsaquo;</button></p>
</section>
<section id="intro-files-view" hidden>
<h1>Your project</h1>
<p class="intro-lead" id="intro-summary"></p>
<div id="intro-guide"></div>
<h2>How a request uses these files</h2>
<ol id="intro-flow" class="flow"></ol>
<p class="intro-actions"><button type="button" class="plain" id="intro-back">&lsaquo; Change my choices</button> <button type="button" class="plain primary" id="intro-open">Open the workbench &rsaquo;</button></p>
</section>
</div>
</div>
<div id="busy" role="status"></div>
<div id="tip" role="tooltip" hidden></div>
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
        "terms": workbench_terms(),
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
