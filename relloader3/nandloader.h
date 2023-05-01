#pragma once

#include <common.h>

#include "fileloader.h"

namespace relloader3 {

/*
    FileLoader implementation for the game save folder
*/
class NandLoader : public FileLoader
{
protected:
    /*
        Whether to load in the pcrel.bin format
    */
    bool mOldMode;

    void loadImpl(void * dest, u32 length) override;

public:
    NandLoader(const char * filename, bool oldMode=false)
        : FileLoader(filename, IOS_ALIGN)
    {
        mOldMode = oldMode;
    }    

    bool canLoad() override;
    u32 getLength() override;
};

}
