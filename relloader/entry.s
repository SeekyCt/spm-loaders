/*
    Place loader context & branch to the main function at binary start
*/

.section .first, "ax"

/*
    Command line define arguments
*/
#ifndef REL_LOADER_VERSION
    .err
#endif
#ifndef IMPLEMENTATION_TYPE
    .err
#endif
#ifndef IMPLEMENTATION_VERSION
    .err
#endif

/*
    Loader context struct - 0x80004200
*/

.global ctx
.type ctx, @object
ctx:

// 0x0 Magic
.ascii "RLd3"

// 0x4 Context version
.4byte 1

// 0x8 Implementation type
.4byte IMPLEMENTATION_TYPE

// 0xC Implementation version
.4byte IMPLEMENTATION_VERSION

// 0x10 Loader version
.4byte 1

// 0x14 Host rel context
.4byte 0

// 0x18 Reserved
.space 0x20 - 0x18

.size ctx, . - ctx

/*
    Entrypoint - 0x80004220
*/

.global entry
.type entry, @function
entry:
    b loaderMain
.size entry, . - entry
