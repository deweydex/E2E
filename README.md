# Server tutorials

A tutorial site about how a click in a browser reaches a database and comes back, with a split-screen workbench where students can watch a request travel through the pipeline. The site has a Python edition and a TypeScript edition, and every diagram is also a standalone SVG file.

## What is in this folder

- `docs/` is the finished site. It is plain HTML, CSS and JavaScript, so it needs no build step to publish.
- `site-src/` holds the Python scripts that build the site into `docs/`.
- `workbench-src/` holds the source of the workbench: the editors, the two server engines, the bridge script, the sample app and the server code that students read.
- `demo-src/` holds the in-page demos, which run a small server in the browser.
- `vending-py/` and `vending-ts/` are the two lab projects that the tutorials link to as downloads.
- `wb-build/` lists the npm packages (Sucrase and Prism) that two of the bundled libraries were made from. The bundled files themselves are already in `workbench-src/vendor/`, so you only need this folder if you want to update a library.
- `machine.png` is the picture of the vending machine used on the landing page.

## Publishing on GitHub Pages

Push this folder to a repository. Then open Settings, then Pages, choose the branch, and choose the `/docs` folder. The site appears at the address that Pages shows. The first page is `docs/index.html`, and the workbench is at `docs/workbench/index.html`.

## Changing something and rebuilding

Edit the files in `site-src/` or `workbench-src/`, then run this from the `site-src` folder:

    python3 build.py

The script rewrites everything in `docs/` that it owns. Commit the result together with your source changes. The build needs Python 3 and no extra packages.

## Libraries that travel with the site

The workbench includes sql.js 1.13.0 (the database), Sucrase 3.35.0 (the TypeScript step) and Prism 1.29.0 (the syntax colouring). All three sit in `docs/workbench/vendor/`, so the TypeScript server and the colouring work even when the page is opened from a folder. The Python server loads Pyodide 0.29.5 from the jsDelivr CDN the first time a student chooses it, which is a download of about 10 MB.

## Known limits

The workbench was tested in Chromium. It has not been tested in Firefox or Safari, and no student has used it yet. The `demo/` and `demo-ts/` pages need to be served over http or https, so they do not run when opened straight from a file.
