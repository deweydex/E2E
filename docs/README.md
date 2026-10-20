# Tutorial site

Static files only. To publish on GitHub Pages, commit this folder (including `downloads/`, `diagrams/`, `demo/` and `demo-ts/`), then choose the folder or branch under Settings, Pages.

- `index.html` is the landing page, and `python.html` and `typescript.html` are the two editions. Each page has a Settings button for theme, text size, code wrapping and motion, saved in the reader's browser.
- `downloads/` holds the two project zips that the pages link to. Rebuild them after you change a project.
- `diagrams/` holds every diagram as a standalone SVG file with its own light and dark styles.
- `demo/` (Python, through Pyodide) and `demo-ts/` (TypeScript, through sql.js) hold the simulated servers. They need the site to be served over http or https, so they do not work when a page is opened straight from a file. They load Pyodide and sql.js from the jsDelivr CDN.
- `workbench/` is a split-screen tool for students. The browser is on the left, and the server and database are on the right, with a timeline between the two. It runs entirely in the browser, and the TypeScript server, the sql.js database and the Prism syntax colouring are included in the folder, so that part also works from a file. The Python server loads Pyodide from the jsDelivr CDN the first time it is chosen.
- The lab itself (the real server) always runs on the student's own computer.
