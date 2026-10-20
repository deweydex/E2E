/* ---------- The TypeScript server: sql.js for the database, Sucrase to remove the types ---------- */

// The sql.js engine file travels inside data as base64 text, so the page also works when opened from a folder. This turns it back into bytes.
function base64ToBytes(base64) {
  const text = atob(base64);
  const bytes = new Uint8Array(text.length);
  for (let index = 0; index < text.length; index += 1) bytes[index] = text.charCodeAt(index);
  return bytes;
}

// Find the names that a statement uses as parameters, ignoring text inside quotes and comments.
function parameterNames(sql) {
  const cleaned = sql.replace(/'(?:[^']|'')*'/g, "''").replace(/--[^\n]*/g, "");
  const names = [];
  for (const match of cleaned.matchAll(/:(\w+)/g)) {
    if (!names.includes(match[1])) names.push(match[1]);
  }
  return names;
}

// The short phrase shown on an SQL card, such as "3 rows came back" or "1 row changed".
function describeResult(rows, changes, isRead) {
  if (isRead) return rows.length === 1 ? "1 row came back" : rows.length + " rows came back";
  return changes === 1 ? "1 row changed" : changes + " rows changed";
}

// The TypeScript server. It strips the types from the server file with Sucrase, runs the result,
// and keeps the data in an in-memory SQLite database from sql.js.
class TsEngine {
  // getFile(name) returns the text of a project file, or undefined when there is no such file.
  constructor(getFile) {
    this.getFile = getFile;
    this.label = "TypeScript";
    this.handler = null;          // the handleRequest function of the compiled server code
    this.problem = null;          // { file, message } when the server code could not be compiled
    this.record = () => {};       // set for each request, and collects the steps for the timeline
  }

  // Load sql.js and create an empty database. Calling it again does nothing.
  async ready() {
    if (this.SQL) return;
    this.SQL = await initSqlJs({ wasmBinary: base64ToBytes(window.SQL_WASM_BASE64) });
    this.database = new this.SQL.Database();
  }

  // The database interface that the server code sees as db.
  makeDatabaseApi() {
    const tsEngine = this;

    // Pick the :name values for a statement out of params. A missing value is an error, and values SQLite cannot store are converted.
    function bindParameters(sql, params) {
      const names = parameterNames(sql);
      const bound = {};          // the values keyed as sql.js wants them, with the colon
      const shown = {};          // the same values keyed as the timeline shows them, without the colon
      for (const name of names) {
        if (!params || !(name in params)) {
          throw new Error("The SQL uses :" + name + ", but the request did not send a value for it.");
        }
        let value = params[name];
        if (typeof value === "boolean") value = value ? 1 : 0;
        if (value !== null && typeof value === "object") value = JSON.stringify(value);
        if (value === undefined) value = null;
        bound[":" + name] = value;
        shown[name] = value;
      }
      return { bound, shown, names };
    }

    // Tell the timeline about one SQL statement: its text, its values, what happened and how long it took.
    function recordSql(sql, shownParams, outcome, startedAt, rows) {
      const isRead = /^\s*(?:--[^\n]*\n\s*)*select/i.test(sql);
      tsEngine.record({
        kind: "sql",
        text: isRead ? "The server asks the database a question." : "The server asks the database to change something.",
        sql: sql.trim(),
        params: shownParams,
        result: outcome,
        rows: rows ? rows.slice(0, 4) : null,     // only the first four rows, so a card stays small
        ms: Math.max(0.1, performance.now() - startedAt),
      });
    }

    // This object is what the server code sees as db.
    const database = {
      all(sql, params) {
        const startedAt = performance.now();
        let shownParams = {};
        try {
          const prepared = bindParameters(sql, params);
          shownParams = prepared.shown;
          const statement = tsEngine.database.prepare(sql);
          const rows = [];
          try {
            if (prepared.names.length) statement.bind(prepared.bound);
            while (statement.step()) rows.push(statement.getAsObject());
          } finally {
            statement.free();
          }
          recordSql(sql, shownParams, describeResult(rows, 0, true), startedAt, rows);
          return rows;
        } catch (error) {
          recordSql(sql, shownParams, "error: " + error.message, startedAt, null);
          throw error;
        }
      },
      get(sql, params) {
        return database.all(sql, params)[0];
      },
      run(sql, params) {
        const startedAt = performance.now();
        let shownParams = {};
        try {
          const prepared = bindParameters(sql, params);
          shownParams = prepared.shown;
          tsEngine.database.run(sql, prepared.names.length ? prepared.bound : undefined);
          const changes = tsEngine.database.getRowsModified();
          recordSql(sql, shownParams, describeResult([], changes, false), startedAt, null);
          return { changes };
        } catch (error) {
          recordSql(sql, shownParams, "error: " + error.message, startedAt, null);
          throw error;
        }
      },
      transaction(work) {
        const recordTransactionStep = (sql, text) => tsEngine.record({ kind: "sql", text, sql, params: {}, result: "ok", rows: null, ms: 0.1 });
        tsEngine.database.run("BEGIN");
        recordTransactionStep("BEGIN", "The transaction begins. Nothing is final until it is committed.");
        try {
          const result = work();
          tsEngine.database.run("COMMIT");
          recordTransactionStep("COMMIT", "The transaction is committed. All of its changes are saved together.");
          return result;
        } catch (error) {
          try { tsEngine.database.run("ROLLBACK"); } catch (ignored) { /* nothing to undo */ }
          recordTransactionStep("ROLLBACK", "The transaction is rolled back. None of its changes were kept.");
          throw error;
        }
      },
    };
    return database;
  }

  // Turn the TypeScript of the server (and of the handlers at the Advanced level) into running code.
  // Each source is { name, text }. Returns null when all went well, or { file, message } describing the first problem.
  compile(sources) {
    this.handler = null;
    this.problem = null;
    const parts = [];
    for (const source of sources) {
      try {
        parts.push(Sucrase.transform(source.text, { transforms: ["typescript"] }).code);
      } catch (error) {
        this.problem = { file: source.name, message: String(error.message || error) };
        return this.problem;
      }
    }
    try {
      // This object is what the server code sees as files.
      const filesApi = {
        read: (name) => {
          const text = this.getFile(name);
          if (text === undefined) throw new Error("The file " + name + " does not exist in this project.");
          return text;
        },
      };
      // The server code runs as the body of a function that is given files, record and db, and returns handleRequest.
      const factory = new Function("files", "record", "db", parts.join("\n") + "\nreturn handleRequest;");
      this.handler = factory(filesApi, (step) => this.record(step), this.makeDatabaseApi());
    } catch (error) {
      this.problem = { file: sources[sources.length - 1].name, message: String(error.message || error) };
    }
    return this.problem;
  }

  // Replace the database with a new one and run the schema in it. Returns null, or { file, message } when the schema has an error.
  reset(schemaText) {
    if (this.database) this.database.close();
    this.database = new this.SQL.Database();
    try {
      this.database.exec(schemaText);
      return null;
    } catch (error) {
      return { file: "schema.sql", message: String(error.message || error) };
    }
  }

  // Run the server code for one request { method, path, query, body }. Returns { status, body, steps }, where steps are the records for the timeline.
  handle(request) {
    const steps = [];
    this.record = (step) => steps.push(step);
    let answer;
    if (this.problem) {
      answer = { status: 500, body: { error: "The server could not start. " + this.problem.file + ": " + this.problem.message } };
    } else {
      try {
        answer = this.handler(request);
        if (!answer || typeof answer.status !== "number") {
          answer = { status: 500, body: { error: "The handler did not return an answer. Return json(...) or fail(...)." } };
        }
      } catch (error) {
        answer = { status: 500, body: { error: String(error.message || error) } };
      }
    }
    return { status: answer.status, body: answer.body, steps };
  }

  // Read every table for the Database panel. Returns a list of { name, columns, rows }.
  tables() {
    const result = [];
    const names = this.database.exec("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name");
    const list = names.length ? names[0].values.map((row) => row[0]) : [];
    for (const name of list) {
      const statement = this.database.prepare('SELECT * FROM "' + name + '"');
      const columns = statement.getColumnNames();
      const rows = [];
      while (statement.step()) rows.push(statement.get());
      statement.free();
      result.push({ name, columns, rows });
    }
    return result;
  }

  // Run any SQL straight on the database, for the "Try SQL" box. Nothing is recorded in the timeline.
  runSqlConsole(sql) {
    try {
      const results = this.database.exec(sql);
      const last = results[results.length - 1];
      return last
        ? { columns: last.columns, rows: last.values }
        : { columns: [], rows: [], message: this.database.getRowsModified() + " rows changed" };
    } catch (error) {
      return { error: String(error.message || error) };
    }
  }
}
