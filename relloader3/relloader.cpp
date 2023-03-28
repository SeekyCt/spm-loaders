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
    CHECK_PTR(bss, rel->bssSize, "bss alloc");

    // Link
    bool ret = wii::os::OSLink(rel, bss);
    CHECK_TRUE(ret, "OSLink");

    // Call prolog
    rel->prolog();    
}

bool RelLoader::tryLoad()
{
    // Check if file exists
    if (!mLoader->canLoad())
        return false;

    // Try load rel
    wii::os::RelHeader * rel = mLoader->load<wii::os::RelHeader>();
    if (rel == nullptr)
        return false;

    // Link and execute
    executeRel(rel);

    return true;
}

}
