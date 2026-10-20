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
