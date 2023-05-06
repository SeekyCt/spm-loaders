# spm-loaders

This repo contains some generalised loader components, and a specific standard design built off of those.
See [Components](#components) for details of the components, and [STANDARD.MD] for the more specific details.

The components are split into 2 categories:
- Payload (end goal code to run)
    - relloader
- Implementations (loaders & executors of generic payloads)
    - Save Exploit
    - Gecko Code
    - Dol Patch
    - Riivolution XML (TODO)

## Memory Usage

A certain range of RAM across all regions is reserved for this: 80004200 - 800060bb (inclusive)
- 80004200 - 80004fff is relloader
- 80005000 - 800060bb is space for saveloader if needed
- This range can be patched in a dol easily
- This is part of the TRK interrupt table, which goes unused and is in the same place in all versions
- Technically, anything from the TRK string at 80004188 could've been used
    - The starting address chosen is slightly nicer
    - This still leaves some space for other systems to use

## Payload Header

| Offset  | Type    | Name                   |
|---------|---------|------------------------|
| 0x00    | char[4] | Header Magic           |
| 0x04    | u32     | Header Version         |
| 0x08    | char[4] | Payload Magic          |
| 0x0C    | u32     | Payload Version        |
| 0x10    | void *  | Context                |
| 0x14    | void *  | Load Address           |
| 0x18    | void *  | Entrypoint             |
| 0x1C    | void *  | Hook Address           |
| 0x20    | u32     | Implementation Type    |
| 0x24    | u32     | Implementation Version |

- The following files assume this format:
    - `include/payload.h`
    - `include/payloadoffs.inc`
    - `relloader3/entry.s`
    - `tools/makegecko.py`
- **Header Magic**: ASCII value 'SPMP' (Super Paper Mario Payload)
- **Header Version**: the format of this struct, currently 1
    - These existing fields can be assumed to keep their position in all future versions
- **Payload Magic**: ASCII identifier of the payload itself
    - See table below for known values
- **Payload Version**: the version of the payload itself
- **Context**: space for the payload to give information to other code
- **Load Address**: address to load the payload at
- **Entrypoint**: address to start execution of the payload at
    - Add 1 to this address to use a bl for the hook instead of a b
- **Hook Address**: address to branch to the entrypoint from
- **Implementation Type**: identifier of the implementation that loaded this payload
    - Should be left as -1 in the payload itself, and written to by implementations
    - See table below for known values
    - More types may be added in the future
    - This is just provided for debugging
        - Error messages in mods should include this
        - No assumptions should be made based on this value
- **Implementation Version**: the version of the implementation that loaded this payload
    - Should be left as -1 in the payload itself, and written to by implementations
    - This is just provided for debugging
        - Error messages in mods should include this
        - No assumptions should be made based on this value

| Payload Magic | Payload Type |
|---------------|--------------|
| RLd3          | relloader3   |

| Implementation Type | Name                       |
|---------------------|----------------------------|
| 0                   | Official Gecko Code        |
| 1                   | Official Dol Patch         |
| 2                   | Official Riivolution Patch |
| 3                   | Official Save exploit      |

## relloader3 Payload

relloader is the main rel loader payload, shared between all implementations.

- This expects to be loaded at 80004200
    - For compatibility with saveloader, this limits the size to 0x800 bytes
- This loads the file "./mod/rgX.rel" from disc if it exists, and falls back to "rgX.rel" in the save file if it doesn't
    - Where `rg` is `eu`, `us`, `jp` or `kr` for the region of the game, and `X` is 0-2 for the revision of the game
- The rel is placed on the unused MEM1 heap (id 2) if there's space, or the main MEM1 heap (id 0) otherwise

## Save Exploit Implementation

Creates a save file that will load a payload when the items menu is opened.

### saveloader

saveloader is the code to run in the save file exploit, to act as a payload implementation. It reboots the game, puts a bundled
payload (ex. relloader) at a specified address, and inserts a branch to it at a specified address from a specified hook address.
It will preserve itself on future game reboots and re-apply the payload hook.

- This is written as position independent assembly code
    - No assumption is made about the position of this loader in the save file
- The following defines should be given when building:
    - PAYLOAD_PATH: path to the main payload to load
- It's assumed that the OS save region is free to be used
- During the initial reboot, the loader requires space at 0x81000000 to relocate itself to
    - This should just be free arena space
- After the initial reboot, the loader requires space at 0x80005000 to relocate itself to
    - This limits the total saveloader size (including its payload) to 0x10bc bytes

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

## Gecko Code Implementation

Creates a gecko code that will load a payload on boot, done by `tools/makegecko.py`.

- If using gecko codes on console, the `VI Hook` hooktype should be used
    - This allows for payloads to use a wider range of hook locations during the game's boot process

## Riivolution Implementation

Creates a riivolution XML snippet that will load a payload on boot.

## Dol Patch Implementation

Patches a dol file to load a payload on boot.
