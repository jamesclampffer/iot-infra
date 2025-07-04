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

import urllib.request
import urllib.parse
import json


class SimpleDeviceProxy:
    __slots__ = "device_vendor", "device_model"


class ShellyHttpDeviceProxy(SimpleDeviceProxy):
    """
    Interface for *unsecured* Shelly REST API
    Concepts (e.g. Component) map to the shelly docs.
    """

    __slots__ = "uri_host", "uri_path", "uri_query"

    def __init__(self, host):
        self.uri_host = host
        self.uri_path = "/rpc/" + "Shelly.getDeviceInfo"
        self.uri_query = ""

    def notImplemented(self, fname):
        """Generate a response for something not implemented yet"""
        print("info: {} not implemented")
        return json.dumps({"error": "not implemented"})

    def do_rpc(self) -> str:
        url = "http://" + self.uri_host + self.uri_path + "?" + self.uri_query
        print("url={}".format(url))

        req = urllib.request.Request(url, headers={
            'Accept-Encoding': 'utf-8, ascii'
        })

        try:
            res = urllib.request.urlopen(req)
        except Exception as e:
            print(e)
            raise e

        ret = [line for line in res]
        assert len(ret) == 1

        doc = json.loads(ret[0])
        return doc

    def getDeviceInfo(self):
        self.uri_path = "Shelly.getDeviceInfo"
        self.uri_query = ""
        return self.do_rpc()

    def kvsSet(self, key: str, val):
        """Set value on the device's KVS service"""
        self.uri_path = "/rpc/KVS.Set"
        key = urllib.parse.quote_plus(key)
        val = urllib.parse.quote_plus(val)
        self.uri_query = "key={}&value={}".format(key, val)
        return self.do_rpc()

    def kvsGet(self, key):
        """Set value from the device's KVS service"""
        self.uri_path = "/rpc/KVS.Get"
        key = urllib.parse.quote_plus(key)
        self.uri_query = "key={}".format(key)
        return self.do_rpc()

    def kvsList(self, filter=None):
        """Return set of {key,val} pairs where key matches filter pred"""
        self.uri_path = "/rpc/KVS.List"
        if filter != None:
            assert type(filter) == str
            self.uri_query = "match={}".format(filter)
        else:
            self.uri_query = ""
        return self.do_rpc()

    def kvsDelete(self, keystr: str):
        """Delete value from the device's KVS service"""
        self.uri_path = "/rpc/KVS.Delete"
        self.uri_query = 'key="{}"'.format(keystr)
        return self.do_rpc()

    def getInputStatus(self, input_id: int):
        """Get the state of an input e.g. on/off"""
        self.uri_path = "/rpc/Input.GetStatus"
        self.uri_query = "id={}".format(input_id)
        return self.do_rpc()

    def getInputConfig(self, input_id: int):
        """Het config for a specific device input"""
        self.uri_path = "/rpc/Input.GetConfig"
        self.uri_query = "id={}".format(input_id)
        return self.do_rpc()

    def setInputConfig(self, input_id: int, jsonconf: str):
        """Set config, returns whether a restart is required"""
        self.uri_path = "/rpc/Input.SetConfig"
        self.uri_query = "id={}&config={}".format(input_id, jsonconf)
        return self.do_rpc()

    def resetInputCounters(self, input_id: int, counterlist):
        # self.uri_path = 'Input.ResetCounters'
        # self.uri_query = 'id={}&type={}'.format(input_id, counterlist)
        # return self.do_rpc()
        return self.notImplemented("ResetInputCounters")

    def triggerInput(self):
        return self.notImplemented("TriggerInput")

    def checkInputExpression(self, exprjs: str, inputlist):
        """Take an expression with a var, for each input evel"""
        self.uri_path = "/rpc/Input.CheckExpression"
        self.uri_query = 'expr="{}"&inputs={}'.format(exprjs, inputlist)
        return self.do_rpc()

    def getSwitchStatus(self, switch_id: int):
        """Fetch status of an output relay"""
        self.uri_path = "/rpc/Switch.GetStatus"
        self.uri_query = "id={}".format(switch_id)
        return self.do_rpc()

    def setRelay(self, switch_id, val, timer_s=None):
        """Set output relay on or off"""
        uri_output = "on" if val == True else "off"
        self.uri_path = "/relay/{}".format(switch_id)
        self.uri_query = "turn={}".format(uri_output)
        if timer_s != None:
            assert type(timer_s) == int
            self.uri_query += "&timer={}".format(timer_s)
        return self.do_rpc()

    def toggleRelay(self, switch_id):
        """Flip the output state"""
        self.uri_path = "/relay/{}".format(switch_id)
        self.uri_query = "turn=toggle"
        return self.do_rpc()

    def getSystemStatus(self):
        """Fetch info about the remote device"""
        self.uri_path = "/rpc/Sys.GetStatus"
        self.uri_query = ""
        return self.do_rpc()

    def getSystemConfig(self):
        self.uri_path = "/rpc/Sys.GetConfig"
        self.uri_query = ""
        return self.do_rpc()

    def getScriptConfig(self, script_id: int):
        """Configuration for a device-hosted script"""
        self.uri_path = "/rpc/Script.GetConfig"
        self.uri_query = "id={}".format(script_id)
        return self.do_rpc()

    def setScriptConfig(self, script_id: int, jsonconf: str):
        """Configuration for a device-hosted script"""
        self.uri_path = "/rpc/Script.SetConfig"
        self.uri_query = "id={}&config={}".format(script_id, jsonconf)
        return self.do_rpc()

    def getScriptStatus(self, script_id: int):
        """Fetch status of a script running on the device"""
        self.uri_path = "/rpc/Script.GetStatus"
        self.uri_query = "id={}".format(script_id)
        return self.do_rpc()

    def listScripts(self):
        """Fetch scripts running on the device"""
        self.uri_path = "/rpc/Script.List"
        self.uri_query = ""
        # TODO This returns a variable len array, json.loads might choke
        return self.do_rpc()

    def createScript(self, script_name: str):
        """Make a new script, the script id will be returned"""
        self.uri_path = "/rpc/Script.Create"
        self.uri_query = 'name="{}"'.format(script_name)
        return self.do_rpc()

    def deleteScript(self, script_id: int):
        self.uri_path = "rpc/Script.Delete"
        self.uri_query = "id={}".format(script_id)
        pass

    def startScript(self, script_id: int, code: str):
        # self.uri_path = '/rpc/Script.Start'
        # self.uri_query = 'id={}'.format(script_id)
        # return self.do_rpc()
        return self.notImplemented("StartScript")

    def stopScript(self, script_id: int):
        self.uri_path = "/rpc/Script.Stop"
        self.uri_query = "id={}".format(script_id)
        return self.do_rps()

    def putScriptCode(self, script_id: int, code: str):
        self.uri_path = "/rpc/Script.PutCode"
        self.uri_query = 'id={}&code="{}"'.format(script_id, code)
        return self.do_rpc()

    def getScriptCode(self, script_id: int):
        self.uri_path = "rpc/Script.GetCode"
        self.uri_query = "id={}".format(script_id)
        return self.do_rpc()

    def evalScript(self):
        self.uri_path = "/rpc/Script.Eval"
        self.uri_query = ""
        return self.do_rpc()

    def setEMConfig(self, id: int, jsonconf: str):
        self.uri_path = "/EM.SetConfig"
        self.uri_query = "id={}&config={}".format(id, jsonconf)
        return self.do_rpc()

    def getEMConfig(self, id: int):
        self.uri_path = "/EM.GetConfig"
        self.uri_query = "id={}".format(id)
        return self.do_rpc()

    def getEMStatus(self, id: int):
        self.uri_path = "/rpc/EM.GetStatus"
        self.uri_query = "id={}".format(id)
        return self.do_rpc()


if __name__ == "__main__":
    prox = ShellyHttpDeviceProxy('192.168.1.165')
    info = prox.getInputConfig(1)
    print(info)
