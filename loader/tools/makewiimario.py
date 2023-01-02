from math import ceil
from typing import Tuple
from common import be32


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

    ADDR = {
        "eu0": 0x80525550
    }


class SaveFile:
    """SaveFile struct constants"""

    OFFS_POUCH = 0x1b10


class PouchWork:
    """PouchWork struct constsnts"""

    OFFS_USE_ITEMS = 0x60
    OFFS_SHOP_ITEMS = 0x74
    OFFS_CATCH_CARDS = 0x10c

    ADDR = {
        "eu0": 0x80511a28
    }

    def addr_to_save_offs(version: str, addr: int) -> int:
        return addr - PouchWork.ADDR[version] + SaveFile.OFFS_POUCH


class StackFrame:
    """pausewinSetMessage stack frame constants"""

    SIZE = 0xa0
    OFFS_STR = 0x10


def find_desc_msg_loc(version: str) -> Tuple[int, int]:
    """Finds an item id and offset can be used for a fake descMsg pointer

    This needs to be a multiple of sizeof(ItemData) away from itemDataTable
    + offsetof(ItemData, descMsg) so that itemDataTable[x].descMsg would read it
    """

    # shopItems has 0x40 safe bytes to use, so an aligned address exists in it
    shop_items_addr = PouchWork.ADDR[version] + PouchWork.OFFS_SHOP_ITEMS

    # Find the first address within shopItems that's aligned to be used
    desc_addr = ItemData.ARRAY_ADDR[version] + ItemData.OFFS_DESC_MSG
    item_id = ceil((shop_items_addr - desc_addr) / ItemData.SIZE)
    addr = desc_addr + item_id * ItemData.SIZE
    save_offs = PouchWork.addr_to_save_offs(version, addr)
    return item_id, save_offs


def make_exploit_string(payload_addr: int) -> bytes:
    padding = b"\x11" * (StackFrame.SIZE - StackFrame.OFFS_STR)
    return padding + be32(payload_addr) + b"\x00"


def patch_wiimario(save: bytes, payload: bytes) -> bytes:
    data = bytes(save)

    return bytes(data)
