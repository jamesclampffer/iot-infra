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
#ifndef URI_H_
#define URI_H_

//todo: pImpl to get map out of the header
#include <map>
#include <string>

class URI {
public:
  URI(const char* authority, const char* path = "");
  ~URI();
  const std::string& getAuthority() const;
  const std::string& getPath() const;

  /// Add a key-value pair to the url query
  void addQryPair(const char* key, const char* val);
  void addQryPair(const std::string& key, const std::string& val);

  /// Convert to a string in caller supplied buffer
  int writeIntoBuffer(char* buf, int bufsz);
private:
  std::string authority;
  std::string path;
  std::map<std::string, std::string> qryParams;
};

/// Content portion of response as a string
class HttpResponse {
public:
  HttpResponse();
  ~HttpResponse();
  /// pointer or ref to string
  const std::string& value() const;
  const char* get() const;
private:
  /// json format expected
  std::string strval;
};

#endif // include guard