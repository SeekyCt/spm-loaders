#pragma once

#include <common.h>

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
        Main implementation of loading
    */
    virtual void * loadImpl() = 0;

public:
    /*
        Checks if the file can be loaded
    */
    virtual bool canLoad() = 0;

    /*
        Loads the file to RAM
    */
    template <typename T>
    T * load()
    {
        return reinterpret_cast<T *>(loadImpl());
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
