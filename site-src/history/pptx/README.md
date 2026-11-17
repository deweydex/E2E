# PowerPoint copies of the two decks

The `.pptx` files beside each deck are made from pictures of the slides, with the speaker notes and each slide's title kept. To rebuild them after a slide changes:

1. Run `python3 build.py` in `site-src/`.
2. Serve the repository root, for example `python3 -m http.server 8765`.
3. In this folder, run `node render.js` and then `node build.js`. Both need Playwright and pptxgenjs.
4. Copy `how-the-web-learned-to-respond.pptx` into `history/web/` and `behind-the-page.pptx` into `history/server/`, then build again.
