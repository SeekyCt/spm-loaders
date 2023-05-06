#pragma once

#include <common.h>
#include <msl/string.h>

#include "payload.h"

namespace relloader3 {

constexpr u32 MAGIC = 0x524c6433; // 'RLd3'

typedef spm_loaders::TPayloadHeader<void, MAGIC, 0x80004200> PayloadHeader;

}
