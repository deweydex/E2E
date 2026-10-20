"""Hover explanations for key words.

mark(html) wraps the first use of each key word in every section with a dotted underline and a short
explanation that appears on hover, on keyboard focus and on touch. Inside diagrams the same words get
an SVG <title>, which browsers show as a hover tooltip.
"""

import html as htmllib
import re

# Words that are too common to mark (request, path, server...) stay out of this list on purpose.
MARKED = [
    "route table", "handler", "service worker", "connection", "transaction", "JSON", "DOM", "fetch",
    "promise", "SQL injection", "SQL", "API", "endpoint", "status code", "parameterised query",
    "placeholder", "schema", "primary key", "constraint", "validation", "serialising", "parsing",
    "event delegation", "CORS", "same-origin policy", "origin", "idempotent", "stateless", "REST",
    "path traversal", "XSS", "relational database", "prepared statement", "contract", "URL",
]

MORE = {
    "request": "A message from the browser that says what it wants.",
    "response": "The message that the server sends back.",
    "server": "A program that waits for requests and answers them.",
    "client": "A program that sends requests to a server. Here the client is the browser.",
    "query": "A question that you ask a database, written in SQL.",
    "row": "One record in a table, such as one slot of the machine.",
    "column": "One named field in a table, such as stock.",
    "HTML": "The language that describes what is on a page: headings, paragraphs, buttons.",
    "CSS": "The language that describes how a page looks: colours, sizes and layout.",
    "JavaScript": "The language that browsers run. Scripts in a page are written in it.",
    "terminal": "A text window where you type commands.",
    "developer tools": "Tools built into the browser that show what a page and its requests are doing.",
    "console": "The part of the developer tools where messages appear and where you can type JavaScript.",
    "Network tab": "The part of the developer tools that lists every request the page sends.",
    "pip": "Python's tool for installing extra packages.",
    "npm": "Node's tool for installing extra packages.",
    "Node": "A program that runs JavaScript and TypeScript outside a browser.",
    "HTTP": "The agreement that browsers and servers use for requests and responses. Going deeper has the details.",
    "layer": "One of the three parts of the server: the data layer talks to the database, the route layer matches URLs, and the HTTP layer reads and writes messages. Step 3 builds them.",
    "port": "A number that says which program on a computer should receive a message.",
    "header": "A name and a value that describe a request or a response, such as Content-Type.",
    "bytes": "The numbers that a computer stores and sends. Text has to become bytes to cross a network.",
    "encode": "Turn text into bytes.",
    "UTF-8": "A standard way of turning characters into bytes.",
    "SQLite": "A database that lives in one ordinary file and needs no separate server.",
    "PostgreSQL": "A larger database that runs as its own server program.",
    "MySQL": "A larger database that runs as its own server program.",
    "library": "Code written by someone else that your program can load and use.",
    "module": "A file of code that other files can load with import.",
    "index": "A lookup structure that lets the database find rows quickly, like the index of a book.",
    "tuple": "A fixed group of values in Python, such as ('A1', 'Sparkling Water', 175, 8).",
    "exception": "An error that stops the normal flow of a Python program until some code handles it.",
    "cursor": "An object that holds the rows a query returned, so that a program can loop over them.",
    "commit": "Make the changes of a transaction permanent.",
    "roll back": "Undo every change that a transaction made.",
    "thread": "A separate line of work inside a program. Several threads can run at the same time.",
    "dictionary": "Python's collection of named values, such as {'stock': 7}.",
    "framework": "A ready-made toolkit that handles the routine parts of a server, so that you write only what is special to your app.",
    "FastAPI": "A popular Python framework for web APIs.",
    "standard library": "The code that comes built into a language, so that nothing needs installing.",
    "static file": "A file, such as HTML, CSS or JavaScript, that the server sends exactly as it is stored.",
    "status line": "The first line of a response: the protocol version, the status code and a short reason.",
    "static host": "A service that stores files and sends them exactly as they are, with no server code of your own.",
    "HTTPS": "HTTP with encryption, so that others on the network cannot read or change the messages.",
    "foreign key": "A column whose value must match the primary key of a row in another table.",
    "log": "A printed record of what the program did.",
    "property": "A named setting on an object, such as disabled on a button.",
    "locale": "A language and region setting that decides how numbers, dates and money are written.",
    "array": "An ordered list of values.",
    "listener": "A function that the browser calls when a certain event happens.",
    "argument": "A value that you pass to a function when you call it.",
    "interface": "The set of functions or messages that one piece of code offers to others.",
    "undefined": "The value that JavaScript gives to something that is missing.",
    "JOIN": "An SQL step that combines rows from two tables that share a value.",
    "GROUP BY": "An SQL step that gathers rows that share a value, so that you can count or add them.",
    "setInterval": "A browser function that runs another function again and again at a fixed interval.",
    "server-sent events": "A way for a server to keep a connection open and push new data to the page.",
    "WebSocket": "A two-way connection between a page and a server that either side can send on at any time.",
    "OpenAPI": "A standard format for describing an API, which other tools can read.",
    "uvicorn": "A program that runs a FastAPI application and listens for requests.",
    "optimistic": "Showing the expected result at once and fixing it afterwards if the server disagrees.",
    "race condition": "A fault where the result depends on which of two actions happens first.",
}

ALIASES = {
    "queries": "query", "encodes": "encode", "encoded": "encode", "commits": "commit", "rolls back": "roll back",
    "WebSockets": "WebSocket", "optimistic update": "optimistic", "data layer": "layer", "route layer": "layer",
    "HTTP layer": "layer", "cross-site scripting": "XSS", "race": "race condition", "layers": "layer", "developer console": "console",
}

EXTRA = {
    "request": "A message from the browser that says what it wants.",
    "response": "The message the server sends back.",
    "route table": "A list that pairs each method and path pattern with the function that handles it.",
    "service worker": "A script that sits between a page and the network and can answer requests itself.",
    "placeholder": "A mark such as ? in SQL that shows where a value goes. The value travels separately.",
    "prepared statement": "SQL that the database has read and checked once, so it can be run many times.",
    "handler": "The function that answers one kind of request.",
    "origin": "Scheme, host and port together. Two addresses with different ports are different origins.",
}

# Basic words get one hover for the whole page, at their first use. The rest repeat in each new subsection.
ONCE_PER_PAGE = {
    "request", "response", "server", "client", "HTML", "CSS", "JavaScript", "terminal", "developer tools", "pip", "npm", "node",
    "query", "row", "column", "port", "header", "log", "console", "network tab", "bytes", "library", "module",
}

VOID = {"br", "img", "hr", "input", "meta", "link", "source", "wbr", "path", "circle", "rect", "line", "polyline", "polygon"}
PROTECTED = {"pre", "code", "a", "button", "summary", "script", "style", "textarea", "title", "dfn", "h1", "h2", "h3", "h4", "svg"}


def definitions():
    """Map each word that gets a hover explanation to its text. Aliases share the text of their main word."""
    from shared_b import GLOSSARY

    table = {t.lower(): d for t, d in GLOSSARY}
    table.update({k.lower(): v for k, v in MORE.items()})
    table.update({k.lower(): v for k, v in EXTRA.items() if k.lower() not in MORE})
    short = {}
    for term in MARKED + list(MORE):
        text = table.get(term.lower())
        assert text, "no definition for " + term
        short[term] = re.split(r"(?<=[.])\s", text)[0] if len(text) > 200 else text
    for alias, main in ALIASES.items():
        short[alias] = short[main]
    return short


def canonical(word):
    """Words that mean the same thing share one hover, so the second form is not marked again in the same place."""
    for alias, main in ALIASES.items():
        if alias.lower() == word.lower():
            return main.lower()
    return word.lower()


def _pattern(defs):
    words = sorted(defs, key=len, reverse=True)

    def alt(word):
        # Acronyms and names such as REST, API or FastAPI must match in exactly that case, so "rest" stays an ordinary word.
        exact = word != word.lower() and word != word.capitalize()
        return f"(?-i:{re.escape(word)})" if exact else re.escape(word)

    return re.compile(r"(?<![\w-])(" + "|".join(alt(w) for w in words) + r")(s?)(?![\w-])", re.I)


def _lookup(defs, word):
    for key in defs:
        if key.lower() == word.lower():
            return key
    return None


def _mark_prose(chunk, defs, pat, seen, page_seen):
    def repl(match):
        key = _lookup(defs, match.group(1))
        if key is None or canonical(key) in seen:
            return match.group(0)
        if canonical(key) in ONCE_PER_PAGE:
            if canonical(key) in page_seen:
                return match.group(0)
            page_seen.add(canonical(key))
        seen.add(canonical(key))
        text = htmllib.escape(defs[key], quote=True)
        return f'<span class="term" tabindex="0" data-def="{text}">{match.group(0)}</span>'

    return pat.sub(repl, chunk)


def _mark_svg(svg, defs, pat):
    def text_repl(match):
        open_tag, content = match.group(1), match.group(2)
        if "<" in content:
            return match.group(0)
        found = []
        for m in pat.finditer(content):
            key = _lookup(defs, m.group(1))
            if key and key not in found:
                found.append(key)
        if not found:
            return match.group(0)
        tip = htmllib.escape("  ".join(f"{k}: {defs[k]}" for k in found))
        if 'class="' in open_tag:
            open_tag = open_tag.replace('class="', 'class="term-svg ', 1)
        else:
            open_tag = open_tag[:-1] + ' class="term-svg">'
        return f"{open_tag}{content}<title>{tip}</title></text>"

    return re.sub(r"(<text\b[^>]*>)([^<]*)</text>", text_repl, svg)


def mark(page):
    defs = definitions()
    pat = _pattern(defs)
    out = []
    page_seen = set()
    # Work one section at a time, so that each word is marked once per section.
    for piece in re.split(r"(?=<section id=)", page):
        seen = set()
        stack = []  # open tags, each with a flag that says whether the words inside must stay unmarked
        result = []
        for token in re.split(r"(<[^>]+>)", piece):
            if token.startswith("<"):
                if token.startswith("<h3") or token.startswith('<figure class="file"'):
                    seen = set()
                name = re.match(r"</?\s*([a-zA-Z0-9]+)", token)
                tag = name.group(1).lower() if name else ""
                if tag and tag not in VOID and not token.endswith("/>") and not token.startswith("<!"):
                    if token.startswith("</"):
                        for i in range(len(stack) - 1, -1, -1):
                            if stack[i][0] == tag:
                                del stack[i:]
                                break
                    else:
                        stack.append((tag, tag in PROTECTED or (tag == "span" and "fname" in token)))
                result.append(token)
            else:
                result.append(token if any(flag for _, flag in stack) else _mark_prose(token, defs, pat, seen, page_seen))
        piece = "".join(result)
        piece = re.sub(r"<svg\b.*?</svg>", lambda m: _mark_svg(m.group(0), defs, pat), piece, flags=re.S)
        out.append(piece)
    return "".join(out)


def intro_list(names):
    """A short list that introduces words before a diagram uses them."""
    defs = definitions()
    items = "".join(f"<li><dfn>{n}</dfn>: {defs[n] if n in defs else EXTRA[n]}</li>" for n in names)
    return f"<ul>{items}</ul>"
