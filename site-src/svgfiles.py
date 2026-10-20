"""Write every diagram as a standalone SVG file with its own light and dark styles."""

import re
from pathlib import Path

import diagrams
import lib
import theme


def _svg_rules():
    rules = re.findall(r"(?m)^svg [^{}\n]+\{[^}]*\}", lib.CSS)
    assert len(rules) >= 15, "expected the svg rules in lib.CSS"
    return "\n".join(rules)


def standalone(svg_markup):
    """Turn inline SVG into a file that carries its own styles."""
    view = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_markup)
    label = re.search(r'aria-label="([^"]*)"', svg_markup)
    width, height = view.groups()
    start_tag_end = svg_markup.index(">") + 1
    start_tag = svg_markup[:start_tag_end].replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    style = f"<style>\n{theme.standalone_token_css()}\n{_svg_rules()}\n</style>"
    title = f"<title>{label.group(1)}</title>" if label else ""
    background = f'<rect width="{width}" height="{height}" rx="12" fill="var(--surface)"/>'
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + start_tag + title + style + background + svg_markup[start_tag_end:] + "\n"


# (file name, description for the landing page, markup builder given one edition's values)
def catalogue(editions):
    items = []
    py, ts = editions
    for edition in (py, ts):
        slug = edition["slug"]
        items.append((f"journey-{slug}.svg", f"The journey of one click, twelve stations ({edition['name']} edition)", diagrams.journey_svg(edition["server_label"])))
    items.append(("trust.svg", "Who controls what: why the browser cannot reach the database", lib.trust_svg() if False else diagrams.trust_svg()))
    for edition in (py, ts):
        slug = edition["slug"]
        items.append((f"url-{slug}.svg", f"Anatomy of a URL and how a route reads it ({edition['name']} edition)", diagrams.url_svg(edition["handler_call"])))
    for edition in (py, ts):
        slug = edition["slug"]
        items.append((f"layers-{slug}.svg", f"The three layers of the server ({edition['name']} edition)", diagrams.layers_svg(edition["layer_names"])))
    for edition in (py, ts):
        slug = edition["slug"]
        items.append((f"shapes-{slug}.svg", f"The same data in five shapes ({edition['name']} edition)", diagrams.shapes_svg(edition)))
    items.append(("race.svg", "Two buyers and one item: read then write, against a single UPDATE", diagrams.race_svg()))
    items.append(("cors.svg", "Why the browser withholds an answer from another origin", diagrams.cors_svg()))
    return items


def write_all(dist: Path, editions):
    out = dist / "diagrams"
    out.mkdir(parents=True, exist_ok=True)
    items = catalogue(editions)
    for name, _, markup in items:
        (out / name).write_text(standalone(markup))
    return [(name, description) for name, description, _ in items]
