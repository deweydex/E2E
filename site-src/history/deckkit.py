"""Helpers for writing slide decks in the Slides artifact format: one <section> per slide on a
1920 by 1080 canvas, with inline styles and speaker notes in <aside>. Each deck script imports
these, adds its slides in order, then calls write()."""

import json
from pathlib import Path

NAVY, CREAM, CARD = "#1B2A4A", "#F7F5F0", "#FFFDF9"
PART = {
    "Network": ("#7CC6C1", "#1F6B66"),
    "HTML": ("#E8955C", "#A24A18"),
    "CSS": ("#8DB4E2", "#24588F"),
    "Scripts": ("#E9C46A", "#7A5D00"),
    "Server": ("#8CC9A6", "#2E6B4A"),
    "Database": ("#B9A6E0", "#5B3F9E"),
}
SERIF = "font-family:'Libre Baskerville', Georgia, serif"
MONO = "font-family:'JetBrains Mono', 'Courier New', monospace"
BASE = "font-family:'Public Sans', Arial, sans-serif;padding:128px"

slides, order, sections = {}, [], {}



def chip(name, size=24):
    pad = "6px 18px" if size <= 24 else "8px 24px"
    return (f'<p style="font-size:{size}px;font-weight:700;color:{NAVY};background:{PART[name][0]};'
            f'padding:{pad};border-radius:24px">{name}</p>')


def add(slide_id, html, section=None):
    if section:
        sections[section[0]] = {"description": section[1], "start": slide_id}
    order.append(slide_id)
    slides[slide_id] = html


def head(eyebrow, chips, title, dark, size=72):
    grey = "#C9D2E3" if dark else "#5A6478"
    return (f'<div style="display:flex;flex-direction:column;gap:16px">'
            f'<div style="display:flex;gap:16px;align-items:center">'
            f'<p style="font-size:24px;font-weight:700;color:{grey};letter-spacing:3px;text-transform:uppercase">{eyebrow}</p>'
            + "".join(chip(c) for c in chips) +
            f'</div><h2 style="{SERIF};font-size:{size}px;font-weight:700;line-height:1.1">{title}</h2></div>')


def section_open(slide_id, dark, layout="display:flex;flex-direction:column;justify-content:center;gap:48px"):
    bg, fg = (NAVY, "#F4F1EA") if dark else (CREAM, NAVY)
    return f'<section id="{slide_id}" data-transition="fade" style="background:{bg};color:{fg};{BASE};{layout}">'


def foot(text, dark):
    color = "#C9D2E3" if dark else "#3D4A63"
    return f'<p style="font-size:30px;line-height:1.45;color:{color}">{text}</p>' if text else ""


def divider(slide_id, number, years, title, sub, chips, notes, section):
    html = (section_open(slide_id, True, "display:flex;flex-direction:column;justify-content:center;gap:40px") +
            f'<p style="font-size:32px;font-weight:700;color:#C9D2E3;letter-spacing:4px;text-transform:uppercase">Chapter {number} · {years}</p>'
            f'<h2 style="{SERIF};font-size:96px;font-weight:700;line-height:1.1">{title}</h2>'
            f'<p style="font-size:40px;line-height:1.4;color:#C9D2E3">{sub}</p>'
            '<div style="display:flex;gap:16px">' + "".join(chip(c, 28) for c in chips) + '</div>'
            f'<aside>{notes}</aside></section>')
    add(slide_id, html, section)


def cards(slide_id, eyebrow, chips, title, items, footer, notes, dark=False, section=None):
    """items: (heading, body, part, example or None)."""
    cols = " ".join(["1fr"] * len(items))
    out = section_open(slide_id, dark) + head(eyebrow, chips, title, dark)
    out += f'<div style="display:grid;grid-template-columns:{cols};gap:40px">'
    for heading, body, part, example in items:
        light, deep = PART[part]
        if dark:
            out += (f'<div style="display:flex;flex-direction:column;gap:16px;border-top:8px solid {light};padding:32px 0 0 0">'
                    f'<h3 style="font-size:38px;font-weight:700;color:{light}">{heading}</h3>'
                    f'<p style="font-size:28px;line-height:1.45;color:#E6E9F0">{body}</p>')
            if example:
                out += f'<p style="font-size:24px;color:#C9D2E3">{example}</p>'
        else:
            out += (f'<div style="display:flex;flex-direction:column;gap:18px;background:{CARD};padding:44px;border:2px solid #D9D3C7;'
                    f'border-top:16px solid {light};border-radius:16px">'
                    f'<h3 style="font-size:38px;font-weight:700;color:{deep}">{heading}</h3>'
                    f'<p style="font-size:28px;line-height:1.45;color:#3D4A63">{body}</p>')
            if example:
                out += f'<p style="font-size:24px;color:#5A6478">{example}</p>'
        out += '</div>'
    out += '</div>' + foot(footer, dark) + f'<aside>{notes}</aside></section>'
    add(slide_id, out, section)


def code(slide_id, eyebrow, chips, title, text, code_label, code_text, footer, notes, dark=False):
    """Text on the left, a code panel on the right."""
    out = section_open(slide_id, dark, "display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center")
    grey = "#C9D2E3" if dark else "#3D4A63"
    out += f'<div style="display:flex;flex-direction:column;gap:32px">{head(eyebrow, chips, title, dark)}'
    out += "".join(f'<p style="font-size:30px;line-height:1.45;color:{grey}">{t}</p>' for t in text)
    out += '</div><div style="display:flex;flex-direction:column;gap:16px">'
    out += (f'<div style="background:#0F1A30;border-radius:16px;padding:32px;display:flex;flex-direction:column;gap:12px">'
            f'<p style="font-size:22px;font-weight:700;color:#C9D2E3">{code_label}</p>'
            f'<p style="{MONO};font-size:25px;line-height:1.6;color:#F4F1EA">{code_text}</p></div>')
    if footer:
        out += f'<p style="font-size:26px;line-height:1.45;color:{grey}">{footer}</p>'
    out += f'</div><aside>{notes}</aside></section>'
    add(slide_id, out)


def dated(slide_id, eyebrow, chips, title, left, items, notes, dark=False):
    """A short explanation on the left and a column of dated events on the right."""
    out = section_open(slide_id, dark) + head(eyebrow, chips, title, dark)
    grey = "#C9D2E3" if dark else "#3D4A63"
    out += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:start">'
    out += '<div style="display:flex;flex-direction:column;gap:24px">' + "".join(
        f'<p style="font-size:30px;line-height:1.45;color:{grey}">{t}</p>' for t in left) + '</div>'
    out += '<div style="display:flex;flex-direction:column;gap:24px">'
    for when, what, part in items:
        light, deep = PART[part]
        colour = light if dark else deep
        out += (f'<div style="display:flex;flex-direction:column;gap:6px;border-left:8px solid {light};padding:0 0 0 24px">'
                f'<p style="font-size:30px;font-weight:700;color:{colour}">{when}</p>'
                f'<p style="font-size:26px;line-height:1.4;color:{grey}">{what}</p></div>')
    out += f'</div></div><aside>{notes}</aside></section>'
    add(slide_id, out)




def write(out, title):
    (out / "slides").mkdir(parents=True, exist_ok=True)
    for old in (out / "slides").glob("*.html"):
        old.unlink()
    for slide_id, html in slides.items():
        (out / "slides" / f"{slide_id}.html").write_text(html + "\n")
    deck = {
        "v": 5, "createdOnFiles": {"v": 1, "at": "2026-11-17T10:00:00Z"}, "lists": "css", "format": {"v": 1, "shared": ["project/deck.css"]},
        "title": title, "order": order, "sections": sections,
        "faces": {
            "libre-baskerville": {"family": "Libre Baskerville", "href": "https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&display=swap"},
            "public-sans": {"family": "Public Sans", "href": "https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;600;700&display=swap"},
            "jetbrains-mono": {"family": "JetBrains Mono", "href": "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap"},
        },
    }
    (out / "deck.css").write_text("body { font-family: 'Public Sans', Arial, sans-serif; color: #1B2A4A; }\n")
    (out / "deck.json").write_text(json.dumps(deck, ensure_ascii=False))
    print(len(order), "slides")
