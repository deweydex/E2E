(function () {
"use strict";
/* ---------- Small helpers shared by the whole workbench ---------- */

// Make text safe to put inside HTML, so that code such as <b> is shown as text and not run.
function escapeHtml(text) {
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

// Which language a file is written in, judging by its ending. The editor uses this to choose the colours.
function languageOf(fileName) {
  const extension = fileName.split(".").pop().toLowerCase();
  if (extension === "htm") return "html";
  if (extension === "ts") return "ts";
  if (extension === "py") return "py";
  if (extension === "txt") return "txt";
  return extension;
}

/* ---------- Syntax colouring: Prism does the tokenising, the stylesheet picks the colours ---------- */

// The names this workbench uses for languages, mapped to Prism's names.
const PRISM_LANGUAGE = { html: "markup", css: "css", js: "javascript", ts: "typescript", py: "python", sql: "sql", txt: "routes" };

// A route table is not a Prism language, so we describe it here: a comment, a method, a :parameter and a result kind.
Prism.languages.routes = {
  comment: /#.*/,
  keyword: /\b(?:GET|POST|PUT|PATCH|DELETE)\b/,
  function: /\b(?:rows|one|change)\b/,
  variable: /:\w+/,
};

// SQL has no named-parameter token in Prism, so we add :name to the SQL grammar.
Prism.languages.insertBefore("sql", "variable", { variable: /:\w+/ });

// Turn plain text into HTML in which each token sits in a span such as <span class="token keyword">.
function colourise(text, language) {
  const grammar = Prism.languages[PRISM_LANGUAGE[language]];
  if (!grammar) return escapeHtml(text);
  return Prism.highlight(text, grammar, PRISM_LANGUAGE[language]);
}

/* ---------- The editor: a textarea on top of a coloured copy of its text ----------
   The student types into a transparent textarea. Underneath it, a <pre> shows the same text with colours.
   Both use the same font and the same line height, so each coloured word sits exactly under its typed word. */

// The height of one line, in pixels. The stylesheet uses the same number, so line numbers and the highlighted line stay aligned.
const LINE_HEIGHT = 20;
// The space above the first line inside the editor, in pixels.
const TOP_PADDING = 8;

class Editor {
  constructor(root) {
    this.root = root;
    root.innerHTML =
      '<div class="ed-gutter" aria-hidden="true"><div class="ed-numbers"></div></div>' +
      '<div class="ed-stage"><div class="ed-band" hidden></div>' +
      '<pre class="ed-colour" aria-hidden="true"></pre>' +
      '<textarea class="ed-input" spellcheck="false" autocapitalize="off" autocomplete="off" wrap="off"></textarea></div>';
    this.numbers = root.querySelector(".ed-numbers");
    this.band = root.querySelector(".ed-band");
    this.colour = root.querySelector(".ed-colour");
    this.input = root.querySelector(".ed-input");
    this.language = "txt";
    this.onChange = () => {};        // the workbench sets this to hear about every edit
    this.escapePressed = false;      // after Escape, the next Tab moves focus away instead of typing spaces
    this.bandLine = 0;               // the line marked as the one the timeline is describing, or 0 for none

    this.input.addEventListener("input", () => { this.paint(); this.onChange(this.input.value); });
    this.input.addEventListener("scroll", () => this.syncScroll());
    this.input.addEventListener("keydown", (event) => this.keydown(event));
  }

  // Show a file. The label is the file name, which a screen reader reads out.
  setText(text, language, readOnly, label) {
    this.language = language;
    this.input.setAttribute("aria-label", (readOnly ? "Read only code: " : "Editing ") + (label || "file"));
    this.input.value = text;
    this.input.readOnly = readOnly;
    this.root.classList.toggle("read-only", readOnly);
    this.paint();
    this.setBand(0);
  }

  // Redraw the coloured copy and the line numbers from the text in the textarea.
  paint() {
    this.colour.innerHTML = colourise(this.input.value, this.language) + "\n ";
    const lineCount = this.input.value.split("\n").length;
    let numbers = "";
    for (let line = 1; line <= lineCount; line += 1) numbers += line + "\n";
    this.numbers.textContent = numbers;
    this.syncScroll();
  }

  // Keep the coloured copy, the line numbers and the marked line level with the textarea when it scrolls.
  syncScroll() {
    this.colour.scrollTop = this.input.scrollTop;
    this.colour.scrollLeft = this.input.scrollLeft;
    this.numbers.style.transform = "translateY(" + -this.input.scrollTop + "px)";
    this.placeBand();
  }

  // Mark one line (counting from 1) as the line the timeline is talking about. Zero clears the mark.
  setBand(line, scrollTo) {
    this.bandLine = line;
    this.placeBand();
    if (line && scrollTo) {
      // Scroll only when the line is out of sight, and leave two lines of context above it.
      const top = (line - 1) * LINE_HEIGHT;
      const visibleTop = this.input.scrollTop;
      const visibleHeight = this.input.clientHeight;
      if (top < visibleTop || top > visibleTop + visibleHeight - 3 * LINE_HEIGHT) {
        this.input.scrollTop = Math.max(0, top - 2 * LINE_HEIGHT);
      }
    }
  }

  // Move the highlight to its line, or hide it when no line is marked.
  placeBand() {
    if (!this.bandLine) { this.band.hidden = true; return; }
    this.band.hidden = false;
    this.band.style.transform = "translateY(" + ((this.bandLine - 1) * LINE_HEIGHT + TOP_PADDING - this.input.scrollTop) + "px)";
  }

  // Tab inserts two spaces. Press Escape first when you want Tab to move focus to the next control.
  keydown(event) {
    if (event.key === "Escape") { this.escapePressed = true; return; }
    if (event.key === "Tab" && !event.shiftKey && !this.escapePressed && !this.input.readOnly) {
      event.preventDefault();
      const { selectionStart, selectionEnd, value } = this.input;
      this.input.value = value.slice(0, selectionStart) + "  " + value.slice(selectionEnd);
      this.input.selectionStart = this.input.selectionEnd = selectionStart + 2;
      this.paint();
      this.onChange(this.input.value);
      return;
    }
    this.escapePressed = false;
  }
}

/* ---------- Downloading, and a small ZIP writer so a project leaves as one file ---------- */

// Offer a Blob to the browser as a download with the given file name.
function downloadBlob(blob, fileName) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = fileName;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(link.href), 2000);
}

// A ZIP file stores a checksum (CRC-32) for each file. This table makes the checksum quick to compute.
const crcTable = (() => {
  const table = [];
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    table.push(c >>> 0);
  }
  return table;
})();

// The CRC-32 checksum of some bytes.
function crc32(bytes) {
  let crc = 0xffffffff;
  for (const byte of bytes) crc = crcTable[(crc ^ byte) & 0xff] ^ (crc >>> 8);
  return (crc ^ 0xffffffff) >>> 0;
}

// Build a ZIP archive with no compression. Each entry is { name, text }.
function makeZip(entries) {
  const encoder = new TextEncoder();
  const chunks = [];
  const central = [];
  let offset = 0;
  // ZIP stores numbers with the least significant byte first. These two helpers write a 16-bit and a 32-bit number that way.
  const u16 = (value) => new Uint8Array([value & 255, (value >> 8) & 255]);
  const u32 = (value) => new Uint8Array([value & 255, (value >> 8) & 255, (value >> 16) & 255, (value >>> 24) & 255]);
  // Join several byte arrays into one.
  const join = (...parts) => parts.reduce((all, part) => { const merged = new Uint8Array(all.length + part.length); merged.set(all); merged.set(part, all.length); return merged; }, new Uint8Array(0));

  // Each file gets a local header followed by its bytes, and a matching entry for the directory at the end of the archive.
  for (const entry of entries) {
    const name = encoder.encode(entry.name);
    const data = encoder.encode(entry.text);
    const crc = crc32(data);
    const local = join(u32(0x04034b50), u16(20), u16(0x0800), u16(0), u16(0), u16(0x21), u32(crc), u32(data.length), u32(data.length), u16(name.length), u16(0), name, data);
    chunks.push(local);
    central.push(join(u32(0x02014b50), u16(20), u16(20), u16(0x0800), u16(0), u16(0), u16(0x21), u32(crc), u32(data.length), u32(data.length), u16(name.length), u16(0), u16(0), u16(0), u16(0), u32(0), u32(offset), name));
    offset += local.length;
  }
  const centralBytes = join(...central);
  const end = join(u32(0x06054b50), u16(0), u16(0), u16(entries.length), u16(entries.length), u32(centralBytes.length), u32(offset), u16(0));
  return new Blob([...chunks, centralBytes, end], { type: "application/zip" });
}

/* ---------- Splitters: drag a bar, or focus it and press the arrow keys ---------- */

function makeSplitter(bar, options) {
  // options: { axis: "x" | "y", get: () => the current size in pixels, set: (pixels) => apply a new size, invert: true when dragging down makes the size smaller }
  let startPosition = 0;
  let startValue = 0;
  const move = (event) => {
    const delta = (options.axis === "x" ? event.clientX : event.clientY) - startPosition;
    options.set(startValue + delta * (options.invert ? -1 : 1));
  };
  const stop = () => {
    window.removeEventListener("pointermove", move);
    window.removeEventListener("pointerup", stop);
    document.body.classList.remove("dragging");
  };
  bar.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    startPosition = options.axis === "x" ? event.clientX : event.clientY;
    startValue = options.get();
    document.body.classList.add("dragging");
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", stop);
  });
  bar.addEventListener("keydown", (event) => {
    const step = event.shiftKey ? 80 : 24;
    const back = options.axis === "x" ? "ArrowLeft" : "ArrowUp";
    const forward = options.axis === "x" ? "ArrowRight" : "ArrowDown";
    if (event.key !== back && event.key !== forward) return;
    event.preventDefault();
    const direction = event.key === forward ? 1 : -1;
    options.set(options.get() + direction * step * (options.invert ? -1 : 1));
  });
}

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

/* ---------- State ----------
   Everything the workbench remembers lives in one object, so a reader can see it all in one place. */

const DATA = window.WB_DATA;
const STORAGE_KEY = "workbench-project-v1";
// These files belong to the server. Every other project file is a page, a stylesheet or a script for the browser.
const SERVER_ONLY = new Set(["schema.sql", "queries.sql", "routes.txt", "handlers.ts", "handlers.py"]);
const LEVELS = ["beginner", "intermediate", "advanced"];

const state = {
  mode: "explore",          // "explore" is the finished vending machine. "own" is the small starter project.
  level: "beginner",        // beginner, intermediate or advanced
  language: "ts",           // the server language: "ts" for TypeScript, "py" for Python
  stepping: true,           // whether the timeline stops after each step and waits for Forward
  follow: true,             // whether the editors jump to the line that the timeline is describing
  files: {},                // the student's current text for every project file, by file name
  baseline: {},             // the original text of each file, used by Revert and by "has the student edited anything?"
  page: "index.html",       // the page shown in the preview
  query: "",                // the part of that page's address after the question mark
  history: [],              // the pages visited, so that the back button works
  panes: { left: "index.html", right: "queries.sql" },   // which file each editor shows
};

const findElement = (selector, root) => (root || document).querySelector(selector);
const findElements = (selector, root) => Array.from((root || document).querySelectorAll(selector));
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

// The server's own file ends in .ts or .py, and so does the student's handlers file.
function serverFileExtension() { return state.language === "ts" ? "ts" : "py"; }
function engineFileName() { return "server." + serverFileExtension(); }
function handlerFileName() { return "handlers." + serverFileExtension(); }

// The server file is not stored in the project. It comes from the level and the language that are chosen.
function getFile(name) {
  if (name === engineFileName()) return DATA.engines[state.language][state.level];
  return state.files[name];
}

// The tabs of the right-hand editor. The student's own files come first, and the read-only server file comes last.
function serverFileList() {
  const first = state.level === "beginner" ? [] : state.level === "intermediate" ? ["routes.txt"] : [handlerFileName()];
  return [...first, "queries.sql", "schema.sql", engineFileName()];
}

// The tabs of the left-hand editor, with index.html first, then other pages, then styles, then scripts.
function browserFileList() {
  const names = Object.keys(state.files).filter((name) => !SERVER_ONLY.has(name));
  const rank = (name) => (name === "index.html" ? 0 : name.endsWith(".html") ? 1 : name.endsWith(".css") ? 2 : 3);
  return names.sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
}

// The file that the right-hand editor opens first: the file where a student at this level does most of the work.
function defaultServerTab() {
  return state.level === "beginner" ? "queries.sql" : state.level === "intermediate" ? "routes.txt" : handlerFileName();
}

/* ---------- Saving and restoring the student's work ---------- */

// Save after the student stops typing for 400 milliseconds, so every keystroke does not write to storage.
let saveTimer = null;
function saveSoon() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        mode: state.mode, level: state.level, language: state.language, stepping: state.stepping,
        follow: state.follow, files: state.files, baseline: state.baseline,
      }));
    } catch (error) { /* storage can be blocked, and the workbench still works */ }
  }, 400);
}

// Load saved work if there is any. Otherwise start from the original files for the current mode and level.
function restore() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (saved && saved.files && saved.baseline) {
      Object.assign(state, { mode: saved.mode, level: saved.level, language: saved.language, stepping: saved.stepping !== false, follow: saved.follow });
      state.files = saved.files;
      state.baseline = saved.baseline;
      return true;
    }
  } catch (error) { /* start fresh */ }
  loadBase(state.mode, state.level);
  return false;
}

function loadBase(mode, level) {
  const base = DATA.samples[mode][level];
  state.baseline = { ...base };
  state.files = { ...base };
}

// True when the student has changed any file from its original text.
function hasEdits() {
  return Object.keys(state.files).some((name) => state.files[name] !== state.baseline[name]);
}

/* ---------- Engines ---------- */

// An engine runs the server code. Both engines offer the same methods, so the rest of this file does not care which one is in use.
// The Python engine is missing when its script did not load.
const engines = { ts: new TsEngine(getFile) };
if (window.PyEngine) engines.py = new PyEngine(getFile, () => Object.keys(state.files));
function currentEngine() { return engines[state.language]; }

/* ---------- Notices ---------- */

// Show a short message above one of the editors. It hides itself after seven seconds.
function notice(side, text) {
  const box = findElement("#notice-" + side);
  box.textContent = text;
  box.hidden = !text;
  clearTimeout(box.timer);
  if (text) box.timer = setTimeout(() => { box.hidden = true; }, 7000);
}

// Show an error from the server code, or from schema.sql, above the right-hand editor. Passing null clears it.
function showProblem(problem) {
  const box = findElement("#server-problem");
  box.hidden = !problem;
  box.textContent = problem ? "Problem in " + problem.file + ": " + problem.message : "";
}

/* ---------- Code panes ---------- */

const panes = {};

// Prepare one editor and its buttons. The side is "left" for the browser files or "right" for the server files.
function setupPane(side) {
  const root = findElement("#code-" + side);
  const editor = new Editor(findElement(".editor", root));
  panes[side] = { root, editor, tabs: findElement(".tabs", root) };
  editor.onChange = (text) => onEdit(side, text);

  root.addEventListener("dragover", (event) => { event.preventDefault(); root.classList.add("drop"); });
  root.addEventListener("dragleave", () => root.classList.remove("drop"));
  root.addEventListener("drop", (event) => {
    event.preventDefault();
    root.classList.remove("drop");
    uploadFiles(side, event.dataTransfer.files);
  });

  const picker = findElement(".picker", root);
  findElement(".upload", root).addEventListener("click", () => picker.click());
  picker.addEventListener("change", () => { uploadFiles(side, picker.files); picker.value = ""; });
  findElement(".download", root).addEventListener("click", () => {
    const name = state.panes[side];
    downloadBlob(new Blob([getFile(name)], { type: "text/plain" }), name);
  });
  findElement(".revert", root).addEventListener("click", () => {
    const name = state.panes[side];
    if (state.baseline[name] === undefined) { notice(side, "There is no original version of " + name + " to go back to."); return; }
    state.files[name] = state.baseline[name];
    showFile(side, name);
    afterFileChange(side, name);
    notice(side, name + " is back to its original text.");
  });

  if (side === "left") {
    findElement(".delete", root).addEventListener("click", () => {
      const name = state.panes.left;
      if (!window.confirm("Remove " + name + " from this project?")) return;
      delete state.files[name];
      state.panes.left = browserFileList()[0];
      renderTabs("left");
      showFile("left", state.panes.left);
      if (state.page === name) loadPage(browserFileList().find((file) => file.endsWith(".html")) || name, "", { reason: "You removed " + name + "." });
      saveSoon();
    });
    const addBar = findElement("#add-bar");
    findElement(".add", root).addEventListener("click", () => { addBar.hidden = !addBar.hidden; if (!addBar.hidden) findElement("input", addBar).focus(); });
    addBar.addEventListener("submit", (event) => {
      event.preventDefault();
      const input = findElement("input", addBar);
      const name = input.value.trim();
      if (!/^[\w.-]+\.(html|css|js)$/i.test(name)) { notice("left", "Use a name such as about.html, theme.css or extra.js."); return; }
      if (state.files[name] !== undefined) { notice("left", name + " already exists."); return; }
      state.files[name] = /\.html$/i.test(name)
        ? '<!DOCTYPE html>\n<html lang="en">\n<head>\n  <meta charset="utf-8">\n  <title>New page</title>\n  <link rel="stylesheet" href="style.css">\n</head>\n<body>\n  <h1>New page</h1>\n  <script src="client.js"></script>\n</body>\n</html>\n'
        : /\.css$/i.test(name) ? "/* Styles for the pages. */\n" : "// A script for the pages.\n";
      input.value = "";
      addBar.hidden = true;
      renderTabs("left");
      showFile("left", name);
      saveSoon();
    });
  }
}

function renderTabs(side) {
  const names = side === "left" ? browserFileList() : serverFileList();
  const tabs = panes[side].tabs;
  tabs.innerHTML = "";
  for (const name of names) {
    const button = document.createElement("button");
    button.type = "button";
    button.setAttribute("role", "tab");
    button.className = "tab" + (name === state.panes[side] ? " current" : "");
    button.setAttribute("aria-selected", String(name === state.panes[side]));
    button.textContent = name;
    if (name.startsWith("server.")) button.classList.add("locked");
    button.addEventListener("click", () => showFile(side, name));
    tabs.append(button);
  }
}

// Show one file in one editor. The server's own file is shown read only.
function showFile(side, name) {
  const names = side === "left" ? browserFileList() : serverFileList();
  if (!names.includes(name)) name = names[0];
  state.panes[side] = name;
  const readOnly = name.startsWith("server.");
  panes[side].editor.setText(getFile(name) || "", languageOf(name), readOnly, name);
  findElement(".lock-note", panes[side].root).hidden = !readOnly;
  findElement(".revert", panes[side].root).disabled = readOnly;
  renderTabs(side);
}

// Find the first line (counting from 1) of a file that contains the given text. Returns 0 when there is none.
// The timeline uses this to point at code, so it finds lines by their content and not by fixed numbers.
// A student who edits the file keeps the highlight, as long as the searched text is still there.
function lineOf(fileName, text) {
  const content = getFile(fileName);
  if (content === undefined || !text) return 0;
  const lines = content.split("\n");
  // Try the text as given, and then with single quotes in place of double quotes.
  for (const candidate of [text, text.replace(/"/g, "'")]) {
    const index = lines.findIndex((line) => line.includes(candidate));
    if (index >= 0) return index + 1;
  }
  return 0;
}

// Find the first line of a file that contains this text, ignoring comment lines.
function codeLine(file, text) {
  if (!text) return 0;
  const lines = (state.files[file] || "").split("\n");
  for (let i = 0; i < lines.length; i++) {
    const trimmed = lines[i].trim();
    if (trimmed.startsWith("//") || trimmed.startsWith("#") || trimmed.startsWith("--")) continue;
    if (lines[i].replace(/\s+/g, " ").includes(text)) return i + 1;
  }
  return 0;
}

// Find the line of queries.sql where a statement starts, by comparing the text of the statement with the file. Returns 0 when it is not there.
function sqlLine(sql) {
  const lines = (state.files["queries.sql"] || "").split("\n");
  const norm = (text) => text.replace(/\s+/g, " ").trim();
  const want = norm(String(sql || "")).replace(/;$/, "");
  if (!want) return 0;
  const head = norm(String(sql).trim().split("\n")[0]);
  for (let i = 0; i < lines.length; i++) {
    if (!norm(lines[i]).startsWith(head)) continue;
    let joined = "";
    for (let j = i; j < lines.length && joined.length < want.length + 2; j++) joined = norm(joined + " " + lines[j]);
    if (joined.startsWith(want)) return i + 1;
  }
  return 0;
}

// Show the file in the editor on its side and mark the line, when "Follow in the code" is ticked.
function focusCode(file, line) {
  if (!state.follow || !file) return;
  const side = browserFileList().includes(file) ? "left" : serverFileList().includes(file) ? "right" : null;
  if (!side) return;
  if (state.panes[side] !== file) showFile(side, file);
  if (line) panes[side].editor.setBand(line, true);
}

function clearBands() { for (const side of ["left", "right"]) panes[side].editor.setBand(0); }

/* ---------- Reacting to edits ---------- */

let previewTimer = null;
let cssTimer = null;
let serverTimer = null;

// Called on every keystroke in an editor.
function onEdit(side, text) {
  const name = state.panes[side];
  state.files[name] = text;
  saveSoon();
  afterFileChange(side, name, true);
}

// Decide what an edit, an upload or a revert should update.
// A stylesheet changes the live page without reloading it. A page or script reloads the page.
// A server file rebuilds the server. While the student types, the work waits briefly so that it runs once per pause.
function afterFileChange(side, name, typing) {
  if (side === "left") {
    if (name.endsWith(".css")) {
      clearTimeout(cssTimer);
      cssTimer = setTimeout(() => postToPage({ type: "css", name, text: state.files[name] }), 120);
    } else {
      clearTimeout(previewTimer);
      // An edited page becomes the page on show, so the student sees the effect of the edit.
      const target = /\.html?$/i.test(name) ? name : state.page;
      previewTimer = setTimeout(() => loadPage(target, target === state.page ? state.query : "", { push: target !== state.page, reason: "You edited " + name + ", so the browser loads the page again." }), typing ? 700 : 0);
    }
  } else {
    clearTimeout(serverTimer);
    serverTimer = setTimeout(() => {
      rebuildServer();
      if (name === "schema.sql") notice("right", "The schema changed. Press Reset database to run it.");
    }, typing ? 450 : 0);
  }
}

// Put uploaded files into the project. The left editor accepts pages, styles and scripts.
// The right editor accepts SQL, routes and handlers, and renames a file when the server needs a fixed name.
async function uploadFiles(side, fileList) {
  for (const file of Array.from(fileList)) {
    const text = await file.text();
    let target = file.name;
    if (side === "left") {
      if (!/\.(html?|css|js)$/i.test(target)) { notice("left", target + " is not an HTML, CSS or JavaScript file."); continue; }
      state.files[target] = text;
      state.panes.left = target;
    } else {
      if (/\.sql$/i.test(target) && !serverFileList().includes(target)) {
        target = /-- name:/i.test(text) ? "queries.sql" : /create\s+table/i.test(text) ? "schema.sql" : "queries.sql";
        notice("right", "Loaded " + file.name + " as " + target + ", because the server reads that file name.");
      } else if (/\.txt$/i.test(target)) {
        target = "routes.txt";
      } else if (/\.(ts|py)$/i.test(target) && !target.startsWith("server.")) {
        const wanted = target.endsWith(".ts") ? "ts" : "py";
        if (wanted !== state.language) { notice("right", target + " is for the " + (wanted === "ts" ? "TypeScript" : "Python") + " server. Switch the server language first."); continue; }
        target = handlerFileName();
        notice("right", "Loaded " + file.name + " as " + target + ".");
      }
      if (target.startsWith("server.")) { notice("right", target + " is the machine itself, so it is read only. At the Advanced level you write a handlers file next to it, and the machine calls your handlers. Upload that file instead."); continue; }
      if (!SERVER_ONLY.has(target)) { notice("right", target + " is not a file the server reads."); continue; }
      state.files[target] = text;
      state.panes.right = target;
    }
    renderTabs(side);
    showFile(side, state.panes[side]);
    afterFileChange(side, target, false);
  }
  saveSoon();
}

/* ---------- The server ---------- */

// Compile the server code again, so that the next request runs the student's latest files.
function rebuildServer() {
  const sources = [{ name: engineFileName(), text: getFile(engineFileName()) }];
  if (state.level === "advanced") sources.push({ name: handlerFileName(), text: state.files[handlerFileName()] || "" });
  const problem = currentEngine().compile(sources);
  showProblem(problem);
  renderRoutes();
  return problem;
}

let previousTables = null;
// Throw the database away and run schema.sql again.
function resetDatabase() {
  const problem = currentEngine().reset(state.files["schema.sql"] || "");
  showProblem(problem);
  previousTables = null;
  renderDatabase();
}

// Draw every table. A row that was not in the previous drawing is marked as changed.
function renderDatabase() {
  const container = findElement("#db-tables");
  let tables;
  try { tables = currentEngine().tables(); } catch (error) { container.textContent = "The database has no tables yet."; return; }
  const before = previousTables;
  container.innerHTML = "";
  for (const table of tables) {
    const known = before && before[table.name] ? new Set(before[table.name]) : null;
    const section = document.createElement("section");
    section.className = "db-table";
    let html = "<h4>" + escapeHtml(table.name) + ' <span class="count">' + table.rows.length + (table.rows.length === 1 ? " row" : " rows") + "</span></h4><div class=\"scroll\"><table><thead><tr>";
    html += table.columns.map((column) => "<th>" + escapeHtml(column) + "</th>").join("") + "</tr></thead><tbody>";
    for (const row of table.rows) {
      const key = JSON.stringify(row);
      const fresh = known && !known.has(key);
      html += "<tr" + (fresh ? ' class="changed"' : "") + ">" + row.map((value) => "<td>" + escapeHtml(value === null ? "NULL" : String(value)) + "</td>").join("") + "</tr>";
    }
    html += "</tbody></table></div>";
    section.innerHTML = html;
    container.append(section);
  }
  previousTables = {};
  for (const table of tables) previousTables[table.name] = table.rows.map((row) => JSON.stringify(row));
}

// Show the addresses the server answers, by reading the files. This is a summary and does not run any code.
function renderRoutes() {
  const box = findElement("#routes-view");
  const rows = [];
  const queries = {};
  let currentName = "";
  (state.files["queries.sql"] || "").split("\n").forEach((text) => {
    const header = text.match(/^--\s*name:\s*(\w+)/);
    if (header) { currentName = header[1]; queries[currentName] = ""; } else if (currentName) queries[currentName] += text + "\n";
  });
  let intro = "";
  if (state.level === "beginner") {
    intro = "At this level the address names the query. A query that starts with SELECT needs GET. Every other query needs POST.";
    for (const [name, sql] of Object.entries(queries)) {
      const read = /^\s*(?:--[^\n]*\n\s*)*select/i.test(sql);
      const params = parameterNames(sql);
      rows.push([read ? "GET" : "POST", "/api/" + name + (params.length ? "?" + params.map((p) => p + "=...").join("&") : ""), "query " + name]);
    }
  } else if (state.level === "intermediate") {
    intro = "Each line of routes.txt is one route. The server reads the first line that matches the request.";
    (state.files["routes.txt"] || "").split("\n").forEach((text) => {
      const trimmed = text.trim();
      if (!trimmed || trimmed.startsWith("#")) return;
      const [method, path, query, shape] = trimmed.split(/\s+/);
      rows.push([method, path, "query " + (query || "?") + ", answers with " + (shape || "?")]);
    });
  } else {
    intro = "Each route( ... ) call in " + handlerFileName() + " adds one route. The server tries them in order.";
    const source = state.files[handlerFileName()] || "";
    const pattern = state.language === "ts" ? /route\(\s*["'](\w+)["']\s*,\s*["']([^"']+)["']/g : /@route\(\s*["'](\w+)["']\s*,\s*["']([^"']+)["']/g;
    for (const match of source.matchAll(pattern)) rows.push([match[1], match[2], "your handler function"]);
  }
  box.innerHTML = "<p>" + escapeHtml(intro) + "</p>" +
    (rows.length ? '<table><thead><tr><th>Method</th><th>Path</th><th>What runs</th></tr></thead><tbody>' +
      rows.map((row) => "<tr><td><code>" + escapeHtml(row[0]) + "</code></td><td><code>" + escapeHtml(row[1]) + "</code></td><td>" + escapeHtml(row[2]) + "</td></tr>").join("") + "</tbody></table>"
      : "<p>The server has no routes yet.</p>");
}

/* ---------- The preview of the page ---------- */

const previewFrame = findElement("#preview");

// Every page load gets a new document number. Messages from an older document are ignored,
// because the page they came from has already been replaced.
let currentDoc = 0;

// Turn a project page into one self-contained document for the preview frame.
// Stylesheets and scripts that the page links to are copied inside it, because the frame has no network to fetch them from.
// The bridge script is added first so that it is in place before the page's own scripts run.
function buildDocument(page, query, doc) {
  let html = state.files[page] || "";
  const missing = [];
  html = html.replace(/<link\b[^>]*>/gi, (tag) => {
    const href = (tag.match(/\bhref=["']([^"']+)["']/i) || [])[1];
    if (!href || !/rel=["']?stylesheet/i.test(tag)) return tag;
    if (state.files[href] === undefined) { missing.push(href); return tag; }
    return '<style data-file="' + href + '">' + state.files[href] + "</style>";
  });
  html = html.replace(/<script\b([^>]*)\bsrc=["']([^"']+)["']([^>]*)>\s*<\/script>/gi, (tag, before, src) => {
    if (state.files[src] === undefined) { missing.push(src); return tag; }
    return '<script data-file="' + src + '">' + state.files[src].replace(/<\/script/gi, "<\\/script") + "</script>";
  });
  const bridge = "<style>[data-wb-flash]{outline:3px solid #e8a317!important;outline-offset:-3px}</style><script>" +
    DATA.bridge.replace("@@DOC@@", String(doc)).replace("@@QUERY@@", query.replace(/^\?/, "").replace(/\\/g, "\\\\").replace(/"/g, '\\"')) + "<\/script>";
  if (/<head[^>]*>/i.test(html)) html = html.replace(/<head[^>]*>/i, (open) => open + bridge);
  else if (/<!doctype[^>]*>/i.test(html)) html = html.replace(/<!doctype[^>]*>/i, (open) => open + bridge);
  else html = bridge + html;
  return { html, missing };
}

// Show a page in the preview and add the load to the timeline.
// Options: push (add to the history, default true), paced (stop at each step while stepping is on), continuing (a link click began this interaction), reason (the text for the timeline).
function loadPage(name, query, options) {
  options = options || {};
  query = query || "";
  if (state.files[name] === undefined) {
    previewFrame.srcdoc = "<p style='font:16px system-ui;padding:20px'>There is no file named <b>" + escapeHtml(name) + "</b> in this project. A link or an address pointed to it.</p>";
    findElement("#address").textContent = "machine.local/" + name;
    enqueue(async () => { beginInteraction(); await playStep({ kind: "error", text: "The page " + name + " does not exist in this project." }); });
    return;
  }
  state.page = name;
  state.query = query;
  lastUserActionAt = performance.now();
  if (options.push !== false) state.history.push({ name, query });
  currentDoc += 1;
  const doc = currentDoc;
  if (!options.continuing) releaseOldRequest();
  const built = buildDocument(name, query, doc);
  previewFrame.srcdoc = built.html;
  findElement("#address").textContent = "machine.local/" + name + (query ? (query.startsWith("?") ? query : "?" + query) : "");
  findElement("#back").disabled = state.history.length < 2;
  const reason = options.reason || "The browser loads " + name + ".";
  enqueue(async () => {
    // A load that follows a link continues the interaction that the click began.
    if (!options.continuing || !interaction) beginInteraction();
    interaction.paced = Boolean(options.paced);
    await playStep({ kind: "load", text: reason });
    if (doc !== currentDoc) return;
    for (const file of built.missing) {
      await playStep({ kind: "error", text: name + " refers to the file " + file + ", but the project has no file with that name. Check the spelling." });
    }
  });
}

// A reload that the student asked for. It stops at each step while stepping is on.
function reloadPage(reason) { loadPage(state.page, state.query, { push: false, reason, paced: true }); }

// Send a message into the preview frame. The bridge script inside it listens.
function postToPage(message) {
  message.__wb = true;
  if (previewFrame.contentWindow) previewFrame.contentWindow.postMessage(message, "*");
}

/* ---------- The timeline ---------- */

/* Each step of a request has a kind. The chip says which station of the timeline it belongs to (-1 means none),
   and "why" is the short explanation shown on the card. */
const STATIONS = [
  "The browser notices the click", "The script builds a request", "The request travels", "The server chooses a handler",
  "The handler checks the input", "The handler sends SQL to the database", "The database changes the row", "The handler packages the result",
  "The server sends a response", "The reply reaches the script", "The script changes the DOM", "The browser repaints the screen",
];

const STEP_KINDS = {
  click: { stations: [1], label: "Click", chip: 0, why: "The browser noticed an event. A script in the page was waiting for it." },
  load: { label: "Page load", chip: 0, why: "The browser received the page and drew it. Scripts in the page can now ask the server for data." },
  request: { stations: [2, 3], label: "Request", chip: 1, why: "The script sends a message in the HTTP format. The message names a method, which says what to do, and a path, which says which thing to do it to." },
  route: { stations: [4], label: "Route", chip: 2, why: "The server compares the method and the path with its list of routes, and picks the code that is responsible. The next station, 5, is where that code checks its input. The workbench shows no card for it, and at the Advanced level you can read the check in your handler." },
  sql: { stations: [6, 7], label: "SQL", chip: 3, why: "The server asks the database a question in SQL. The values travel separately as parameters, so a visitor can never turn them into SQL commands." },
  response: { stations: [8, 9], label: "Response", chip: 4, why: "The server answers with a status code and a body. The body is JSON, which is text that JavaScript can turn back into objects." },
  dom: { stations: [10, 11, 12], label: "Screen update", chip: 5, why: "The script used the JSON to build or change elements in the page. The browser redraws those elements, and this is the moment the screen changes." },
  error: { label: "Problem", chip: -1, why: "Something went wrong in the page itself. The browser console would show this message." },
};

const STATUS_NAMES = { 200: "OK", 400: "Bad Request", 404: "Not Found", 405: "Method Not Allowed", 409: "Conflict", 500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable" };

// The timeline records every step of a request. The student moves through the steps with Start, Back, Forward and End.
// While stepping is on, the request waits after each step until the student presses Forward, so the page and the database change only when the student reaches that station.
let playbackChain = Promise.resolve();
let queuedTaskCount = 0;
let skippingToEnd = false;
let fastForwardOld = false;
let interaction = null;
let lastUserActionAt = 0;
let interactionCounter = 0;
let releaseNextStep = null;

// Add work to the end of the timeline's playback.
function enqueue(task) {
  queuedTaskCount += 1;
  playbackChain = playbackChain.then(task).catch((error) => console.error(error)).then(() => {
    queuedTaskCount -= 1;
    if (queuedTaskCount === 0) { skippingToEnd = false; if (interaction && interaction.steps.length) showAt(interaction.steps.length - 1); else updateControls(); }
  });
}

// Start a fresh set of cards and chips for a new interaction, such as one click and everything it causes.
function beginInteraction() {
  fastForwardOld = false;
  interaction = { id: ++interactionCounter, steps: [], cards: [], cursor: -1, queryName: "", terms: new Set() };
  findElement("#cards").innerHTML = "";
  findElements("#chips li").forEach((chip) => chip.classList.remove("active", "done", "bad"));
  clearBands();
  updateControls();
}

// After a step is shown, wait for the student to press Forward.
// Page loads that the workbench caused, such as after an edit, always run straight through, and so does a request that the student has left behind.
async function pause(step) {
  if (step.kind === "dom" || step.kind === "error") return;
  if (skippingToEnd || fastForwardOld || !state.stepping || !(interaction && interaction.paced)) { await sleep(0); return; }
  await new Promise((resolve) => { releaseNextStep = resolve; updateControls(); });
  releaseNextStep = null;
  // The student has just acted, so what the page does next belongs to the same request.
  lastUserActionAt = performance.now();
  updateControls();
}

// Let the waiting request carry on, and run through everything that the old request still has to do.
function releaseOldRequest() {
  fastForwardOld = true;
  if (releaseNextStep) releaseNextStep();
}

function stepForward() {
  if (!interaction || !interaction.steps.length) return;
  if (interaction.cursor < interaction.steps.length - 1) { showAt(interaction.cursor + 1); return; }
  if (releaseNextStep) releaseNextStep();
}
function stepBack() { if (interaction && interaction.cursor > 0) showAt(interaction.cursor - 1); }
function stepStart() { if (interaction && interaction.steps.length) showAt(0); }
function stepEnd() {
  if (!interaction || !interaction.steps.length) return;
  if (releaseNextStep || queuedTaskCount > 0) { skippingToEnd = true; if (releaseNextStep) releaseNextStep(); }
  showAt(interaction.steps.length - 1);
}

function updateControls() {
  const total = interaction ? interaction.steps.length : 0;
  const at = interaction ? interaction.cursor : -1;
  const waiting = Boolean(releaseNextStep);
  const finished = queuedTaskCount === 0 && !waiting;
  findElement("#step-start").disabled = total === 0 || at <= 0;
  findElement("#step-back").disabled = total === 0 || at <= 0;
  findElement("#step-forward").disabled = total === 0 || (at >= total - 1 && !waiting);
  findElement("#step-end").disabled = total === 0 || (at >= total - 1 && finished);
  findElement("#step-pos").textContent = total === 0 ? "No steps yet" : "Step " + (at + 1) + " of " + total + (finished ? "" : " so far");
  const looking = total > 0 && at < total - 1;
  findElement("#tl-state").textContent = looking
    ? "You are looking at an earlier step. The page and the database keep their latest state."
    : waiting ? "Press Forward to continue." : queuedTaskCount > 0 ? "The request is moving." : "";
}

// Show the step at this position: its card, its chips and its line of code. Cards after this step are hidden until the student gets there.
function showAt(index) {
  if (!interaction || !interaction.steps.length) { updateControls(); return; }
  const steps = interaction.steps;
  index = Math.max(0, Math.min(index, steps.length - 1));
  interaction.cursor = index;
  interaction.cards.forEach((card, i) => { card.hidden = i > index; card.classList.toggle("active", i === index); });
  const reached = new Set();
  for (let i = 0; i <= index; i++) { const kind = STEP_KINDS[steps[i].kind]; if (kind && kind.chip >= 0) reached.add(kind.chip); }
  const step = steps[index];
  const current = STEP_KINDS[step.kind];
  findElements("#chips li").forEach((chip, i) => {
    const here = Boolean(current) && current.chip === i;
    chip.classList.toggle("active", here);
    chip.classList.toggle("done", !here && reached.has(i));
    chip.classList.toggle("bad", here && step.kind === "response" && step.status >= 400);
  });
  clearBands();
  if (step.file && step.line) focusCode(step.file, step.line);
  interaction.cards[index].scrollIntoView({ block: "nearest", inline: "nearest" });
  updateControls();
}

function prettyJson(value) {
  let text;
  try { text = JSON.stringify(value, null, 2); } catch (error) { text = String(value); }
  return text.length > 1400 ? text.slice(0, 1400) + "\n..." : text;
}

// The details shown on a card, which depend on the kind of step: the request, the SQL, or the response.
function stepBody(step) {
  if (step.kind === "request") {
    let html = '<p class="mono">' + escapeHtml(step.method + " " + step.path + (step.search || "")) + "</p>";
    html += step.body ? '<pre class="detail">' + escapeHtml(step.body) + "</pre>" : '<p class="quiet">There is no body.</p>';
    return html;
  }
  if (step.kind === "sql") {
    let html = '<pre class="detail">' + colourise(step.sql, "sql") + "</pre>";
    const names = Object.keys(step.params || {});
    if (names.length) html += '<p class="mono">' + names.map((name) => escapeHtml(":" + name + " = " + JSON.stringify(step.params[name]))).join("<br>") + "</p>";
    html += '<p class="result' + (String(step.result).startsWith("error") ? " bad" : "") + '">' + escapeHtml(step.result) + " (" + step.ms.toFixed(1) + " ms)</p>";
    if (step.rows && step.rows.length) {
      const columns = Object.keys(step.rows[0]);
      html += '<div class="scroll"><table class="mini"><thead><tr>' + columns.map((c) => "<th>" + escapeHtml(c) + "</th>").join("") + "</tr></thead><tbody>" +
        step.rows.map((row) => "<tr>" + columns.map((c) => "<td>" + escapeHtml(String(row[c])) + "</td>").join("") + "</tr>").join("") + "</tbody></table></div>";
    }
    return html;
  }
  if (step.kind === "response") {
    return '<p class="mono status s' + String(step.status)[0] + '">' + step.status + " " + (STATUS_NAMES[step.status] || "") + "</p>" +
      '<pre class="detail">' + escapeHtml(prettyJson(step.body)) + "</pre>";
  }
  return "";
}

// The words for the stations a step covers, such as "Stations 2 to 3", with the stations before and after it.
function stationHtml(info) {
  if (!info || !info.stations) return "";
  const list = info.stations;
  const first = list[0];
  const last = list[list.length - 1];
  const heading = list.length === 1 ? "Station " + first : "Stations " + first + " to " + last;
  const titles = list.map((n, i) => (i === 0 ? STATIONS[n - 1] : STATIONS[n - 1][0].toLowerCase() + STATIONS[n - 1].slice(1))).join(", then ");
  const before = first === 1 ? "the click has not happened yet" : "Station " + (first - 1) + ", " + STATIONS[first - 2];
  const next = last === 12 ? "the journey is over" : "Station " + (last + 1) + ", " + STATIONS[last];
  const page = state.language === "py" ? "python.html" : "typescript.html";
  return '<p class="station"><b><a href="../' + page + '#journey" target="_blank" rel="noopener" title="Open the journey in the tutorial">' + heading + "</a></b> " + escapeHtml(titles) + "</p>" +
    '<p class="trail"><span>&larr; Before: ' + escapeHtml(before) + "</span><span>Next: " + escapeHtml(next) + " &rarr;</span></p>";
}

function renderCard(step, index) {
  const info = STEP_KINDS[step.kind] || { label: "Note", why: "" };
  const card = document.createElement("article");
  card.className = "card kind-" + step.kind + (step.kind === "response" && step.status >= 400 ? " bad" : "");
  card.innerHTML = '<header><span class="num">' + (index + 1) + "</span> " + escapeHtml(info.label) + "</header>" + stationHtml(info) +
    "<p>" + termHtml(step.text) + "</p>" + stepBody(step) + (info.why ? '<p class="why">' + termHtml(info.why) + "</p>" : "");
  return card;
}

// Add one line to the text log under "Log".
function appendLog(step) {
  const log = findElement("#log");
  const when = new Date().toLocaleTimeString([], { hour12: false });
  let line = when + "  " + (STEP_KINDS[step.kind] ? STEP_KINDS[step.kind].label : "Note") + ": " + step.text;
  if (step.sql) line += "\n    " + step.sql.replace(/\s+/g, " ");
  log.textContent += line + "\n";
  log.scrollTop = log.scrollHeight;
}

async function playStep(step) {
  if (!interaction) beginInteraction();
  // Work out which line of code this step is about.
  // The steps from the server say where they come from. The steps from the page are matched against text in client.js,
  // so these highlights stop quietly when a student replaces client.js with a script that does not contain that text.
  if (step.kind === "route") interaction.queryName = step.query || "";
  if (step.kind === "route" && step.find && !step.line) step.line = lineOf(step.file, step.find);
  if (step.kind === "route" && step.file && step.line) interaction.serverMark = { file: step.file, line: step.line };
  if (step.kind === "sql") {
    // Mark the statement itself in queries.sql. A step such as BEGIN or COMMIT has no line of its own, so it marks the name of the query.
    const wording = String(step.sql || "").replace(/\s+/g, " ").trim();
    let file = "queries.sql";
    let line = 0;
    if (state.level === "advanced") {
      // A handler may write its SQL inside the handlers file, and BEGIN and COMMIT belong to the line that opens the transaction.
      const handlers = handlerFileName();
      const wrapper = /^(BEGIN|COMMIT|ROLLBACK)/i.test(wording);
      line = codeLine(handlers, wrapper ? "db.transaction" : wording.slice(0, 30));
      if (line) file = handlers;
    }
    if (!line) line = sqlLine(step.sql) || (interaction.queryName ? lineOf("queries.sql", "name: " + interaction.queryName) : 0);
    if (line) { step.file = file; step.line = line; }
  }
  // The answer is built by the code that the route chose, so the response step marks that code again.
  if (step.kind === "response" && interaction.serverMark) { step.file = interaction.serverMark.file; step.line = interaction.serverMark.line; }
  if (step.kind === "request") { step.file = "client.js"; step.line = lineOf("client.js", step.method === "GET" ? "dataset.get" : "dataset.post"); }
  if (step.kind === "dom") { step.file = "client.js"; step.line = lineOf("client.js", "section.append") || lineOf("client.js", "textContent"); }
  if (step.kind === "click") { step.file = "client.js"; step.line = lineOf("client.js", step.viaSubmit ? 'addEventListener("submit"' : 'addEventListener("click"'); }

  lastUserActionAt = performance.now();
  interaction.steps.push(step);
  interaction.cards.push(renderCard(step, interaction.steps.length - 1));
  findElement("#cards").append(interaction.cards[interaction.cards.length - 1]);
  showAt(interaction.steps.length - 1);
  appendLog(step);
  if (step.kind === "response") renderDatabase();
  await pause(step);
}

// Answer one request that the page made. This plays the request card, runs the server code,
// plays every step the server recorded, plays the response card, and finally sends the answer back into the page.
async function handleFetch(message) {
  const url = new URL(message.url, "http://machine.local/");
  const search = url.search;
  await playStep({
    kind: "request", method: message.method, path: url.pathname, search, body: message.body,
    text: "The page sends " + message.method + " " + url.pathname + search + ".",
  });
  // The student may have reloaded the page while the timeline was playing. Then this request is out of date.
  if (message.doc !== currentDoc) return;

  let result;
  let body = {};
  let bodyProblem = "";
  if (message.body) {
    try {
      const parsed = JSON.parse(message.body);
      body = parsed && typeof parsed === "object" && !Array.isArray(parsed) ? parsed : { value: parsed };
    } catch (error) { bodyProblem = "The body of the request is not valid JSON."; }
  }
  if (url.origin !== "http://machine.local") {
    result = { status: 502, body: { error: "The workbench only serves addresses on its own machine, and " + url.origin + " is somewhere else." }, steps: [] };
  } else if (bodyProblem) {
    result = { status: 400, body: { error: bodyProblem }, steps: [] };
  } else if (!currentEngine().ready || (currentEngine().loading)) {
    result = { status: 503, body: { error: "The server is still starting." }, steps: [] };
  } else {
    result = currentEngine().handle({ method: message.method, path: url.pathname, query: Object.fromEntries(url.searchParams), body });
  }

  for (const step of result.steps) {
    if (message.doc !== currentDoc) return;
    if (step.kind === "route" && step.file && step.find && !step.line) step.line = lineOf(step.file, step.find);
    await playStep(step);
  }
  await playStep({
    kind: "response", status: result.status, body: result.body,
    text: "The server answers with status " + result.status + (STATUS_NAMES[result.status] ? " (" + STATUS_NAMES[result.status] + ")" : "") + ".",
  });
  if (message.doc !== currentDoc) return;
  postToPage({ type: "reply", id: message.id, status: result.status, bodyText: JSON.stringify(result.body) });
}

// Messages from the page in the preview frame. The bridge script sends them.
window.addEventListener("message", (event) => {
  if (event.source !== previewFrame.contentWindow) return;
  const message = event.data;
  if (!message || !message.__wb || message.doc !== currentDoc) return;
  const now = performance.now();
  if (message.type === "click") {
    lastUserActionAt = now;
    releaseOldRequest();
    enqueue(async () => { beginInteraction(); interaction.paced = true; await playStep({ kind: "click", viaSubmit: message.viaSubmit, text: message.viaSubmit ? "The page sent a form." : "You clicked " + message.label + "." }); });
  } else if (message.type === "navigate") {
    lastUserActionAt = now;
    releaseOldRequest();
    const [name, ...rest] = message.href.split("?");
    enqueue(async () => { beginInteraction(); interaction.paced = true; await playStep({ kind: "click", text: "You followed the link " + message.label + "." }); });
    loadPage(name, rest.length ? "?" + rest.join("?") : "", { continuing: true, paced: true });
  } else if (message.type === "fetch") {
    if (now - lastUserActionAt > 2500) enqueue(async () => { beginInteraction(); interaction.paced = true; });
    lastUserActionAt = now;
    enqueue(() => handleFetch(message));
  } else if (message.type === "dom") {
    lastUserActionAt = now;
    enqueue(() => playStep({ kind: "dom", text: "The page changed: " + message.summary + ". The browser redraws those parts." }));
  } else if (message.type === "error") {
    enqueue(() => playStep({ kind: "error", text: message.message }));
  }
});

/* ---------- Things to try ----------
   Suggestions for each level. Each one was run in the workbench, and each one names what the student should look at. */

const THINGS_TO_TRY = {
  beginner: [
    "Press Buy on A1 and read each card of the timeline. Which table in the Database panel changes, and which row?",
    "Press Buy on B1, which has no stock left. Which status code does the server send, and what does the page show?",
    "In queries.sql, change stock > 0 to stock > 1 in both statements of buy_slot. Press Buy on B2 three times. What happens on the third press, and is that what the machine should do?",
    "In style.css, change a colour. The page changes at once. Which steps of the timeline did not happen, and why?",
    "Open Try SQL and run SELECT * FROM sales. Run it again after buying something.",
    "Write a new query called list_cheap in queries.sql that selects the slots with price_cents below 160. Then change data-get in index.html to /api/list_cheap.",
  ],
  intermediate: [
    "In routes.txt, change the path /api/slots to /api/machine. What does the page show, and which card of the timeline tells you why?",
    "Change the method of buy_slot from POST to GET. What status does the Buy button receive?",
    "Change the shape of buy_slot from change to rows, and press Buy. Compare the Database panel with the SQL cards. Which statement never ran?",
    "Add a query called low_stock to queries.sql, add a route for it to routes.txt, and show it in a new page with data-get.",
    "Delete the line for sales.html from the navigation in one page. How does the rest of the site behave?",
  ],
  advanced: [
    "Change the 409 answer in the buy handler to 400, and watch the status card change. Which one describes the problem better?",
    "Add a route that answers GET /api/slots/:slot/price with only the price. Use db.get and an existing query.",
    "In the buy handler, move the INSERT above the UPDATE. Press Buy on B1, which is sold out. Which rows change, and why does the sale stay? How could you make the sale disappear again?",
    "Make a handler fail on purpose by throwing an error. Which status does the server send, and which part of the server caught it?",
    "Write a handler for a route that does not exist yet, and call it from a new page with data-get or data-post.",
  ],
};

function renderIdeas() {
  const list = findElement("#try-list");
  list.innerHTML = "";
  findElement(".try-panel p").textContent = "Suggestions for the " + state.level + " level. Pick one, then press Forward to move through the timeline and watch which step changes.";
  for (const idea of THINGS_TO_TRY[state.level]) {
    const item = document.createElement("li");
    item.textContent = idea;
    list.append(item);
  }
}

/* ---------- Controls ---------- */

// Bring the buttons, the help text and the suggestions in line with the current state.
function reflectControls() {
  for (const group of findElements(".seg")) {
    const setting = group.dataset.setting;
    for (const button of findElements("button", group)) button.setAttribute("aria-pressed", String(String(state[setting]) === button.dataset.value));
  }
  findElement("#follow").checked = state.follow;
  findElement("#stepping").checked = state.stepping;
  renderIdeas();
  const seen = new Set();
  findElement("#level-help").innerHTML = termHtml({
    beginner: "Beginner: you write HTML, CSS and SQL. The address names the query, for example /api/list_slots, so the server does the routing for you.",
    intermediate: "Intermediate: you also write routes.txt. Each line maps a method and a path to a query.",
    advanced: "Advanced: you write the handlers yourself, in " + (state.language === "ts" ? "TypeScript" : "Python") + ". A handler is the function that answers one route.",
  }[state.level], seen);
  findElement("#mode-help").innerHTML = termHtml(state.mode === "explore"
    ? "Explore: a finished vending machine with four pages. Press Buy, then press Forward to move through the request one step at a time."
    : "Bring your own: upload your HTML and CSS on the left and your SQL on the right, or paste them in.", seen);
}

// Change the level. Files the student has not edited take the new level's version.
async function changeLevel(level) {
  if (level === state.level) return;
  const previousBaseline = state.baseline;
  state.level = level;
  const newBaseline = DATA.samples[state.mode][level];
  // A file the student has not touched takes the new level's version. A file they edited stays as they left it.
  for (const name of Object.keys(newBaseline)) {
    const untouched = state.files[name] === previousBaseline[name];
    const newToProject = state.files[name] === undefined && previousBaseline[name] === undefined;
    if (untouched || newToProject) state.files[name] = newBaseline[name];
  }
  state.baseline = { ...newBaseline };
  state.panes.right = defaultServerTab();
  await applyEverything("You changed the level, so the pages use that level's addresses.");
}

// Change the server language. The Python server downloads Pyodide the first time, so this can take a few seconds.
async function changeLanguage(language) {
  if (language === state.language) return;
  if (!engines[language]) { notice("right", "The Python server is not available in this build."); return; }
  setBusy(true, language === "py" ? "Python is loading. The first time, this downloads about 10 MB." : "");
  try {
    await engines[language].ready();
  } catch (error) {
    setBusy(false);
    notice("right", String(error.message || error));
    return;
  }
  setBusy(false);
  state.language = language;
  state.panes.right = defaultServerTab();
  await applyEverything("You changed the server language.");
}

// Switch between the finished vending machine and the starter project. Edited files are replaced, so the student confirms first.
async function changeMode(mode) {
  if (mode === state.mode) return;
  if (hasEdits() && !window.confirm("Switching replaces the files you changed. Do you want to continue?")) return;
  state.mode = mode;
  loadBase(mode, state.level);
  state.panes.left = "index.html";
  state.panes.right = defaultServerTab();
  await applyEverything("You switched mode.");
}

// After the level, the language or the mode changes: rebuild the server, reset the database, redraw the editors and load the first page.
async function applyEverything(reason) {
  reflectControls();
  setBusy(true);
  try {
    await currentEngine().ready();
    rebuildServer();
    resetDatabase();
  } catch (error) {
    showProblem({ file: "server", message: String(error.message || error) });
  }
  setBusy(false);
  renderTabs("left");
  renderTabs("right");
  showFile("left", state.panes.left);
  showFile("right", state.panes.right);
  state.history = [];
  loadPage("index.html", "", { reason });
  saveSoon();
}

// Show or hide the message that says the server is starting.
function setBusy(busy, message) {
  document.body.classList.toggle("busy", busy);
  findElement("#busy").textContent = busy ? message || "The server is starting." : "";
}

// Save the whole project as one ZIP file: the pages next to each other, and the server files in a server folder.
function downloadProject() {
  const entries = [];
  for (const name of browserFileList()) entries.push({ name, text: state.files[name] });
  for (const name of ["schema.sql", "queries.sql"]) entries.push({ name: "server/" + name, text: state.files[name] || "" });
  if (state.level === "intermediate") entries.push({ name: "server/routes.txt", text: state.files["routes.txt"] || "" });
  if (state.level === "advanced") entries.push({ name: "server/" + handlerFileName(), text: state.files[handlerFileName()] || "" });
  entries.push({ name: "README.txt", text: "This project was made in the workbench.\nThe pages and the stylesheet are in this folder.\nThe SQL and the server files are in the server folder.\nLevel: " + state.level + ". Server language: " + (state.language === "ts" ? "TypeScript" : "Python") + ".\n" });
  downloadBlob(makeZip(entries), "workbench-project.zip");
}

// Attach every button, tab, splitter and form to the code that responds to it.
function bindControls() {
  for (const group of findElements(".seg")) {
    group.addEventListener("click", (event) => {
      const button = event.target.closest("button");
      if (!button) return;
      const setting = group.dataset.setting;
      const value = button.dataset.value;
      if (setting === "level") changeLevel(value);
      else if (setting === "language") changeLanguage(value);
      else if (setting === "mode") changeMode(value);
    });
  }
  findElement("#follow").addEventListener("change", (event) => { state.follow = event.target.checked; saveSoon(); });
  findElement("#step-start").addEventListener("click", stepStart);
  findElement("#step-back").addEventListener("click", stepBack);
  findElement("#step-forward").addEventListener("click", stepForward);
  findElement("#step-end").addEventListener("click", stepEnd);
  findElement("#stepping").addEventListener("change", (event) => { state.stepping = event.target.checked; if (!state.stepping && releaseNextStep) releaseNextStep(); saveSoon(); });
  // With the cards focused, the arrow keys, Home and End move through the steps.
  findElement("#cards").addEventListener("keydown", (event) => {
    const keys = { ArrowRight: stepForward, ArrowLeft: stepBack, Home: stepStart, End: stepEnd };
    if (!keys[event.key]) return;
    event.preventDefault();
    keys[event.key]();
  });
  findElement("#clear-log").addEventListener("click", () => { findElement("#log").textContent = ""; });
  findElement("#start-over").addEventListener("click", async () => {
    if (hasEdits() && !window.confirm("Start over replaces the files you changed with the originals. Do you want to continue?")) return;
    loadBase(state.mode, state.level);
    state.panes.left = "index.html";
    state.panes.right = defaultServerTab();
    await applyEverything("You started over.");
  });
  findElement("#reset-db").addEventListener("click", () => { resetDatabase(); notice("right", "The database is back to the rows in schema.sql."); });
  findElement("#download-project").addEventListener("click", downloadProject);
  findElement("#back").addEventListener("click", () => {
    if (state.history.length < 2) return;
    state.history.pop();
    const previous = state.history[state.history.length - 1];
    loadPage(previous.name, previous.query, { push: false, paced: true, reason: "You went back to " + previous.name + "." });
  });
  findElement("#reload").addEventListener("click", () => reloadPage("You reloaded the page."));

  findElements(".subtabs").forEach((list) => {
    list.addEventListener("click", (event) => {
      const button = event.target.closest("button[data-name]");
      if (!button) return;
      findElements("button[data-name]", list).forEach((other) => other.setAttribute("aria-selected", String(other === button)));
      const group = list.dataset.group;
      findElements("[data-panel='" + group + "']").forEach((panel) => { panel.hidden = panel.dataset.name !== button.dataset.name; });
    });
  });

  findElement("#sql-form").addEventListener("submit", (event) => {
    event.preventDefault();
    const outcome = currentEngine().runSqlConsole(findElement("#sql-input").value);
    const box = findElement("#sql-result");
    if (outcome.error) { box.innerHTML = '<p class="result bad">' + escapeHtml(outcome.error) + "</p>"; return; }
    if (!outcome.columns.length) { box.innerHTML = "<p>" + escapeHtml(outcome.message || "Done.") + "</p>"; renderDatabase(); return; }
    box.innerHTML = '<div class="scroll"><table class="mini"><thead><tr>' + outcome.columns.map((c) => "<th>" + escapeHtml(c) + "</th>").join("") + "</tr></thead><tbody>" +
      outcome.rows.map((row) => "<tr>" + row.map((value) => "<td>" + escapeHtml(value === null ? "NULL" : String(value)) + "</td>").join("") + "</tr>").join("") + "</tbody></table></div>";
    renderDatabase();
  });

  findElements(".viewtabs button").forEach((button) => {
    button.addEventListener("click", () => {
      document.body.dataset.view = button.dataset.view;
      findElements(".viewtabs button").forEach((other) => other.setAttribute("aria-pressed", String(other === button)));
    });
  });

  const main = findElement("#main");
  const timeline = findElement("#timeline");
  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));
  makeSplitter(findElement("#split-x"), {
    axis: "x",
    get: () => findElement("#pane-left").getBoundingClientRect().width,
    set: (pixels) => main.style.setProperty("--col-left", clamp(pixels, 280, main.clientWidth - 330) + "px"),
  });
  makeSplitter(findElement("#split-left"), {
    axis: "y",
    get: () => findElement("#left-top").getBoundingClientRect().height,
    set: (pixels) => findElement("#pane-left").style.setProperty("--top-height", clamp(pixels, 120, findElement("#pane-left").clientHeight - 170) + "px"),
  });
  makeSplitter(findElement("#split-right"), {
    axis: "y",
    get: () => findElement("#right-top").getBoundingClientRect().height,
    set: (pixels) => findElement("#pane-right").style.setProperty("--top-height", clamp(pixels, 120, findElement("#pane-right").clientHeight - 170) + "px"),
  });
  makeSplitter(findElement("#split-timeline"), {
    axis: "y", invert: true,
    get: () => timeline.getBoundingClientRect().height,
    set: (pixels) => document.documentElement.style.setProperty("--timeline-height", clamp(pixels, 150, window.innerHeight - 300) + "px"),
  });
}

/* ---------- Hover terms ----------
   A word with a dotted underline explains itself on hover, on keyboard focus and on touch.
   The texts come from the same list as the tutorial, so a word means the same thing in both places.
   One floating box shows the text, so a card that scrolls can never cut it off. */

let termPattern = null;
const termInfo = {};

function buildTerms() {
  const names = Object.keys(DATA.terms).sort((a, b) => b.length - a.length);
  for (const name of names) {
    // Acronyms such as SQL and JSON match only in capitals, so an ordinary word is never marked by mistake.
    const exact = name !== name.toLowerCase() && name !== name[0].toUpperCase() + name.slice(1).toLowerCase();
    termInfo[name.toLowerCase()] = { name, def: DATA.terms[name], exact };
  }
  termPattern = new RegExp("(?<![\\w-])(" + names.map((n) => n.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")(s?)(?![\\w-])", "gi");
}

// Turn plain text into HTML in which the first use of each key word (once per set) carries its explanation.
function termHtml(text, seen) {
  text = String(text);
  seen = seen || (interaction ? interaction.terms : new Set());
  let out = "";
  let last = 0;
  for (const match of text.matchAll(termPattern)) {
    const key = match[1].toLowerCase();
    const info = termInfo[key];
    if (!info || seen.has(key) || (info.exact && match[1] !== info.name)) continue;
    seen.add(key);
    out += escapeHtml(text.slice(last, match.index)) + '<span class="term" tabindex="0" data-def="' + escapeHtml(info.def).replace(/"/g, "&quot;") + '">' + escapeHtml(match[0]) + "</span>";
    last = match.index + match[0].length;
  }
  return out + escapeHtml(text.slice(last));
}

function setupTips() {
  const tip = findElement("#tip");
  const show = (term) => {
    tip.textContent = term.dataset.def;
    tip.hidden = false;
    const box = term.getBoundingClientRect();
    const size = tip.getBoundingClientRect();
    const left = Math.max(8, Math.min(window.innerWidth - size.width - 8, box.left + box.width / 2 - size.width / 2));
    const top = box.top - size.height - 8 >= 8 ? box.top - size.height - 8 : box.bottom + 8;
    tip.style.left = left + "px";
    tip.style.top = top + "px";
  };
  const hide = () => { tip.hidden = true; };
  document.addEventListener("mouseover", (event) => { const term = event.target.closest && event.target.closest(".term"); if (term) show(term); });
  document.addEventListener("mouseout", (event) => { if (event.target.closest && event.target.closest(".term")) hide(); });
  document.addEventListener("focusin", (event) => { const term = event.target.closest && event.target.closest(".term"); if (term) show(term); });
  document.addEventListener("focusout", hide);
  document.addEventListener("scroll", hide, true);
}

/* ---------- The setup screen ----------
   The student chooses a mode, a level and a server language (and may upload files),
   reads a short tour of the files and how they connect, and then opens the workbench. */

let hadSavedWork = false;
let workbenchStarted = false;
const staged = [];   // files chosen on the setup screen, as { name, text }

const PAGE_FILE = /\.(html?|css|js)$/i;

// What each file is for, in one or two sentences. The key is the file name, with the language filled in for the server files.
function fileNote(name) {
  if (name === "style.css") return "How the pages look: colours, sizes and layout. A change here never changes what a page does.";
  if (name === "client.js") return "The only JavaScript. It reads the data- attributes in the HTML, sends the request and fills the page in with the answer. You can read it, and you rarely need to change it.";
  if (name === "item.html") return "The page for one slot. The slot comes from the address, for example item.html?slot=A1, and the page asks the server for that slot.";
  if (name === "restock.html") return "A page with a form that adds stock to a slot. Sending the form is a POST request.";
  if (name === "sales.html") return "A page that lists the sales that the database has recorded.";
  if (/\.html?$/i.test(name)) return name === "index.html"
    ? "The first page. It holds the structure: headings, buttons and empty places to fill. A data-get attribute tells client.js which address to ask for data."
    : "Another page. It is built the same way as index.html, and links connect the pages.";
  if (name === "schema.sql") return "The tables and the rows they start with. Reset database runs this file again.";
  if (name === "queries.sql") return "Every question the server may ask the database. Each query starts with a comment of the form -- name: something, and a word such as :slot is a parameter.";
  if (name === "routes.txt") return "One route per line: the method, the path, the name of the query and the shape of the answer.";
  if (/^handlers\./.test(name)) return "Your handlers. Each call to route(method, pattern, handler) says what to do when that request arrives.";
  if (/^server\./.test(name)) return "The machine itself. It listens for requests, finds the route, runs the query and sends the answer. It is read only, and you can read it to see how a server works.";
  return "A file you added.";
}

// Which server file an uploaded file will become. This follows the same rules as the editors.
function uploadTarget(entry, language) {
  const name = entry.name;
  if (PAGE_FILE.test(name)) return name;
  if (/\.sql$/i.test(name) && name !== "schema.sql" && name !== "queries.sql") return /-- name:/i.test(entry.text) ? "queries.sql" : /create\s+table/i.test(entry.text) ? "schema.sql" : "queries.sql";
  if (/\.txt$/i.test(name)) return "routes.txt";
  if (/\.(ts|py)$/i.test(name) && !name.startsWith("server.")) return "handlers." + language;
  return name;
}

function chosen(name) { const input = findElement('input[name="intro-' + name + '"]:checked'); return input ? input.value : ""; }

function showIntro() {
  document.body.classList.add("setup");
  for (const [group, value] of [["mode", state.mode], ["level", state.level], ["language", state.language]]) {
    const input = findElement('input[name="intro-' + group + '"][value="' + value + '"]');
    if (input) input.checked = true;
  }
  findElement("#intro-upload").hidden = chosen("mode") !== "own";
  findElement("#intro-saved").hidden = !(hadSavedWork || workbenchStarted);
  findElement("#intro-continue").textContent = workbenchStarted ? "Go back to my project" : "Continue with my saved project";
  findElement("#intro-choose").hidden = false;
  findElement("#intro-files-view").hidden = true;
  window.scrollTo(0, 0);
}

function renderGuide() {
  const mode = chosen("mode");
  const level = chosen("level");
  const language = chosen("language");
  const sample = DATA.samples[mode][level];
  const uploads = {};
  for (const entry of staged) uploads[uploadTarget(entry, language)] = entry.name;
  const rank = (n) => (n === "index.html" ? 0 : n.endsWith(".html") ? 1 : n.endsWith(".css") ? 2 : 3);
  const pages = Array.from(new Set([...Object.keys(sample).filter((n) => !SERVER_ONLY.has(n)), ...Object.keys(uploads).filter((n) => PAGE_FILE.test(n))])).sort((a, b) => rank(a) - rank(b) || a.localeCompare(b));
  const server = [];
  if (level === "advanced") server.push("handlers." + language);
  if (level === "intermediate") server.push("routes.txt");
  server.push("queries.sql", "schema.sql", "server." + language);
  const group = (title, names, intro) => {
    const items = names.map((n) => "<li><span><code>" + escapeHtml(n) + "</code>" + (uploads[n] ? '<span class="tag">from ' + escapeHtml(uploads[n]) + "</span>" : "") + "</span><span>" + termHtml(fileNote(n), seen) + "</span></li>").join("");
    return '<div class="guide-group"><h3>' + escapeHtml(title) + "</h3>" + (intro ? '<p class="quiet">' + termHtml(intro, seen) + "</p>" : "") + "<ul>" + items + "</ul></div>";
  };
  const seen = new Set();
  const label = { explore: "Explore", own: "Bring your own", beginner: "Beginner", intermediate: "Intermediate", advanced: "Advanced", ts: "TypeScript", py: "Python" };
  findElement("#intro-summary").textContent = label[mode] + ", " + label[level] + " level, " + label[language] + " server. Files on the left of the workbench run in the browser. Files on the right run in the server.";
  findElement("#intro-guide").innerHTML =
    group("Front end: runs in the browser", pages, "These files make the page. The browser loads them first.") +
    group("Back end: runs in the server and the database", server, level === "beginner" ? "You write queries.sql and schema.sql. The server file does the rest." : level === "intermediate" ? "You write routes.txt, queries.sql and schema.sql." : "You write the handlers file, queries.sql and schema.sql.");
  const choose = {
    beginner: "The server reads the address, which names a query, for example /api/list_slots runs the query list_slots (Station 4).",
    intermediate: "The server looks the method and the path up in routes.txt, which names the query to run (Station 4).",
    advanced: "The server finds the route that your handlers file registered and calls your handler, which checks the input (Stations 4 and 5).",
  }[level];
  const second = level === "advanced" ? "Your handler picks a query from queries.sql and runs it against the tables that schema.sql created (Stations 6 and 7)." : "The query in queries.sql runs against the tables that schema.sql created (Stations 6 and 7).";
  const flow = [
    "You press a button in a page. The browser notices the click (Station 1), and client.js builds and sends a request (Stations 2 and 3).",
    choose,
    second,
    "The server answers with a status code and JSON (Stations 8 and 9). client.js receives the answer and changes the page, and the browser repaints it (Stations 10 to 12).",
  ];
  findElement("#intro-flow").innerHTML = flow.map((line) => "<li>" + termHtml(line, seen) + "</li>").join("");
}

async function openFromSetup() {
  if (hasEdits() && !window.confirm("A new setup replaces the files you changed. Do you want to continue?")) return;
  state.mode = chosen("mode");
  state.level = chosen("level");
  state.language = chosen("language");
  loadBase(state.mode, state.level);
  state.panes.left = "index.html";
  state.panes.right = defaultServerTab();
  document.body.classList.remove("setup");
  await startWorkbench();
  // Files from the setup screen go in after the project is running, so each one is checked and shown as if it had been uploaded in an editor.
  const asFiles = (list) => list.map((entry) => ({ name: entry.name, text: async () => entry.text }));
  const pages = staged.filter((entry) => PAGE_FILE.test(entry.name));
  const others = staged.filter((entry) => !PAGE_FILE.test(entry.name));
  if (pages.length) await uploadFiles("left", asFiles(pages));
  if (others.length) await uploadFiles("right", asFiles(others));
  staged.length = 0;
  findElement("#intro-staged").textContent = "";
}

function bindIntro() {
  const modeInputs = findElements('input[name="intro-mode"]');
  modeInputs.forEach((input) => input.addEventListener("change", () => { findElement("#intro-upload").hidden = chosen("mode") !== "own"; }));
  findElement("#intro-files").addEventListener("change", async (event) => {
    for (const file of Array.from(event.target.files)) {
      if (!/\.(html?|css|js|sql|txt|ts|py)$/i.test(file.name)) continue;
      const entry = { name: file.name, text: await file.text() };
      const at = staged.findIndex((other) => other.name === entry.name);
      if (at >= 0) staged[at] = entry; else staged.push(entry);
    }
    event.target.value = "";
    findElement("#intro-staged").textContent = staged.length ? "Ready to add: " + staged.map((entry) => entry.name).join(", ") + "." : "";
  });
  findElement("#intro-next").addEventListener("click", () => {
    renderGuide();
    findElement("#intro-choose").hidden = true;
    findElement("#intro-files-view").hidden = false;
    window.scrollTo(0, 0);
  });
  findElement("#intro-back").addEventListener("click", () => { findElement("#intro-choose").hidden = false; findElement("#intro-files-view").hidden = true; });
  findElement("#intro-open").addEventListener("click", openFromSetup);
  findElement("#intro-continue").addEventListener("click", async () => {
    document.body.classList.remove("setup");
    if (!workbenchStarted) await startWorkbench();
  });
  findElement("#open-setup").addEventListener("click", showIntro);
}

/* ---------- Start ---------- */

// Get the editors and controls ready, then show the setup screen. Nothing runs until the student chooses.
async function boot() {
  hadSavedWork = restore();
  buildTerms();
  setupTips();
  setupPane("left");
  setupPane("right");
  bindControls();
  bindIntro();
  state.panes.left = browserFileList().includes(state.panes.left) ? state.panes.left : "index.html";
  state.panes.right = serverFileList().includes(state.panes.right) ? state.panes.right : defaultServerTab();
  reflectControls();
  showIntro();
}

// Start the server and load the first page, after the student has chosen a setup or asked to continue.
async function startWorkbench() {
  workbenchStarted = true;
  if (state.language === "py" && !engines.py) state.language = "ts";
  if (state.language === "py") {
    setBusy(true, "Python is loading. The first time, this downloads about 10 MB.");
    try { await engines.py.ready(); } catch (error) { state.language = "ts"; state.panes.right = defaultServerTab(); notice("right", String(error.message || error)); }
    setBusy(false);
  }
  await applyEverything("The workbench opens the first page.");
}

boot();

})();
