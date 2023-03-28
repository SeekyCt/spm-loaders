#include <common.h>
#include <spm/dvdmgr.h>
#include <wii/dvd.h>
#include <wii/os.h>
#include <msl/stdio.h>

#include "diskloader.h"
#include "error.h"
#include "util.h"

namespace relloader3 {

void DiskLoader::buildPath(char * dest, size_t n, const char * filename)
{
    msl::stdio::snprintf(dest, n, "./mod/%s", filename);
}

DiskLoader::DiskLoader(const char * filename)
{
    mFilename = filename;
}

bool DiskLoader::canLoad()
{
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    return wii::dvd::DVDConvertPathToEntrynum(path) != -1;
}

void * DiskLoader::loadImpl()
{
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    spm::dvdmgr::DVDEntry * entry = spm::dvdmgr::DVDMgrOpen(path, 2, 0);

    if (entry == nullptr)
        return nullptr;

    u32 length = ALIGN_TO(spm::dvdmgr::DVDMgrGetLength(entry), DVD_ALIGN);
 
    void * mem = alloc(length, DVD_ALIGN);
    CHECK_PTR(mem, length, "file alloc");

    spm::dvdmgr::DVDMgrRead(entry, mem, length, 0);

    spm::dvdmgr::DVDMgrClose(entry);

    wii::os::OSReport("Read %s from DVD\n", mFilename);

    return mem;    
}

}
