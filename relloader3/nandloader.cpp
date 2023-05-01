#include <common.h>
#include <spm/dvdmgr.h>
#include <wii/ipc.h>
#include <wii/nand.h>
#include <wii/os.h>
#include <ios/fs.h>
#include <ios/ios.h>
#include <msl/stdio.h>

#include "nandloader.h"
#include "error.h"
#include "util.h"

namespace relloader3 {

static s32 open(const char * path, bool mustExist=true)
{
    s32 fd = wii::ipc::IOS_Open(path, wii::ipc::IOS_OPEN_READ);
    if (fd != ios::fs::ERR_FS_ENOENT || mustExist)
        CHECK_ERROR(fd);
    return fd;
}

static void close(s32 fd)
{
    s32 ret = wii::ipc::IOS_Close(fd);
    CHECK_ERROR(ret);
}

static void read(s32 fd, void * dest, u32 length)
{
    s32 ret = wii::ipc::IOS_Read(fd, dest, length);
    CHECK_ERROR(ret);
}


/*
    Get the length of a NAND file
*/
static u32 getLengthNew(s32 fd)
{
    ios::fs::FsFileStats ALIGNED(IOS_ALIGN) stats;
    s32 ret = wii::ipc::IOS_Ioctl(fd, ios::fs::IOCTL_FS_GET_FILE_STATS, nullptr, 0, &stats, sizeof(stats));
    CHECK_ERROR(ret);
    return stats.length;
}

/*
    Get the length of a pcrel.bin format NAND file
*/
static u32 getLengthOld(s32 fd)
{
    u8 header[0x20] ALIGNED(IOS_ALIGN);
    read(fd, header, sizeof(header));
    return readBe32(header);
}

void NandLoader::buildPath(char * dest, size_t n, const char * filename)
{
    // Get game save folder path
    char homedir[64];
    s32 ret = wii::nand::NANDGetHomeDir(homedir);
    CHECK_ERROR(ret);

    // Append filename to path
    msl::stdio::snprintf(dest, n, "%s/%s", homedir, filename);
}

NandLoader::NandLoader(const char * filename, bool oldMode)
    : FileLoader(filename, IOS_ALIGN)
{
    mOldMode = oldMode;
}

bool NandLoader::canLoad()
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Try open
    s32 fd = open(path, false);

    // Fail if not opened
    if (fd == ios::fs::ERR_FS_ENOENT)
        return false;

    // Clean up if opened
    close(fd);

    // Success
    return true;
}

u32 NandLoader::getLength()
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Get length
    s32 fd = open(path);
    u32 length;
    if (mOldMode)
        length = getLengthOld(fd);
    else
        length = getLengthNew(fd);
    close(fd);

    return length;
}

void NandLoader::loadImpl(void * dest, u32 length)
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Open file
    s32 fd = open(path);

    // Skip over header if needed
    if (mOldMode)
        read(fd, dest, IOS_ALIGN);

    // Read from file
    read(fd, dest, length);

    // Close file
    close(fd);
}

}
