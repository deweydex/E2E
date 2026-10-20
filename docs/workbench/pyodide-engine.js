/* ---------- The Python server: Pyodide runs Python, and Python's own sqlite3 is the database ---------- */

// The address that Pyodide downloads from. The version is pinned, so the workbench behaves the same each time.
const PYODIDE_URL = "https://cdn.jsdelivr.net/pyodide/v0.29.5/full/";

// This Python code belongs to the workbench, and students do not see it. It gives the server code a db object,
// a files object and a record function. It also turns requests and answers into JSON text, because JSON
// is a simple way to pass data between JavaScript and Python. Functions that start with _wb_ are the ones JavaScript calls.
const PYTHON_PRELUDE = `
import sqlite3, json, re, time, contextlib
from types import SimpleNamespace

_steps = []         # the records for the timeline, collected while one request runs
_problem = None     # { file, message } when the server code could not be loaded
_namespace = {}     # the names defined by the server code, including handle_request
_files = {}         # the text of the project files that the server may read


def record(step):
    """Add one step to the timeline."""
    _steps.append(step)


class _Files:
    """The object that the server code sees as files."""

    def read(self, name):
        if name not in _files:
            raise FileNotFoundError("The file " + name + " does not exist in this project.")
        return _files[name]


files = _Files()


def _parameter_names(sql):
    """Find the :name parameters in a statement, ignoring text inside quotes and comments."""
    cleaned = re.sub(r"'(?:[^']|'')*'", "''", sql)
    cleaned = re.sub(r"--[^\\n]*", "", cleaned)
    names = []
    for name in re.findall(r":(\\w+)", cleaned):
        if name not in names:
            names.append(name)
    return names


class Database:
    """The object that the server code sees as db. It wraps Python's own sqlite3 and records each statement."""

    def __init__(self):
        self.connection = None
        self.reset("")

    def reset(self, schema):
        """Replace the database with a new one and run the schema in it."""
        if self.connection is not None:
            self.connection.close()
        self.connection = sqlite3.connect(":memory:", isolation_level=None)
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(schema)

    def _bind(self, sql, params):
        """Pick the values the statement needs out of params. A missing value is an error."""
        shown = {}
        for name in _parameter_names(sql):
            if params is None or name not in params:
                raise ValueError("The SQL uses :" + name + ", but the request did not send a value for it.")
            value = params[name]
            if isinstance(value, bool):
                value = int(value)
            elif isinstance(value, (dict, list)):
                value = json.dumps(value)
            shown[name] = value
        return shown

    def _record_sql(self, sql, shown, outcome, started, rows=None):
        """Tell the timeline about one statement: its text, its values, what happened and how long it took."""
        is_read = re.match(r"\\s*(?:--[^\\n]*\\n\\s*)*select", sql, re.IGNORECASE) is not None
        record({
            "kind": "sql",
            "text": "The server asks the database a question." if is_read else "The server asks the database to change something.",
            "sql": sql.strip(),
            "params": shown,
            "result": outcome,
            "rows": rows[:4] if rows else None,
            "ms": max(0.1, (time.perf_counter() - started) * 1000),
        })

    def all(self, sql, params=None):
        started = time.perf_counter()
        shown = {}
        try:
            shown = self._bind(sql, params)
            rows = [dict(row) for row in self.connection.execute(sql, shown).fetchall()]
            self._record_sql(sql, shown, "1 row came back" if len(rows) == 1 else str(len(rows)) + " rows came back", started, rows)
            return rows
        except Exception as error:
            self._record_sql(sql, shown, "error: " + str(error), started)
            raise

    def get(self, sql, params=None):
        rows = self.all(sql, params)
        return rows[0] if rows else None

    def run(self, sql, params=None):
        started = time.perf_counter()
        shown = {}
        try:
            shown = self._bind(sql, params)
            cursor = self.connection.execute(sql, shown)
            changes = max(cursor.rowcount, 0)
            self._record_sql(sql, shown, "1 row changed" if changes == 1 else str(changes) + " rows changed", started)
            return SimpleNamespace(changes=changes)
        except Exception as error:
            self._record_sql(sql, shown, "error: " + str(error), started)
            raise

    @contextlib.contextmanager
    def transaction(self):
        def mark(sql, text):
            record({"kind": "sql", "text": text, "sql": sql, "params": {}, "result": "ok", "rows": None, "ms": 0.1})

        self.connection.execute("BEGIN")
        mark("BEGIN", "The transaction begins. Nothing is final until it is committed.")
        try:
            yield
        except BaseException:
            self.connection.execute("ROLLBACK")
            mark("ROLLBACK", "The transaction is rolled back. None of its changes were kept.")
            raise
        else:
            self.connection.execute("COMMIT")
            mark("COMMIT", "The transaction is committed. All of its changes are saved together.")


db = Database()


def _wb_set_files(files_json):
    """Replace the files that the server code may read."""
    _files.clear()
    _files.update(json.loads(files_json))


def _wb_compile(sources_json):
    """Run the server code. Returns JSON: null when all went well, or { file, message } for the first problem."""
    global _namespace, _problem
    _problem = None
    namespace = {"db": db, "files": files, "record": record, "__name__": "workbench"}
    for source in json.loads(sources_json):
        try:
            exec(compile(source["text"], source["name"], "exec"), namespace)
        except SyntaxError as error:
            _problem = {"file": source["name"], "message": "line " + str(error.lineno) + ": " + str(error.msg)}
        except Exception as error:
            _problem = {"file": source["name"], "message": type(error).__name__ + ": " + str(error)}
        if _problem:
            break
    _namespace = namespace
    return json.dumps(_problem)


def _wb_reset(schema):
    """Replace the database and run the schema. Returns JSON: null, or { file, message }."""
    try:
        db.reset(schema)
        return json.dumps(None)
    except Exception as error:
        return json.dumps({"file": "schema.sql", "message": str(error)})


def _wb_handle(request_json):
    """Run handle_request for one request. Returns JSON with the status, the body and the recorded steps."""
    _steps.clear()
    if _problem:
        answer = {"status": 500, "body": {"error": "The server could not start. " + _problem["file"] + ": " + _problem["message"]}}
    else:
        try:
            answer = _namespace["handle_request"](json.loads(request_json))
            if not isinstance(answer, dict) or "status" not in answer:
                answer = {"status": 500, "body": {"error": "The handler did not return an answer. Return ok(...) or fail(...)."}}
        except Exception as error:
            answer = {"status": 500, "body": {"error": type(error).__name__ + ": " + str(error)}}
    return json.dumps({"status": answer["status"], "body": answer["body"], "steps": list(_steps)}, default=str)


def _wb_tables():
    """Read every table for the Database panel."""
    result = []
    names = [row[0] for row in db.connection.execute("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    for name in names:
        cursor = db.connection.execute('SELECT * FROM "' + name + '"')
        columns = [column[0] for column in cursor.description]
        result.append({"name": name, "columns": columns, "rows": [list(row) for row in cursor.fetchall()]})
    return json.dumps(result, default=str)


def _wb_run_sql_console(sql):
    """Run any SQL straight on the database, for the Try SQL box. Nothing is recorded."""
    try:
        cursor = db.connection.execute(sql)
        if cursor.description:
            return json.dumps({"columns": [c[0] for c in cursor.description], "rows": [list(r) for r in cursor.fetchall()]}, default=str)
        return json.dumps({"columns": [], "rows": [], "message": str(max(cursor.rowcount, 0)) + " rows changed"})
    except Exception as error:
        return json.dumps({"error": str(error)})
`;

// The Python server. It has the same methods as the TypeScript engine in wb-engines.js, so the rest of the workbench can use either.
class PyEngine {
  // getFile(name) returns the text of a project file. listFileNames() returns the name of every project file.
  constructor(getFile, listFileNames) {
    this.getFile = getFile;
    this.listFileNames = listFileNames;
    this.label = "Python";
    this.loading = false;      // true while Pyodide downloads
    this.pyReady = false;      // true once the Python helpers are in place
  }

  // Download Pyodide the first time, load sqlite3 and the Python helpers. Calling it again does nothing.
  async ready() {
    if (this.pyReady) return;
    this.loading = true;
    try {
      if (!window.loadPyodide) {
        await new Promise((resolve, reject) => {
          const script = document.createElement("script");
          script.src = PYODIDE_URL + "pyodide.js";
          script.onload = resolve;
          script.onerror = () => reject(new Error("The Python server could not be loaded. It needs an internet connection to download Pyodide, which is about 10 MB. The TypeScript server works without one."));
          document.head.append(script);
        });
      }
      this.py = await loadPyodide({ indexURL: PYODIDE_URL });
      await this.py.loadPackage("sqlite3");
      this.py.runPython(PYTHON_PRELUDE);
      const pythonGlobals = this.py.globals;
      this.callPython = {
        setFiles: pythonGlobals.get("_wb_set_files"), compile: pythonGlobals.get("_wb_compile"), reset: pythonGlobals.get("_wb_reset"),
        handle: pythonGlobals.get("_wb_handle"), tables: pythonGlobals.get("_wb_tables"), runSqlConsole: pythonGlobals.get("_wb_run_sql_console"),
      };
      this.pyReady = true;
    } finally {
      this.loading = false;
    }
  }

  // Copy the project files into Python, so that files.read(name) sees the student's latest text.
  syncFiles() {
    const allFiles = {};
    for (const name of this.listFileNames()) {
      const text = this.getFile(name);
      if (text !== undefined) allFiles[name] = text;
    }
    this.callPython.setFiles(JSON.stringify(allFiles));
  }

  // Same as the TypeScript engine: run the server code. Returns null, or { file, message } for the first problem.
  compile(sources) {
    this.syncFiles();
    return JSON.parse(this.callPython.compile(JSON.stringify(sources)));
  }

  reset(schemaText) {
    return JSON.parse(this.callPython.reset(schemaText));
  }

  handle(request) {
    this.syncFiles();
    return JSON.parse(this.callPython.handle(JSON.stringify(request)));
  }

  tables() {
    return JSON.parse(this.callPython.tables());
  }

  runSqlConsole(sql) {
    return JSON.parse(this.callPython.runSqlConsole(sql));
  }
}

window.PyEngine = PyEngine;
