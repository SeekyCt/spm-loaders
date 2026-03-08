#pragma once

#include <common.h>

#include "error.h"
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

    u32 alignment()
    {
        return mAlignment;
    }

    u32 alignLength(u32 length)
    {
        return ALIGN_TO(length, mAlignment);
    }

    /*
        Loads the file to RAM
    */
    template <typename T>
    void load(T * dest, u32 length)
    {
        length = alignLength(length);
        loadImpl(dest, length);
    }

    /*
        Loads the file to RAM
    */
    template <typename T>
    T * load(u32 length, u32 alignment=0)
    {
        length = alignLength(length);
        void * buf = alloc(length, MAX(alignment, mAlignment));
        CHECK_ALLOC(buf, length);
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
