// handlers.ts holds your routes. A route says: when this request arrives, run this function.
//
// These names come from server.ts and are ready to use:
//   route(method, pattern, handler)   registers a route. A word such as :slot in the pattern is read from the path.
//   json(body)                        answers 200 with this body
//   fail(status, message)             answers with an error status and a message
//   db.all(sql, params)               runs a query and returns every row
//   db.get(sql, params)               runs a query and returns the first row, or undefined
//   db.run(sql, params)               runs a statement that changes data and returns { changes }
//   db.transaction(work)              runs work as one unit that succeeds or fails as a whole
//   queries.list_slots.sql            holds the text of a query from queries.sql

route("GET", "/api/slots", () => {
  return json(db.all(queries.list_slots.sql));
});

route("GET", "/api/slots/:slot", (request) => {
  const slot = db.get(queries.get_slot.sql, { slot: request.params.slot });
  if (!slot) {
    return fail(404, `There is no slot called ${request.params.slot}.`);
  }
  return json(slot);
});

route("POST", "/api/slots/:slot/buy", (request) => {
  const slotId = request.params.slot;

  // Both statements run inside one transaction, so the sale and the stock change happen together.
  const bought = db.transaction(() => {
    const update = db.run(
      "UPDATE slots SET stock = stock - 1 WHERE slot_id = :slot AND stock > 0",
      { slot: slotId }
    );
    // Nothing was updated, so the slot is sold out or does not exist. Leaving the transaction here changes nothing.
    if (update.changes === 0) {
      return false;
    }
    db.run(
      "INSERT INTO sales (slot_id, price_cents) SELECT slot_id, price_cents FROM slots WHERE slot_id = :slot",
      { slot: slotId }
    );
    return true;
  });

  if (!bought) {
    return fail(409, "That slot is sold out, or it does not exist.");
  }
  return json(db.get(queries.get_slot.sql, { slot: slotId }));
});

route("POST", "/api/slots/:slot/restock", (request) => {
  const amount = Number(request.body.amount);
  if (!Number.isInteger(amount) || amount < 1) {
    return fail(400, "The amount must be a whole number of at least 1.");
  }
  const result = db.run(queries.restock_slot.sql, { slot: request.params.slot, amount });
  if (result.changes === 0) {
    return fail(404, `There is no slot called ${request.params.slot}.`);
  }
  return json(db.get(queries.get_slot.sql, { slot: request.params.slot }));
});

route("GET", "/api/sales", () => {
  return json(db.all(queries.list_sales.sql));
});
