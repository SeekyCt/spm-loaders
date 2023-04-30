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
        Gets the alignment required for buffer addresses and lengths
    */
    virtual u32 getAlign();

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
    virtual u32 getLength();

    /*
        Loads the file to RAM
    */
    template <typename T>
    T * load(u32 length, u32 alignment=0)
    {
        u32 loaderAlign = getAlign();
        length = ALIGN_TO(length, loaderAlign);
        void * buf = alloc(length, MAX(alignment, loaderAlign));
        loadImpl(buf, length);
        return reinterpret_cast<T *>(buf);
    }

    /*
        Creates a loader for a file
    */
    FileLoader(const char * filename)
    {
        mFilename = filename;
    }
};

}
