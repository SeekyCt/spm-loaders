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
        Attempt to load and execute the rel
    */
    virtual bool tryLoad();

    /*
        Create a rel loader for a file
    */
    RelLoader(FileLoader * loader);
};

}
