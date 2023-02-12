/*
    Define the following when including:
        PAYLOAD_MAGIC
        PAYLOAD_VERSION
        CONTEXT
        LOAD_ADDRESS
        ENTRYPOINT
        HOOK_ADDRESS
*/

// 0x00 Header Magic
.ascii "SPMP"

// 0x04 Header Version
.4byte 1

// 0x08 Payload Magic
.ascii PAYLOAD_MAGIC

// 0x0C Payload Version
.4byte PAYLOAD_VERSION

// 0x10 Context
.4byte CONTEXT

// 0x14 Load Address
.4byte LOAD_ADDRESS

// 0x18 Entrypoint
.4byte ENTRYPOINT

// 0x1C Hook Address
.4byte HOOK_ADDRESS

// 0x20 Implementation type
.4byte -1

// 0x24 Implementation version
.4byte -1
