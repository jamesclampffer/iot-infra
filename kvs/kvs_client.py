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
import urllib.error
import urllib.parse
import urllib.request


class HttpKVSClient:
    """Makes http requests to kvs service"""

    __slots__ = "uri_host", "uri_path", "uri_query"

    def __init__(self, host):
        self.uri_host = host
        self.uri_path = ""
        self.uri_query = ""

    def notImplemented(self, fname):
        """Generate a response for something not implemented yet"""
        return {"error": "not implemented"}

    def do_rpc(self) -> str:
        """Put together a URI and load it"""
        url = "http://" + self.uri_host + self.uri_path + "?" + self.uri_query
        try:
            res = urllib.request.urlopen(url)
        except urllib.error.HTTPError as e:
            return {"error": "Resource not found (key missing)"}
        except Exception as e:
            print("warn: unexpected exception: {}".format(str(e)))
            return {"error": "unexpected exception"}

        # Expext single line json value
        ret = json.loads([line for line in res][0])

    def getVal(self, key: str) -> object:
        """Get a value"""
        self.uri_path = "/get"
        key = urllib.parse.quote_plus(key)
        self.uri_query = "key={}".format(key)
        return self.do_rpc()

    def setVal(self, key: str, val: str) -> object:
        """Set a value"""
        self.uri_path = "/set"
        key = urllib.parse.quote_plus(key)
        val = urllib.parse.quote_plus(val)
        self.uri_query = "key={}&value={}".format(key, val)
        return self.do_rpc()

    def delVal(self, key: str) -> object:
        """Delete a value"""
        self.uri_path = "/delete"
        key = urllib.parse.quote_plus(key)
        self.uri_query = "key={}".format(key)
        return self.do_rpc()

    def listAll(self, keyregex: str = ""):
        """Return all values in table.
        Server doesn't support filter yet
        """
        if keyregex != "":
            print('warn: ignoring listAll regex "{}"'.format(keyregex))
        self.uri_path = "/listall"
        encodedexp = urllib.parse.quote_plus(keyregex)
        self.uri_query = "filter={}".format(encodedexp)
        return self.do_rpc()
