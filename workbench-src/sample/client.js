// client.js is the only JavaScript in these pages. It reads data- attributes in the HTML,
// asks the server for data, and fills the page in. You can build a whole page with
// HTML and CSS alone, because this file does the JavaScript part for you.
//
//   data-get="/api/slots"        Fetch this address when the page loads and show the answer inside this element.
//   <template>                   Put the markup to repeat for every row inside the element. The markup needs one outer element.
//   data-one                     The answer is a list, but show only its first row.
//   data-field="item_name"       Put the value of this column into the text of this element.
//   data-format="euros"          Show a number of cents as euros.
//   data-href="item.html?slot={slot_id}"   Build a link from the values of the row.
//   data-post="/api/slots/{slot_id}/buy"   Send a POST request when this button is clicked or this form is sent.
//   data-success="Enjoy."        Set the message to show when the server answers OK.
//   data-message                 Mark the element that shows messages.
//
// After a POST succeeds, the script fetches every data-get address on the page again, so the page shows the new data.
// The script gives each row it builds the attribute data-generated, so that it can find and replace those rows later.
//
// In a text such as {slot_id}, the braces take a value from the row. In {query.slot} they
// take a value from the address of the page, such as item.html?slot=A1.

// The values after the question mark in the page's address, such as { slot: "A1" } for item.html?slot=A1.
// The workbench supplies window.pageQuery because its pages do not have separate addresses.
// On a real website you would read window.location.search instead.
const addressValues = Object.fromEntries(new URLSearchParams(window.pageQuery || window.location.search));

// Replace every {name} or {query.name} in a text with a value, made safe for use in an address.
function fillIn(text, row) {
  return text.replace(/\{(query\.)?(\w+)\}/g, (_wholeMatch, queryPrefix, name) => {
    const source = queryPrefix ? addressValues : row;
    return encodeURIComponent(source[name] ?? "");
  });
}

// Turn a number of cents into text such as €1.75.
function formatValue(value, format) {
  if (format === "euros") {
    return "€" + (Number(value) / 100).toFixed(2);
  }
  return value;
}

// Show a message to the visitor, in the nearest element marked data-message.
function showMessage(text, isError) {
  const messageBox = document.querySelector("[data-message]");
  if (!messageBox) {
    return;
  }
  messageBox.textContent = text;
  messageBox.dataset.kind = isError ? "error" : "ok";
}

// Fetch the data for one section and rebuild its rows.
async function loadSection(section) {
  // A section has no row yet, so its address can use {query.name} but not {column}.
  const response = await fetch(fillIn(section.dataset.get, {}));
  const answer = await response.json();
  if (!response.ok) {
    showMessage(answer.error, true);
    return;
  }

  let rows = Array.isArray(answer) ? answer : [answer];
  if (section.hasAttribute("data-one")) {
    rows = rows.slice(0, 1);
  }

  const template = section.querySelector("template");
  section.querySelectorAll("[data-generated]").forEach((oldRow) => oldRow.remove());

  for (const row of rows) {
    const rowElement = template.content.firstElementChild.cloneNode(true);
    rowElement.dataset.generated = "";

    // Every column also becomes a data- attribute, so CSS can write rules such as [data-stock="0"].
    for (const [column, value] of Object.entries(row)) {
      rowElement.dataset[column] = value;
    }
    rowElement.querySelectorAll("[data-field]").forEach((element) => {
      element.textContent = formatValue(row[element.dataset.field], element.dataset.format);
    });
    rowElement.querySelectorAll("[data-href]").forEach((link) => {
      link.setAttribute("href", fillIn(link.dataset.href, row));
    });
    section.append(rowElement);
  }
}

// Send a POST request for a button or a form, then refresh every section on the page.
async function sendPost(element, body) {
  // A button inside a generated row can use that row's columns in its address, such as {slot_id}.
  const row = element.closest("[data-generated]")?.dataset ?? {};
  const response = await fetch(fillIn(element.dataset.post, row), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const answer = await response.json();
  showMessage(response.ok ? element.dataset.success || "Done." : answer.error, !response.ok);
  if (response.ok) {
    document.querySelectorAll("[data-get]").forEach(loadSection);
  }
}

// One listener on the whole document handles every button, including buttons added later.
document.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-post]");
  if (button) {
    sendPost(button, {});
  }
});

// A form sends its fields as JSON. Numbers in the fields are converted from text to numbers.
document.addEventListener("submit", (event) => {
  const form = event.target.closest("form[data-post]");
  if (!form) {
    return;
  }
  event.preventDefault();
  const body = {};
  for (const [name, value] of new FormData(form)) {
    body[name] = value !== "" && !Number.isNaN(Number(value)) ? Number(value) : value;
  }
  sendPost(form, body);
});

document.querySelectorAll("[data-get]").forEach(loadSection);
