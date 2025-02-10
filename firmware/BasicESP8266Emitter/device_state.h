#ifndef DEMO_DEVICESTATE_H_
#define DEMO_DEVICESTATE_H_

#include <string.h>

/**
Convert a 4-bit nibble into corresponding hex char
*/
char nib2hex(uint8_t b) {
  static const char hexChars[] = {'0','1','2','3','4','5','6','7','8','9','A','B','C','D','E','F'};
  return hexChars[b & 0x0F];
}

/**
Need some way to identify this specific SOM, MAC address will do for now
*/
class DeviceUUID {
public:
  // Fetch MAC addr when wifi is up and running
  void load_dev_uuid() {
    uint8_t macbytes[6];
    WiFi.macAddress(macbytes);

    // Hex encode the raw bytes
    ::memset(addrString, 0, 2*6+1);
    for(int i=0;i<6;i++) {
      int base = i*2;
      uint8_t b = macbytes[i];
      // low nibble
      addrString[base] = nib2hex( b & 0xF);
      // high nibble   
      addrString[base+1] = nib2hex ((b>>4) & 0xF);
    }
  }

  // Return the hex encoded mac addr as a poor man's uuid
  const char *get_dev_uuid() {
    return addrString;
  }

private:
  // hex doubles len, plus a null char
  char addrString[6*2+1];
};

/**
Here's where the work is done to take stuff from GPIO and throw it into a URI qury string
*/
class PassthroughDevice {
public:
  // Place an ASCII formatted URI query in the specified buffer
  // note: snprintf will truncate if there isn't enough space in the buffer
  bool makeGetString(char *buf, int bufsz);
};

/**
Populate the string with input pin values
TODO: move to a .cc file if this is to be extended
*/
bool PassthroughDevice::makeGetString(char *buf, int bufsz) {
  // Single 10-bit ADC on ESP8266
  int a0 = analogRead(0);

  // Some digital inputs
  int d4 = digitalRead(4);
  int d5 = digitalRead(5);

  // memset not strictly required, but makes dangling ptr issues more obvious
  ::memset(buf, 0, 2048);

  // build up the query string for a HTTP GET
  const char *fmt = "device_type=ArduinoSimple8266&device_model=generic8266&a0=%d&d4=%d&d5=%d";
  snprintf(buf, 2048, fmt, a0, d4, d5);
  return true;
}

#endif // include guard
