// A small web server that sells snacks from a SQLite database.
//
// The file has four layers, from the bottom of the program to the top:
//   1. The data layer talks to the database. It knows nothing about HTTP.
//   2. The route layer connects URLs to data functions and checks the input.
//   3. The HTTP layer reads requests and writes responses.
//   4. The last lines start the server.

// Modules whose names start with "node:" are built into Node, so nothing needs installing.
import { readFileSync } from "node:fs";
import { createServer } from "node:http";
import type { IncomingMessage, ServerResponse } from "node:http";
import path from "node:path";
import { DatabaseSync } from "node:sqlite";

// The shape of one slot. It matches one row of the inventory table and the
// JSON that we send to the browser. A type exists only while we write and
// check the program. Node removes it before the program runs.
type Slot = {
  slot_id: string;
  item_name: string;
  price_cents: number;
  stock: number;
};

// --- Settings ----------------------------------------------------------------

// 127.0.0.1 means "this computer", so only programs on your own machine can connect.
const HOST = "127.0.0.1";

// The port decides which program on this computer receives the request.
const PORT = 8000;

// import.meta.dirname is the folder that holds this file, which is src,
// so ".." leads to the project folder above it.
const PROJECT_FOLDER = path.join(import.meta.dirname, "..");
const DATABASE_FILE = path.join(PROJECT_FOLDER, "vending.db");
const PUBLIC_FOLDER = path.join(PROJECT_FOLDER, "public");

// The only files that the server will send. Each URL path maps to a file name
// and a Content-Type. A fixed list stops visitors from asking for other files,
// such as server.ts or vending.db, by typing a path like /../src/server.ts.
const STATIC_FILES = new Map([
  ["/", { fileName: "index.html", contentType: "text/html; charset=utf-8" }],
  ["/style.css", { fileName: "style.css", contentType: "text/css; charset=utf-8" }],
  ["/app.js", { fileName: "app.js", contentType: "text/javascript; charset=utf-8" }],
]);

// A valid slot id is one capital letter followed by one digit, such as A1 or B2.
const SLOT_ID_PATTERN = /^[A-Z][0-9]$/;

// --- Errors ------------------------------------------------------------------
// The data layer reports problems by throwing these errors. Each name
// describes a problem in the language of the vending machine, and the HTTP
// layer decides which status code each problem deserves.

class BadRequest extends Error {}
class NoSuchSlot extends Error {}
class SoldOut extends Error {}

// --- Data layer --------------------------------------------------------------
// These functions are the only place where the program talks to the database.

// We open one connection for the whole program. Node runs our code on a single
// thread, so only one request touches the connection at a time. The Python
// edition opens a new connection for every request because its server uses
// several threads.
const database = new DatabaseSync(DATABASE_FILE);

// A prepared statement is SQL that the database has already read and checked.
// We prepare each statement once, when the server starts, and run it many
// times. If a table or column name were wrong, the error would appear here at
// startup and not on the first click. The ? is a placeholder for a value that
// travels separately from the SQL text, so a visitor can never change what the
// SQL means (SQL injection).
const selectAllSlots = database.prepare(
  "SELECT slot_id, item_name, price_cents, stock FROM inventory ORDER BY slot_id",
);
const selectOneSlot = database.prepare(
  "SELECT slot_id, item_name, price_cents, stock FROM inventory WHERE slot_id = ?",
);
// One statement checks the stock and changes it. If two buyers arrive at the
// same moment, the database handles them one after the other, so they cannot
// both take the last item.
const decrementStockIfAvailable = database.prepare(
  "UPDATE inventory SET stock = stock - 1 WHERE slot_id = ? AND stock > 0",
);

// Run some work as a transaction: all of it happens, or none of it does.
// The <T> means "whatever type the work returns", and the function returns the
// same type.
function runInTransaction<T>(work: () => T): T {
  database.exec("BEGIN");
  try {
    const result = work();
    database.exec("COMMIT");
    return result;
  } catch (error) {
    // Something went wrong, so undo every change made since BEGIN.
    database.exec("ROLLBACK");
    throw error;
  }
}

function getAllSlots(): Slot[] {
  // "as Slot[]" is a promise to the compiler. The compiler cannot see inside
  // the database, so it takes our word for the shape of the rows.
  return selectAllSlots.all() as Slot[];
}

function getSlot(slotId: string): Slot {
  const slot = selectOneSlot.get(slotId) as Slot | undefined;
  if (slot === undefined) {
    throw new NoSuchSlot(`No slot called ${slotId}.`);
  }
  return slot;
}

// Take one item from a slot and return the updated slot.
function buySlot(slotId: string): Slot {
  return runInTransaction(() => {
    const updateResult = decrementStockIfAvailable.run(slotId);

    // Read the slot inside the same transaction, so that the numbers we report
    // agree with the change we just made. This line throws NoSuchSlot when the
    // slot does not exist.
    const slot = getSlot(slotId);

    // "changes" is the number of rows that the UPDATE changed.
    if (updateResult.changes === 0) {
      throw new SoldOut(`${slot.item_name} is sold out.`);
    }
    return slot;
  });
}

// --- Route layer -------------------------------------------------------------
// A handler connects one URL to one data function. It checks the input, calls
// the data layer and returns data. It contains no SQL and no HTTP details.

// Tidy up a slot id from the URL and check that it has the right shape.
function validateSlotId(rawSlotId: string): string {
  // toUpperCase lets a visitor type a1 and mean A1.
  const slotId = rawSlotId.toUpperCase();
  if (!SLOT_ID_PATTERN.test(slotId)) {
    throw new BadRequest("Slot ids look like A1 or B2.");
  }
  return slotId;
}

function handleListSlots(): Slot[] {
  return getAllSlots();
}

function handleShowSlot(rawSlotId: string): Slot {
  return getSlot(validateSlotId(rawSlotId));
}

function handleBuySlot(rawSlotId: string): Slot {
  return buySlot(validateSlotId(rawSlotId));
}

// One row of the route table: an HTTP method, a pattern for the URL path, and
// the handler for that route.
type Route = {
  httpMethod: string;
  pathPattern: RegExp;
  handler: (...capturedText: string[]) => unknown;
};

// The route table is the API written as data. In a pattern, ([^/]+) captures
// the text between two slashes, and the captured text is passed to the
// handler as an argument.
const ROUTES: Route[] = [
  { httpMethod: "GET", pathPattern: /^\/api\/slots$/, handler: handleListSlots },
  { httpMethod: "GET", pathPattern: /^\/api\/slots\/([^/]+)$/, handler: handleShowSlot },
  { httpMethod: "POST", pathPattern: /^\/api\/slots\/([^/]+)\/buy$/, handler: handleBuySlot },
];

// --- HTTP layer --------------------------------------------------------------

function sendBody(
  response: ServerResponse,
  statusCode: number,
  contentType: string,
  body: string | Buffer,
): void {
  // HTTP requires this order: status line, headers, a blank line, body.
  // writeHead writes the status line and the headers, and end writes the body.
  response.writeHead(statusCode, {
    "Content-Type": contentType, // how to read the body
    // Content-Length counts bytes, and some characters take more than one
    // byte, so we measure the bytes and not the characters.
    "Content-Length": Buffer.byteLength(body),
    "Cache-Control": "no-store", // always ask again while we develop
  });
  response.end(body);
}

function sendJson(response: ServerResponse, statusCode: number, data: unknown): void {
  // JSON.stringify turns the data into text, and the network carries it as bytes.
  sendBody(response, statusCode, "application/json; charset=utf-8", JSON.stringify(data));
}

// Node calls this function once for every request that arrives.
function answerRequest(request: IncomingMessage, response: ServerResponse): void {
  // "??" means "use the value on the right if the one on the left is missing".
  const httpMethod = request.method ?? "GET";

  // request.url holds the path and any query string together. The URL class
  // takes them apart. It needs a base address for a path with no host.
  const urlPath = new URL(request.url ?? "/", `http://${HOST}:${PORT}`).pathname;

  // Print one log line when the response has been sent.
  response.on("finish", () => console.log(`${httpMethod} ${urlPath} ${response.statusCode}`));

  try {
    // First, is the visitor asking for one of our page files?
    const staticFile = STATIC_FILES.get(urlPath);
    if (httpMethod === "GET" && staticFile !== undefined) {
      const body = readFileSync(path.join(PUBLIC_FOLDER, staticFile.fileName));
      sendBody(response, 200, staticFile.contentType, body);
      return;
    }

    // Otherwise look for a matching route. The first match wins.
    for (const route of ROUTES) {
      const pathMatch = route.pathPattern.exec(urlPath);
      if (route.httpMethod === httpMethod && pathMatch !== null) {
        // slice(1) drops the whole match and keeps the captured text, such as "A1".
        sendJson(response, 200, route.handler(...pathMatch.slice(1)));
        return;
      }
    }

    // Nothing matched.
    sendJson(response, 404, { error: "No such route." });
  } catch (error) {
    // These lines turn the errors of the data layer into status codes.
    if (error instanceof BadRequest) {
      sendJson(response, 400, { error: error.message });
    } else if (error instanceof NoSuchSlot) {
      sendJson(response, 404, { error: error.message });
    } else if (error instanceof SoldOut) {
      sendJson(response, 409, { error: error.message });
    } else {
      // Anything else is a bug in our program. We print the details for the
      // developer and tell the visitor very little.
      console.error("Unexpected error:", error);
      sendJson(response, 500, { error: "Something went wrong on the server." });
    }
  }
}

// Create the server and tell it to call answerRequest for every request.
const webServer = createServer(answerRequest);

// Start listening on the host and port. The function runs once the server is ready.
webServer.listen(PORT, HOST, () => {
  console.log(`Vending machine running at http://${HOST}:${PORT}  (press Ctrl+C to stop)`);
});
