## General Notes

- The loader should hook on the blr of spmarioInit
    - If using gecko codes on console, this requires `VI Hook` to be able to be patched in time

## Context

The loader has an embedded context struct in the reserved memory for mods to use.

| Address  | Type    | Name                   | Notes                                         |
|----------|---------|------------------------|-----------------------------------------------|
| 80004200 | char[4] | Magic                  | ASCII 'RLd3'                                  |
| 80004204 | u32     | Context Version        | Context version (=1)                          |
| 80004208 | s32     | Implementation Type    | Specific implementation type, see table below |
| 8000420C | s32     | Implementation Version | Version of the implementaiton                 |
| 80004210 | s32     | Rel Loader Version     | Version of the loader itself                  |
| 80004214 | void *  | Host Rel Context       | If a rel is acting as a host, context for it  |
| 80004218-F | Reserved for future use

### Magic

- ASCII value 'RLd3' (Rel Loader 3).
- If this isn't set, it can be assumed that a functionally different loader was used
    - A loader is functionally different if it executes the rel prolog at a different time, or if it doesn't provide a compatible context struct
    - These loaders should either not touch this memory, or use a different magic

### Context Version

- Determines the format of this struct, currently 1
- These existing fields can be assumed to keep their position in all future versions

### Loader Type

| Type | Info                       |
|------|----------------------------|
| -1   | Unset                      |
| 0    | Official Gecko Code        |
| 1    | Official Dol Patch         |
| 2    | Official Riivolution Patch |
| 3    | Official Save exploit      |

- More types may be added in the future
- This is just provided for debugging
    - Error messages in mods should include this
    - No assumptions should be made based on this value

### Loader Version

- The version of the specific loader used (given by Loader Type)
- This is just provided for debugging
    - Error messages in mods should include this
    - No assumptions should be made based on this value

### Host Rel Context

- A place for the rel loaded to provide information to other rels if it's acting as host
    - No dependence on module id or version
- A host rel should assert that this is null before writing here
- The context should start with a 4 byte magic value, hosts are free to structure the rest however they like
- Child rels should assert the magic matches the expected host

Known magic values:

| Magic Value | Host Type |
|-------------|-----------|
| CORE        | spm-core  |
