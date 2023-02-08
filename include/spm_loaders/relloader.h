#pragma once

#include <common.h>
#include <msl/string.h>

#include "payload.h"

namespace relloader3 {

constexpr u32 MAGIC = 0x524c6433; // 'RLd3'

struct RelLoaderContext
{
/* 0x0 */ char magic[4]; // RLd3
/* 0x4 */ void * hostRelContext;
};

typedef spm_loaders::TPayloadHeader<RelLoaderContext, MAGIC> RelLoaderHeader;

inline RelLoaderHeader * const payloadHeader = (RelLoaderHeader *)0x80004200;
}
