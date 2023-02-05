#pragma once

#include "payload.h"

namespace relloader3 {

struct RelLoaderContext
{
/* 0x0 */ char magic[4]; // RLd3
/* 0x4 */ void * hostRelContext;
};

typedef spm_loaders::TPayloadHeader<RelLoaderContext> RelLoaderHeader;

inline RelLoaderHeader * const payloadHeader = (RelLoaderHeader *)0x80004200;

}
