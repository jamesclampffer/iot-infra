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

class BaseMockComponent:
    __slots__ = 'deviceref'

class InputComponent(BaseMockComponent):
    """Config + state for a single input"""
    def __init__(self, dev):
        self.deviceref = dev
    def getConfig(self):
        pass
    def setConfig(self):
        pass
    def getStatus(self):
        pass
    def resetCounters(self):
        pass
    def trigger(self):
        pass

class SystemComponent(BaseMockComponent):
    """Component that returns system stats"""
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



"""
Mock device exposes more components than may be available on specific devices
"""
class MockShellyDevice:
    __slots__ = 'inputs', 'switches', 'system', 'scripts', 'handlers', 'hostname', 'port'
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port

        # Set up all loaded components, for now hard code counts
        self.inputs = [InputComponent(self) for x in range(4)]
        self.switches = [SwitchComponent(self) for x in range(4)]
        self.system = SystemComponent(self)
        self.scripts = []

    def bind_handlers(self):
        handlers = {}

        # Key in by ID
        handlers['Input.SetConfig'] = None
        handlers['Input.GetConfig'] = None
        handlers['Input.GetStatus'] = None
        handlers['Input.ResetCounters'] = None
        handlers['Input.Trigger'] = None

        # Figure out ID
        handlers['Switch.SetConfig'] = None
        handlers['Switch.GetConfig'] = None
        handlers['Switch.GetStatus'] = None
        handlers['Switch.Set'] = None
        handlers['Switch.Toggle'] = None
        handlers['Switch.ResetCounters'] = None

        # No ID, singleton
        handlers['Sys.SetConfig'] = None
        handlers['Sys.GetConfig'] = None
        handlers['Sys.GetStatus'] = None
        self.handlers = handlers

    def handle_root(self, uri : str):
        """Redirect to handler for resource in the uri query"""
        uriobj = urlparse(uri)

        #Build up query argument map, use parse_qs?
        q = uriobj.query
        pairs = dict(pair.split('=') for pair in q.split('&'))

        id = None
        if 'id' in pairs:
            id = int(pairs[id])

        p = uriobj.path

        if p.find('Input') == 1:
            self.handle_input(id, pairs)
        elif p.find('Switch') == 1:
            self.handle_switch(id, pairs)
        elif p.find('Sys') == 1:
            self.handle_sys(pairs)
        elif p.find('Scripts') == 1:
            pass
            

    def handle_input(self, id : int, uriargmap : dict):
        """Redirect to inputs[id]"""
        assert 1 != id
        input = inputs[id]
        pass
    def handle_switch(self, id : int, uriargmap : dict):
        """Redirect to switchs[id]"""
        switch = switches[id]
        assert 1 != id
        pass
    def handle_sys(self, uriargmap : dict):
        """Redirect to system[0]"""
        pass



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
    device = MockShellyDevice(hostname,port)