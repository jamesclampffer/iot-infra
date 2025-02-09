This project contains various software for automating things.

Objectives:
- lightweight client that can run on a windows/linux compute node
- develop esp32 firmware to facilitate implementing hardware that is
  a little closer to PLC territory.

Client utils:
- Python proxy for "Shelly" brand devices over http (unencrypted)
  - My use case drops everything onto a secure LAN and encryption isn't
    strictly required yet.

Devices:
- A handful of "Shelly" brand IOT products to start doing 120VAC IO
- Mock devices (see mock-emitters.py)
- Some bespoke ESP32-based interface boards


To testing mock emitters and endpoint using the default authority 'localhost:9050'
1) in terminal 1> python3 collector-endpoint.py
2) in terminal 2> python3 mock-emitters.py
3) Watch stdout


KVS Service
- Simple {string:string} map available via HTTP
  - kvs_service: the server
  - kvs_client: client API
  - kvs_test: smoke test, start kvs_service prior to running



