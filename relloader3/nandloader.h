#pragma once

#include <common.h>

#include "fileloader.h"

namespace relloader3 {

/*
    Loader implementation for the game save folder
*/
class NandLoader : public FileLoader
{
protected:
    /*
        Whether to load in the pcrel.bin format
    */
    bool mOldMode;

    /*
        Build the full NAND path for a file
    */
    void buildPath(char * dest, size_t n, const char * filename);

    void loadImpl(void * dest, u32 length) override;

public:
    NandLoader(const char * filename, bool oldMode=false);
    bool canLoad() override;
    u32 getLength() override;
};

}
