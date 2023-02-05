#pragma once

#include <common.h>

#include "payloadoffs.inc"

namespace spm_loaders {

template <typename T>
struct TPayloadHeader
{
/* 0x00 */ char headerMagic[4]; // SPMP
/* 0x04 */ u32 headerVersion;
/* 0x08 */ char payloadMagic[4];
/* 0x0C */ u32 payloadVersion;
/* 0x10 */ T * context;
/* 0x14 */ void * loadAddress;
/* 0x18 */ void (*entrypoint)();
/* 0x1C */ void * hookAddress;
/* 0x20 */ u32 implementationType;
/* 0x24 */ u32 implementationVersion;
};

OFFSET_ASSERT(TPayloadHeader<void>, loadAddress, OFFS_PAYLOAD_LOAD_ADDRESS);
OFFSET_ASSERT(TPayloadHeader<void>, entrypoint, OFFS_PAYLOAD_ENTRYPOINT);
OFFSET_ASSERT(TPayloadHeader<void>, hookAddress, OFFS_PAYLOAD_HOOK_ADDRESS);

}
