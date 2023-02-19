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

void NORETURN assertionError(const char * file, s32 line, const char * function, s32 code,
                             const char * context)
{
    char message[128];

    msl::stdio::snprintf(
        message,
        sizeof(message),
        "%s line %d (%s):\nfailed %s with %d",
        file,
        line,
        function,
        context,
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
        "[%d|%d|%d] %s",
        relloader3::RelLoaderHeader::instance->implementationType,
        relloader3::RelLoaderHeader::instance->implementationVersion,
        relloader3::RelLoaderHeader::instance->payloadVersion,
        message
    );

    static const wii::gx::GXColor fg = {0xff, 0xff, 0xff, 0xff};
    static const wii::gx::GXColor bg = {0x00, 0x00, 0x00, 0xff};
    wii::os::OSFatal(&fg, &bg, fullMessage);
}

}
