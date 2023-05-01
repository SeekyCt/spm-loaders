#include <common.h>
#include <spm/dvdmgr.h>
#include <spm/relmgr.h>
#include <wii/dvd.h>
#include <wii/os.h>
#include <msl/stdio.h>

#include "error.h"
#include "relloader.h"
#include "util.h"

namespace relloader3 {

static void executeRel(wii::os::RelHeader * rel)
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

void loadRel(FileLoader * loader)
{
    // Get alignment from file header
    auto * header = loader->load<wii::os::RelHeader>(sizeof(wii::os::RelHeader));
    u32 relAlign = header->align;
    free(header);

    // Load rel
    auto * rel = loader->load<wii::os::RelHeader>(loader->getLength(), relAlign);

    // Link and execute
    executeRel(rel);
}

static FileLoader * finalLoader;

static void doOldLoad(wii::os::RelHeader * relF)
{
    // Original instruction at hook
    relF->prolog();

    // Load rel
    loadRel(finalLoader);
}

void loadRelOld(FileLoader * loader)
{
    // Setup to run after relF.rel prolog
    writeBranchLink(spm::relmgr::relMain, 0x194, doOldLoad);
    finalLoader = loader;
}

}
