"""Shared concept sections, part one: overview to the shapes of data."""

from lib import (
    annotated,
    box,
    predict,
    section,
    snippet,
)
from diagrams import dl_link, journey_svg, shapes_figure, stepper_html, trust_svg, url_figure


def fill(text, E):
    for key, value in E.items():
        if isinstance(value, str):
            text = text.replace(f"@@{key}@@", value)
    return text


def sec_start(E, machine_uri):
    body = fill(
        """
<div class="prose">
<p class="lede">Press Buy on a vending machine page and the number of snacks left changes a moment later. That small change involves a browser, a network, a server program, a database and a file on a disk. This page follows one click through all of them, slows it down, and lets you build every stage yourself.</p>
</div>

<div class="hero-grid">
<div class="prose">
<p>@@intro_languages@@</p>
<p>Along the way we answer a set of questions that usually stay hidden. What does a database do that a file cannot? How does a program talk to a database? What is a server, and what does it mean to set up an API? What is JSON, and why does the page need it? How does something that arrives from a server end up changing the screen?</p>
<p>We explain each piece of code beside the code itself, including the reasons behind the choices we made. Some choices have alternatives that are just as good, and we point those out too.</p>
<div class="downloads">
<a class="btn" href="@@zip@@" download>Download the project (.zip)</a>
</div>
</div>
<figure>
<img src="@@machine@@" alt="The finished vending machine page: four slots, each with a name, a price, a stock count and a Buy button. One slot is sold out and greyed.">
<figcaption>The page we build. Three slots have stock and one is sold out.</figcaption>
</figure>
</div>

<div class="prose">
<h3>What you need</h3>
<p>@@prereq@@</p>
<h3>How to read this page</h3>
<p>Each code file appears in short pieces, with the code on the left and the explanation beside it. The explanation carries badges such as <span class="badge">Station 4</span> that point back to the journey in Part 1, so you can always see where a piece of code sits in the whole trip. Boxes headed <em>A prediction to make first</em> invite you to answer in your own words before you read on. Your answer does not need to be right. The gap between your answer and the explanation is where most of the learning happens.</p>
</div>
""",
        {**E, "machine": machine_uri},
    )
    return section("start", "Start here", "From click to row and back again", body)


def sec_journey(E):
    stations = [
        ("The browser notices the click.",
         "A click is an <dfn>event</dfn>, a message the browser creates whenever something happens on the page, such as a click, a key press or the page finishing its loading. Our script has asked the browser to run a function whenever a click lands inside the area that holds the slots."),
        ("The script builds a request.",
         "The script calls <code>fetch</code>, a browser function that sends a <dfn>request</dfn>, which is a message to another program that says what we want and how we want it done. Here the message says, in effect, <em>please buy one item from slot A1</em>."),
        ("The request travels.",
         "The message goes to an address made of a <dfn>host</dfn> (which computer) and a <dfn>port</dfn> (which program on that computer). On your own machine the browser and the server share one computer, so the message never leaves it, yet it follows the same rules as a message sent across the world."),
        ("The server chooses a handler.",
         "The <dfn>server</dfn> is a program that waits for requests and answers them. It reads the message, compares the method and the path with a table of <dfn>routes</dfn>, and passes the request to the function responsible for that route. We call that function the <dfn>handler</dfn>."),
        ("The handler checks the input.",
         "<dfn>Validation</dfn> means testing that what arrived is well formed before we use it. Slot ids look like A1 or B2, and anything else is turned away with an explanation."),
        ("The handler sends SQL to the database.",
         "<dfn>SQL</dfn> (Structured Query Language) is the language we use to ask a relational database to find or change rows. The handler sends it through a <dfn>connection</dfn>, an open line of communication between a program and a database."),
        ("The database changes the row.",
         "The database applies the change as a <dfn>transaction</dfn>, a group of steps that either all happen or none happen. Then it reports how many rows it changed."),
        ("The handler packages the result.",
         "Inside the server the result is a @@record_word@@. A network carries only bytes, so the handler converts the result into <dfn>JSON</dfn> (JavaScript Object Notation), a text format for structured data. Turning structured data into text is called <dfn>serialising</dfn> it."),
        ("The server sends a response.",
         "The <dfn>response</dfn> has three parts: a <dfn>status code</dfn> that says how things went (200 means success), <dfn>headers</dfn> that describe the message, and a <dfn>body</dfn> that holds the JSON."),
        ("The reply reaches the script.",
         "Waiting for a network reply takes time, so <code>fetch</code> gives back a <dfn>promise</dfn>, an object that stands for a value that has not arrived yet. When the reply arrives the promise settles, and our script carries on from the line where it waited."),
        ("The script changes the DOM.",
         "The <dfn>DOM</dfn> (Document Object Model) is the browser's live tree of objects, one for every element on the page. The script edits the tree: new text, a changed class, a disabled button."),
        ("The browser repaints the screen.",
         "The browser notices that the tree has changed, works out the new layout and redraws. We write no code for this step, and it is the reason an edit to the DOM becomes visible."),
    ]
    items = "".join(f"<li><strong>{t}</strong>{d}</li>" for t, d in stations)
    body = fill(
        f"""
<div class="prose">
<p>Suppose you press Buy on slot A1. The screen changes after a few milliseconds, and we can split those milliseconds into twelve stations. The diagram shows them in order, and the list below it says what happens at each one.</p>
</div>
{stepper_html(E, journey_svg(E["server_label"]))}
<ol class="stations">{items}</ol>
<div class="prose">
<p>You do not need to memorise the list. Each later part zooms in on a few stations, and the code explanations carry matching badges so that you can find your place again. If you only remember one thing from this part, remember that the browser and the server are two separate programs that cooperate by exchanging messages, and that the database sits behind the server, never in front of it.</p>
</div>
""",
        E,
    )
    return section("journey", "Part 1", "The journey of one click", body)


def sec_why_db(E):
    body = fill(
        """
<div class="prose">
<h3>What a page and a server forget</h3>
<p>Reload a page and every variable in its script disappears. The server forgets in the same way. If it kept the stock count in a variable, stopping the program would reset the count, and two copies of the server would disagree about it. Something outside both programs has to keep the count safe between visits, and it has to keep exactly one shared count, even when many people press Buy at the same moment.</p>
<p>A text file could store the numbers. Think about what you would need to add to make that file behave. You would want a way to find one row without reading the whole file, a rule that stops two programs from writing at once and ruining each other's work, a promise that a half finished change is undone if the power fails, and a rule that stock can never drop below zero. A <dfn>database management system</dfn> is a program that has already solved those problems, and a <dfn>relational database</dfn> keeps its data in tables of rows and columns.</p>

<h3>Five things a database gives us</h3>
<p><strong>Persistence.</strong> The data survives when the programs stop. <strong>Structure.</strong> A <dfn>schema</dfn> declares the tables, the columns and the type of each column, so every row has the same shape. <strong>Queries.</strong> SQL lets us ask for exactly the rows we want, and the database finds them quickly, using an index when one exists. <strong>Safe changes.</strong> Transactions make a group of changes all-or-nothing, and they keep simultaneous users from tripping over each other. <strong>Rules.</strong> <dfn>Constraints</dfn> such as <code>NOT NULL</code> and <code>CHECK (stock &gt;= 0)</code> make the database itself refuse bad data, even if a bug in our code tries to write it.</p>

<p>Our vending machine needs one table. It has a <dfn>primary key</dfn>, <code>slot_id</code>, which is a column whose value is different in every row and so identifies exactly one row.</p>
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
<div class="prose">
<h3>Why the price is a whole number of cents</h3>
<p>You might expect a column called <code>price</code> holding <code>1.75</code>. Computers store numbers with fractions in binary, and many decimal fractions cannot be written exactly in binary. In most languages <code>0.1 + 0.2</code> gives <code>0.30000000000000004</code>. A shop that adds up prices with numbers like that will eventually be wrong by a cent. Whole numbers are exact, so we store <code>175</code> cents and convert to euros only at the last moment, when we display the price.</p>

<h3>Where SQLite fits</h3>
<p>SQLite is a database engine that lives inside a library that our program loads. It keeps everything in one ordinary file, and it needs no installation and no separate server. Larger systems such as PostgreSQL and MySQL run as their own server programs and accept connections from other programs. All of them speak SQL, and they all have connections, transactions and constraints, so what you learn here carries over. We choose SQLite for the same reason a driving lesson starts in a quiet car park: it removes everything that is not the lesson.</p>
</div>
""",
        E,
    )
    return section("why-db", "Part 2", "Why a database at all", body)


def sec_trust(E):
    body = fill(
        """
<div class="prose">
<p>A fair question follows from Part 2. If the page needs data from the database, why can the page not ask the database itself? Why do we put a server in the middle?</p>
<p>There are two answers, a practical one and a more important one. The practical answer is that a browser has no way to open a database. SQLite is a file on the server's disk, and bigger databases listen for a specialised protocol on a port that should never face the public internet.</p>
<p>The more important answer concerns trust. <strong>The visitor owns the browser.</strong> They can read every line of the page, edit it, run any script in the developer console, or skip the page altogether and send requests by hand from a terminal. Anything we ship to the browser is readable, and any check that happens only in the browser can be skipped. So the rules of the vending machine cannot live there. They live on the server, where the visitor cannot reach them, and the server is the only program that holds a route to the database.</p>
</div>
<figure class="diagram"><div class="scroll">
@@trust_svg@@
</div><figcaption>The browser is outside our control, so the server treats every request as untrusted input. The database is reachable only through the server.@@trust_dl@@</figcaption>
</figure>
<div class="prose">
<p>Look at how the Buy request in this project is designed. The browser names a slot and nothing else. It does not say what the price is, how many items to take, or which SQL to run. Those decisions belong to the server.</p>
</div>
""".replace("@@trust_svg@@", trust_svg()).replace("@@trust_dl@@", dl_link("trust.svg"))
        + predict(
            "<p>Imagine that the page sent <code>{ \"slot\": \"A1\", \"price_cents\": 0 }</code> with every purchase and the server trusted it. What would a curious visitor do with the developer console? Then think about which other parts of our design would protect us even if the server were careless, and which would not.</p>"
        ),
        E,
    )
    return section("trust", "Part 3", "Why the browser cannot reach the database", body)


def sec_http(E):
    request_items = [
        (
            "POST /api/slots/a1/buy HTTP/1.1",
            "<p>The first line of a request is the <dfn>request line</dfn>. It holds the <dfn>method</dfn> (<code>POST</code>, the kind of action we want), the <dfn>path</dfn> (<code>/api/slots/a1/buy</code>, which thing we want it done to) and the protocol version.</p>",
            [2],
        ),
        (
            "Host: 127.0.0.1:8000\nUser-Agent: curl/8.5.0\nAccept: */*",
            "<p>Next come <dfn>headers</dfn>, one per line, each written as a name, a colon and a value. They carry extra information about the request. <code>Host</code> names the server the client believes it is talking to, <code>User-Agent</code> names the client program, and <code>Accept</code> lists the formats the client can read. The tool <code>curl</code> sends fewer headers than a browser does.</p>",
            [2, 3],
        ),
        (
            "",
            "<p>A blank line ends the headers. A <code>POST</code> request may carry a <dfn>body</dfn> after the blank line, for example a form or a JSON document. This one carries none, because the path already says everything the server needs.</p>",
            [2],
        ),
    ]
    response_items = [
        (
            E["http_status_line"],
            E["http_status_note"],
            [9],
        ),
        (
            E["http_headers"],
            "<p>The response headers describe the body. <code>Content-Type</code> tells the client how to read it, in this case JSON written in UTF-8, a standard way of turning characters into bytes. <code>Content-Length</code> says how many bytes of body follow. <code>Cache-Control: no-store</code> asks the browser never to reuse an old copy, which keeps our development loop reliable, because an edit then shows up on the next reload. " + E["http_headers_extra"] + "</p>",
            [9],
        ),
        (
            '\n{"slot_id": "A1", "item_name": "Sparkling Water", "price_cents": 175, "stock": 7}'.replace(": ", E["json_colon"]).replace(", ", E["json_comma"]),
            "<p>After the blank line comes the <dfn>body</dfn>. This is the JSON that the script will parse at Station 10.</p>",
            [8, 9],
        ),
    ]
    status_rows = [
        ("200", "OK", "The request worked and the body holds the result."),
        ("400", "Bad Request", "The client sent something we cannot make sense of, such as the slot id <code>hello</code>."),
        ("404", "Not Found", "The request was well formed, yet nothing exists at that address, such as slot <code>Z9</code>."),
        ("409", "Conflict", "The request was fine, but it clashes with the current state of things. Buying from a sold-out slot is a conflict."),
        ("500", "Internal Server Error", "Something broke inside the server. The fault is ours and not the client's."),
    ]
    rows = "".join(f"<tr><td><strong>{c}</strong></td><td>{n}</td><td>{d}</td></tr>" for c, n, d in status_rows)
    body = fill(
        """
<div class="prose">
<h3>Clients, servers, hosts and ports</h3>
<p>A <dfn>client</dfn> is a program that starts a conversation, and a <dfn>server</dfn> is a program that waits for conversations to start. The word <em>server</em> also names the computer that runs such a program, but in this tutorial it always means the program. Our browser is the client, and our @@name@@ program is the server.</p>
<p>To reach a server, a client needs an address. The <dfn>host</dfn> says which computer. We use <code>127.0.0.1</code>, a special address that always means <em>this computer</em>, and the name <code>localhost</code> means the same thing. A computer can run many servers at once, so the <dfn>port</dfn>, a number between 0 and 65535, tells the operating system which waiting program should receive the message. We pick port 8000. Together, the scheme, host, port and path make a <dfn>URL</dfn>:</p>
<p><code>http://127.0.0.1:8000/api/slots/A1/buy</code></p>
@@url_figure@@
<h3>HTTP, the agreement between them</h3>
<p>A <dfn>protocol</dfn> is an agreement about the order and shape of messages, and <dfn>HTTP</dfn> (HyperText Transfer Protocol) is the agreement that browsers and web servers use. Every exchange has two messages, a request and a response, and both are plain text with a fixed layout. We captured a real exchange from the running project, and we can read it piece by piece.</p>
</div>
""",
        E,
    ).replace("@@url_figure@@", url_figure(E["handler_call"], E["slug"])) + annotated(request_items, "http", "The request the client sends") + annotated(response_items, "http", "The response the server sends back") + fill(
        """
<div class="prose">
<h3>Status codes</h3>
<p>The status code is a three digit number that tells the client how things went before it reads a single byte of the body. The first digit gives the family: 2 means success, 4 means the client made a mistake, and 5 means the server did. We use five codes.</p>
</div>
<div class="tablewrap">
<table class="tbl"><thead><tr><th>Code</th><th>Name</th><th>When we send it</th></tr></thead><tbody>
@@rows@@
</tbody></table>
</div>
<div class="prose">
<h3>Methods, and a server with no memory</h3>
<p>We use two methods. <code>GET</code> asks the server to read something and promises to change nothing. <code>POST</code> asks the server to do something, and the server is allowed to change data when it does. HTTP is also <dfn>stateless</dfn>, which means the server treats every request as a fresh conversation and keeps no memory of the previous one. The state of our machine, the stock count, therefore lives in the database and never in a variable inside the server.</p>
</div>
""".replace("@@rows@@", rows),
        E,
    )
    return section("http", "Part 4", "Servers, ports and HTTP", body)


def sec_api(E):
    rows = [
        ("GET", "/api/slots", "Lists every slot", "200 with a JSON array of slots", "None expected"),
        ("GET", "/api/slots/A1", "Shows one slot", "200 with one slot", "400 for a malformed id, 404 for a missing slot"),
        ("POST", "/api/slots/A1/buy", "Buys one item from the slot", "200 with the updated slot", "400, 404, and 409 when the slot is sold out"),
    ]
    trs = "".join(
        f"<tr><td><code>{m}</code></td><td><code>{u}</code></td><td>{w}</td><td>{s}</td><td>{e}</td></tr>"
        for m, u, w, s, e in rows
    )
    body = fill(
        """
<div class="prose">
<p>The word <dfn>API</dfn> stands for Application Programming Interface. An interface is the part of a program that other programs are allowed to use, and it describes what you may ask for and what you will get back, without saying anything about how the answer is produced. A <dfn>web API</dfn> offers that interface over HTTP, and it usually replies with JSON, because JSON is easy for programs to read.</p>
<p>Setting up an API therefore means making four decisions and then writing code that keeps the promises those decisions make.</p>
<p><strong>The first decision is which things the API offers.</strong> Each thing gets a URL. Ours are the collection of all slots, <code>/api/slots</code>, and each single slot, <code>/api/slots/A1</code>. An address like this is often called an <dfn>endpoint</dfn>.</p>
<p><strong>The second decision is which actions are allowed on each thing.</strong> The method says which action. Reading uses <code>GET</code>, and buying uses <code>POST</code>.</p>
<p><strong>The third decision is the shape of the data in both directions.</strong> The <dfn>contract</dfn> says which fields exist and what type each one has.</p>
<p><strong>The fourth decision is how outcomes are reported.</strong> We use status codes for the category and a JSON message for the detail.</p>
</div>
<div class="tablewrap">
<table class="tbl">
<thead><tr><th>Method</th><th>URL</th><th>What it does</th><th>On success</th><th>On failure</th></tr></thead>
<tbody>@@trs@@</tbody>
</table>
</div>
<div class="prose">
<p>The two shapes of JSON that cross the network are a slot and an error:</p>
</div>
""".replace("@@trs@@", trs),
        E,
    ) + snippet('{\n  "slot_id": "A1",\n  "item_name": "Sparkling Water",\n  "price_cents": 175,\n  "stock": 7\n}\n\n{ "error": "Oat Biscuits is sold out." }', "json", "A slot, followed by an error") + fill(
        """
<div class="prose">
<p>The contract matters because the page and the server are written at different times, and possibly by different people. If the server renames <code>stock</code> to <code>quantity</code>, the page breaks, and nothing in the browser will warn anyone beforehand. @@contract_note@@</p>
<h3>Why buying uses POST</h3>
<p>A method is <dfn>safe</dfn> when calling it changes nothing, and <code>GET</code> is meant to be safe. Browsers, link previews in chat apps and search engine crawlers all send <code>GET</code> requests freely, and they may repeat them. If buying were a <code>GET</code>, a chat app that previews a link could buy a snack. Buying is also not <dfn>idempotent</dfn>, which means that doing it twice does not leave the same result as doing it once: two presses buy two snacks. Reading is idempotent, and that is why it is safe to refresh a page as often as you like.</p>
<h3>REST, in one paragraph</h3>
<p>Many web APIs follow a style called <dfn>REST</dfn> (Representational State Transfer). In this style, URLs name things with nouns, the method chooses the action, and each request is complete in itself. Our API borrows that style without trying to follow every rule of it. The route table in the server file is the API written down as code, and in Part 8 you will see that the table is only a few lines long.</p>
</div>
""",
        E,
    )
    return section("api", "Part 5", "What an API is, and what setting one up means", body)


def sec_shapes(E):
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
        from lib import esc
        parts.append(f'<div class="stage"><h4>{title}</h4><pre>{esc(code)}</pre></div>')
        if i < len(steps):
            parts.append(f'<div class="step"><b>&darr;</b> {steps[i]}</div>')
    body = fill(
        """
<div class="prose">
<p>The same fact, that slot A1 has seven items left, takes five different shapes on its way from the disk to the screen. Following the shapes explains a great deal about why the code looks the way it does.</p>
</div>
@@shapes_fig@@
<div class="pipeline">@@parts@@</div>
<div class="prose">
<p>Only the third shape can cross the network, because a network carries bytes and the others are structures inside the memory of one program. <dfn>Serialising</dfn> turns a structure into text, as in the step from shape 2 to shape 3. <dfn>Parsing</dfn> turns text back into a structure, as in the step from shape 3 to shape 4. Every arrow in the pipeline is a place where something can go wrong. A key can be missing, a number can arrive as text, or a value can be empty, and we will meet each of those problems in the code.</p>
</div>
""".replace("@@parts@@", "".join(parts)).replace("@@shapes_fig@@", shapes_figure(E)),
        E,
    ) + predict(
        "<p>The fourth and fifth shapes both live in the browser. Why might we bother with the fourth at all, instead of writing the JSON text straight into the page?</p>"
    )
    return section("shapes", "Part 6", "The same data in five shapes", body)
