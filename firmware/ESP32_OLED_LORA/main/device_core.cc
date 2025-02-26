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

#include <Arduino.h>  // for Serial, get this out of here

#include "config.h"
#include "device_core.h"
#include "emit.h"
#include "udf_impl.h"  // See if this can be reduced to udf.h

#include <algorithm>
#include <map>
#include <memory>
#include <string>
#include <string.h>

#include <freertos/FreeRTOS.h>
#include <freertos/semphr.h>
#include <freertos/task.h>

auto ms2ticks = [](int ms) -> TickType_t {
  if (ms == 0) return 0;
  return ms / portTICK_PERIOD_MS;
};

// Move this to a util header
namespace port {
void task_yield() {
  vTaskDelay(0);
}
void sleep(int ms) {
  vTaskDelay(ms2ticks(ms));
}
}

// another that belongs in a header
class Task {
public:
  using fn = void (*)(void*);

  Task(fn f, void* params = nullptr)
    : task(NULL), funcPtr(f), funcParam(params), error(false) {
    BaseType_t flag = xTaskCreate(f, "TaskTask", 1024 * 32 /*stacksz*/, params, tskIDLE_PRIORITY + 1, &task);
    if (pdPASS != flag) {
      //OOM
      error = true;
    }
  }

  ~Task() {}

  void join() {
    if (task != NULL) {
      vTaskDelete(task);
    }
  }

  bool taskFailed() {
    return task != NULL && !error;
  }

  Task(){};

private:
  TaskHandle_t task;
  fn funcPtr;
  void* funcParam;
  bool error;
};

// Might make more sense to implement the std::mutex interface. Then
// std::lock_guard would replace this.
struct MutexAdapter {
  MutexAdapter(SemaphoreHandle_t& sem)
    : mtx(sem) {
    xSemaphoreTake(mtx, portMAX_DELAY);
  }
  ~MutexAdapter() {
    xSemaphoreGive(mtx);
  }
private:
  MutexAdapter();
  SemaphoreHandle_t& mtx;
};

void systask_io(void*) {
  while (1) {
    //Serial.println("iotask");
    port::sleep(1000);
  }
}

void systask_emitter(void*) {
  static Emitter emitObj;  //move into DeviceImpl
  //emitObj.addEndpoint(const char *host, int port)
  emitObj.loop_enter(nullptr);
  Serial.println("\n\n loop returned - should not happen \n\n");
}

class DeviceImpl {
public:
  DeviceImpl()
    : appInterface(std::make_unique<AppSystemInterface>()) {
    stateLock = xSemaphoreCreateMutex();
  }
  ~DeviceImpl() {
    vSemaphoreDelete(stateLock);
  }

  void initAll() {
    auto guard = MutexAdapter(stateLock);
  }

  void spawnTasks() {
    auto guard = MutexAdapter(stateLock);
    //this->ioTask = std::make_unique<Task>(&systask_io, nullptr);
    this->emitterTask = std::make_unique<Task>(&systask_emitter, nullptr);
  }

  void yieldTime() {
    vTaskDelay(1);
  }
  AppSystemInterface& getAppInterface();

  std::unique_ptr<HttpResponse> sendGetRequest(URI& uri);
private:
  // take before mutating instance state
  SemaphoreHandle_t stateLock;
  
  // udf scripts share one interface - io mask is global
  std::unique_ptr<AppSystemInterface> appInterface;

  // uart output buffering
  std::unique_ptr<Task> ioTask;

  // loop over io and send requests to remote datacollector
  std::unique_ptr<Task> emitterTask;

  friend class Device;
};

AppSystemInterface& DeviceImpl::getAppInterface() {
  return *appInterface;
}

std::unique_ptr<HttpResponse> DeviceImpl::sendGetRequest(URI& uri) {
  // Call ESP Arduino lib here
}

Device::Device()
  : impl(std::make_unique<DeviceImpl>()) {
}

Device::~Device() {
}

void Device::initAll() {
  impl->initAll();
}

void Device::spawnTasks() {
  impl->spawnTasks();
}

AppSystemInterface& Device::getAppInterface() {
  return impl->getAppInterface();
}

std::unique_ptr<HttpResponse> Device::sendGetRequest(URI& uri) {
  return impl->sendGetRequest(uri);
}

void Device::yieldTime() {
  impl->yieldTime();
}