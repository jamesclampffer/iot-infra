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
#ifndef UDF_H_
#define UDF_H_

#include "stdint.h"

/// Interface provided to script interpreters or user-defined logic
struct AppSystemInterface {
    /// malloc()-like, used for resource tracking
    /// Memory allocated through here must be freed using returnMemory
    char* allocateMemory(int numbytes);

    /// free()-like, return heap memory starting at addr
    void returnMemory(char *addr);

    /// Read an input using same index as public API 
    bool readInputChannel(int idx);

    /// Read current output (switch/relay) channel value
    bool readOutputChannel(int idx);

    /// @brief Set output for specified relay.
    /// @todo  Task level IO masking (file tickets)
    bool writeOutputChannel(int idx, bool value);
private:
  friend class Device;
  friend class DeviceImpl;
};

#endif // include guard