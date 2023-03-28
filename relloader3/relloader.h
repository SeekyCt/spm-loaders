#pragma once

#include <common.h>
#include <wii/os.h>

#include "fileloader.h"

namespace relloader3 {

class RelLoader
{
protected:
    FileLoader * mLoader;
    void executeRel(wii::os::RelHeader * rel);

public:
    virtual bool tryLoad();

    RelLoader(FileLoader * loader);
};

}
