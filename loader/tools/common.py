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


def write_u16(data: bytearray, offs: int, val: int):
    struct.pack_into(">H", data, offs, val)


def write_bytes(data: bytearray, offs: int, val: bytes):
    data[offs:offs+len(val)] = val


def write_str(data: bytearray, offs: int, val: str):
    enc = val.encode("ascii") + b"\x00"
    write_bytes(data, offs, enc)


def patch_context(data: bytes, loader_type: int, loader_version: int) -> bytes:
    """Patch the context of the loader"""

    data = bytearray(data)

    write_u32(data, Context.OFFS_LOADER_TYPE, loader_type)
    write_u32(data, Context.OFFS_LOADER_VERSION, loader_version)

    return bytes(data)
