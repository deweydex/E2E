# Server tutorials

A tutorial site that shows how a click in a browser reaches a database and comes back. It includes a split-screen workbench where students watch a request travel through the pipeline.

## Contents of the site

- The landing page links to everything else.
- The Python edition and the TypeScript edition build the same vending machine in two languages.
- Every diagram is also available as a standalone SVG file with light and dark styles.
- Two in-page demos run a small server inside the browser.
- The workbench opens on a setup screen. The student chooses a mode, a level and a server language, can upload their own files, and reads a short tour of what each file is for before the workbench opens.
- The workbench shows a front end on the left and a back end on the right, with a timeline below.
- The timeline stops at every step. Start, Back, Forward and End move through the request, and each card names the tutorial station it belongs to, with the station before and after. Key words have the same hover explanations as the tutorials.
- Two lab projects (Python and TypeScript) can be downloaded from the tutorial pages.

## How each tutorial is organised

- **Start here** lists what you build, what you learn and what you need.
- **Try it first** runs the finished machine in the page.
- **Steps 1 to 6** lead the student through making it: follow one click, build the database, the server, the page and the script, then run it and watch the traffic.
- Every build step has a goal, numbered actions, the annotated code, a check that it works, and a short explanation.
- **Going deeper** holds the optional material: HTTP messages and status codes, experiments that break the machine on purpose, design choices, and extensions.
- The **Glossary** names the step or section that explains each term.

## Publish on GitHub Pages

The site is published from the `docs/` folder. To set it up again, for example in a new repository:

1. Open the repository's Settings, then Pages.
2. Set Source to "Deploy from a branch".
3. Choose branch `main` and folder `/docs`, then press Save.
4. Wait a minute or two for the site to appear.

The finished site is plain HTML, CSS and JavaScript, so it needs no build step.

## Folder guide

| Folder or file | What it holds |
|---|---|
| `docs/` | The finished site, which is the only folder that Pages publishes. |
| `site-src/` | The Python scripts that build the site into `docs/`. |
| `workbench-src/` | The source of the workbench: editors, server engines, sample app and the server code that students read. |
| `demo-src/` | The source of the two in-page demos. |
| `vending-py/` | The Python lab project. |
| `vending-ts/` | The TypeScript lab project. |
| `wb-build/` | The npm package list for updating the bundled libraries. |
| `machine.png` | The picture on the landing page. |

## Change something and rebuild

1. Edit a file in `site-src/`, `workbench-src/` or `demo-src/`.
2. Run `python3 build.py` from inside `site-src/`. It needs Python 3 and no other packages.
3. Commit the changed source and the rebuilt `docs/` together.

Do not edit files in `docs/` by hand, because the next build overwrites them.

## Bundled libraries

All four are open source. The first three sit in `workbench-src/vendor/`.

- sql.js 1.13.0 provides the database for the TypeScript server.
- Sucrase 3.35.0 removes TypeScript types in the browser.
- Prism 1.29.0 colours the code in the editors.
- Pyodide 0.29.5 provides the Python server. It loads from the jsDelivr CDN on first use, which is a download of about 10 MB.

## Browser support

- The workbench is tested in Chromium.
- The TypeScript server and the colouring work from a local folder without a network.
- The Python server and the two in-page demos need http or https and an internet connection.
