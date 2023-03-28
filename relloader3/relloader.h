#pragma once

#include <common.h>
#include <wii/os.h>

#include "loader.h"

namespace relloader3 {

class RelLoader
{
protected:
    Loader * mLoader;
    void executeRel(wii::os::RelHeader * rel);

public:
    virtual bool tryLoad();

    RelLoader(Loader * loader);
};

}
