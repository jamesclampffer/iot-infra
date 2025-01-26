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
from enum import Enum    
import json
import sys
from urllib.parse import urlparse

#replace prints with logging.logger()
#https://stackoverflow.com/questions/18444395/basehttprequesthandler-with-custom-instance/18445168#18445168

class BaseMockComponent:

    """Pointer to the device for components that need crosstalk"""
    __slots__ = 'deviceref'

class InputComponent(BaseMockComponent):
    """Config + state for a single input"""
    __slots__ = 'lut' #just use getattr?
    def __init__(self, dev):
        self.deviceref = dev
        self.lut = {}
        self.lut['GetConfig'] = self.getConfig
        self.lut['SetConfig'] = self.setConfig
        self.lut['GetStatus'] = self.getStatus
        self.lut['ResetCounters'] = self.resetCounters
        self.lut['Trigger'] = self.trigger

    def call(self, fname : str, args : dict):
        print("trace: Input.call({},{})".format(fname,args))
        if fname not in self.lut:
            print("error: call not found")
            return None
        else:
            self.lut[fname](args)

    def getConfig(self, args : dict):
        return '{"called":"getConfig"}'
    def setConfig(self, args : dict):
        return '{"called":"setConfig"}'
    def getStatus(self, args : dict):
        return '{"called":"getStatus"}'
    def resetCounters(self, args : dict):
        return '{"called":"resetCounters"}'
    def trigger(self, args : dict):
        return '{"called":"trigger"}'

class SystemComponent(BaseMockComponent):
    """Component that returns system stats"""
    def call(self, fname, args):
        """Map string name to function"""
        pass
    def __init__(self, dev):
        self.deviceref = dev
    def getConfig(self):
        pass
    def setConfig(self):
        pass
    def getStatus(self):
        pass

class SwitchComponent(BaseMockComponent):
    """Single switch/relay output"""
    def __init__(self, dev):
        self.deviceref = dev
    def getConfig(self):
        pass
    def setConfig(self):
        pass
    def getStatus(self):
        pass
    def set(self):
        pass
    def toggle(self):
        pass
    def resetCounters(self):
        pass

class ScriptComponent(BaseMockComponent):
    """An instance of a script manager running on the device"""
    def __init__(self, dev):
        self.deviceref = dev
    def getConfig(self):
        pass
    def setConfig(self):
        pass
    def getStatus(self):
        pass
    def list(self):
        pass
    def create(self):
        pass
    def delete(self):
        pass
    def start(self):
        pass
    def stop(self):
        pass
    def putCode(self):
        pass
    def getCode(self):
        pass
    def eval(self):
        pass

class DeviceState:
    __slots__ = 'inputs', 'switches', 'system', 'scripts', 'handlers'

    def __init__(self):
        print("Setting up emulated hardware")
        self.inputs = [InputComponent(self) for x in range(4)]
        self.switches = [SwitchComponent(self) for x in range(4)]
        self.system = SystemComponent(self)
        self.scripts = []

    def process_get(self, pathstr : str) -> str:
        print("Processing path: {}".format(pathstr))
        examplestr = """
        {"id": 1, "name"=dude}
        """

        #TODO: START HERE
        resp = self.handle_root(pathstr)

        return examplestr

    def handle_root(self, uri : str):
        """Redirect to handler for resource in the uri query"""
        uriobj = urlparse(uri)

        #Build up query argument map, use parse_qs?
        q = uriobj.query
        pairs = {}
        substrs = q.split('&')
        for pair in substrs:
            print(pair)
            a, b = tuple(pair.split('='))
            pairs[a] = b

        # Find component index if there is one
        id = None
        if 'id' in pairs:
            id = int(pairs['id'])

        #todo: fold these decode cases into a generic dispatch
        p = uriobj.path
        if p.find('Input') == 1:
            fname = p[7:].split('?')[0]
            print(fname)
            print(pairs)
            self.inputs[id].call(fname, pairs)
        elif p.find('Switch') == 1:
            fname = p[8:].split('?')[0]
            print(fname)
            print(pairs)
            self.switches[id].call(fname,pairs)
        elif p.find('Sys') == 1:
            fname = p[5:].splid('?')[0]
            print(fname)
            print(pairs)
            self.sys.call(fname, pairs)
        elif p.find('Scripts') == 1:
            fname = p[8:].split('?')[0]
            print(fname)
            print(pairs)
            self.scripts[id].call(fname, pairs)

    def handle_input(self, id : int, uriargmap : dict):
        """Redirect to inputs[id]"""
        input = self.inputs[id]
        
    def handle_switch(self, id : int, uriargmap : dict):
        """Redirect to switchs[id]"""
        switch = self.switches[id]
        assert 1 != id
        
    def handle_sys(self, uriargmap : dict):
        """Redirect to system[0]"""
        pass
        


"""
Mock device exposes more components than may be available on specific devices
"""
class MockShellyDevice(BaseHTTPRequestHandler):
    __slots__ = 'inputs', 'switches', 'system', 'scripts', 'handlers', 'hostname', 'port'
    singleton_state = None

    def do_GET(self):
        """Entrypoint for http connections"""

        # Shared state, does this limit to one mock instance per process
        # shelly_dev = MockShellyDevice

        #response headers
        #todo: resource not found handling
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
 
        if self.path.find('/favicon.ico') == 0:
            self.wfile.write(bytes("",'utf-8'))
        else:
            # Poke the device state, respond accordingly
            resp = MockShellyDevice.singleton_state.process_get(self.path)
            # Send response to client
            self.wfile.write(bytes(resp, 'utf-8'))

if __name__ == '__main__':
    # todo - figure out how to pass args in vscode
    if len(sys.argv) == 1:
        sys.argv.append('localhost')
        sys.argv.append('8080')
        if len(sys.argv) == 3:
            _, hostname, port = sys.argv
            print("Starting, host={} port={}".format(hostname,port))
        else:
            print("expected a host and port argument")

    # Make the mock device
    print("Starting server")
    srv = HTTPServer(('localhost',8080), MockShellyDevice)
    MockShellyDevice.singleton_state = DeviceState()
    print("server started localhost:8080")

    # Allow execution of handlers
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.socket.close()

