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

/*
    Open a NAND file
*/
static s32 open(const char * path, s32 mode)
{
    s32 fd = wii::ipc::IOS_Open(path, mode);

    if (fd != ios::fs::ERR_FS_ENOENT)
        CHECK_ERROR(fd, "IOS_Open");
    
    return fd;
}

/*
    Close a NAND file
*/
static void close(s32 fd)
{
    s32 ret = wii::ipc::IOS_Close(fd);
    CHECK_ERROR(ret, "IOS_Close");
}

/*
    Read from a NAND file
*/
static s32 read(s32 fd, void * mem, u32 length)
{
    s32 ret = wii::ipc::IOS_Read(fd, mem, length);

    CHECK_ERROR(ret, "IOS_Read");

    return ret;
}

/*
    Get the length of a NAND file
*/
static u32 getLength(s32 fd)
{
    ios::fs::FsFileStats ALIGNED(IOS_ALIGN) stats;
    
    s32 ret = wii::ipc::IOS_Ioctl(fd, ios::fs::IOCTL_FS_GET_FILE_STATS, nullptr, 0, &stats, sizeof(stats));
    
    CHECK_ERROR(ret, "IOS_Ioctl");
    
    return stats.length;
}

/*
    Get the length of a pcrel.bin format NAND file
*/
static u32 getLengthOld(s32 fd)
{
    u8 header[0x20] ALIGNED(NAND_ALIGN);
    read(fd, header, sizeof(header));

    return readBe32(header);
}

void NandLoader::buildPath(char * dest, size_t n, const char * filename)
{
    // Get game save folder path
    char homedir[64];
    wii::nand::NANDGetHomeDir(homedir);

    // Append filename to path
    msl::stdio::snprintf(dest, n, "%s/%s", homedir, filename);
}

NandLoader::NandLoader(const char * filename, bool oldMode)
    : FileLoader(filename)
{
    mOldMode = oldMode;
}

bool NandLoader::canLoad()
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Try open
    s32 fd = open(path, wii::ipc::IOS_OPEN_READ);

    // Fail if not opened
    if (fd == ios::fs::ERR_FS_ENOENT)
        return false;

    // Clean up if opened
    close(fd);

    // Success
    return true;
}

void * NandLoader::loadImpl()
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Try open file
    s32 fd = open(path, wii::ipc::IOS_OPEN_READ);

    // Fail if not opened
    if (fd == ios::fs::ERR_FS_ENOENT)
        return nullptr;

    // Get length
    u32 length;
    if (mOldMode)
        length = getLengthOld(fd);
    else
        length = getLength(fd);

    // Allocate space for file
    void * mem = alloc(ALIGN_TO(length, IOS_ALIGN), IOS_ALIGN);
    CHECK_PTR(mem, length, "file alloc");

    // Read from file
    read(fd, mem, length);

    // Close file
    close(fd);

    wii::os::OSReport("Read %s from NAND\n", mFilename);

    return mem;
}

}
