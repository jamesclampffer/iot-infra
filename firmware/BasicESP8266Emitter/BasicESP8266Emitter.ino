/**
  Derived from BasicHTTPClient for a WEMOS D1 mini esp8266 board
  Original BasicHTTPClient Created on: 24.05.2015

  FIXME: Add proper attribution for IP this is based on.
         There wasn't a license in the example file - it's unclear at a glance who owns the IP. 
*/

#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <ESP8266WiFiMulti.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

/**
  NOTE: Add a "creds.h" file in the same source directory with the wifi AP ssid and
        password to make this work. creds.h is in the .gitignore, not foolproof but keeps
        this simple.

                Example: creds.h
----------------------------------------------------------
#ifndef DEMO_CREDS_H_
#define DEMO_CREDS_H_

// Fill in your network info here!
const char *ap_ssid = "MyWifiSSID";
const char *ap_pass = "MyWifiPassword";
#endif // include guard
----------------------------------------------------------
*/
#include "creds.h"

// snprintf buffers
char qry_param_buf[2096];
char get_req_buf[2096];

// Inline the whole file for now
#include "device_state.h"

ESP8266WiFiMulti WiFiMulti;

// Things added on top of BasicHttpClient example, see device_state.h
PassthroughDevice dev;
DeviceUUID uuidgen;


void setup() {
  Serial.begin(115200);
  Serial.println();

  // Wait a second before spamming uart0
  for (uint8_t t = 4; t > 0; t--) {
    Serial.printf("[SETUP] WAIT %d...\n", t);
    Serial.flush();
    delay(1000);
  }

  // Client only
  WiFi.mode(WIFI_STA);
  WiFiMulti.addAP(ap_ssid, ap_pass);

  // Grab mac addr to use as device ID
  uuidgen.load_dev_uuid();
}

void loop() {
  // wait for WiFi connection
  if ((WiFiMulti.run() == WL_CONNECTED)) {
    
    WiFiClient client;
    HTTPClient http;

    // Fill qry_param_buf with the HTTP GET query
    dev.makeGetString(qry_param_buf, 2048);

    ::memset(get_req_buf, 0, 2048);
    snprintf(get_req_buf, 2048, "http://192.168.1.21:9050/?uuid=%s&heapfree=%d&uptime=%d&%s", uuidgen.get_dev_uuid(), ESP.getFreeHeap(), ESP.getFreeHeap(), qry_param_buf);

    Serial.print("[HTTP] begin...\n");
    if (http.begin(client, get_req_buf)) {  // HTTP


      Serial.print("[HTTP] GET...\n");
      // start connection and send HTTP header
      int httpCode = http.GET();

      // httpCode will be negative on error
      if (httpCode > 0) {
        // HTTP header has been send and Server response header has been handled
        Serial.printf("[HTTP] GET... code: %d\n", httpCode);

        // file found at server
        if (httpCode == HTTP_CODE_OK || httpCode == HTTP_CODE_MOVED_PERMANENTLY) {
          String payload = http.getString();
          Serial.println(payload);
        }
      } else {
        Serial.printf("[HTTP] GET... failed, error: %s\n", http.errorToString(httpCode).c_str());
      }

      http.end();
    } else {
      Serial.println("[HTTP] Unable to connect");
    }
  }

  delay(5000);
}
