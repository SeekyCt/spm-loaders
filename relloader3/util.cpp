#include <common.h>
#include <spm/memory.h>
#include <wii/os.h>

#include "main.h"
#include "util.h"

namespace relloader3 {

void * alloc(size_t size, u32 alignment)
{
    wii::os::OSReport("alloc(%zu, %u)\n", size, alignment);
    // Enforce minimum alignment
    alignment = MAX(alignment, 0x20);
    wii::os::OSReport("->%d (%d)\n", alignment, gameBooted);

    // Allocate from arena hi if running before memInit
    if (!gameBooted)
    {
        // Create buffer
        u32 addr = (u32) wii::os::OSGetMEM1ArenaHi();
        addr -= size;
        addr = ALIGN_DOWN_TO(addr, alignment);
        void * ptr = (void *) addr;

        // Exclude allocated memory from arena
        wii::os::OSSetMEM1ArenaHi(ptr);

        return ptr;
    }
    else
    {
        // Try unused heap first
        auto handle = spm::memory::memory_wp->heapHandle[spm::memory::HEAP_MEM1_UNUSED];
        void * firstAlloc = wii::mem::MEMAllocFromExpHeapEx(handle, size, alignment);
        if (firstAlloc != nullptr)
            return firstAlloc;
        
        // Fall back to main heap
        // Use negative alignment to allocate from tail so that relF.rel won't shift 
        handle = spm::memory::memory_wp->heapHandle[spm::memory::HEAP_MAIN];
        return wii::mem::MEMAllocFromExpHeapEx(handle, size, -alignment);
    }
}

void _writeBranch(void * ptr, void * destination, bool link)
{
    u32 delta = reinterpret_cast<u32>(destination) - reinterpret_cast<u32>(ptr);
    u32 value = link ? 0x48000001 : 0x48000000;
    value |= (delta & 0x03FFFFFC);
    
    u32 * p = reinterpret_cast<u32 *>(ptr);
    *p = value;

    wii::os::DCFlushRange(ptr, sizeof(u32));
    wii::os::ICInvalidateRange(ptr, sizeof(u32));
}

}
