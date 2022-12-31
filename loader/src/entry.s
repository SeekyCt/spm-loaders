/*
    Place a branch to the main function at the start of the binary
*/

.section .first, "ax"

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

// 0x8 Loader type
// Implementations should patch this
.4byte -1

// 0xC Loader version
// Implementations should patch this
.4byte -1

// 0x10 Host rel context
.4byte 0

// 0x14 Reserved
.space 0x20 - 0x14

.size ctx, . - ctx

/*
    Entrypoint - 0x80004220
*/

.global entry
.type entry, @function
entry:
    mflr r0
    stwu r1, -0x10 (r1)
    stw r0, 0x14 (r1)

    // Run main loader
    bl loaderMain

    // Default instruction at hook
    li r3, 0

    lwz r0, 0x14  (r1)
    mtlr r0
    addi r1, r1, 0x10
    blr
.size entry, . - entry
