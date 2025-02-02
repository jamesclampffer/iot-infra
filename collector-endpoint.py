import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from os import getenv
import urllib.parse
import uuid

# This is what'd live in a config file later on
# A record my define a subset or superset of what the endpoint will recv
# For now just hard code a couple subclasses
"""
recorddefs = {
    'compressor' : {
        'psi':'float',
        'compressor_running':'bool',
    }
}
"""

class TelemetryRecord:
    __slots__ = 'uuid', 'recordtype', 'recordtypever', 'colnames', 'kvpairs'
    def __init__(self, kvpairs):
        """ Set up common column names """
        self.colnames = ['uuid', 'recordtype', 'recordtypever']
        self.uuid = uuid.SafeUUID()
        self.recordtype = 'TelemetryRecordBase'
        self.recordtypever = '0.0.0'
        self.kvpairs = kvpairs
    def __repr__(self):
        return 'TelemetryRecord {}.{}: {}'.format(self.recordtype, self.recordtypever, json.dumps(self.kvpairs))
    def __str__(self):
        return self.__repr__()
    def to_delimited(self, delim=' '):
        """ Build a delimited string of just the values based on ordinal pos """
        buf=[]
        for colname in self.colnames:
            if colname not in self.kvpairs:
                val = None
            else:
                val = str(self.kvpairs[colname])
            buf.append(val)
        return delim.join(buf)
    def to_json(self):
        arr = []
        for idx, colname in enumerate(self.colnames):
            colval = None
            if colname in self.kvpairs:
                colval = self.kvpairs[colname]
            arr.append({
                'name': colname,
                'colidx': idx,
                'value': colval
            })
            return json.dumps(arr)
            
class EndpointState:
    __slots__ = 'records'
    def __init__(self):
        self.records = []
        pass
    def process_path(self, path:str):
        """ Return json string response """
        print("processing path: {}".format(path))
        # Expects a simple authority/?query
        # Consider using the path to indicate the desired grouping

        encodedqry = path.split('?')[1]
        #FIXME: Only values of query parts should be escaped
        qry = urllib.parse.unquote_plus(encodedqry)

        # do this with urllib parser
        pairs = qry.split('&')
        m = {}
        for pair in pairs:
            pair = pair.split('=')
            m[pair[0]] = pair[1]

        topic = path.split('?')[0]
        return self.recv_record(topic, m)

    def recv_record(self, topic:str, recordcontents : dict) -> str:
        return json.dumps({
            'recorded':True
        })


class StdoutEndpoint(BaseHTTPRequestHandler):
    singleton_state = None
    def __init__(self):
        pass

    def do_GET(self):
        s = StdoutEndpoint.singleton_state
        try:
            res = s.process_path(self.path)
        except Exception as e:
            print(e)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            b = bytes(res, 'utf-8')
            self.wfile.write(b)
            return

        #TBD Config flag to return some optional metadata?
        self.send_response(400)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        b = bytes(res, 'utf-8')
        self.wfile.write(b)

if __name__ == 'main':
    HOST = getenv('EPHOST', default='localhost')
    PORT = getenv('EPPORT')
    if PORT != None:
        PORT = int(PORT)

    srv = HTTPServer((HOST,PORT), StdoutEndpoint)
    StdoutEndpoint.singleton_state = EndpointState()

    # Start listening
    try:
        srv.serve_forever()
        print("Serving")
    except KeyboardInterrupt:
        srv.socket.close()
            