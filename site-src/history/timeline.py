"""Every date in the three histories, kept in one list.

Run this script to write:
- a timeline section near the end of each notes.html, between markers;
- two "Every date in this talk" slides before the recap slide of each deck;
and history.py builds a combined page, docs/history/timeline.html, from the same list.
Each entry: (year, label, part, story). Year can be a string such as "Late 1960s".
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORIES = {"web": "From the Browser", "server": "Behind the Page", "network": "Down the Wire"}
PARTS = {"html": ("HTML", "#E8955C"), "css": ("CSS", "#8DB4E2"), "scripts": ("Scripts", "#E9C46A"), "server": ("Server", "#8CC9A6"),
         "db": ("Database", "#B9A6E0"), "net": ("Network", "#7CC6C1"), "plugin": ("Plugins", "#C9D2E3")}

DATES = [
    # the browser's story
    (1991, "The first web page goes online at CERN", "html", "web"),
    (1995, "Forms become part of HTML 2.0", "html", "web"),
    (1995, "JavaScript arrives in the Netscape browser", "scripts", "web"),
    (1995, "PHP is first released", "server", "web"),
    (1996, "CSS level 1 becomes a standard", "css", "web"),
    (1996, "Flash appears as a browser plugin", "plugin", "web"),
    (1996, "Microsoft releases ASP", "server", "web"),
    (1998, "CSS level 2 adds positioning and :hover", "css", "web"),
    (2003, "WordPress is released", "server", "web"),
    (2004, "Gmail updates its inbox without reloading", "scripts", "web"),
    (2005, "Ajax is named, and Google Maps launches", "scripts", "web"),
    (2005, "Tim O'Reilly's essay defines Web 2.0", "server", "web"),
    (2006, "jQuery is released", "scripts", "web"),
    (2007, "The first iPhone arrives without Flash", "html", "web"),
    (2009, "Node.js runs JavaScript on the server", "scripts", "web"),
    (2010, "Responsive web design is named", "css", "web"),
    (2010, "AngularJS is released", "scripts", "web"),
    (2012, "TypeScript is released", "scripts", "web"),
    (2013, "React is released", "scripts", "web"),
    (2014, "HTML5 becomes a finished standard", "html", "web"),
    (2014, "Vue is released", "scripts", "web"),
    (2015, "Let's Encrypt gives away free certificates", "server", "web"),
    (2016, "Next.js renders React pages on the server", "server", "web"),
    (2017, "CSS Grid ships in every major browser", "css", "web"),
    (2017, "WebAssembly runs in every major browser", "scripts", "web"),
    (2018, "The GDPR begins to apply", "server", "web"),
    (2018, "Chrome marks plain HTTP pages “Not secure”", "server", "web"),
    (2019, "HTML becomes one living standard", "html", "web"),
    (2019, "CSS can follow the device's dark mode", "css", "web"),
    (2020, "Flash reaches its official end", "plugin", "web"),
    (2022, "Internet Explorer is retired", "html", "web"),
    (2022, "Browser makers begin Interop", "html", "web"),
    (2022, "ChatGPT launches", "scripts", "web"),
    (2023, ":has() and container queries work everywhere", "css", "web"),
    (2023, "OpenAI names its crawler, GPTBot", "server", "web"),
    (2024, "Google shows AI Overviews above search results", "server", "web"),
    (2024, "llms.txt is proposed", "server", "web"),
    (2025, "Cloudflare blocks AI crawlers by default", "server", "web"),
    (2025, "Buttons can open dialogs with commandfor", "html", "web"),
    # the server's and the database's story
    ("Late 1960s", "IBM's IMS stores data as trees", "db", "server"),
    (1970, "Codd describes the relational model", "db", "server"),
    (1974, "SEQUEL, later SQL, is described at IBM", "db", "server"),
    (1979, "The first commercial SQL database goes on sale", "db", "server"),
    (1986, "SQL becomes an official standard", "db", "server"),
    (1990, "The first web server runs at CERN", "server", "server"),
    (1993, "CGI lets a server run a program", "server", "server"),
    (1994, "Cookies let a server remember a browser", "server", "server"),
    (1995, "Apache, PHP and MySQL are released", "server", "server"),
    (1996, "PostgreSQL takes its name", "db", "server"),
    (1998, "LAMP is named", "server", "server"),
    (1998, "SQL injection is described", "db", "server"),
    (2000, "Fielding describes REST", "server", "server"),
    (2000, "SQLite is released", "db", "server"),
    (2003, "memcached caches answers in memory", "server", "server"),
    (2004, "Ruby on Rails is released", "server", "server"),
    (2005, "Django is released", "server", "server"),
    (2006, "Amazon S3 and EC2 rent storage and servers", "server", "server"),
    (2006, "Google describes Bigtable", "db", "server"),
    (2007, "Amazon describes Dynamo", "db", "server"),
    (2009, "NoSQL is named; MongoDB and Redis appear", "db", "server"),
    (2013, "Docker makes containers easy", "server", "server"),
    (2014, "Kubernetes and AWS Lambda arrive", "server", "server"),
    (2017, "The Equifax breach exposes about 147 million people", "server", "server"),
    (2020, "Retrieval-augmented generation is described", "db", "server"),
    (2021, "pgvector adds vector search to PostgreSQL", "db", "server"),
    # the network's story
    (1969, "ARPANET carries its first message, “LO”", "net", "network"),
    (1974, "Cerf and Kahn publish the design of TCP", "net", "network"),
    (1983, "ARPANET switches to TCP/IP on flag day", "net", "network"),
    (1983, "DNS turns names into addresses", "net", "network"),
    (1991, "HTTP/0.9: one line, one page", "net", "network"),
    (1994, "Netscape adds SSL encryption", "net", "network"),
    (1996, "HTTP/1.0 adds status codes and headers", "net", "network"),
    (1997, "HTTP/1.1 keeps connections open and adds Host", "net", "network"),
    (1997, "The first Wi-Fi standard, 802.11", "net", "network"),
    (1998, "The 56k modem standard is agreed", "net", "network"),
    (1998, "Akamai starts the first big CDN", "net", "network"),
    (1999, "802.11b and the group now called the Wi-Fi Alliance; TLS 1.0", "net", "network"),
    (2001, "The first 3G network opens, in Japan", "net", "network"),
    (2005, "YouTube launches", "net", "network"),
    (2008, "The iPhone 3G brings mobile data to a mass audience", "net", "network"),
    (2009, "The first 4G LTE networks open", "net", "network"),
    (2009, "Google starts SPDY, the ancestor of HTTP/2", "net", "network"),
    (2011, "WebSocket keeps a line open", "scripts", "network"),
    (2013, "Google starts testing QUIC", "net", "network"),
    (2015, "HTTP/2 becomes a standard", "net", "network"),
    (2018, "TLS 1.3 halves the handshake", "net", "network"),
    (2019, "The first 5G networks open; Wi-Fi 6 arrives", "net", "network"),
    (2019, "Lazy loading becomes an HTML attribute", "html", "network"),
    (2021, "QUIC becomes a standard", "net", "network"),
    (2022, "HTTP/3 becomes a standard", "net", "network"),
    (2024, "68 per cent of the world is online; 2.6 billion are not", "net", "network"),
]


def year_key(y):
    return 1968 if isinstance(y, str) else y


def entries(story):
    return sorted([d for d in DATES if d[3] == story], key=lambda d: year_key(d[0]))


def chip_html(part):
    name, colour = PARTS[part]
    return f'<span class="t" data-part="{part}" style="background:{colour}">{name}</span>'


def notes_block(story):
    rows = "".join(f"<tr><td>{y}</td><td>{label}</td><td>{chip_html(p)}</td></tr>" for y, label, p, _ in entries(story))
    return f"""<!-- timeline:start -->
<h2 id="timeline">Every date in this story</h2>
<p>All the dates in these notes, in order. Remember the opening section: each date marks when something appeared or became a standard, not when everyone used it.</p>
<table>
<tr><th>Year</th><th>What happened</th><th>Part</th></tr>
{rows}
</table>
<!-- timeline:end -->
"""


def slide(story, part_no, items, total_parts):
    NAVY = "#1B2A4A"
    cols = [items[i::3] for i in range(3)]
    cols = [items[: (len(items) + 2) // 3], items[(len(items) + 2) // 3: 2 * ((len(items) + 2) // 3)], items[2 * ((len(items) + 2) // 3):]]
    col_html = ""
    for col in cols:
        col_html += '<div style="display:flex;flex-direction:column;gap:12px">' + "".join(
            f'<div style="display:flex;gap:14px;align-items:baseline"><p style="font-size:24px;font-weight:700;color:{NAVY};min-width:96px">{y}</p>'
            f'<div style="width:14px;height:14px;border-radius:7px;background:{PARTS[p][1]};flex:none"></div>'
            f'<p style="font-size:24px;line-height:1.3;color:#3D4A63">{label}</p></div>'
            for y, label, p, _ in col) + '</div>'
    title = "Every date in this talk" + (f", part {part_no} of {total_parts}" if total_parts > 1 else "")
    legend = "".join(f'<div style="display:flex;gap:8px;align-items:center"><div style="width:14px;height:14px;border-radius:7px;background:{PARTS[k][1]}"></div><p style="font-size:22px;color:#5A6478">{PARTS[k][0]}</p></div>'
                     for k in sorted({p for _, _, p, _ in items}, key=list(PARTS).index))
    sid = f"dates-{part_no}"
    return sid, (f'<section id="{sid}" data-transition="fade" style="background:#F7F5F0;color:{NAVY};font-family:\'Public Sans\', Arial, sans-serif;padding:96px 112px;display:flex;flex-direction:column;gap:32px">'
                 '<div style="display:flex;flex-direction:column;gap:10px">'
                 f'<div style="display:flex;gap:24px;align-items:center;flex-wrap:wrap"><p style="font-size:24px;font-weight:700;color:#5A6478;letter-spacing:3px;text-transform:uppercase">Timeline</p>{legend}</div>'
                 f'<h2 style="font-family:\'Libre Baskerville\', Georgia, serif;font-size:56px;font-weight:700;line-height:1.1">{title}</h2></div>'
                 f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:40px">{col_html}</div>'
                 '<aside>Every date from the talk, in order. Use it to check the order of events, or ask the class to pick two dates and explain how one led to the other. Remember the adoption curves: each date marks a start, not the moment everyone switched.</aside></section>')


def update_deck(story):
    deck_dir = HERE / story / "deck"
    items = entries(story)
    half = (len(items) + 1) // 2
    chunks = [items] if len(items) <= 33 else [items[:half], items[half:]]
    for old in deck_dir.glob("slides/dates-*.html"):
        old.unlink()
    ids = []
    for n, chunk in enumerate(chunks, 1):
        sid, html = slide(story, n, chunk, len(chunks))
        (deck_dir / "slides" / f"{sid}.html").write_text(html + "\n")
        ids.append(sid)
    deck = json.loads((deck_dir / "deck.json").read_text())
    order = [s for s in deck["order"] if not s.startswith("dates-")]
    i = order.index("recap")
    deck["order"] = order[:i] + ids + order[i:]
    (deck_dir / "deck.json").write_text(json.dumps(deck, ensure_ascii=False))
    return ids


def update_notes(story):
    path = HERE / story / "notes.html"
    text = re.sub(r"<!-- timeline:start -->.*?<!-- timeline:end -->\n?", "", path.read_text(), flags=re.S)
    i = text.index('<h2 id="sources">')
    path.write_text(text[:i] + notes_block(story) + text[i:])


def combined_page():
    data = [{"year": str(y), "sort": year_key(y), "label": l, "part": p, "story": s} for y, l, p, s in DATES]
    data.sort(key=lambda d: d["sort"])
    parts = {k: {"name": v[0], "colour": v[1]} for k, v in PARTS.items()}
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Every date, Pages Through the Ages</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@700&family=Public+Sans:wght@400;700&display=swap">
<style>
:root {{ --bg: #f7f5f0; --fg: #1b2a4a; --muted: #4a5568; --card: #fffdf9; --line: #d9d3c7; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg: #131b2e; --fg: #f4f1ea; --muted: #c9d2e3; --card: #1b2a4a; --line: #33456b; }} }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--fg); font: 17px/1.55 "Public Sans", system-ui, sans-serif; }}
main {{ max-width: 900px; margin: 0 auto; padding: 40px 16px 80px; }}
h1 {{ font: 700 clamp(30px, 6vw, 44px)/1.1 "Libre Baskerville", Georgia, serif; margin: 0 0 10px; }}
.lede {{ color: var(--muted); max-width: 64ch; }}
a {{ color: inherit; text-underline-offset: 3px; }}
fieldset {{ border: 1px solid var(--line); border-radius: 12px; padding: 10px 14px; margin: 14px 0; }}
legend {{ font-weight: 700; padding: 0 6px; }}
.filters {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.filters button {{ font: 600 14px "Public Sans", sans-serif; border: 2px solid var(--line); background: var(--card); color: var(--fg); border-radius: 999px; padding: 5px 12px; cursor: pointer; }}
.filters button[aria-pressed="true"] {{ border-color: var(--fg); }}
.filters button[aria-pressed="false"] {{ opacity: .55; text-decoration: line-through; }}
.dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 6px; vertical-align: -1px; margin-right: 6px; }}
ol {{ list-style: none; padding: 0; margin: 20px 0 0; border-left: 3px solid var(--line); }}
li {{ display: grid; grid-template-columns: 7.5em 1fr; gap: 4px 14px; padding: 8px 0 8px 18px; position: relative; }}
li::before {{ content: ""; position: absolute; left: -9px; top: 15px; width: 15px; height: 15px; border-radius: 50%; background: var(--c); border: 2px solid var(--bg); }}
li .y {{ font-weight: 700; }}
li .s {{ grid-column: 2; font-size: 13px; color: var(--muted); }}
li[hidden] {{ display: none; }}
.count {{ color: var(--muted); font-size: 14px; }}
:focus-visible {{ outline: 3px solid #e9c46a; outline-offset: 2px; }}
@media (max-width: 520px) {{ li {{ grid-template-columns: 1fr; }} li .s {{ grid-column: 1; }} }}
</style>
</head>
<body>
<main>
<p><a href="index.html">All history pages</a></p>
<p style="text-transform:uppercase;letter-spacing:.12em;font-size:13px;font-weight:700;margin:0">Pages Through the Ages</p>
<h1>Every date on one line</h1>
<p class="lede">Every date from the three views of Pages Through the Ages, on one line of time. Each date marks when something appeared or became a standard, not when everyone used it, so read it alongside the adoption curves at the start of each history.</p>
<fieldset><legend>Show these histories</legend><div class="filters" id="f-story"></div></fieldset>
<fieldset><legend>Show these parts</legend><div class="filters" id="f-part"></div></fieldset>
<p class="count" id="count" aria-live="polite"></p>
<ol id="list"></ol>
</main>
<script>
(function () {{
  var DATA = {json.dumps(data, ensure_ascii=False)};
  var STORIES = {json.dumps(STORIES)};
  var PARTS = {json.dumps(parts)};
  var on = {{ story: {{}}, part: {{}} }};
  Object.keys(STORIES).forEach(function (k) {{ on.story[k] = true; }});
  Object.keys(PARTS).forEach(function (k) {{ on.part[k] = true; }});
  var list = document.getElementById("list");
  DATA.forEach(function (d) {{
    var li = document.createElement("li");
    li.dataset.story = d.story; li.dataset.part = d.part; li.style.setProperty("--c", PARTS[d.part].colour);
    li.innerHTML = '<span class="y"></span><span class="l"></span><span class="s"></span>';
    li.querySelector(".y").textContent = d.year;
    li.querySelector(".l").textContent = d.label;
    li.querySelector(".s").textContent = STORIES[d.story] + " · " + PARTS[d.part].name;
    list.appendChild(li);
  }});
  function filters(id, kind, names) {{
    var box = document.getElementById(id);
    Object.keys(names).forEach(function (k) {{
      var b = document.createElement("button"); b.type = "button"; b.setAttribute("aria-pressed", "true");
      b.innerHTML = (kind === "part" ? '<span class="dot" style="background:' + names[k].colour + '"></span>' : "") + (kind === "part" ? names[k].name : names[k]);
      b.addEventListener("click", function () {{ on[kind][k] = !on[kind][k]; b.setAttribute("aria-pressed", String(on[kind][k])); apply(); }});
      box.appendChild(b);
    }});
  }}
  function apply() {{
    var n = 0;
    Array.prototype.forEach.call(list.children, function (li) {{
      var show = on.story[li.dataset.story] && on.part[li.dataset.part]; li.hidden = !show; if (show) n++;
    }});
    document.getElementById("count").textContent = n + " of " + DATA.length + " dates shown";
  }}
  filters("f-story", "story", STORIES); filters("f-part", "part", PARTS); apply();
}})();
</script>
</body>
</html>
"""


def main():
    for story in STORIES:
        if (HERE / story / "notes.html").exists():
            update_notes(story)
            update_deck(story)
    print(len(DATES), "dates")


if __name__ == "__main__":
    main()
