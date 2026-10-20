"""server.py (Intermediate level) is the middle layer between the browser and the database.
You do not need to change it. You decide what it does by editing routes.txt.

For each request it finds the first line of routes.txt that matches the method and the path.
That line names a query in queries.sql, and says what shape the answer should have:
  rows    answers with a list of rows
  one     answers with the first row, or with 404 when there is none
  change  runs the query as a transaction and answers with the number of rows changed, or with 409 when none changed

The workbench gives this file these ready-made names:
  db.all(sql, params)   runs a query and returns every row
  db.run(sql, params)   runs a statement that changes data and returns a result with .changes
  db.transaction()      is a "with" block whose statements succeed or fail as a whole
  files.read(name)      returns the text of a file in the project
  record(step)          tells the workbench what happened, so the timeline can draw it
"""

import re
from urllib.parse import unquote


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


def parse_routes(text):
    """Read routes.txt. Every line that is not empty and does not start with # is one route."""
    routes = []
    for index, line_text in enumerate(text.split("\n")):
        trimmed = line_text.strip()
        if trimmed == "" or trimmed.startswith("#"):
            continue
        columns = trimmed.split()
        method, path, query_name, shape = (columns + ["", "", "", ""])[:4]

        # A word such as :slot in the path becomes a pattern that captures that part of the address.
        names = re.findall(r":(\w+)", path)
        regex = re.compile("^" + re.sub(r":\w+", "([^/]+)", path) + "$")
        routes.append({"method": method, "path": path, "regex": regex, "names": names,
                       "query_name": query_name, "shape": shape, "line": index + 1})
    return routes


def split_statements(sql_text):
    """Cut a query into its statements. This version splits on semicolons, so a semicolon inside a text value would confuse it."""
    lines = [line for line in sql_text.split("\n") if not line.strip().startswith("--")]
    parts = [part.strip() for part in "\n".join(lines).split(";")]
    return [part for part in parts if part]


def handle_request(incoming):
    """Answer one request. The argument is a dictionary with the keys method, path, query and body."""
    routes = parse_routes(files.read("routes.txt"))
    queries = parse_queries(files.read("queries.sql"))

    # Find the first route whose path matches. Remember if any path matched, to tell 404 from 405.
    path_matched = False
    for route in routes:
        match = route["regex"].match(incoming["path"])
        if not match:
            continue
        path_matched = True
        if route["method"] != incoming["method"]:
            continue

        # The workbench listens to record() to draw the timeline. A real server has no such line.
        record({
            "kind": "route",
            "text": f"{incoming['method']} {incoming['path']} matches the route {route['method']} {route['path']}, which runs the query {route['query_name']}.",
            "file": "routes.txt",
            "line": route["line"],
            "query": route["query_name"],
        })

        query = queries.get(route["query_name"])
        if query is None:
            return {"status": 500, "body": {"error": f"routes.txt line {route['line']} names the query {route['query_name']}, but queries.sql has no query with that name."}}

        # Values from the path win over values from the address, which win over values from the body.
        path_values = {name: unquote(value) for name, value in zip(route["names"], match.groups())}
        params = {**incoming["body"], **incoming["query"], **path_values}

        try:
            statements = split_statements(query["sql"])
            if route["shape"] in ("rows", "one"):
                rows = db.all(statements[0], params)
                if route["shape"] == "one":
                    if rows:
                        return {"status": 200, "body": rows[0]}
                    return {"status": 404, "body": {"error": "Nothing matches that request."}}
                return {"status": 200, "body": rows}

            # The shape "change": run every statement as one transaction and count the rows changed by the last one.
            changes = 0
            with db.transaction():
                for statement in statements:
                    changes = db.run(statement, params).changes
            if changes > 0:
                return {"status": 200, "body": {"changes": changes}}
            return {"status": 409, "body": {"error": "No row changed, so the request could not be carried out."}}
        except Exception as error:
            return {"status": 400, "body": {"error": str(error)}}

    if path_matched:
        return {"status": 405, "body": {"error": f"The path {incoming['path']} exists, but not for the method {incoming['method']}."}}
    return {"status": 404, "body": {"error": f"No route in routes.txt matches {incoming['method']} {incoming['path']}."}}
