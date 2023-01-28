/*
    SPDX-License-Identifier: GPL-3.0-or-later
    Copyright 2020 Linus S. (aka PistonMiner)
    Copyright 2021 Zephiles

    This is heavily based off of the original TTYD save exploit code by
    PistonMiner, and Zephiles' original SPM port, slightly edited by Seeky
*/

.section .text
.global entry
.type entry, @function
entry:

/*
    Command line define arguments
*/
#ifndef PAYLOAD_PATH
    .err
#endif
#ifndef PAYLOAD_DEST
    .err
#endif
#ifndef PAYLOAD_ENTRY
    .err
#endif
#ifndef PAYLOAD_HOOK
    .err
#endif

/*
    Run function in the apploader
    Korean has a newer version of the apploader
*/
#ifdef SPM_KR0
    .set Apploader_Run, 0x8133405C
#else
    .set Apploader_Run, 0x81333B28
#endif

/*
    Constants
*/
.set LOADER_LOWMEM_LOCATION, 0x80005000
.set LOADER_ARENA_LOCATION, 0x81000000

/*
    ABI notes:

    All locations hooked at will never return to higher in the callstack,
    so the stack, lr and non-volatile registers don't need to be preserved

    The helper functions follow the ABI as normal
*/

/*
    Stage 1
    Execution Location: in save file
    Execution Time: on initial exploit
    Purpose: reboot game with hook for stage 2

    NORETURN from hook
*/
stage1:

// Get base address
bl stage1_pic
stage1_pic:
mflr r4

// Setup stage 2 to run
// writeBranch(__OSReboot, stage2)
lis r3, __OSReboot@h
ori r3, r3, __OSReboot@l
addi r4, r4, (stage2 - stage1_pic)
bl writeBranch

// Restart game
.set wiiResetCode, spmarioMain + 0x118
lis r12, wiiResetCode@h
ori r12, r12, wiiResetCode@l
mtlr r12
blr

/*
    Stage 2
    Execution Location: in save file (first) or lowmem (on user reboot)
    Execution Time: on __OSReboot
    Purpose: copy loader to saved region & hook dol's Run for stage 3

    NORETURN from hook
*/
stage2:

// Backup original args
mr r30, r3
mr r31, r4

// Get base address
bl stage2_pic
stage2_pic:
mflr r4

// Get loader arena location
lis r29, LOADER_ARENA_LOCATION@h
ori r29, r29, LOADER_ARENA_LOCATION@l

// Copy loader to arena location
// memmove(LOADER_ARENA_LOCATION, entry, LOADER_SIZE)
mr r3, r29
addi r4, r4, (entry - stage2_pic)
li r5, LOADER_SIZE
lis r12, memmove@h
ori r12, r12, memmove@l
mtlr r12
blrl
// flushCache(LOADER_ARENA_LOCATION, LOADER_SIZE)
mr r3, r29
li r4, LOADER_SIZE
bl flushCache

// Set the OS saved region to the new loader copy
// SaveStart = LOADER_ARENA_LOCATION
lis r3, SaveStart@ha
stw r29, SaveStart@l (r3)
// SaveEnd = LOADER_ARENA_LOCATION + LOADER_SIZE
addi r4, r29, LOADER_SIZE
lis r3, SaveEnd@ha
stw r4, SaveEnd@l (r3)

// Setup stage 3 to run
// writeBranch(Run, LOADER_ARENA_LOCATION.stage3)
lis r3, Run@h
ori r3, r3, Run@l
addi r4, r29, (stage3 - entry)
bl writeBranch

// Return to OSReboot
.set stage2_ret, __OSReboot + 4
mr r3, r30
mr r4, r31
lis r12, stage2_ret@h
ori r12, r12, stage2_ret@l
mtlr r12
blr

/*
    Stage 3
    Execution Location: in saved region
    Execution Time: on dol's Run(apploader) call
    Purpose: hook apploader's Run for stage 4

    NORETURN from hook
*/
stage3:

// Backup original arg
mr r31, r3

// Get base address
bl stage3_pic
stage3_pic:
mflr r4

// Setup stage 4 to run 
// writeBranch(Apploader_Run, stage4)
lis r3, Apploader_Run@h
ori r3, r3, Apploader_Run@l
addi r4, r4, (stage4 - stage3_pic)
bl writeBranch

// Return to Run
.set stage3_ret, Run + 4
mr r3, r31
lis r12, stage3_ret@h 
ori r12, r12, stage3_ret@l
mtlr r12
blr

/*
    Stage 4
    Execution Location: in saved region
    Execution Time: on apploader's Run(dol) call
    Purpose: patch game for payload & for reboot re-application

    NORETURN from hook
*/
stage4:

// Backup original arg
mr r31, r3

// Get base address
bl stage4_pic
stage4_pic:
mflr r30

// Get payload dest
lis r29, PAYLOAD_DEST@h
ori r29, r29, PAYLOAD_DEST@l

// Put payload in place
// memmove(PAYLOAD_DEST, payload, PAYLOAD_SIZE)
mr r3, r29
addi r4, r30, (payload - stage4_pic)
li r5, PAYLOAD_SIZE
lis r12, memmove@h
ori r12, r12, memmove@l
mtlr r12
blrl
// flushCache(PAYLOAD_DEST, PAYLOAD_SIZE)
mr r3, r29
li r4, PAYLOAD_SIZE
bl flushCache

// Write payload hook
// writeBranch(PAYLOAD_HOOK, PAYLOAD_ENTRY)
lis r3, PAYLOAD_HOOK@h
ori r3, r3, PAYLOAD_HOOK@l
lis r4, PAYLOAD_ENTRY@h
ori r4, r4, PAYLOAD_ENTRY@l
bl writeBranch

// Get lowmem location
lis r28, LOADER_LOWMEM_LOCATION@h
ori r28, r28, LOADER_LOWMEM_LOCATION@l

// Copy loader to lowmem location
// memmove(LOADER_LOWMEM_LOCATION, entry, LOADER_SIZE)
mr r3, r28
addi r4, r30, (entry - stage4_pic)
li r5, LOADER_SIZE
lis r12, memmove@h
ori r12, r12, memmove@l
mtlr r12
blrl
// flushCache(LOADER_LOWMEM_LOCATION, LOADER_SIZE)
mr r3, r28
li r4, LOADER_SIZE
bl flushCache

// Setup stage 2 to rerun on user reboot
// writeBranch(__OSReboot, LOADER_LOWMEM_LOCATION.stage2)
lis r3, __OSReboot@h
ori r3, r3, __OSReboot@l
addi r4, r28, (stage2 - entry)
bl writeBranch

// Return to Run
.set stage4_ret, Apploader_Run + 4
mr r3, r31
lis r12, stage4_ret@h
ori r12, r12, stage4_ret@l
mtlr 12
blr

/*
    Helper - writeBranch
        r3: hook address
        r4: destination
*/
writeBranch:

// Write instruction
sub r4, r4, r3
rlwinm r4, r4, 0, 6, 29
oris r4, r4, 0x4800
stw r4, 0 (r3)

// Flush cache
li r4, 4
b flushCache

/*
    Helper - flushCache
        r3: address
        r4: length
*/
flushCache:

// Push stack
stwu r1, -0x20 (r1)
mflr r0
stw r0, 0x24 (r1)
stmw r30, 0x8 (r1)
mr r31, r3
mr r30, r4

// DCFlushRange(address, length)
lis r12, DCFlushRange@h
ori r12, r12, DCFlushRange@l
mtlr r12
blrl

// ICInvalidateRange(address, length)
mr r3, r31
mr r4, r30
lis r12, ICInvalidateRange@h
ori r12, r12, ICInvalidateRange@l
mtlr r12
blrl

// Pop stack
lmw r30, 0x8 (r1)
lwz r0, 0x24 (r1)
mtlr r0
addi r1, r1, 0x20
blr

/*
    Payload
*/

#define _TOSTRING(a) #a
#define TOSTRING(a) _TOSTRING(a)

payload:
.incbin TOSTRING(PAYLOAD_PATH)

.set PAYLOAD_SIZE, . - payload

.set LOADER_SIZE, . - entry
