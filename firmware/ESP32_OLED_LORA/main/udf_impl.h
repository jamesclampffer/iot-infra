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
#ifndef UDF_IMPL_H_
#define UDF_IMPL_H_

#include "udf.h"

/** UDF IO mask
 * @brief Specify what IO channels the UDF can access
 */
struct AppIOMask {
    AppIOMask();

    /// Avoid confusion about meaning of a bool
    enum Enabled {
        NO=0,
        YES
    };

    /// Use to check if a requested read is allowed
    Enabled checkInputEnabled(int idx);

    /// Check if output value may be changed or read back
    Enabled checkOutputEnabled(int idx);

    /// @brief Mask for 32 channels of input as bits 0..31
    /// @note  This limits the amount of inputs on the device to 32
    uint32_t ch_read_mask;
 
    /// Mask for 32 channels of output as bits 0..31
    uint32_t ch_write_mask;
};

#endif // include guard