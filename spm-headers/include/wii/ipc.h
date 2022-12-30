#pragma once

#include <common.h>

CPP_WRAPPER(wii::ipc)

/*
    IOS_Open mode param
*/
enum IosOpenMode
{
/* 0x0 */ IOS_OPEN_NONE,
/* 0x1 */ IOS_OPEN_READ,
/* 0x2 */ IOS_OPEN_WRITE
};

/*
    /dev/fs GetFileStats output
*/
typedef struct
{
/* 0x0 */ u32 position;
/* 0x4 */ u32 length;
} FsFileStats;
SIZE_ASSERT(FsFileStats, 8);

typedef struct
{
/* 0x0 */ void * data;
/* 0x4 */ u32 len;
} Ioctlv;
SIZE_ASSERT(Ioctlv, 0x8);

UNKNOWN_FUNCTION(IPCInit);
UNKNOWN_FUNCTION(IPCReadReg);
UNKNOWN_FUNCTION(IPCWriteReg);
UNKNOWN_FUNCTION(IPCGetBufferHi);
UNKNOWN_FUNCTION(IPCGetBufferLo);
UNKNOWN_FUNCTION(IPCSetBufferLo);
UNKNOWN_FUNCTION(strnlen);
UNKNOWN_FUNCTION(IpcReplyHandler);
UNKNOWN_FUNCTION(IPCInterruptHandler);
UNKNOWN_FUNCTION(IPCCltInit);
UNKNOWN_FUNCTION(__ios_Ipc2);
UNKNOWN_FUNCTION(IOS_OpenAsync);
s32 IOS_Open(const char * path, s32 mode);
UNKNOWN_FUNCTION(IOS_CloseAsync);
s32 IOS_Close(s32 fd);
UNKNOWN_FUNCTION(IOS_ReadAsync);
UNKNOWN_FUNCTION(IOS_Read);
UNKNOWN_FUNCTION(IOS_WriteAsync);
UNKNOWN_FUNCTION(IOS_Write);
UNKNOWN_FUNCTION(IOS_SeekAsync);
UNKNOWN_FUNCTION(IOS_IoctlAsync);
UNKNOWN_FUNCTION(IOS_Ioctl);
UNKNOWN_FUNCTION(__ios_Ioctlv);
UNKNOWN_FUNCTION(IOS_IoctlvAsync);
s32 IOS_Ioctlv(s32 fd, s32 command, s32 inCount, s32 outCount, Ioctlv * vecs);
UNKNOWN_FUNCTION(IOS_IoctlvReboot);
UNKNOWN_FUNCTION(iosCreateHeap);
UNKNOWN_FUNCTION(__iosAlloc);
UNKNOWN_FUNCTION(iosAllocAligned);
UNKNOWN_FUNCTION(iosFree);
UNKNOWN_FUNCTION(IPCiProfInit);
UNKNOWN_FUNCTION(IPCiProfQueueReq);
UNKNOWN_FUNCTION(IPCiProfAck);
UNKNOWN_FUNCTION(IPCiProfReply);

CPP_WRAPPER_END()
