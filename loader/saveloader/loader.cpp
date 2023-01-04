#include <common.h>
#include <spm/spmario.h>
#include <wii/os.h>
#include <msl/string.h>

#include "context.h"

struct Payload
{
    u8 * dest;
    u32 length;
    u8 data[];
};

typedef void (Entry)();

extern "C" void loaderMain();
void loaderMain()
{
    wii::os::OSReport("Save Loader - v1\n");

    Payload * payload = (Payload *) &spm::spmario::gp->gsw[0x400];
    msl::string::memcpy(payload->dest, payload->data, payload->length);
    Entry * entry = (Entry *)(payload->dest + sizeof(RelLoaderContext));
    entry();
}
