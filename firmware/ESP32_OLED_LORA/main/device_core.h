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

#ifndef DEVICECORE_H_
#define DEVICECORE_H_
#include <memory>
#include "uri.h"

// GET request objects
class URI;
class HttpResponse;

// SDK headers
class AppSystemInterface;

/// Program/state to make the hardware act as a networked IO node.
class DeviceImpl;
class Device {
public:
  Device();
  ~Device();

  /// Where dynamic components can allocate resources
  /// @note The idea is that very little should happen in spawnTasks other than
  ///       task creation.
  void initAll();

  /// Spin up tasks/threads for services
  void spawnTasks();

  /// Provide a handle to the system interface intended for applications/scripts
  AppSystemInterface& getAppInterface();

  /// Give current thread a way to suspend itself (without including rtos stuff)
  void yieldTime();

  /// Sends request, use query params in uri
  /// Returns json
  std::unique_ptr<HttpResponse> sendGetRequest(URI& uri);

  /// pImpl to keep other c++ stuff out of the header
  std::unique_ptr<DeviceImpl> impl;
};

#endif  // include guard