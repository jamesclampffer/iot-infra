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
#ifndef EMIT_H_
#define EMIT_H_

#include <memory>

struct EmitterImpl;

/// Transmit sensor info periodically
struct Emitter {
  Emitter();
  ~Emitter();

  /// Adding >1 endpoint allows HA failback, if implemented
  void addEndpoint(const char *host, int port);

  /// Run this from a task
  void loop_enter(void *);

  std::unique_ptr<EmitterImpl> impl;
};

#endif  // include guard