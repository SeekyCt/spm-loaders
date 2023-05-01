#pragma once

#include <common.h>

#include "fileloader.h"

namespace relloader3 {

/*
    Loader implementation for the disk ./mod/ folder
*/
class DvdLoader : public FileLoader
{
protected:
    /*
        Build the full DVD path for a file
    */
    void buildPath(char * dest, size_t n, const char * filename);

    void loadImpl(void * dest, u32 length) override;

public:
    DvdLoader(const char * filename);
    bool canLoad() override;
    u32 getLength() override;
};

}
