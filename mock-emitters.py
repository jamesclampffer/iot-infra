"""
Mocks that represent shop devices to begin standing up an end-end test network
"""

import time
import urllib
import urllib.parse
import json
from enum import IntEnum
import os
import urllib.request as builtin_open
import urllib.error
import threading


class NetworkTimeout(BaseException):
    __slots__ = 'what'
    def __init__(self,w=""):
        self.what = w
    def __repr__(self):
        return "NetworkTimeout: {}".format(self.what)

class MockTelemetryEmitter:
    __slots__ = 'device_type', 'device_model', 'firmware_ver', 'protocol_ver', \
            'endpoint_host', 'endpoint_port'
    def __init__(self, host, port):
        self.device_type = None
        self.device_model = None
        self.protocol_ver = -1
        self.firmware_ver = -1
        self.endpoint_host = host
        self.endpoint_port = port

    def get_uri_qry_pairs(self):
        cur = self.getcurrent()
        pairs = [
            "device_type={}".format(self.device_type),
            "device_model={}".format(self.device_model),
            "protocol_ver={}".format(self.protocol_ver),
            "firmware_ver={}".format(self.firmware_ver)
        ]

        for name, met in cur.items():
            met = str(met)
            met = urllib.parse.quote_plus(bytes(met, 'utf-8'))
            aspair = "metric.{}={}".format(name, str(met))
            pairs.append(aspair)
        return '&'.join(pairs)

    def send_get_req(self):
        qstr = self.get_uri_qry_pairs()
        uri = 'http://{}:{}?{}'.format(self.endpoint_host, self.endpoint_port, qstr)
        print("Sending: {}".format(uri))
        try:
            res = builtin_open.urlopen(uri)
        except urllib.error.URLError as e:
            print("got url error)")
            return {}
        except Exception as e:
            print("Send request got: {}..\nrethrowing".format(str(e)))
            raise NetworkTimeout(str(e))

        # shelly api uses same logic, maybe factor out
        ret = [line for line in res]
        doc = json.loads(ret[0])
        return doc

    def loop(self, interval_s:int):
        while True:
            try:
                resp = self.send_get_req()
                print("Got response: {}".format(json.dumps(resp)))
                time.sleep(interval_s)
            except KeyboardInterrupt as e:
                print("exiting {}: {}".format(str(self),str(e)))
                break
            except Exception as e:
                # ignore this, assume network timeout for now
                print("caught {}.. trying again".format(str(e)))
        print('exiting loop fn')

class AirCompressor(MockTelemetryEmitter):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.device_type = 'AirCompressor'
        self.device_model = 'PythonMock'
    def getcurrent(self):
        return {
            'psi': 90,
            'tank_temp_f' : 130,
            'head_temp_f' : 200,
            'compressor_running' : 'no',
            'power_w': 0.1
        }

class AirDryer(MockTelemetryEmitter):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.device_type = 'AirDryer'
        self.device_model = 'PythonMockRefrigerated'
    def getcurrent(self):
        return {
            'dryer_running' : 'yes',
            'power_w' : 250,
            'uptime_s' : 60*60*5,
            'ambient_temp_f' : 72,
            'in_temp_f' : 105,
            'out_temp_f' : 50,
            'condenser_air_temp_f': 130    
        }

class Heater(MockTelemetryEmitter):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.device_type = 'Heater'
        self.device_model = 'MockElectricHeater'

    def getcurrent(self):
        return {
            'heater_running':'yes',
            'nominal_w':500,
            'power_w':520
        }

if __name__ == '__main__':
    # Mock endpoint default localhost:9050
    # Override with env vars
    EP_HOST = os.environ.get('EP_HOST', 'localhost')
    EP_PORT = os.environ.get('EP_PORT', 9050)
    EP_PORT = int(EP_PORT)

    # Make configurable later
    BROADCAST_INTERVAL = 5

    #some example devices
    tools = [Heater('localhost',9050), AirDryer('localhost',9050), AirCompressor('localhost',9050)]
    for tool in tools:
        print(tool)

    threads = []
    for tool in tools:
        fn = lambda i: tool.loop(i) 
        t = threading.Thread(target=fn, args=[BROADCAST_INTERVAL])  
        t.run()
        threads.append(t)


    time.sleep(5 * 60)


    # join when loops exit due to keyboard interrupt
    for t in threads:
        t.join()




