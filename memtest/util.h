#pragma once

namespace memtest {

/*
    Gets the number of items in an array
*/
#define ARRAY_SIZEOF(arr) sizeof(arr)/sizeof(arr[0])

/*
    Rounds a value up to an alignment (must be a power of 2)
*/
#define ALIGN_TO(val, align) (((val) + ((align)-1)) & ~((align)-1))

/*
    Gets the maximum of 2 values
*/
#define MAX(a, b) (a > b ? a : b)

/*
    Reads a 32-bit unsigned big endian integer from a byte stream
*/
inline u32 readBe32(u8 * data)
{
    return data[0] << 24 | data[1] << 16 | data[2] << 8 | data[3];
}

/*
    Allocates memory with optional alignment
    Uses the unused MEM1 heap if there's space, falls back to the main heap otherwise
*/
void * alloc(size_t size, u32 alignment = 0);

/*
    Frees memory allocated by alloc
*/
void free(void * buf);

/*
    Writes a b within a function to another function
*/
#define writeBranch(ptr, offset, destination) \
    memtest::_writeBranch(((u8 *)(ptr)) + (offset), (void *)(destination), false)

/*
    Writes a bl within a function to another function
*/
#define writeBranchLink(ptr, offset, destination) \
    memtest::_writeBranch(((u8 *)(ptr)) + (offset), (void *)(destination), true)

/*
    Writes a branch at an address to another function
    Uses b if link=false, bl if link=true
*/
void _writeBranch(void * ptr, void * destination, bool link);

#define writeWord(ptr, offset, value) \
    memtest::_writeWord(((u8 *)(ptr)) + (offset), value)

/*
    Writes a word at an address
*/
void _writeWord(void * ptr, u32 value);

}
