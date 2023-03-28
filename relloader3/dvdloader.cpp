#include <common.h>
#include <spm/dvdmgr.h>
#include <wii/dvd.h>
#include <wii/os.h>
#include <msl/stdio.h>

#include "dvdloader.h"
#include "error.h"
#include "util.h"

namespace relloader3 {

void DvdLoader::buildPath(char * dest, size_t n, const char * filename)
{
    msl::stdio::snprintf(dest, n, "./mod/%s", filename);
}

DvdLoader::DvdLoader(const char * filename)
    : FileLoader(filename)
{

}

bool DvdLoader::canLoad()
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Check file exists
    return wii::dvd::DVDConvertPathToEntrynum(path) != -1;
}

void * DvdLoader::loadImpl()
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Try open
    spm::dvdmgr::DVDEntry * entry = spm::dvdmgr::DVDMgrOpen(path, 2, 0);

    // Fail if not opened
    if (entry == nullptr)
        return nullptr;

    // Get length
    u32 length = ALIGN_TO(spm::dvdmgr::DVDMgrGetLength(entry), DVD_ALIGN);
 
    // Allocate memory
    void * mem = alloc(length, DVD_ALIGN);
    CHECK_PTR(mem, length, "file alloc");

    // Read file
    spm::dvdmgr::DVDMgrRead(entry, mem, length, 0);

    // Close file
    spm::dvdmgr::DVDMgrClose(entry);

    wii::os::OSReport("Read %s from DVD\n", mFilename);

    return mem;    
}

}
