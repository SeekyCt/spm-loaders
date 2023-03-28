#pragma once

#include <common.h>

#include "fileloader.h"

namespace relloader3 {

/*
    Loader implementation for the disk ./mod/ folder
*/
class DiskLoader : public FileLoader
{
protected:
    /*
        Build the full DVD path for a file
    */
    void buildPath(char * dest, size_t n, const char * filename);

    void * loadImpl() override;

public:
    DiskLoader(const char * filename);
    bool canLoad() override;
};

}
