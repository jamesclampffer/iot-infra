The data collector

A mechanism to collect and combine streams of timeseries data coming from each sensing device.

Concepts:
- Emitter: Embedded device that forwards hardware inputs on some interval.\
- Data Collector: listens on a (configurable) port for GET requests sent by 1 or more Emitters.

Note: DataCollector currently accepts asynchronous http requests while code in client sends them out and blocks on the response. These will most likely be combined client-side, and will be combined on the device firmware.

To testing mock emitters and endpoint using the default authority 'localhost:9050'
1) in terminal 1> python3 collector-endpoint.py
2) in terminal 2> python3 mock-emitters.py
3) Watch stdout