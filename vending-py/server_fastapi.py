"""The same API, written with the FastAPI framework.

Install:  pip install fastapi uvicorn
Run:      uvicorn server_fastapi:app --port 8000
Then open http://127.0.0.1:8000 and also http://127.0.0.1:8000/docs
"""

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Path as UrlPath, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

# We reuse the data layer from server.py. Importing that file does not start
# the other server, because of the "if __name__ == '__main__'" guard there.
from server import NoSuchSlot, SoldOut, buy_slot, get_all_slots, get_slot

app = FastAPI(title="Vending machine")

# A slot id must match this pattern. The framework checks it for us, which
# replaces the validate_slot_id function in server.py.
SlotId = Annotated[str, UrlPath(pattern=r"^[A-Za-z][0-9]$")]


# Each decorator adds one row to the framework's route table. These are the same
# three routes as the ROUTES list in server.py.
@app.get("/api/slots")
def list_slots():
    return get_all_slots()


@app.get("/api/slots/{slot_id}")
def show_slot(slot_id: SlotId):
    return get_slot(slot_id.upper())


@app.post("/api/slots/{slot_id}/buy")
def buy(slot_id: SlotId):
    return buy_slot(slot_id.upper())


# These handlers turn exceptions into status codes. We keep the same
# {"error": ...} shape as before, so the page does not need to change.
@app.exception_handler(RequestValidationError)
def handle_bad_request(request: Request, error: RequestValidationError):
    return JSONResponse({"error": "Slot ids look like A1 or B2."}, status_code=400)


@app.exception_handler(NoSuchSlot)
def handle_no_such_slot(request: Request, error: NoSuchSlot):
    return JSONResponse({"error": str(error)}, status_code=404)


@app.exception_handler(SoldOut)
def handle_sold_out(request: Request, error: SoldOut):
    return JSONResponse({"error": str(error)}, status_code=409)


# Serve the page files. This line must come last, because the routes above
# are checked first.
app.mount("/", StaticFiles(directory=Path(__file__).parent / "public", html=True))
