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

import urllib.request as builtin_request
import json

import shelly_api_data

class SimpleDeviceProxy:
    __slots__ = 'device_vendor', 'device_model'

class ShellyHttpDeviceProxy(SimpleDeviceProxy):
    __slots__ = 'uri_host', 'uri_path', 'uri_query'
    def __init__(self, host):
        self.uri_host = host
        self.uri_path = '/rpc/' + 'Shelly.getDeviceInfo'
        self.uri_query = ''

        #consider building LUTs for valid operations etc
        #based on getconfig
    def do_rpc(self) ->str:
        url = 'http://' + self.uri_host + self.uri_path + self.uri_query
        print("url={}".format(url))
        try:
            res = builtin_request.urlopen(url)
        except Exception as e:
            print(e)
            raise e

        ret = []
        for line in res:
            ret.append(line)
        assert len(ret) == 1


        doc = json.loads(ret[0])
        #print("parsed: {}".format(str(doc)))
        return doc

    def getDeviceInfo(self):
        self.uri_path = 'Shelly.getDeviceInfo'
        return self.do_rpc()

    def kvsSet(self, key, val):
        self.uri_path = '/rpc/KVS.Set'
        self.uri_query = '?key="{}"&value="{}"'.format(key, val)
        return self.do_rpc()

    def kvsGet(self, key) -> str:
        self.uri_path = '/rpc/KVS.Get'
        self.uri_query = '?key="{}"'.format(key)
        return self.do_rpc()

    def kvsList(self, filter=None):
        self.uri_path = '/rpc/KVS.List'
        if filter != None:
            assert type(filter) == str
            self.uri_query = '?match={}'.format(filter)
        else:
            self.uri_query = ''
        return self.do_rpc()
    
    def kvsDelete(self,keystr):
        assert type(keystr) == str
        self.uri_path = '/rpc/KVS.Delete'
        self.uri_query = '?key="{}"'.format(keystr)
        return self.do_rpc()
    
    def getInputStatus(self,input_id : int):
        assert type(input_id) == int
        self.uri_path = '/rpc/Input.GetStatus'
        self.uri_query = '?id={}'.format(input_id)
        return self.do_rpc()
    def getInputConfig(self, input_id : int):
        assert type(input_id) == int
        self.uri_path = '/rpc/Input.GetConfig'
        self.uri_query = '?id={}'.format(input_id)
        return self.do_rpc()
    def setInputConfig(self, input_id : int, jsonconf : str):
        """Set config, returns whether a restart is required """
        assert type(input_id) == int and type(jsonconf) == str
        self.uri_path = '/rpc/Input.SetConfig'
        self.uri_query = '?id={}&config={}'.format(input_id, jsonconf)
        return self.do_rpc()
    def resetInputCounters(self, input_id:int, counterlist):
        self.uri_path = 'Input.ResetCounters'
        self.uri_query = '?id={}&type={}'.format(input_id, counterlist)
        return self.do_rpc()
    def triggerInput(self):
        pass
    def checkInputExpression(self, exprjs : str, inputlist):
        """Take an expression with a var, for each input evel"""
        assert type(exprjs) == str
        self.uri_path = '/rpc/Input.CheckExpression'
        self.uri_query = '?expr="{}"&inputs={}'.format(exprjs, inputlist)
        return self.do_rpc()
    def getSwitchStatus(self,switch_id):
        assert type(switch_id) == int
        self.uri_path = '/rpc/Switch.GetStatus'
        self.uri_query = '?id={}'.format(switch_id)
        return self.do_rpc()

    def setRelay(self,switch_id,val,timer_s=None):
        assert type(switch_id) == int and val in (True,False)
        uri_output = 'on' if val==True else 'off'
        self.uri_path = '/relay/{}'.format(switch_id)
        self.uri_query = '?turn={}'.format(uri_output)
        if timer_s != None:
            assert type(timer_s) == int
            self.uri_query += '&timer={}'.format(timer_s)
        return self.do_rpc()
    
    def toggleRelay(self, switch_id):
        assert type(switch_id) == int
        self.uri_path = '/relay/{}'.format(switch_id)
        self.uri_query = '?turn=toggle'
        return self.do_rpc()
        
    def getSystemStatus(self):
        self.uri_path = '/rpc/Sys.GetStatus'
        self.uri_query = ''
        return self.do_rpc()

    def getSystemConfig(self):
        self.uri_path = '/rpc/Sys.GetConfig'
        self.uri_query =''
        return self.do_rpc()

    # Batch of untested new stuff
    def getScriptConfig(self, script_id : int):
        assert type(script_id) == int
        self.uri_path = '/rpc/Script.GetConfig'
        self.uri_query = '?id={}'.format(script_id)
        return self.do_rpc()
    def setScriptConfig(self, script_id : int, jsonconf : str):
        assert type(script_id) == int
        assert type(jsonconf) == str
        self.uri_path = '/rpc/Script.SetConfig'
        self.uri_query = '?id={}&config={}'.format(script_id,jsonconf)  
        return self.do_rpc()                            
    def getScriptStatus(self, script_id : int):
        assert type(script_id) == int
        self.uri_path = '/rpc/Script.GetStatus'
        self.uri_query = '?id={}'.format(script_id)
        return self.do_rpc()
    def listScripts(self):
        self.uri_path = '/rpc/Script.List'
        self.uri_query = ''
        #TODO This returns a variable len array, not handled
        return self.do_rpc()
    def createScript(self, script_name : str):
        """ Make a new script, the script id will be returned """
        self.uri_path = '/rpc/Script.Create'
        self.uri_query = '?name="{}"'
        return self.do_rpc()
    def deleteScript(self, script_id : int):
        assert type(script_id) == int
        self.uri_path = 'rpc/Script.Delete'
        self.uri_query = '?id={}'.format(script_id)
        pass
    def startScript(self, script_id : int, code : str):
        assert type(script_id) == int
        self.uri_path = '/rpc/Script.Start'
        self.uri_query = '?id={}'.format(script_id)
        return self.do_rpc()
    def stopScript(self, script_id : int):
        assert type(script_id) == int
        self.uri_path = '/rpc/Script.Stop'
        self.uri_query = '?id={}'.format(script_id)
        return self.do_rps()
    def putScriptCode(self, script_id : int, code : str):
        assert type(script_id) == int
        assert type(code) == str
        self.uri_path = '/rpc/Script.PutCode'
        self.uri_query = '?id={}&code="{}"'.format(script_id, code)
        return self.do_rpc()
    def getScriptCode(self, script_id : int):
        self.uri_path = 'rpc/Script.GetCode'
        self.uri_query = '?id={}'.format(script_id)
        return self.do_rpc()
    def evalScript(self):
        self.uri_path = '/rpc/Script.Eval'
        self.uri_query = ''
        return self.do_rpc()
    def setEMConfig(self, id : int, jsonconf : str):
        self.uri_path = '/EM.SetConfig'
        self.uri_query = '?id={}&config={}'.format(id, jsonconf)
        return self.do_rpc()
    def getRMConfig(self, id : int):
        self.uri_path = '/EM.GetConfig'
        self.uri_query = '?id={}'.format(id)
        return self.do_rpc()
    def getEMStatus(self, id : int):
        self.uri_path = '/rpc/EM.GetStatus'
        self.uri_query = '?id={}'.format(id)
        return self.do_rpc()


if __name__ == "__main__":
    """Poke around with device on 192.168.0.32"""
    x = ShellyHttpDeviceProxy('192.168.0.32')
    j = x.kvsSet("k1", "1")
    print(j)
    j = x.kvsGet("k1")
    print(j)

    v = x.getInputStatus(0)
    print(v)
    v = x.getInputStatus(1)
    print(v)

    v = x.setRelay(0,False)
    print(v)
    v = x.getSwitchStatus(0)
    print(v)
    v = x.toggleRelay(0)
    print(v)
    v = x.getSwitchStatus(0)
    print(v)
    v = x.getSwitchStatus(1)
    print(v)
    v = x.getSystemStatus()
    print(json.dumps(v,indent=4))
    v = x.getSystemConfig()
    print(v)    
    v = x.kvsList('*')
    print(json.dumps(v,indent=4))
