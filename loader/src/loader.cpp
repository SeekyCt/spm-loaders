#include <spm/dvdmgr.h>
#include <spm/memory.h>
#include <wii/gx.h>
#include <wii/ipc.h>
#include <wii/nand.h>
#include <wii/os.h>
#include <ios/ios.h>
#include <ios/fs.h>
#include <msl/stdio.h>
#include <msl/string.h>

#define ALIGN_TO(val, align) (((val) + ((align)-1)) & ~((align)-1))

struct LoaderContext
{
/* 0x00 */ char magic[4]; // RLd3
/* 0x04 */ u32 contextVersion;
/* 0x08 */ s32 loaderType;
/* 0x0C */ s32 loaderVersion;
/* 0x10 */ void * hostRelContext;
};
extern LoaderContext ctx;

static const wii::gx::GXColor fg = {0xff, 0xff, 0xff, 0xff};
static const wii::gx::GXColor bg = {0x00, 0x00, 0x00, 0xff};

// TODO: consider adding function names
static void NORETURN errorPanic(const char * file, s32 line, const char * function, s32 code,
                                const char * context)
{
    char message[128];
    msl::stdio::sprintf(
        message,
        "[%d %d] %s line %d (%s): failed %s with %d",
        ctx.loaderType,
        ctx.loaderVersion,
        file,
        line,
        function,
        context,
        code
    );
    wii::os::OSFatal(&fg, &bg, message);
}

#define ERROR(code, context) errorPanic(__FILE__, __LINE__, __FUNCTION__, code, context)
#define CHECK_ERROR(code, ctx) if (code < 0) ERROR(code, ctx)
#define CHECK_TRUE(condition, context) if (!condition) ERROR(0, context)
#define CHECK_PTR(ptr, size, context) if (ptr == nullptr) ERROR(size, context)

#ifdef SPM_EU0
    #define FILENAME "eu0.rel"
#elif defined SPM_EU1
    #define FILENAME "eu1.rel"
#elif defined SPM_US0
    #define FILENAME "us0.rel"
#elif defined SPM_US1
    #define FILENAME "us1.rel"
#elif defined SPM_US2
    #define FILENAME "us2.rel"
#elif defined SPM_JP0
    #define FILENAME "jp0.rel"
#elif defined SPM_JP1
    #define FILENAME "jp1.rel"
#elif defined SPM_KR0
    #define FILENAME "kr0.rel"
#endif

static void * alloc(size_t size, u32 alignment = 0)
{
    alignment = alignment > 0x20 ? alignment : 0x20;
    auto handle = spm::memory::memory_wp->heapHandle[spm::memory::HEAP_MEM1_UNUSED];
    return wii::mem::MEMAllocFromExpHeapEx(handle, size, alignment);
}

static wii::os::RelHeader * tryNandLoad()
{
    char path[64];
    s32 ret;

    // Build path
    wii::nand::NANDGetHomeDir(path);
    msl::string::strcat(path, "/" FILENAME);

    // Try open
    s32 fd = wii::ipc::IOS_Open(path, wii::ipc::IOS_OPEN_READ);
    if (fd == ios::fs::ERR_FS_ENOENT)
        return nullptr;
    CHECK_ERROR(fd, "IOS_Open");

    // Get length
    ios::fs::FsFileStats ALIGNED(IOS_ALIGN) stats;
    ret = wii::ipc::IOS_Ioctl(fd, ios::fs::IOCTL_FS_GET_FILE_STATS, nullptr, 0, &stats, sizeof(stats));
    CHECK_ERROR(ret, "IOS_Ioctl");
    u32 length = ALIGN_TO(stats.length, IOS_ALIGN);

    // Allocate memory
    auto * rel = (wii::os::RelHeader *) alloc(length, IOS_ALIGN);
    CHECK_PTR(rel, length, "rel alloc");

    // Read rel
    ret = wii::ipc::IOS_Read(fd, rel, stats.length);
    CHECK_ERROR(ret, "IOS_Read");

    // Close
    ret = wii::ipc::IOS_Close(fd);
    CHECK_ERROR(ret, "IOS_Close");

    wii::os::OSReport("Read from NAND\n");
    return rel;
}

static wii::os::RelHeader * tryDvdLoad()
{
    // Build path
    const char * path = "./mod/" FILENAME;

    // Try open
    spm::dvdmgr::DVDEntry * entry = spm::dvdmgr::DVDMgrOpen(path, 2, 0);
    if (entry == nullptr)
        return nullptr;

    // Get length
    u32 length = ALIGN_TO(spm::dvdmgr::DVDMgrGetLength(entry), DVD_ALIGN);
 
    // Allocate memory
    auto * rel = (wii::os::RelHeader *) alloc(length, DVD_ALIGN);
    CHECK_PTR(rel, length, "rel alloc");

    // Try read
    spm::dvdmgr::DVDMgrRead(entry, rel, length, 0);

    // Close
    spm::dvdmgr::DVDMgrClose(entry);

    wii::os::OSReport("Read from DVD\n");
    return rel;
}

extern "C" void loaderMain();
void loaderMain()
{
    wii::os::OSReport("Rel Loader 3 - v1\n");

    // Load rel from somewhere
    wii::os::RelHeader * rel =  tryDvdLoad();
    if (rel == nullptr)
        rel = tryNandLoad();
    if (rel == nullptr)
        wii::os::OSFatal(&fg, &bg, "Error: rel not found on disc or in save file");

    // Allocate bss
    void * bss = alloc(rel->bssSize, rel->bssAlign);
    CHECK_PTR(bss, rel->bssSize, "bss alloc");

    // Link
    bool ret = wii::os::OSLink(rel, bss);
    CHECK_TRUE(ret, "OSLink");

    // Call prolog
    rel->prolog();
}
