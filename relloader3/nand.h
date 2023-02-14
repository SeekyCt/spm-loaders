/*
    NAND file loading functions
*/

#pragma once

#include <common.h>

namespace relloader3 {

/*
    Checks if a file exists in the game save folder
*/
bool nandFileExists(const char * filename);

/*
    Tries to load a file from the game save folder

    If oldMode is true, the file is read in the pcrel.bin format used by the old rel loader
    This format is an 0x20 byte header, with the first 4 bytes storing the length of the rest of
    the file (big endian)
*/
void * tryNandLoad(const char * filename, bool oldMode);

}
