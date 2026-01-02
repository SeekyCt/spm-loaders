"""
Makes a gecko code to load and execute a statically-linked payload in RAM
"""

from argparse import ArgumentParser

from common import be32, make_branch_instr, Payload


def gecko_opword(opcode: int, addr: int) -> bytes:
    """Creates the opcode word of a gecko code"""

    opword = (opcode << 24) | (addr & 0x1ff_ffff)
    return be32(opword)


def make_uint_04(addr: int, val: int) -> bytes:
    """Makes an 04 gecko code"""

    return gecko_opword(0x04, addr) + be32(val)


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

HEAPSIZE_PERCENT_REMAINING = 0
HEAPSIZE_ABSOLUTE_KB = 1

def make_size_table(data : list[tuple[int, int]]) -> bytes:
    ret = b""

    for (mode, size) in data:
        ret += be32(mode) + be32(size)

    return ret

new_size_table = make_size_table([
    (HEAPSIZE_ABSOLUTE_KB, 0x2400),
    (HEAPSIZE_ABSOLUTE_KB, 0x1800),
    (HEAPSIZE_PERCENT_REMAINING, 100),
    (HEAPSIZE_ABSOLUTE_KB, 0x100),
    (HEAPSIZE_ABSOLUTE_KB, 0x100),
    (HEAPSIZE_ABSOLUTE_KB, 0x80),
    (HEAPSIZE_ABSOLUTE_KB, 0x4400),
    (HEAPSIZE_PERCENT_REMAINING, 100),
    (HEAPSIZE_ABSOLUTE_KB, 1)
])


if __name__ == "__main__":
    hex_int = lambda x: int(x, 16)
    parser = ArgumentParser()
    parser.add_argument('region')
    args = parser.parse_args()

    region = args.region

    memInit = {
        "eu0": 0x801a5dcc,
        "jp0": 0x801a5184,
        "jp1": 0x801a51cc,
        "us0": 0x801a5194,
        "us1": 0x801a51f0,
        "us2": 0x801a5508,
    }[region]

    size_table = {
        "eu0": 0x8042a408,
        "jp0": 0x803bfc68,
        "jp1": 0x803c0de8,
        "us0": 0x803eaa08,
        "us1": 0x803ebd68,
        "us2": 0x803ebf48,
    }[region]

    hudDisp = {
        "eu0": 0x8019a16c,
        "us0": 0x8019933c,
        "us1": 0x80199398,
        "us2": 0x801997a8,
        "jp0": 0x8019932c,
        "jp1": 0x80199374,
    }[region]
    hudDisp_hook = {
        "eu0": 0x33c,
        "eu1": 0x33c,
        "us0": 0x2f8,
        "us1": 0x2f8,
        "us2": 0x2f8,
        "jp0": 0x2f8,
        "jp1": 0x2f8,
    }[region]

    # Make code
    code = (
        make_uint_04(memInit + 0xa0, 0x2c1d0003) +
        make_uint_04(memInit + 0x178, 0x2c1b0003) +
        make_uint_04(memInit + 0x1b0, 0x2c190003) +
        make_uint_04(memInit + 0x1e0, 0x3b600003) +
        make_uint_04(memInit + 0x1e4, 0x3b240018) +
        make_uint_04(memInit + 0x1e8, 0x3b40000c) +
        make_uint_04(memInit + 0x274, 0x3b600003) +
        make_uint_04(memInit + 0x278, 0x3be30018) +
        make_uint_04(memInit + 0x27c, 0x3bc0000c) +
        make_uint_04(memInit + 0x344, 0x3b200003) +
        make_uint_04(memInit + 0x348, 0x3b00000c) + 
        make_bin_06(size_table, new_size_table) +

        make_uint_04(hudDisp + hudDisp_hook, 0x98810054) # Discolour HP bar
    )

    # Convert to text
    txt = to_gecko_text(code)

    print(txt)
