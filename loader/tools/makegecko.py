from argparse import ArgumentParser

CTX_SIZE = 0x20
CTX_TYPE_OFFS = 0x8
CTX_VERSION_OFFS = 0xc

LOADER_TYPE = 0
LOADER_VERSION = 1

def be32(val: int) -> bytes:
    """Converts an integer to big-endian 32-bit"""

    return int.to_bytes(val, 4, "big")

def patch_context(data: bytes) -> bytes:
    """Patch the context of the loader"""

    data = bytearray(data)

    # Loader type
    data[CTX_TYPE_OFFS:CTX_TYPE_OFFS+4] = be32(LOADER_TYPE)

    # Loader version
    data[CTX_VERSION_OFFS:CTX_VERSION_OFFS+4] = be32(LOADER_VERSION)

    return bytes(data)


def gecko_opword(opcode: int, addr: int) -> bytes:
    """Creates the opcode word of a gecko code"""

    opword = (opcode << 24) | (addr & 0x1ff_ffff)
    return be32(opword)


def make_branch_04(hook_addr: int, bin_addr: int, link: bool = False) -> bytes:
    """Makes an 04 gecko code for a branch"""

    opword = gecko_opword(0x04, hook_addr)

    delta = bin_addr - hook_addr
    branch = 0x4800_0000 | (delta & 0x03FF_FFFC)
    if link:
        branch |= 1
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
    parser.add_argument("hook_addr", type=hex_int)
    parser.add_argument("bin_addr", type=hex_int)
    parser.add_argument("bin_path")
    parser.add_argument("out_path")
    args = parser.parse_args()

    # Get data
    with open(args.bin_path, "rb") as f:
        data = f.read()
    
    # Patch header
    data = patch_context(data)

    # Make code
    code = (
        make_branch_04(args.hook_addr, args.bin_addr + CTX_SIZE, True) +
        make_bin_06(args.bin_addr, data)
    )

    # Convert to text
    txt = to_gecko_text(code)

    # Output
    with open(args.out_path, "w") as f:
        f.write(txt)

