"""
Mocks that represent shop devices to begin standing up an end-end test network
"""

import json
import threading
import time
import urllib
import urllib.request
import urllib.error
import urllib.parse
import os


class NetworkTimeout(BaseException):
    """network timeout during comms with external node"""

    __slots__ = "what"

    def __init__(self, w=""):
        self.what = w

    def __repr__(self):
        return "NetworkTimeout: {}".format(self.what)


class MockTelemetryEmitter:
    """Sends synthetic data on an interval"""

    runLoop = True

    __slots__ = (
        "device_type",
        "device_model",
        "firmware_ver",
        "protocol_ver",
        "endpoint_host",
        "endpoint_port",
    )

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
            "firmware_ver={}".format(self.firmware_ver),
        ]

        for name, met in cur.items():
            met = str(met)
            met = urllib.parse.quote_plus(bytes(met, "utf-8"))
            aspair = "metric.{}={}".format(name, str(met))
            pairs.append(aspair)
        return "&".join(pairs)

    def send_get_req(self):
        """Send a GET to the endpoint using the http node protocol"""

        qstr = self.get_uri_qry_pairs()
        uri = "http://{}:{}?{}".format(self.endpoint_host, self.endpoint_port, qstr)
        print("Sending: {}".format(uri))
        try:
            res = urllib.request.urlopen(uri)
        except urllib.error.URLError as e:
            print("got url error)")
            return {"error": str(e)}
        except Exception as e:
            print("Send request got: {}..\nrethrowing".format(str(e)))
            raise NetworkTimeout(str(e))

        # Just a single line status flag
        return json.loads([line for line in res][0])

    def loop(self, interval_s: int):
        while MockTelemetryEmitter.runLoop:
            time.sleep(interval_s)
            try:
                resp = self.send_get_req()
                print("Got response: {}".format(json.dumps(resp)))
            except KeyboardInterrupt as e:
                # Stop other thread loops
                MockTelemetryEmitter.runLoop = False
                raise e
            except Exception as e:
                # ignore this, assume network timeout for now
                print("caught {}.. trying again".format(str(e)))


class SingleChannelSensor(MockTelemetryEmitter):
    """Produces a single datum per timepoint"""

    __slots__ = "makevalue", "guid"

    def __init__(self, host, port, guid: str):
        super().__init__(host, port)
        self.device_type = "SingleChannelSensor"
        self.device_model = "PythonMock"
        self.makevalue = lambda: 1.0
        self.guid = guid

    def getcurrent(self):
        """Sample input and attach metadata including units"""
        return {
            "sensor_uuid": "DEADBEEF",  # UUID if a 1-Wire with ID in ROM
            "sensor_metric": "current",  # Thing being tracked
            "sensor_units": "amp",  # Thing's unit of measurement
            "sensor_poll": self.makevalue(),  # Make a value for this call
        }


class AirCompressor(MockTelemetryEmitter):
    """Something that approximates a 3.5HP compressor"""

    def __init__(self, host, port):
        super().__init__(host, port)
        self.device_type = "AirCompressor"
        self.device_model = "PythonMock"

    def getcurrent(self):
        return {
            "psi": 90,
            "tank_temp_f": 130,
            "head_temp_f": 200,
            "compressor_running": "no",
            "power_w": 0.1,
        }


class AirDryer(MockTelemetryEmitter):
    """Non-cycling refrigerated air dryer"""

    def __init__(self, host, port):
        super().__init__(host, port)
        self.device_type = "AirDryer"
        self.device_model = "PythonMockRefrigerated"

    def getcurrent(self):
        return {
            "dryer_running": "yes",
            "power_w": 250,
            "uptime_s": 60 * 60 * 5,
            "ambient_temp_f": 72,
            "in_temp_f": 105,
            "out_temp_f": 50,
            "condenser_air_temp_f": 130,
        }


class Heater(MockTelemetryEmitter):
    """Electric heater"""

    def __init__(self, host, port):
        super().__init__(host, port)
        self.device_type = "Heater"
        self.device_model = "MockElectricHeater"

    def getcurrent(self):
        return {"heater_running": "yes", "nominal_w": 500, "power_w": 520}


if __name__ == "__main__":
    # Mock endpoint default localhost:9050
    # Override with env vars
    EP_HOST = os.environ.get("EP_HOST", "127.0.0.1")
    EP_PORT = os.environ.get("EP_PORT", 9050)

    # Make configurable later
    BROADCAST_INTERVAL = 5

    def make_some_sensors(cnt: int):
        sensors = []
        for i in range(cnt):
            v = SingleChannelSensor(EP_HOST, EP_PORT, "Chan {}".format(i))
            sensors.append(v)
        return sensors

    # example devices
    tools = [
        Heater(EP_HOST, 9050),
        AirDryer(EP_HOST, 9050),
        AirCompressor(EP_HOST, 9050),
    ]

    simple_sensors = make_some_sensors(50)
    tools = tools + simple_sensors

    threads = []
    for tool in tools:
        fn = lambda i: tool.loop(i)
        t = threading.Thread(target=fn, args=[BROADCAST_INTERVAL])
        t.start()
        threads.append(t)

    # joins when loops exit due to keyboard interrupt
    for t in threads:
        t.join()
