#include <common.h>
#include <spm/dvdmgr.h>
#include <wii/dvd.h>
#include <wii/os.h>
#include <msl/stdio.h>

#include "error.h"
#include "relloader.h"
#include "util.h"

namespace relloader3 {

RelLoader::RelLoader(FileLoader * loader)
{
    mLoader = loader;
}

void RelLoader::executeRel(wii::os::RelHeader * rel)
{
    // Allocate bss
    void * bss = alloc(rel->bssSize, rel->bssAlign);
    CHECK_ALLOC(bss, rel->bssSize);

    // Link
    bool ret = wii::os::OSLink(rel, bss);
    CHECK_TRUE(ret);

    // Call prolog
    rel->prolog();    
}

void RelLoader::load()
{
    // Get alignment from file header
    auto * header = mLoader->load<wii::os::RelHeader>(sizeof(wii::os::RelHeader));
    u32 relAlign = header->align;
    free(header);

    // Load rel
    auto * rel = mLoader->load<wii::os::RelHeader>(mLoader->getLength(), relAlign);

    // Link and execute
    executeRel(rel);
}

}
