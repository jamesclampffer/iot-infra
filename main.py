
import urllib.request as builtin_request
import json

class StatelessDeviceProxy:
    __slots__ = 

class ShellyHttpDeviceProxy:
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

    def getInputStatus(self,input_id):
        assert type(input_id) == int
        self.uri_path = '/rpc/Input.GetStatus'
        self.uri_query = '?id={}'.format(input_id)
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
        

if __name__ == "__main__":
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

    
