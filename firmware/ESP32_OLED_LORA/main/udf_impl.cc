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
#include "udf_impl.h"

#include "config.h"
#include "string.h"

#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>

AppIOMask::AppIOMask() : ch_read_mask(0xFF), ch_write_mask(0xFF) {
  // Enable 8 bits of digital IO, reduce based on config.h
}

char* AppSystemInterface::allocateMemory(int numbytes) {
    static_assert(sizeof(char) == 1);
    // forward to malloc to get the interface working for now
    char *p = (char*)malloc(numbytes);
    memset(p, 0, numbytes);
}

void AppSystemInterface::returnMemory(char *addr) {
    // See this->allocateMemory()
    free(addr);
}

// Placeholder until masks are mapped to tasks
static AppIOMask& getIOMask() {
  static AppIOMask mask;
  return mask;
}

bool AppSystemInterface::readInputChannel(int idx) {
  auto mask = getIOMask();
  if (mask.checkInputEnabled(idx)) {
    #pragma message("Add digital IO support");
    return true;
  }
  return false;
}

bool AppSystemInterface::readOutputChannel(int idx) {
  auto mask = getIOMask();
  if (mask.checkOutputEnabled(idx)) {
    //do IO
    return true;
  }
  return false;
}

bool AppSystemInterface::writeOutputChannel(int idx, bool value) {
  auto mask = getIOMask();
  if (mask.checkOutputEnabled(idx)) {
    //do IO
    return true;
  }
  return false;
}