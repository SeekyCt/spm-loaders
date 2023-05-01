#pragma once

#include <common.h>
#include <wii/os.h>

#include "fileloader.h"

namespace relloader3 {

/*
    Load and execute a rel
*/
void loadRel(FileLoader * loader);

/*
    Load and execute a rel after relF.rel
*/
void loadRelOld(FileLoader * loader);


}
