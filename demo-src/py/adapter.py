"""A stand-in for the HTTP layer of server.py, for use inside a browser.

A browser cannot open a network port, so the real HTTP layer (the class that
reads sockets) cannot run here. The data layer and the route layer in
server.py do not need sockets, so we import them unchanged and write only
this small replacement for the top layer.
"""

import json
from urllib.parse import urlsplit

import server


def answer(http_method, path):
    """Answer one request and return (status_code, body_text)."""
    # The path may carry a query string, so we keep only the path.
    url_path = urlsplit(path).path

    try:
        # The same route table that the real server uses. The first match wins.
        for route_method, path_pattern, handler in server.ROUTES:
            path_match = path_pattern.fullmatch(url_path)
            if route_method == http_method and path_match:
                return 200, json.dumps(handler(*path_match.groups()))

        return 404, json.dumps({"error": "No such route."})

    # The same translation from exceptions to status codes as the real server.
    except server.BadRequest as error:
        return 400, json.dumps({"error": str(error)})
    except server.NoSuchSlot as error:
        return 404, json.dumps({"error": str(error)})
    except server.SoldOut as error:
        return 409, json.dumps({"error": str(error)})
