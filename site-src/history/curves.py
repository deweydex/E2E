"""An adoption chart at the end of every chapter, on one shared time axis, 1995 to 2026.

Run this script after the decks, notes and pages exist. It writes:
- a slide called curve-chN after the last slide of each chapter in each deck;
- a short section at the end of each chapter in each notes.html (between markers);
- a card at the end of the matching band of each era page (between markers).
Every series below names its source. Where no series covers a whole span, the line starts
and stops where the data does.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

HERE = Path(__file__).resolve().parent
X0, X1 = 1995, 2026
NAVY, CREAM = "#1B2A4A", "#F7F5F0"

WB = [(1995, 0.68), (1996, 1.33), (1997, 2.04), (1998, 3.14), (1999, 4.63), (2000, 6.72), (2001, 8.02), (2002, 10.48), (2003, 12.16), (2004, 14.04),
      (2005, 15.6), (2006, 17.3), (2007, 20.3), (2008, 22.8), (2009, 25.4), (2010, 28.5), (2011, 31.0), (2012, 33.5), (2013, 35.4), (2014, 37.5),
      (2015, 39.9), (2016, 42.9), (2017, 45.4), (2018, 48.6), (2019, 53.2), (2020, 59.3), (2021, 62.2), (2022, 64.4), (2023, 67.4), (2024, 68.0)]
import adoption as A

YRS = A.YEARS  # 2015 to 2025, W3Techs on 1 January each year


def annual(story, name):
    for n, _, vals in A.DATA[story]["series"]:
        if n == name:
            return list(zip(YRS, vals))
    raise KeyError(name)


SERIES = {
    "world_online": ("People online, world", "#1F6B66", WB, "World Bank and ITU"),
    "us_online": ("US adults online", "#24588F", [(2000, 52), (2002, 59), (2004, 63), (2006, 71), (2008, 74), (2010, 76), (2012, 83), (2014, 84), (2016, 88), (2018, 89), (2019, 90), (2021, 93), (2023, 95), (2024, 96), (2026, 97)], "Pew Research Center"),
    "us_broadband": ("US adults with home broadband", "#2E6B4A", [(2000, 1), (2001, 6), (2002, 9), (2003, 15), (2004, 24), (2005, 29), (2006, 41), (2007, 51), (2009, 62), (2010, 61), (2012, 67), (2013, 70), (2015, 66), (2016, 70), (2018, 65), (2019, 73), (2021, 77), (2023, 80), (2024, 79), (2026, 78)], "Pew Research Center"),
    "world_fixed_bb": ("Fixed broadband lines per 100 people, world", "#7A5D00", [(2001, 0.84), (2003, 1.98), (2005, 3.66), (2007, 5.37), (2009, 7.10), (2011, 8.99), (2013, 9.78), (2015, 11.52), (2017, 13.76), (2019, 14.89), (2020, 15.89)], "ITU, via World Bank"),
    "world_mobile": ("Mobile subscriptions per 100 people, world", "#A24A18", [(1995, 1.6), (1997, 3.7), (1999, 8.1), (2001, 15.5), (2003, 22.2), (2005, 33.8), (2007, 50.3), (2009, 67.5), (2011, 83.7), (2013, 92.5), (2015, 97.4), (2017, 102.9), (2019, 106.6), (2020, 106.2)], "ITU, via World Bank"),
    "us_smartphone": ("US adults with a smartphone", "#A24A18", A.PEW_SMART + [(2026, 91)], "Pew Research Center"),
    "mobile_traffic": ("Web visits made on a phone, world", "#5B3F9E", [(2010, 3), (2017, 50), (2024, 61), (2025, 58.5)], "StatCounter, via Statista"),
    "netscape": ("Netscape's share of browsers", "#24588F", [(1997, 76), (2000, 19)], "US Department of Justice trial exhibit"),
    "ie": ("Internet Explorer's share of browsers", "#A24A18", [(1997, 20), (2000, 69)], "US Department of Justice trial exhibit"),
    "apache": ("Sites served by Apache", "#2E6B4A", [(1996, 41), (2005, 70.3), (2010, 52.3)], "Netcraft web server surveys"),
    "php": ("Sites running PHP (of those with a known language)", "#2E6B4A", annual("server", "PHP"), "W3Techs"),
    "aspnet": ("Sites running ASP.NET", "#24588F", annual("server", "ASP.NET"), "W3Techs"),
    "ruby": ("Sites running Ruby", "#A24A18", annual("server", "Ruby"), "W3Techs"),
    "node": ("Sites running JavaScript on the server", "#7A5D00", annual("server", "JavaScript (Node)"), "W3Techs"),
    "js": ("Sites using JavaScript in the page", "#7A5D00", annual("web", "JavaScript in the page"), "W3Techs"),
    "flash": ("Sites using Flash", "#5A6478", annual("web", "Flash"), "W3Techs"),
    "wordpress": ("Sites using WordPress", "#5B3F9E", annual("web", "WordPress"), "W3Techs"),
    "https": ("Sites sending visitors to HTTPS", "#2E6B4A", A.HTTPS, "W3Techs"),
    "http2": ("Sites using HTTP/2", "#24588F", A.H2, "W3Techs"),
    "http3": ("Sites using HTTP/3", "#7A5D00", A.H3, "W3Techs"),
    "flexbox": ("Pages using Flexbox", "#24588F", A.FLEX, "HTTP Archive, Web Almanac"),
    "grid": ("Pages using Grid", "#8DB4E2", A.GRID, "HTTP Archive, Web Almanac"),
    "typescript": ("Developers using TypeScript", "#7A5D00", A.TS, "Stack Overflow developer surveys"),
    "chatgpt": ("US adults who have used ChatGPT", "#A24A18", [(2023, 18), (2024, 23), (2025, 34), (2026, 44)], "Pew Research Center"),
}

# story -> chapter number -> (series keys, what to notice)
CHAPTERS = {
    "web": {
        1: (["world_online", "us_online"], "In 1995 fewer than 1 person in 100 worldwide was online. The first pages were written for a tiny audience that grew every year."),
        2: (["netscape", "ie", "js", "php"], "Netscape lost three-quarters of its share in three years. The scripts and server languages of this chapter took far longer to become near-universal, and the survey data that shows it starts only in 2015."),
        3: (["us_broadband", "us_smartphone", "mobile_traffic", "wordpress"], "Broadband reached half of US adults by 2007. Smartphones went from a third to nine in ten in about a decade, and by 2017 half of all web visits came from a phone."),
        4: (["js", "node", "typescript"], "JavaScript in the page was already near 100 per cent. On the server, and as TypeScript, it rose slowly over years."),
        5: (["https", "flexbox", "grid", "flash"], "HTTPS and Flexbox climbed fast once browsers supported them. Grid, everywhere from 2017, was on only 12 per cent of pages by 2022, and Flash faded slowly for a decade."),
        6: (["chatgpt", "us_smartphone"], "Use of ChatGPT more than doubled between 2023 and 2026. It is still early on its curve, where smartphones were around 2011."),
        7: (["world_online", "us_smartphone", "https", "chatgpt"], "Four curves from four chapters on one axis: each started at a different time and climbed at its own speed."),
    },
    "server": {
        1: (["world_online"], "Databases are older than the web, but the people who would use websites built on them were still arriving: under 1 in 100 people was online in 1995."),
        2: (["apache", "world_online"], "Apache served 41 per cent of sites by the end of 1996 and 70 per cent by 2005, as the audience grew from a few million to over a billion people."),
        3: (["php", "aspnet", "wordpress"], "PHP still ran about three sites in four in 2025, thirty years after its release. WordPress rose to about 43 per cent of all sites, then levelled off."),
        4: (["ruby", "node", "typescript"], "The frameworks and languages of this chapter grew for years without ever coming close to PHP's share."),
        5: (["https", "us_smartphone", "world_mobile"], "Servers had to serve phones as well as computers, and HTTPS went from a quarter of sites to nearly nine in ten in seven years."),
        6: (["chatgpt"], "AI assistants spread quickly, but in 2026 fewer than half of US adults had used one."),
        7: (["php", "node", "wordpress", "https"], "The server changes slowly: old tools keep running while new ones grow alongside them."),
    },
    "network": {
        1: (["world_online"], "When the web began, the network built in chapter 1 reached under 1 per cent of the world. The climb took thirty years."),
        2: (["us_online", "us_broadband"], "In 2000 half of US adults were online, but only 1 in 100 had broadband: almost everyone else was dialling in."),
        3: (["us_broadband", "world_fixed_bb"], "Broadband reached half of US adults by 2007, while worldwide there were still only about 5 fixed broadband lines per 100 people."),
        4: (["world_mobile", "us_smartphone", "mobile_traffic"], "Mobile subscriptions passed one per person worldwide by 2016, and phones overtook computers for web visits in about 2017."),
        5: (["https", "http2", "http3"], "HTTP/2 rose to half of sites and then fell back as HTTP/3 replaced it, while HTTPS kept climbing."),
        6: (["world_online", "world_fixed_bb", "world_mobile"], "Mobile reached the world far faster than wires did, but in 2024 about a third of people were still offline."),
        7: (["world_online", "us_broadband", "us_smartphone", "http3"], "Every layer of the network spread at its own speed, and each new layer was built on top of the last."),
    },
}

PAGE_BANDS = {
    "web": {1: "y1994", 2: "y2003", 3: "y2013", 4: "y2016", 5: "y2019", 6: "y2023", 7: "now"},
    "server": {1: "y1970", 2: "y1993", 3: "y1999", 4: "y2005", 5: "y2014", 6: "y2023", 7: "now"},
    "network": {1: "y1969", 2: "y1996", 3: "y2004", 4: "y2010", 5: "y2016", 6: "y2023", 7: "now"},
}


def ymax(keys):
    top = max(v for k in keys for _, v in SERIES[k][2])
    return 110 if top > 100 else 100


PALETTE = ["#24588F", "#A24A18", "#2E6B4A", "#5B3F9E"]


def colour(keys, k):
    return PALETTE[keys.index(k) % len(PALETTE)]


SLIDE_PAD = 8


def svg(keys, width, height, labels, text_colour=NAVY, grid="#D9D3C7"):
    top = ymax(keys)
    pad_l, pad_r, pad_t, pad_b = (44 if labels else SLIDE_PAD), (24 if labels else SLIDE_PAD), 10, (26 if labels else SLIDE_PAD)
    w, h = width - pad_l - pad_r, height - pad_t - pad_b

    def X(y):
        return pad_l + (y - X0) / (X1 - X0) * w

    def Y(v):
        return pad_t + h - v / top * h

    out = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="Line chart, {X0} to {X1}: '
           + "; ".join(SERIES[k][0] for k in keys) + '" style="max-width:100%;height:auto">']
    for v in (0, 25, 50, 75, 100):
        out.append(f'<line x1="{pad_l}" y1="{Y(v):.1f}" x2="{pad_l + w}" y2="{Y(v):.1f}" stroke="{grid}" stroke-width="1"/>')
        if labels:
            out.append(f'<text x="{pad_l - 6}" y="{Y(v) + 4:.1f}" text-anchor="end" font-size="12" font-family="system-ui, sans-serif" fill="{text_colour}">{v}</text>')
    if labels:
        for y in (1995, 2000, 2005, 2010, 2015, 2020, 2026):
            out.append(f'<text x="{X(y):.1f}" y="{pad_t + h + 18}" text-anchor="middle" font-size="12" font-family="system-ui, sans-serif" fill="{text_colour}">{y}</text>')
    for k in keys:
        name, _, pts, _ = SERIES[k]
        col = colour(keys, k)
        sw, r = (3, 3.5) if labels else (6, 7)
        if len(pts) > 1:
            out.append(f'<polyline points="{" ".join(f"{X(y):.1f},{Y(v):.1f}" for y, v in pts)}" fill="none" stroke="{col}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>')
        for y, v in pts:
            out.append(f'<circle cx="{X(y):.1f}" cy="{Y(v):.1f}" r="{r}" fill="{col}"/>')
    out.append("</svg>")
    return "".join(out)


def legend_rows(keys):
    rows = []
    for k in keys:
        name, _, pts, src = SERIES[k]
        rows.append((name, colour(keys, k), f"{pts[0][1]:g} ({pts[0][0]}) → {pts[-1][1]:g} ({pts[-1][0]})", src))
    return rows


def unit_note(keys):
    return "Values are per cent, except subscriptions, which are per 100 people and can pass 100." if ymax(keys) > 100 else "All values are per cent."


def slide(story, n):
    keys, notice = CHAPTERS[story][n]
    legend = "".join(
        f'<div style="display:flex;gap:14px;align-items:center"><div style="width:36px;height:8px;background:{c};border-radius:4px;flex:none"></div>'
        f'<p style="font-size:24px;color:{NAVY};line-height:1.3"><b>{name}</b> {span}</p></div>' for name, c, span, _ in legend_rows(keys))
    srcs = "; ".join(sorted({SERIES[k][3] for k in keys}))
    cw, ch = 780, 500
    years = "".join(f'<p style="position:absolute;left:{SLIDE_PAD + (y - X0) / (X1 - X0) * (cw - 2 * SLIDE_PAD):.0f}px;transform:translateX(-50%);font-size:22px;color:#5A6478">{y}</p>' for y in (1995, 2000, 2005, 2010, 2015, 2020, 2026))
    ylab = "".join(f'<p style="position:absolute;right:0;top:{SLIDE_PAD + (1 - v / ymax(keys)) * (ch - 2 * SLIDE_PAD) - 14:.0f}px;font-size:22px;color:#5A6478">{v}</p>' for v in (0, 50, 100))
    top = ymax(keys)
    return (f'<section id="curve-ch{n}" data-transition="fade" style="background:{CREAM};color:{NAVY};font-family:\'Public Sans\', Arial, sans-serif;padding:104px 128px;display:flex;flex-direction:column;gap:28px">'
            '<div style="display:flex;flex-direction:column;gap:10px">'
            f'<p style="font-size:24px;font-weight:700;color:#5A6478;letter-spacing:3px;text-transform:uppercase">End of chapter {n} · {X0} to {X1}</p>'
            f'<h2 style="font-family:\'Libre Baskerville\', Georgia, serif;font-size:60px;font-weight:700;line-height:1.1">How fast did it spread?</h2></div>'
            '<div style="display:grid;grid-template-columns:1.15fr 1fr;gap:56px;align-items:start">'
            '<div style="display:flex;flex-direction:column;gap:10px">'
            f'<div style="display:flex;gap:14px"><div style="position:relative;width:56px;height:{ch}px;flex:none">{ylab}</div>'
            f'<div style="width:{cw}px;flex:none">{svg(keys, cw, ch, False)}<div style="position:relative;height:34px;margin-top:6px">{years}</div></div></div></div>'
            '<div style="display:flex;flex-direction:column;gap:16px">'
            f'{legend}<p style="font-size:26px;line-height:1.45;color:#3D4A63">{notice}</p></div></div>'
            f'<p style="font-size:22px;color:#5A6478">{unit_note(keys)} Sources: {srcs}.</p>'
            f'<aside>Every chapter ends with a chart on the same axis, {X0} to {X1}, so the curves can be compared from chapter to chapter. A line starts and stops where the data does; it does not mean the technology began or ended there. {notice}</aside></section>')


def block(story, n, fig_class, heading_tag="h3"):
    keys, notice = CHAPTERS[story][n]
    rows = "".join(f'<tr><td><span class="sw" style="background:{c}"></span>{name}</td><td>{span}</td><td>{src}</td></tr>' for name, c, span, src in legend_rows(keys))
    return (f'<{heading_tag}>How fast did it spread?</{heading_tag}>\n'
            f'<p>{notice}</p>\n'
            f'<figure class="{fig_class}">{svg(keys, 760, 300, True, text_colour="currentColor", grid="rgba(127,127,127,.3)")}</figure>\n'
            f'<table class="curve-key"><tr><th>Line</th><th>First and last point</th><th>Source</th></tr>{rows}</table>\n'
            f'<p class="cap">{unit_note(keys)} Each chapter ends with a chart on the same axis, {X0} to {X1}. A line starts and stops where the data does.</p>\n')


def update_deck(story):
    deck_dir = HERE / story / "deck"
    deck = json.loads((deck_dir / "deck.json").read_text())
    order = [s for s in deck["order"] if not s.startswith("curve-ch")]
    for old in deck_dir.glob("slides/curve-ch*.html"):
        old.unlink()
    for n in range(1, 8):
        (deck_dir / "slides" / f"curve-ch{n}.html").write_text(slide(story, n) + "\n")
    out = []
    chapter = 0
    for sid in order:
        m = re.fullmatch(r"ch(\d)", sid)
        if (m or sid in ("dates-1", "recap")) and chapter and f"curve-ch{chapter}" not in out:
            out.append(f"curve-ch{chapter}")
        if m:
            chapter = int(m.group(1))
        out.append(sid)
    deck["order"] = out
    (deck_dir / "deck.json").write_text(json.dumps(deck, ensure_ascii=False))


def update_notes(story):
    path = HERE / story / "notes.html"
    text = re.sub(r"<!-- curve:start ch\d -->.*?<!-- curve:end -->\n?", "", path.read_text(), flags=re.S)
    for n in range(1, 8):
        nxt = f'<h2 id="ch{n + 1}">' if n < 7 else ('<!-- timeline:start -->' if '<!-- timeline:start -->' in text else '<h2 id="sources">')
        i = text.index(nxt)
        text = text[:i] + f"<!-- curve:start ch{n} -->\n" + block(story, n, "chart") + "<!-- curve:end -->\n" + text[i:]
    path.write_text(text)


PAGE_CSS = """
.curve-card { background: #fffdf9; color: #1b2a4a; border: 2px solid #1b2a4a; border-radius: 14px; padding: 16px 20px; margin: 28px auto 0; max-width: 960px; font: 16px/1.55 "Atkinson Hyperlegible Next", "Segoe UI", system-ui, sans-serif; text-shadow: none; text-transform: none; letter-spacing: normal; }
.curve-card h3 { font: 700 20px/1.25 "Atkinson Hyperlegible Next", system-ui, sans-serif; margin: 0 0 6px; color: #1b2a4a; }
.curve-card .from { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; color: #5a6478; margin: 0 0 4px; }
.curve-card figure { margin: 10px 0; color: #1b2a4a; }
.curve-card svg { display: block; width: 100%; height: auto; }
.curve-card table { border-collapse: collapse; width: 100%; font-size: 14px; background: none; }
.curve-card th, .curve-card td { text-align: left; padding: 5px 8px; border: 0; border-bottom: 1px solid #d9d3c7; color: #1b2a4a; background: none; }
.curve-card .sw, .curve-key .sw { display: inline-block; width: 18px; height: 6px; border-radius: 3px; margin-right: 8px; vertical-align: middle; }
.curve-card .cap { font-size: 13px; color: #5a6478; }
"""


def update_page(story):
    path = HERE / story / "site.html"
    text = re.sub(r"<!-- curve:start ch\d -->.*?<!-- curve:end -->\n?", "", path.read_text(), flags=re.S)
    if ".curve-card {" not in text:
        text = text.replace("</style>", PAGE_CSS + "</style>", 1)
    for n, band in PAGE_BANDS[story].items():
        start = text.index(f'id="{band}"')
        end = text.index("</section>", start)
        card = (f'<!-- curve:start ch{n} -->\n<div class="wrap"><aside class="curve-card" aria-label="Adoption chart for this era">'
                f'<p class="from">A note from today · {X0} to {X1}</p>' + block(story, n, "", "h3") + '</aside></div>\n<!-- curve:end -->\n')
        text = text[:end] + card + text[end:]
    path.write_text(text)


def main():
    for story in ("web", "server", "network"):
        update_deck(story)
        update_notes(story)
        update_page(story)
    print("curves written")


if __name__ == "__main__":
    main()
