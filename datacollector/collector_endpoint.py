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

import collector_backend
            
class EndpointState:
    """ Make sense of incoming GET requests, write them to the backend """
    __slots__ = 'writer'
    def __init__(self, backend=None):
        if backend == None:
            self.writer = collector_backend.DBWriter()
        else:
            self.writer = backend

    def process_path(self, path:str):
        """
        Path expected to be of the form authority/?<query>, however handling
        <authority>/<topic>?<query> should be supported soon.
        Return json string response
        """

        # TODO: do this with urllib parser
        qry = path.split('?')[1]
        pairs = qry.split('&')
        m = {}
        for pair in pairs:
            pair = pair.split('=')
            pair[1] = urllib.parse.unquote_plus(pair[1])
            m[pair[0]] = pair[1]

        # TODO: Using the path to indicate the desired grouping/topic
        return self.recv_record(m)

    def recv_record(self, recordcontents : dict) -> str:
        self.writer.acceptData(recordcontents)
        return json.dumps({
            'recorded':True
        })


class StdoutEndpoint(BaseHTTPRequestHandler):
    singletonState = None

    def do_GET(self):
        def send_header(code:int):
            """ Send http response header """
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

        s = StdoutEndpoint.singletonState
        try:
            res = s.process_path(self.path)
        except Exception as e:
            # TODO: identify and disambiguate failure modes (400 vs 404 etc)
            print(e)
            send_header(400)
            # TODO: Does spec require a response body?
            b = bytes("", 'utf-8')
            self.wfile.write(b)
            return

        # Report success
        send_header(200)
        b = bytes(res, 'utf-8')
        self.wfile.write(b)

if __name__ == '__main__':
    # Bind to all network interfaces by default
    HOST = getenv('EP_HOST', default='0.0.0.0')
    PORT = getenv('EP_PORT', 9050)
    PORT = int(PORT)

    srv = HTTPServer((HOST,PORT), StdoutEndpoint)
    StdoutEndpoint.singletonState = EndpointState()

    # Start listening
    try:
        srv.serve_forever()
        print("Serving")
    except KeyboardInterrupt:
        srv.socket.close()
            
