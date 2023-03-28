#pragma once

#include <common.h>
#include <wii/os.h>

#include "relloader.h"

namespace relloader3 {

class OldRelLoader : public RelLoader
{
protected:
    /*
        Instance to call when rel prolog runs
    */
    static OldRelLoader * finalLoader;

    /*
        Callback for rel prolog hook
    */
    static void doOldLoad(wii::os::RelHeader * relF);

public:
    /*
        Override to load after 
    */
    bool tryLoad() override;

    OldRelLoader(Loader * loader);
};

}
