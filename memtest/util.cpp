#include <common.h>
#include <spm/memory.h>
#include <wii/os.h>

#include "util.h"

namespace memtest {

void * alloc(size_t size, u32 alignment)
{
    // Enforce minimum alignment
    alignment = MAX(alignment, 0x20);

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

void free(void * buf)
{
    wii::mem::MEMHeapHandle heap = wii::mem::MEMFindContainHeap(buf);
    wii::mem::MEMFreeToExpHeap(heap, buf);
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

void _writeWord(void * ptr, u32 value)
{
    u32 * p = reinterpret_cast<u32 *>(ptr);
    *p = value;

    wii::os::DCFlushRange(ptr, sizeof(u32));
    wii::os::ICInvalidateRange(ptr, sizeof(u32));
}

}
