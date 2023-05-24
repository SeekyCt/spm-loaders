#include <common.h>
#include <spm/dvdmgr.h>
#include <wii/dvd.h>
#include <wii/os.h>
#include <msl/stdio.h>

#include "dvdloader.h"
#include "error.h"
#include "util.h"

// Arbitrary length that should be long enough for paths
#define PATH_SPACE 64

namespace relloader3 {

/*
    Opens a file and checks for errors
*/
static spm::dvdmgr::DVDEntry * open(const char * path)
{
    spm::dvdmgr::DVDEntry * ret = spm::dvdmgr::DVDMgrOpen(path, 2, 0);
    CHECK_PTR(ret);
    return ret;
}

/*
    Builds the full path for a file in the mod folder
*/
static void buildPath(char * dest, size_t n, const char * filename)
{
    msl::stdio::snprintf(dest, n, "./mod/%s", filename);
}

bool DvdLoader::canLoad()
{
    // Build full path
    char path[PATH_SPACE];
    buildPath(path, sizeof(path), mFilename);

    // Check file exists
    return wii::dvd::DVDConvertPathToEntrynum(path) != -1;
}

u32 DvdLoader::getLength()
{
    // Build full path
    char path[PATH_SPACE];
    buildPath(path, sizeof(path), mFilename);

    // Get length
    spm::dvdmgr::DVDEntry * entry = open(path);
    u32 length = spm::dvdmgr::DVDMgrGetLength(entry);
    spm::dvdmgr::DVDMgrClose(entry);
    return length;
}

void DvdLoader::loadImpl(void * dest, u32 length)
{
    // Build full path
    char path[PATH_SPACE];
    buildPath(path, sizeof(path), mFilename);

    // Load file contents
    spm::dvdmgr::DVDEntry * entry = open(path);
    spm::dvdmgr::DVDMgrRead(entry, dest, length, 0);
    spm::dvdmgr::DVDMgrClose(entry);
}

}
