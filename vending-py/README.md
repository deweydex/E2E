# Vending machine, Python edition

A small web server written with the Python standard library, a SQLite database, and a page made of plain HTML, CSS and a short script.

You need Python 3.10 or newer. No packages are required.

```
python setup_db.py     # creates vending.db (run it again to reset the machine)
python server.py       # starts the server
```

Then open http://127.0.0.1:8000 in a browser. Press Ctrl+C in the terminal to stop the server.

On macOS and Linux the command may be `python3` instead of `python`.

| File | Purpose |
| --- | --- |
| `setup_db.py` | Creates the table and fills it with four snacks |
| `server.py` | The web server and the API |
| `public/index.html` | The structure of the page |
| `public/style.css` | The look of the page |
| `public/app.js` | The script that asks the server for data and updates the page |
| `injection_demo.py` | Shows why queries use parameters |
| `server_fastapi.py` | Optional: the same API written with the FastAPI framework |
