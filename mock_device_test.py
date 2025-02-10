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

import json
import os
import shelly_client

def test_toggle_all(client):
    for i in (0,1,2,3):
        res = client.setRelay(i, False)
        assert 'error' not in res
        print(res)

    for i in (0,1,2,3):
        res = client.getSwitchStatus(i)
        assert 'error' not in res
        print(res)

    for i in (0,1,2,3):
        res = client.setRelay(i, True)
        assert 'error' not in res
        print(res)

    for i in (0,1,2,3):
        res = client.getSwitchStatus(i)
        assert 'error' not in res
        print(res)

def test_kvs_getset(client):
    for i in range(10):
        res = client.kvsSet(str(i), str(i*i))
        assert 'error' not in res
    for i in range(10):
        res = client.kvsGet(str(i))
        assert 'error' not in res
        val = res['value']        
        assert int(val) == i*i

if __name__ == "__main__":
    HOST = os.getenv("DEVICE_TEST_PORT","127.0.0.1")

    client = shelly_client.ShellyHttpDeviceProxy(HOST)

    test_toggle_all(client)
    test_kvs_getset(client)
    print("Made it to end without an assertion error... PASS")






