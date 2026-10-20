// A web worker runs a script on its own thread, so a slow job does not freeze
// the page. This worker loads Pyodide, which is Python compiled to run inside
// the browser, and then runs the real files from the vending machine project.

importScripts("https://cdn.jsdelivr.net/pyodide/v0.29.5/full/pyodide.js");

const HOME = "/home/pyodide";
let adapter = null;

async function start() {
  const pyodide = await loadPyodide();

  // sqlite3 is part of the Python standard library, and Pyodide loads it on request.
  await pyodide.loadPackage("sqlite3");

  // Copy our Python files into Pyodide's private, in-memory file system.
  for (const fileName of ["setup_db.py", "server.py", "adapter.py"]) {
    const text = await (await fetch("py/" + fileName)).text();
    pyodide.FS.writeFile(`${HOME}/${fileName}`, text);
  }

  // Run the real setup script, which creates vending.db in the memory file system.
  await pyodide.runPythonAsync(`
import os, runpy, sys
os.chdir("${HOME}")
sys.path.insert(0, "${HOME}")
runpy.run_path("${HOME}/setup_db.py", run_name="__main__")
`);

  adapter = pyodide.pyimport("adapter");
  postMessage({ type: "ready" });
}

onmessage = (event) => {
  const { id, method, path } = event.data;
  // answer() returns a Python tuple, and toJs() converts it to a JavaScript array.
  const [status, body] = adapter.answer(method, path).toJs();
  postMessage({ type: "reply", id, status, body });
};

start().catch((error) => postMessage({ type: "failed", message: String(error) }));
