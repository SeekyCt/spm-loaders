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

u32 DvdLoader::getLength()
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Get length
    spm::dvdmgr::DVDEntry * entry = spm::dvdmgr::DVDMgrOpen(path, 2, 0);
    u32 length = spm::dvdmgr::DVDMgrGetLength(entry);
    spm::dvdmgr::DVDMgrClose(entry);
    return length;
}

u32 DvdLoader::getAlign()
{
    return DVD_ALIGN;
}

void DvdLoader::loadImpl(void * dest, u32 length)
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Load file contents
    spm::dvdmgr::DVDEntry * entry = spm::dvdmgr::DVDMgrOpen(path, 2, 0);
    spm::dvdmgr::DVDMgrRead(entry, dest, length, 0);
    spm::dvdmgr::DVDMgrClose(entry);
}

}
