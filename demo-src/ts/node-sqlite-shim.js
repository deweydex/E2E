// Node has a built-in SQLite module called node:sqlite, and a browser does not.
// sql.js is SQLite compiled to run in a browser. This file gives the code from
// server.ts the same small interface that node:sqlite offers, backed by sql.js.

// Each database "file" lives in memory, and opening the same name twice returns
// the same database, so the setup script and the server share one machine.
const openDatabases = new Map();

class StatementSync {
  constructor(database, sqlText) {
    this.database = database;
    this.sqlText = sqlText;
    // Preparing a statement checks the SQL straight away, as node:sqlite does.
    database.prepare(sqlText).free();
  }

  // Return every matching row as an object.
  all(...values) {
    const statement = this.database.prepare(this.sqlText);
    try {
      statement.bind(values);
      const rows = [];
      while (statement.step()) {
        rows.push(statement.getAsObject());
      }
      return rows;
    } finally {
      statement.free();
    }
  }

  // Return the first matching row, or undefined when nothing matched.
  get(...values) {
    return this.all(...values)[0];
  }

  // Run a statement that changes data, and report how many rows it changed.
  run(...values) {
    this.database.run(this.sqlText, values);
    return { changes: this.database.getRowsModified(), lastInsertRowid: 0 };
  }
}

class DatabaseSync {
  constructor(fileName) {
    if (!openDatabases.has(fileName)) {
      openDatabases.set(fileName, new SQL.Database());
    }
    this.database = openDatabases.get(fileName);
  }

  exec(sqlText) {
    this.database.exec(sqlText);
  }

  prepare(sqlText) {
    return new StatementSync(this.database, sqlText);
  }

  // The data must survive a close, because the browser has no file to reopen.
  close() {}
}
