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

void NandLoader::buildPath(char * dest, size_t n, const char * filename)
{
    char homedir[64];
    wii::nand::NANDGetHomeDir(homedir);

    msl::stdio::snprintf(dest, n, "%s/%s", homedir, filename);
}

NandLoader::NandLoader(const char * filename, bool oldMode)
{
    mFilename = filename;
    mOldMode = oldMode;
}

static s32 open(const char * path, s32 mode)
{
    s32 fd = wii::ipc::IOS_Open(path, mode);

    if (fd != ios::fs::ERR_FS_ENOENT)
        CHECK_ERROR(fd, "IOS_Open");
    
    return fd;
}

static void close(s32 fd)
{
    s32 ret = wii::ipc::IOS_Close(fd);
    CHECK_ERROR(ret, "IOS_Close");
}

static s32 read(s32 fd, void * mem, u32 length)
{
    s32 ret = wii::ipc::IOS_Read(fd, mem, length);

    CHECK_ERROR(ret, "IOS_Read");

    return ret;
}

static u32 getLength(s32 fd)
{
    ios::fs::FsFileStats ALIGNED(IOS_ALIGN) stats;
    
    s32 ret = wii::ipc::IOS_Ioctl(fd, ios::fs::IOCTL_FS_GET_FILE_STATS, nullptr, 0, &stats, sizeof(stats));
    
    CHECK_ERROR(ret, "IOS_Ioctl");
    
    return stats.length;
}

static u32 getLengthOld(s32 fd)
{
    u8 header[0x20] ALIGNED(NAND_ALIGN);
    read(fd, header, sizeof(header));

    return readBe32(header);
}

bool NandLoader::canLoad()
{
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    s32 fd = open(path, wii::ipc::IOS_OPEN_READ);

    if (fd == ios::fs::ERR_FS_ENOENT)
        return false;

    close(fd);

    return true;
}

void * NandLoader::loadImpl()
{
    char path[64];
    buildPath(path, sizeof(path), mFilename);

    s32 fd = open(path, wii::ipc::IOS_OPEN_READ);

    if (fd == ios::fs::ERR_FS_ENOENT)
        return nullptr;
    
    u32 length;
    if (mOldMode)
        length = getLengthOld(fd);
    else
        length = getLength(fd);
    
    void * mem = alloc(ALIGN_TO(length, IOS_ALIGN), IOS_ALIGN);
    CHECK_PTR(mem, length, "file alloc");

    read(fd, mem, length);

    close(fd);

    wii::os::OSReport("Read %s from NAND\n", mFilename);

    return mem;
}

}
