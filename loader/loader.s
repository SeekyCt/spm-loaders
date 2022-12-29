# C2 insert at:
#   jp0
#   jp1
#   us0
#   us1
#   us2
#   eu0 801a84b0
#   eu1 801a84b0
#   kr0

.set REGION, 'e' # e(u), u(s), j(p), k(r)
.set REVISION, 0 # 0-1,  0-2,  0-1,  0
.set GECKO, 0

.set memcpy, 0x80004000 # region free
.if (REGION == 'e') # both revisions have identical dols
    .set DVDMgrOpen, 0x8019e08c
    .set DVDMgrRead, 0x8019e1e4
    .set DVDMgrClose, 0x8019e2e0
    .set DVDMgrGetLength, 0x8019e320
    .set __memAlloc, 0x801a626c
    .set OSFatal, 0x802729b8
    .set OSLink, 0x80274c0c
.elseif ((REGION == 'u') && (REVISION == 0))
    .set DVDMgrOpen, 
    .set DVDMgrRead, 
    .set DVDMgrClose, 
    .set DVDMgrGetLength, 
    .set __memAlloc, 0x801A5634
    .set OSFatal, 0x80270198
    .set OSLink, 0x802723CC
.elseif ((REGION == 'u') && (REVISION == 1))
    .set DVDMgrOpen, 
    .set DVDMgrRead, 
    .set DVDMgrClose, 
    .set DVDMgrGetLength, 
    .set __memAlloc, 0x801A5690
    .set OSFatal, 0x80270868
    .set OSLink, 0x80272ABC
.elseif ((REGION == 'u') && (REVISION == 2))
    .set DVDMgrOpen, 
    .set DVDMgrRead, 
    .set DVDMgrClose, 
    .set DVDMgrGetLength, 
    .set __memAlloc, 0x801A59A8
    .set OSFatal, 0x80270908
    .set OSLink, 0x80272B5C
.elseif ((REGION == 'j') && (REVISION == 0))
    .set DVDMgrOpen, 
    .set DVDMgrRead, 
    .set DVDMgrClose, 
    .set DVDMgrGetLength, 
    .set __memAlloc, 0x801A5624
    .set OSFatal, 0x80270148
    .set OSLink, 0x8027237C
.elseif ((REGION == 'j') && (REVISION == 1))
    .set DVDMgrOpen, 
    .set DVDMgrRead, 
    .set DVDMgrClose, 
    .set DVDMgrGetLength, 
    .set __memAlloc, 0x801A566C
    .set OSFatal, 0x802707C8
    .set OSLink, 0x80272A1C
.elseif ((REGION == 'k') && (REVISION == 0))
    .set DVDMgrOpen, 
    .set DVDMgrRead, 
    .set DVDMgrClose, 
    .set DVDMgrGetLength, 
    .set __memAlloc, 0x8019EB44
    .set OSFatal, 0x80275114
    .set OSLink, 0x80277328
.else
    .err # Unknown version
.endif

# r31: startdata pointer
# r30: DVDEntry pointer
# r29: rel length
# r28: rel pointer

# Push stack
stwu r1, -0x18 (r1)
stmw r28, 0x8 (r1)
.if GECKO == 0
	mflr r0
	stw r0, 0x1c (r1)
.endif

# Get pointer to data
bl enddata

startdata:

relPath:
.string "/mod/mod.rel"

noRelMsg:
.string "ERROR: mod.rel was not found"
noMemMsg:
.string "ERROR: couldn't allocate file memory"
noBssMsg:
.string "ERROR: couldn't allocate bss memory"

foreground:
.byte 0xff, 0xff, 0xff, 0xff
background:
.byte 0, 0, 0, 0xff

.align 2

# Takes message in r5, expects r31 to be startdata
errorFunc:
    addi r3, r31, foreground - startdata
    addi r4, r31, background - startdata
    lis r12, OSFatal@ha
    addi r12, r12, OSFatal@l
    mtlr r12
    blrl

enddata:

mflr r31

# DVDMgrOpen(relPath, 2, 0)
addi r3, r31, relPath - startdata
li r4, 2
li r5, 0
lis r12, DVDMgrOpen@ha
addi r12, r12, DVDMgrOpen@l
mtlr r12
blrl
mr r30, r3

# Check file exists
cmpwi r30, 0
bne exists
    # Throw error
    addi r5, r31, noRelMsg - startdata
    b errorFunc
exists:

# DVDMgrGetLength(entry)
mr r3, r30
lis r12, DVDMgrGetLength@ha
addi r12, r12, DVDMgrGetLength@l
mtlr r12
blrl

# Round up length to DVD read size
addi r3, r3, 0x1f
rlwinm r29, r3, 0, 0xffffffe0

# __memAlloc(MEM1_UNUSED, length)
li r3, 2
mr r4, r29
lis r12, __memAlloc@ha
addi r12, r12, __memAlloc@l
mtlr r12
blrl
mr r28, r3

# Check allocation worked
cmpwi r28, 0
bne memAllocated
    # Throw error
    addi r5, r31, noMemMsg - startdata
    b errorFunc
memAllocated:

# DVDMgrRead(entry, rel, length, 0)
mr r3, r30
mr r4, r28
mr r5, r29
li r6, 0
lis r12, DVDMgrRead@ha
addi r12, r12, DVDMgrRead@l
mtlr r12
blrl

# DVDMgrClose(entry)
mr r3, r30
lis r12, DVDMgrClose@ha
addi r12, r12, DVDMgrClose@l
mtlr r12
blrl

# __memAlloc(MEM1_UNUSED, rel->bssSize)
li r3, 2
lwz r4, 0x20 (r28)
lis r12, __memAlloc@ha
addi r12, r12, __memAlloc@l
mtlr r12
blrl

# Check allocation worked
cmpwi r3, 0
bne bssAllocated
    # Throw error
    addi r5, r31, noBssMsg - startdata
    b errorFunc
bssAllocated:

# Link rel
mr r4, r3
mr r3, r28
lis r12, OSLink@ha
addi r12, r12, OSLink@l
mtlr r12
blrl

# Call prolog
lwz r12, 0x34 (r28)
mtlr r12
blrl

# Pop stack
.if GECKO == 0
	lwz r0, 0x1c (r1)
	mtlr r0
.endif
lmw r28, 0x8 (r1)
addi r1, r1, 0x18

# Original instruction
li r3, 0

# Blr if needed
.if GECKO == 0
	blr
.endif
