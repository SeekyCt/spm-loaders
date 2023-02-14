#include <common.h>
#include <spm/dvdmgr.h>
#include <spm/memory.h>
#include <spm/relmgr.h>
#include <wii/gx.h>
#include <wii/ipc.h>
#include <wii/nand.h>
#include <wii/os.h>
#include <ios/ios.h>
#include <ios/fs.h>
#include <msl/stdio.h>
#include <msl/string.h>

#include <spm_loaders/relloader.h>

#include "dvd.h"
#include "error.h"
#include "nand.h"
#include "util.h"

namespace relloader3 {

extern "C" {

RelLoaderContext loaderCtx;

}

static bool tryLoadRel(const char * diskFilename, const char * nandFilename, bool oldNandMode=false)
{
    // Load rel from somewhere
    auto * rel = (wii::os::RelHeader *) tryDvdLoad(diskFilename);
    if (rel == nullptr)
        rel = (wii::os::RelHeader *) tryNandLoad(nandFilename, oldNandMode);
    if (rel == nullptr)
        return false;

    // Allocate bss
    void * bss = alloc(rel->bssSize, rel->bssAlign);
    CHECK_PTR(bss, rel->bssSize, "bss alloc");

    // Link
    bool ret = wii::os::OSLink(rel, bss);
    CHECK_TRUE(ret, "OSLink");

    // Call prolog
    rel->prolog();

    return true;
}

/*
    Old rel loader - load mod.rel after relF.rel
*/
#define OLD_DISK_FILENAME "mod.rel"
#define OLD_NAND_FILENAME "pcrel.bin"
static void doOldLoad(wii::os::RelHeader * relF)
{
    // Original instruction at hook
    relF->prolog();

    CHECK_TRUE(tryLoadRel(OLD_DISK_FILENAME, OLD_NAND_FILENAME, true), "old load");
}
bool tryOldLoad()
{
    // Check if either old file exists
    if (!dvdFileExists(OLD_DISK_FILENAME) && !nandFileExists(OLD_NAND_FILENAME))
        return false;
    
    // Setup to run after relF.rel prolog
    writeBranchLink(spm::relmgr::relMain, 0x194, doOldLoad);

    return true;
}

/*
    Modern rel loader - load rgX.rel after spmarioInit
*/
#ifdef SPM_EU0
    #define FILENAME "eu0.rel"
#elif defined SPM_EU1
    #define FILENAME "eu1.rel"
#elif defined SPM_US0
    #define FILENAME "us0.rel"
#elif defined SPM_US1
    #define FILENAME "us1.rel"
#elif defined SPM_US2
    #define FILENAME "us2.rel"
#elif defined SPM_JP0
    #define FILENAME "jp0.rel"
#elif defined SPM_JP1
    #define FILENAME "jp1.rel"
#elif defined SPM_KR0
    #define FILENAME "kr0.rel"
#endif
bool tryModernLoad()
{
    return tryLoadRel(FILENAME, FILENAME);
}

/*
    Main entrypoint
*/
extern "C" void loaderMain();
void loaderMain()
{
    wii::os::OSReport("Rel Loader 3 - v1\n");

    bool loaded = tryModernLoad();
    if (!loaded)
        loaded = tryOldLoad();
    if (!loaded)
        error("Error: rel not found on disc or in save file");
}

}
