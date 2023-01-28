#pragma once

struct RelLoaderContext
{
/* 0x00 */ char magic[4]; // RLd3
/* 0x04 */ u32 contextVersion;
/* 0x08 */ s32 implementationType;
/* 0x0C */ s32 implementationVersion;
/* 0x10 */ s32 relLoaderVersion;
/* 0x14 */ void * hostRelContext;
/* 0x18 */ u8 reserved[0x20 - 0x18];
};
inline RelLoaderContext * const loaderCtx = (RelLoaderContext *)0x80004200;
