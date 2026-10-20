"""Shared teaching text, part one: the opening, the journey, and the short concept pieces that sit inside the build steps."""

from lib import (
    check,
    deeper,
    esc,
    goal,
    predict,
    section,
    snippet,
)
import terms
from diagrams import dl_link, journey_svg, shapes_figure, stations_data, stepper_html, trust_svg, url_figure


def fill(text, E):
    """Replace @@name@@ markers with the value of the same name in the edition's settings."""
    for key, value in E.items():
        if isinstance(value, str):
            text = text.replace(f"@@{key}@@", value)
    return text


# ---------------------------------------------------------------- the opening


def sec_start(E, machine_uri):
    needs = "".join(f"<li>{item}</li>" for item in E["needs"])
    body = fill(
        """
<div class="prose">
<p class="lede">Press Buy on a vending machine page and the number of snacks left changes a moment later. In this tutorial you build that whole machine, one piece at a time, and you watch a click travel from the page to a database and back.</p>
</div>

<div class="hero-grid">
<div class="prose">
<h3>You will build</h3>
<ul>
<li>A <strong>database</strong> that stores the machine's slots.</li>
<li>A <strong>server</strong> that answers requests about those slots.</li>
<li>A <strong>page</strong> with a Buy button.</li>
<li>A short <strong>script</strong> that connects the page to the server.</li>
</ul>
<h3>You will learn</h3>
<ul>
<li>What a database, a server and an API each do.</li>
<li>How a click becomes a request, a query and a changed screen.</li>
<li>How to watch that traffic in your browser.</li>
</ul>
<div class="downloads">
<a class="btn" href="@@zip@@" download>Download the finished project (.zip)</a>
</div>
</div>
<figure>
<img src="@@machine@@" alt="The finished vending machine page: four slots, each with a name, a price, a stock count and a Buy button. One slot is sold out and greyed.">
<figcaption>The page you build. Three slots have stock and one is sold out.</figcaption>
</figure>
</div>

<div class="prose">
<h3>You need</h3>
<ul>@@needs@@</ul>
<p>@@intro_languages@@</p>
<h3>How to use this page</h3>
<ul>
<li>Work through Steps 1 to 6 in order. Each step has a goal, the code to make, a check, and a short explanation.</li>
<li>Code appears in small pieces, with the explanation beside each piece.</li>
<li>A badge such as <span class="badge">Station 4</span> points back to the journey in Step 1.</li>
<li>A box headed <em>A prediction to make first</em> asks you to guess before you read on. A wrong guess is fine, because the gap between your guess and the answer is where you learn.</li>
<li>A box marked <em>Optional</em> holds extra detail that you can skip.</li>
<li>The <em>Going deeper</em> sections after Step 6 cover HTTP, experiments and design choices.</li>
</ul>
</div>
""".replace("@@needs@@", needs),
        {**E, "machine": machine_uri},
    )
    return section("start", "Start here", "From click to row and back again", body)


# ----------------------------------------------------------- step 1: the journey


def sec_journey(E):
    stations = stations_data(E)
    items = "".join(f"<li><strong>{s['title']}</strong> {s['text']}</li>" for s in stations)
    body = (
        goal(
            [
                "Follow one click through twelve stations, from the button to the database and back to the screen.",
                "See which program handles each station: the browser, the server or the database.",
                "Meet the words that the later steps explain in detail. You do not need to remember them yet.",
            ],
            "In this step you will",
        )
        + '<div class="prose"><p>Press Buy on slot A1. The screen changes after a few milliseconds, and those milliseconds hold twelve stations. Ten words appear on the diagram, so here they are first, in plain terms. Each one gets a fuller explanation in the step that builds it.</p>'
        + terms.intro_list(["request", "response", "fetch", "route table", "handler", "SQL", "connection", "transaction", "JSON", "DOM"])
        + '<p>Use the buttons under the diagram to step through the stations. In the diagram and in the text, a dotted underline marks a key word, and hovering over it shows what it means.</p></div>'
        + stepper_html(E, journey_svg(E["server_label"]))
        + deeper("The twelve stations as a list", f'<ol class="stations">{items}</ol>', "Reference")
        + check(
            [
                "The browser and the server are two separate programs. They work together by sending messages.",
                "A click becomes a request, the server answers with a response, and the script uses that response to change the page.",
                "The server holds the rules, and the browser is never trusted to follow them.",
                "The database sits behind the server and never in front of it.",
                "Each of the next steps builds one part of this picture.",
            ],
            "Keep these ideas",
        )
    )
    return section("journey", "Step 1", "Follow one click", body)


# ------------------------------------------------- concept pieces for the build steps


def concept_database(E):
    """Short reasons for a database, placed at the start of Step 2."""
    return fill(
        """
<div class="prose">
<h3>Why a database?</h3>
<p>A page forgets everything when it reloads, and a server forgets everything when it stops. The stock count has to live somewhere that outlasts both, and every visitor has to see the same count. A text file could hold the numbers, but then you would solve several hard problems yourself. A <dfn>database</dfn> has already solved them. A <dfn>relational database</dfn> keeps its data in tables of rows and columns.</p>
<p>A database gives you five things:</p>
<ul>
<li><strong>Persistence.</strong> The data survives when the programs stop.</li>
<li><strong>Structure.</strong> A <dfn>schema</dfn> declares the tables, the columns and the type of each column.</li>
<li><strong>Queries.</strong> SQL asks for exactly the rows you want, and the database finds them quickly.</li>
<li><strong>Safe changes.</strong> A transaction makes a group of changes all-or-nothing, and keeps simultaneous users from spoiling each other's work.</li>
<li><strong>Rules.</strong> A <dfn>constraint</dfn> such as <code>CHECK (stock &gt;= 0)</code> makes the database refuse bad data, even when a bug in your code tries to write it.</li>
</ul>
<p>The machine needs one table. Its <dfn>primary key</dfn>, <code>slot_id</code>, is a column whose value differs in every row, so it identifies exactly one row.</p>
</div>
<div class="tablewrap">
<table class="tbl">
<thead><tr><th>slot_id</th><th>item_name</th><th>price_cents</th><th>stock</th></tr></thead>
<tbody>
<tr><td>A1</td><td>Sparkling Water</td><td>175</td><td>8</td></tr>
<tr><td>A2</td><td>Salted Peanuts</td><td>125</td><td>5</td></tr>
<tr><td>B1</td><td>Chocolate Bar</td><td>200</td><td>3</td></tr>
<tr><td>B2</td><td>Oat Biscuits</td><td>150</td><td>0</td></tr>
</tbody>
</table>
</div>
"""
        + deeper(
            "Why the price is a whole number of cents",
            "<p>Computers store fractions in binary, and many decimal fractions cannot be written exactly in binary. In most languages <code>0.1 + 0.2</code> gives <code>0.30000000000000004</code>. A shop that adds up prices like that will be wrong by a cent sooner or later. Whole numbers are exact, so the table stores <code>175</code> cents and the page converts to euros only when it shows the price.</p>",
        )
        + deeper(
            "Where SQLite fits",
            "<p>SQLite is a database that lives inside a library that your program loads. SQLite keeps everything in one ordinary file and needs no installation and no separate server. Larger systems such as PostgreSQL and MySQL run as their own server programs. All of them speak SQL, so what you learn here carries over. SQLite suits a first lesson the way a quiet car park suits a first driving lesson: nothing gets in the way.</p>",
        ),
        E,
    )


def concept_server(E):
    """The ideas behind a server and its API, placed at the start of Step 3."""
    rows = [
        ("GET", "/api/slots", "Lists every slot", "200 and a list of slots", "None expected"),
        ("GET", "/api/slots/A1", "Shows one slot", "200 and one slot", "400 for a malformed id, 404 for a missing slot"),
        ("POST", "/api/slots/A1/buy", "Buys one item", "200 and the updated slot", "400, 404, or 409 when sold out"),
    ]
    trs = "".join(
        f"<tr><td><code>{m}</code></td><td><code>{u}</code></td><td>{w}</td><td>{s}</td><td>{e}</td></tr>"
        for m, u, w, s, e in rows
    )
    first = fill(
        """
<div class="prose">
<h3>Two programs, one conversation</h3>
<ul>
<li>A <dfn>client</dfn> starts a conversation. Your browser is the client.</li>
<li>A <dfn>server</dfn> waits for conversations to start. Your @@name@@ program is the server.</li>
<li>The client needs an address. The <dfn>host</dfn> says which computer, and the <dfn>port</dfn> says which program on that computer. We use host <code>127.0.0.1</code>, which always means <em>this computer</em>, and port <code>8000</code>.</li>
<li>Host, port and <dfn>path</dfn> together make a <dfn>URL</dfn>, such as <code>http://127.0.0.1:8000/api/slots/A1/buy</code>. The server reads the path to decide what to do.</li>
</ul>
</div>
@@url_figure@@
<div class="prose">
<h3>Why the page never talks to the database</h3>
<p>The visitor owns the browser. They can read every line of the page, change it, run any script in the console, or skip the page and send requests by hand. A check that exists only in the browser can always be skipped. So the rules of the machine live on the server, and the server is the only program with a route to the database.</p>
</div>
<figure class="diagram"><div class="scroll">
@@trust_svg@@
</div><figcaption>The browser is outside your control, so the server treats every request as untrusted. The database is reachable only through the server.@@trust_dl@@</figcaption>
</figure>
<div class="prose">
<p>Look at how Buy is designed. The browser names a slot and nothing else. The browser does not say what the price is or which SQL to run. Those decisions belong to the server.</p>
</div>
""",
        E,
    ).replace("@@url_figure@@", url_figure(E["handler_call"], E["slug"])).replace("@@trust_svg@@", trust_svg()).replace("@@trust_dl@@", dl_link("trust.svg"))
    first += predict(
        "<p>Suppose the page sent <code>{ \"slot\": \"A1\", \"price_cents\": 0 }</code> with every purchase and the server trusted it. What could a curious visitor do with the developer console? Which other parts of the design would still protect us, and which would not?</p>"
    )
    second = fill(
        """
<div class="prose">
<h3>Design the API before you write it</h3>
<p>An <dfn>API</dfn> (Application Programming Interface) is the part of a program that other programs may use. A web API makes that part available over HTTP, and usually replies in JSON. Designing one means four decisions:</p>
<ul>
<li><strong>Which things does the API offer?</strong> Each thing gets a URL, called an <dfn>endpoint</dfn>. Ours are all the slots and each single slot.</li>
<li><strong>Which actions are allowed?</strong> The <dfn>method</dfn> names the action. <code>GET</code> reads, and <code>POST</code> changes something.</li>
<li><strong>What shape does the data have?</strong> The <dfn>contract</dfn> lists the fields and their types.</li>
<li><strong>How are outcomes reported?</strong> A <dfn>status code</dfn> gives the category, and a JSON message gives the detail. 200 means success, 400 means the client asked badly, 404 means nothing is there, and 409 means the request clashes with the current state.</li>
</ul>
</div>
<div class="tablewrap">
<table class="tbl">
<thead><tr><th>Method</th><th>URL</th><th>What it does</th><th>On success</th><th>On failure</th></tr></thead>
<tbody>@@trs@@</tbody>
</table>
</div>
<div class="prose">
<p>Two shapes of JSON cross the network, a slot and an error:</p>
</div>
""".replace("@@trs@@", trs),
        E,
    )
    second += snippet(
        '{\n  "slot_id": "A1",\n  "item_name": "Sparkling Water",\n  "price_cents": 175,\n  "stock": 7\n}\n\n{ "error": "Oat Biscuits is sold out." }',
        "json",
        "A slot, followed by an error",
    )
    second += fill(
        """
<div class="prose">
<p>The page and the server are written at different times. If the server renames <code>stock</code> to <code>quantity</code>, the page breaks without any warning. @@contract_note@@</p>
</div>
""",
        E,
    )
    return first + second


def concept_shapes(E):
    """The five shapes of one fact, placed at the start of Step 5."""
    stages = [
        ("1. A row in the database", "slot_id | item_name       | price_cents | stock\nA1      | Sparkling Water | 175         | 7"),
        ("2. " + E["shape2_title"], E["shape2_code"]),
        ("3. Text on the network (JSON)", '{"slot_id": "A1", "item_name": "Sparkling Water", "price_cents": 175, "stock": 7}'.replace(": ", E["json_colon"]).replace(", ", E["json_comma"])),
        ("4. An object in the browser's script", '{ slot_id: "A1", item_name: "Sparkling Water", price_cents: 175, stock: 7 }'),
        ("5. Elements in the DOM", '<p class="stock">7 left</p>'),
    ]
    steps = [E["shape_step_1"], E["shape_step_2"], "<code>response.json()</code> parses the text into an object", "<code>createSlotCard</code> copies the values into elements with <code>textContent</code>"]
    parts = []
    for i, (title, code) in enumerate(stages):
        parts.append(f'<div class="stage"><h4>{title}</h4><pre>{esc(code)}</pre></div>')
        if i < len(steps):
            parts.append(f'<div class="step"><b>&darr;</b> {steps[i]}</div>')
    html = fill(
        """
<div class="prose">
<h3>The same fact in five shapes</h3>
<p>The fact that slot A1 has seven items left takes five shapes on its way from the disk to the screen. The script you are about to write handles the last three.</p>
</div>
@@shapes_fig@@
<div class="pipeline">@@parts@@</div>
<div class="prose">
<ul>
<li>Only the third shape can cross the network, because a network carries text and bytes.</li>
<li><dfn>Serialising</dfn> turns a structure into text. <dfn>Parsing</dfn> turns text back into a structure.</li>
<li>Every arrow is a place where something can go wrong: a key can be missing, a number can arrive as text, or a value can be empty.</li>
</ul>
</div>
""".replace("@@parts@@", "".join(parts)).replace("@@shapes_fig@@", shapes_figure(E)),
        E,
    )
    html += predict(
        "<p>The fourth and fifth shapes both live in the browser. Why bother with the fourth, instead of writing the JSON text straight into the page?</p>"
    )
    return html
