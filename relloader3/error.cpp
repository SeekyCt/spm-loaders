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

void NORETURN assertionError(const char * file, s32 line, s32 code)
{
    char message[128];

    msl::stdio::snprintf(
        message,
        sizeof(message),
        "%s line %d:\nfailed with %d",
        file,
        line,
        code
    );

    error(message);
}

void NORETURN error(const char * message)
{
    char fullMessage[256];

    msl::stdio::snprintf(
        fullMessage,
        sizeof(fullMessage),
        "[%d|%d|%d|%d] %s",
        relloader3::RelLoaderHeader::instance->implementationType,
        relloader3::RelLoaderHeader::instance->implementationVersion,
        relloader3::RelLoaderHeader::instance->payloadVersion,
        loaderUsed,
        message
    );

    static const wii::gx::GXColor fg = {0xff, 0xff, 0xff, 0xff};
    static const wii::gx::GXColor bg = {0x00, 0x00, 0x00, 0xff};
    wii::os::OSFatal(&fg, &bg, fullMessage);
}

}
