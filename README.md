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

