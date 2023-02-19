"""
Patches a dol file to load an execute a statically-linked payload in RAM
"""

from argparse import ArgumentParser
from dataclasses import dataclass
import struct
from typing import List

from common import make_branch_instr, Payload


IMPLEMENTATION_TYPE = 1
IMPLEMENTATION_VERSION = 1


@dataclass
class DolSection:
    offs: int
    addr: int
    size: int

    def contains_addr(self, addr: int) -> bool:
        return self.addr <= addr < self.addr + self.size
    
    def addr_to_offs(self, addr: int) -> int:
        return addr - self.addr + self.offs

class DolReader:
    OFFS_SEC_OFFSETS = 0
    OFFS_SEC_ADDRS = 0x48
    OFFS_SEC_SIZES = 0x90

    data: bytearray
    sections: List[DolSection]

    def __init__(self, path: str):
        with open(path, "rb") as f:
            self.data = bytearray(f.read())
        
        offsets = [*struct.unpack_from(">18I", self.data, self.OFFS_SEC_OFFSETS)]
        addrs = [*struct.unpack_from(">18I", self.data, self.OFFS_SEC_ADDRS)]
        sizes = [*struct.unpack_from(">18I", self.data, self.OFFS_SEC_SIZES)]
        self.sections = [
            DolSection(offs, addr, size)
            for offs, addr, size in zip(offsets, addrs, sizes)
        ]

    def addr_to_offs(self, addr: int) -> int:
        for sec in self.sections:
            if sec.contains_addr(addr):
                return sec.addr_to_offs(addr)
        return -1

    def write(self, addr: int, data: bytes):
        offs = self.addr_to_offs(addr)
        self.data[offs:offs+len(data)] = data

    def write_branch(self, hook_addr: int, dest: int):
        branch = make_branch_instr(hook_addr, dest)
        self.write(hook_addr, branch)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("dol_path", type=str)
    parser.add_argument("payload_path", type=str)
    parser.add_argument("out_path", type=str)
    args = parser.parse_args()

    dol = DolReader(args.dol_path)
    payload = Payload(args.payload_path, IMPLEMENTATION_TYPE, IMPLEMENTATION_VERSION)
    dol.write_branch(payload.hook_addr, payload.entrypoint)
    dol.write(payload.load_addr, payload.data)

    with open(args.out_path, "wb") as f:
        f.write(dol.data)
