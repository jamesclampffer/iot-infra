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

#include "uri.h"

#include <string.h>

URI::URI(const char* authority, const char* path)
    : authority(authority), path(path) {}

URI::~URI() {}
const std::string& URI::getAuthority() const { return authority; }
const std::string& URI::getPath() const { return path; }

/// Add a key=value to the qu
void URI::addQryPair(const char* key, const char* val) {
  if (key == nullptr || val == nullptr) return;
  qryParams[key] = val;
}

/// Delegate to char* version
void URI::addQryPair(const std::string& key, const std::string& val) {
  return addQryPair(key.c_str(), val.c_str());
}

int URI::writeIntoBuffer(char* buf, int bufsz) {
  static_assert(sizeof(char)==1);
  char* start = buf;
  char* current = buf;
  char* end = buf + bufsz;
  auto getRemaining = [&current, &end]() {
    return end - current;
  };
  memset(buf, 0, bufsz);

  int len = snprintf(current, getRemaining(), "%s%s?", authority.c_str(), path.c_str());
  current += len;

  for (auto it : qryParams) {
    //fixme will leave a trailing '&'
    len = snprintf(current, getRemaining(), "%s=%s&", it.first.c_str(), it.second.c_str());
    current += len;
  }
  return current - start;
}

HttpResponse::HttpResponse() {

}
HttpResponse::~HttpResponse() {

}

const std::string& HttpResponse::value() const {
  return strval;
}

const char* HttpResponse::get() const {
  return strval.c_str();
}
