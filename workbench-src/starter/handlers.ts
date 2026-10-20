// handlers.ts holds your routes. A route says: when this request arrives, run this function.
// Ready-made names: route, json, fail, db.all, db.get, db.run, db.transaction, queries.<name>.sql

route("GET", "/api/slots", () => {
  return json(db.all(queries.list_slots.sql));
});
