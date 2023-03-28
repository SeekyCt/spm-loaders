#pragma once

#include <common.h>

#include "loader.h"

namespace relloader3 {

class DiskLoader : public Loader
{
protected:
    const char * mFilename;

    void buildPath(char * dest, size_t n, const char * filename);
    void * loadImpl() override;

public:
    DiskLoader(const char * filename);
    bool canLoad() override;
};

}
