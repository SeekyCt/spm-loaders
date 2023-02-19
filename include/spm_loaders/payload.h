#pragma once

#include <common.h>
#include <msl/string.h>

#include "payloadoffs.inc"

namespace spm_loaders {

constexpr u32 HEADER_MAGIC = 0x53504d50; // 'SPMP'

template <typename tContext, u32 tMagic, u32 tAddr>
struct TPayloadHeader
{
/* 0x00 */ u32 headerMagic; // SPMP
/* 0x04 */ u32 headerVersion;
/* 0x08 */ u32 payloadMagic;
/* 0x0C */ u32 payloadVersion;
/* 0x10 */ tContext * context;
/* 0x14 */ void * loadAddress;
/* 0x18 */ void (*entrypoint)();
/* 0x1C */ void * hookAddress;
/* 0x20 */ u32 implementationType;
/* 0x24 */ u32 implementationVersion;

    bool isLoaded()
    {
        return headerMagic == HEADER_MAGIC && payloadMagic == tMagic;
    }

    static inline auto const instance = reinterpret_cast<TPayloadHeader<tContext, tMagic, tAddr> *>(tAddr);
};

namespace {
typedef TPayloadHeader<void, 0, 0> _PayloadHeader;

OFFSET_ASSERT(_PayloadHeader, loadAddress, OFFS_PAYLOAD_LOAD_ADDRESS);
OFFSET_ASSERT(_PayloadHeader, entrypoint, OFFS_PAYLOAD_ENTRYPOINT);
OFFSET_ASSERT(_PayloadHeader, hookAddress, OFFS_PAYLOAD_HOOK_ADDRESS);
}

}
