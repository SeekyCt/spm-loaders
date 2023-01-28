#!/usr/bin/env python3
from argparse import ArgumentParser
from dataclasses import dataclass
import os
from typing import List, Tuple


@dataclass
class DolSymbol:
    addr: int
    name: str


@dataclass
class RelSymbol:
    module_id: int
    section_id: int
    offset: int
    name: str


def load_lst(filename: str) -> Tuple[List[DolSymbol], List[RelSymbol]]:
    # Load LST
    with open(filename) as f:
        lines = f.readlines()

    # Parse lines
    dol_symbols = []
    rel_symbols = []
    for i, line in enumerate(lines):
        # Ignore comments and whitespace
        line = line.strip()
        if line.startswith("/") or len(line) == 0:
            continue

        # Try parse
        try:
            # Dol - addr:name
            # Rel - moduleId,sectionId,offset:name
            colon_parts = [s.strip() for s in line.split(":")]
            other, name = colon_parts
            comma_parts = [s.strip() for s in other.split(',')]
            if len(comma_parts) == 1:
                addr, = comma_parts
                dol_symbols.append(
                    DolSymbol(
                        int(addr, 16),
                        name
                    )
                )
            else:
                module_id, section_id, offset = comma_parts
                rel_symbols.append(
                    RelSymbol(
                        int(module_id, 0),
                        int(section_id, 0),
                        int(offset, 16),
                        name
                    )
                )
                # ignore rel symbols
        except Exception as e:
            raise Exception(f"Error on line {i+1}: {e}")

    return dol_symbols, rel_symbols


def make_ld(symbols: List[DolSymbol]) -> str:
    return '\n'.join([
        f"PROVIDE({sym.name} = 0x{sym.addr:x});"
        for sym in symbols
    ])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("lst_path")
    parser.add_argument("ld_path")
    args = parser.parse_args()

    dol_symbols, _ = load_lst(args.lst_path)
    txt = make_ld(dol_symbols)
    with open(args.ld_path, 'w') as f:
        f.write(txt)
