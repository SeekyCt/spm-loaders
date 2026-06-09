#include <common.h>
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
static bool open(const char * path, wii::dvd::DVDFileInfo * fileInfo)
{
    s32 entrynum = wii::dvd::DVDConvertPathToEntrynum(path);

    if (entrynum == -1)
        return false;

    return wii::dvd::DVDFastOpen(entrynum, fileInfo);
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
    wii::dvd::DVDFileInfo fileInfo;
    open(path, &fileInfo);
    u32 length = fileInfo.length;
    wii::dvd::DVDClose(&fileInfo);
    return length;
}

void DvdLoader::loadImpl(void * dest, u32 length)
{
    // Build full path
    char path[PATH_SPACE];
    buildPath(path, sizeof(path), mFilename);

    // Load file contents
    wii::dvd::DVDFileInfo fileInfo;
    open(path, &fileInfo);
    wii::dvd::DVDReadPrio(&fileInfo, dest, length, 0, 2);
    wii::dvd::DVDClose(&fileInfo);
}

}
