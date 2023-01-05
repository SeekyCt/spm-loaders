#pragma once

#include <common.h>

CPP_WRAPPER(wii::os)

void __OSReboot(Unk param_1, Unk param_2);
UNKNOWN_FUNCTION(OSGetSaveRegion);
UNKNOWN_FUNCTION(OSRegisterShutdownFunction);
UNKNOWN_FUNCTION(__OSCallShutdownFunctions);
UNKNOWN_FUNCTION(__OSShutdownDevices);
void OSShutdownSystem();
UNKNOWN_FUNCTION(__OSRebootForNANDAPP);
void OSRestart(s32 code);
void OSReturnToMenu();
UNKNOWN_FUNCTION(__OSReturnToMenuForError);
s32 OSGetResetCode();
UNKNOWN_FUNCTION(OSResetSystem);

CPP_WRAPPER_END()
