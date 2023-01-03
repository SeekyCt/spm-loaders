#pragma once

struct RelLoaderContext
{
/* 0x00 */ char magic[4]; // RLd3
/* 0x04 */ u32 contextVersion;
/* 0x08 */ s32 loaderType;
/* 0x0C */ s32 loaderVersion;
/* 0x10 */ void * hostRelContext;
};
