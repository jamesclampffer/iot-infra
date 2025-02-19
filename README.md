This project contains various software for automating things.

Problem statement:\
I have a workshop and I'd like to automate dependencies for certain pieces of equipment. 

Example use cases:\
Detect when a piece of equipment has been manually turned on -> power on/enable supporting equipment.
- If a CNC laser is running open air assist solenoid and turn on vent blower.
- If plasma table is on then also turn on the air dryer.

Track equpment state over time for health checks
- Trigger a warning as average load approaches a configurable duty cycle limit. This could then drive a visual warning and try to shed some load.
- Uptime based reminders for ordering consumables.


Initial scope:
- Implement lightweight client(s) that can run on a windows/linux node that interfaces with with network-connected embedded devices.
    - Devices may be off the shelf (e.g. "Shelly" switches) or make use of some custom hardware.
    - For now network comms aren't secured - not strictly required for my use case.
- Implement firmware that may run on embedded devices that expose an interface for remote IO.
    - Assume ESP32/ESP8266 + FreeRTOS platform

Directories:
- kvs: A http based key value store service
- client: client to send signals to embedded devices on the network
- datacollector: Infrastructure to bind an endpoint to a port, and then pipe incoming data to a pluggable backend. 


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



