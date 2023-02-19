#pragma once

#include <common.h>
#include <msl/string.h>

#include "payload.h"

namespace relloader3 {

constexpr u32 MAGIC = 0x524c6433; // 'RLd3'

struct RelLoaderContext
{
/* 0x0 */ void * hostRelContext;
};

typedef spm_loaders::TPayloadHeader<RelLoaderContext, MAGIC, 0x80004200> RelLoaderHeader;

}
