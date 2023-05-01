#pragma once

#include <common.h>
#include <wii/os.h>

#include "relloader.h"

namespace relloader3 {

/*
    Modified RelLoader to load after relF.rel
*/
class OldRelLoader : public RelLoader
{
protected:
    /*
        Instance to call when relF prolog runs
    */
    static OldRelLoader * sFinalLoader;

    /*
        Callback for relF prolog hook
    */
    static void doOldLoad(wii::os::RelHeader * relF);

public:
    /*
        Override to load after relF.rel
    */
    void load() override;

    OldRelLoader(FileLoader * loader);
};

}
