#pragma once

#include <common.h>
#include <msl/string.h>

#include "payload.h"

namespace memtest {

constexpr u32 MAGIC = 0x4d454d54; // 'MEMT'

typedef spm_loaders::TPayloadHeader<void, MAGIC, 0x80004200> PayloadHeader;

}
