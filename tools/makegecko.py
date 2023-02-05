"""
Makes a gecko code to load and execute a statically-linked payload in RAM
"""

from argparse import ArgumentParser
import struct


class Payload:
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

    def __init__(self, path: str):
        with open(path, 'rb') as f:
            self.data = f.read()

        (
            header_magic, header_ver, payload_magic, payload_ver, context, load_addr, entrypoint,
            hook_addr, impl_type, impl_ver
        ) = struct.unpack(">4sI4sIIIIIII", self.data[:self.HEADER_SIZE])

        assert header_magic == b"SPMP"
        assert header_ver == 1

        self.payload_magic = payload_magic
        self.payload_ver = payload_ver
        self.context = context
        self.load_addr = load_addr
        self.entrypoint = entrypoint
        self.hook_addr = hook_addr
        self.impl_type = impl_type
        self.impl_ver = impl_ver


def be32(val: int) -> bytes:
    """Converts an integer to big-endian 32-bit"""

    return int.to_bytes(val, 4, "big")


def gecko_opword(opcode: int, addr: int) -> bytes:
    """Creates the opcode word of a gecko code"""

    opword = (opcode << 24) | (addr & 0x1ff_ffff)
    return be32(opword)


def make_branch_04(hook_addr: int, dest: int) -> bytes:
    """Makes an 04 gecko code for a branch"""

    opword = gecko_opword(0x04, hook_addr)

    delta = dest - hook_addr
    branch = 0x4800_0000 | (delta & 0x03FF_FFFC)
    val = be32(branch)

    return opword + val


def make_bin_06(bin_addr: int, bin_data: bytes) -> bytes:
    """Makes an 06 gecko code for a binary file"""

    opword = gecko_opword(0x06, bin_addr)

    sizeword = be32(len(bin_data))

    rounded_size = (len(bin_data) + 7) & ~7
    extra = rounded_size - len(bin_data)
    rounded = bin_data + bytes(extra)

    return opword + sizeword + rounded


def to_gecko_text(code: bytes) -> str:
    """Convertes a binary gecko code to text representation"""

    # TODO: this can probably be nicer
    txt = code.hex().upper()
    ret = []
    for i in range(0, len(txt), 16):
        first = txt[i:i+8]
        second = txt[i+8:i+16]
        ret.append(f"{first} {second}")
    return '\n'.join(ret)


if __name__ == "__main__":
    hex_int = lambda x: int(x, 16)
    parser = ArgumentParser()
    parser.add_argument("payload_path", type=str)
    parser.add_argument("out_path", type=str)
    args = parser.parse_args()

    # Get data
    payload = Payload(args.payload_path)

    # Make code
    code = (
        make_branch_04(payload.hook_addr, payload.entrypoint) +
        make_bin_06(payload.load_addr, payload.data)
    )

    # Convert to text
    txt = to_gecko_text(code)

    # Output
    with open(args.out_path, "w") as f:
        f.write(txt)
