#include <common.h>
#include <spm/dvdmgr.h>
#include <spm/memory.h>
#include <wii/dvd.h>
#include <wii/os.h>
#include <msl/stdio.h>

#include "dvd.h"
#include "error.h"
#include "util.h"

namespace relloader3 {

static void buildPath(char * dest, size_t n, const char * filename)
{
    msl::stdio::snprintf(dest, n, "./mod/%s", filename);
}

bool dvdFileExists(const char * filename)
{
    char path[64];
    buildPath(path, sizeof(path), filename);

    return wii::dvd::DVDConvertPathToEntrynum(path) != -1;
}

void * tryDvdLoad(const char * filename)
{
    char path[64];
    buildPath(path, sizeof(path), filename);

    spm::dvdmgr::DVDEntry * entry = spm::dvdmgr::DVDMgrOpen(path, 2, 0);

    if (entry == nullptr)
        return nullptr;

    u32 length = ALIGN_TO(spm::dvdmgr::DVDMgrGetLength(entry), DVD_ALIGN);
 
    void * mem = alloc(length, DVD_ALIGN);
    CHECK_PTR(mem, length, "file alloc");

    spm::dvdmgr::DVDMgrRead(entry, mem, length, 0);

    spm::dvdmgr::DVDMgrClose(entry);

    wii::os::OSReport("Read %s from DVD\n", filename);

    return mem;
}

}
