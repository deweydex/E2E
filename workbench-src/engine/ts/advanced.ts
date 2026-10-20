// server.ts (Advanced level) is a small framework. Your handlers.ts plugs into it.
// It stores the routes you register, finds the one that matches each request,
// and turns what your handler returns into an answer. Express and FastAPI do the same job on a larger scale.
// You write the handlers. You can read this file, but the workbench keeps it fixed.
//
// The workbench gives this file three ready-made names: db, files and record.
//   db.all(sql, params)    runs a query and returns every row
//   db.get(sql, params)    runs a query and returns the first row, or undefined
//   db.run(sql, params)    runs a statement that changes data and returns { changes }
//   db.transaction(work)   runs work as one unit that succeeds or fails as a whole
//   files.read(name)       returns the text of a file in the project
//   record(step)           tells the workbench what happened, so the timeline can draw it
//
// This file also reads queries.sql once, and gives your handlers the result as queries.<name>.sql.

// Params holds the values that fill the :name parameters of a query.
type Params = Record<string, unknown>;
// Incoming is the request as the workbench hands it to this file.
type Incoming = { method: string; path: string; query: Params; body: Params };
// What a handler receives: the incoming request, plus the words that were read from the path, such as { slot: "A1" }.
type HandlerRequest = Incoming & { params: Record<string, string> };
// What a handler returns: a status code and a body.
type Answer = { status: number; body: unknown };
type Handler = (request: HandlerRequest) => Answer;

// Every route that handlers.ts has registered, in the order it registered them.
const routes: { method: string; pattern: string; regex: RegExp; names: string[]; handler: Handler }[] = [];

// Register a route. A word such as :slot in the pattern is captured from the address.
function route(method: string, pattern: string, handler: Handler) {
  const names: string[] = [];
  const source = pattern.replace(/:(\w+)/g, (_wholeMatch, name) => {
    names.push(name);
    return "([^/]+)";
  });
  routes.push({ method, pattern, regex: new RegExp("^" + source + "$"), names, handler });
}

// These two small helpers build an answer.
function json(body: unknown): Answer {
  return { status: 200, body };
}
function fail(status: number, message: string): Answer {
  return { status, body: { error: message } };
}

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
// Your handlers use these as queries.list_slots.sql, queries.get_slot.sql and so on.
const queries = parseQueries(files.read("queries.sql"));

// Answer one request. The argument says which method, path, address values and body arrived.
function handleRequest(incoming: Incoming): Answer {
  let pathMatched = false;
  for (const candidate of routes) {
    const match = candidate.regex.exec(incoming.path);
    if (!match) {
      continue;
    }
    pathMatched = true;
    if (candidate.method !== incoming.method) {
      continue;
    }

    // The workbench listens to record() to draw the timeline. A real server has no such line.
    record({
      kind: "route",
      text: `${incoming.method} ${incoming.path} matches the route ${candidate.method} ${candidate.pattern}.`,
      file: "handlers.ts",
      find: '"' + candidate.pattern + '"',
    });

    const params: Record<string, string> = {};
    candidate.names.forEach((name, index) => {
      params[name] = decodeURIComponent(match[index + 1]);
    });

    // A handler that throws an error must not crash the whole server, so the error becomes a 500 answer.
    try {
      return candidate.handler({ ...incoming, params });
    } catch (error) {
      return fail(500, "The handler failed: " + String((error as Error).message));
    }
  }

  if (pathMatched) {
    return fail(405, `The path ${incoming.path} exists, but not for the method ${incoming.method}.`);
  }
  return fail(404, `No route matches ${incoming.method} ${incoming.path}.`);
}
