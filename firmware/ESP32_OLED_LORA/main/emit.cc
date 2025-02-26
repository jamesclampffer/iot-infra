/*
Copyright 2025 Jim Clampffer

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

#include "emit.h"

#include <Arduino.h>  // for Serial.x functions
#include <WiFi.h>
#include <WiFiMulti.h>
#include <HTTPClient.h>

#include "creds.h"
/*
Add a file like this in the same directory with wifi creds, this file is in the .gitignore
todo: read this stuff from eeprom
#ifndef CREDS_H_
#define CREDS_H_

const char *WIFI_SSID = "";
const char *WIFI_PASS = "";

#endif // include guard
*/

#include <utility>
#include <map>
#include <memory.h>
#include <set>
#include <string>
#include <string.h>

class EmitterImpl {
public:
  EmitterImpl();
  ~EmitterImpl();

  /// See header
  void addEndpoint(const char *host, int port);
  void loop_enter(void *param);

  /// Select an authority from the available set
  std::string getEndpointAuthority();

  /// One or more URI authority segments
  std::set<std::string> endpoints;
};

EmitterImpl::EmitterImpl() {}
EmitterImpl::~EmitterImpl() {}


void EmitterImpl::addEndpoint(const char *host, int port) {
  char buf[256];
  memset(buf, 0, 256);
  int len = snprintf(buf, 256, "%s:%d", host, port);
  endpoints.insert(buf);
}

std::string EmitterImpl::getEndpointAuthority() {
  /// Tree will be lexographically sorted, and this grabs the lowest
  return *endpoints.begin();
}

void EmitterImpl::loop_enter(void *params) {

  // fixme: Make a thread safe wrapper over radio io and expose to other components
  WiFiMulti wifi;
  wifi.addAP(WIFI_SSID, WIFI_PASS);

  bool stop = false;  // Placeholder,
  while (!stop) {

    // factor this out, duplicates device_core.cc ports:: functions
    auto sleep_ms = [](int ms) -> int {
      int ticks = ms / portTICK_PERIOD_MS;
      vTaskDelay(ticks);
    };

    // skip if not connected, add endpoint failover here
    if (wifi.run() == WL_CONNECTED) {
      HTTPClient conn;

      std::string qryUrl = "http://192.168.1.157:9050/?foo=bar";

      conn.begin(qryUrl.c_str());
      int respCode = conn.GET();
      Serial.printf("Got response code: %d\n", respCode);
      if (respCode == HTTP_CODE_OK) {
        String resp = conn.getString();
        Serial.println(resp);
      }
      conn.end();
    } else {
      sleep_ms(2000);
    }
    // fixme: make configurable
    sleep_ms(1000);
  }
}

// Only forwarding calls below here!
Emitter::Emitter()
  : impl(std::make_unique<EmitterImpl>()) {}

Emitter::~Emitter() {}

void Emitter::addEndpoint(const char *host, int port) {
  impl->addEndpoint(host, port);
}

void Emitter::loop_enter(void *p) {
  impl->loop_enter(p);
}