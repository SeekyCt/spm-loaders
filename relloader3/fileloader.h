#pragma once

#include <common.h>

#include "util.h"

namespace relloader3 {

/*
    Abstract interface to load a file from somewhere
*/
class FileLoader
{
protected:
    /*
        Name of the file to load
    */
    const char * mFilename;

    /*
        Alignment required for buffer addresses and lengths
    */
    u32 mAlignment;

    /*
        Actual file reading implementation
    */
    virtual void loadImpl(void * dest, u32 length) = 0; 

public:
    /*
        Checks if the file can be loaded
    */
    virtual bool canLoad() = 0;

    /*
        Checks the length of the file
    */
    virtual u32 getLength() = 0;

    /*
        Loads the file to RAM
    */
    template <typename T>
    T * load(u32 length, u32 alignment=0)
    {
        length = ALIGN_TO(length, mAlignment);
        void * buf = alloc(length, MAX(alignment, mAlignment));
        loadImpl(buf, length);
        return reinterpret_cast<T *>(buf);
    }

    /*
        Creates a loader for a file
    */
    FileLoader(const char * filename, u32 alignment)
    {
        mFilename = filename;
        mAlignment = alignment;
    }
};

}
