"""Add the opening section on adoption curves to both history pieces.

Run once after changing anything here: it rewrites two slides per deck
(adoption-curve and messy), puts them after the plan slide in each deck.json,
and replaces the marked adoption section in each notes.html and site.html.

Sources for the numbers:
- Everett M. Rogers, Diffusion of Innovations (first published 1962): adopter categories
  2.5, 13.5, 34, 34 and 16 per cent.
- W3Techs historical surveys, 1 January of each year, 2015 to 2025:
  client-side languages, content management systems, and server-side programming languages.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
YEARS = list(range(2015, 2026))
ROGERS = [("Innovators", 2.5), ("Early adopters", 13.5), ("Early majority", 34), ("Late majority", 34), ("Laggards", 16)]
DATA = {
    "web": {
        "title": "Old and new overlap for years",
        "eyebrow": "2015 to 2025 · share of all websites",
        "series": [
            ("JavaScript in the page", "#7A5D00", [88.1, 92.1, 94.4, 94.9, 95.1, 95.0, 97.1, 97.8, 98.0, 98.8, 98.9]),
            ("WordPress", "#2E6B4A", [23.3, 25.6, 27.3, 29.2, 32.7, 35.4, 39.5, 43.2, 43.1, 43.1, 43.6]),
            ("Flash", "#5A6478", [12.1, 9.5, 7.3, 5.5, 4.0, 2.8, 2.2, 1.6, 1.5, 1.2, 1.0]),
        ],
        "ymax": 100,
        "points": [
            "<b>Overlap.</b> Flash officially ended in December 2020, and about 1 site in 100 still carried it in 2025.",
            "<b>Different speeds.</b> WordPress climbed for years, then levelled off at about 43 per cent of all sites.",
            "<b>Dependency.</b> Ajax was named in 2005, but it rested on a browser feature from 1999 and on faster connections.",
        ],
        "source": "Source: W3Techs surveys of the top ten million websites, 1 January each year.",
        "notes": "Use this slide to set expectations for the dates in the rest of the talk. A date on a slide marks when something appeared or became a standard, not when everyone used it. The three lines come from one survey, so they can be compared. Flash shows the long tail of a technology that has officially ended, WordPress shows a climb that stops, and JavaScript shows something close to universal.",
    },
    "server": {
        "title": "The old languages keep running",
        "eyebrow": "2015 to 2025 · share of websites whose server language is known",
        "series": [
            ("PHP", "#2E6B4A", [80.6, 80.0, 80.0, 80.2, 78.9, 78.9, 79.1, 78.1, 77.7, 76.7, 75.2]),
            ("ASP.NET", "#24588F", [16.7, 15.6, 14.8, 13.5, 11.8, 10.6, 9.3, 8.0, 7.4, 6.6, 5.4]),
            ("Ruby", "#A24A18", [0.9, 1.1, 1.3, 1.6, 2.4, 3.0, 4.3, 6.0, 5.3, 5.6, 6.2]),
            ("JavaScript (Node)", "#7A5D00", [0.1, 0.2, 0.3, 0.4, 0.7, 0.8, 1.2, 1.8, 2.3, 3.1, 4.0]),
        ],
        "ymax": 100,
        "points": [
            "<b>Overlap.</b> PHP is from 1995, and three sites in four still ran it in 2025.",
            "<b>Different speeds.</b> Node arrived in 2009 but reached 4 per cent of sites only in 2025.",
            "<b>Dependency.</b> A change of language means rewriting a working site, so servers change far more slowly than browsers.",
        ],
        "source": "Source: W3Techs surveys of the top ten million websites, 1 January each year.",
        "notes": "A date on a slide marks when something appeared, not when everyone used it, and on the server the gap is widest. Rewriting a working site is expensive, so old languages keep running for decades. The survey can only see the language on sites that reveal it, which is why the shares are of sites whose language is known.",
    },
}

NET_YEARS = list(range(1990, 2024))
DATA["network"] = {
    "title": "The curve has not reached the top",
    "eyebrow": "1990 to 2023 · share of the world’s people using the internet",
    "years": NET_YEARS,
    "every": 5,
    "series": [
        ("Internet users", "#1F6B66", [0.05, 0.08, 0.13, 0.18, 0.36, 0.68, 1.33, 2.04, 3.14, 4.63, 6.72, 8.02, 10.48, 12.16, 14.04,
                                       15.6, 17.3, 20.3, 22.8, 25.4, 28.5, 31.0, 33.5, 35.4, 37.5, 39.9, 42.9, 45.4, 48.6, 53.2, 59.3, 62.2, 64.4, 67.4]),
    ],
    "ymax": 100,
    "points": [
        "<b>A real S-curve.</b> Under 1 per cent of people were online in 1995, 16 per cent in 2005 and 67 per cent in 2023.",
        "<b>Not finished.</b> About 2.6 billion people were still offline in 2024, so the curve is still climbing.",
        "<b>Overlap.</b> HTTP/2 reached about half of all sites in 2021, then fell to about a third by 2025 as HTTP/3 took over, while older sites kept HTTP/1.1.",
    ],
    "source": "Sources: World Bank and ITU, internet users per 100 people; ITU Facts and Figures 2024; W3Techs, HTTP/2 and HTTP/3 usage.",
    "intro": "The share of the world’s people using the internet follows Rogers’ S-curve closely, and it has not reached the top.",
    "site_intro": "The share of the world’s people online follows the same S-curve, and it has not reached the top.",
    "notes": "This chart is the same S-curve as the slide before, drawn from real numbers. It rose slowly through the 1990s, steeply in the 2000s and 2010s, and is now flattening below the top. A protocol date on a later slide marks the start of a curve like this one, which for HTTP/2 rose and then fell back as HTTP/3 replaced it.",
}

NAVY, CREAM = "#1B2A4A", "#F7F5F0"


def rogers_svg(width, height, labels, stroke="#1B2A4A", fill="#B9A6E0", s_colour="#A24A18", text_colour="#1B2A4A"):
    """A bell curve split into Rogers' five groups, with the cumulative S-curve over it."""
    import math
    mu, sd = 0.0, 1.0
    xs = [-3 + 6 * i / 120 for i in range(121)]
    pdf = [math.exp(-0.5 * x * x) for x in xs]
    cdf = []
    total = 0
    for p in pdf:
        total += p
        cdf.append(total)
    cdf = [c / total for c in cdf]
    pad_l, pad_b, pad_t = (48 if labels else 8), (40 if labels else 8), 12
    w, h = width - pad_l - 8, height - pad_b - pad_t

    def X(x):
        return pad_l + (x + 3) / 6 * w

    def Y(v):
        return pad_t + h - v * h

    bounds = [-3, -2, -1, 0, 1, 3]  # Rogers' cuts at the mean minus 2, minus 1 standard deviations, the mean, plus 1
    shades = ["#E6DFF7", "#D3C6F0", "#B9A6E0", "#9C86D0", "#7E66BC"]
    out = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="A bell curve divided into innovators, early adopters, early majority, late majority and laggards, with an S-shaped curve of total adoption rising from 0 to 100 per cent" style="max-width:100%;height:auto">']
    for k in range(5):
        pts = [(x, p) for x, p in zip(xs, pdf) if bounds[k] - 1e-9 <= x <= bounds[k + 1] + 1e-9]
        d = f"M{X(pts[0][0]):.1f},{Y(0):.1f} " + " ".join(f"L{X(x):.1f},{Y(p * 0.9):.1f}" for x, p in pts) + f" L{X(pts[-1][0]):.1f},{Y(0):.1f} Z"
        out.append(f'<path d="{d}" fill="{shades[k]}" stroke="{stroke}" stroke-width="1.5"/>')
    s = "M" + " L".join(f"{X(x):.1f},{Y(c):.1f}" for x, c in zip(xs, cdf))
    out.append(f'<path d="{s}" fill="none" stroke="{s_colour}" stroke-width="4" stroke-linecap="round"/>')
    out.append(f'<line x1="{pad_l}" y1="{Y(0)}" x2="{pad_l + w}" y2="{Y(0)}" stroke="{stroke}" stroke-width="1.5"/>')
    if labels:
        out.append(f'<line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{Y(0)}" stroke="{stroke}" stroke-width="1"/>')
        for v, t in [(0, "0%"), (0.5, "50%"), (1, "100%")]:
            out.append(f'<text x="{pad_l - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="12" fill="{text_colour}">{t}</text>')
        for k, (name, pct) in enumerate(ROGERS):
            cx = X((bounds[k] + bounds[k + 1]) / 2 if k != 4 else 1.6)
            out.append(f'<text x="{cx:.1f}" y="{Y(0) + 16:.1f}" text-anchor="middle" font-size="12" fill="{text_colour}">{name}</text>')
            out.append(f'<text x="{cx:.1f}" y="{Y(0) + 31:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="{text_colour}">{pct:g}%</text>')
        out.append(f'<text x="{X(1.25):.1f}" y="{Y(0.78):.1f}" font-size="13" font-weight="700" fill="{s_colour}">total adopted so far</text>')
        out.append(f'<text x="{X(-2.9):.1f}" y="{Y(0.42):.1f}" font-size="13" fill="{text_colour}">new adopters</text><text x="{X(-2.9):.1f}" y="{Y(0.42) + 16:.1f}" font-size="13" fill="{text_colour}">in each period</text>')
    out.append("</svg>")
    return "".join(out)


def lines_svg(series, ymax, width, height, labels, axis="#1B2A4A", text_colour="#1B2A4A", grid="#D9D3C7", years=None, every=2):
    years = years or YEARS
    pad_l, pad_r, pad_t, pad_b = (44 if labels else 6), (150 if labels else 6), 10, (28 if labels else 6)
    w, h = width - pad_l - pad_r, height - pad_t - pad_b

    def X(i):
        return pad_l + i / (len(years) - 1) * w

    def Y(v):
        return pad_t + h - v / ymax * h

    out = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Line chart from {years[0]} to {years[-1]}" style="max-width:100%;height:auto">']
    for v in (0, 25, 50, 75, 100):
        out.append(f'<line x1="{pad_l}" y1="{Y(v):.1f}" x2="{pad_l + w}" y2="{Y(v):.1f}" stroke="{grid}" stroke-width="1"/>')
        if labels:
            out.append(f'<text x="{pad_l - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="12" fill="{text_colour}">{v}%</text>')
    if labels:
        for i, y in enumerate(years):
            if i % every == 0 or i == len(years) - 1:
                out.append(f'<text x="{X(i):.1f}" y="{pad_t + h + 18}" text-anchor="middle" font-size="12" fill="{text_colour}">{y}</text>')
    placed = []
    for name, colour, vals in series:
        pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
        out.append(f'<polyline points="{pts}" fill="none" stroke="{colour}" stroke-width="{3 if labels else 6}" stroke-linejoin="round" stroke-linecap="round"/>')
        out.append(f'<circle cx="{X(len(vals) - 1):.1f}" cy="{Y(vals[-1]):.1f}" r="{4 if labels else 9}" fill="{colour}"/>')
        if labels:
            ly = Y(vals[-1]) + 4
            while any(abs(ly - p) < 15 for p in placed):
                ly -= 15
            placed.append(ly)
            out.append(f'<text x="{X(len(vals) - 1) + 8:.1f}" y="{ly:.1f}" font-size="12" font-weight="700" fill="{colour}">{name} {vals[-1]:g}%</text>')
    out.append("</svg>")
    return "".join(out)


def chip(name, bg):
    return f'<p style="font-size:24px;font-weight:700;color:{NAVY};background:{bg};padding:6px 18px;border-radius:24px">{name}</p>'


def slide_curve(name):
    labels = "".join(
        f'<div style="display:flex;flex-direction:column;gap:4px;align-items:center"><p style="font-size:24px;font-weight:700;color:{NAVY};text-align:center">{n}</p><p style="font-size:24px;color:#3D4A63">{p:g}%</p></div>'
        for n, p in ROGERS)
    cols = "1fr 1fr 1fr 1fr 2fr"  # the same widths as the five shaded bands, which are cut at whole standard deviations
    return (f'<section id="adoption-curve" data-transition="fade" style="background:{CREAM};color:{NAVY};font-family:\'Public Sans\', Arial, sans-serif;padding:112px 128px;display:grid;grid-template-columns:1.25fr 1fr;gap:72px;align-items:center">'
            '<div style="display:flex;flex-direction:column;gap:20px">'
            f'{rogers_svg(980, 470, False)}'
            f'<div style="display:grid;grid-template-columns:{cols};gap:0;padding:0 0 0 8px">{labels}</div>'
            '<div style="display:flex;gap:24px;align-items:center"><div style="width:48px;height:8px;background:#A24A18;border-radius:4px"></div><p style="font-size:24px;color:#3D4A63">The S-curve: the total who have adopted so far</p></div>'
            '</div>'
            '<div style="display:flex;flex-direction:column;gap:28px">'
            '<p style="font-size:24px;font-weight:700;color:#5A6478;letter-spacing:3px;text-transform:uppercase">Before we start</p>'
            '<h2 style="font-family:\'Libre Baskerville\', Georgia, serif;font-size:64px;font-weight:700;line-height:1.1">How a new technology spreads</h2>'
            '<p style="font-size:28px;line-height:1.45;color:#3D4A63">In 1962 the sociologist Everett Rogers described how new ideas spread through a group of people. A few innovators try something first. Early adopters follow, then the majority, and last of all the laggards.</p>'
            '<p style="font-size:28px;line-height:1.45;color:#3D4A63">Plot the total who have adopted so far, and you get an S-curve: slow, then steep, then flat.</p>'
            '</div>'
            '<aside>Rogers set out these groups in Diffusion of Innovations, first published in 1962. The bell curve shows how many people adopt in each period. The S-curve adds them up. The percentages are idealised, and real technologies rarely follow the shape exactly, which the next slide shows. Every date in this talk marks a point near the start of a curve, not the moment everyone switched.</aside>'
            '</section>')


def slide_messy(name):
    d = DATA[name]
    legend = "".join(
        f'<div style="display:flex;gap:16px;align-items:center"><div style="width:40px;height:8px;background:{c};border-radius:4px"></div><p style="font-size:24px;color:{NAVY}"><b>{n}</b> {v[0]:g}% → {v[-1]:g}%</p></div>'
        for n, c, v in d["series"])
    points = "".join(f'<p style="font-size:26px;line-height:1.4;color:#3D4A63">{p}</p>' for p in d["points"])
    ys = d.get("years", YEARS)
    years = "".join(f'<p style="font-size:22px;color:#5A6478">{y}</p>' for y in (ys[::5] + [ys[-1]] if "years" in d else (2015, 2017, 2019, 2021, 2023, 2025)))
    return (f'<section id="messy" data-transition="fade" style="background:{CREAM};color:{NAVY};font-family:\'Public Sans\', Arial, sans-serif;padding:112px 128px;display:flex;flex-direction:column;gap:36px">'
            '<div style="display:flex;flex-direction:column;gap:12px">'
            f'<p style="font-size:24px;font-weight:700;color:#5A6478;letter-spacing:3px;text-transform:uppercase">{d["eyebrow"]}</p>'
            f'<h2 style="font-family:\'Libre Baskerville\', Georgia, serif;font-size:64px;font-weight:700;line-height:1.1">{d["title"]}</h2></div>'
            '<div style="display:grid;grid-template-columns:1.1fr 1fr;gap:64px;align-items:start">'
            '<div style="display:flex;flex-direction:column;gap:12px">'
            '<div style="display:flex;gap:16px">'
            '<div style="display:flex;flex-direction:column;justify-content:space-between;height:420px"><p style="font-size:22px;color:#5A6478">100%</p><p style="font-size:22px;color:#5A6478">50%</p><p style="font-size:22px;color:#5A6478">0%</p></div>'
            f'{lines_svg(d["series"], d["ymax"], 760, 420, False, years=d.get("years"))}</div>'
            f'<div style="display:flex;justify-content:space-between;padding:0 0 0 88px">{years}</div>'
            f'<div style="display:flex;flex-direction:column;gap:10px">{legend}</div></div>'
            f'<div style="display:flex;flex-direction:column;gap:24px">{points}<p style="font-size:22px;color:#5A6478">{d["source"]}</p></div>'
            '</div>'
            f'<aside>{d["notes"]}</aside></section>')


def update_deck(name):
    deck_dir = HERE / name / "deck"
    (deck_dir / "slides" / "adoption-curve.html").write_text(slide_curve(name) + "\n")
    (deck_dir / "slides" / "messy.html").write_text(slide_messy(name) + "\n")
    deck = json.loads((deck_dir / "deck.json").read_text())
    order = [s for s in deck["order"] if s not in ("adoption-curve", "messy")]
    i = order.index("timeline") + 1
    deck["order"] = order[:i] + ["adoption-curve", "messy"] + order[i:]
    deck["sections"]["s1a"] = {"description": "Before we start: how technologies spread, and why the dates are messy", "start": "adoption-curve"}
    deck["sections"] = dict(sorted(deck["sections"].items(), key=lambda kv: deck["order"].index(kv[1]["start"])))
    (deck_dir / "deck.json").write_text(json.dumps(deck, ensure_ascii=False))
    if name == "server":
        maker = (HERE / "server" / "make_deck.py").read_text()
        if "adoption" not in maker:
            maker = maker.replace('    print(len(order), "slides")', '    print(len(order), "slides")\n    import adoption  # the opening section on adoption curves\n    adoption.update_deck("server")')
            maker = maker.replace("import json\nfrom pathlib import Path", "import json\nimport sys\nfrom pathlib import Path\nsys.path.insert(0, str(Path(__file__).resolve().parent.parent))")
            (HERE / "server" / "make_deck.py").write_text(maker)


def table_html(series, years=None, every=2):
    years = years or YEARS
    head = "<tr><th>Year</th>" + "".join(f"<th>{n}</th>" for n, _, _ in series) + "</tr>"
    rows = "".join("<tr><td>" + str(y) + "</td>" + "".join(f"<td>{v[i]:g}%</td>" for _, _, v in series) + "</tr>" for i, y in enumerate(years) if i % every == 0 or i == len(years) - 1)
    return f"<details><summary>The numbers behind the chart</summary><table>{head}{rows}</table></details>"


def notes_section(name):
    d = DATA[name]
    return f"""<!-- adoption:start -->
<h2 id="before">Before we start: history is messy</h2>
<p>The dates in these notes mark when something appeared or became a standard. They do not mark when everyone used it. Every technology here spread at its own speed, overlapped with older ones for years, and depended on others that came before it.</p>

<h3>How a new technology spreads</h3>
<p>In 1962 the sociologist Everett Rogers described how new ideas spread through a group of people in his book <i>Diffusion of Innovations</i>. He sorted people into five groups by when they take up something new.</p>
<figure class="chart">{rogers_svg(720, 330, True, stroke="currentColor", text_colour="currentColor")}</figure>
<table>
<tr><th>Group</th><th>Share</th><th>Who they are</th></tr>
<tr><td>Innovators</td><td>2.5%</td><td>Try something while it is still rough and risky</td></tr>
<tr><td>Early adopters</td><td>13.5%</td><td>Take it up once it shows promise, and others watch them</td></tr>
<tr><td>Early majority</td><td>34%</td><td>Wait until it works reliably</td></tr>
<tr><td>Late majority</td><td>34%</td><td>Join once most people already use it</td></tr>
<tr><td>Laggards</td><td>16%</td><td>Switch last, often only when the old way stops working</td></tr>
</table>
<p>The bell curve shows how many people adopt in each period. Add them up, and the total so far follows an <b>S-curve</b>: slow at first, then steep, then flat. The percentages are idealised, and real technologies rarely follow the shape exactly.</p>

<h3>{d["title"]}</h3>
<p>{d.get("intro", "Real numbers show how untidy the picture is. The chart below uses one survey, W3Techs, which checks the top ten million websites, so the lines can be compared with each other.")}</p>
<figure class="chart">{lines_svg(d["series"], d["ymax"], 720, 300, True, axis="currentColor", text_colour="currentColor", grid="rgba(127,127,127,.3)", years=d.get("years"), every=d.get("every", 2))}</figure>
{table_html(d["series"], d.get("years"), d.get("every", 2))}
<ul>{"".join(f"<li>{p}</li>" for p in d["points"])}</ul>
<p class="cap">{d["source"]}</p>
<!-- adoption:end -->
"""


def site_section(name):
    d = DATA[name]
    return f"""<!-- adoption:start -->
<section class="era enow" id="prologue" data-era="now" data-who="Before we start" data-url="https://w3techs.com/" data-cmd="history --is messy">
<div class="wrap">
<h2>Before we start: history is messy</h2>
<p>The dates on this page mark when something appeared, not when everyone used it. In 1962 the sociologist Everett Rogers described how new ideas spread: a few innovators first, then early adopters, the majority, and last of all the laggards. Add them up and the total follows an S-curve, slow, then steep, then flat.</p>
<figure class="adopt-fig">{rogers_svg(720, 330, True, stroke="currentColor", text_colour="currentColor")}</figure>
<p>{d.get("site_intro", "Real technologies are untidier than the curve. This chart comes from one survey of the top ten million websites, so the lines can be compared.")}</p>
<figure class="adopt-fig">{lines_svg(d["series"], d["ymax"], 720, 300, True, axis="currentColor", text_colour="currentColor", grid="rgba(127,127,127,.3)", years=d.get("years"), every=d.get("every", 2))}</figure>
<ul>{"".join(f"<li>{p}</li>" for p in d["points"])}</ul>
<p class="muted">{d["source"]} Rogers, <i>Diffusion of Innovations</i> (1962).</p>
</div>
</section>
<!-- adoption:end -->
"""


def splice(text, block, before):
    text = re.sub(r"<!-- adoption:start -->.*?<!-- adoption:end -->\n?", "", text, flags=re.S)
    i = text.index(before)
    return text[:i] + block + text[i:]


def main():
    for name in ("web", "server", "network"):
        if not (HERE / name / "notes.html").exists():
            continue
        update_deck(name)
        notes = (HERE / name / "notes.html").read_text()
        (HERE / name / "notes.html").write_text(splice(notes, notes_section(name), '<h2 id="ch1">'))
        site = (HERE / name / "site.html").read_text()
        first = {"web": '<section class="era e1991"', "server": '<section class="era e1970"', "network": '<section class="era e1969"'}[name]
        site = splice(site, site_section(name), first)
        if ".adopt-fig" not in site:
            site = site.replace("</style>", ".adopt-fig { margin: 18px 0; color: var(--fg); }\n.adopt-fig svg { display: block; width: 100%; height: auto; }\n</style>", 1)
        if '<option value="prologue">' not in site:
            site = site.replace('<select id="jump">\n', '<select id="jump">\n    <option value="prologue">Before we start · History is messy</option>\n', 1)
        (HERE / name / "site.html").write_text(site)
    print("adoption section written")


if __name__ == "__main__":
    main()
