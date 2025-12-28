#include <common.h>
#include <spm/memory.h>
#include <spm/spmario.h>
#include <msl/string.h>

#include <spm_loaders/relloader.h>

#include "ctors.h"
#include "error.h"
#include "util.h"

namespace memtest {

extern "C" void spmarioInit_real();
__asm__(
".global spmarioInit_real;"
"spmarioInit_real:"
    "stwu 1, -0x20 (1);"
    "b spmarioInit+4;"
);

static spm::memory::HeapSize size_table[HEAP_COUNT] =
{
    // MEM1
    { // 0
        spm::memory::HEAPSIZE_ABSOLUTE_KB,
        0x2400
    },
    { // 1
        spm::memory::HEAPSIZE_ABSOLUTE_KB,
        0x1800
    },
    { // 2
        spm::memory::HEAPSIZE_PERCENT_REMAINING,
        100
    },

    // MEM2
    { // 3
        spm::memory::HEAPSIZE_ABSOLUTE_KB,
        0x100
    },
    { // 4
        spm::memory::HEAPSIZE_ABSOLUTE_KB,
        0x100
    },
    { // 5
        spm::memory::HEAPSIZE_ABSOLUTE_KB,
        0x80
    },
    { // 6
        spm::memory::HEAPSIZE_ABSOLUTE_KB,
        0x4400
    },
    { // 7 - smart heap
        spm::memory::HEAPSIZE_PERCENT_REMAINING,
        100
    },
    { // 8
        spm::memory::HEAPSIZE_ABSOLUTE_KB,
        1
    }
};


void memPatch()
{
    msl::string::memcpy(&spm::memory::memory_size_table, &size_table, sizeof(size_table));

    writeWord(spm::memory::memInit, 0xa0, 0x2c1d0003); // cmpwi r29, 0x3
    writeWord(spm::memory::memInit, 0x178, 0x2c1b0003); // cmpwi r27, 0x3
    writeWord(spm::memory::memInit, 0x1b0, 0x2c190003); // cmpwi r25, 0x3
    
    writeWord(spm::memory::memInit, 0x1e0, 0x3b600003); // li r27, 0x3
    writeWord(spm::memory::memInit, 0x1e4, 0x3b240018); // addi r25, r4, 0x18
    writeWord(spm::memory::memInit, 0x1e8, 0x3b40000c); // li r26, 0xc
    
    writeWord(spm::memory::memInit, 0x274, 0x3b600003); // li r27, 0x3
    writeWord(spm::memory::memInit, 0x278, 0x3be30018); // addi r31, r3, 0x18
    writeWord(spm::memory::memInit, 0x27c, 0x3bc0000c); // li r30, 0xc
    
    writeWord(spm::memory::memInit, 0x344, 0x3b200003); // li r25, 0x3
    writeWord(spm::memory::memInit, 0x348, 0x3b00000c); // li r24, 0xc

}

// TODO: title screen patch, crash handler

void logHeaps()
{
    for (int i = 0; i < HEAP_COUNT; i++)
    {
        wii::os::OSReport("%d: %p %p %p (0x%x kb)\n", i,
            spm::memory::memory_wp->heapHandle[i],
            spm::memory::memory_wp->heapStart[i],
            spm::memory::memory_wp->heapEnd[i],
            ((size_t)spm::memory::memory_wp->heapEnd[i] - (size_t)spm::memory::memory_wp->heapStart[i]) / 1024
        );
    }
}

/*
    Main entrypoint (spmarioInit)
*/
extern "C" void loaderMain();
void loaderMain()
{
    wii::os::OSReport("memtest - v1\n");

    // Run setup
    callCtors();

    // memPatch();

    writeBranch(spm::memory::memInit, 0x414, logHeaps);

    spmarioInit_real();
}

// TODO: korea

}
