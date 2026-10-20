// Runs in the demo page. It connects three things: the page's own script,
// the service worker that intercepts its requests, and the Python worker.

const banner = document.getElementById("sim-banner");

function setBanner(text, failed = false) {
  banner.textContent = text;
  banner.classList.toggle("failed", failed);
}

async function startDemo() {
  if (!("serviceWorker" in navigator)) {
    throw new Error("This browser has no service workers.");
  }
  if (location.protocol === "file:") {
    throw new Error("Open this page through a web server (http), not from a file.");
  }

  setBanner(banner.dataset.starting);

  // Start the Python worker. It tells us when the database is ready.
  const worker = new Worker("worker.js");
  const pending = new Map();
  let nextId = 0;

  const pythonReady = new Promise((resolve, reject) => {
    worker.onmessage = (event) => {
      const message = event.data;
      if (message.type === "ready") resolve();
      else if (message.type === "failed") reject(new Error(message.message));
      else if (message.type === "reply") pending.get(message.id)(message);
    };
  });

  // Register the service worker and wait until it controls this page.
  await navigator.serviceWorker.register("sw.js");
  await navigator.serviceWorker.ready;
  if (!navigator.serviceWorker.controller) {
    await new Promise((resolve) => navigator.serviceWorker.addEventListener("controllerchange", resolve, { once: true }));
  }

  // The service worker sends us each API request. We pass it to Python and send the reply back.
  navigator.serviceWorker.addEventListener("message", (event) => {
    const id = nextId++;
    pending.set(id, (reply) => event.ports[0].postMessage({ ...reply, servedBy: banner.dataset.servedBy }));
    worker.postMessage({ id, method: event.data.method, path: event.data.path });
  });

  await pythonReady;

  // Now start the page's own script, exactly as the real project ships it.
  const script = document.createElement("script");
  script.type = "module";
  script.src = "app.js";
  document.body.append(script);
  setBanner(banner.dataset.ready);
}

startDemo().catch((error) => setBanner("The demo could not start: " + error.message, true));
