A place for firmware intended to run on ESP32/ESP8266 SOMs

Emitter Implementations
- SimpleEmitter


SimpleEmitter:
An emitter that's, well, very simple. Just enough there to push some input pin values to a CollectorEndpoint
- Minimize how long it takes to get something running by building in the Arduino IDE.
  - No config to speak of, just consts in the code.
- Not optimized. Mostly a bunch of calls the ESP/Arduino APIs, so not a ton to be clever with.
  - Still plenty of headroom on an ESP8266, and makes the code more beginner friendly
- WIFI client device only - no range extention.

