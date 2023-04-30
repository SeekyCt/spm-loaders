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
    Get the length of a NAND file
*/
static u32 getLengthNew(s32 fd)
{
    ios::fs::FsFileStats ALIGNED(IOS_ALIGN) stats;
    wii::ipc::IOS_Ioctl(fd, ios::fs::IOCTL_FS_GET_FILE_STATS, nullptr, 0, &stats, sizeof(stats));
    return stats.length;
}

/*
    Get the length of a pcrel.bin format NAND file
*/
static u32 getLengthOld(s32 fd)
{
    u8 header[0x20] ALIGNED(NAND_ALIGN);
    wii::ipc::IOS_Read(fd, header, sizeof(header));
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
    s32 fd = wii::ipc::IOS_Open(path, wii::ipc::IOS_OPEN_READ);

    // Fail if not opened
    if (fd == ios::fs::ERR_FS_ENOENT)
        return false;

    // Clean up if opened
    wii::ipc::IOS_Close(fd);

    // Success
    return true;
}

u32 NandLoader::getLength()
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Get length
    s32 fd = wii::ipc::IOS_Open(path, wii::ipc::IOS_OPEN_READ);
    u32 length;
    if (mOldMode)
        length = getLengthOld(fd);
    else
        length = getLengthNew(fd);
    wii::ipc::IOS_Close(fd);

    return length;
}

u32 NandLoader::getAlign()
{
    return IOS_ALIGN;
}

void NandLoader::loadImpl(void * dest, u32 length)
{
    // Build full path
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    // Open file
    s32 fd = wii::ipc::IOS_Open(path, wii::ipc::IOS_OPEN_READ);

    // Read from file
    wii::ipc::IOS_Read(fd, dest, length);

    // Close file
    wii::ipc::IOS_Close(fd);
}

}
