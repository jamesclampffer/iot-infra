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
from enum import Enum, Flag, UNIQUE
import enum
import json
import sys
from urllib.parse import urlparse

class ComponentNotFound(BaseException):
    __slots__ = 'what'
    def __init__(self, w):
        self.what = w
    def __str_(self):
        return self.__repr__()
    def __repr__(self):
        return "ComponentNotFound: {}".format(self.what)

class BaseMockComponent:
    """
    Intend to move error handling and logging utils into here, the call()
    method could also be hoisted.

    deviceref: Pointer to the device for components that need crosstalk
    dispatch_lit: name->method obj mapping
    component_config: dict containing a canned config for the component
    """
    __slots__ = 'deviceref', 'dispatch_lut', 'config'
    def __init__(self):
        """ Just explicitly null out slots """
        self.deviceref = None
        self.dispatch_lut = None
        self.config = None

    def operationNotFound(self,ctx):
        print("error: Operation not found: {}".format(ctx))
        return {"error":"invalid operation"}
    def callNotImplemented(self,ctx):
        print("error: This isn't implemented yet: {}".format(ctx))
        return {"error":"not implemented (yet)"}
    def call(self, fname, args):
        lut = self.dispatch_lut
        if fname not in lut:
            return self.operationNotFound(fname)
        else:
            return lut[fname](args)
    def setConfig(self, args):
        key = None #todo
        val = None #todo
        print("debug: setting {} to {}".format(key,val))
        if key in self.config:
            self.config[key] = val
            err = False
        else:
            err = True    
        return {
            "restart_required": False,
            "error" : False
        }
    def getConfig(self, args):
        key = None #todo
        val = None

        if key in self.config:
            val = self.config[key]
            err = False
        else:
            err = True
        return {
            "value":val,
            "error":err
        }

