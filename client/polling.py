# Copyright 2024 Jim Clampffer
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Quick, extensible, and generic utility to poll IOT devices with REST
APIs. This is primarily tested against "Shelly" brand smart switches
and relays.

Design considerations:
- self contained process, make scaleout easy.
"""


import argparse
import json
import time
import types
import urllib.request
import pickle

from data_manip import flatten_schema

"""
Network Model:
{shelly-style device}
    <-- HTTP polling request
        -- {this utility program}
            --> Direct to data collector
            --> Or rebroadcast/multicast as push

This module implements an executable and reusable utility functions for
polling hardware that exposes a REST API similar to Shelly IoT devices.
Their hardware is inexpensive, covers a lot of the stuff I thought I'd need
to make PCBs for, and has a fairly intuitive API.

Limitations:
    - Currently, one process per polling loop.
        - Works well in a distributed system.
            - Aggregator nodes can be implemented later.
        - Concurrency at the networking level is sidestepped for now.
"""


class PersistedRecordBuffer(object):
    """
    File-backed deque.
    """

    def __init__(self):
        pass


class Poller(object):
    __slots__ = "uri_authority", "client"

    def __init__(self, uri_authority: str):
        self.uri_authority = uri_authority

    def poll(self, timeout_s=10) -> dict:
        req = urllib.request.Request(
            self.uri_authority, headers={"Accept-Encoding": "identity"}
        )

        resp = urllib.request.urlopen(req)
        v = resp.readlines()
        v = [v.decode("utf-8") for v in v]
        v = "\n".join(v)
        o = json.loads(v)
        return o

    def loop(self, interval_s=1):
        pass


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--dbfile", type=str, default="poller_continued_1.db")

    p = Poller("http://192.168.1.165/rpc/Shelly.GetStatus")

    vals = []

    start = time.time()

    try:
        for i in range(3000):
            data = None
            try:
                data = p.poll()
            except Exception:
                # Best effort, need to tolerate some data loss due to
                # network issues and device firmware updates.
                print("error during polling")

            print("\n\n\n" + "*" * 80 + " " + str(i))
            print(data["sys"])
            print(flatten_schema(data))
            sample = {"poller_receive": time.time(), "status_data": data}
            vals.append(sample)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("KeyboardInterrupt, saving data")

    # Measure amortized time to fetch samples, not including exception handling.
    # Sleep is constant so the distance will always be more than the ideal interval
    delta_s = time.time() - start
    print("Amortized time to fetch samples: {:.2f} seconds".format(delta_s / len(vals)))

    # Keep things simple for now. Use arrow/pandas if reads and writes
    # bottleneck. Or use Apache ORC directly if parquet still stuffs
    # rowbatch metadata (min/max, nullcnt) in the footer. ORC is more
    # suitable for optimizations described in C-Store + "C-Store: 7
    # Years Later". Both allow metadata based pruning, but ORC allows
    # pruning of some of the actual metadata decode overhead.
    to_save = {
        "time": time.time(),
        "poller_uri": p.uri_authority,
        "samples": vals,
        "note": "First half is on the low pressure side of the regulator, which is why it caps out. I closed off the main tank, dumped the aux tank and dryer, then moved to the upstream side.",
    }

    with open(a.parse_args().dbfile, "wb") as f:
        pickle.dump(to_save, f)
    print("Saved {} samples to {}".format(len(vals), a.parse_args().dbfile))

    # sanity check
    with open(a.parse_args().dbfile, "rb") as f:
        loaded = pickle.load(f)
    print(
        "Loaded {} samples from {}".format(
            len(loaded["samples"]), a.parse_args().dbfile
        )
    )
