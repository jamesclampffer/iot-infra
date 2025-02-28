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

import kvs_client
import os
import urllib.error
import urllib.parse
import urllib.request
import json


def test_clear_all(client):
    contents = client.listAll()
    if contents == None:
        return
    startCount = len(contents)
    for key in contents:
        resp = client.delVal(key)
        assert "lastversion" in resp

    contents = client.listAll()
    endCount = len(contents)
    assert endCount == 0


def test_value_version(client):
    """Hammer a single key"""
    for i in range(1000):
        client.setVal("version_test_key", str(i + 1))
    resp = client.getVal("version_test_key")
    assert int(resp["version"]) == 999
    assert int(resp["value"]) == 1000


def test_query_val_escape(client):
    TEST_KEY = "escape_test_key"
    TEST_VAL = 'here are "some" embedded quotes & stuff'

    client.setVal(TEST_KEY, TEST_VAL)
    resp = client.getVal(TEST_KEY)
    assert resp["value"] == TEST_VAL
    resp = client.delVal(TEST_KEY)
    assert "lastversion" in resp


if __name__ == "__main__":
    HOST = os.getenv("KVS_HOST", "127.0.0.1")
    PORT = os.getenv("KVS_PORT", 9090)
    PORT = int(PORT)

    client = kvs_client.HttpKVSClient("127.0.0.1:9090")

    # empty current contents to get a clean slate
    test_clear_all(client)
    test_value_version(client)
    test_query_val_escape(client)

    print("Got here without breaking an assert - PASS")
