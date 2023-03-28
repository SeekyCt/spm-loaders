#include <common.h>
#include <spm/dvdmgr.h>
#include <spm/relmgr.h>
#include <wii/dvd.h>
#include <wii/os.h>
#include <msl/stdio.h>

#include "oldrelloader.h"
#include "error.h"
#include "util.h"

namespace relloader3 {

OldRelLoader * OldRelLoader::sFinalLoader;

OldRelLoader::OldRelLoader(FileLoader * loader)
    : RelLoader(loader)
{

}

void OldRelLoader::doOldLoad(wii::os::RelHeader * relF)
{
    // Original instruction at hook
    relF->prolog();

    // Load rel
    CHECK_TRUE(sFinalLoader->RelLoader::tryLoad(), "old load");
}

bool OldRelLoader::tryLoad()
{
    // Check if old file exists
    if (!mLoader->canLoad())
        return false;
    
    // Setup to run after relF.rel prolog
    writeBranchLink(spm::relmgr::relMain, 0x194, doOldLoad);
    sFinalLoader = this;

    return true;
}

}
