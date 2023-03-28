#pragma once

#include <common.h>

#include "loader.h"

namespace relloader3 {

class NandLoader : public Loader
{
protected:
    const char * mFilename;
    bool mOldMode;

    void buildPath(char * dest, size_t n, const char * filename);
    void * loadImpl() override;

public:
    NandLoader(const char * filename, bool oldMode=false);
    bool canLoad() override;
};

}
