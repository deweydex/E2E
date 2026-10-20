// server.ts (Intermediate level) is the middle layer between the browser and the database.
// You do not need to change it. You decide what it does by editing routes.txt.
//
// For each request it finds the first line of routes.txt that matches the method and the path.
// That line names a query in queries.sql, and says what shape the answer should have:
//   rows    answers with a list of rows
//   one     answers with the first row, or with 404 when there is none
//   change  runs the query as a transaction and answers with the number of rows changed, or with 409 when none changed
//
// The workbench gives this file three ready-made names: db, files and record.
//   db.all(sql, params)    runs a query and returns every row
//   db.run(sql, params)    runs a statement that changes data and returns { changes }
//   db.transaction(work)   runs work as one unit that succeeds or fails as a whole
//   files.read(name)       returns the text of a file in the project
//   record(step)           tells the workbench what happened, so the timeline can draw it

// Params holds the values that fill the :name parameters of a query.
type Params = Record<string, unknown>;
// Incoming is the request as the workbench hands it to this file.
type Incoming = { method: string; path: string; query: Params; body: Params };

// Read queries.sql and cut it into named queries. Each one starts with "-- name: something".
function parseQueries(text: string) {
  const queries: Record<string, { sql: string; line: number }> = {};
  let currentName = "";
  text.split("\n").forEach((lineText, index) => {
    const header = lineText.match(/^--\s*name:\s*(\w+)/);
    if (header) {
      currentName = header[1];
      queries[currentName] = { sql: "", line: index + 1 };
    } else if (currentName) {
      queries[currentName].sql += lineText + "\n";
    }
  });
  return queries;
}

// Read routes.txt. Every line that is not empty and does not start with # is one route.
function parseRoutes(text: string) {
  const routes: { method: string; path: string; regex: RegExp; names: string[]; queryName: string; shape: string; line: number }[] = [];
  text.split("\n").forEach((lineText, index) => {
    const trimmed = lineText.trim();
    if (trimmed === "" || trimmed.startsWith("#")) {
      return;
    }
    const [method, path, queryName, shape] = trimmed.split(/\s+/);

    // A word such as :slot in the path becomes a pattern that captures that part of the address.
    const names: string[] = [];
    const pattern = path.replace(/:(\w+)/g, (_wholeMatch, name) => {
      names.push(name);
      return "([^/]+)";
    });
    routes.push({ method, path, regex: new RegExp("^" + pattern + "$"), names, queryName, shape, line: index + 1 });
  });
  return routes;
}

// Cut a query into its statements. This version splits on semicolons, so a semicolon inside a text value would confuse it.
function splitStatements(sqlText: string): string[] {
  const withoutComments = sqlText
    .split("\n")
    .filter((lineText) => !lineText.trim().startsWith("--"))
    .join("\n");
  return withoutComments
    .split(";")
    .map((statement) => statement.trim())
    .filter((statement) => statement.length > 0);
}

// Answer one request. The argument says which method, path, address values and body arrived.
function handleRequest(incoming: Incoming) {
  const routes = parseRoutes(files.read("routes.txt"));
  const queries = parseQueries(files.read("queries.sql"));

  // Find the first route whose path matches. Remember if any path matched, to tell 404 from 405.
  let pathMatched = false;
  for (const route of routes) {
    const match = route.regex.exec(incoming.path);
    if (!match) {
      continue;
    }
    pathMatched = true;
    if (route.method !== incoming.method) {
      continue;
    }

    // The workbench listens to record() to draw the timeline. A real server has no such line.
    record({
      kind: "route",
      text: `${incoming.method} ${incoming.path} matches the route ${route.method} ${route.path}, which runs the query ${route.queryName}.`,
      file: "routes.txt",
      line: route.line,
      query: route.queryName,
    });

    const query = queries[route.queryName];
    if (!query) {
      return { status: 500, body: { error: `routes.txt line ${route.line} names the query ${route.queryName}, but queries.sql has no query with that name.` } };
    }

    // Values from the path win over values from the address, which win over values from the body.
    const pathValues: Params = {};
    route.names.forEach((name, index) => {
      pathValues[name] = decodeURIComponent(match[index + 1]);
    });
    const params = { ...incoming.body, ...incoming.query, ...pathValues };

    try {
      const statements = splitStatements(query.sql);
      if (route.shape === "rows" || route.shape === "one") {
        const rows = db.all(statements[0], params);
        if (route.shape === "one") {
          return rows.length > 0
            ? { status: 200, body: rows[0] }
            : { status: 404, body: { error: "Nothing matches that request." } };
        }
        return { status: 200, body: rows };
      }

      // The shape "change": run every statement as one transaction and count the rows changed by the last one.
      let changes = 0;
      db.transaction(() => {
        for (const statement of statements) {
          changes = db.run(statement, params).changes;
        }
      });
      return changes > 0
        ? { status: 200, body: { changes } }
        : { status: 409, body: { error: "No row changed, so the request could not be carried out." } };
    } catch (error) {
      return { status: 400, body: { error: String((error as Error).message) } };
    }
  }

  if (pathMatched) {
    return { status: 405, body: { error: `The path ${incoming.path} exists, but not for the method ${incoming.method}.` } };
  }
  return { status: 404, body: { error: `No route in routes.txt matches ${incoming.method} ${incoming.path}.` } };
}
