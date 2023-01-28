# spm-loaders

Loader source code for the following rel loader implementations:
- Gecko code
- Save exploit
- Riivolution (TODO)
- Dol patch (TODO)

This repo contains some generalised loader components, and a specific standard design built off of those.
See [Components](#components) for details of the components, and [STANDARD.MD] for the more specific details.

## Memory Usage

A certain range of RAM across all regions is reserved for this: 80004200 - 800060bb (inclusive)
- 80004200 - 80005000 is relloader
- 80005000 - 800060bb is space for saveloader if needed
- This range can be patched in a dol easily
- This is part of the TRK interrupt table, which goes unused and is in the same place in all versions
- Technically, anything from the TRK string at 80004188 could've been used
    - The starting address chosen is slightly nicer
    - This still leaves some space for future standards to use, should that be needed

## Components

The components are split into 2 categories:
- Payload (end goal code to run)
    - relloader
- Implementations (loaders & executors of generic payloads)
    - saveloader + makewiimario
    - makegecko
    - dol (TODO)
    - riivo (TODO)

### relloader

relloader is the main rel loader payload, shared between all implementations.

- This expects to be loaded at 80004200
    - For compatibility with saveloader, this limits the size to 0x800 bytes
- Entrypoint is 80004220
- This loads the file "./mod/rgX.rel" from disc if it exists, and falls back to "rgX.rel" in the save file if it doesn't
    - Where `rg` is `eu`, `us`, `jp` or `kr` for the region of the game, and `X` is 0-2 for the revision of the game
- The loader code itself doesn't assume a specific hook location, though it must be after memInit and dvdmgrInit
- The following defines should be given when building:
    - REL_LOADER_VERSION: version of the relloader payload itself
    - IMPLEMENTATION_TYPE: type of implementation this is being built for use in
    - IMPLEMENTATION_VERSION: version of implementation this is being built for use in
- The rel is placed on the unused MEM1 heap (id 2) if there's space, or the main MEM1 heap (id 1) otherwise

### saveloader

saveloader is the code to run in the save file exploit, to act as a payload implementation. It reboots the game, puts a bundled
payload (ex. relloader) at a specified address, and inserts a branch to it at a specified address from a specified hook address.
It will preserve itself on future game reboots and re-apply the payload hook.

- This is written as position independent assembly code
- No assumption is made about the position of this loader in the save file
- The following defines should be given when building:
    - PAYLOAD_PATH: path to the main payload to load
    - PAYLOAD_DEST: address to copy the main payload to
    - PAYLOAD_ENTRY: address to start execution in the main payload at
    - PAYLOAD_HOOK: address to branch to the payload entry from
- It's assumed that the OS save region is free to be used
- During the initial reboot, the loader requires space at 0x81000000 to relocate itself to
    - This should just be free arena space
- After the initial reboot, the loader requires space at 0x80005000 to relocate itself to
    - This limits the total loader size (including its payload) to 0x10bc bytes

### tools/makegecko.py

Creates a payload implementation gecko code. No assumptions are made about this payload.

### tools/makewiimario.py

Creates a save file with a loader (ex. saveloader) + the exploit to load it.

- Save file parts used for the exploit:
    - MarioWork:
        - useItems
        - shopItems
        - catchCards
    - SpmarioGlobals
        - lswf
        - lsw
        - coinEntries
- Assumes the loader is expecting to be loaded at & executed from the start of lswf
