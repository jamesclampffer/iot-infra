"""
Copyright 2024 Jim Clampffer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at^M

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from os import getenv
import uuid
import urllib.parse
import urllib.request

import sqlite3_collector_backend


class EndpointState:
    """Make sense of incoming GET requests, write them to the backend"""

    __slots__ = "writer"

    def __init__(self, backend=None):
        if backend == None:
            self.writer = sqlite3_collector_backend.DBWriter()
        else:
            self.writer = backend

    def process_path(self, path: str) -> str:
        """
        Path expected to be of the form authority/?<query>, however handling
        <authority>/<topic>?<query> should be supported soon.
        Return json string response
        """

        # TODO: do this with urllib parser
        qry = path.split("?")[1]
        pairs = qry.split("&")
        m = {}
        for pair in pairs:
            pair = pair.split("=")
            pair[1] = urllib.parse.unquote_plus(pair[1])
            m[pair[0]] = pair[1]

        return self.recv_record(m)

    def recv_record(self, recordcontents: dict) -> str:
        "Forward record derived from request to (storage) backend"
        self.writer.acceptData(recordcontents)
        return json.dumps({"recorded": True})


class StdoutEndpoint(BaseHTTPRequestHandler):
    singletonState = None

    def do_GET(self) -> None:
        """Handle a GET request from a sensing node"""

        def send_header(code: int) -> None:
            """Send http response header, common to all return paths"""
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

        # Get away with this because the server is single threaded
        s = StdoutEndpoint.singletonState
        try:
            res = s.process_path(self.path)
        except Exception as e:
            # todo: 400 vs 404 etc
            print("Exception in processing {}\n{}".format(self.path, str(e)))
            send_header(400)
            b = bytes("", "utf-8")
            self.wfile.write(b)
            return

        # Report success, needs content-length
        send_header(200)
        b = bytes(res, "utf-8")
        self.wfile.write(b)


if __name__ == "__main__":
    # Bind to all network interfaces by default
    HOST = getenv("EP_HOST", default="0.0.0.0")
    PORT = int(getenv("EP_PORT", 9050))

    srv = HTTPServer((HOST, PORT), StdoutEndpoint)
    StdoutEndpoint.singletonState = EndpointState()

    # Start listening
    try:
        srv.serve_forever()
        print("Endpoint {}:{} started".format(HOST, PORT))
    except KeyboardInterrupt:
        srv.socket.close()
