/*
    DVD file loading functions
*/

#pragma once

#include <common.h>

namespace relloader3 {

/*
    Checks if a file exists in the mod folder on the disc
*/
bool dvdFileExists(const char * filename);

/*
    Tries to load a file from the mod folder on the disc
*/
void * tryDvdLoad(const char * filename);

}
