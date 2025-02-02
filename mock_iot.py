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
from enum import Enum, IntEnum
import json
import sys
from urllib.parse import urlparse

class BaseMockComponent:
    """
    Intend to move error handling and logging utils into here, the call()
    method could also be hoisted.

    deviceref: Pointer to the device for components that need crosstalk
    dispatch_lit: name->method obj mapping
    component_config: dict containing a canned config for the component
    """
    __slots__ = 'deviceref', 'dispatch_lut', 'component_config'
    def __init__(self):
        """ Just explicitly null out slots """
        self.deviceref = None
        self.dispatch_lut = None
        self.component_config = None

    def operationNotFound(self,ctx):
        print("error: Operation not found: {}".format(ctx))

    def setConfig(self, args):
        return {
            "restart_required": False
        }
 

class InputComponent(BaseMockComponent):
    """
    State for a single input along with spoofed config.
    Only 120VAC inputs supported for now (no TLL or ADC)
    """
    __slots__ = 'val' #just use getattr?

    class InputValue(Enum):
        OFF = 0 # Open circuit, or pulled to ground
        ON  = 1 # 120VAC or 240VAC

    def __init__(self, dev):
        """
        Initialize Input in a known state (OFF)
        Populate the lookup table for a string based call() mechanism
        """
        self.deviceref = dev
        self.val = InputComponent.InputValue.OFF

        # bind methods by string name
        lut = {}
        lut['GetConfig'] = self.getConfig
        lut['SetConfig'] = self.setConfig
        lut['GetStatus'] = self.getStatus
        lut['ResetCounters'] = self.resetCounters
        lut['Trigger'] = self.trigger
        self.dispatch_lut = lut

    def call(self, fname : str, args : dict):
        #Push this into the base class!
        """ Look up method by name and forward args """
        lut = self.dispatch_lut
        if fname not in lut:
            return self.operationNotFound(fname)
        else:
            return lut[fname](args)

    def getConfig(self, args : dict):
        """ Return a valid canned config until setConfig is implemented """
        return '{"called":"getConfig"}'

    def getStatus(self, args : dict):
        """ Return status of a digital input """
        valstr = str(self.val)
        status = {
            'id':None,
            'state':valstr
        }
        return status

    def resetCounters(self, args : dict):
        """
        No-op, but return a valid response
        Counter inputs not supported yet
        """
        return '{"called":"resetCounters"}'
    def trigger(self, args : dict):
        """
        Not implemented, try to return valid response.
        """
        return '{"called":"trigger"}'

class SystemComponent(BaseMockComponent):
    """Component that returns system stats"""
    __slots__ = 'system_state', 'system_config'

    def __init__(self, dev):
        self.deviceref = dev
        lut = {}
        lut['GetConfig'] = self.getConfig
        lut['SetConfig'] = self.setConfig
        lut['GetStatus'] = self.getStatus
        self.dispatch_lut = lut

        # Add keys, don't need vals for now
        self.system_config = {
            "device":{
                "name":None,
                "eco_mode":None,
                "mac":None,
                "fw_id":None,
                "profile":None,
                "discoverable":None,
                "addon_type":None,
                "sys_btn_toggle":None
            },
            "location":{
                "tz":None,
                "lat":None,
                "lon":None
            },
            "debug":{
                "mqtt":None,
                "websocket":None,
                "udp":None
            },
            "cfg_rev":None
        }

        self.system_state = {
            "mac": "DEADBEEFD00D",
            "restart_required": False,
            "time": "00:00",
            "unixtime": 1654694407,
            "last_sync_ts": 1654694307,
            "uptime": 1000,
            # todo: load from config based on hardware response
            "ram_size": 253464,
            "ram_free": 146012,
            "fs_size": 458752,
            "fs_free": 212992,
            "cfg_rev": 10,
            "kvs_rev": 277,
            "schedule_rev": 0,
            "webhook_rev": 0,
            "btrelay_rev": 0,
            "available_updates": {
                "stable": {
                "version": "0.10.2"
                }
            }
        }

    def call(self, fname, args):
        """ See InputComponent """
        lut = self.dispatch_lut
        if fname not in lut:
            return self.operationNotFound(fname)
        else:
            return lut[fname](args)

    def getConfig(self, args:dict):
        """ Config from example """
        return self.system_config

    def getStatus(self, args:dict):
        """ Other things update status, this just returns it """
        # todo: need locking?
        return self.system_state

class SwitchComponent(BaseMockComponent):
    """Single switch/relay output"""
    __slots__ = 'output'

    class OutputValue(Enum):
        """ This only applies to AC on/off """
        OFF = 0
        ON = 1

    def __init__(self, dev):
        self.deviceref = dev
        lut={}
        lut['GetConfig'] = self.getConfig
        lut['SetConfig'] = self.setConfig
        lut['GetStatus'] = self.getStatus
        lut['Set'] = self.set
        lut['ResetCounters'] = self.resetCounters
        self.dispatch_lut = lut
        self.output = SwitchComponent.OutputValue.OFF

    def call(self, fname, args):
        lut = self.dispatch_lut
        if fname not in lut:
            return self.operationNotFound(fname)
        else:
            return lut[fname](args)

    def getConfig(self, args):
        pass

    def getStatus(self, args):
        valstr = str(self.output)
        resp = {
            'id':None,
            'output':valstr,
            'voltage':120,
            'freq':60,
        }
        return resp
    def set(self):
        pass
    def toggle(self):
        pass
    def resetCounters(self):
        pass

class KVSComponent(BaseMockComponent):
    """ Stubbing this out - NOTHING TESTED """
    __slots__ = 'kvs_map'
    def __init__(self, dev):
        self.deviceref = dev
        self.kvs_map = {}

        lut = {}
        lut['Set'] = self.doSet
        lut['Get'] = self.doGet
        lut['GetMany'] = self.doGetMany
        lut['List'] = self.doList
        lut['Delete'] = self.doDelete
        self.dispatch_lut = lut

    def call(self, fname, args):
        lut = self.dispatch_lut
        if fname not in lut:
            return self.operationNotFound(fname)
        else:
            return lut[fname](args)

    def doSet(self, args):
        """ Add etag support later """
        key = args['key']
        vpair = args['value'].split(' ')
        self.kvs_map[key] = vpair
        rval = {
            "etag": "",
            "rev": -1
        }
        return rval
        
    def doGet(self, args):
        key = args['key']
        v = None
        if key in self.kvs_map:
            v = self.kvs_map[key]
        return {
            "etag": "",
            "value": v
        }

    def doGetMany(self, args):
        pass
    def doList(self, args):
        pass
    def doDelete(self, args):
        key = args['key']
        del self.kvs_map[key]
        return {
            "rev":-1
        }
        
class ScriptComponent(BaseMockComponent):
    """An instance of a script manager running on the device"""
    def __init__(self, dev):
        self.deviceref = dev
    def getConfig(self):
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
    """
    Represent a set of hardware components (e.g. IO) and system services that a device sould run
    note: Until device profile configs are used to init this just sets up a bunch of IO
    """
    __slots__ = 'inputs', 'switches', 'system', 'scripts', 'kvs'

    def __init__(self):
        print("Setting up emulated hardware")
        self.inputs = [InputComponent(self) for x in range(4)]
        self.switches = [SwitchComponent(self) for x in range(4)]
        self.system = SystemComponent(self)
        self.scripts = []
        self.kvs = KVSComponent(self)

    def process_get(self, pathstr : str) -> str:
        """ Pull apart the URI and figure out what to do """
        resp = self.handle_root(pathstr)
        return resp

    def handle_root(self, uri : str):
        """Redirect to handler for resource in the uri query"""
        uriobj = urlparse(uri)
        q = uriobj.query
        pairs = {}
        substrs = q.split('&')
        for pair in substrs:
            print(pair)
            a, b = tuple(pair.split('='))
            pairs[a] = b

        # Find component id if there is one, isex to index into vector of components
        id = None
        if 'id' in pairs:
            id = int(pairs['id'])

        #TODO: Lookup table line mock-emitters.py uses
        resp = None
        p = uriobj.path
        if p.find('Input') == 1:
            if id not in range(len(self.inputs)):
                return self.componentIdNotFound(id)
            fname = p[7:].split('?')[0]
            print(fname)
            resp = self.inputs[id].call(fname, pairs)
        elif p.find('Switch') == 1:
            if id not in range(len(self.inputs)):
                return self.componentIdNotFound(id)
            fname = p[8:].split('?')[0]
            resp = self.switches[id].call(fname,pairs)
        elif p.find('Sys') == 1:
            fname = p[5:].splid('?')[0]
            resp = self.sys.call(fname, pairs)
        elif p.find('Scripts') == 1:
            if id not in range(len(self.inputs)):
                return self.componentIdNotFound(id)
            fname = p[8:].split('?')[0]
            resp = self.scripts[id].call(id, fname, pairs)
        elif p.find('KVS') == 1:
            fname = p[5:].split('?')[0]
            resp = self.kvs.call(fname,pairs)
        else:
            print("error: Component not found")
            resp = {"error": "Component not found"} # Need a http header soln

        # Individual components don't need to track their ID relative to others of same type,
        # but stuff the id into the map if it is used
        if id != None and 'id' in resp:
            resp['id'] = id

        # make JSON out of dict
        return json.dumps(resp)

    def componentIdNotFound(self, id : int):
        print("warn: Component index {} does not exist".format(id))


class MockShellyDevice(BaseHTTPRequestHandler):
    """
    Server responsible for exposing the mock device over http
    """
    singleton_state = None

    def do_GET(self):
        """Entrypoint for http connections"""
        #response headers
        self.send_response(200) #todo: resource not found handling
        self.send_header('Content-type', 'application/json')
        self.end_headers()
 
        # Todo - better handling of browser requests
        if self.path.find('/favicon.ico') == 0:
            self.wfile.write(bytes("",'utf-8'))
        else:
            # Poke the device state, respond accordingly
            resp = MockShellyDevice.singleton_state.process_get(self.path)
            print("info: got json resp {} for {}".format(resp, self.path))
            # Send response to client
            self.wfile.write(bytes(resp, 'utf-8'))

if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('localhost')
        sys.argv.append('8080')
        if len(sys.argv) == 3:
            _, hostname, port = sys.argv
            print("Starting, host={} port={}".format(hostname,port))
        else:
            print("error: expected a host and port argument, using defaults")

    # Make the mock device
    print("Starting server")
    srv = HTTPServer(('localhost',8080), MockShellyDevice)
    MockShellyDevice.singleton_state = DeviceState()
    print("server started localhost:8080")

    # Start listening
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.socket.close()

