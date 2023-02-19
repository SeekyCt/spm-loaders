import struct


def be32(val: int) -> bytes:
    """Converts an integer to big-endian 32-bit"""

    return int.to_bytes(val, 4, "big")


def make_branch_instr(hook_addr: int, dest: int) -> bytes:
    """Makes the bytes for a branch instruction from hook_addr to dest"""

    delta = dest - hook_addr
    return be32(0x4800_0000 | (delta & 0x03FF_FFFC))


class Payload:
    """Reader for a payload file"""

    data: bytes

    payload_magic: int
    payload_ver: int
    context: int
    load_addr: int
    entrypoint: int
    hook_addr: int
    impl_type: int
    impl_ver: int

    HEADER_SIZE = 0x28

    def __init__(self, path: str, impl_type: int, impl_ver: int):
        # Load raw data
        with open(path, 'rb') as f:
            data = bytearray(f.read())

        # Patch implementation type
        struct.pack_into(">II", data, 0x20, impl_type, impl_ver)

        # Parse header
        (
            header_magic, header_ver, payload_magic, payload_ver, context, load_addr, entrypoint,
            hook_addr, impl_type, impl_ver
        ) = struct.unpack(">4sI4sIIIIIII", data[:self.HEADER_SIZE])

        assert header_magic == b"SPMP"
        assert header_ver == 1

        self.data = bytes(data)
        self.payload_magic = payload_magic
        self.payload_ver = payload_ver
        self.context = context
        self.load_addr = load_addr
        self.entrypoint = entrypoint
        self.hook_addr = hook_addr
        self.impl_type = impl_type
        self.impl_ver = impl_ver
