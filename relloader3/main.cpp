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
#include "dvdloader.h"
#include "error.h"
#include "nandloader.h"
#include "relloader.h"
#include "util.h"

namespace relloader3 {

extern "C" void main_real();
__asm__(
".global main_real;"
"main_real:"
    "stwu 1, -0x10 (1);"
    "b main+4;"
);

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

/*
    Set up load methods
*/

struct LoadMethod
{
    FileLoader * loader;
    bool oldMode;
};

static DvdLoader loaderDiskNew = DvdLoader(FILENAME);
static DvdLoader loaderDiskOld = DvdLoader(OLD_DISK_FILENAME);
static NandLoader loaderNandNew = NandLoader(FILENAME);
static NandLoader loaderNandOld = NandLoader(OLD_NAND_FILENAME, true);

static LoadMethod loadMethods[] = {
    {&loaderDiskNew, false},
    {&loaderDiskOld, true},
    {&loaderNandNew, false},
    {&loaderNandOld, true}
};

bool gameBooted = false;

/*
    Main entrypoint (on blr of spmarioInit)
*/
extern "C" void loaderMain();
void loaderMain()
{
    wii::os::OSReport("Rel Loader 3 (main) - v1\n");

    // Run setup
    callCtors();

    // Try all load methods in order
    bool loaded = false;
    for (u32 i = 0; i < ARRAY_SIZEOF(loadMethods); i++)
    {
        LoadMethod * method = loadMethods + i;
        if (method->loader->canLoad())
        {
            logLoaderUsed(i);

            if (method->oldMode)
                loadRelOld(method->loader);
            else
                loadRel(method->loader);

            loaded = true;
            break;
        }
    }

    // Check success
    if (!loaded)
        error("Error: rel not found on disc or in save file");

    gameBooted = true;
    main_real();
}

}
