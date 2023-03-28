#pragma once

#include <common.h>

namespace relloader3 {

class Loader
{
protected:
    virtual void * loadImpl() = 0;

public:
    virtual bool canLoad() = 0;

    template <typename T>
    T * load()
    {
        return reinterpret_cast<T *>(loadImpl());
    }
};

}
