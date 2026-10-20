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

PROTECTED = {"pre", "code", "a", "button", "summary", "script", "style", "textarea", "title", "dfn", "h1", "h2", "h3", "h4", "svg"}


def definitions():
    from shared_b import GLOSSARY

    table = {t.lower(): d for t, d in GLOSSARY}
    table.update(EXTRA)
    short = {}
    for term in MARKED:
        text = table.get(term.lower())
        assert text, "no definition for " + term
        short[term] = re.split(r"(?<=[.])\s", text)[0] if len(text) > 160 else text
    return short


def _pattern(defs):
    words = sorted(defs, key=len, reverse=True)
    return re.compile(r"(?<![\w-])(" + "|".join(re.escape(w) for w in words) + r")(s?)(?![\w-])", re.I)


def _lookup(defs, word):
    for key in defs:
        if key.lower() == word.lower():
            return key
    return None


def _mark_prose(chunk, defs, pat, seen):
    def repl(match):
        key = _lookup(defs, match.group(1))
        if key is None or key in seen:
            return match.group(0)
        seen.add(key)
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
    # Work one section at a time, so that each word is marked once per section.
    for piece in re.split(r"(?=<section id=)", page):
        seen = set()
        stack = []
        result = []
        for token in re.split(r"(<[^>]+>)", piece):
            if token.startswith("<"):
                name = re.match(r"</?\s*([a-zA-Z0-9]+)", token)
                tag = name.group(1).lower() if name else ""
                if tag in PROTECTED:
                    if token.startswith("</"):
                        if tag in stack:
                            while stack and stack.pop() != tag:
                                pass
                    elif not token.endswith("/>"):
                        stack.append(tag)
                result.append(token)
            else:
                result.append(token if stack else _mark_prose(token, defs, pat, seen))
        piece = "".join(result)
        piece = re.sub(r"<svg\b.*?</svg>", lambda m: _mark_svg(m.group(0), defs, pat), piece, flags=re.S)
        out.append(piece)
    return "".join(out)


def intro_list(names):
    """A short list that introduces words before a diagram uses them."""
    defs = definitions()
    items = "".join(f"<li><dfn>{n}</dfn>: {defs[n] if n in defs else EXTRA[n]}</li>" for n in names)
    return f"<ul>{items}</ul>"
