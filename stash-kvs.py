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
from urllib.parse import urlparse

import pickle
import json

class InvalidOperationError(BaseException):
    """
    Request specifies an operation that doesn't exist.
    """
    __slots__ = 'opname'
    def __init__(self, name):
        self.opname = name
    def __str__(self):
        return "InvalidOperationError: {}".format(self.opname)

class HashKeyNotFoundError(BaseException):
    """
    Request specifies a key that's not in the map
    """
    __slots__ = 'keystr'
    def __init__(self, k):
        self.keystr = k
    def __str__(self):
        return "HashKeyNotFoundError: {}".format(self.keystr)

class VersionedPickle(object):
    """ 
    Serialize contents
    TODO: Is picking datum usefull here?
    """
    __slots__ = 'bytes', 'version'
    def __init__(self):
        self.version = -1
        self.bytes = pickle.dumps(None)
    def update(self, obj):
        self.bytes = pickle.dumps(obj)
        self.version += 1
        return self
    def value(self):
        return pickle.loads(self.bytes)
    def __repr__(self):
        return "VersionedPickle: {}".format(str({
            'version': self.version,
            'strval': self.value()
        }))
    def __str__(self):
        return self.__repr__()

class SharedHash(object):
    """
    Hash table that versions contents
    Intended as a quick & dirty way to publish data
    """
    __slots__ = 'bigmap', 'dispatch_lut', 'table'

    def __init__(self):
        self.table = {}
        lut = {}
        lut['get'] = self.get
        lut['set'] = self.set
        lut['delete'] = self.delete
        self.dispatch_lut = lut

    def call(self, uri_path:str):
        """
        Parse the path to figure out action and params
        TODO: This is the same(ish) code as SHOP-316, refactor when that's merged
        """
        oper = uri_path.split('/')[1]
        oper = oper.split('?')[0]

        # Validate operation
        if oper not in self.dispatch_lut:
            raise InvalidOperationError(oper)

        query = uri_path.split('?')[1]
        argpairs = query.split('&')

        args = {}
        for apair in argpairs:
            v = apair.split('=')
            args[v[0]] = v[1]
        
        k = None
        if 'key' in args:
            k = args['key']
        v = None
        if 'value' in args:
            v = args['value']
        elif 'val' in args:
            v = args['val']

        # lambda bindings in lut setup rather than tuple wrapped args?
        if oper in self.dispatch_lut:
            return self.dispatch_lut[oper]((k,v))
        return "invalid operation!"

    def set(self, kvtup):
        """ Bump version number on each set call, even if same value """
        key, val = kvtup
        self.addslot(key)
        self.table[key].update(str(val))
        return { 
            'version' : self.table[key].version
        }

    def get(self,keytup:tuple):
        """ Fetch the value and associated version """
        key, _ = keytup
        if key not in self.table:
            raise HashKeyNotFoundError(key)
        
        o = self.table[key]
        return {
            'value':o.value(),
            'version':o.version
        }

    def delete(self, keytup:tuple):
        """ Not tested! """
        key, _ = keytup
        if key not in self.table:
            return {
                'version':-1
            }
        ref = self.table[key]
        del self.table[key]
        return {
            'lastversion':ref.version
        }

    # not public interface
    def addslot(self,keytup):
        """ Make sure there's a slot (and table) set up. Don't need latter anymore """
        if self.table == None:
            self.table = dict()
        key = keytup
        if key in self.table:
            return
        self.table[key] = VersionedPickle()


class KVSHandler(BaseHTTPRequestHandler):
    """ Exists to forward requests from do_GET to the singletonState class var """

    singletonState = SharedHash()
    def do_GET(self):

        # Handle browser stuff better..
        if self.path.find('/favicon.ico') == 0:
            self.send_response(204) # 204=no content
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes("",'utf-8'))
            return

        # Do lookup, make sure response header is reasonable
        obj = None
        try:
            obj = KVSHandler.singletonState.call(self.path)
        except InvalidOperationError as e:
            print('error: {}'.format(str(e)))
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            return
        except HashKeyNotFoundError as e:
            print('error: {}'.format(str(e)))
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            return

        print("sending {}".format(obj))
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # serialize to json
        outbytes = json.dumps(obj)
        self.wfile.write(bytes(outbytes,'utf-8'))

if __name__ == '__main__':
    #XXX Use config or cmd line args
    HOST = 'localhost'
    PORT = 9090

    print("Starting server")
    srv = HTTPServer((HOST, PORT), KVSHandler)
    KVSHandler.singleton_state = SharedHash()
    print("kvs server started localhost:9090")

    # Start listening
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.socket.close()
            