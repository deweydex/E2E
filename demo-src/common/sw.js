// A service worker sits between a page and the network. It sees every request
// that the page makes, and it may answer a request itself instead of sending
// it anywhere. Here it answers the requests that start with /api/.

// Take control of the page straight away, so the first visit works too.
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  const isApiRequest = url.origin === self.location.origin && url.pathname.startsWith("/api/");
  if (!isApiRequest) {
    return; // anything else goes to the network as usual
  }
  event.respondWith(answerFromPython(event));
});

async function answerFromPython(event) {
  const page = await self.clients.get(event.clientId);
  if (page === undefined) {
    return new Response(JSON.stringify({ error: "The demo page is not available." }), { status: 503 });
  }

  const url = new URL(event.request.url);

  // Ask the page to pass the request on to the Python worker, and wait for the reply.
  const reply = await new Promise((resolve) => {
    const channel = new MessageChannel();
    channel.port1.onmessage = (message) => resolve(message.data);
    page.postMessage({ method: event.request.method, path: url.pathname + url.search }, [channel.port2]);
  });

  return new Response(reply.body, {
    status: reply.status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "X-Served-By": reply.servedBy || "a simulated server in this browser",
    },
  });
}
