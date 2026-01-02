#include <common.h>
#include <wii/gx.h>
#include <wii/os.h>
#include <msl/stdio.h>
#include <msl/string.h>
#include <common.h>
#include <spm/evtmgr_cmd.h>
#include <spm/memory.h>
#include <spm/romfont.h>
#include <spm/relmgr.h>
#include <spm/spmario.h>
#include <wii/DEMOInit.h>
#include <wii/gx.h>
#include <wii/mtx.h>
#include <wii/os.h>
#include <wii/vi.h>
#include <msl/string.h>

#include <spm_loaders/memtest.h>

#include "error.h"
#include "romfontexpand.h"
#include "util.h"

namespace memtest {

/*
    Id of the loader chosen
*/
static s32 loaderUsed = -1;

void logLoaderUsed(s32 loader)
{
    wii::os::OSReport("Use loader %d\n", loader);
    loaderUsed = loader;
}

/*
    Prints a stack trace to a buffer, truncating at destSize
*/
static void printStackTrace(char * dest, u32 destSize)
{
    u32 * p = (u32 *) __builtin_frame_address(0);
    s32 i = 0;
    while (0x80000000 <= (u32)p && (u32)p <= 0x81ffffff && destSize > 0)
    {
        // Write lr save to output
        u32 lr = p[1];
        const char * end;
        if (i % 4 == 3)
            end = "<-\n";
        else
            end = "<-";
        u32 numWrote = msl::stdio::snprintf(dest, destSize, "%08x%s", lr, end);
        dest += numWrote;
        destSize -= numWrote;

        // Move to next frame
        p = (u32 *)p[0];
        i += 1;
    }
}

void NORETURN assertionError(const char * file, s32 line, s32 code)
{
    char message[256];

    u32 numWrote = msl::stdio::snprintf(
        message,
        sizeof(message),
        "[%c|%d|%d|%d|%d|%d] %s %d %d\n",
        *(char *)0x80000003,
        *(u8 *)0x80000007,
        PayloadHeader::instance->implementationType,
        PayloadHeader::instance->implementationVersion,
        PayloadHeader::instance->payloadVersion,
        loaderUsed,
        file,
        line,
        code
    );
    printStackTrace(message + numWrote, sizeof(message) - numWrote);

    error(message);
}

void NORETURN error(const char * message)
{
    static const wii::gx::GXColor fg = {0xff, 0xff, 0xff, 0xff};
    static const wii::gx::GXColor bg = {0x00, 0x00, 0x00, 0xff};
    wii::os::OSFatal(&fg, &bg, message);
}

#if defined SPM_EU0 || defined SPM_EU1
    #define getGameRegion() ("PAL")
#elif defined SPM_US0 || defined SPM_US1 || defined SPM_US2
    #define getGameRegion() ("NTSC-U")
#elif defined SPM_JP0 || defined SPM_JP1
    #define getGameRegion() ("NTSC-U")
#elif defined SPM_KR0
    #define getGameRegion() ("NTSC-U")
#else
    #error "Bad version"
#endif

#if defined SPM_EU0 || defined SPM_JP0 || defined SPM_US0 || defined SPM_KR0
    #define getGameRevision() (0)
#elif defined SPM_EU1 || defined SPM_JP1 || defined SPM_US1
    #define getGameRevision() (1)
#elif defined SPM_US2
    #define getGameRevision() (2)
#else
    #error "Bad version"
#endif

extern "C" {
    bool inOSPanic = false;
    char exceptionWorkingText[256];

    void OSPanicForwarder();
    void exceptionOSReportForwarder();
    void exceptionDraw();

    void __OSUnhandledExceptionReal(s32 p1, s32 p2, s32 p3, s32 p4);
    s32 evtmgrCmdReal(spm::evtmgr::EvtEntry*);
}

static bool inException = false;
static char * exceptionText;
#define EXCEPTION_TEXT_SIZE 4096
static u32 head = 0;
static spm::evtmgr::EvtScriptCode * lastScript = nullptr;

#define SCREEN_TOP 228.0f
#define SCREEN_BOTTOM -228.0f
#define TITLE_Y 195.0f
#define TEXT_TOP (TITLE_Y - (LINE_HEIGHT * 2))
#define TEXT_BOTTOM (SCREEN_BOTTOM - LINE_HEIGHT)
#define TEXT_LEFT -300.0f
#define LINE_HEIGHT 15.0f

__asm__ (
".global __OSUnhandledExceptionReal;"
"__OSUnhandledExceptionReal:"
    "stwu 1, -0x30(1);"
    "b __OSUnhandledException+4;"

".global evtmgrCmdReal;"
"evtmgrCmdReal:"
    "stwu 1, -0x20(1);"
    "b evtmgrCmd+4;"

".global OSPanicForwarder;"
".type OSPanicForwarder, @function;"
"OSPanicForwarder:"
    "li 0, 1;"
    "lis 4, inOSPanic@ha;"
    "stw 0, inOSPanic@l (4);"
    "addi 3, 1, 0x78;"
    "b exceptionMessageHandler;"

".global exceptionOSReportForwarder;"
".type exceptionOSReportForwarder, @function;"
"exceptionOSReportForwarder:"
    "mflr 0;"
    "stw 0, 4 (1);"
    "stwu 1, -32 (1);"
    "mr 10, 9;"
    "mr 9, 8;"
    "mr 8, 7;"
    "mr 7, 6;"
    "mr 6, 5;"
    "mr 5, 4;"
    "mr 4, 3;"
    "lis 3, exceptionWorkingText@h;"
    "ori 3, 3, exceptionWorkingText@l;"
    "bl sprintf;"

    "lis 3, exceptionWorkingText@h;"
    "ori 3, 3, exceptionWorkingText@l;"
    "addi 1, 1, 32;"
    "lwz 0, 4 (1);"
    "mtlr 0;"
    "b exceptionOSReport;"
);

static wii::gx::GXColor titleColour {0xff, 0x20, 0x20, 0xff};

static void drawTitle(f32 scale)
{
    spm::romfont::romFontPrintGX(TEXT_LEFT, TITLE_Y, scale, &titleColour,
                                 "Exception - memtest - %s Revision %d",
                                 getGameRegion(), getGameRevision());
    spm::romfont::romFontPrintGX(TEXT_LEFT, TITLE_Y - LINE_HEIGHT, scale, &titleColour,
                                 "Last Evt %p - relF %p", (void *) lastScript,
                                 (void *) (spm::relmgr::relmgr_wp ? spm::relmgr::relmgr_wp->relFile : 0));
}

const wii::gx::GXColor white  {0xff, 0xff, 0xff, 0xff};
static void draw(char * msg, f32 yShift, f32 scale)
{
    char * p = msg;
    bool done = false;
    const f32 x = TEXT_LEFT;
    f32 y = 200.0f - yShift;
    while (!done)
    {
        // Find end of line
        char * q = p;
        while ((*q != '\n') && (*q != '\0'))
            q++;
        
        // Split line into its own string temporarily
        done = *q == '\0';
        *q = '\0';
        
        // Draw line if on screen
        if ((y >= TEXT_BOTTOM) && (y <= TEXT_TOP))
            spm::romfont::romFontPrintGX(x, y, scale, &white, p);

        // Move to next line
        y -= LINE_HEIGHT;
        p = q + 1;

        // Restore string
        if (!done)
            *q = '\n';
    }
}

static f32 getBottomY(char * msg)
{
    // Count newlines
    int n = 0;
    for (int i = 0; msg[i]; i++)
    {
        if (msg[i] == '\n')
            n++;
    }

    // Calculate
    return TEXT_TOP - (LINE_HEIGHT * n);
}

extern "C" void exceptionMessageHandler(char * msg)
{
    wii::os::OSReport("<<FULL MESSAGE>> %s\n <</FULL MESSAGE>>", msg);

    // Print to OSReport
    wii::os::OSReport("%s\n", msg);

    const f32 topY = 50.0f;
    f32 bottomY = getBottomY(msg);
    f32 yShift = topY;
    f32 delta = bottomY <= SCREEN_BOTTOM ? 1.0f : 0.0f;
    // f32 scale = gIsDolphin ? 0.7f : 0.55f; // dolphin uses a custom font for copyright reasons
    f32 scale = 0.7f;
    while (true)
    {
        // Check if power button was pressed
        if (spm::spmario::spmario_doShutdown)
        {
            wii::vi::VISetBlack(1);
            wii::vi::VIFlush();
            wii::vi::VIWaitForRetrace();
            wii::vi::VIWaitForRetrace();
            wii::vi::VIWaitForRetrace();
            wii::os::OSShutdownSystem();
            while (true) {};
        }

        // Start frame
        wii::mtx::Mtx44 mtx;
        wii::DEMOInit::DEMOBeforeRender();
        wii::mtx::C_MTXOrtho(&mtx, SCREEN_TOP, SCREEN_BOTTOM, -304.0f, 304.0f, 1.0f, 1000.0f);
        wii::gx::GXSetProjection(&mtx, 1);

        // Draw game & mod version header
        drawTitle(scale);

        // Render main text
        draw(msg, yShift, scale);

        // Scroll for next frame
        if ((yShift >= topY) || (yShift <= bottomY))
            delta *= -1.0f;
        yShift += delta;

        // End frame
        wii::DEMOInit::DEMODoneRender();
    }
}

extern "C" void exceptionOSReport(const char * msg)
{
    // Print to OSReport
    wii::os::OSReport("!!!! %s\n", msg);

    // Store message to be drawn to screen
    size_t len = msl::string::strlen(msg);
    if ((head + len) >= EXCEPTION_TEXT_SIZE)
        return;    
    msl::string::strcpy(exceptionText + head, msg);
    head += len;
    wii::os::OSReport("-> %d/%d\n", head, EXCEPTION_TEXT_SIZE);
}

void checkExceptionFlags()
{
    if (inException)
        error("WARNING: Exception handler has crashed!\n");

    if (inOSPanic)
        exceptionOSReport("WARNING: OSPanic handler has crashed!\n");
}

static void checkDoubleCrash(s32 p1, s32 p2, s32 p3, s32 p4)
{
    checkExceptionFlags();
    inException = true;
    __OSUnhandledExceptionReal(p1, p2, p3, p4);
}

void exceptionDraw()
{
    exceptionMessageHandler(exceptionText);
}

static s32 patched_evtmgrCmd(spm::evtmgr::EvtEntry * entry)
{
    lastScript = entry->scriptStart;
    return evtmgrCmdReal(entry);
}

void exceptionPatch()
{   
    // OSPanic
    writeBranch(wii::os::OSPanic, 0x130, OSPanicForwarder); 

    // __OSUnhandledException
    writeBranchLink(wii::os::__OSUnhandledException, 0x50,  exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x1b0, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x1bc, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x1d8, exceptionOSReportForwarder);    
    writeBranchLink(wii::os::__OSUnhandledException, 0x1ec, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x220, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x234, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x24c, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x264, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x274, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x28c, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x2a0, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x2b4, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x2d0, exceptionOSReportForwarder);
    writeBranchLink(wii::os::__OSUnhandledException, 0x2d4, exceptionDraw);
    writeBranch(wii::os::__OSUnhandledException, 0, checkDoubleCrash);
    wii::os::__OSUnhandledException_msg1[73] = '\n';
    wii::os::__OSUnhandledException_msg2[75] = '\n';
    wii::os::__OSUnhandledException_msg3[72] = '\n';

    exceptionText = (char *) spm::memory::__memAlloc(spm::memory::HEAP_MAIN, 4096);

    // OSDumpContext
    writeBranchLink(wii::os::OSDumpContext, 0x2c, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x58, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x7c, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x90, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x9c, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0xc0, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x120, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x158, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x174, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x1ac, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x1fc, exceptionOSReportForwarder);
    writeBranchLink(wii::os::OSDumpContext, 0x220, exceptionOSReportForwarder);

    writeBranch(spm::evtmgr_cmd::evtmgrCmd, 0, patched_evtmgrCmd);

    romfontExpand();
}

}
