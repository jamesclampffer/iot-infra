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


"""
Python wrappers for RPC. Not convinced this is better than json.

Reference:
https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/Shell
"""

import json


class ShellyHttpResponse:
    def parse_from_http(self, http_body : str):
        pass
    def to_json(self):
        pass
    def from_json(self, json_doc):
        pass

class ShellyHttpRequest:
    def built_uri_path_with_query(self):
        pass
    def to_json(self):
        pass
    def from_json(self, json_doc):
        pass


class Shelly:
    class RpcRequest:
        def __str__(self) -> str:
            return self.to_json()


    class GetStatus:
        path = '/rpc/Shelly.GetStatus'
        class Request:
            pass
        class Response:
            pass
    class GetConfig:
        path = '/rpc/Shelly.GetConfig'
        class Request:
            pass
        class Resposnse:
            pass
    class ListMethods:
        path = '/rpc/Shelly.ListMethods'
        class Request:
            pass
        class Response:
            pass
    class GetDeviceInfo:
        path = '/rpc/Shelly.GetDeviceInfo'
        class Request:
            __slots__ = 'ident'
        class Response:
            __slots__ = 'id', 'mac', 'model', 'gen'\
                        'fw_id', 'ver', 'app', 'profile'\
                        'auth_en', 'auth_domain', 'discoverable'\
                        'key', 'batch', 'fw_sbits'
            def to_dict(self):
                return {
                    'id':self.id,
                    'mac':self.mac,
                    'model':self.model,
                    'gen':self.gen,
                    'fw_id':self.fw_id,
                    'ver':self.ver,
                    'app':self.app,
                    'auth_en':self.auth_en,
                    'auth_domain':self.auth_domain,
                    'discoverable':self.discoverable
                }
            def to_json(self):
                return json.dumps(self.to_dict())
            def __str__(self):
                return self.to_json()

    class DetectLocation:
        path = '/rpc/Shelly.DetectLocation'
        class Request:
            pass
        class Response:
            __slots__ = 'tz', 'lat_deg', 'lon_deg'
    class GetComponents:
        path = '/rpc/Shelly/GetComponents'
        class Request:
            __slots__ = 'offset', 'include', 'dynamic_only'
        class Response:
            __slots__ = 'component_array', 'cfg_rev', 'offset'\
                        'total'
    class ListMethods:
        path = '/rpc/Shelly.ListMethods'
        class Request:
            pass
        class Response:
            pass


class Humidity:
    class SetConfig:
        path = 'Humidity.SetConfig'
        class Request:
            __slots__ = 'id', 'config'
            def to_dict(self) -> dict:
                return {'id':self.id, 'config':self.config}
            def to_json(self) -> str:
                return json.dumps(self.to_dict())
            def __str__(self) -> str:
                return self.to_json()
        class Response:
            __slots__ = 'restart_required'
            def to_dict(self):
                return {'restart_required':self.restart_required}
            def to_json(self):
                return json.dumps(self.to_dict())
            def __str__(self) -> str:
                return self.to_json()
    class GetConfig:
        path = 'Humidity.GetConfig'
        class Request:
            __slots__ = 'id'
            def to_dict(self):
                return {'id':id}
            def to_json(self):
                return json.dumps(self.to_dict())
            def __str__(self):
                return self.to_json()
        class Response:
            __slots__ = 'id', 'src', 'params_list'
            def to_dict(self) -> dict:
                return {
                    'id':self.id,
                    'src':self.src,
                    'params_list':self.params_list
                }
            def to_json(self) -> str:
                return json.dumps(self.to_dict())
            def __str__(self) -> str:
                return self.to_json()
    class GetStatus:
        path = 'Humidity.GetStatus'
        class Request:
            __slots__ = 'id'
            def from_json(self,json_doc:str):
                doc = json.loads(json_doc)
                self.id = doc['id']
            def to_json(self) ->str:
                return json.dumps(self.to_dict())
            def to_dict(self) -> dict:
                return {'id':self.id}
            def __str__(self) -> str:
                return self.to_json()
        class Response:
            __slots__ = 'id', 'rh'
            def to_dict(self) -> dict:
                return {'id':self.id, 'rh':self.rh}
            def to_json(self) -> str:
                return json.dumps(self.to_dict())
            def __str__(self) -> str:
                return self.to_json()

class Voltmeter:
    class SetConfig:
        path = 'Voltmeter.SetConfig'
        class Request:
            __slots__ = 'id', 'config'
            def to_dict(self) -> dict:
                return {'id':self.id, 'config':self.config}
            def to_json(self) -> str:
                return json.dumps(self.to_dict())
            def __str__(self) -> str:
                return self.to_json()
            def check(self):
                assert type(self.id) == int and self.config != None
        class Response:
            __slots__ = 'id','name','report_thr','range',\
                        'xvoltage'
            def to_dict(self) -> dict:
                return {
                    'id':self.id,
                    'name':self.name,
                    'report_thr':self.report_thr,
                    'range':self.range,
                    'xvoltage':self.xvoltage
                }
            def to_json(self) -> str:
                return json.dumps(self.to_dict())
            def __str__(self) -> str:
                return self.to_json()
            def check(self):
                pass
            
    class GetConfig:
        path = 'Voltmeter.GetConfig'
        class Request:
            __slots__ = 'id'
            def from_json(self,json_doc:str):
                doc = json.loads(json_doc)
                self.id = doc['id']
            def to_json(self) ->str:
                return json.dumps(self.to_dict())
            def to_dict(self):
                return {'id':self.id}            
            def check(self):
                assert type(self.id) == int
        class Response:
            pass
    class GetStatus:
        path = 'Voltmeter.GetStatus'
        class Request:
            __slots__ = 'id'
            def from_json(self,json_doc:str):
                doc = json.loads(json_doc)
                self.id = doc['id']
            def to_json(self) ->str:
                return json.dumps(self.to_dict())
            def to_dict(self):
                return {'id':self.id}
            def check(self):
                assert type(self.id) == int
        class Reponse:
            __slots__ = 'id','voltage','xvoltage','errors'
            def from_json(self,json_doc:str):
                doc = json.loads(json_doc)
                self.id = doc['id']
                self.voltage = doc['voltage']
                self.xvoltage = doc['xvoltage']
                if 'errors' in doc:
                    self.errors=doc['errors']
            def to_json(self) -> str:
                return json.dumps(self.to_dict())
            def to_dict(self) -> dict:
                return {
                    'id':self.id,
                    'voltage':self.voltage,
                    'xvoltage':self.xvoltage,
                    'errors':self.errors
                }
            def check(self):
                assert type(self.id) == int
                assert type(self.voltage) in (int,float) or self.voltage == None
                assert type(self.xvoltage) in (int,float) or self.xvoltage == None
                if self.errors != None:
                    for e in self.errors:
                        assert type(e) == str

            


        
    