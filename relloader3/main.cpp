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

#include "ctors.h"
#include "diskloader.h"
#include "error.h"
#include "nandloader.h"
#include "oldrelloader.h"
#include "relloader.h"
#include "util.h"

namespace relloader3 {

/*
    Create the context instance expected by the header
*/
extern "C" {

RelLoaderContext loaderCtx;

}

/*
    Old loader filenames
*/
#define OLD_DISK_FILENAME "mod.rel"
#define OLD_NAND_FILENAME "pcrel.bin"

/*
    New loader filenames
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

static DiskLoader loaderDiskOld = DiskLoader(OLD_DISK_FILENAME);
static NandLoader loaderNandOld = NandLoader(OLD_NAND_FILENAME, true);
static DiskLoader loaderDiskNew = DiskLoader(FILENAME);
static NandLoader loaderNandNew = NandLoader(FILENAME);

static RelLoader relLoaderDiskNew = RelLoader(&loaderDiskNew);
static RelLoader relLoaderNandNew = RelLoader(&loaderNandNew);
static OldRelLoader relLoaderDiskOld = OldRelLoader(&loaderDiskOld);
static OldRelLoader relLoaderNandOld = OldRelLoader(&loaderNandOld);

static RelLoader * relLoaders[] = {
    &relLoaderDiskNew,
    &relLoaderDiskOld,
    &relLoaderNandNew,
    &relLoaderNandOld
};

/*
    Main entrypoint (on blr of spmarioInit)
*/
extern "C" void loaderMain();
void loaderMain()
{
    wii::os::OSReport("Rel Loader 3 - v1 aaa\n");

    callCtors();

    bool loaded = false;
    for (u32 i = 0; i < ARRAY_SIZEOF(relLoaders); i++)
    {
        RelLoader * loader = relLoaders[i];
        if (loader->tryLoad())
        {
            loaded = true;
            break;
        }
    }

    if (!loaded)
        error("Error: rel not found on disc or in save file");
}

}
