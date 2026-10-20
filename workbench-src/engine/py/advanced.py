"""server.py (Advanced level) is a small framework. Your handlers.py plugs into it.
It stores the routes you register, finds the one that matches each request,
and turns what your handler returns into an answer. Flask and FastAPI do the same job on a larger scale.
You write the handlers. You can read this file, but the workbench keeps it fixed.

The workbench gives this file these ready-made names:
  db.all(sql, params)   runs a query and returns every row
  db.get(sql, params)   runs a query and returns the first row, or None
  db.run(sql, params)   runs a statement that changes data and returns a result with .changes
  db.transaction()      is a "with" block whose statements succeed or fail as a whole
  files.read(name)      returns the text of a file in the project
  record(step)          tells the workbench what happened, so the timeline can draw it

This file also reads queries.sql once, and gives your handlers the result as queries["name"]["sql"].
"""

import re
from urllib.parse import unquote

# Every route that handlers.py has registered, in the order it registered them.
routes = []


class Request:
    """What a handler receives. The path words, the address values and the body are dictionaries."""

    def __init__(self, method, path, params, query, body):
        self.method = method
        self.path = path
        self.params = params
        self.query = query
        self.body = body


def route(method, pattern):
    """A decorator. Put @route("GET", "/api/slots") above a function to register it as a route.
    A word such as :slot in the pattern is captured from the address."""

    def register(handler):
        names = re.findall(r":(\w+)", pattern)
        regex = re.compile("^" + re.sub(r":\w+", "([^/]+)", pattern) + "$")
        routes.append({"method": method, "pattern": pattern, "regex": regex, "names": names, "handler": handler})
        return handler

    return register


def ok(body):
    """Build an answer with status 200."""
    return {"status": 200, "body": body}


def fail(status, message):
    """Build an answer with an error status and a message."""
    return {"status": status, "body": {"error": message}}


def parse_queries(text):
    """Read queries.sql and cut it into named queries. Each one starts with "-- name: something"."""
    queries = {}
    current_name = ""
    for index, line_text in enumerate(text.split("\n")):
        header = re.match(r"^--\s*name:\s*(\w+)", line_text)
        if header:
            current_name = header.group(1)
            queries[current_name] = {"sql": "", "line": index + 1}
        elif current_name:
            queries[current_name]["sql"] += line_text + "\n"
    return queries


# Your handlers use these as queries["list_slots"]["sql"] and so on.
queries = parse_queries(files.read("queries.sql"))


def handle_request(incoming):
    """Answer one request. The argument is a dictionary with the keys method, path, query and body."""
    path_matched = False
    for candidate in routes:
        match = candidate["regex"].match(incoming["path"])
        if not match:
            continue
        path_matched = True
        if candidate["method"] != incoming["method"]:
            continue

        # The workbench listens to record() to draw the timeline. A real server has no such line.
        record({
            "kind": "route",
            "text": f"{incoming['method']} {incoming['path']} matches the route {candidate['method']} {candidate['pattern']}.",
            "file": "handlers.py",
            "find": '"' + candidate["pattern"] + '"',
        })

        params = {name: unquote(value) for name, value in zip(candidate["names"], match.groups())}
        request = Request(incoming["method"], incoming["path"], params, incoming["query"], incoming["body"])

        # A handler that raises an error must not crash the whole server, so the error becomes a 500 answer.
        try:
            return candidate["handler"](request)
        except Exception as error:
            return fail(500, f"The handler failed: {error}")

    if path_matched:
        return fail(405, f"The path {incoming['path']} exists, but not for the method {incoming['method']}.")
    return fail(404, f"No route matches {incoming['method']} {incoming['path']}.")
