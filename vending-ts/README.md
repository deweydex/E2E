# Vending machine, TypeScript edition

A small web server written in TypeScript on Node, a SQLite database, and a page made of plain HTML, CSS and a short TypeScript script.

You need Node 22.18 or newer (Node 24 is recommended). The only packages are the TypeScript compiler and Node's type definitions, and both are used while you develop.

```
npm install            # downloads TypeScript and the type definitions
npm run setup-db       # creates vending.db (run it again to reset the machine)
npm run build          # compiles client/app.ts into public/app.js
npm run start          # starts the server
```

Then open http://127.0.0.1:8000 in a browser. Press Ctrl+C in the terminal to stop the server.

Node prints a warning that SQLite is an experimental feature. The warning is expected.

| File | Purpose |
| --- | --- |
| `src/setup-db.ts` | Creates the table and fills it with four snacks |
| `src/server.ts` | The web server and the API |
| `client/app.ts` | The script that asks the server for data and updates the page |
| `public/index.html` | The structure of the page |
| `public/style.css` | The look of the page |
| `src/injection-demo.ts` | Shows why queries use parameters |
| `npm run check` | Type-checks the server files without running them |
