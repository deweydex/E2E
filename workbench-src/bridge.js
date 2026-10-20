// Injected into the preview frame before the student's own scripts run.
// It replaces fetch so that requests go to the workbench instead of the network,
// and it reports clicks, link navigation, changes to the page and errors.
//
// The workbench replaces the two @@ markers below with this page's address values and its document number
// before it puts the script into the frame.
(function () {
  var ADDRESS_QUERY = "@@QUERY@@";
  var DOCUMENT_NUMBER = @@DOC@@;
  window.pageQuery = ADDRESS_QUERY;

  // Every message carries the document number, so the workbench can ignore messages from a page it has already replaced.
  var send = function (message) { message.__wb = true; message.doc = DOCUMENT_NUMBER; parent.postMessage(message, "*"); };

  // A request waits here until the workbench sends the server's answer back.
  var pendingReplies = {};
  var lastRequestId = 0;

  window.fetch = function (url, options) {
    options = options || {};
    return new Promise(function (resolve, reject) {
      lastRequestId += 1;
      pendingReplies[lastRequestId] = { resolve: resolve, reject: reject };
      send({
        type: "fetch",
        id: lastRequestId,
        method: String(options.method || "GET").toUpperCase(),
        url: String(url),
        body: typeof options.body === "string" ? options.body : null,
      });
    });
  };

  window.addEventListener("message", function (event) {
    var data = event.data;
    if (!data || !data.__wb) { return; }
    if (data.type === "reply" && pendingReplies[data.id]) {
      var waiting = pendingReplies[data.id];
      delete pendingReplies[data.id];
      waiting.resolve(new Response(data.bodyText, { status: data.status, headers: { "Content-Type": "application/json" } }));
    }
    // A changed stylesheet replaces the text of its <style> element, so the page restyles without reloading.
    if (data.type === "css") {
      var style = document.querySelector('style[data-file="' + data.name + '"]');
      if (style) { style.textContent = data.text; }
    }
  });

  // A short description of an element for the timeline, such as <button> “Buy”.
  function labelFor(element) {
    var text = (element.textContent || element.value || "").trim().replace(/\s+/g, " ").slice(0, 30);
    var tag = element.tagName.toLowerCase();
    return text ? "<" + tag + "> “" + text + "”" : "<" + tag + ">";
  }

  // Link clicks to pages in the project become navigation inside the workbench. Button clicks are reported as clicks.
  document.addEventListener("click", function (event) {
    var link = event.target.closest && event.target.closest("a");
    if (link && link.getAttribute("href") && !/^(https?:|mailto:|#)/.test(link.getAttribute("href"))) {
      event.preventDefault();
      send({ type: "navigate", href: link.getAttribute("href"), label: labelFor(link) });
      return;
    }
    var target = event.target.closest && event.target.closest("button, a, input[type=submit]");
    if (target) { send({ type: "click", label: labelFor(target) }); }
  }, true);

  document.addEventListener("submit", function () {
    send({ type: "click", label: "a form being sent", viaSubmit: true });
  }, true);

  // A form that nothing handled would reload the page. Say so, and stop it.
  window.addEventListener("submit", function (event) {
    if (!event.defaultPrevented) {
      event.preventDefault();
      send({ type: "error", message: "A form was sent, but no script handled it. Add data-post to the form, or write a script that handles the submit event." });
    }
  });

  // Report what changed on the page, once the changes have stopped for a moment.
  var changedElements = [];
  var settleTimer = null;
  // A short name for an element, such as section#list or article.slot, to say where a change happened.
  function shortName(element) {
    var name = element.tagName.toLowerCase();
    if (element.id) { name += "#" + element.id; }
    else if (element.classList && element.classList.length) { name += "." + element.classList[0]; }
    return name;
  }
  var observer = new MutationObserver(function (records) {
    // Each record describes one change. We keep the changed element and the parent that contains it.
    records.forEach(function (record) {
      record.addedNodes.forEach(function (node) {
        if (node.nodeType === 1 && node.tagName !== "SCRIPT" && node.tagName !== "STYLE") { changedElements.push({ node: node, parent: record.target }); }
        if (node.nodeType === 3 && record.target.nodeType === 1) { changedElements.push({ node: record.target, parent: record.target, changed: true }); }
      });
      if (record.type === "characterData" || record.type === "attributes") {
        if (record.target.nodeType === 1 && record.attributeName !== "data-wb-flash") { changedElements.push({ node: record.target, parent: record.target, changed: true }); }
      }
    });
    clearTimeout(settleTimer);
    settleTimer = setTimeout(function () {
      if (!changedElements.length) { return; }
      // Count the changes by parent and flash each parent briefly, so the student can see where the page changed.
      var parents = {};
      changedElements.forEach(function (entry) {
        var target = entry.parent.nodeType === 1 ? entry.parent : document.body;
        var key = shortName(target);
        parents[key] = (parents[key] || 0) + 1;
        if (target.setAttribute) { target.setAttribute("data-wb-flash", ""); setTimeout(function () { target.removeAttribute("data-wb-flash"); }, 900); }
      });
      var summary = Object.keys(parents).slice(0, 3).map(function (key) { return parents[key] + (parents[key] === 1 ? " element" : " elements") + " in <" + key + ">"; }).join(", ");
      send({ type: "dom", count: changedElements.length, summary: summary });
      changedElements = [];
    }, 120);
  });
  // Start watching once the page has been built, so the first drawing of the page is not reported as a change.
  function startWatching() {
    observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true, attributes: true });
  }
  if (document.readyState === "loading") { document.addEventListener("DOMContentLoaded", startWatching); } else { startWatching(); }

  window.addEventListener("error", function (event) { send({ type: "error", message: event.message }); });
  window.addEventListener("unhandledrejection", function (event) { send({ type: "error", message: String(event.reason) }); });
})();
