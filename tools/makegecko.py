"""
Makes a gecko code to load and execute a statically-linked payload in RAM
"""

from argparse import ArgumentParser

from common import be32, make_branch_instr, Payload


IMPLEMENTATION_TYPE = 0
IMPLEMENTATION_VERSION = 1

DOLPHIN_MAX_CODESIZE = 0xcb8

def gecko_opword(opcode: int, addr: int) -> bytes:
    """Creates the opcode word of a gecko code"""

    opword = (opcode << 24) | (addr & 0x1ff_ffff)
    return be32(opword)


def make_bin_04(addr: int, bin_data: bytes) -> bytes:
    """Makes an 04 gecko code"""

    assert len(bin_data) == 4
    return gecko_opword(0x04, addr) + bin_data


def make_bin_06(bin_addr: int, bin_data: bytes) -> bytes:
    """Makes an 06 gecko code for a binary file"""

    opword = gecko_opword(0x06, bin_addr)

    sizeword = be32(len(bin_data))

    rounded_size = (len(bin_data) + 7) & ~7
    extra = rounded_size - len(bin_data)
    rounded = bin_data + bytes(extra)

    return opword + sizeword + rounded


def make_byte_28(addr: int, val: int) -> bytes:
    # Handle offset from 2-byte alignment
    if (addr & 1) == 0:
        mask = 0x00ff
        val <<= 16
    else:
        mask = 0xff00
        addr &= ~1
    
    opword = gecko_opword(0x28, addr)
    valword = be32((mask << 16) | val)
    
    return opword + valword


def make_bin_22(addr: int, bin_data: bytes) -> bytes:
    assert len(bin_data) == 4
    return gecko_opword(0x22, addr) + bin_data


def make_conditional_end() -> bytes:
    return gecko_opword(0xE0, 0) + be32(0x8000_8000)


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
    parser.add_argument("--revision", type=int, default=-1)
    args = parser.parse_args()

    # Get data
    payload = Payload(args.payload_path, IMPLEMENTATION_TYPE, IMPLEMENTATION_VERSION)

    # Calculate hook branch
    branch = make_branch_instr(payload.hook_addr, payload.entrypoint)

    # Make code
    code = (
        (make_byte_28(0x8000_0007, args.revision) if args.revision != -1 else bytes()) +
        make_bin_22(payload.hook_addr, branch) +
        make_bin_04(payload.hook_addr, branch) +
        make_bin_06(payload.load_addr, payload.data) +
        make_conditional_end()
    )

    assert len(code) < DOLPHIN_MAX_CODESIZE, f"Gecko code too big ({len(code)}/{DOLPHIN_MAX_CODESIZE} bytes)"

    # Convert to text
    txt = to_gecko_text(code)

    # Output
    with open(args.out_path, "w") as f:
        f.write(txt)
