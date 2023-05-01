#pragma once

#include <common.h>
#include <wii/os.h>

#include "fileloader.h"

namespace relloader3 {

/*
    Loads and executes a rel file from a loader
*/
class RelLoader
{
protected:
    /*
        Loader to get the rel from
    */
    FileLoader * mLoader;

    /*
        Link and execute a rel file in RAM
    */
    void executeRel(wii::os::RelHeader * rel);

public:
    /*
        Checks if the file can be loaded
    */
    bool canLoad()
    {
        return mLoader->canLoad();
    }

    /*
        Load and execute the rel
    */
    virtual void load();


    /*
        Create a rel loader for a file
    */
    RelLoader(FileLoader * loader);
};

}
