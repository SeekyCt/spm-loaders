"""
Makes a save file to load and execute a payload

Note that a payload here is just a flat binary which starts execution
from its beginning address (such as saveloader), not the payload format
used by the rest of the repo.

Save file parts used:
    MarioPouchWork.shopItems: fake descMsg pointer
    MarioPouchWork.catchCards: fake descMsg string
    SpmarioGlobals.lswf,lsw,coinEntries: payload

This script makes no assumptions about the payload itself, other
than it expecting to run from the lswf position
"""

from argparse import ArgumentParser
from math import ceil
from struct import pack_into
from typing import Tuple

"""
Big endian binary helpers
"""


def be32(val: int) -> bytes:
    """Converts an integer to big-endian 32-bit"""

    return int.to_bytes(val, 4, "big")


def write_u32(data: bytearray, offs: int, val: int):
    pack_into(">I", data, offs, val)


def write_u16(data: bytearray, offs: int, val: int):
    pack_into(">H", data, offs, val)


def write_bytes(data: bytearray, offs: int, val: bytes):
    data[offs:offs+len(val)] = val


def write_str(data: bytearray, offs: int, val: str):
    enc = val.encode("ascii") + b"\x00"
    write_bytes(data, offs, enc)


"""
Game struct definitions, no exploit implementation specific logic or information
"""


class ItemData:
    """ItemData struct constants"""

    SIZE = 0x2c
    OFFS_DESC_MSG = 0x14

    ARRAY_ADDR = {
        "eu0": 0x803f5f98,
        "eu1": 0x803f5f98,
        # TODO
        "us0": 0,
        "us1": 0,
        "us2": 0,
        "jp0": 0,
        "jp1": 0,
        "kr0": 0,
    }


class SpmarioGlobals:
    """SpmarioGlobals struct constants"""

    SIZE = 0x1b08

    OFFS_FRAMEBUFFER_WIDTH = 0x18
    OFFS_FRAMEBUFFER_HEIGHT = 0x1A
    OFFS_SAVE_NAME = 0x20
    OFFS_MAP_NAME = 0x44
    OFFS_LSWF = 0xD44

    SIZE_LSWF = 0x40
    SIZE_LSW = 0x400
    SIZE_COIN_ENTRIES = 0x900

    ADDR = {
        "eu0": 0x80525550,
        "eu1": 0x80525550,
        # TODO
        "us0": 0,
        "us1": 0,
        "us2": 0,
        "jp0": 0,
        "jp1": 0,
        "kr0": 0,
    }

    @staticmethod
    def make_default(name: str, map: str) -> bytes:
        spmg = bytearray(SpmarioGlobals.SIZE)

        # Set the default efb width and height, as they can prevent being able to open the item menu
        write_u16(spmg, SpmarioGlobals.OFFS_FRAMEBUFFER_WIDTH, 608)
        write_u16(spmg, SpmarioGlobals.OFFS_FRAMEBUFFER_HEIGHT, 480)

        # Write the new file name
        write_str(spmg, SpmarioGlobals.OFFS_SAVE_NAME, name)

        # Write the map name
        write_str(spmg, SpmarioGlobals.OFFS_MAP_NAME, map)

        return bytes(spmg)


class MarioPouchWork:
    """MarioPouchWork struct constsnts"""

    SIZE = 0x6a0

    OFFS_LEVEL = 0x4
    OFFS_FLIP_TIMER = 0x14
    OFFS_USE_ITEMS = 0x60
    OFFS_SHOP_ITEMS = 0x74
    OFFS_CATCH_CARDS = 0x10c
    OFFS_MINIGAME_SCORES = 0x368

    ADDR = {
        "eu0": 0x80511a28,
        "eu1": 0x80511a28,
        # TODO
        "us0": 0,
        "us1": 0,
        "us2": 0,
        "jp0": 0,
        "jp1": 0,
        "kr0": 0,
    }

    @staticmethod
    def make_default() -> bytes:
        pouch = bytearray(MarioPouchWork.SIZE)

        # Set Mario's level to 1, to prevent leveling up immediately
        write_u32(pouch, MarioPouchWork.OFFS_LEVEL, 1)

        # Set the flip timer to 10 to prevent counting up immediately
        write_u32(pouch, MarioPouchWork.OFFS_FLIP_TIMER, 10)

        return bytes(pouch)


class SaveFile:
    """SaveFile struct constants"""

    SIZE = 0x25b8

    HEADER_SIZE = 0x8
    OFFS_UNK = 0x21b0
    UNK_SIZE = 0x400

    OFFS_POUCH = 0x1b10

    @staticmethod
    def build(spmg: bytes, pouch: bytes) -> bytes:
        assert len(spmg) == 0x1b08 == SpmarioGlobals.SIZE
        assert len(pouch) == 0x6a0 == MarioPouchWork.SIZE
        header = bytes(SaveFile.HEADER_SIZE)
        unk = bytes(SaveFile.UNK_SIZE)
        main_save = header + spmg + pouch + unk
        checksum = sum(main_save) + (0xff * 4)
        return (
            main_save + be32(checksum) + be32(~checksum & 0xffff_ffff)
        )


class StackFrame:
    """pausewinSetMessage stack frame constants"""

    SIZE = 0xa0
    OFFS_LR_SAVE = SIZE + 4
    OFFS_STR = 0x10


"""
Exploit implementation
"""


def find_desc_msg_loc(version: str) -> Tuple[int, int]:
    """Finds an item id and offset that can be used for a fake descMsg pointer

    This needs to be a multiple of sizeof(ItemData) away from itemDataTable
    + offsetof(ItemData, descMsg) so that itemDataTable[x].descMsg would read it
    """

    # shopItems has 0x40 safe bytes to use, so an aligned address exists in it
    shop_items_addr = MarioPouchWork.ADDR[version] + MarioPouchWork.OFFS_SHOP_ITEMS

    # Find the first address within shopItems that's aligned to be used
    desc_addr = ItemData.ARRAY_ADDR[version] + ItemData.OFFS_DESC_MSG
    item_id = ceil((shop_items_addr - desc_addr) / ItemData.SIZE)
    addr = desc_addr + item_id * ItemData.SIZE
    pouch_offs = addr - MarioPouchWork.ADDR[version]
    return item_id, pouch_offs


def make_exploit_string(payload_addr: int) -> bytes:
    """Makes the string to copy onto the stack in the buffer overflow

    This string overwrites the lr save of the stack frame above with the payload address
    """
    padding = b"\x11" * (StackFrame.OFFS_LR_SAVE - StackFrame.OFFS_STR)
    return padding + be32(payload_addr) + b"\x00"


def patch_wiimario(spmg: bytes, pouch: bytes, payload: bytes, version: str) -> Tuple[bytes, bytes]:
    """Patches a wiimario save file's SpmarioGlobals and MarioPouchWork sections to execute a
    payload through the exploit"""

    spmg = bytearray(spmg)
    pouch = bytearray(pouch)

    # Calculate addresses and offsets
    desc_msg_offs = MarioPouchWork.OFFS_CATCH_CARDS
    desc_msg_addr = MarioPouchWork.ADDR[version] + desc_msg_offs
    item_id, desc_msg_ptr_offs = find_desc_msg_loc(version)
    payload_offs = SpmarioGlobals.OFFS_LSWF
    max_size = (
        SpmarioGlobals.SIZE_LSWF +
        SpmarioGlobals.SIZE_LSW +
        SpmarioGlobals.SIZE_COIN_ENTRIES
    )
    assert len(payload) < max_size, f"Payload too big (0x{len(payload):x}/0x{max_size:x})"
    payload_addr = SpmarioGlobals.ADDR[version] + payload_offs

    # Write exploit string
    desc_msg = make_exploit_string(payload_addr)
    write_bytes(pouch, desc_msg_offs, desc_msg)

    # Write exploit string pointer
    write_u32(pouch, desc_msg_ptr_offs, desc_msg_addr)

    # Write item id
    write_u16(pouch, MarioPouchWork.OFFS_USE_ITEMS, item_id)

    # Write payload
    write_bytes(spmg, payload_offs, payload)

    return bytes(spmg), bytes(pouch)


if __name__ == "__main__":
    hex_int = lambda x: int(x, 16)
    parser = ArgumentParser()
    parser.add_argument("payload_path")
    parser.add_argument("save_name")
    parser.add_argument("version")
    parser.add_argument("out_path")
    args = parser.parse_args()

    # Get payload data
    with open(args.payload_path, "rb") as f:
        payload = f.read()

    spmg = SpmarioGlobals.make_default(args.save_name, "dos_01")
    pouch = MarioPouchWork.make_default()
    spmg, pouch = patch_wiimario(spmg, pouch, payload, args.version)
    save = SaveFile.build(spmg, pouch)

    # Output
    with open(args.out_path, "wb") as f:
        f.write(save)
