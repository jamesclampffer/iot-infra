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

#include "config.h"
#include "device_core.h"

Device device;
void setup() {
  Serial.begin(115200);

  // Allocate resources and set up hardware
  device.initAll();
  
  // Launch RTOS tasks for components/services
  device.spawnTasks();

#if 1
  // sanity check on uri::addQueryPair
  URI uri("127.0.0.1");
  char buf[512];
  uri.addQryPair("hello","world");
  uri.addQryPair("foo","bar");
  int num = uri.writeIntoBuffer(buf,512);
  Serial.printf("URI is %d bytes: %s", num, buf);
#endif
}

void loop() {
  // Don't busy loop, yield back to scheduler
  device.yieldTime();  
}
