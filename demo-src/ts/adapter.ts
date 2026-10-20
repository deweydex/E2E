// A stand-in for the HTTP layer of server.ts, for use inside a browser.
//
// A browser cannot open a network port, so the real HTTP layer (the code that
// uses node:http) cannot run here. The data layer and the route layer do not
// need a network, so the build copies them out of server.ts unchanged, and
// this file replaces only the top layer.

// The pieces of server.ts that this file needs.
type Machine = {
  ROUTES: { httpMethod: string; pathPattern: RegExp; handler: (...capturedText: string[]) => unknown }[];
  BadRequest: new (message: string) => Error;
  NoSuchSlot: new (message: string) => Error;
  SoldOut: new (message: string) => Error;
};

type Answer = { status: number; body: string };

function createAnswerer(machine: Machine) {
  // Answer one request and return a status code and the body text.
  return function answer(httpMethod: string, urlPath: string): Answer {
    try {
      // The same route table that the real server uses. The first match wins.
      for (const route of machine.ROUTES) {
        const pathMatch = route.pathPattern.exec(urlPath);
        if (route.httpMethod === httpMethod && pathMatch !== null) {
          return { status: 200, body: JSON.stringify(route.handler(...pathMatch.slice(1))) };
        }
      }
      return { status: 404, body: JSON.stringify({ error: "No such route." }) };
    } catch (error) {
      // The same translation from errors to status codes as the real server.
      if (error instanceof machine.BadRequest) {
        return { status: 400, body: JSON.stringify({ error: error.message }) };
      } else if (error instanceof machine.NoSuchSlot) {
        return { status: 404, body: JSON.stringify({ error: error.message }) };
      } else if (error instanceof machine.SoldOut) {
        return { status: 409, body: JSON.stringify({ error: error.message }) };
      }
      return { status: 500, body: JSON.stringify({ error: "Something went wrong on the server." }) };
    }
  };
}
