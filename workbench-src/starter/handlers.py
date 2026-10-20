# handlers.py holds your routes. A route says: when this request arrives, run this function.
# Ready-made names: route, ok, fail, db.all, db.get, db.run, db.transaction, queries["name"]["sql"]


@route("GET", "/api/slots")
def list_slots(request):
    return ok(db.all(queries["list_slots"]["sql"]))
