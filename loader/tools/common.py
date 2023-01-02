from enum import IntEnum
import struct


class Context:
    SIZE = 0x20

    OFFS_LOADER_TYPE = 0x8
    OFFS_LOADER_VERSION = 0xc


class LoaderType(IntEnum):
    UNSET = -1
    GECKO = 0
    DOL = 1
    RIIVOLUTION = 2
    SAVE = 3


def be32(val: int) -> bytes:
    """Converts an integer to big-endian 32-bit"""

    return int.to_bytes(val, 4, "big")


def write_u32(data: bytearray, offs: int, val: int):
    struct.pack_into(">I", data, offs, val)
