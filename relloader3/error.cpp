#include <common.h>
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

#include <spm_loaders/relloader.h>

#include "error.h"

namespace relloader3 {

static s32 loaderUsed = -1;

void logLoaderUsed(s32 loader)
{
    wii::os::OSReport("Use loader %d\n", loader);
    loaderUsed = loader;
}

static void printStackTrace(char * dest, u32 destSize)
{
    u32 * p = (u32 *) __builtin_frame_address(0);
    s32 i = 0;
    while (0x80000000 <= (u32)p && (u32)p <= 0x81ffffff && destSize > 0)
    {
        // Write lr save to output
        u32 lr = p[1];
        const char * end;
        if (i % 4 == 3)
            end = "<-\n";
        else
            end = "<-";
        u32 numWrote = msl::stdio::sprintf(dest, "%08x%s", lr, end);
        dest += numWrote;
        destSize -= numWrote;

        // Move to next frame
        p = (u32 *)p[0];
        i += 1;
    }
}

void NORETURN assertionError(const char * file, s32 line, s32 code)
{
    char message[256];

    u32 numWrote = msl::stdio::snprintf(
        message,
        sizeof(message),
        "[%c|%d|%d|%d|%d|%d] %s %d %d\n",
        *(char *)0x80000003,
        *(u8 *)0x80000007,
        relloader3::RelLoaderHeader::instance->implementationType,
        relloader3::RelLoaderHeader::instance->implementationVersion,
        relloader3::RelLoaderHeader::instance->payloadVersion,
        loaderUsed,
        file,
        line,
        code
    );
    printStackTrace(message + numWrote, sizeof(message) - numWrote);

    error(message);
}

void NORETURN error(const char * message)
{
    static const wii::gx::GXColor fg = {0xff, 0xff, 0xff, 0xff};
    static const wii::gx::GXColor bg = {0x00, 0x00, 0x00, 0xff};
    wii::os::OSFatal(&fg, &bg, message);
}

}
