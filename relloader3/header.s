/*
    Place loader context & branch to the main function at binary start
*/

.section .first, "ax"

/*
    Payload header struct - 0x80004200
*/

.global header
.type header, @object
header:

// TODO
#if defined SPM_EU0 || defined SPM_EU1
#define HOOK_OFFS 0x6f8
#elif defined SPM_US0
#define HOOK_OFFS 0x590
#else
.err
#endif

#define PAYLOAD_MAGIC "RLd3"
#define PAYLOAD_VERSION 1
#define CONTEXT loaderCtx
#define LOAD_ADDRESS 0x80004200
#define ENTRYPOINT loaderMain
#define HOOK_ADDRESS (spmarioInit + HOOK_OFFS)

#include "spm_loaders/payloadheader.inc"

.size header, . - header
