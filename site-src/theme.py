"""Theme tokens, the settings panel, and the page shell.

The colour tokens are read out of lib.CSS (light block and dark block), so
there is one source of truth. This module turns them into three rules:
the device's preference by default, and explicit light and dark overrides
that the settings panel switches with a data attribute on <html>.
"""

import re

import lib

SEGMENT_LIGHT = "--seg1: #cfe6f6;\n  --seg2: #f6e1be;\n  --seg3: #e2d3f3;\n  --seg4: #cdeed4;"
SEGMENT_DARK = "--seg1: #1f4560;\n  --seg2: #5a4219;\n  --seg3: #46316a;\n  --seg4: #1f5133;"

_TOKEN_BLOCKS = re.compile(
    r":root \{\n  color-scheme: light dark;\n(.*?)\n\}\n@media \(prefers-color-scheme: dark\) \{\n  :root \{\n(.*?)\n  \}\n\}",
    re.S,
)


_CACHE = {}


def _tokens():
    if "value" in _CACHE:
        return _CACHE["value"]
    match = _TOKEN_BLOCKS.search(lib.CSS)
    assert match, "token blocks not found in lib.CSS"
    light = match.group(1).strip() + "\n  " + SEGMENT_LIGHT
    dark = match.group(2).strip() + "\n  " + SEGMENT_DARK
    _CACHE["value"] = (match, light, dark)
    return _CACHE["value"]


def token_css():
    _, light, dark = _tokens()
    return f""":root {{
  color-scheme: light;
  {light}
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme: dark;
    {dark}
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  {dark}
}}"""


def standalone_token_css():
    """Tokens for a standalone SVG file, which follows the device's preference."""
    _, light, dark = _tokens()
    return f""":root {{
  {light}
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    {dark}
  }}
}}"""


SETTINGS_CSS = r"""
/* settings panel */
.settings { position: fixed; top: 12px; right: 12px; z-index: 50; font-size: 15px; }
.settings-toggle {
  display: inline-flex; align-items: center; gap: 8px; font: inherit; font-weight: 700;
  background: var(--surface); color: var(--text); border: 1px solid var(--line); border-radius: 999px;
  padding: 7px 14px; cursor: pointer; box-shadow: 0 1px 4px rgba(0, 0, 0, 0.12);
}
.settings-toggle:hover { border-color: var(--accent); }
.settings-toggle svg { width: 16px; height: 16px; }
.settings-panel {
  position: absolute; top: 46px; right: 0; width: min(320px, calc(100vw - 24px));
  background: var(--surface); color: var(--text); border: 1px solid var(--line); border-radius: 12px;
  padding: 14px 16px 12px; box-shadow: 0 8px 28px rgba(0, 0, 0, 0.22);
}
.settings-panel[hidden] { display: none; }
.settings-panel fieldset { border: none; padding: 0; margin: 0 0 12px; }
.settings-panel legend { font-weight: 700; font-size: 13px; letter-spacing: 0.04em; text-transform: uppercase; color: var(--muted); padding: 0; margin-bottom: 4px; }
.settings-panel label { display: block; padding: 3px 0; cursor: pointer; }
.settings-panel input { margin-right: 8px; accent-color: var(--accent); }
.settings-panel .reset { font: inherit; font-size: 14px; background: none; color: var(--accent); border: none; padding: 0; cursor: pointer; text-decoration: underline; }
a.svg-dl { white-space: nowrap; }

/* reading settings, applied by data attributes on the html element */
html[data-text="large"] body { font-size: 19.5px; }
html[data-text="large"] .why { font-size: 17.5px; }
html[data-text="large"] pre.code { font-size: 14.5px; }
html[data-text="large"] .chunk pre.code { font-size: 14px; }
html[data-wrap="off"] .chunk pre.code { white-space: pre; overflow-wrap: normal; }
html[data-motion="reduce"] { scroll-behavior: auto; }
html[data-motion="reduce"] *, html[data-motion="reduce"] *::before, html[data-motion="reduce"] *::after { transition: none !important; animation: none !important; }
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  * { transition: none !important; animation: none !important; }
}
@media (max-width: 1000px) { .settings-toggle span { display: none; } .settings-toggle { padding: 8px 10px; } }
"""

HEAD_SCRIPT = """<script>
(function () {
  try {
    var saved = JSON.parse(localStorage.getItem("tutorial-settings") || "{}");
    ["theme", "text", "wrap", "motion"].forEach(function (key) {
      if (saved[key]) document.documentElement.dataset[key] = saved[key];
    });
  } catch (error) { /* storage can be blocked, and the page works without it */ }
})();
</script>"""

SETTINGS_HTML = """<div class="settings">
<button type="button" class="settings-toggle" aria-expanded="false" aria-controls="settings-panel">
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/></svg>
<span>Settings</span></button>
<div id="settings-panel" class="settings-panel" role="group" aria-label="Reading settings" hidden>
<fieldset><legend>Theme</legend>
<label><input type="radio" name="theme" value="system"> Match my device</label>
<label><input type="radio" name="theme" value="light"> Light</label>
<label><input type="radio" name="theme" value="dark"> Dark</label></fieldset>
<fieldset><legend>Text size</legend>
<label><input type="radio" name="text" value="normal"> Normal</label>
<label><input type="radio" name="text" value="large"> Larger</label></fieldset>
<fieldset><legend>Long lines of code</legend>
<label><input type="radio" name="wrap" value="on"> Wrap onto the next line</label>
<label><input type="radio" name="wrap" value="off"> Keep on one line and scroll</label></fieldset>
<fieldset><legend>Motion</legend>
<label><input type="radio" name="motion" value="system"> Match my device</label>
<label><input type="radio" name="motion" value="reduce"> Reduce motion</label></fieldset>
<button type="button" class="reset" id="settings-reset">Reset to defaults</button>
</div></div>"""

SETTINGS_JS = r"""
(function () {
  const KEY = "tutorial-settings";
  const defaults = { theme: "system", text: "normal", wrap: "on", motion: "system" };
  const root = document.documentElement;
  const toggle = document.querySelector(".settings-toggle");
  const panel = document.getElementById("settings-panel");
  if (!toggle || !panel) return;

  function load() {
    try { return Object.assign({}, defaults, JSON.parse(localStorage.getItem(KEY) || "{}")); }
    catch (error) { return Object.assign({}, defaults); }
  }
  function save(settings) {
    try { localStorage.setItem(KEY, JSON.stringify(settings)); } catch (error) { /* ignore */ }
  }
  function apply(settings) {
    Object.keys(defaults).forEach((key) => {
      if (settings[key] === defaults[key]) delete root.dataset[key];
      else root.dataset[key] = settings[key];
    });
    Object.keys(defaults).forEach((key) => {
      const radio = panel.querySelector(`input[name="${key}"][value="${settings[key]}"]`);
      if (radio) radio.checked = true;
    });
  }

  let settings = load();
  apply(settings);

  panel.addEventListener("change", (event) => {
    const input = event.target;
    if (input.name in defaults) {
      settings[input.name] = input.value;
      apply(settings);
      save(settings);
    }
  });
  document.getElementById("settings-reset").addEventListener("click", () => {
    settings = Object.assign({}, defaults);
    apply(settings);
    save(settings);
  });

  function setOpen(open) {
    panel.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
  }
  toggle.addEventListener("click", () => setOpen(panel.hidden));
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) { setOpen(false); toggle.focus(); }
  });
  document.addEventListener("click", (event) => {
    if (!panel.hidden && !event.target.closest(".settings")) setOpen(false);
  });
})();
"""


def shell(title, description, nav_html, body, extra_head=""):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{lib.esc(title)}</title>
<meta name="description" content="{lib.esc(description)}">
{HEAD_SCRIPT}
<style>{lib.CSS}</style>
{extra_head}
</head>
<body>
{SETTINGS_HTML}
{body}
<script>{lib.JS}</script>
</body>
</html>
"""


def apply():
    """Rewrite lib.CSS and lib.JS in place, and replace lib.shell."""
    match, _, _ = _tokens()
    lib.CSS = lib.CSS[: match.start()] + token_css() + lib.CSS[match.end():] + SETTINGS_CSS
    lib.JS = lib.JS + SETTINGS_JS
    lib.shell = shell
