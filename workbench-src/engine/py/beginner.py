"""server.py (Beginner level) is the middle layer between the browser and the database.
You do not need to change it. Read it to see how a request turns into a query.

The rule is short. The address /api/list_slots runs the query named list_slots in queries.sql.
A query that starts with SELECT is a read, so it needs a GET request.
Every other query changes data, so it needs a POST request.
A query that changes no row at all is answered with 409, which means "this could not be done".

The workbench gives this file these ready-made names:
  db.all(sql, params)   runs a query and returns every row
  db.run(sql, params)   runs a statement that changes data and returns a result with .changes
  db.transaction()      is a "with" block whose statements succeed or fail as a whole
  files.read(name)      returns the text of a file in the project
  record(step)          tells the workbench what happened, so the timeline can draw it
"""

import re


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


def split_statements(sql_text):
    """Cut a query into its statements. This version splits on semicolons, so a semicolon inside a text value would confuse it."""
    lines = [line for line in sql_text.split("\n") if not line.strip().startswith("--")]
    parts = [part.strip() for part in "\n".join(lines).split(";")]
    return [part for part in parts if part]


def is_read_query(statements):
    """A query is a read when it is one SELECT statement. Anything else may change data."""
    return len(statements) == 1 and re.match(r"select", statements[0], re.IGNORECASE) is not None


def run_query(sql_text, params):
    """Run every statement of a query. A read returns rows. A write runs as one transaction and reports how many rows its last statement changed."""
    statements = split_statements(sql_text)
    if is_read_query(statements):
        return {"rows": db.all(statements[0], params), "changes": 0, "is_read": True}
    changes = 0
    with db.transaction():
        for statement in statements:
            changes = db.run(statement, params).changes
    return {"rows": [], "changes": changes, "is_read": False}


def handle_request(incoming):
    """Answer one request. The argument is a dictionary with the keys method, path, query and body."""
    if not incoming["path"].startswith("/api/"):
        return {"status": 404, "body": {"error": f"This server only answers addresses that start with /api/, not {incoming['path']}."}}

    queries = parse_queries(files.read("queries.sql"))
    query_name = incoming["path"][len("/api/"):]
    query = queries.get(query_name)
    if query is None:
        known = ", ".join(queries.keys())
        return {"status": 404, "body": {"error": f"There is no query named {query_name} in queries.sql. The names are: {known}."}}

    # A read must use GET and a write must use POST.
    is_read = is_read_query(split_statements(query["sql"]))
    expected_method = "GET" if is_read else "POST"
    if incoming["method"] != expected_method:
        return {"status": 405, "body": {"error": f"The query {query_name} needs {expected_method}, but this request used {incoming['method']}."}}

    # The workbench listens to record() to draw the timeline. A real server has no such line.
    record({
        "kind": "route",
        "text": f"The path {incoming['path']} names the query {query_name}.",
        "file": "queries.sql",
        "line": query["line"],
        "query": query_name,
    })

    # Values can arrive in the address (?slot=A1) or in the body. Both become parameters, and a value in the body wins when both have the same name.
    params = {**incoming["query"], **incoming["body"]}
    try:
        result = run_query(query["sql"], params)
    except Exception as error:
        return {"status": 400, "body": {"error": str(error)}}

    if result["is_read"]:
        return {"status": 200, "body": result["rows"]}
    if result["changes"] == 0:
        return {"status": 409, "body": {"error": "No row changed, so the request could not be carried out."}}
    return {"status": 200, "body": {"changes": result["changes"]}}
