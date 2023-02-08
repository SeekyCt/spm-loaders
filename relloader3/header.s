/*
    Place loader context & branch to the main function at binary start
*/

.section .first, "ax"

/*
    Command line define arguments
*/

#ifndef IMPLEMENTATION_TYPE
    .err
#endif
#ifndef IMPLEMENTATION_VERSION
    .err
#endif

/*
    Payload header struct - 0x80004200
*/

.global header
.type header, @object
header:

#define PAYLOAD_MAGIC "RLd3"
#define PAYLOAD_VERSION 1
#define CONTEXT loaderCtx
#define LOAD_ADDRESS 0x80004200
#define ENTRYPOINT loaderMain
#define HOOK_ADDRESS (spmarioInit + 0x6f8)

#include "payloadheader.inc"

.size header, . - header
