"""Diagrams: hand-authored inline SVG plus the step-through stepper.

Each figure makes one claim. Colours come from CSS custom properties so the
diagrams follow the page's light and dark themes.
"""

import json

from lib import CSS, JS, esc  # noqa: F401  (CSS and JS are extended below)


def fill(text, E):
    for key, value in E.items():
        if isinstance(value, str):
            text = text.replace(f"@@{key}@@", value)
    return text


# ------------------------------------------------------------ station data


def stations_data(E):
    """The twelve stations: title, explanation, and what is in flight."""
    json_text = '{"slot_id": "A1", "item_name": "Sparkling Water", "price_cents": 175, "stock": 7}'
    json_text = json_text.replace(": ", E["json_colon"]).replace(", ", E["json_comma"])
    rows = [
        ("The browser notices the click.",
         "The page has a script that listens for clicks. The script wakes up when you press Buy. A click is one kind of <dfn>event</dfn>, a message the browser creates whenever something happens on the page.",
         '<button class="buy"> clicked inside <article data-slot="A1">'),
        ("The script builds a request.",
         "The script sends a message to the server, called a <dfn>request</dfn>. Here the request says <em>please buy one item from slot A1</em>. The script sends it with <code>fetch</code>, a function that the browser provides.",
         "POST /api/slots/A1/buy HTTP/1.1\nHost: 127.0.0.1:8000"),
        ("The request travels.",
         "The message goes to an address with two parts: the <dfn>host</dfn>, which is the computer, and the <dfn>port</dfn>, which is the program on that computer. Here both are on your own machine.",
         "host 127.0.0.1   (this computer)\nport 8000        (the server program)"),
        ("The server chooses a handler.",
         "The <dfn>server</dfn> is a program that waits for requests. The server reads the method and the path of the request, and picks the function that deals with that request. That function is called the <dfn>handler</dfn>.",
         E["route_row_flight"]),
        ("The handler checks the input.",
         "The handler checks that the slot id looks right, such as A1. Anything else is turned away with a message. Checking input like this is called <dfn>validation</dfn>.",
         E["validate_flight"]),
        ("The handler sends SQL to the database.",
         "<dfn>SQL</dfn> is the language for asking a database to find or change rows. The handler sends one SQL statement through a <dfn>connection</dfn>, which is an open line between the program and the database.",
         'UPDATE inventory SET stock = stock - 1\n WHERE slot_id = ? AND stock > 0\n-- the value "A1" travels separately'),
        ("The database changes the row.",
         "The database takes one away from the stock and says how many rows it changed. The database does this as a <dfn>transaction</dfn>, which means the change either happens completely or not at all.",
         "rows changed: 1\nstock of A1: 8 becomes 7"),
        ("The handler packages the result.",
         "The result becomes <dfn>JSON</dfn>, a text format that other programs can read. Only bytes can cross a network, so structured data has to become text first. This step is called serialising.",
         json_text),
        ("The server sends a response.",
         "The <dfn>response</dfn> holds a status code that says how it went (200 means it worked), some headers that describe the message, and a body that carries the JSON.",
         E["http_status_line"] + "\nContent-Type: application/json; charset=utf-8\n\n" + json_text),
        ("The reply reaches the script.",
         "The script receives the JSON and turns it back into an object. Waiting for a reply takes time, so <code>fetch</code> gives the script a <dfn>promise</dfn>, which stands for a value that has not arrived yet.",
         'await requestJson(...)  gives\n{ slot_id: "A1", item_name: "Sparkling Water",\n  price_cents: 175, stock: 7 }'),
        ("The script changes the DOM.",
         "The <dfn>DOM</dfn> is the browser's live tree of the elements on the page. The script edits that tree: new text, or a button that becomes disabled.",
         '<p class="stock">8 left</p>\nbecomes\n<p class="stock">7 left</p>'),
        ("The browser repaints the screen.",
         "The browser notices that the tree has changed and redraws. You write no code for this step, and that is why the screen updates.",
         "The browser lays out the changed card\nand draws it on the screen."),
    ]
    return [{"title": t, "text": fill(x, E), "flight": f} for t, x, f in rows]


def stepper_html(E, svg):
    data = stations_data(E)
    payload = json.dumps(data).replace("</", "<\\/")
    return (
        '<figure class="diagram stepper" id="stepper">'
        '<div class="scroll">' + svg + "</div>"
        '<figcaption>One click, twelve stations. Stations 1, 2, 10, 11 and 12 happen in the browser, station 3 is the network between the two programs, stations 4 to 9 happen in the server, and the database answers at stations 6 and 7. '
        "The buttons step through the stations one at a time and show what is travelling at each one." + dl_link(f"journey-{E['slug']}.svg") + "</figcaption>"
        '<div class="stepper-controls" role="group" aria-label="Step through the journey">'
        '<button type="button" id="step-prev" disabled>Previous</button>'
        '<button type="button" id="step-next">Step through</button>'
        '<button type="button" id="step-all" disabled>Show all</button>'
        '<span id="step-count" aria-live="polite"></span>'
        "</div>"
        '<div class="step-panel" id="step-panel" aria-live="polite" hidden>'
        '<h4 id="step-title"></h4><p id="step-text"></p>'
        '<p class="cap">In flight at this station</p><pre class="code" id="step-flight"></pre>'
        "</div>"

        f'<script type="application/json" id="stations-data">{payload}</script>'
        "</figure>"
    )


# ----------------------------------------------------------------- journey


def journey_svg(server_label):
    bx, sx, dx = 160, 560, 930
    width, height = 1080, 850

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

    def arrow(x1, x2, y, label, back=False):
        cls = "arrow back" if back else "arrow"
        d = 1 if x2 > x1 else -1
        mid = (x1 + x2) / 2
        return (
            f'<path class="{cls}" d="M {x1} {y} L {x2 - 10 * d} {y}"/>'
            f'<path class="{cls}" d="M {x2 - 12 * d} {y - 7} L {x2} {y} L {x2 - 12 * d} {y + 7}"/>'
            f'<text x="{mid}" y="{y - 12}" font-size="14.5" text-anchor="middle">{label}</text>'
        )

    def group(ns, inner):
        return f'<g class="station" data-n="{ns}">{inner}</g>'

    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Sequence diagram of one click: twelve numbered stations across the browser, the server and the database, from the click to the repainted screen.">',
    ]
    for x, name, sub in [(bx, "Browser", "HTML, CSS and a script"), (sx, "Server", server_label), (dx, "Database", "SQLite file")]:
        parts.append(f'<line class="lane" x1="{x}" y1="84" x2="{x}" y2="{height - 20}"/>')
        parts.append(f'<rect class="head" x="{x - 105}" y="16" width="210" height="62" rx="10"/>')
        parts.append(f'<text class="strong" x="{x}" y="43" text-anchor="middle" font-size="17">{name}</text>')
        parts.append(f'<text class="t-muted" x="{x}" y="64" text-anchor="middle" font-size="13.5">{sub}</text>')

    parts.append(group("1", badge(1, bx, 130) + selfnote(bx, 130, 250, "The click event fires")))
    parts.append(group("2 3", arrow(bx, sx, 200, "POST /api/slots/A1/buy")))
    parts.append(group("2", badge(2, bx + 40, 226) + f'<text class="t-muted" x="{bx + 64}" y="231" font-size="13.5">fetch builds it</text>'))
    parts.append(group("3", badge(3, sx - 40, 226) + f'<text class="t-muted" x="{sx - 62}" y="231" font-size="13.5" text-anchor="end">travels to :8000</text>'))
    parts.append(group("4", badge(4, sx, 280) + selfnote(sx, 280, 290, "The route table picks a handler")))
    parts.append(group("5", badge(5, sx, 335) + selfnote(sx, 335, 290, "The input is checked")))
    parts.append(group("6", arrow(sx, dx, 400, "UPDATE ... SET stock = stock - 1") + badge(6, sx + 40, 426) + f'<text class="t-muted" x="{sx + 64}" y="431" font-size="13.5">SQL travels over a connection</text>'))
    parts.append(group("7", badge(7, dx, 480) + selfnote(dx, 480, 250, "Row changed and committed", side="left") + arrow(dx, sx, 535, "1 row changed", back=True)))
    parts.append(group("8", badge(8, sx, 590) + selfnote(sx, 590, 290, "The result becomes JSON")))
    parts.append(group("9", arrow(sx, bx, 655, "200 OK with a JSON body", back=True) + badge(9, sx - 40, 681) + f'<text class="t-muted" x="{sx - 62}" y="686" font-size="13.5" text-anchor="end">status, headers and body</text>'))
    parts.append(group("10", badge(10, bx, 715) + selfnote(bx, 715, 330, "fetch hands the reply to our script")))
    parts.append(group("11", badge(11, bx, 760) + selfnote(bx, 760, 330, "The script changes the DOM")))
    parts.append(group("12", badge(12, bx, 805) + selfnote(bx, 805, 330, "The browser repaints the screen")))
    parts.append("</svg>")
    return "".join(parts)


# ------------------------------------------------------------------- trust


def trust_svg():
    width, height = 1080, 400
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="The visitor controls the browser, so the server checks every request. Only the server has a route to the database.">',
        '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)"/></marker>'
        '<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--bad)"/></marker></defs>',
    ]
    boxes = [
        (30, 300, "zone-bad", "The visitor's browser", "Not under our control",
         ["The visitor can edit the page,", "run any script in the console,", "or send requests by hand."]),
        (390, 300, "zone-good", "Our server", "Under our control",
         ["The server checks every request,", "owns every SQL statement,", "and decides what is allowed."]),
        (750, 300, "zone-db", "The database", "Reachable only from the server",
         ["The database holds the data and the rules", "(constraints) that protect it,", "and never faces the visitor."]),
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
    parts.append('<path class="arrow bad" d="M 180 118 C 180 66, 900 66, 900 116" marker-end="url(#ahb)"/>')
    parts.append('<text class="strong" x="540" y="34" text-anchor="middle" font-size="16" style="fill: var(--bad)">No direct route from the browser to the database</text>')
    parts.append("</svg>")
    return "".join(parts)


# --------------------------------------------------------------- url anatomy


def url_svg(handler_call):
    width, height = 1080, 500
    cw = 19  # width of one monospace character at 32px, enforced with textLength
    x0, y = 100, 86
    segments = [
        ("http", "seg1", True), ("://", None, False), ("127.0.0.1", "seg2", True),
        (":8000", "seg3", True), ("/api/slots", "seg4", True), ("/A1", "seg4", True), ("/buy", "seg4", True),
    ]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="A URL split into scheme, host, port and path, and the path matched against a route pattern that captures the slot id and passes it to the handler.">',
        '<defs><marker id="ah2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)"/></marker></defs>',
    ]
    x = x0
    for text, cls, boxed in segments:
        w = len(text) * cw
        if cls:
            parts.append(f'<rect class="{cls}" x="{x}" y="{y - 34}" width="{w}" height="50" rx="6"/>')
        parts.append(
            f'<text x="{x}" y="{y}" class="mono" font-size="32" textLength="{w}" lengthAdjust="spacing">{esc(text)}</text>'
        )
        x += w
    legend = [
        ("seg1", "scheme", "http", "The protocol. Here it is plain HTTP, the agreement that browsers and servers use."),
        ("seg2", "host", "127.0.0.1", "Which computer. This address always means this computer."),
        ("seg3", "port", ":8000", "Which program on that computer. Our server listens here."),
        ("seg4", "path", "/api/slots/A1/buy", "Which thing, and what to do with it. The route table reads this part."),
    ]
    for i, (cls, name, example, text) in enumerate(legend):
        ly = 150 + i * 38
        parts.append(f'<rect class="{cls}" x="{x0}" y="{ly - 18}" width="22" height="22" rx="4"/>')
        parts.append(f'<text class="strong" x="{x0 + 36}" y="{ly}" font-size="16">{name}</text>')
        parts.append(f'<text x="{x0 + 110}" y="{ly}" font-size="15.5">{text}</text>')
    # routing mechanism
    ry = 380
    parts.append(f'<text class="t-muted" x="40" y="{ry - 38}" font-size="14">How the server reads the path</text>')
    boxes = [
        (40, 250, "The path", "/api/slots/A1/buy"),
        (370, 340, "A row of the route table", "/api/slots/([^/]+)/buy"),
        (790, 260, "The handler call", handler_call),
    ]
    for bx, bw, title, code in boxes:
        parts.append(f'<rect class="note" x="{bx}" y="{ry - 22}" width="{bw}" height="74" rx="8"/>')
        parts.append(f'<text class="t-muted" x="{bx + 12}" y="{ry}" font-size="13">{title}</text>')
        parts.append(f'<text x="{bx + 12}" y="{ry + 30}" class="mono" font-size="15.5">{esc(code)}</text>')
    parts.append(f'<path class="arrow" d="M 292 {ry + 15} L 366 {ry + 15}" marker-end="url(#ah2)"/>')
    parts.append(f'<text x="329" y="{ry + 70}" font-size="13" text-anchor="middle">is tried against</text>')
    parts.append(f'<path class="arrow" d="M 712 {ry + 15} L 786 {ry + 15}" marker-end="url(#ah2)"/>')
    parts.append(f'<text x="749" y="{ry + 70}" font-size="13" text-anchor="middle">captured text "A1"</text>')
    parts.append("</svg>")
    return "".join(parts)


# ------------------------------------------------------------------ layers


def layers_svg(names):
    width, height = 1080, 560
    cx0, cw = 40, 520
    layers = [
        (116, "HTTP layer", names["http"], ["Knows methods, paths, status codes and headers.", "Never touches SQL."]),
        (240, "Route layer", names["route"], ["Knows which URL means which action,", "and what a valid slot id looks like."]),
        (364, "Data layer", names["data"], ["Knows SQL, transactions and the rules of the machine.", "Never touches HTTP or status codes."]),
    ]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Three layers of the server stacked between the browser and the database. Each layer calls only the one below it, and only the data layer talks to the database.">',
        '<defs><marker id="ah3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)"/></marker>'
        '<marker id="ah3b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/></marker></defs>',
    ]

    def endcap(y, label, cls):
        parts.append(f'<rect class="{cls}" x="{cx0}" y="{y}" width="{cw}" height="48" rx="10"/>')
        parts.append(f'<text class="strong" x="{cx0 + cw / 2}" y="{y + 30}" text-anchor="middle" font-size="16">{label}</text>')

    endcap(16, "The browser", "zone-bad")
    for y, title, fn_names, notes in layers:
        parts.append(f'<rect class="zone-good" x="{cx0}" y="{y}" width="{cw}" height="84" rx="10"/>')
        parts.append(f'<text class="strong" x="{cx0 + 16}" y="{y + 28}" font-size="17">{title}</text>')
        parts.append(f'<text x="{cx0 + 16}" y="{y + 56}" class="mono" font-size="13.5">{esc(fn_names)}</text>')
        parts.append(f'<text class="t-muted" x="{cx0 + cw + 28}" y="{y + 34}" font-size="15">{notes[0]}</text>')
        parts.append(f'<text class="t-muted" x="{cx0 + cw + 28}" y="{y + 58}" font-size="15">{notes[1]}</text>')
    endcap(488, "The SQLite database", "zone-db")

    gaps = [
        (64, 116, "request", "response"),
        (200, 240, "calls a handler", "data, or an error"),
        (324, 364, "calls a data function", "data, or an error"),
        (448, 488, "SQL and values", "rows"),
    ]
    for y1, y2, down, up in gaps:
        parts.append(f'<path class="arrow" d="M 180 {y1 + 2} L 180 {y2 - 2}" marker-end="url(#ah3)"/>')
        parts.append(f'<text x="192" y="{(y1 + y2) / 2 + 5}" font-size="13.5">{down}</text>')
        parts.append(f'<path class="arrow back" d="M 400 {y2 - 2} L 400 {y1 + 2}" marker-end="url(#ah3b)"/>')
        parts.append(f'<text x="412" y="{(y1 + y2) / 2 + 5}" font-size="13.5">{up}</text>')
    parts.append("</svg>")
    return "".join(parts)


# -------------------------------------------------------------------- race


def race_svg():
    width, height = 1100, 470

    def panel(x0, title, subtitle, steps, verdict, good):
        out = [
            f'<text class="strong" x="{x0 + 260}" y="30" text-anchor="middle" font-size="17">{title}</text>',
            f'<text class="t-muted" x="{x0 + 260}" y="52" text-anchor="middle" font-size="13.5">{subtitle}</text>',
        ]
        lanes = [(x0 + 60, "Buyer A"), (x0 + 230, "Buyer B"), (x0 + 440, "Database")]
        for lx, name in lanes:
            out.append(f'<line class="lane" x1="{lx}" y1="96" x2="{lx}" y2="380"/>')
            out.append(f'<rect class="head" x="{lx - 52}" y="64" width="104" height="30" rx="8"/>')
            out.append(f'<text class="strong" x="{lx}" y="84" text-anchor="middle" font-size="14">{name}</text>')
        for (src, dst, y, label, back) in steps:
            sx_, dx_ = lanes[src][0], lanes[dst][0]
            d = 1 if dx_ > sx_ else -1
            cls = "arrow back" if back else "arrow"
            out.append(f'<path class="{cls}" d="M {sx_} {y} L {dx_ - 10 * d} {y}"/>')
            out.append(f'<path class="{cls}" d="M {dx_ - 12 * d} {y - 6} L {dx_} {y} L {dx_ - 12 * d} {y + 6}"/>')
            out.append(f'<text x="{(sx_ + dx_) / 2}" y="{y - 8}" font-size="13" text-anchor="middle">{label}</text>')
        colour = "var(--good)" if good else "var(--bad)"
        out.append(f'<text class="strong" x="{x0 + 260}" y="425" text-anchor="middle" font-size="15" style="fill: {colour}">{verdict}</text>')
        return "".join(out)

    left = [
        (0, 2, 120, "SELECT stock", False), (2, 0, 144, "1", True),
        (1, 2, 190, "SELECT stock", False), (2, 1, 214, "1", True),
        (0, 2, 270, "write stock = 0", False),
        (1, 2, 330, "write stock = 0", False),
    ]
    right = [
        (0, 2, 130, "UPDATE ... WHERE stock &gt; 0", False), (2, 0, 156, "1 row changed", True),
        (1, 2, 230, "UPDATE ... WHERE stock &gt; 0", False), (2, 1, 256, "0 rows changed", True),
    ]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Two buyers race for the last item. With read-then-write, both read a stock of 1 and both write, so two buyers get one item. With a single UPDATE, the database serves them one after the other and the second is told the slot is sold out.">',
        panel(10, "Read, then write", "two steps with a gap between them", left, "Two buyers took the one item that was left.", False),
        '<line class="lane" x1="560" y1="20" x2="560" y2="440"/>',
        panel(570, "One statement", "check and change happen together", right, "The second buyer is told that the slot is sold out.", True),
        "</svg>",
    ]
    return "".join(parts)


# -------------------------------------------------------------------- cors


def cors_svg():
    width, height = 1080, 470
    lanes = {"script": 150, "browser": 540, "server": 930}
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="A script on a page from port 9000 asks the browser to fetch from port 8000. The server answers normally, but the browser withholds the answer from the script because no permission header is present.">',
        '<defs><marker id="ah4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)"/></marker>'
        '<marker id="ah4m" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--muted)"/></marker>'
        '<marker id="ah4b" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--bad)"/></marker></defs>',
    ]
    for key, name, sub in [("script", "Script in the page", "page came from port 9000"), ("browser", "The browser", "enforces the same-origin policy"), ("server", "The API server", "listens on port 8000")]:
        x = lanes[key]
        parts.append(f'<line class="lane" x1="{x}" y1="84" x2="{x}" y2="{height - 16}"/>')
        parts.append(f'<rect class="head" x="{x - 120}" y="16" width="240" height="62" rx="10"/>')
        parts.append(f'<text class="strong" x="{x}" y="43" text-anchor="middle" font-size="16">{name}</text>')
        parts.append(f'<text class="t-muted" x="{x}" y="64" text-anchor="middle" font-size="13">{sub}</text>')

    def arrow(x1, x2, y, label, marker, cls="arrow"):
        d = 1 if x2 > x1 else -1
        parts.append(f'<path class="{cls}" d="M {x1} {y} L {x2 - 2 * d} {y}" marker-end="url(#{marker})"/>')
        parts.append(f'<text x="{(x1 + x2) / 2}" y="{y - 10}" font-size="14" text-anchor="middle">{label}</text>')

    arrow(lanes["script"], lanes["browser"], 130, "fetch(&quot;http://127.0.0.1:8000/api/slots&quot;)", "ah4")
    arrow(lanes["browser"], lanes["server"], 190, "GET /api/slots", "ah4")
    arrow(lanes["server"], lanes["browser"], 250, "200 OK and JSON, with no permission header", "ah4m", "arrow back")
    parts.append(f'<text class="t-muted" x="{lanes["server"]}" y="282" text-anchor="middle" font-size="13">server log: GET /api/slots 200</text>')
    parts.append(f'<rect class="note" x="320" y="306" width="440" height="58" rx="8" style="stroke: var(--bad)"/>')
    parts.append('<text x="540" y="330" text-anchor="middle" font-size="14">The page is from port 9000, the answer is from port 8000,</text>')
    parts.append('<text x="540" y="350" text-anchor="middle" font-size="14">and no header gives permission, so the answer is withheld.</text>')
    arrow(lanes["browser"], lanes["script"], 420, "network error: the script never sees the answer", "ah4b", "arrow bad")
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------- extra css and js

EXTRA_CSS = r"""
svg text.mono { font-family: ui-monospace, Menlo, Consolas, "DejaVu Sans Mono", monospace; }
svg .seg1 { fill: var(--seg1); }
svg .seg2 { fill: var(--seg2); }
svg .seg3 { fill: var(--seg3); }
svg .seg4 { fill: var(--seg4); }
figure.diagram .scroll { overflow-x: auto; }
figure.diagram .scroll svg { min-width: 760px; }
.stepper-controls { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 12px 0 0; }
.stepper-controls button {
  font: inherit; font-size: 15px; background: var(--accent); color: var(--on-accent);
  border: none; border-radius: 8px; padding: 7px 14px; cursor: pointer; font-weight: 700;
}
.stepper-controls button:disabled { background: var(--surface-2); color: var(--muted); cursor: not-allowed; }
#step-count { color: var(--muted); font-size: 14px; margin-left: 6px; }
.step-panel { border: 1px solid var(--line); background: var(--surface); border-radius: 10px; padding: 12px 18px 6px; margin-top: 12px; max-width: 900px; }
.step-panel h4 { margin: 0 0 4px; font-size: 1.05rem; }
.step-panel .cap { font-size: 13px; color: var(--muted); margin: 8px 0 2px; }
.step-panel pre.code { border: 1px solid var(--line); border-radius: 8px; margin-bottom: 10px; white-space: pre-wrap; word-break: break-word; }
.stepper.stepping g.station { opacity: 0.25; transition: opacity 0.2s; }
.stepper.stepping g.station.active { opacity: 1; }
.stepper g.station.active .dot { stroke: var(--text); stroke-width: 3; }
figure.demo { margin: 22px 0 28px; max-width: 760px; }
figure.demo iframe { width: 100%; border: 1px solid var(--line); border-radius: 10px; background: var(--surface-2); }
.zones { max-width: 760px; margin: 22px 0 30px; display: grid; gap: 10px; }
.zone { border: 2px dashed var(--line); border-radius: 12px; padding: 8px 12px 12px; }
.zone > .zone-title { font-size: 13px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; color: var(--muted); margin: 0 0 6px; }
.zone.server { border-color: var(--accent); }
.zone.net { border-color: var(--warn); background: var(--warn-soft); }
.zone.browser { border-color: var(--tok-func); }
.chip { display: inline-block; font-size: 12px; font-weight: 700; background: var(--surface-2); border: 1px solid var(--line); color: var(--muted); border-radius: 999px; padding: 0 8px; margin-left: 6px; vertical-align: middle; }
"""

STEPPER_JS = r"""
(function () {
  const stepper = document.getElementById("stepper");
  const dataElement = document.getElementById("stations-data");
  if (!stepper || !dataElement) return;
  const stations = JSON.parse(dataElement.textContent);
  const groups = [...stepper.querySelectorAll("g.station")];
  const panel = document.getElementById("step-panel");
  const prev = document.getElementById("step-prev");
  const next = document.getElementById("step-next");
  const all = document.getElementById("step-all");
  const count = document.getElementById("step-count");
  let current = 0;

  function render() {
    stepper.classList.toggle("stepping", current > 0);
    groups.forEach((group) => {
      const numbers = group.dataset.n.split(" ").map(Number);
      group.classList.toggle("active", numbers.includes(current));
    });
    if (current === 0) {
      panel.hidden = true;
      count.textContent = "";
      next.textContent = "Step through";
    } else {
      const station = stations[current - 1];
      panel.hidden = false;
      document.getElementById("step-title").textContent = current + ". " + station.title;
      document.getElementById("step-text").innerHTML = station.text;
      document.getElementById("step-flight").textContent = station.flight;
      count.textContent = "Station " + current + " of " + stations.length;
      next.textContent = "Next";
    }
    prev.disabled = current <= 1;
    all.disabled = current === 0;
    next.disabled = current === stations.length;
  }

  next.addEventListener("click", () => { if (current < stations.length) { current += 1; render(); } });
  prev.addEventListener("click", () => { if (current > 1) { current -= 1; render(); } });
  all.addEventListener("click", () => { current = 0; render(); });
  render();
})();
"""


def dl_link(file_name):
    return f' <a class="svg-dl" href="diagrams/{file_name}" download>Download this diagram as SVG</a>'


def url_figure(handler_call, slug):
    return ('<figure class="diagram"><div class="scroll">' + url_svg(handler_call) + "</div>"
            "<figcaption>A URL is an address with four parts, and the server reads the path part with its route table. "
            "The text captured from the path becomes the argument of the handler." + dl_link(f"url-{slug}.svg") + "</figcaption></figure>")


def layers_figure(names, slug):
    return ('<figure class="diagram"><div class="scroll">' + layers_svg(names) + "</div>"
            "<figcaption>The server is three layers. Each one calls only the layer below it, so the SQL stays in the data layer, "
            "the URLs stay in the route layer, and the status codes stay in the HTTP layer." + dl_link(f"layers-{slug}.svg") + "</figcaption></figure>")


def race_figure():
    return ('<figure class="diagram"><div class="scroll">' + race_svg() + "</div>"
            "<figcaption>Two buyers reach a slot with one item left. When the program reads and then writes, the database can "
            "serve the second buyer between those steps. A single UPDATE with the condition inside it leaves no gap." + dl_link("race.svg") + "</figcaption></figure>")


def cors_figure():
    return ('<figure class="diagram"><div class="scroll">' + cors_svg() + "</div>"
            "<figcaption>The server received the request and answered it. The browser, not the server, refused to give the answer to the script." + dl_link("cors.svg") + "</figcaption></figure>")


def shapes_figure(E):
    return ('<figure class="diagram"><div class="scroll">' + shapes_svg(E) + "</div>"
            "<figcaption>The same fact in five shapes, with the place where each one lives and the step that converts one shape into the next." + dl_link(f"shapes-{E['slug']}.svg") + "</figcaption></figure>")


# ------------------------------------------------------------------ shapes


def shapes_svg(E):
    width, height = 1080, 640
    rows = [
        ("1. A row in the database", "A1 | Sparkling Water | 175 | 7", "zone-db", "On the server's disk, inside the SQLite file"),
        ("2. " + E["shape2_title"], E["shape2_code"], "zone-good", "In the memory of the server program"),
        ("3. Text on the network (JSON)", E["json_sample"], "zone-bad", "On the network, as bytes"),
        ("4. An object in the page's script", '{ slot_id: "A1", item_name: "Sparkling Water", price_cents: 175, stock: 7 }', "seg1", "In the memory of the page's script"),
        ("5. Elements in the DOM", '<p class="stock">7 left</p>', "seg1", "In the browser's DOM, then on the screen"),
    ]
    steps = [E["shape_label_1"], E["shape_label_2"], "response.json()", "createSlotCard(slot)"]
    parts = [
        f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="The fact that slot A1 has seven items left in five shapes: a database row, a server object, JSON text on the network, a script object in the page, and DOM elements. Four labelled arrows show the step that converts each shape into the next.">',
        '<defs><marker id="ah5" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent)"/></marker></defs>',
    ]
    box_x, box_w, box_h, pitch = 30, 640, 76, 130
    for i, (title, sample, cls, where) in enumerate(rows):
        y = 24 + i * pitch
        extra = ' style="stroke: var(--line); stroke-width: 2"' if cls.startswith("seg") else ""
        parts.append(f'<rect class="{cls}" x="{box_x}" y="{y}" width="{box_w}" height="{box_h}" rx="10"{extra}/>')
        parts.append(f'<text class="strong" x="{box_x + 16}" y="{y + 28}" font-size="16">{esc(title)}</text>')
        parts.append(f'<text class="mono" x="{box_x + 16}" y="{y + 56}" font-size="12">{esc(sample)}</text>')
        parts.append(f'<text class="t-muted" x="{box_x + box_w + 28}" y="{y + 44}" font-size="15">{esc(where)}</text>')
        if i < len(steps):
            ay1, ay2 = y + box_h + 4, y + pitch - 4
            parts.append(f'<path class="arrow" d="M 120 {ay1} L 120 {ay2}" marker-end="url(#ah5)"/>')
            parts.append(f'<text class="mono" x="140" y="{(ay1 + ay2) / 2 + 5}" font-size="13">{esc(steps[i])}</text>')
    parts.append("</svg>")
    return "".join(parts)


import lib  # noqa: E402

lib.CSS = lib.CSS + EXTRA_CSS
lib.JS = lib.JS + STEPPER_JS
