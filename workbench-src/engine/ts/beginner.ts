// server.ts (Beginner level) is the middle layer between the browser and the database.
// You do not need to change it. Read it to see how a request turns into a query.
//
// The rule is short. The address /api/list_slots runs the query named list_slots in queries.sql.
// A query that starts with SELECT is a read, so it needs a GET request.
// Every other query changes data, so it needs a POST request.
// A query that changes no row at all is answered with 409, which means "this could not be done".
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

// A query is a read when it is one SELECT statement. Anything else may change data.
function isReadQuery(statements: string[]) {
  return statements.length === 1 && /^select/i.test(statements[0]);
}

// Run every statement of a query. A read returns rows. A write runs as one transaction and reports how many rows its last statement changed.
function runQuery(sqlText: string, params: Params) {
  const statements = splitStatements(sqlText);
  if (isReadQuery(statements)) {
    return { rows: db.all(statements[0], params), changes: 0, isRead: true };
  }
  let changes = 0;
  db.transaction(() => {
    for (const statement of statements) {
      changes = db.run(statement, params).changes;
    }
  });
  return { rows: [], changes, isRead: false };
}

// Answer one request. The argument says which method, path, address values and body arrived.
function handleRequest(incoming: Incoming) {
  if (!incoming.path.startsWith("/api/")) {
    return { status: 404, body: { error: `This server only answers addresses that start with /api/, not ${incoming.path}.` } };
  }

  const queries = parseQueries(files.read("queries.sql"));
  const queryName = incoming.path.slice("/api/".length);
  const query = queries[queryName];
  if (!query) {
    const known = Object.keys(queries).join(", ");
    return { status: 404, body: { error: `There is no query named ${queryName} in queries.sql. The names are: ${known}.` } };
  }

  // A read must use GET and a write must use POST.
  const isRead = isReadQuery(splitStatements(query.sql));
  const expectedMethod = isRead ? "GET" : "POST";
  if (incoming.method !== expectedMethod) {
    return { status: 405, body: { error: `The query ${queryName} needs ${expectedMethod}, but this request used ${incoming.method}.` } };
  }

  // The workbench listens to record() to draw the timeline. A real server has no such line.
  record({
    kind: "route",
    text: `The path ${incoming.path} names the query ${queryName}.`,
    file: "queries.sql",
    line: query.line,
    query: queryName,
  });

  // Values can arrive in the address (?slot=A1) or in the body. Both become parameters, and a value in the body wins when both have the same name.
  const params = { ...incoming.query, ...incoming.body };
  try {
    const result = runQuery(query.sql, params);
    if (result.isRead) {
      return { status: 200, body: result.rows };
    }
    if (result.changes === 0) {
      return { status: 409, body: { error: "No row changed, so the request could not be carried out." } };
    }
    return { status: 200, body: { changes: result.changes } };
  } catch (error) {
    return { status: 400, body: { error: String((error as Error).message) } };
  }
}
