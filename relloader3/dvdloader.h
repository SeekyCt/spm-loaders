#pragma once

#include <common.h>

#include "fileloader.h"

namespace relloader3 {

/*
    FileLoader implementation for the disk ./mod/ folder
*/
class DvdLoader : public FileLoader
{
protected:
    void loadImpl(void * dest, u32 length) override;

public:
    DvdLoader(const char * filename)
        : FileLoader(filename, DVD_ALIGN)
    {

    }

    bool canLoad() override;
    u32 getLength() override;
};

}
