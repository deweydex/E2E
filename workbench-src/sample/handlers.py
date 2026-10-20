# handlers.py holds your routes. A route says: when this request arrives, run this function.
#
# These names come from server.py and are ready to use:
#   @route(method, pattern)   registers the function below it. A word such as :slot is read from the path.
#   ok(body)                  answers 200 with this body
#   fail(status, message)     answers with an error status and a message
#   db.all(sql, params)       runs a query and returns every row
#   db.get(sql, params)       runs a query and returns the first row, or None
#   db.run(sql, params)       runs a statement that changes data and returns a result with .changes
#   with db.transaction():    runs the indented lines as one unit that succeeds or fails as a whole
#   queries["list_slots"]["sql"]   holds the text of a query from queries.sql


@route("GET", "/api/slots")
def list_slots(request):
    return ok(db.all(queries["list_slots"]["sql"]))


@route("GET", "/api/slots/:slot")
def get_slot(request):
    slot = db.get(queries["get_slot"]["sql"], {"slot": request.params["slot"]})
    if slot is None:
        return fail(404, f"There is no slot called {request.params['slot']}.")
    return ok(slot)


@route("POST", "/api/slots/:slot/buy")
def buy_slot(request):
    slot_id = request.params["slot"]

    # Both statements run inside one transaction, so the sale and the stock change happen together.
    with db.transaction():
        update = db.run(
            "UPDATE slots SET stock = stock - 1 WHERE slot_id = :slot AND stock > 0",
            {"slot": slot_id},
        )
        # Nothing was updated, so the slot is sold out or does not exist. Leaving the with block here changes nothing.
        if update.changes == 0:
            return fail(409, "That slot is sold out, or it does not exist.")
        db.run(
            "INSERT INTO sales (slot_id, price_cents) SELECT slot_id, price_cents FROM slots WHERE slot_id = :slot",
            {"slot": slot_id},
        )

    return ok(db.get(queries["get_slot"]["sql"], {"slot": slot_id}))


@route("POST", "/api/slots/:slot/restock")
def restock_slot(request):
    amount = request.body.get("amount")
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < 1:
        return fail(400, "The amount must be a whole number of at least 1.")
    result = db.run(queries["restock_slot"]["sql"], {"slot": request.params["slot"], "amount": amount})
    if result.changes == 0:
        return fail(404, f"There is no slot called {request.params['slot']}.")
    return ok(db.get(queries["get_slot"]["sql"], {"slot": request.params["slot"]}))


@route("GET", "/api/sales")
def list_sales(request):
    return ok(db.all(queries["list_sales"]["sql"]))
